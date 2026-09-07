// SPDX-License-Identifier: GPL-2.0-or-later
#include "direct_memory.h"
#include <cstdlib>
#include <cstring>
#include "direct-entries.h"
static constexpr uint64_t PC=0x100300000ULL,DATA=0x78000000ULL,STACK=0x79000000ULL,RET=0xfeed5001ULL,BUDGET=0x120000000ULL;
static const bb_runtime::Target targets[]=DIRECT_TARGETS;
static const bb_runtime::Import imports[]={
 {0x900002000ULL,"pO96TwzOm5E","libkernel","libkernel",bb_runtime::direct_memory_size,0},
 {0x900002010ULL,"rTXw65xmLIA","libkernel","libkernel",bb_runtime::direct_memory_allocate,0},
 {0x900002020ULL,"L-Q3LEjIbgA","libkernel","libkernel",bb_runtime::direct_memory_map,0},
 {0x900002030ULL,"MBuItvba6z8","libkernel","libkernel",bb_runtime::direct_memory_release,0}};
static const bb_runtime::Tables tables{targets,4,nullptr,0,imports,4,"authored-native-direct-memory-v1"};
static void require(bool v){if(!v)std::abort();}
int main(int argc,char** argv){
 if(argc!=2)return 2;bb_runtime::AddressSpace space;space.add(DATA,256,3);space.guard(DATA+128,8,"authored-unresolved");space.add(STACK,512,3);space.add(DATA+4096,16,5);space.seal();bb_runtime::DirectMemory pool(space,BUDGET);State state{};Memory memory{};memory.state=&state;memory.space=&space;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.direct_memory=&pool;bb_runtime::validate_tables(tables);uint64_t cases=0;
 auto write=[&](uint64_t at,uint64_t v){space.write(&memory,at,&v,8);};auto read=[&](uint64_t at){uint64_t v=0;space.read(&memory,at,&v,8);return v;};
 auto call=[&](unsigned op,uint64_t a=0,uint64_t b=0,uint64_t c=0,uint64_t d=0,uint64_t e=0,uint64_t f=0){state=State{};state.gpr.rip.qword=PC+256*op;state.gpr.rsp.qword=STACK+504;state.gpr.rdi.qword=a;state.gpr.rsi.qword=b;state.gpr.rdx.qword=c;state.gpr.rcx.qword=d;state.gpr.r8.qword=e;state.gpr.r9.qword=f;state.gpr.rbx.qword=0x1112223334445556ULL;state.gpr.rbp.qword=0x666777888999aaabULL;state.gpr.r12.qword=0x12;state.gpr.r13.qword=0x13;state.gpr.r14.qword=0x14;state.gpr.r15.qword=0x15;memory.entry=state.gpr.rip.qword;write(STACK+504,RET);require(bb_runtime::dispatch(&state,state.gpr.rip.qword,&memory)==&memory);require(state.gpr.rip.qword==RET&&state.gpr.rsp.qword==STACK+512&&state.gpr.rbx.qword==0x1112223334445556ULL&&state.gpr.rbp.qword==0x666777888999aaabULL&&state.gpr.r12.qword==0x12&&state.gpr.r13.qword==0x13&&state.gpr.r14.qword==0x14&&state.gpr.r15.qword==0x15);++cases;return state.gpr.rax.qword;};
 if(!std::strcmp(argv[1],"missing-provider")){memory.direct_memory=nullptr;call(0);return 3;}
 if(!std::strcmp(argv[1],"bad-output")){call(1,0,BUDGET,0x4000,0,0,DATA+252);return 3;}
 if(!std::strcmp(argv[1],"memory-type")){call(1,0,BUDGET,0x4000,0,3,DATA);return 3;}
 if(!std::strcmp(argv[1],"map-mode")){call(2,DATA+8,0x4000,0x33,0,0,0);return 3;}
 if(!std::strcmp(argv[1],"partial-release")){call(1,0,BUDGET,0x8000,0,0,DATA);call(3,read(DATA),0x4000);return 3;}
 if(!std::strcmp(argv[1],"mapped-release")||!std::strcmp(argv[1],"map-hint")||!std::strcmp(argv[1],"map-bounds")||!std::strcmp(argv[1],"old-guard")||!std::strcmp(argv[1],"old-code")){
  call(1,0,BUDGET,0x4000,0,0,DATA);uint64_t physical=read(DATA);write(DATA+8,!std::strcmp(argv[1],"map-hint")?0x2000000000ULL:0);call(2,DATA+8,0x4000,3,0,physical,0);uint64_t mapped=read(DATA+8);
  if(!std::strcmp(argv[1],"mapped-release"))call(3,physical,0x4000);
  if(!std::strcmp(argv[1],"map-bounds"))read(mapped+0x4000);
  if(!std::strcmp(argv[1],"old-guard"))read(DATA+128);
  if(!std::strcmp(argv[1],"old-code"))write(DATA+4096,0);
  return 3;
 }
 if(std::strcmp(argv[1],"positive"))return 2;
 require(call(0)==BUDGET&&BUDGET>0xffffffffULL);
 // Independent division/remainder rounding for nonzero search starts above 4 GiB.
 for(uint64_t i=0;i<2048;++i){uint64_t start=0x100000000ULL+i*31,alignment=0x4000ULL<<(i%8),length=0x4000*(1+i%7);uint64_t wanted=((start+alignment-1)/alignment)*alignment;require(call(1,start,BUDGET,length,alignment,0,DATA)==0);require(read(DATA)==wanted);require(call(3,wanted,length)==0);}
 // Every successful whole-allocation release makes the first-fit range available again.
 require(call(1,0,0x10000,0x4000,0,0,DATA)==0&&read(DATA)==0);require(call(1,0,0x10000,0x4000,0,0,DATA+8)==0&&read(DATA+8)==0x4000);require(call(3,0,0x4000)==0);require(call(1,0,0x10000,0x4000,0,0,DATA)==0&&read(DATA)==0);require(call(3,0,0x4000)==0);require(call(3,0x4000,0x4000)==0);
 uint64_t invalid=0;
 for(uint64_t length:{0ULL,1ULL,0x4001ULL}){write(DATA,0xface);require(call(1,0,BUDGET,length,0,0,DATA)==0x80020016u&&read(DATA)==0xface);++invalid;}
 for(uint64_t alignment:{1ULL,0x3000ULL,0xc000ULL}){require(call(1,0,BUDGET,0x4000,alignment,0,DATA)==0x80020016u);++invalid;}
 require(call(1,0,0x4000,0x8000,0,0,DATA)==0x80020023u);++invalid;
 uint64_t aliases=0;
 for(uint64_t i=0;i<64;++i){require(call(1,0,BUDGET,0x4000,0x4000,0,DATA)==0);uint64_t physical=read(DATA);write(DATA+8,0);require(call(2,DATA+8,0x4000,3,0,physical,0x200000)==0);uint64_t first=read(DATA+8);require(first%0x200000==0&&read(first)==0&&read(first+0x3ff8)==0);write(DATA+16,0);require(call(2,DATA+16,0x4000,3,0,physical,0x4000)==0);uint64_t second=read(DATA+16);require(first!=second);write(first,0x12340000+i);require(read(second)==0x12340000+i);write(second+0x3ff8,0xfedc0000+i);require(read(first+0x3ff8)==0xfedc0000+i);++aliases;}
 // Runtime registration accepts only this private allocation's committed NX data.
 auto owner=std::shared_ptr<void>(VirtualAlloc(nullptr,0x4000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE),[](void* p){VirtualFree(p,0,MEM_RELEASE);});require(bool(owner));void* raw=owner.get();require(!space.map_private(&memory,DATA,0x4000,3,raw,owner));require(!space.map_private(&memory,bb_runtime::DIRECT_MAP_END-0x4000,0x4000,5,raw,owner));require(space.map_private(&memory,bb_runtime::DIRECT_MAP_END-0x4000,0x4000,3,raw,owner));owner.reset();write(bb_runtime::DIRECT_MAP_END-8,0x12345);require(read(bb_runtime::DIRECT_MAP_END-8)==0x12345);
 std::printf("{\"status\":\"pass\",\"aot_service_calls\":%llu,\"allocation_release_pairs\":2048,\"alias_pairs\":%llu,\"invalid_returns\":%llu,\"size_query_above_4g\":true,\"shared_backing_lifetime\":true}\n",(unsigned long long)cases,(unsigned long long)aliases,(unsigned long long)invalid);
}
