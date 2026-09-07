// SPDX-License-Identifier: GPL-2.0-or-later
#include "runtime.h"
#include <cstdlib>
#include <cstring>
#include "leaf-batch-config.h"
constexpr uint64_t DATA=0x78000000,STACK=0x79000000,RET=0xfeedc001;
static const bb_runtime::Tables tables{BATCH_TARGETS,BATCH_COUNT,nullptr,0,nullptr,0,"conditional-simple-leaf-batch-v1"};
static void require(bool v){if(!v)std::abort();}
int main(int argc,char** argv){
 if(argc<2)return 2;unsigned selected=argc==3?unsigned(std::strtoul(argv[2],nullptr,10)):0;require(selected<BATCH_COUNT);bb_runtime::AddressSpace space;space.add(DATA,256,3);space.guard(DATA+128,8,"batch-data-guard");space.add(STACK,256,3);space.guard(STACK+128,8,"batch-return-guard");space.seal();State s{};Memory m{};m.space=&space;m.state=&s;m.tables=&tables;m.owner_thread=GetCurrentThreadId();bb_runtime::validate_tables(tables);uint64_t cases=0;
 auto call=[&](const Leaf& leaf,uint64_t at,uint64_t initial,bool bad,bool guarded){s=State{};s.gpr.rip.qword=leaf.pc;s.gpr.rsp.qword=bad&&!leaf.width?(guarded?STACK+128:STACK+256):STACK+248;s.gpr.rdi.qword=at;s.gpr.rax.qword=initial;s.gpr.rbx.qword=0x123456789abcdef0;s.gpr.rbp.qword=0xfedcba9876543210;s.gpr.r12.qword=12;s.gpr.r13.qword=13;s.gpr.r14.qword=14;s.gpr.r15.qword=15;s.aflag.cf=1;s.aflag.pf=1;s.aflag.af=1;s.aflag.zf=1;s.aflag.sf=1;s.aflag.of=1;m.entry=leaf.pc;if(s.gpr.rsp.qword==STACK+248)space.write(&m,STACK+248,&RET,8);require(bb_runtime::dispatch(&s,leaf.pc,&m)==&m);require(s.gpr.rip.qword==RET&&s.gpr.rsp.qword==STACK+256&&s.gpr.rdi.qword==at&&s.gpr.rbx.qword==0x123456789abcdef0&&s.gpr.rbp.qword==0xfedcba9876543210&&s.gpr.r12.qword==12&&s.gpr.r13.qword==13&&s.gpr.r14.qword==14&&s.gpr.r15.qword==15);require(s.aflag.cf&&s.aflag.pf&&s.aflag.af&&s.aflag.zf&&s.aflag.sf&&s.aflag.of);++cases;return s.gpr.rax.qword;};
 if(!std::strcmp(argv[1],"unmapped")||!std::strcmp(argv[1],"guard")){bool guarded=!std::strcmp(argv[1],"guard");auto& leaf=LEAVES[selected];call(leaf,DATA+(guarded?128:256)-leaf.displacement,0,true,guarded);return 3;}
 if(std::strcmp(argv[1],"positive"))return 2;
 for(const auto& leaf:LEAVES)for(unsigned v=0;v<256;++v)for(uint64_t initial:{0ULL,0xffffffffffffffffULL,0x123456789abcdef0ULL,0x8000000000000055ULL})for(uint64_t offset:{0ULL,17ULL,256ULL-leaf.width}){
  uint64_t supplied=leaf.width==1?v:(uint64_t(v)*0x9e3779b97f4a7c15ULL)^initial;if(leaf.width)space.write(&m,DATA+offset,&supplied,leaf.width);uint64_t expected=leaf.width==1?initial/256*256+v:leaf.width==8?supplied:leaf.address;require(call(leaf,DATA+offset-leaf.displacement,initial,false,false)==expected);if(leaf.width){uint64_t after=0;space.read(&m,DATA+offset,&after,leaf.width);require(after==supplied);}
 }
 std::printf("{\"status\":\"pass\",\"cases\":%llu,\"roots\":%llu,\"cases_per_root\":3072,\"game_derived_aot_execution\":true,\"native_game_boot\":false}\n",(unsigned long long)cases,(unsigned long long)BATCH_COUNT);
}
