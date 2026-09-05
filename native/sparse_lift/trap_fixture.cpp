// SPDX-License-Identifier: GPL-2.0-or-later
// Authored branch-to-fault check. No hardware UD2 or game code is executed.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t stack[8];unsigned reads=0;uint64_t returned=0;};
static State expected;static uint64_t saved_stack[8];
[[noreturn]] static void fail(const char* why){std::fprintf(stderr,"FAIL %s\n",why);std::exit(2);}
extern "C" Memory* sub_100020000(State*,uint64_t,Memory*);
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("read boundary");++m->reads;return m->stack[4];}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("generic compiler error");}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");}
extern "C" [[noreturn]] Memory* __bb_native_ud2(State* state,uint64_t pc,Memory* m){
 if(pc!=0x100020045||state->gpr.rip.qword!=pc||std::memcmp(state,&expected,sizeof expected)||m->reads||m->returned||std::memcmp(m->stack,saved_stack,sizeof saved_stack))fail("fault address/state/memory");
 std::puts("{\"status\":\"expected_native_fault\",\"fault_pc\":4295098437,\"game_code_execution\":false}");std::exit(74);
}
int main(int argc,char**){
 bool trap=argc>1;Memory m{};for(auto& x:m.stack)x=0xcdcdcdcdcdcdcdcdULL;m.stack[4]=0xfeed0001;std::memcpy(saved_stack,m.stack,sizeof saved_stack);
 alignas(64) State s;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=trap?0:1;s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=0x100020000;
 expected=s;expected.aflag.cf=0;expected.aflag.of=0;expected.aflag.sf=0;expected.aflag.af=0;expected.aflag.zf=trap;expected.aflag.pf=trap;expected.gpr.rax.qword=trap?9:7;expected.gpr.rip.qword=trap?0x100020045:0xfeed0001;if(!trap)expected.gpr.rsp.qword+=8;
 auto* result=sub_100020000(&s,0x100020000,&m);if(trap)fail("fault returned");
 if(result!=&m||std::memcmp(&s,&expected,sizeof s)||m.reads!=1||m.returned!=0xfeed0001||std::memcmp(m.stack,saved_stack,sizeof saved_stack))fail("normal branch state/return");
 std::puts("{\"status\":\"normal_return\",\"game_code_execution\":false}");
}
