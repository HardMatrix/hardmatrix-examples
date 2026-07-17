package vector_adder_machine

import chisel3._
import chisel3.util._

class VectorAdderUnit(numElements: Int, elementWidth: Int) extends Module {
  require(numElements > 0, "numElements must be greater than 0")
  require(elementWidth > 0, "elementWidth must be greater than 0")

  val io = IO(new Bundle {
    val op = Input(UInt(8.W))
    val out = Irrevocable(Vec(numElements, UInt(elementWidth.W)))
    val in = Flipped(Irrevocable(Vec(2, Vec(numElements, UInt(elementWidth.W)))))
    val error = Output(Bool())
  })

  val OP_ADD = 1.U(8.W)
  val OP_SUB = 2.U(8.W)

  val opReg = RegEnable(io.op, io.in.fire)
  val inDataR = RegEnable(io.in.bits, io.in.fire)
  val start = RegNext(io.in.fire, false.B)

  val running = Wire(Bool())
  val (count, last) = Counter(running, numElements)

  val outData = Reg(chiselTypeOf(io.out.bits))
  val errorReg = RegInit(false.B)

  running := start || (count > 0.U)

  when (running) {
    val result = MuxCase(inDataR(0)(count) + inDataR(1)(count), Seq(
      (opReg === OP_ADD) -> (inDataR(0)(count) + inDataR(1)(count)),
      (opReg === OP_SUB) -> (inDataR(0)(count) - inDataR(1)(count))
    ))
    outData(count) := result
  }

  // Flag error on unknown op (detected at start)
  when (start) {
    errorReg := !(opReg === OP_ADD || opReg === OP_SUB)
  }.elsewhen(io.out.fire) {
    errorReg := false.B
  }

  io.in.ready := !(running || io.out.valid)
  io.out.bits := outData
  io.out.valid := RegEnable(last, false.B, io.out.fire || last)
  io.error := errorReg
}
