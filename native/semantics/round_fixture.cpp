// SPDX-License-Identifier: GPL-2.0-or-later
#include "fp_fixture.h"
#include <cmath>
static uint64_t get64(const uint8_t* p){uint64_t v;std::memcpy(&v,p,8);return v;}
static void put64(uint8_t* p,uint64_t v){std::memcpy(p,&v,8);}
__declspec(noinline) static unsigned reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec,unsigned imm,unsigned control){
 std::memcpy(out,m.vectors,sizeof out);std::memcpy(out[spec.destination],m.vectors[1],16);std::memset(out[spec.destination]+16,0,16);
 uint64_t bits=get64(spec.memory?m.backing+3:m.vectors[2]),mag=bits&0x7fffffffffffffffULL,sign=bits&0x8000000000000000ULL,result=bits;unsigned raised=0;
 if(mag>0x7ff0000000000000ULL){if(!(mag&0x8000000000000ULL))raised=1;result|=0x8000000000000ULL;}
 else if((control&64)&&mag<0x10000000000000ULL)result=sign;
 else if(mag&&mag<0x4330000000000000ULL){
  double value;std::memcpy(&value,&bits,8);unsigned mode=(imm&4)?(control>>13)&3:imm&3;double rounded;
  if(mode==1)rounded=std::floor(value);else if(mode==2)rounded=std::ceil(value);else if(mode==3)rounded=std::trunc(value);
  else {double magnitude=std::abs(value),lower=std::floor(magnitude),fraction=magnitude-lower;double absolute=lower+((fraction>0.5||(fraction==0.5&&std::fmod(lower,2.0)!=0))?1.0:0.0);rounded=std::copysign(absolute,value);}
  if(rounded!=value&&!(imm&8))raised|=32;std::memcpy(&result,&rounded,8);
 }
 put64(out[spec.destination],result);return raised;
}
int main(){
 static const uint64_t values[]={0,0x8000000000000000ULL,1,0x8000000000000001ULL,0x000fffffffffffffULL,0x800fffffffffffffULL,0x0010000000000000ULL,0x8010000000000000ULL,0x3ff8000000000000ULL,0xbff8000000000000ULL,0x3fe0000000000000ULL,0xbfe0000000000000ULL,0x7ff0000000000000ULL,0xfff0000000000000ULL,0x7ff8000000000000ULL,0xfff8000000000000ULL,0x7ff0000000000001ULL,0xfff0000000000001ULL,0x7fffffffffffffffULL,0xffffffffffffffffULL,0x3fefffffffffffffULL,0x3ff0000000000001ULL,0x7fefffffffffffffULL,0xffefffffffffffffULL,0x4004000000000000ULL,0xc004000000000000ULL,0x432fffffffffffffULL,0xc32fffffffffffffULL,0x4330000000000000ULL,0x3fe0000000000001ULL,0xbfe0000000000001ULL,0x3fdfffffffffffffULL};
 static const unsigned masks[]={0x1f80,0,0x1f00,0xf80};unsigned saved=_mm_getcsr();uint64_t cases=0,faults=0;
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned test=0;test<64;++test)for(unsigned setting=0;setting<64;++setting){
  const auto& spec=specs[form];guest={};setup(guest,guest_state,spec);uint64_t value=test<32?values[test]:(uint64_t(next())<<32)|next();put64(guest.vectors[2],value);put64(guest.backing+3,value);std::memcpy(&guest_state.vec[2].ymm,guest.vectors[2],32);
  unsigned control=masks[setting/16]|((setting%4)<<13)|((setting&4)?0x40:0)|((setting&8)?0x8000:0);if(test&1)control|=63;
  guest_state.x87.fxsave.mxcsr.flat=control;expected_state=guest_state;initial_memory=guest;alignas(32) uint8_t ref[4][32],observed[4][32];_mm_setcsr(0x1f80);
  unsigned raised=reference(ref,guest,spec,immediates[form],control),unmasked=raised&~(control>>7)&63;bool should_fault=unmasked!=0;expected_state.x87.fxsave.mxcsr.flat=control|raised;
  if(!should_fault)std::memcpy(&expected_state.vec[spec.destination].ymm,ref[spec.destination],32);
  unsigned host_control=0x1f80|((test%4)<<13)|(setting%64);_mm_setcsr(host_control);native_fault=false;native_raised=native_unmasked=0;returned_memory=nullptr;invoke(lifted[form],spec.pc);
  if(!native_fault){if(should_fault)fail("missing native round fault",form,test,setting);compare(guest,initial_memory,guest_state,expected_state,returned_memory,spec,form,test,setting);}
  if(_mm_getcsr()!=host_control||native_fault!=should_fault)fail("host MXCSR/native round fault",form,test,setting);
  if(native_fault){if(native_raised!=raised||native_unmasked!=unmasked||std::memcmp(&guest_state,&expected_state,sizeof guest_state)||guest.return_reads||guest.returned||guest.vector_bytes!=(spec.memory?spec.width:0)||std::memcmp(guest.vectors,initial_memory.vectors,sizeof guest.vectors)||std::memcmp(guest.backing,initial_memory.backing,sizeof guest.backing)||std::memcmp(guest.stack,initial_memory.stack,sizeof guest.stack))fail("precise round fault State/memory/PC",form,test,setting);++faults;}
  hardware_run(hardware[form],guest.vectors,observed,guest.backing+3,control);
  if(bool(fault.code)!=should_fault||fault.csr!=(control|raised))fail("hardware round fault/MXCSR",form,test,setting);
  if(!fault.code){if(std::memcmp(observed,ref,sizeof ref))fail("hardware round/reference",form,test,setting);}
  else for(unsigned r=0;r<4;++r)if(std::memcmp(fault.vectors[r],guest.vectors[r],16))fail("hardware round fault preserved XMM",form,test,setting);
  ++cases;
 }
 _mm_setcsr(saved);std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"precise_native_faults\":%llu,\"forms\":4,\"immediates\":256,\"mxcsr_settings\":64,\"game_code_execution\":false,\"ps4_exception_delivery\":false}\n",(unsigned long long)cases,(unsigned long long)faults);
}
