import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ReadOnly, RisingEdge


def gf_multiply(a, b, width=10, polynomial=0x409):
    product = 0
    for _ in range(width):
        if b & 1:
            product ^= a
        b >>= 1
        reduction = polynomial if a & (1 << (width - 1)) else 0
        a = ((a << 1) ^ reduction) & ((1 << width) - 1)
    return product


def polynomial_value(coefficients, point):
    accumulator = 0
    for coefficient in reversed(coefficients):
        accumulator = gf_multiply(accumulator, point) ^ coefficient
    return accumulator


@cocotb.test()
async def test_rs_data_bringup(dut):
    cocotb.start_soon(Clock(dut.clk, 2, unit="ns").start())
    dut.rst_n.value = 1
    dut.valid_i.value = 0

    roots = (2, 5)
    coefficients = [gf_multiply(*roots), roots[0] ^ roots[1], 1] + [0] * 61
    dut.coefficients_i.value = sum(
        value << (10 * index) for index, value in enumerate(coefficients)
    )
    dut.load_coefficients_i.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.load_coefficients_i.value = 0

    expected = []
    for point in range(12):
        dut.x_i.value = point
        dut.valid_i.value = 1
        expected.append(polynomial_value(coefficients, point))
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.valid_o.value == 1:
            reference = expected.pop(0)
            assert int(dut.value_o.value) == reference
            assert int(dut.root_o.value) == (reference == 0)
        await FallingEdge(dut.clk)

    dut.valid_i.value = 0
    for _ in range(80):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.valid_o.value == 1:
            reference = expected.pop(0)
            assert int(dut.value_o.value) == reference
            assert int(dut.root_o.value) == (reference == 0)
        if not expected:
            break

    assert not expected
