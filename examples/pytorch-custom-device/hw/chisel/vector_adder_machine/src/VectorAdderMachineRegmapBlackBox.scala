package vector_adder_machine

import chisel3._
import chisel3.util._

class VectorAdderMachineRegmapBlackBox extends BlackBox {
  override def desiredName: String = "vector_adder_machine_regmap_wrapper"
  val io = IO(new Bundle {
    val hwif = new VectorAdderMachineRegmapHwifBundle()
    val s_axil = new VectorAdderMachineRegmapAxi4LiteBundle()
    val clk = Input(Clock())
    val rst = Input(Bool())
  })
}
