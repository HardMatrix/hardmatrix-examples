package vector_adder_machine

import chisel3._
import chisel3.util._
import _root_.circt.stage.ChiselStage

class VectorAdderMachine(numElements: Int, elementWidth: Int) extends Module {
  val s_axil = IO(new VectorAdderMachineRegmapAxi4LiteBundle())

  val unit = Module(new VectorAdderUnit(numElements, elementWidth))
  val csr = Module(new VectorAdderMachineRegmapBlackBox)
  csr.io.s_axil <> s_axil
  csr.io.clk := clock
  csr.io.rst := reset.asBool

  // Instruction fields
  val opCode = csr.io.hwif.out.instruction.op.value
  val regaAddr = csr.io.hwif.out.instruction.rega.value
  val regbAddr = csr.io.hwif.out.instruction.regb.value
  val destAddr = csr.io.hwif.out.instruction.dest.value

  // Read operand vectors from register file
  val regA = VecInit.tabulate(numElements){i =>
    csr.io.hwif.out.vectors(regaAddr).elems(i).data.value
  }
  val regB = VecInit.tabulate(numElements){i =>
    csr.io.hwif.out.vectors(regbAddr).elems(i).data.value
  }

  // Connect to adder unit
  unit.io.op := opCode
  unit.io.in.bits := VecInit(regA, regB)
  unit.io.in.valid := RegNext(csr.io.hwif.out.instruction.op.swmod, false.B)
  unit.io.out.ready := true.B

  // Write result back to vector register file
  csr.io.hwif.in.vectors.zipWithIndex.foreach{ case(v, idx) =>
    v.elems.zip(unit.io.out.bits).foreach{ case(e, res) =>
      e.data.next := res
      e.data.we := unit.io.out.fire && destAddr === idx.U
    }
  }

  // --- STATUS register logic ---
  val clearActive = csr.io.hwif.out.status.clear.value

  // Default: don't write status fields
  csr.io.hwif.in.status.done.next := false.B
  csr.io.hwif.in.status.done.we := false.B
  csr.io.hwif.in.status.error.next := false.B
  csr.io.hwif.in.status.error.we := false.B
  csr.io.hwif.in.status.clear.next := false.B
  csr.io.hwif.in.status.clear.we := false.B

  // When SW writes clear=1: reset done, error, and auto-clear the clear bit
  when (clearActive) {
    csr.io.hwif.in.status.done.next := false.B
    csr.io.hwif.in.status.done.we := true.B
    csr.io.hwif.in.status.error.next := false.B
    csr.io.hwif.in.status.error.we := true.B
    csr.io.hwif.in.status.clear.next := false.B
    csr.io.hwif.in.status.clear.we := true.B
  }

  // When compute completes: latch done (overrides clear if same cycle)
  when (unit.io.out.fire) {
    csr.io.hwif.in.status.done.next := true.B
    csr.io.hwif.in.status.done.we := true.B
  }

  // When unit reports error: latch error
  when (unit.io.error && unit.io.out.fire) {
    csr.io.hwif.in.status.error.next := true.B
    csr.io.hwif.in.status.error.we := true.B
  }
}

object VectorAdderMachine extends App {
  // Generate Verilog
  val numElements = 4
  val elementWidth = 32

  // Use Circt if available, otherwise default
  ChiselStage.emitSystemVerilogFile(
    new VectorAdderMachine(numElements, elementWidth),
    args,
    firtoolOpts = Array("-disable-all-randomization", "-strip-debug-info")
  )
}
