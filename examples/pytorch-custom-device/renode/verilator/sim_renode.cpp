// sim_renode.cpp — Renode Verilator integration adapter for VectorAdderMachine
// Uses Renode's AxiLite bus class from the IntegrationLibrary.
//
// Signal width mismatch: Renode AxiLite uses uint64_t* for addr/data,
// but Verilator generates narrower types (uint16_t for 9-bit addr,
// uint32_t for 32-bit data). We use shadow uint64_t variables and
// sync them to/from the Verilator model in evaluateModel().
//
// Build with: renode/build_verilated_vam.sh

#include <verilated.h>
#include "VVectorAdderMachine.h"
#include "src/renode_bus.h"
#include "src/buses/axilite.h"

static VVectorAdderMachine *top = nullptr;

// Shadow variables (uint64_t) for signals wider than 8 bits.
// Renode's AxiLite bus reads/writes these, and evaluateModel() syncs
// them to/from the actual Verilator ports.
static uint64_t shadow_awaddr = 0;
static uint64_t shadow_wdata  = 0;
static uint64_t shadow_araddr = 0;
static uint64_t shadow_rdata  = 0;

// Sync shadows → Verilator inputs, eval, then Verilator outputs → shadows
static void evaluateModel() {
    // Input shadows → Verilator (narrow types)
    top->s_axil_awaddr = (uint16_t)shadow_awaddr;
    top->s_axil_wdata  = (uint32_t)shadow_wdata;
    top->s_axil_araddr = (uint16_t)shadow_araddr;

    top->eval();

    // Verilator outputs → output shadows
    shadow_rdata = top->s_axil_rdata;
}

RenodeAgent *Init() {
    Verilated::commandArgs(0, (const char**)nullptr);
    top = new VVectorAdderMachine;

    auto *bus = new AxiLite();

    // 1-bit signals — direct pointer (uint8_t matches CData)
    bus->clk     = &top->clock;
    bus->rst     = &top->reset;
    bus->awvalid = &top->s_axil_awvalid;
    bus->awready = &top->s_axil_awready;
    bus->awprot  = &top->s_axil_awprot;
    bus->wvalid  = &top->s_axil_wvalid;
    bus->wready  = &top->s_axil_wready;
    bus->wstrb   = &top->s_axil_wstrb;
    bus->bvalid  = &top->s_axil_bvalid;
    bus->bready  = &top->s_axil_bready;
    bus->bresp   = &top->s_axil_bresp;
    bus->arvalid = &top->s_axil_arvalid;
    bus->arready = &top->s_axil_arready;
    bus->arprot  = &top->s_axil_arprot;
    bus->rvalid  = &top->s_axil_rvalid;
    bus->rready  = &top->s_axil_rready;
    bus->rresp   = &top->s_axil_rresp;

    // Multi-bit signals — point to shadow uint64_t variables
    bus->awaddr = &shadow_awaddr;
    bus->wdata  = &shadow_wdata;
    bus->araddr = &shadow_araddr;
    bus->rdata  = &shadow_rdata;

    bus->evaluateModel = evaluateModel;

    auto *agent = new RenodeAgent();
    agent->addBus(bus);
    agent->connectNative();

    return agent;
}
