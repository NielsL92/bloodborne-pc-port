// SPDX-License-Identifier: Apache-2.0
// Register arithmetic for the recovered startup graph. Numeric helpers never
// execute guest CPU instructions. Reserved controls are an explicit boundary.
// BB_REPLACE_SELECTOR: FADDP_X87_ST0
// BB_REPLACE_SELECTOR: FSUBP_X87_ST0
// BB_REPLACE_SELECTOR: FSUBRP_X87_ST0
// BB_REPLACE_SELECTOR: FSUB_ST0_X87
// BB_REPLACE_SELECTOR: FMUL_ST0_X87
#include "x87_numeric.h"
extern "C" [[noreturn]] void __bb_native_x87_unsupported(Memory*,State*,uint32_t);
namespace {
template<unsigned Operation,bool Reverse,bool Pop> DEF_SEM(BBX87Arithmetic,RF80W dst,RF80W first,RF80W second,PC pc,I16 fop){
 BBX87Pending(memory,state);auto cw=state.x87.fxsave.cwd.flat;
 if(((cw>>8)&3)==1)__bb_native_x87_unsupported(memory,&state,1);
 bool empty=!BBX87Occupied(state,BBX87Index(state,first))||!BBX87Occupied(state,BBX87Index(state,second));
 BBX87ArithmeticResult value{};if(empty){value.significand=0xc000000000000000ULL;value.sign_exponent=0xffff;value.flags=1;}
 else {auto a=BBX87Read(Reverse?second.val_ref:first.val_ref),b=BBX87Read(Reverse?first.val_ref:second.val_ref);
  if(Operation==0)__bb_x87_add(a.significand,a.sign_exponent,b.significand,b.sign_exponent,cw,&value);
  else if(Operation==1)__bb_x87_sub(a.significand,a.sign_exponent,b.significand,b.sign_exponent,cw,&value);
  else __bb_x87_mul(a.significand,a.sign_exponent,b.significand,b.sign_exponent,cw,&value);
  if(value.unsupported)__bb_native_x87_unsupported(memory,&state,value.unsupported);
 }
 BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));
 bool unmasked=value.flags&&BBX87Raise(state,value.flags,empty);bool blocked=(value.flags&~cw&3)!=0;
 if(!blocked&&value.rounded_up)BBX87SetStatus(state,BBX87Status(state)|0x200);
 BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,unmasked);
 if(blocked)return memory;BBX87Write(dst.val_ref,{value.significand,value.sign_exponent});BBX87Occupy(state,BBX87Index(state,dst));if(Pop)BBX87Pop(state);return memory;
}
}
DEF_ISEL(FADDP_X87_ST0)=BBX87Arithmetic<0,false,true>;
DEF_ISEL(FSUBP_X87_ST0)=BBX87Arithmetic<1,false,true>;
DEF_ISEL(FSUBRP_X87_ST0)=BBX87Arithmetic<1,true,true>;
DEF_ISEL(FSUB_ST0_X87)=BBX87Arithmetic<1,false,false>;
DEF_ISEL(FMUL_ST0_X87)=BBX87Arithmetic<2,false,false>;
