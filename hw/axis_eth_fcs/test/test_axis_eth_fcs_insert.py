import itertools
import random
import zlib

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, with_timeout
from cocotb_bus.drivers import BitDriver
from cocotb_bus.scoreboard import Scoreboard
from utils.tb_utils.axi4stream_driver import AXI4Stream as AxisDrv
from utils.tb_utils.axi4stream_monitor import AXI4Stream as AxisMon

CLK_PERIOD_NS = 10


class AxisEthFcsInsertTester:
    def __init__(self, dut):
        self.dut = dut
        cocotb.start_soon(Clock(dut.clk, CLK_PERIOD_NS, unit="ns").start())

        self.ready_drv = BitDriver(signal=dut.m_axis_tready, clk=dut.clk)

        self.driver = AxisDrv(dut, "s_axis", dut.clk, valid_rate=1.0)
        self.monitor_in = AxisMon(dut, "s_axis", dut.clk, config={"capture_tlast": True})
        self.monitor_out = AxisMon(dut, "m_axis", dut.clk, config={"capture_tlast": True})

        self.expected_data = []
        self.input_packet = []
        self.scoreboard = Scoreboard(dut)

    async def reset(self, n_cycles):
        self.dut.rst_n.value = 0
        self.driver.bus.tvalid.value = 0
        self.dut.m_axis_tready.value = 0
        await ClockCycles(self.dut.clk, n_cycles)
        self.dut.rst_n.value = 1

    def start_random_backpressure(self):
        self.ready_drv.start(
            (random.randint(0, 1), random.randint(0, 1)) for _ in itertools.count()
        )

    def start_no_backpressure(self):
        self.dut.m_axis_tready.value = 1

    def build_expected_output(self, transaction):
        self.input_packet.append(transaction["tdata"])
        self.expected_data.append({"tdata": transaction["tdata"], "tlast": 0})

        if transaction["tlast"]:
            payload = bytes(self.input_packet)
            fcs = zlib.crc32(payload).to_bytes(4, "little")
            for idx, byte in enumerate(fcs):
                self.expected_data.append({"tdata": byte, "tlast": int(idx == len(fcs) - 1)})
            self.input_packet = []

    def send_packets(self, packets):
        for packet in packets:
            packet_bytes = list(packet)
            self.driver.append(packet_bytes, pkt_size=len(packet_bytes))

    async def wait_for_output(self, packets):
        expected_output_count = sum(len(packet) + 4 for packet in packets)
        for _ in range(expected_output_count):
            await with_timeout(self.monitor_out.wait_for_recv(), 1000, "ns")


def random_packet(min_size=1, max_size=256):
    return bytes(random.getrandbits(8) for _ in range(random.randint(min_size, max_size)))


@cocotb.test()
async def test_axis_eth_fcs_insert_scoreboard(dut):
    tb = AxisEthFcsInsertTester(dut)
    await tb.reset(10)
    tb.start_no_backpressure()

    tb.monitor_in.add_callback(tb.build_expected_output)
    tb.scoreboard.add_interface(tb.monitor_out, tb.expected_data)

    random.seed(42)
    packets = [
        b"\x00",
        b"\xff" * 8,
        bytes(range(64)),
        random_packet(),
        random_packet(),
        random_packet(),
        random_packet(),
    ]

    tb.send_packets(packets)
    await tb.wait_for_output(packets)

    tb.scoreboard.result


@cocotb.test()
async def test_axis_eth_fcs_insert_known_vector(dut):
    tb = AxisEthFcsInsertTester(dut)
    await tb.reset(10)
    tb.start_no_backpressure()

    tb.monitor_in.add_callback(tb.build_expected_output)
    tb.scoreboard.add_interface(tb.monitor_out, tb.expected_data)

    packets = [b"123456789"]

    tb.send_packets(packets)
    await tb.wait_for_output(packets)

    expected_fcs = 0xCBF43926
    assert zlib.crc32(packets[0]) == expected_fcs

    tb.scoreboard.result
