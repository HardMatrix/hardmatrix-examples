# Testing RTL with cocotb and AXI Stream

Most hardware blocks are easier to trust when they can be compared against a small,
independent model. For many networking blocks, that model can be plain Python.

As a minimal example, consider an AXI-stream Ethernet FCS inserter. The RTL receives
a packet byte by byte, forwards the payload, computes the Ethernet CRC32, and appends
the four FCS bytes before asserting `tlast`.

The Python model is only a few lines:

```python
import zlib

def add_fcs(payload: bytes) -> bytes:
    return payload + zlib.crc32(payload).to_bytes(4, "little")
```

The cocotb test drives packets into the RTL, monitors the input stream, builds the
expected output with `zlib.crc32`, and lets a `cocotb_bus` scoreboard compare every
output beat.

## Why AXI Stream

AXI Stream is a good fit for these examples because it captures the parts we care
about in packet datapaths:

- `tdata` carries the byte or word.
- `tvalid` and `tready` model flow control.
- `tlast` marks packet boundaries.

That means the test is not just checking a function. It is also checking that the
block behaves correctly when data moves through a real streaming interface.

## What the test checks

For each input packet, the test expects:

```text
payload bytes, then fcs[0], fcs[1], fcs[2], fcs[3]
```

with `tlast` asserted only on `fcs[3]`.

If the RTL computes the wrong CRC, sends the FCS in the wrong byte order, drops a
payload byte, or asserts `tlast` at the wrong time, the scoreboard fails.

The useful part is that the RTL and the model are intentionally different. The RTL
implements the streaming hardware. The Python side uses the standard library. When
both agree over many packets, we get a compact but meaningful verification loop.

This is the pattern we use throughout HardMatrix examples: keep the hardware block
small, drive it through the same interface it will use in a larger design, and compare
its behavior against the simplest independent model we can find.
