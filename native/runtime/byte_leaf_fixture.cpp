// SPDX-License-Identifier: GPL-2.0-or-later
// Supplied four-byte body, compiled by Remill/LLVM; explicit synthetic input contexts.
#include "runtime.h"
#include <cstdlib>
#include <cstring>
extern "C" Memory* sub_10207f3b0(State*,uint64_t,Memory*);
constexpr uint64_t PC=0x10207f3b0ULL,DATA=0x78000000,STACK=0x79000000,RET=0xfeed8001;
static const bb_runtime::Target targets[]={{PC,sub_10207f3b0}};
static const bb_runtime::Tables tables{targets,1,nullptr,0,nullptr,0,"supplied-byte-leaf-v1"};
static void require(bool value){if(!value)std::abort();}
int main(int argc,char** argv){
 if(argc!=2)return 2;bb_runtime::AddressSpace space;space.add(DATA,256,3);space.add(STACK,256,3);space.guard(DATA+128,1,"leaf-unresolved-byte");space.seal();State state{};Memory m{};m.state=&state;m.space=&space;m.tables=&tables;m.owner_thread=GetCurrentThreadId();m.entry=PC;bb_runtime::validate_tables(tables);uint64_t cases=0;
 auto call=[&](uint64_t at,uint64_t value){state=State{};state.gpr.rip.qword=PC;state.gpr.rsp.qword=STACK+248;state.gpr.rdi.qword=at;state.gpr.rax.qword=value;state.gpr.rbx.qword=0x123456789abcdef0;state.gpr.rbp.qword=0xfedcba9876543210;state.gpr.r12.qword=12;state.gpr.r13.qword=13;state.gpr.r14.qword=14;state.gpr.r15.qword=15;state.aflag.cf=1;state.aflag.pf=1;state.aflag.af=1;state.aflag.zf=1;state.aflag.sf=1;state.aflag.of=1;space.write(&m,STACK+248,&RET,8);require(bb_runtime::dispatch(&state,PC,&m)==&m);require(state.gpr.rip.qword==RET&&state.gpr.rsp.qword==STACK+256&&state.gpr.rdi.qword==at);require(state.gpr.rbx.qword==0x123456789abcdef0&&state.gpr.rbp.qword==0xfedcba9876543210&&state.gpr.r12.qword==12&&state.gpr.r13.qword==13&&state.gpr.r14.qword==14&&state.gpr.r15.qword==15);require(state.aflag.cf&&state.aflag.pf&&state.aflag.af&&state.aflag.zf&&state.aflag.sf&&state.aflag.of);++cases;return state.gpr.rax.qword;};
 if(!std::strcmp(argv[1],"unmapped")){call(DATA+256-16,0);return 3;}
 if(!std::strcmp(argv[1],"guard")){call(DATA+128-16,0);return 3;}
 if(std::strcmp(argv[1],"positive"))return 2;
 for(unsigned value=0;value<256;++value)for(uint64_t initial:{0ULL,0xffffffffffffffffULL,0x123456789abcdef0ULL,0x8000000000000055ULL})for(uint64_t offset:{0ULL,17ULL,239ULL}){
  uint8_t byte=uint8_t(value);space.write(&m,DATA+offset+16,&byte,1);require(call(DATA+offset,initial)==(initial/256*256+value));uint8_t after=0;space.read(&m,DATA+offset+16,&after,1);require(after==value);
 }
 std::printf("{\"status\":\"pass\",\"cases\":%llu,\"all_byte_values\":256,\"high_rax_preserved\":true,\"flags_preserved\":true,\"game_derived_aot_execution\":true,\"native_game_boot\":false}\n",(unsigned long long)cases);
}
