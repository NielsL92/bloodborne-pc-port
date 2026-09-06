// SPDX-License-Identifier: GPL-2.0-or-later
#include "fp_fixture.h"
static uint32_t get32(const uint8_t* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(uint8_t* p,uint32_t v){std::memcpy(p,&v,4);}
static bool nan(uint32_t v){return (v&0x7fffffff)>0x7f800000;}
static bool denormal(uint32_t v){return (v&0x7fffffff)!=0&&(v&0x7f800000)==0;}
__declspec(noinline) static unsigned reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec,unsigned op,unsigned control){
 std::memcpy(out,m.vectors,sizeof out);const auto* second=spec.memory?m.backing+3:m.vectors[2];unsigned raised=0;
 for(unsigned i=0;i<spec.width/4;++i){uint32_t x=get32(m.vectors[1]+i*4),y=get32(second+i*4);bool invalid=nan(x)||nan(y);
  if(control&0x40){if(denormal(x))x&=0x80000000;if(denormal(y))y&=0x80000000;}
  else if(!invalid&&(denormal(x)||denormal(y)))raised|=2;
  uint32_t result=y;if(invalid)raised|=1;else {float a,b;std::memcpy(&a,&x,4);std::memcpy(&b,&y,4);if(op==OP_VMINPS?double(a)<double(b):double(a)>double(b))result=x;}
  put32(out[spec.destination]+i*4,result);
 }
 if(spec.width==16)std::memset(out[spec.destination]+16,0,16);return raised;
}
int main(){
 static const uint32_t values[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0x3f7fffff,0x3f800001,0x7f7fffff,0xff7fffff};
 static const unsigned masks[]={0x1f80,0,0x1f00,0x1e80,0xf80,0x1e00,0xe00,0x180};unsigned saved=_mm_getcsr();uint64_t cases=0,faults=0;
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned test=0;test<768;++test)for(unsigned setting=0;setting<128;++setting){
  const auto& spec=specs[form];guest={};setup(guest,guest_state,spec);
  if(test<640)for(unsigned lane=0;lane<8;++lane){uint32_t x,y;if(test<576){x=lane?0x3f800000:values[test/24];y=lane?0x3f800000:values[test%24];}else{x=values[(test+lane)%24];y=values[(test*7+lane*3)%24];}put32(guest.vectors[1]+lane*4,x);put32(guest.vectors[2]+lane*4,y);put32(guest.backing+3+lane*4,y);}
  for(unsigned r=1;r<=2;++r)std::memcpy(&guest_state.vec[r].ymm,guest.vectors[r],32);
  unsigned control=masks[setting/16]|((setting%4)<<13)|((setting&4)?0x40:0)|((setting&8)?0x8000:0);if(test&1)control|=0x3f;
  guest_state.x87.fxsave.mxcsr.flat=control;expected_state=guest_state;initial_memory=guest;
  alignas(32) uint8_t ref[4][32],observed[4][32];_mm_setcsr(0x1f80);unsigned raised=reference(ref,guest,spec,operations[form],control);unsigned unmasked=raised&~(control>>7)&63;bool should_fault=unmasked!=0;
  expected_state.x87.fxsave.mxcsr.flat=control|raised;if(!should_fault)std::memcpy(&expected_state.vec[spec.destination].ymm,ref[spec.destination],32);
  unsigned host_control=0x1f80|((test%4)<<13)|(setting%64);_mm_setcsr(host_control);native_fault=false;native_raised=native_unmasked=0;
  returned_memory=nullptr;invoke(lifted[form],spec.pc);if(!native_fault){if(should_fault)fail("missing native fault",form,test,setting);compare(guest,initial_memory,guest_state,expected_state,returned_memory,spec,form,test,setting);}
  if(_mm_getcsr()!=host_control)fail("host MXCSR changed",form,test,setting);
  if(native_fault!=should_fault)fail("native fault decision",form,test,setting);
  if(native_fault){if(std::memcmp(&guest_state,&expected_state,sizeof guest_state)){for(unsigned byte=0;byte<sizeof guest_state;++byte)if(reinterpret_cast<const uint8_t*>(&guest_state)[byte]!=reinterpret_cast<const uint8_t*>(&expected_state)[byte])std::fprintf(stderr,"state byte %u got=%02x expected=%02x\n",byte,reinterpret_cast<const uint8_t*>(&guest_state)[byte],reinterpret_cast<const uint8_t*>(&expected_state)[byte]);}if(native_raised!=raised||native_unmasked!=unmasked)std::fprintf(stderr,"fault flags got=%x/%x expected=%x/%x pc=%llx expected_pc=%llx\n",native_raised,native_unmasked,raised,unmasked,(unsigned long long)guest_state.gpr.rip.qword,(unsigned long long)expected_state.gpr.rip.qword);if(native_raised!=raised||native_unmasked!=unmasked||std::memcmp(&guest_state,&expected_state,sizeof guest_state)||guest.return_reads||guest.returned||guest.vector_bytes!=(spec.memory?spec.width:0)||std::memcmp(guest.vectors,initial_memory.vectors,sizeof guest.vectors)||std::memcmp(guest.backing,initial_memory.backing,sizeof guest.backing)||std::memcmp(guest.stack,initial_memory.stack,sizeof guest.stack))fail("precise native fault State/memory/PC",form,test,setting);++faults;}
  hardware_run(hardware[form],guest.vectors,observed,guest.backing+3,control);
  if(bool(fault.code)!=should_fault||fault.csr!=(control|raised))fail("hardware fault/MXCSR",form,test,setting);
  if(!fault.code){if(std::memcmp(observed,ref,sizeof ref))fail("hardware/reference result",form,test,setting);}
  else for(unsigned r=0;r<4;++r)if(std::memcmp(fault.vectors[r],guest.vectors[r],16))fail("hardware fault preserved XMM",form,test,setting);
  ++cases;
 }
 _mm_setcsr(saved);std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"precise_native_faults\":%llu,\"forms\":16,\"mxcsr_settings\":128,\"game_code_execution\":false,\"ps4_exception_delivery\":false}\n",(unsigned long long)cases,(unsigned long long)faults);
}
