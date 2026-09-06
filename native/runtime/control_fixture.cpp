// SPDX-License-Identifier: GPL-2.0-or-later
// Exercises runtime gateways with authored AOT objects only.
#include "runtime.h"
#include <cstring>
#include <string>
#include <vector>
using namespace bb_runtime;
#include "runtime-entries.h"
extern "C" Memory* __bb_native_block_transfer(State*,uint64_t,Memory*,uint64_t,uint64_t)noexcept;
extern "C" uint64_t __remill_read_memory_64(Memory*,uint64_t)noexcept;
extern "C" Memory* __remill_write_memory_64(Memory*,uint64_t,uint64_t)noexcept;
constexpr uint64_t PC=0x1000c0000ULL,STACK=0x70000000ULL,RET=0xfeed0001;
static Memory* authored_service(State* s,uint64_t,Memory* m){s->gpr.rax.qword=s->gpr.rdi.qword*3+5;return return_from_import(s,m);}
extern "C" Memory* sub_1000c2000(State* s,uint64_t pc,Memory* m){return imported(s,pc,m);}
extern "C" Memory* sub_1000c2010(State* s,uint64_t pc,Memory* m){return imported(s,pc,m);}
static void require(bool b,const char* why){if(!b){std::fprintf(stderr,"FAIL %s\n",why);std::exit(2);}}
static void add_flags(State& state,uint32_t a,uint32_t b){uint32_t r=a+b;state.aflag.cf=uint64_t(a)+b>0xffffffffULL;state.aflag.pf=__builtin_parity(unsigned(r&255))==0;state.aflag.af=((a^b^r)&16)!=0;state.aflag.zf=r==0;state.aflag.sf=r>>31;state.aflag.of=((~(a^b)&(a^r))>>31)!=0;}
int main(int argc,char** argv){
 if(argc!=2)return 2;std::string mode=argv[1];Target targets[]=BB_RUNTIME_TARGETS;SourcePair pairs[]={{PC+5,PC+32}};Import imports[]={{PC+0x2000,"authored-native","authored","authored",mode=="unimplemented-import"?nullptr:authored_service,0},{PC+0x2010,"authored-export","authored","authored",nullptr,PC+64}};Tables tables{targets,sizeof(targets)/sizeof(*targets),pairs,1,imports,2,"authored-runtime-control"};
 if(mode=="bad-table"){targets[1].pc=targets[0].pc;bool rejected=false;try{validate_tables(tables);}catch(const std::exception&){rejected=true;}require(rejected,"duplicate target table");std::puts("{\"status\":\"setup-rejected\"}");return 0;}
 validate_tables(tables);bb_runtime::AddressSpace space;space.add(STACK,4096,Read|Write);space.add(PC,4096,Read|Code);space.add(PC+0x2000,32,Read|Code);space.seal();State state{},expected{};Memory memory;memory.space=&space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();
 auto init=[&](uint64_t entry,unsigned trial){std::memset(&state,0xa5,sizeof state);state.gpr.rip.qword=entry;state.gpr.rsp.qword=STACK+128;state.gpr.rax.qword=1000+trial;state.gpr.rdi.qword=trial;state.gpr.rcx.qword=PC+((trial&1)?32:64);state.aflag.cf=trial&1;state.aflag.pf=(trial>>1)&1;state.aflag.af=(trial>>2)&1;state.aflag.zf=(trial>>3)&1;state.aflag.sf=(trial>>4)&1;state.aflag.of=(trial>>5)&1;memory.entry=entry;memory.returned_pc=0;for(unsigned i=0;i<32;++i)__remill_write_memory_64(&memory,STACK+i*8,0xccccccccccccccccULL);__remill_write_memory_64(&memory,STACK+128,RET);};
 if(mode=="bad-source"||mode=="bad-request"){init(PC,0);state.gpr.rip.qword=PC+32;__bb_native_block_transfer(&state,PC+32,&memory,mode=="bad-source"?PC+6:PC+5,mode=="bad-request"?PC+64:PC+32);return 2;}
 if(mode!="positive"){
  uint64_t entry=mode=="bad-return"?PC+0x600:mode=="nonreturn"?PC+0x500:mode=="ud2"?PC+0x700:mode=="async"?PC+0x800:mode=="sync"?PC+0x900:mode=="unimplemented-import"?PC+0x100:PC+0x300;init(entry,1);if(mode=="unknown-target")state.gpr.rcx.qword=0xbad;dispatch(&state,entry,&memory);return 2;
 }
 uint64_t cases=0;
 for(unsigned form=0;form<5;++form)for(unsigned trial=0;trial<4096;++trial){uint64_t entry=PC+form*256;init(entry,trial);expected=state;expected.gpr.rip.qword=RET;expected.gpr.rsp.qword+=8;
  if(form==0){expected.gpr.rax.qword=111+trial;add_flags(expected,111,trial);}
  else if(form==1)expected.gpr.rax.qword=trial*3+5;
  else if(form==2||!(trial&1))expected.gpr.rax.qword=111;
  else{expected.gpr.rax.qword=1000+trial*2;add_flags(expected,1000+trial,trial);}
  auto* result=dispatch(&state,entry,&memory);require(result==&memory&&memory.returned_pc==RET&&!memory.active_import&&!memory.atomic_depth,"normal runtime return");require(!std::memcmp(&state,&expected,sizeof state),"AOT full State");
  for(unsigned i=0;i<32;++i){uint64_t value=i==16?RET:i==15&&form!=4?entry+(form==3?2:5):0xccccccccccccccccULL;require(__remill_read_memory_64(&memory,STACK+i*8)==value,"logical stack effects");}++cases;
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"paths\":5,\"private_mappings_NX\":true,\"game_execution\":false}\n",(unsigned long long)cases);
}
