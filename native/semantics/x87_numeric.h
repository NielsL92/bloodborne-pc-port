#pragma once
// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
struct BBX87NumericResult {uint64_t significand;uint16_t sign_exponent;uint8_t flags;uint8_t rounded_up;};
extern "C" void __bb_x87_from_f32(uint32_t,uint16_t,BBX87NumericResult*);
extern "C" void __bb_x87_from_f64(uint64_t,uint16_t,BBX87NumericResult*);
extern "C" void __bb_x87_from_i64(int64_t,uint16_t,BBX87NumericResult*);

// Destination bits plus numeric facts; the instruction owns trap priority,
// stack effects and whether these facts permit a memory write.
struct BBX87StoreResult {uint64_t bits;uint8_t flags;uint8_t rounded_up;uint8_t tiny;};
extern "C" void __bb_x87_to_f32(uint64_t,uint16_t,uint16_t,BBX87StoreResult*);
extern "C" void __bb_x87_to_f64(uint64_t,uint16_t,uint16_t,BBX87StoreResult*);
extern "C" void __bb_x87_to_i16_trunc(uint64_t,uint16_t,uint16_t,BBX87StoreResult*);
extern "C" void __bb_x87_to_i32_trunc(uint64_t,uint16_t,uint16_t,BBX87StoreResult*);
extern "C" void __bb_x87_to_i64_trunc(uint64_t,uint16_t,uint16_t,BBX87StoreResult*);

struct BBX87ArithmeticResult {uint64_t significand;uint16_t sign_exponent;uint8_t flags;uint8_t rounded_up;uint8_t unsupported;};
extern "C" void __bb_x87_add(uint64_t,uint16_t,uint64_t,uint16_t,uint16_t,BBX87ArithmeticResult*);
extern "C" void __bb_x87_sub(uint64_t,uint16_t,uint64_t,uint16_t,uint16_t,BBX87ArithmeticResult*);
extern "C" void __bb_x87_mul(uint64_t,uint16_t,uint64_t,uint16_t,uint16_t,BBX87ArithmeticResult*);
