// SPDX-License-Identifier: GPL-2.0-or-later
#include "vector_fixture.h"
__declspec(noinline) static void reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec){
 std::memcpy(out,m.vectors,sizeof out);const auto* second=spec.memory?m.backing+3:m.vectors[2];
 for(unsigned base=0;base<spec.width;base+=spec.element_bytes){bool choose_second=(m.vectors[3][base+spec.element_bytes-1]>>7)!=0;std::memcpy(out[spec.destination]+base,(choose_second?second:m.vectors[1])+base,spec.element_bytes);}
 if(spec.width==16)std::memset(out[spec.destination]+16,0,16);
}
int main(){uint64_t cases=0;
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned trial=0;trial<4096;++trial){
  const auto& spec=specs[form];Memory m{};State s;setup(m,s,spec);
  if(trial<256)for(unsigned byte=0;byte<32;++byte)m.vectors[3][byte]=uint8_t(trial);std::memcpy(&s.vec[3].ymm,m.vectors[3],32);
  Memory initial=m;State expected=s;alignas(32) uint8_t ref[4][32],observed[4][32];reference(ref,m,spec);std::memcpy(&expected.vec[spec.destination].ymm,ref[spec.destination],32);
  auto* result=lifted[form](&s,spec.pc,&m);hardware[form](m.vectors,observed,m.backing+3);
  if(std::memcmp(ref,observed,sizeof ref))fail("hardware/reference",form,trial);compare(m,initial,s,expected,result,spec,form,trial);++cases;
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":30,\"game_code_execution\":false}\n",(unsigned long long)cases);
}
