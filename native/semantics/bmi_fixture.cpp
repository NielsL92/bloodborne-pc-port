// SPDX-License-Identifier: GPL-2.0-or-later
// Authored BMI AOT vs bit-scan reference and compiled hardware instruction forms.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <intrin.h>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory { uint64_t words[3];uint64_t stack[8];unsigned data_reads=0,return_reads=0;unsigned width=0;bool memory_form=false;uint64_t returned=0;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);
using Hardware=uint64_t(*)(uint64_t,uint64_t*);
#include "bmi-entries.h"
[[noreturn]] static void fail(const char* why,unsigned form,uint64_t x){std::fprintf(stderr,"FAIL %s form=%u x=%llx\n",why,form,(unsigned long long)x);std::exit(2);}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){
 if(at==uint64_t(&m->stack[4])){++m->return_reads;return m->stack[4];}
 if(m->memory_form&&m->width==64&&at==uint64_t(&m->words[1])){++m->data_reads;return m->words[1];}
 fail("read64 boundary",0,at);
}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t at){if(m->memory_form&&m->width==32&&at==uint64_t(&m->words[1])){++m->data_reads;return uint32_t(m->words[1]);}fail("read32 boundary",0,at);}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" uint8_t __remill_undefined_8(){return 0;}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
extern "C" Memory* __remill_error(State*,uint64_t at,Memory*){fail("lifter error",0,at);}
extern "C" Memory* __remill_missing_block(State*,uint64_t at,Memory*){fail("missing block",0,at);}
// Independent reference deliberately scans bit positions; this TU disables BMI.
__declspec(noinline) static uint64_t reference(uint64_t value,unsigned width,bool isolate){
 uint64_t result=isolate?0:value;
 for(unsigned bit=0;bit<width;++bit){uint64_t mask=uint64_t(1)<<bit;if(value&mask){result=isolate?mask:(value^mask);break;}}
 return result;
}
int main(){
 int cpu[4];__cpuidex(cpu,7,0);if(!(cpu[1]&(1<<3)))fail("hardware lacks BMI1",0,0);
 uint64_t cases=0,random=0x3a169af092772e41ULL;
 for(unsigned n=0;n<8;++n){unsigned width=(n&1)?64:32;bool mem=bool(n&2),isolate=n>=4;
  for(unsigned trial=0;trial<4352;++trial){
   random^=random<<13;random^=random>>7;random^=random<<17;uint64_t input=random;
   if(trial<64)input=uint64_t(1)<<trial;
   else if(trial<128)input=~(uint64_t(1)<<(trial-64));
   else if(trial<192)input=(uint64_t(1)<<(trial-128))|1;
   else if(trial<256)input=(trial&1)?0:~uint64_t(0);
   uint64_t value=width==32?uint32_t(input):input,expected_value=reference(value,width,isolate);
   uint64_t expected_flags=(uint64_t(isolate?value!=0:value==0))|(uint64_t(expected_value==0)<<6)|(((expected_value>>(width-1))&1)<<7);
   Memory m{};m.width=width;m.memory_form=mem;m.words[0]=m.words[2]=0xababababababababULL;m.words[1]=input;
   for(auto& w:m.stack)w=0xcdcdcdcdcdcdcdcdULL;m.stack[4]=0xfeed0001;Memory snapshot=m;
   alignas(64) State s;std::memset(&s,0xa5,sizeof s);s.aflag.cf=0;s.aflag.pf=0;s.aflag.af=0;s.aflag.zf=0;s.aflag.sf=0;s.aflag.of=1;
   s.gpr.rdi.qword=mem?uint64_t(&m.words[1]):input;s.gpr.rax.qword=0xfefefefefefefefeULL;s.gpr.rsp.qword=uint64_t(&m.stack[4]);s.gpr.rip.qword=addresses[n];
   State expected=s;expected.gpr.rax.qword=expected_value;expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=m.stack[4];
   expected.aflag.cf=uint8_t(expected_flags&1);expected.aflag.zf=uint8_t((expected_flags>>6)&1);expected.aflag.sf=uint8_t((expected_flags>>7)&1);expected.aflag.of=0;
   auto* returned=lifted[n](&s,addresses[n],&m);expected.aflag.af=s.aflag.af;expected.aflag.pf=s.aflag.pf;
   uint64_t flags=0,hardware_value=hardware[n](mem?uint64_t(&m.words[1]):input,&flags);
   if(hardware_value!=expected_value||(flags&0x8c1)!=expected_flags)fail("hardware/reference result or defined flags",n,input);
   if(returned!=&m||std::memcmp(&s,&expected,sizeof s))fail("AOT full state",n,input);
   if(m.return_reads!=1||m.data_reads!=unsigned(mem)||m.returned!=0xfeed0001||std::memcmp(m.words,snapshot.words,sizeof m.words)||std::memcmp(m.stack,snapshot.stack,sizeof m.stack))fail("AOT memory/return",n,input);
   ++cases;
  }
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":8,\"reference\":\"bit-scan plus authored hardware; defined flags and full State\",\"game_code_execution\":false}\n",(unsigned long long)cases);
}
