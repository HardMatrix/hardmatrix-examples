"""Python abstraction for SystemRDL register description.

Don't override. Generated from:
    hw/chisel/vector_adder_machine/rdl/vector_adder_machine.rdl
"""

from peakrdl_python_simple.regif import access, spec


class instructionReg(access.RegAccess):
    """Instruction Register

    Register for issuing instructions
    """

    op = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='op', type_name='op', orig_type_name=None, external=False, width=8, msb=7, lsb=0, high=7, low=0, is_virtual=False, is_volatile=False, is_sw_writable=True, is_sw_readable=True, is_hw_writable=False, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)
    """Operation code"""

    rega = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='rega', type_name='rega', orig_type_name=None, external=False, width=3, msb=10, lsb=8, high=10, low=8, is_virtual=False, is_volatile=False, is_sw_writable=True, is_sw_readable=True, is_hw_writable=False, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)
    """Register A operand"""

    regb = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='regb', type_name='regb', orig_type_name=None, external=False, width=3, msb=13, lsb=11, high=13, low=11, is_virtual=False, is_volatile=False, is_sw_writable=True, is_sw_readable=True, is_hw_writable=False, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)
    """Register B operand"""

    dest = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='dest', type_name='dest', orig_type_name=None, external=False, width=3, msb=16, lsb=14, high=16, low=14, is_virtual=False, is_volatile=False, is_sw_writable=True, is_sw_readable=True, is_hw_writable=False, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)
    """Destination Register"""


class StatusReg(access.RegAccess):
    """Status Register

    Hardware status: done/error flags set by HW, clear written by SW
    """

    done = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='done', type_name='done', orig_type_name=None, external=False, width=1, msb=0, lsb=0, high=0, low=0, is_virtual=False, is_volatile=True, is_sw_writable=False, is_sw_readable=True, is_hw_writable=True, is_hw_readable=False, implements_storage=False, is_up_counter=False, is_down_counter=False, encode='bool'), field_type=bool)
    """Operation complete"""

    error = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='error', type_name='error', orig_type_name=None, external=False, width=1, msb=1, lsb=1, high=1, low=1, is_virtual=False, is_volatile=True, is_sw_writable=False, is_sw_readable=True, is_hw_writable=True, is_hw_readable=False, implements_storage=False, is_up_counter=False, is_down_counter=False, encode='bool'), field_type=bool)
    """Operation error"""

    clear = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='clear', type_name='clear', orig_type_name=None, external=False, width=1, msb=2, lsb=2, high=2, low=2, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='bool'), field_type=bool)
    """Write 1 to clear done/error (auto-clears)"""


class VectorElementTReg(access.RegAccess):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_1(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_2(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_3(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile(access.RegfileAccess):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=256, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_1(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=260, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_2(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=264, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_3(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=268, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_4(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_5(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_6(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_7(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_1(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_4(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=272, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_5(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=276, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_6(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=280, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_7(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=284, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_8(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_9(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_10(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_11(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_2(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_8(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=288, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_9(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=292, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_10(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=296, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_11(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=300, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_12(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_13(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_14(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_15(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_3(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_12(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=304, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_13(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=308, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_14(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=312, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_15(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=316, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_16(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_17(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_18(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_19(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_4(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_16(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=320, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_17(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=324, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_18(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=328, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_19(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=332, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_20(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_21(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_22(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_23(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_5(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_20(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=336, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_21(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=340, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_22(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=344, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_23(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=348, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_24(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_25(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_26(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_27(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_6(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_24(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=352, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_25(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=356, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_26(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=360, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_27(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=364, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorElementTReg_28(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_29(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_30(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorElementTReg_31(VectorElementTReg):
    """Vector Element

    Single 32-bit element of a vector
    """

    data = access.FieldAccess(specification=spec.FieldNodeSpec(inst_name='data', type_name='data', orig_type_name=None, external=False, width=32, msb=31, lsb=0, high=31, low=0, is_virtual=False, is_volatile=True, is_sw_writable=True, is_sw_readable=True, is_hw_writable=True, is_hw_readable=True, implements_storage=True, is_up_counter=False, is_down_counter=False, encode='int'), field_type=int)


class VectorRegTRegfile_7(VectorRegTRegfile):
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    elems_0 = VectorElementTReg_28(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=256, absolute_address=368, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_1 = VectorElementTReg_29(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=4, raw_absolute_address=256, absolute_address=372, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_2 = VectorElementTReg_30(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=8, raw_absolute_address=256, absolute_address=376, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """

    elems_3 = VectorElementTReg_31(specification=spec.RegNodeSpec(inst_name='elems', type_name='vector_element_t', orig_type_name='vector_element_t', external=False, raw_address_offset=0, address_offset=12, raw_absolute_address=256, absolute_address=380, size=4, total_size=16, is_array=True, array_dimensions=[4], array_stride=4, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=1))
    """Vector Element

    Single 32-bit element of a vector
    """


class VectorAdderMachineRegmapAddrmap(access.AddrmapAccess):
    """Device Register Map"""

    _spec = spec.AddrmapNodeSpec(inst_name='vector_adder_machine_regmap', type_name='vector_adder_machine_regmap', orig_type_name='vector_adder_machine_regmap', external=True, raw_address_offset=0, address_offset=0, raw_absolute_address=0, absolute_address=0, size=384, total_size=384, is_array=False, array_dimensions=None, array_stride=None)
    instruction = instructionReg(specification=spec.RegNodeSpec(inst_name='instruction', type_name='instruction', orig_type_name=None, external=False, raw_address_offset=0, address_offset=0, raw_absolute_address=0, absolute_address=0, size=4, total_size=4, is_array=False, array_dimensions=None, array_stride=None, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=False, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=4))
    """Instruction Register

    Register for issuing instructions
    """

    status = StatusReg(specification=spec.RegNodeSpec(inst_name='status', type_name='status_reg', orig_type_name='status_reg', external=False, raw_address_offset=4, address_offset=4, raw_absolute_address=4, absolute_address=4, size=4, total_size=4, is_array=False, array_dimensions=None, array_stride=None, is_virtual=False, has_sw_writable=True, has_sw_readable=True, has_hw_writable=True, has_hw_readable=True, is_interrupt_reg=False, is_halt_reg=False, field_count=3))
    """Status Register

    Hardware status: done/error flags set by HW, clear written by SW
    """

    vectors_0 = VectorRegTRegfile(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=256, raw_absolute_address=256, absolute_address=256, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_1 = VectorRegTRegfile_1(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=272, raw_absolute_address=256, absolute_address=272, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_2 = VectorRegTRegfile_2(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=288, raw_absolute_address=256, absolute_address=288, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_3 = VectorRegTRegfile_3(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=304, raw_absolute_address=256, absolute_address=304, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_4 = VectorRegTRegfile_4(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=320, raw_absolute_address=256, absolute_address=320, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_5 = VectorRegTRegfile_5(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=336, raw_absolute_address=256, absolute_address=336, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_6 = VectorRegTRegfile_6(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=352, raw_absolute_address=256, absolute_address=352, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """

    vectors_7 = VectorRegTRegfile_7(specification=spec.RegfileNodeSpec(inst_name='vectors', type_name='vector_reg_t', orig_type_name='vector_reg_t', external=False, raw_address_offset=256, address_offset=368, raw_absolute_address=256, absolute_address=368, size=16, total_size=128, is_array=True, array_dimensions=[8], array_stride=16))
    """Vector Register File

    Collection of 4 elements forming a vector
    """
