from cocotb.triggers import RisingEdge
from cocotb_bus.monitors import BusMonitor


class AXI4Stream(BusMonitor):
    """AXI4-Stream monitor."""

    _signals = ["tvalid", "tdata"]
    _optional_signals = ["tready", "tlast"]

    _default_config = {"firstSymbolInHighOrderBits": True, "capture_tlast": False}

    def __init__(self, entity, name, clock, *, config=None, **kwargs):
        BusMonitor.__init__(self, entity, name, clock, **kwargs)

        self.config = self._default_config.copy()
        if config is None:
            config = {}

        for configoption, value in config.items():
            self.config[configoption] = value
            self.log.debug("Setting config option %s to %s", configoption, str(value))

        self._has_tready = hasattr(self.bus, "tready")
        self._has_tlast = hasattr(self.bus, "tlast")

    async def _monitor_recv(self):
        """Watch the pins and reconstruct transactions."""
        clkedge = RisingEdge(self.clock)

        while True:
            await clkedge
            tvalid = int(self.bus.tvalid.value)
            if tvalid == 1 and (not self._has_tready or int(self.bus.tready.value) == 1):
                tdata_value = int(self.bus.tdata.value)
                if self.config["capture_tlast"] and self._has_tlast:
                    transaction = {"tdata": tdata_value, "tlast": int(self.bus.tlast.value)}
                    self._recv(transaction)
                else:
                    self._recv(tdata_value)
