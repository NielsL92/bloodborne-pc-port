// SPDX-License-Identifier: GPL-2.0-or-later
// Authored integrity boundaries only; no game or production unwind execution.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t stack[32];unsigned reads,writes,returns,indirect;uint64_t last_return;};
struct Spec {uint64_t pc;unsigned mode;bool indirect;unsigned length,delta;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=uint64_t(*)(uint64_t);
#include "call-entries.h"
static Memory memory,initial_memory;static State state,expected;static const Spec* active;static unsigned form;static void* escape[5];static bool faulted;static Memory* returned;
[[noreturn]] static void fail(const char* why){std::fprintf(stderr,"FAIL %s form=%u\n",why,form);std::exit(2);}
static unsigned slot(Memory* m,uint64_t at){if(m!=&memory||at<uint64_t(m->stack)||at>=uint64_t(m->stack+32)||(at-uint64_t(m->stack))%8)fail("memory span");return unsigned((at-uint64_t(m->stack))/8);}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){auto n=slot(m,at);if(n!=15&&n!=16)fail("read slot");++m->reads;return m->stack[n];}
extern "C" Memory* __remill_write_memory_64(Memory* m,uint64_t at,uint64_t value){auto n=slot(m,at);if(n!=15)fail("write slot");++m->writes;m->stack[n]=value;return m;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){if(s!=&state||m!=&memory||s->gpr.rip.qword!=pc)fail("return identity");++m->returns;m->last_return=pc;return m;}
extern "C" Memory* __remill_function_call(State* s,uint64_t pc,Memory* m){if(s!=&state||m!=&memory||pc!=active->pc+64)fail("indirect target");++m->indirect;return helpers[form](s,pc,m);}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("generic compiler error");}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("unexpected missing block");}
extern "C" [[noreturn]] void __bb_native_control_fault(State* s,uint64_t source,Memory* m,uint32_t reason,uint64_t wanted,uint64_t actual){
 if(s!=&state||m!=&memory||source!=active->pc||reason!=(active->mode==1?1U:2U)||wanted!=active->pc+active->length||actual!=(active->mode==1?active->pc+32:wanted)||state.gpr.rip.qword!=actual)fail("source-aware fault arguments");
 faulted=true;__builtin_longjmp(escape,1);
}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){
 asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");
 if(__builtin_setjmp(escape)==0)returned=fn(&state,pc,&memory);
}
int main(int argc,char** argv){
 if(argc!=2)return 2;bool unchecked=std::strcmp(argv[1],"unchecked")==0;uint64_t cases=0,faults=0,wrong_continuations=0,ignored_contracts=0;
 for(form=0;form<6;++form)for(unsigned trial=0;trial<2048;++trial){
  active=&specs[form];const auto& spec=*active;auto hardware_result=hardware[form](uint64_t(hardware[form])+64);if(hardware_result!=(spec.mode==1?222:111))fail("hardware authored route");
  memory={};for(auto& q:memory.stack)q=0xccccccccccccccccULL;memory.stack[16]=0xfeed0001;initial_memory=memory;
  std::memset(&state,0xa5,sizeof state);state.gpr.rsp.qword=uint64_t(memory.stack+16);state.gpr.rip.qword=spec.pc;state.gpr.rax.qword=0xfeed00000000ULL+trial;state.gpr.rcx.qword=spec.pc+64;state.aflag.cf=trial&1;state.aflag.pf=(trial>>1)&1;state.aflag.af=(trial>>2)&1;state.aflag.zf=(trial>>3)&1;state.aflag.sf=(trial>>4)&1;state.aflag.of=(trial>>5)&1;expected=state;
  bool should_fault=!unchecked&&spec.mode!=0;uint64_t callee_return=spec.mode==1?spec.pc+32:spec.pc+spec.length;initial_memory.stack[15]=callee_return;
  if(spec.mode==1){expected.aflag.cf=0;expected.aflag.pf=0;expected.aflag.af=1;expected.aflag.zf=0;expected.aflag.sf=0;expected.aflag.of=0;}
  if(should_fault)expected.gpr.rip.qword=callee_return;else {expected.gpr.rip.qword=0xfeed0001;expected.gpr.rsp.qword+=8;expected.gpr.rax.qword=111;}
  faulted=false;returned=nullptr;invoke(entries[form],spec.pc);if(faulted!=should_fault)fail("boundary fault decision");
  if(std::memcmp(&state,&expected,sizeof state)||std::memcmp(memory.stack,initial_memory.stack,sizeof memory.stack))fail("full State / stack boundary");
  if(memory.writes!=(spec.mode==1?2U:1U)||memory.reads!=(spec.mode==1?1U:0U)+(should_fault?1U:2U)||memory.returns!=(should_fault?1U:2U)||memory.indirect!=unsigned(spec.indirect)||memory.last_return!=(should_fault?callee_return:0xfeed0001)||(!should_fault&&returned!=&memory))fail("memory and control events");
  faults+=faulted;wrong_continuations+=unchecked&&spec.mode==1;ignored_contracts+=unchecked&&spec.mode==2;++cases;
 }
#ifdef BB_INCLUDE_GETPC
 for(unsigned trial=0;trial<2048;++trial){
  form=6;constexpr uint64_t pc=0x100092000ULL;if(hw_getpc()!=uint64_t(hw_getpc)+5)fail("hardware CALL-next POP route");
  memory={};for(auto& q:memory.stack)q=0xccccccccccccccccULL;memory.stack[16]=0xfeed0001;initial_memory=memory;initial_memory.stack[15]=pc+5;
  std::memset(&state,0xa5,sizeof state);state.gpr.rsp.qword=uint64_t(memory.stack+16);state.gpr.rip.qword=pc;state.gpr.rax.qword=trial;expected=state;expected.gpr.rax.qword=pc+5;expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;
  faulted=false;returned=nullptr;invoke(sub_100092000,pc);if(faulted||returned!=&memory||std::memcmp(&state,&expected,sizeof state)||std::memcmp(memory.stack,initial_memory.stack,sizeof memory.stack)||memory.writes!=1||memory.reads!=2||memory.returns!=1||memory.indirect||memory.last_return!=0xfeed0001)fail("CALL-next POP full State and events");++cases;
 }
#endif
 std::printf("{\"status\":\"pass\",\"cases\":%llu,\"native_faults\":%llu,\"legacy_wrong_continuations\":%llu,\"legacy_ignored_nonreturn_contracts\":%llu,\"all_continuation_targets_compiled\":true,\"game_execution\":false}\n",(unsigned long long)cases,(unsigned long long)faults,(unsigned long long)wrong_continuations,(unsigned long long)ignored_contracts);
}
