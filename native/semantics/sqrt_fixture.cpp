// SPDX-License-Identifier: GPL-2.0-or-later
#include "fp_fixture.h"
#include <cmath>
static uint32_t get32(const uint8_t* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(uint8_t* p,uint32_t v){std::memcpy(p,&v,4);}
__declspec(noinline) static unsigned reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec,unsigned control){
 std::memcpy(out,m.vectors,sizeof out);const auto* source=spec.memory?m.backing+3:m.vectors[2];unsigned raised=0;bool precision=false;
 for(unsigned word=0;word<spec.width/4;++word){uint32_t bits=get32(source+4*word),mag=bits&0x7fffffff,sign=bits&0x80000000,result=bits;
  if(mag>0x7f800000){if(!(bits&0x400000))raised|=1;result|=0x400000;}
  else if((control&64)&&mag<0x800000)result=sign;
  else if(!mag){}
  else if(sign){result=0xffc00000;raised|=1;}
  else if(mag!=0x7f800000){
   if(mag<0x800000)raised|=2;float value;std::memcpy(&value,&bits,4);double square_root=std::sqrt(double(value));float candidate=float(square_root);std::memcpy(&result,&candidate,4);unsigned mode=(control>>13)&3;
   if((mode==1||mode==3)&&double(candidate)>square_root)--result;else if(mode==2&&double(candidate)<square_root)++result;
   std::memcpy(&candidate,&result,4);precision|=double(candidate)*double(candidate)!=double(value);
  }
  put32(out[spec.destination]+4*word,result);
 }
 if(precision&&!(raised&~(control>>7)&3))raised|=32;
 if(spec.width==16)std::memset(out[spec.destination]+16,0,16);return raised;
}
int main(){
 static const uint32_t edge[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x40800000,0xc0800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0x3f7fffff,0x3f800001,0x00800001,0x007ffffe,0x01000000,0x7f000000,0x3eaaaaab,0x3f000000};
 static const uint32_t mantissa[]={0,1,2,0x3fffff,0x400000,0x400001,0x7ffffe,0x7fffff};static const unsigned masks[]={0x1f80,0,0x1f00,0x1e80,0xf80,0x1e00,0xe00,0x180};unsigned saved=_mm_getcsr();uint64_t cases=0,faults=0;
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned test=0;test<4096;++test)for(unsigned setting=0;setting<128;++setting){
  const auto& spec=specs[form];guest={};setup(guest,guest_state,spec);
  for(unsigned lane=0;lane<8;++lane){uint32_t value;
   if(test<32)value=edge[test];else if(test<2064)value=((1+(test-32)/8)<<23)|mantissa[(test-32)%8];else if(test<2088)value=uint32_t(1)<<(test-2064);else if(test<2152)value=edge[(test+lane*3)%32];else value=next();
   put32(guest.vectors[2]+4*lane,value);put32(guest.backing+3+4*lane,value);
  }
  std::memcpy(&guest_state.vec[2].ymm,guest.vectors[2],32);unsigned control=masks[setting/16]|((setting%4)<<13)|((setting&4)?0x40:0)|((setting&8)?0x8000:0);if(test&1)control|=63;
  guest_state.x87.fxsave.mxcsr.flat=control;expected_state=guest_state;initial_memory=guest;alignas(32) uint8_t ref[4][32],observed[4][32];_mm_setcsr(0x1f80);
  unsigned raised=reference(ref,guest,spec,control),unmasked=raised&~(control>>7)&63;bool should_fault=unmasked!=0;expected_state.x87.fxsave.mxcsr.flat=control|raised;
  if(!should_fault)std::memcpy(&expected_state.vec[spec.destination].ymm,ref[spec.destination],32);
  unsigned host_control=0x1f80|((test%4)<<13)|(setting%64);_mm_setcsr(host_control);native_fault=false;native_raised=native_unmasked=0;returned_memory=nullptr;invoke(lifted[form],spec.pc);
  if(!native_fault){if(should_fault)fail("missing native sqrt fault",form,test,setting);compare(guest,initial_memory,guest_state,expected_state,returned_memory,spec,form,test,setting);}
  if(_mm_getcsr()!=host_control||native_fault!=should_fault)fail("host MXCSR/native sqrt fault",form,test,setting);
  if(native_fault){if(native_raised!=raised||native_unmasked!=unmasked||std::memcmp(&guest_state,&expected_state,sizeof guest_state)||guest.return_reads||guest.returned||guest.vector_bytes!=(spec.memory?spec.width:0)||std::memcmp(guest.vectors,initial_memory.vectors,sizeof guest.vectors)||std::memcmp(guest.backing,initial_memory.backing,sizeof guest.backing)||std::memcmp(guest.stack,initial_memory.stack,sizeof guest.stack))fail("precise sqrt fault State/memory/PC",form,test,setting);++faults;}
  hardware_run(hardware[form],guest.vectors,observed,guest.backing+3,control);
  if(bool(fault.code)!=should_fault||fault.csr!=(control|raised))fail("hardware sqrt fault/MXCSR",form,test,setting);
  if(!fault.code){if(std::memcmp(observed,ref,sizeof ref))fail("hardware sqrt/reference",form,test,setting);}
  else for(unsigned r=0;r<4;++r)if(std::memcmp(fault.vectors[r],guest.vectors[r],16))fail("hardware sqrt fault preserved XMM",form,test,setting);
  ++cases;
 }
 _mm_setcsr(saved);std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"precise_native_faults\":%llu,\"forms\":6,\"mxcsr_settings\":128,\"game_code_execution\":false,\"ps4_exception_delivery\":false}\n",(unsigned long long)cases,(unsigned long long)faults);
}
