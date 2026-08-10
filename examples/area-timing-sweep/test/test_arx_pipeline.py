import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


def arx_model(a, b, rounds=64, width=32):
    mask = (1 << width) - 1
    for _ in range(rounds):
        a = (((a << 5) | (a >> (width - 5))) + b) & mask
        b = (((b << 11) | (b >> (width - 11))) & mask) ^ a
    return a, b


@cocotb.test()
async def test_arx_data_bringup(dut):
    cocotb.start_soon(Clock(dut.clk, 2, unit="ns").start())
    dut.rst_n.value = 1
    dut.valid_i.value = 0

    expected = []
    inputs = [
        (0x12345678 + index, 0x9ABCDEF0 ^ (index * 0x11111111))
        for index in range(12)
    ]
    for a, b in inputs:
        await FallingEdge(dut.clk)
        dut.a_i.value = a
        dut.b_i.value = b
        dut.valid_i.value = 1
        expected.append(arx_model(a, b))
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.valid_o.value == 1:
            assert (int(dut.a_o.value), int(dut.b_o.value)) == expected.pop(0)

    await FallingEdge(dut.clk)
    dut.valid_i.value = 0
    for _ in range(80):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.valid_o.value == 1:
            assert (int(dut.a_o.value), int(dut.b_o.value)) == expected.pop(0)
        if not expected:
            break

    assert not expected
