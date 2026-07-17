import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_bus.drivers.amba import AXI4Master
import multiprocessing
import time
import socket
import logging
from multiprocessing.connection import Listener
import threading # Import the threading module

# Import the generated register model and the socket backend
# We need to add the test directory to sys.path in the client process if it's not picked up,
# but typically multiprocessing replicates the environment.
from vector_adder_machine_rdl import VectorAdderMachineRegmapAddrmap
from peakrdl_python_simple.regif.impl.socket import SocketRegIfClient, SocketRegIfPacket, PROTOCOL_VERSION

# --- Configuration ---
SOCKET_HOST = 'localhost'
SOCKET_PORT = 12345
SOCKET_ADDRESS = (SOCKET_HOST, SOCKET_PORT)

# --- Minimal AxiLiteMaster adapter ---
class AxiLite4Master(AXI4Master):
    _signals = [
        "AWVALID", "AWADDR", "AWREADY",
        "WVALID", "WDATA", "WSTRB", "WREADY",
        "BVALID", "BREADY", "BRESP",
        "ARVALID", "ARADDR", "ARREADY",
        "RVALID", "RDATA", "RREADY", "RRESP"
    ]
    def __init__(self, entity, name, clock, **kwargs):
        super().__init__(entity, name, clock, **kwargs)

# --- Client Process Function ---
# This runs in a separate process and acts like the "Firmware" or "High-level Test"
def client_test_process():
    # Give the server a moment to start
    time.sleep(1) 
    
    print("[Client] Connecting to hardware simulation...")
    
    # Retry connection logic
    reg_if = None
    for attempt in range(5):
        try:
            reg_if = SocketRegIfClient(SOCKET_ADDRESS, data_width=32)
            break
        except ConnectionRefusedError: # Or OSError depending on Python/OS
            print(f"[Client] Connection refused. Retrying... ({attempt+1}/5)")
            time.sleep(1) # Wait a bit before retrying
        except OSError as e: # Catch OSError for broader compatibility
            if e.errno == 111: # Connection refused
                print(f"[Client] Connection refused. Retrying... ({attempt+1}/5)")
                time.sleep(1)
            else:
                print(f"[Client] Unexpected OS error: {e}")
                exit(1)
    
    if reg_if is None:
        print("[Client] Failed to connect after multiple attempts.")
        exit(1)

    try:
        reg_model = VectorAdderMachineRegmapAddrmap(register_interface=reg_if)
        
        print("[Client] Connected. Starting register sequence.")

        # Test Data
        num_elements = 4
        vec_a_idx = 0
        vec_b_idx = 1
        vec_dest_idx = 2
        vec_a_data = [10, 20, 30, 40]
        vec_b_data = [1, 2, 3, 4]
        op_code = 1
        expected_sum = [a + b for a, b in zip(vec_a_data, vec_b_data)]

        # 1. Write Vector A
        # Flattened access: vectors_0, vectors_1, ...
        vec_a_regfile = getattr(reg_model, f"vectors_{vec_a_idx}")
        for i, val in enumerate(vec_a_data):
            elem_reg = getattr(vec_a_regfile, f"elems_{i}")
            # Synchronous write via socket!
            elem_reg.data = val # Use property assignment
            print(f"[Client] Wrote RegA[{i}] = {val}")

        # 2. Write Vector B
        vec_b_regfile = getattr(reg_model, f"vectors_{vec_b_idx}")
        for i, val in enumerate(vec_b_data):
            elem_reg = getattr(vec_b_regfile, f"elems_{i}")
            elem_reg.data = val # Use property assignment
            print(f"[Client] Wrote RegB[{i}] = {val}")

        # 3. Issue Instruction: Single Atomic Write to prevent multiple swmod triggers
        print("[Client] Issuing Instruction (Atomic)...")
        
        instr_val = (op_code & 0xFF) | \
                    ((vec_a_idx & 0x7) << 8) | \
                    ((vec_b_idx & 0x7) << 11) | \
                    ((vec_dest_idx & 0x7) << 14)
        
        # Perform raw write using the interface to ensure atomic update
        reg_model.instruction.regif.set(
            reg_model.instruction.spec.absolute_address,
            instr_val
        )

        # 4. Poll for completion? 
        # In a real HW we might poll a status register. 
        # Here we just wait a bit of wall-clock time to let the sim advance.
        # Note: Time here is real time, not sim time. 
        time.sleep(0.5) 

        # 5. Read Result
        print("[Client] Reading Results...")
        vec_dest_regfile = getattr(reg_model, f"vectors_{vec_dest_idx}")
        read_data = []
        for i in range(num_elements):
            elem_reg = getattr(vec_dest_regfile, f"elems_{i}")
            # Synchronous read via socket!
            val = elem_reg.data # Use property access
            read_data.append(val)
            print(f"[Client] Read Result[{i}] = {val}")

        # Verification
        if read_data == expected_sum:
            print("[Client] SUCCESS: Data matches expected sum.")
        else:
            print(f"[Client] FAILURE: Expected {expected_sum}, got {read_data}")
            exit(1) # Fail the process

    except Exception as e:
        print(f"[Client] Error: {e}")
        exit(1)

# --- Server (Cocotb) Logic ---
async def run_socket_server(dut, axi_master):
    dut._log.info(f"Starting Socket Server on {SOCKET_ADDRESS}")
    
    # We use peakrdl's SocketRegIfPacket definitions to decode requests
    
    # Create the listener
    # Note: 'Listener' blocks on __init__ if we aren't careful? No, it binds.
    # But accept() blocks. We need to be careful not to block the event loop.
    # multiprocessing.connection.Listener is blocking.
    # We should run the listener accept loop in a way that doesn't kill cocotb.
    # BUT wait, Listener uses standard sockets under the hood. 
    # Can we just use a non-blocking poll?
    
    # Alternatively, use a separate thread for the *Listener* that pushes requests 
    # to an async queue that the main cocotb loop consumes.
    
    # REVISED SERVER STRATEGY:
    # Use standard python threading.Queue for passing data between the blocking server thread and the async cocotb loop.
    import queue
    thread_req_queue = queue.Queue()
    thread_resp_queue = queue.Queue()

    def blocking_server():
        try:
            with Listener(SOCKET_ADDRESS) as listener:
                with listener.accept() as conn:
                    while True:
                        try:
                            req = conn.recv()
                            thread_req_queue.put(req)
                            resp = thread_resp_queue.get() # Wait for Cocotb to process
                            conn.send(resp)
                        except EOFError:
                            break
        except Exception as e:
            # print(f"Server Thread Exception: {e}") # Expected on shutdown
            pass

    t = threading.Thread(target=blocking_server, daemon=True)
    t.start()
    
    dut._log.info("Server thread started. Entering event processing loop...")

    # Main Async Loop to process requests
    while True:
        # Check for requests non-blocking or with a short sleep to allow sim to progress
        # Since 'thread_req_queue' is blocking, we can't await it directly.
        # We poll it.
        if not thread_req_queue.empty():
            req = thread_req_queue.get()
            
            # Process Request (Async bus access)
            resp = req # Reuse packet for response
            
            try:
                if req.operation[0] == SocketRegIfPacket.Operation.GET:
                    addr = req.reg_address
                    dut._log.debug(f"Server received GET request for 0x{addr:X}")
                    val_list = await axi_master.read(addr, 1)
                    val = val_list[0].to_unsigned()
                    resp.value = int(val)
                    resp.status = (SocketRegIfPacket.Status.RESPONSE_OK, None)
                    dut._log.debug(f"Server read 0x{val:X} from 0x{addr:X}. Sending 0x{resp.value:X} as response.")
                    
                elif req.operation[0] == SocketRegIfPacket.Operation.SET:
                    addr = req.reg_address
                    val = req.value
                    dut._log.debug(f"Server received SET request for 0x{addr:X} with value 0x{val:X}")
                    await axi_master.write(addr, int(val))
                    resp.status = (SocketRegIfPacket.Status.RESPONSE_OK, None)
                    dut._log.debug(f"Server wrote 0x{val:X} to 0x{addr:X}. Sending OK response.")
                    
                else:
                    raise NotImplementedError("Unknown Op")
                    
            except Exception as e:
                dut._log.error(f"Error processing packet: {e}")
                resp.status = (SocketRegIfPacket.Status.RESPONSE_ERROR, str(e))
            
            # Send response back to thread
            thread_resp_queue.put(resp)
            
        else:
            # Yield to simulation time to let things happen (e.g. clock running)
            await Timer(1, unit='ns')
            
        # Exit condition? 
        # For this test, we run until the client process finishes. 
        # We'll check that in the main test function.

@cocotb.test()
async def test_vector_adder_machine_socket(dut):
    """
    Hardware-in-the-Loop style test using SocketRegIf and Multiprocessing.
    """
    # Start Clock
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    # Initialize AXI Master
    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)

    # Start the Client Process
    # Start process BEFORE creating threads (in run_socket_server) to avoid fork warnings/deadlocks
    dut._log.info("Spawning Client Process...")
    p = multiprocessing.Process(target=client_test_process)
    p.start()

    # Start the Server Task
    server_task = cocotb.start_soon(run_socket_server(dut, axi_master))
    
    # Wait for Client to finish
    # We loop and yield to allow the server_task to run
    while p.is_alive():
        await Timer(100, unit='ns')
        
    p.join()
    
    if p.exitcode == 0:
        dut._log.info("Client process finished SUCCESS.")
    else:
        assert False, "Client process failed."
