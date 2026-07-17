// Generated Chisel Bundles mirroring peakrdl-regblock hwif structs

package vector_adder_machine

import chisel3._


// --- Status register bundles ---

class vector_adder_machine_regmap__status_reg__done__in_t extends Bundle {
  val next = Bool()
  val we = Bool()
}

class vector_adder_machine_regmap__status_reg__error__in_t extends Bundle {
  val next = Bool()
  val we = Bool()
}

class vector_adder_machine_regmap__status_reg__clear__in_t extends Bundle {
  val next = Bool()
  val we = Bool()
}

class vector_adder_machine_regmap__status_reg__in_t extends Bundle {
  val done = new vector_adder_machine_regmap__status_reg__done__in_t()
  val error = new vector_adder_machine_regmap__status_reg__error__in_t()
  val clear = new vector_adder_machine_regmap__status_reg__clear__in_t()
}

class vector_adder_machine_regmap__status_reg__done__out_t extends Bundle {
  val value = Bool()
}

class vector_adder_machine_regmap__status_reg__error__out_t extends Bundle {
  val value = Bool()
}

class vector_adder_machine_regmap__status_reg__clear__out_t extends Bundle {
  val value = Bool()
}

class vector_adder_machine_regmap__status_reg__out_t extends Bundle {
  val done = new vector_adder_machine_regmap__status_reg__done__out_t()
  val error = new vector_adder_machine_regmap__status_reg__error__out_t()
  val clear = new vector_adder_machine_regmap__status_reg__clear__out_t()
}

// --- Vector element bundles ---

class vector_adder_machine_regmap__vector_element_t__data__in_t extends Bundle {
  val next = UInt(32.W)
  val we = Bool()
}

class vector_adder_machine_regmap__vector_element_t__in_t extends Bundle {
  val data = new vector_adder_machine_regmap__vector_element_t__data__in_t()
}

class vector_adder_machine_regmap__vector_reg_t__in_t extends Bundle {
  val elems = Vec(4, new vector_adder_machine_regmap__vector_element_t__in_t())
}

class vector_adder_machine_regmap__in_t extends Bundle {
  val status = new vector_adder_machine_regmap__status_reg__in_t()
  val vectors = Vec(8, new vector_adder_machine_regmap__vector_reg_t__in_t())
}

class vector_adder_machine_regmap__instruction__op__out_t extends Bundle {
  val value = UInt(8.W)
  val swmod = Bool()
}

class vector_adder_machine_regmap__instruction__rega__out_t extends Bundle {
  val value = UInt(3.W)
}

class vector_adder_machine_regmap__instruction__regb__out_t extends Bundle {
  val value = UInt(3.W)
}

class vector_adder_machine_regmap__instruction__dest__out_t extends Bundle {
  val value = UInt(3.W)
}

class vector_adder_machine_regmap__instruction__out_t extends Bundle {
  val op = new vector_adder_machine_regmap__instruction__op__out_t()
  val rega = new vector_adder_machine_regmap__instruction__rega__out_t()
  val regb = new vector_adder_machine_regmap__instruction__regb__out_t()
  val dest = new vector_adder_machine_regmap__instruction__dest__out_t()
}

class vector_adder_machine_regmap__vector_element_t__data__out_t extends Bundle {
  val value = UInt(32.W)
}

class vector_adder_machine_regmap__vector_element_t__out_t extends Bundle {
  val data = new vector_adder_machine_regmap__vector_element_t__data__out_t()
}

class vector_adder_machine_regmap__vector_reg_t__out_t extends Bundle {
  val elems = Vec(4, new vector_adder_machine_regmap__vector_element_t__out_t())
}

class vector_adder_machine_regmap__out_t extends Bundle {
  val instruction = new vector_adder_machine_regmap__instruction__out_t()
  val status = new vector_adder_machine_regmap__status_reg__out_t()
  val vectors = Vec(8, new vector_adder_machine_regmap__vector_reg_t__out_t())
}

class VectorAdderMachineRegmapHwifBundle extends Bundle {
  val in = Input(new vector_adder_machine_regmap__in_t())
  val out = Output(new vector_adder_machine_regmap__out_t())
}

class VectorAdderMachineRegmapAxi4LiteBundle extends Bundle {
  val awready = Output(Bool())
  val awvalid = Input(Bool())
  val awaddr = Input(UInt(9.W))
  val awprot = Input(UInt(3.W))
  val wready = Output(Bool())
  val wvalid = Input(Bool())
  val wdata = Input(UInt(32.W))
  val wstrb = Input(UInt(4.W))
  val bready = Input(Bool())
  val bvalid = Output(Bool())
  val bresp = Output(UInt(2.W))
  val arready = Output(Bool())
  val arvalid = Input(Bool())
  val araddr = Input(UInt(9.W))
  val arprot = Input(UInt(3.W))
  val rready = Input(Bool())
  val rvalid = Output(Bool())
  val rdata = Output(UInt(32.W))
  val rresp = Output(UInt(2.W))
}
