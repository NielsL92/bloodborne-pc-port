// SPDX-License-Identifier: GPL-2.0-or-later
// Authored sparse-branch and independent-entry contracts. AOT only; no original
// instruction execution, guest runtime, or general exception implementation.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t* stack;uint64_t returned=0;};
static void fail(const char* why){std::fprintf(stderr,"FAIL %s\n",why);std::exit(2);}
extern "C" Memory* sub_100000200(State*,uint64_t,Memory*);
extern "C" Memory* sub_100000600(State*,uint64_t,Memory*);
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("unexpected memory read");return m->stack[4];}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("lifter error");return nullptr;}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("unexpected missing block");return nullptr;}
int main(){
  constexpr uint64_t sentinel=0xfeed0001,base=0x100000200;
  unsigned checked=0;
  for(unsigned i=0;i<4096;++i)for(unsigned entry=0;entry<2;++entry){
    alignas(64) State s{};uint64_t stack[8],copy[8];for(auto& v:stack)v=0xababababababababULL;stack[4]=sentinel;std::memcpy(copy,stack,sizeof stack);
    Memory m{stack};uint64_t x=(uint64_t(i)<<32)|(i%3?i:0);
    s.gpr.rdi.qword=x;s.gpr.rbx.qword=0x123456789abcdef0ULL;s.gpr.rsp.qword=uint64_t(stack+4);s.gpr.rip.qword=entry?0x100000600:base;
    auto* result=entry?sub_100000600(&s,s.gpr.rip.qword,&m):sub_100000200(&s,s.gpr.rip.qword,&m);
    uint64_t expected=entry?42:(uint32_t(x)?9:7);
    if(result!=&m||s.gpr.rax.qword!=expected||s.gpr.rdi.qword!=x||s.gpr.rbx.qword!=0x123456789abcdef0ULL||s.gpr.rsp.qword!=uint64_t(stack+5)||s.gpr.rip.qword!=sentinel||m.returned!=sentinel||std::memcmp(stack,copy,sizeof stack))fail("sparse control/return contract");
    ++checked;
  }
  std::printf("{\"status\":\"pass\",\"aot_cases\":%u,\"original_code_execution\":false}\n",checked);
}
