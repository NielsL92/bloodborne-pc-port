#pragma once
// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
struct BBX87NumericResult {uint64_t significand;uint16_t sign_exponent;uint8_t flags;uint8_t rounded_up;};
extern "C" void __bb_x87_from_f32(uint32_t,uint16_t,BBX87NumericResult*);
extern "C" void __bb_x87_from_f64(uint64_t,uint16_t,BBX87NumericResult*);
extern "C" void __bb_x87_from_i64(int64_t,uint16_t,BBX87NumericResult*);
