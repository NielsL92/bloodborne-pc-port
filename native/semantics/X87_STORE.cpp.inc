// SPDX-License-Identifier: Apache-2.0
// Bounded numeric stores: conversion facts are distinct from architectural
// exception priority, write completion and stack-pop decisions.
// BB_REPLACE_SELECTOR: FST_MEMmem32real_ST0
// BB_REPLACE_SELECTOR: FST_MEMm64real_ST0
// BB_REPLACE_SELECTOR: FSTP_MEMmem32real_ST0
// BB_REPLACE_SELECTOR: FSTP_MEMm64real_ST0
// BB_REPLACE_SELECTOR: FISTTP_MEMmem16int_ST0
// BB_REPLACE_SELECTOR: FISTTP_MEMmem32int_ST0
// BB_REPLACE_SELECTOR: FISTTP_MEMm64int_ST0
#include "x87_numeric.h"
namespace {
template<unsigned Width,bool Integer,bool Pop> DEF_SEM(BBX87StoreNumber,M8W dst,RF80W src,PC pc,I16 fop){
 BBX87Pending(memory,state);auto address=AddressOf(dst);__bb_native_x87_check_span(memory,&state,address,Width/8,1,1);BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));
 bool empty=!BBX87Occupied(state,BBX87Index(state,src));BBX87StoreResult value{};unsigned flags=0;bool blocked=false,unmasked=false;auto cw=state.x87.fxsave.cwd.flat;
 if(empty){flags=1;blocked=BBX87Raise(state,1,true);unmasked=blocked;value.bits=Integer?(uint64_t(1)<<(Width-1)):(Width==32?0xffc00000:0xfff8000000000000ULL);}
 else {auto source=BBX87Read(src.val_ref);
  if(Integer){if(Width==16)__bb_x87_to_i16_trunc(source.significand,source.sign_exponent,cw,&value);else if(Width==32)__bb_x87_to_i32_trunc(source.significand,source.sign_exponent,cw,&value);else __bb_x87_to_i64_trunc(source.significand,source.sign_exponent,cw,&value);}
  else if(Width==32)__bb_x87_to_f32(source.significand,source.sign_exponent,cw,&value);else __bb_x87_to_f64(source.significand,source.sign_exponent,cw,&value);
  flags=value.flags;if(flags&1)flags=1;else if((flags&8)&&!(cw&8))flags=8;else if(!Integer&&(value.tiny||(flags&16))&&!(cw&16))flags=16;
  unmasked=flags&&BBX87Raise(state,flags);blocked=(flags&~cw&0x19)!=0;if(!blocked&&value.rounded_up)BBX87SetStatus(state,BBX87Status(state)|0x200);
 }
 BBX87Instruction(memory,state,Read(pc),Read(fop),true,address,unmasked);if(blocked)return memory;for(unsigned i=0;i<Width/8;++i)memory=__remill_write_memory_8(memory,address+i,uint8_t(value.bits>>(i*8)));if(Pop)BBX87Pop(state);return memory;
}
}
DEF_ISEL(FST_MEMmem32real_ST0)=BBX87StoreNumber<32,false,false>;
DEF_ISEL(FST_MEMm64real_ST0)=BBX87StoreNumber<64,false,false>;
DEF_ISEL(FSTP_MEMmem32real_ST0)=BBX87StoreNumber<32,false,true>;
DEF_ISEL(FSTP_MEMm64real_ST0)=BBX87StoreNumber<64,false,true>;
DEF_ISEL(FISTTP_MEMmem16int_ST0)=BBX87StoreNumber<16,true,true>;
DEF_ISEL(FISTTP_MEMmem32int_ST0)=BBX87StoreNumber<32,true,true>;
DEF_ISEL(FISTTP_MEMm64int_ST0)=BBX87StoreNumber<64,true,true>;
