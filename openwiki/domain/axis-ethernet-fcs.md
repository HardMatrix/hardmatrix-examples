---
type: Hardware Domain Concept
title: AXI Ethernet FCS Inserter
description: Behavioral contract, CRC semantics, backpressure handling, and verification guidance for the byte-wide AXI4-Stream Ethernet FCS example.
tags: [axis4-stream, ethernet, crc32, systemverilog]
---

# AXI Ethernet FCS inserter

## Purpose

`examples/axis-eth-fcs` demonstrates a small, synthesizable packet transform: copy a byte-wide AXI4-Stream payload and append the standard four-byte Ethernet CRC-32/FCS. Its behavior and packaging make it the compact entry point to the repository's [architecture](../architecture/overview.md).

## Stream contract

The shared `axis_if` interface contains `tdata`, `tvalid`, `tready`, and `tlast`; a transfer occurs when valid and ready are both asserted. There is no `tkeep`, so a beat always represents one complete byte in this example.

`axis_eth_fcs_insert` has two states:

1. **Bypass payload** — output valid/data mirror the input and output ready propagates to input ready. Each accepted byte advances the CRC.
2. **Send FCS** — upstream ready is low; the saved FCS is emitted over four accepted output beats.

The input payload's final `tlast` is consumed as an internal boundary and is not forwarded. Downstream `tlast` is asserted only with FCS byte 3. The observable packet is therefore payload plus FCS, not a payload packet followed by a second packet.

There is no packet buffer or overlap. Payload throughput is one byte per cycle when unstalled, followed by four FCS cycles before the next packet can begin. FCS state advances only on an output handshake, keeping output data stable under backpressure.

## CRC contract

The implementation in `rtl/eth_crc32_byte.sv` and `rtl/axis_eth_fcs_insert.sv` uses:

- initial CRC `0xFFFFFFFF`;
- reflected polynomial `0xEDB88320`;
- least-significant-bit-first processing within each byte;
- final bitwise complement;
- least-significant-byte-first FCS emission.

These choices collectively match `zlib.crc32`; changing only one ordering or inversion rule produces an incompatible checksum. On the accepted final payload byte, the design saves `~next_crc`, resets the running CRC for the next packet, and enters FCS emission.

## Reset and interface assertions

The DUT uses an active-low synchronous reset in its sequential processes. The shared interface adds simulation assertions for valid behavior around reset, data/`tlast` stability while stalled, and unknown values on valid transfers. Treat reset-policy changes as both a DUT and assertion-contract change.

The module implicitly assumes eight-bit `tdata`: the CRC consumes eight bits and each FCS beat selects one byte. No local assertion enforces this, so widening the interface is not a parameter-only change.

## Verification model

`test/tb_axis_eth_fcs_insert.sv` bridges flat cocotb signals to two `axis_if` instances. `test/test_axis_eth_fcs_insert.py`:

- records only accepted input bytes;
- predicts unchanged payload beats with `tlast=0`;
- appends `zlib.crc32(payload)` as four little-endian bytes;
- exercises directed/random packet lengths with randomized output readiness;
- checks the standard `"123456789" → 0xCBF43926` vector.

The test uses shared drivers and monitors from `shared/python/utils/tb_utils`. The [integration page](../integrations/interfaces.md) explains that reusable support; the exact FuseSoC test/lint commands are in the [testing runbook](../operations/testing-runbook.md).

## Change checklist

When changing this block:

1. Preserve handshake gating for every CRC or FCS state update.
2. Confirm whether downstream packet-boundary semantics intentionally change.
3. Keep reflected bit order, complement, and wire byte order aligned.
4. Run both FuseSoC `test` and `lint` targets.
5. Add tests for any new width, partial-beat, buffering, or reset behavior.

Current coverage does not explicitly test source-valid gaps, reset during payload/FCS, zero-length frames, or deterministic long stalls. Empty frames and partial bytes cannot be represented by the existing interface.