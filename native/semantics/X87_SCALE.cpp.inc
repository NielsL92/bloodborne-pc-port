// SPDX-License-Identifier: Apache-2.0
// PC-independent, integer power-of-two scaling in canonical guest state.
// BB_REPLACE_SELECTOR: FSCALE
#include "x87_numeric.h"
namespace {
DEF_SEM(BBX87Scale,PC pc,I16 fop){
 BBX87Pending(memory,state);auto cw=state.x87.fxsave.cwd.flat;bool empty=!BBX87Occupied(state,0)||!BBX87Occupied(state,1);BBX87ArithmeticResult value{};
 if(empty){value.significand=0xc000000000000000ULL;value.sign_exponent=0xffff;value.flags=1;}
 else{auto a=BBX87Read(&state.st.elems[0].val),b=BBX87Read(&state.st.elems[1].val);__bb_x87_scale(a.significand,a.sign_exponent,b.significand,b.sign_exponent,cw,&value);if(value.unsupported)__bb_native_x87_unsupported(memory,&state,value.unsupported);}
 BBX87SetStatus(state,BBX87Status(state)&~uint16_t(0x200));bool unmasked=value.flags&&BBX87Raise(state,value.flags,empty);bool blocked=(value.flags&~cw&3)!=0;
 if(!blocked&&value.rounded_up)BBX87SetStatus(state,BBX87Status(state)|0x200);BBX87Instruction(memory,state,Read(pc),Read(fop),false,0,unmasked);
 if(blocked)return memory;BBX87Write(&state.st.elems[0].val,{value.significand,value.sign_exponent});BBX87Occupy(state,0);return memory;
}
}
DEF_ISEL(FSCALE)=BBX87Scale;
