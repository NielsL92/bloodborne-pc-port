// SPDX-License-Identifier: GPL-2.0-or-later
// Authored provenance tests. Hypercall responses are mocks, not service support.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t stack[32];unsigned reads,writes,returns,transfers,hyper;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=uint64_t(*)(uint64_t,uint64_t*,uint64_t);
#include "exit-entries.h"
static State state,expected;static Memory memory,wanted_memory;static unsigned form,trial;static uint64_t root,expected_source,expected_target;static void* escape[5];static bool faulted;static Memory* returned;
[[noreturn]] static void fail(const char* why){std::fprintf(stderr,"FAIL %s form=%u trial=%u\n",why,form,trial);std::exit(2);}
static unsigned slot(Memory* m,uint64_t at){if(m!=&memory||at<uint64_t(m->stack)||at>=uint64_t(m->stack+32)||(at-uint64_t(m->stack))%8)fail("memory span");return unsigned((at-uint64_t(m->stack))/8);}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){auto n=slot(m,at);if(n!=15&&n!=16)fail("read slot");++m->reads;return m->stack[n];}
extern "C" Memory* __remill_write_memory_64(Memory* m,uint64_t at,uint64_t value){if(slot(m,at)!=15)fail("write slot");++m->writes;m->stack[15]=value;return m;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){if(s!=&state||m!=&memory||state.gpr.rip.qword!=pc)fail("return identity");++m->returns;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("generic error");}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("unsourced missing block");}
extern "C" Memory* __bb_native_block_transfer(State* s,uint64_t target,Memory* m,uint64_t source,uint64_t requested){
 if(s!=&state||m!=&memory||target!=expected_target||requested!=expected_target||source!=expected_source||state.gpr.rip.qword!=target)fail("transfer provenance");++m->transfers;return m;
}
extern "C" Memory* __remill_async_hyper_call(State* s,uint64_t pc,Memory* m){
 if(form!=6||s!=&state||m!=&memory||pc!=root||state.gpr.rip.qword!=root||state.hyper_call!=AsyncHyperCall::kX86Int3||state.hyper_call_vector!=3)fail("authored hypercall input");++m->hyper;state.gpr.rip.qword=root+((trial&1)?32:1);return m;
}
extern "C" [[noreturn]] void __bb_native_control_fault(State* s,uint64_t source,Memory* m,uint32_t reason,uint64_t wanted,uint64_t actual){
 if(form!=6||!(trial&1)||s!=&state||m!=&memory||source!=root||reason!=3||wanted!=root+1||actual!=root+32||state.gpr.rip.qword!=actual)fail("hypercall fault provenance");faulted=true;__builtin_longjmp(escape,1);
}
extern "C" uint8_t __remill_undefined_8(){return 0;}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn){
 asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");if(__builtin_setjmp(escape)==0)returned=fn(&state,root,&memory);
}
static void flags(State& s,uint64_t f){s.aflag.cf=f&1;s.aflag.pf=(f>>2)&1;s.aflag.af=(f>>4)&1;s.aflag.zf=(f>>6)&1;s.aflag.sf=(f>>7)&1;s.aflag.of=(f>>11)&1;}
int main(){uint64_t cases=0,transfers=0,faults=0,hardware_cases=0;
 for(form=0;form<7;++form)for(trial=0;trial<4096;++trial){
  root=0x1000b0000ULL+form*256;uint64_t input=form==3?1+trial%64:trial%3;uint64_t initial_flags=2|((trial&1)?1:0)|((trial&2)?4:0)|((trial&4)?16:0)|((trial&8)?64:0)|((trial&16)?128:0)|((trial&32)?2048:0),hw_flags=0;uint64_t hw_value=form<6?hardware[form](input,&hw_flags,initial_flags):0;hardware_cases+=form<6;
  memory={};for(auto& q:memory.stack)q=0xccccccccccccccccULL;memory.stack[16]=0xfeed0001;wanted_memory=memory;
  std::memset(&state,0xa5,sizeof state);state.gpr.rsp.qword=uint64_t(memory.stack+16);state.gpr.rip.qword=root;state.gpr.rax.qword=0x12345678;state.gpr.rcx.qword=input;flags(state,initial_flags);expected=state;
  expected_source=root;expected_target=root+((form==0||form==2||form==3)?32:(form==5?9:5));
  if(form==2)expected_source=root+(input?4:2);if(form==3){expected_source=root+4;expected.gpr.rcx.qword=0;}if(form==5)expected_source=root+(input?4:2);
  bool should_fault=form==6&&(trial&1);
  if(form<6){expected.gpr.rax.qword=hw_value;expected.gpr.rip.qword=expected_target;flags(expected,hw_flags);if(form==2||form==5)expected.aflag.af=state.aflag.af;wanted_memory.transfers=1;}
  if(form==4){wanted_memory.stack[15]=root+5;wanted_memory.reads=1;wanted_memory.writes=1;wanted_memory.returns=1;}
  if(form==6){expected.hyper_call=AsyncHyperCall::kX86Int3;expected.hyper_call_vector=3;wanted_memory.hyper=1;expected.gpr.rip.qword=should_fault?root+32:0xfeed0001;if(!should_fault){expected.gpr.rax.qword=111;expected.gpr.rsp.qword+=8;wanted_memory.reads=1;wanted_memory.returns=1;}}
  faulted=false;returned=nullptr;invoke(entries[form]);if(faulted!=should_fault||(!should_fault&&returned!=&memory))fail("exit decision");
  if(form==2||form==5)state.aflag.af=expected.aflag.af; // TEST's AF is architecturally undefined.
  if(std::memcmp(&state,&expected,sizeof state)||std::memcmp(&memory,&wanted_memory,sizeof memory))fail("full State and memory events");++cases;transfers+=memory.transfers;faults+=faulted;
 }
 std::printf("{\"status\":\"pass\",\"cases\":%llu,\"hardware_cases\":%llu,\"sourced_transfers\":%llu,\"hypercall_faults\":%llu,\"game_execution\":false}\n",(unsigned long long)cases,(unsigned long long)hardware_cases,(unsigned long long)transfers,(unsigned long long)faults);
}
