// SPDX-License-Identifier: GPL-2.0-or-later
#include <cstdint>
#define BB_FLAG(name) extern "C" bool __remill_flag_computation_##name(bool value,...)noexcept{return value;}
BB_FLAG(carry) BB_FLAG(overflow) BB_FLAG(sign) BB_FLAG(zero)
#define BB_COMPARE(name) extern "C" bool __remill_compare_##name(bool value)noexcept{return value;}
BB_COMPARE(eq) BB_COMPARE(neq) BB_COMPARE(sge) BB_COMPARE(sgt) BB_COMPARE(sle) BB_COMPARE(slt) BB_COMPARE(uge) BB_COMPARE(ugt) BB_COMPARE(ule) BB_COMPARE(ult)
// Architectural undefined AF values stay outside correctness comparisons.
extern "C" uint8_t __remill_undefined_8()noexcept{return 0;}
