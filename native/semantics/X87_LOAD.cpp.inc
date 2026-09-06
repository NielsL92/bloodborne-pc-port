// SPDX-License-Identifier: Apache-2.0
// Narrow loads convert through bounded native numeric helpers. Stack and x87
// exception behavior remains in the instruction semantics, not the library.
// BB_REPLACE_SELECTOR: FLD_ST0_MEMmem32real
// BB_REPLACE_SELECTOR: FLD_ST0_MEMm64real
// BB_REPLACE_SELECTOR: FILD_ST0_MEMmem16int
// BB_REPLACE_SELECTOR: FILD_ST0_MEMmem32int
// BB_REPLACE_SELECTOR: FILD_ST0_MEMm64int
#include "x87_numeric.h"
namespace {
template<unsigned Width,bool Integer> DEF_SEM(BBX87LoadNumber,RF80W,M8 src,PC pc,I16 fop){
 BBX87Pending(memory,state);auto address=AddressOf(src);__bb_native_x87_check_span(memory,&state,address,Width/8,0,1);uint64_t bits=0;for(unsigned i=0;i<Width/8;++i)bits|=uint64_t(__remill_read_memory_8(memory,address+i))<<(i*8);
 BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool full=BBX87Occupied(state,7);BBX87NumericResult value{};bool blocked=false,unmasked=false;
 if(full){blocked=BBX87Raise(state,1,true,true);unmasked=blocked;auto indefinite=BBX87Indefinite();value.significand=indefinite.significand;value.sign_exponent=indefinite.sign_exponent;}
 else {
  if(Integer){int64_t integer;if(Width==16)integer=int16_t(bits);else if(Width==32)integer=int32_t(bits);else __builtin_memcpy(&integer,&bits,8);__bb_x87_from_i64(integer,state.x87.fxsave.cwd.flat,&value);}
  else if(Width==32)__bb_x87_from_f32(uint32_t(bits),state.x87.fxsave.cwd.flat,&value);else __bb_x87_from_f64(bits,state.x87.fxsave.cwd.flat,&value);
  if(value.flags){unmasked=BBX87Raise(state,value.flags);blocked=unmasked&&(value.flags&1);}
 }
 BBX87RawInstruction(memory,state,Read(pc),Read(fop),true,address,unmasked);if(!blocked)BBX87Push(state,{value.significand,value.sign_exponent});return memory;
}
}
DEF_ISEL(FLD_ST0_MEMmem32real)=BBX87LoadNumber<32,false>;
DEF_ISEL(FLD_ST0_MEMm64real)=BBX87LoadNumber<64,false>;
DEF_ISEL(FILD_ST0_MEMmem16int)=BBX87LoadNumber<16,true>;
DEF_ISEL(FILD_ST0_MEMmem32int)=BBX87LoadNumber<32,true>;
DEF_ISEL(FILD_ST0_MEMm64int)=BBX87LoadNumber<64,true>;
