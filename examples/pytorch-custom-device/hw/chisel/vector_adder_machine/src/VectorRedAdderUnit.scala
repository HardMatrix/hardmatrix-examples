package vector_adder_machine

import chisel3._
import chisel3.util._

class VectorRedAdderUnit(numElements: Int, elementWidth: Int) extends Module {
  require(numElements > 0, "numElements must be greater than 0")
  require(elementWidth > 0, "elementWidth must be greater than 0")

  val io = IO(new Bundle {
    val in = Flipped(Irrevocable(Vec(numElements, UInt(elementWidth.W))))
    val out = Irrevocable(UInt(elementWidth.W))
  })

  val inDataR = RegEnable(io.in.bits, io.in.fire)
  val start = RegNext(io.in.fire, false.B)

  val running = Wire(Bool())
  val (count, last) = Counter(running, numElements)
  val acc = Reg(chiselTypeOf(io.out.bits))

  running := start || (count > 0.U)

  when (running) {
    acc := Mux(start, inDataR(count), acc + inDataR(count))
  }

  io.in.ready := !(running || io.out.valid)
  io.out.bits := acc
  io.out.valid := RegEnable(last, false.B, io.out.fire || last)
}
