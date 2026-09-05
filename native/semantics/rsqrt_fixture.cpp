// SPDX-License-Identifier: GPL-2.0-or-later
#include "vector_fixture.h"
#include <cmath>
#include <xmmintrin.h>
static const uint32_t edges[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x40800000,0xc0800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0x3f7fffff,0x3f800001,0x00800001,0x007ffffe,0x01000000,0x7f000000,0x3eaaaaab,0x3f000000};
__declspec(noinline) static double check_value(uint32_t bits,uint32_t output){
 uint32_t magnitude=bits&0x7fffffff,sign=bits&0x80000000;
 if(magnitude>0x7f800000){if(output!=(bits|0x00400000))fail("NaN quieting and payload");return 0;}
 if(magnitude<0x00800000){if(output!=(sign|0x7f800000))fail("signed zero/denormal result");return 0;}
 if(sign){if(output!=0xffc00000)fail("negative normal/infinity indefinite");return 0;}
 if(magnitude==0x7f800000){if(output!=0)fail("positive infinity result");return 0;}
 float input,value;std::memcpy(&input,&bits,4);std::memcpy(&value,&output,4);double exact=1/std::sqrt(double(input));double relative=std::abs((double(value)-exact)/exact);
 if(!std::isfinite(value)||relative>1.5/4096.0)fail("documented approximation bound");return relative;
}
int main(){uint64_t cases=0;double maximum_error=0;unsigned saved=_mm_getcsr();
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned trial=0;trial<2080;++trial){
  const auto& spec=specs[form];Memory original{};State original_state;setup(original,original_state,spec);
  for(unsigned word=0;word<8;++word){uint32_t bits=trial<32?edges[(trial+word)%32]:next();std::memcpy(original.vectors[2]+4*word,&bits,4);std::memcpy(original.backing+3+4*word,&bits,4);}
  std::memcpy(&original_state.vec[2].ymm,original.vectors[2],32);uint8_t invariant[32]{};
  for(unsigned setting=0;setting<32;++setting){
   Memory m=original;State s=original_state;s.gpr.rdi.qword=uint64_t(m.backing+3);s.gpr.rsp.qword=uint64_t(m.stack+4);
   unsigned control=((setting&3)<<13)|((setting&4)?0x40:0)|((setting&8)?0x8000:0)|((setting&16)?0x1f80:0)|(trial&63);
   s.x87.fxsave.mxcsr.flat=control;State expected=s;Memory initial=m;alignas(32) uint8_t observed[4][32];
   _mm_setcsr(control);auto* result=lifted[form](&s,spec.pc,&m);unsigned after_aot=_mm_getcsr();
   hardware[form](m.vectors,observed,m.backing+3);unsigned after_hardware=_mm_getcsr();_mm_setcsr(0x1f80);
   if(after_aot!=control||after_hardware!=control)fail("MXCSR status/control preservation",form,trial,setting);
   if(setting==0)std::memcpy(invariant,observed[spec.destination],32);else if(std::memcmp(invariant,observed[spec.destination],32))fail("rounding/DAZ/FTZ/mask invariance",form,trial,setting);
   std::memcpy(&expected.vec[spec.destination].ymm,observed[spec.destination],32);
   for(unsigned reg=0;reg<4;++reg)if(reg!=spec.destination&&std::memcmp(observed[reg],m.vectors[reg],32))fail("hardware preserved registers",form,trial,setting);
   if(spec.width==16)for(unsigned byte=16;byte<32;++byte)if(observed[spec.destination][byte])fail("VEX128 upper clearing",form,trial,setting);
   for(unsigned word=0;word<spec.width/4;++word){uint32_t bits,value;const auto* source=spec.memory?m.backing+3:m.vectors[2];std::memcpy(&bits,source+4*word,4);std::memcpy(&value,observed[spec.destination]+4*word,4);double error=check_value(bits,value);if(error>maximum_error)maximum_error=error;}
   compare(m,initial,s,expected,result,spec,form,trial,setting);++cases;
  }
 }
 _mm_setcsr(saved);
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":6,\"mxcsr_settings\":32,\"maximum_relative_error\":%.17g,\"game_code_execution\":false,\"jaguar_bit_exactness\":\"unverified\"}\n",(unsigned long long)cases,maximum_error);
}
