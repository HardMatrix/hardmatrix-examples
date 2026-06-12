from typing import Any, Callable, List

from cocotb.triggers import Event, ReadOnly, RisingEdge, Timer
from cocotb_bus.drivers import ValidatedBusDriver

from utils.tb_utils.test_helpers import (
    sigma_delta_generator,
    weighted_random_valid_generator,
)


class AXI4Stream(ValidatedBusDriver):
    """AXI4 Streaming Interface Driver."""

    _signals = ["tvalid", "tdata"]
    _optional_signals = ["tready", "tlast"]

    _default_config = {"firstSymbolInHighOrderBits": True, "drive_external_tlast": False}

    def __init__(self, entity, name, clock, *, config=None, valid_rate=None, **kwargs):
        if valid_rate is not None:
            self.valid_generator = sigma_delta_generator(valid_rate)
        else:
            self.valid_generator = weighted_random_valid_generator()
        ValidatedBusDriver.__init__(
            self, entity, name, clock, valid_generator=self.valid_generator, **kwargs
        )

        self.config = self.__class__._default_config.copy()
        if config is None:
            config = {}

        for configoption, value in config.items():
            self.config[configoption] = value
            self.log.debug("Setting config option %s to %s", configoption, str(value))

        self.bus.tvalid.value = 0
        self.bus.tlast.value = 0
        self.bus.tdata.value = 0
        self._clkedge = RisingEdge(self.clock)
        self._has_tready = hasattr(self.bus, "tready")
        self._has_tlast = hasattr(self.bus, "tlast")

    def set_valid_rate(self, valid_rate):
        if self.valid_generator is None:
            self.set_valid_generator(sigma_delta_generator(valid_rate))
        elif hasattr(self.valid_generator, "set_valid_rate"):
            self.valid_generator.set_valid_rate(valid_rate)
        else:
            self.set_valid_generator(sigma_delta_generator(valid_rate))

    async def _wait_ready(self):
        """Wait for a ready cycle on the bus before continuing."""
        await ReadOnly()
        while int(self.bus.tready.value) != 1:
            await self._clkedge
            await ReadOnly()

    async def _synchronize(self, sync=True):
        self.bus.tvalid.value = 0

        if sync:
            await self._clkedge

        if not self.on:
            self.bus.tvalid.value = 0
            for _ in range(self.off):
                await self._clkedge
            self._next_valids()

        if self.on is not True and self.on:
            self.on -= 1

    async def _finish_transaction(self):
        if self._has_tready:
            await self._wait_ready()

        await self._clkedge
        self.bus.tvalid.value = 0

        if self._has_tlast:
            self.bus.tlast.value = 0

        self.bus.tdata.value = 0

    async def _driver_send(self, value, sync=True, pkt_size=None, **kwargs):
        """Send one AXI4-Stream transaction or packet."""
        self.log.debug("Sending AXI4-Stream transmission: %r", value)

        if isinstance(value, list):
            for i, v in enumerate(value):
                if self.config["drive_external_tlast"]:
                    is_last = v["tlast"]
                    tdata = v["tdata"]
                elif pkt_size is not None:
                    tdata = v
                    assert len(value) >= pkt_size, (
                        "AXI4-Stream driver error: list length is smaller than pkt_size"
                    )
                    is_last = (i % pkt_size) == pkt_size - 1
                else:
                    tdata = v
                    is_last = i == len(value) - 1
                await self._drive_value(
                    tdata, sync=(sync if i == 0 else False), tlast=int(is_last), **kwargs
                )
        else:
            await self._drive_value(value, sync=sync, tlast=0, **kwargs)

        self.log.debug("Successfully sent AXI4-Stream transmission: %r", value)

    async def _drive_value(self, value, sync=True, tlast=0, **kwargs):
        await self._synchronize(sync)

        self.bus.tvalid.value = 1
        self.bus.tdata.value = value

        if self._has_tlast:
            self.bus.tlast.value = tlast

        await self._finish_transaction()

    async def send_with_throughput(
        self,
        transaction_rate: float,
        transaction: List[Any],
        pkt_size=None,
        callback: Callable[[Any], Any] = None,
        event: Event = None,
        **kwargs: Any,
    ):
        if pkt_size:
            tdict = [
                [{"tdata": d, "tlast": (i % pkt_size) == (pkt_size - 1)}]
                for i, d in enumerate(transaction)
            ]
        else:
            tdict = transaction

        for trans in tdict[:-1]:
            self.append(trans, callback, event, **kwargs)
            await Timer(transaction_rate, "sec", round_mode="round")

        last_transaction = Event()
        self.append(tdict[-1], callback, last_transaction, **kwargs)
        await Timer(transaction_rate, "sec", round_mode="round")
        await last_transaction.wait()
