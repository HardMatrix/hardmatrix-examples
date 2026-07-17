import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb_bus.drivers.amba import AXI4Master
import logging

from vector_adder_machine_rdl import VectorAdderMachineRegmapAddrmap

# Hardware constants
VAM_REG_STATUS = 0x04
STATUS_DONE = 0x01
STATUS_ERR = 0x02
STATUS_CLEAR = 0x04
VAM_OP_ADD = 1
VAM_OP_SUB = 2


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


async def write_reg(axi_master, node, value):
    addr = node.spec.absolute_address
    await axi_master.write(addr, int(value))


async def read_reg(axi_master, node):
    addr = node.spec.absolute_address
    val_bin_list = await axi_master.read(addr, 1)
    return val_bin_list[0].to_unsigned()


async def write_addr(axi_master, addr, value):
    await axi_master.write(addr, int(value))


async def read_addr(axi_master, addr):
    val_bin_list = await axi_master.read(addr, 1)
    return val_bin_list[0].to_unsigned()


async def poll_status(dut, axi_master, max_cycles=100):
    """Poll STATUS register until DONE or ERR."""
    for _ in range(max_cycles):
        await RisingEdge(dut.clock)
        status = await read_addr(axi_master, VAM_REG_STATUS)
        if status & (STATUS_DONE | STATUS_ERR):
            return status
    raise TimeoutError("STATUS poll timed out")


async def run_op_test(dut, axi_master, reg_model, op_code,
                      vec_a_idx, vec_b_idx, vec_dest_idx,
                      vec_a_data, vec_b_data, expected):
    """Run a vector operation with STATUS polling and verify results."""
    op_name = "ADD" if op_code == VAM_OP_ADD else "SUB"
    num_elements = len(vec_a_data)

    dut._log.info(f"--- {op_name}: vec[{vec_a_idx}] op vec[{vec_b_idx}] -> vec[{vec_dest_idx}] ---")

    def get_vector_reg(idx):
        return getattr(reg_model, f"vectors_{idx}")

    def get_vector_elem(vec_obj, idx):
        return getattr(vec_obj, f"elems_{idx}")

    # Write Vector A
    vec_a = get_vector_reg(vec_a_idx)
    for i, val in enumerate(vec_a_data):
        await write_reg(axi_master, get_vector_elem(vec_a, i), val)

    # Write Vector B
    vec_b = get_vector_reg(vec_b_idx)
    for i, val in enumerate(vec_b_data):
        await write_reg(axi_master, get_vector_elem(vec_b, i), val)

    # Clear status
    await write_addr(axi_master, VAM_REG_STATUS, STATUS_CLEAR)

    # Wait a couple cycles for clear to take effect
    for _ in range(4):
        await RisingEdge(dut.clock)

    # Issue instruction
    instruction_val = (op_code & 0xFF) | \
                      ((vec_a_idx & 0x7) << 8) | \
                      ((vec_b_idx & 0x7) << 11) | \
                      ((vec_dest_idx & 0x7) << 14)

    await write_reg(axi_master, reg_model.instruction, instruction_val)

    # Poll status
    status = await poll_status(dut, axi_master)
    dut._log.info(f"STATUS = 0x{status:X} (done={bool(status & STATUS_DONE)}, err={bool(status & STATUS_ERR)})")

    assert not (status & STATUS_ERR), f"Hardware error! STATUS=0x{status:X}"
    assert status & STATUS_DONE, f"Not done! STATUS=0x{status:X}"

    # Read result
    vec_dest = get_vector_reg(vec_dest_idx)
    read_data = []
    for i in range(num_elements):
        val = await read_reg(axi_master, get_vector_elem(vec_dest, i))
        read_data.append(val)
        dut._log.info(f"  Result[{i}] = {val} (expected {expected[i]})")

    assert read_data == expected, f"Mismatch! Expected {expected}, got {read_data}"
    dut._log.info(f"{op_name} test passed!")


@cocotb.test()
async def test_vector_add(dut):
    """Test vector addition with STATUS polling."""
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)
    reg_model = VectorAdderMachineRegmapAddrmap(register_interface=None)

    await run_op_test(
        dut, axi_master, reg_model,
        op_code=VAM_OP_ADD,
        vec_a_idx=0, vec_b_idx=1, vec_dest_idx=2,
        vec_a_data=[10, 20, 30, 40],
        vec_b_data=[1, 2, 3, 4],
        expected=[11, 22, 33, 44]
    )


@cocotb.test()
async def test_vector_sub(dut):
    """Test vector subtraction with STATUS polling."""
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)
    reg_model = VectorAdderMachineRegmapAddrmap(register_interface=None)

    await run_op_test(
        dut, axi_master, reg_model,
        op_code=VAM_OP_SUB,
        vec_a_idx=0, vec_b_idx=1, vec_dest_idx=2,
        vec_a_data=[100, 200, 300, 400],
        vec_b_data=[10, 20, 30, 40],
        expected=[90, 180, 270, 360]
    )


@cocotb.test()
async def test_invalid_op_error(dut):
    """Test that an invalid opcode sets the error flag."""
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)
    reg_model = VectorAdderMachineRegmapAddrmap(register_interface=None)

    # Write some data to vectors first
    vec_a = reg_model.vectors_0
    vec_b = reg_model.vectors_1
    for i in range(4):
        await write_reg(axi_master, getattr(vec_a, f"elems_{i}"), i + 1)
        await write_reg(axi_master, getattr(vec_b, f"elems_{i}"), i + 10)

    # Clear status
    await write_addr(axi_master, VAM_REG_STATUS, STATUS_CLEAR)
    for _ in range(4):
        await RisingEdge(dut.clock)

    # Issue instruction with invalid opcode (0xFF)
    invalid_op = 0xFF
    instruction_val = (invalid_op & 0xFF) | (0 << 8) | (1 << 11) | (2 << 14)
    await write_reg(axi_master, reg_model.instruction, instruction_val)

    # Poll status — should get error
    status = await poll_status(dut, axi_master)
    dut._log.info(f"STATUS = 0x{status:X}")

    assert status & STATUS_ERR, f"Expected error flag, got STATUS=0x{status:X}"
    dut._log.info("Invalid op error test passed!")


@cocotb.test()
async def test_status_clear(dut):
    """Test that writing STATUS_CLEAR resets done/error flags."""
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)
    reg_model = VectorAdderMachineRegmapAddrmap(register_interface=None)

    # Run an addition to set DONE
    vec_a = reg_model.vectors_0
    vec_b = reg_model.vectors_1
    for i in range(4):
        await write_reg(axi_master, getattr(vec_a, f"elems_{i}"), 1)
        await write_reg(axi_master, getattr(vec_b, f"elems_{i}"), 2)

    instruction_val = (VAM_OP_ADD & 0xFF) | (0 << 8) | (1 << 11) | (2 << 14)
    await write_reg(axi_master, reg_model.instruction, instruction_val)

    status = await poll_status(dut, axi_master)
    assert status & STATUS_DONE, "Expected DONE after add"

    # Now clear
    await write_addr(axi_master, VAM_REG_STATUS, STATUS_CLEAR)
    for _ in range(4):
        await RisingEdge(dut.clock)

    status = await read_addr(axi_master, VAM_REG_STATUS)
    assert status == 0, f"Expected cleared status, got 0x{status:X}"
    dut._log.info("Status clear test passed!")


@cocotb.test()
async def test_multiple_operations(dut):
    """Test multiple sequential operations using various register combos."""
    clock = Clock(dut.clock, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    dut.reset.value = 0
    await RisingEdge(dut.clock)

    axi_master = AxiLite4Master(dut, "s_axil", dut.clock)
    reg_model = VectorAdderMachineRegmapAddrmap(register_interface=None)

    # Op 1: Add
    await run_op_test(
        dut, axi_master, reg_model,
        op_code=VAM_OP_ADD,
        vec_a_idx=0, vec_b_idx=1, vec_dest_idx=2,
        vec_a_data=[10, 20, 30, 40],
        vec_b_data=[1, 2, 3, 4],
        expected=[11, 22, 33, 44]
    )

    # Op 2: Sub with different registers
    await run_op_test(
        dut, axi_master, reg_model,
        op_code=VAM_OP_SUB,
        vec_a_idx=3, vec_b_idx=4, vec_dest_idx=5,
        vec_a_data=[50, 60, 70, 80],
        vec_b_data=[5, 6, 7, 8],
        expected=[45, 54, 63, 72]
    )

    # Op 3: Chain — use result of Op 1 (vec[2]) as input
    await run_op_test(
        dut, axi_master, reg_model,
        op_code=VAM_OP_ADD,
        vec_a_idx=2, vec_b_idx=5, vec_dest_idx=7,
        vec_a_data=[11, 22, 33, 44],
        vec_b_data=[45, 54, 63, 72],
        expected=[56, 76, 96, 116]
    )

    dut._log.info("All multiple operation tests passed!")
