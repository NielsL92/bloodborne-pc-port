// SPDX-License-Identifier: GPL-2.0-or-later
#include "runtime.h"
#include <array>
#include <cstring>
#include <cstdlib>
#include <stdexcept>
#include "guard-entries.h"
extern "C" Memory* __remill_compare_exchange_memory_64(Memory*,uint64_t,uint64_t&,uint64_t)noexcept;
extern "C" Memory* __remill_atomic_begin(Memory*)noexcept;
constexpr uint64_t BASE=0x70000000,STACK=0x71000000,PC=0x1000e0000,RETURN=0xfeed0001;
static void require(bool value,const char* why){if(!value){std::fprintf(stderr,"guard fixture: %s\n",why);std::exit(2);}}
int main(int argc,char** argv){
 if(argc<2)return 2;std::string mode=argv[1];std::array<uint8_t,8192> initial{};for(size_t i=0;i<initial.size();++i)initial[i]=uint8_t(i*29+7);std::array<uint8_t,512> stack{};uint64_t ret=RETURN;std::memcpy(stack.data()+128,&ret,8);
 bb_runtime::AddressSpace space;space.add(BASE,4096,bb_runtime::Read|bb_runtime::Write,initial.data(),4096);space.add(BASE+4096,4096,bb_runtime::Read|bb_runtime::Write,initial.data()+4096,4096);space.add(STACK,512,bb_runtime::Read|bb_runtime::Write,stack.data(),512);space.add(PC,4096,bb_runtime::Read|bb_runtime::Code);
 space.guard(BASE+128,8,"authored-slot-A");space.guard(BASE+4092,8,"authored-cross-region");
 if(mode=="setup-overlap"||mode=="setup-zero"||mode=="setup-unmapped"||mode=="setup-sealed"){
  try{if(mode=="setup-sealed")space.seal();space.guard(mode=="setup-unmapped"?BASE+8192:mode=="setup-overlap"?BASE+130:BASE+256,mode=="setup-zero"?0:8,"invalid");}catch(const std::exception&){std::puts("{\"status\":\"setup-rejected\"}");return 0;}return 2;
 }
 space.seal();State state{};state.gpr.rip.qword=PC;state.gpr.rsp.qword=STACK+128;Memory memory{};memory.space=&space;memory.state=&state;memory.owner_thread=GetCurrentThreadId();memory.entry=PC;
 const bb_runtime::Tables tables{roots,sizeof(roots)/sizeof(*roots),nullptr,0,nullptr,0,"authored-guard-runtime-v1"};bb_runtime::validate_tables(tables);memory.tables=&tables;
 if(mode=="positive"){
  unsigned spans=0,aot=0;std::array<uint8_t,32> buffer{};
  for(unsigned offset=104;offset<160;++offset)for(unsigned width=1;width<=16;++width){if(offset<136&&128<offset+width)continue;space.read(&memory,BASE+offset,buffer.data(),width);require(!std::memcmp(buffer.data(),initial.data()+offset,width),"unguarded bytes");++spans;}
  for(unsigned offset:{120u,136u,4084u,4100u})for(unsigned write=0;write<2;++write){
   state={};state.gpr.rip.qword=PC+write*16;state.gpr.rsp.qword=STACK+128;state.gpr.rdi.qword=BASE+offset;state.gpr.rax.qword=0xcafe1234deadbeefULL;uint64_t expected=state.gpr.rax.qword;
   if(!write)std::memcpy(&expected,initial.data()+offset,8);require(bb_runtime::dispatch(&state,state.gpr.rip.qword,&memory)==&memory,"AOT context");require(state.gpr.rip.qword==RETURN&&state.gpr.rsp.qword==STACK+136&&state.gpr.rax.qword==expected,"AOT State");space.read(&memory,BASE+offset,buffer.data(),8);uint64_t actual;std::memcpy(&actual,buffer.data(),8);require(actual==expected,"AOT memory");++aot;
  }
  for(unsigned seed=0;seed<512;++seed)for(unsigned path=0;path<5;++path){
   state={};uint64_t root=PC+(path<2?0x100:path==2?0x200:0x300);unsigned offset=512+seed%256;state.gpr.rip.qword=root;state.gpr.rsp.qword=STACK+128;state.gpr.rdi.qword=BASE+offset;state.gpr.rsi.qword=BASE+1024;state.gpr.rcx.qword=path&1;
   require(bb_runtime::dispatch(&state,root,&memory)==&memory,"flow context");uint64_t expected;std::memcpy(&expected,initial.data()+offset+(path==2?3:0),8);require(state.gpr.rax.qword==expected&&state.gpr.rip.qword==RETURN&&state.gpr.rsp.qword==STACK+136&&memory.active_source==nullptr,"flow state/source restoration");++aot;
  }
  require(space.guard_count()==2&&memory.active_guard==nullptr,"guard metadata");std::printf("{\"status\":\"pass\",\"unguarded_spans\":%u,\"aot_cases\":%u,\"guards\":2,\"game_execution\":false}\n",spans,aot);return 0;
 }
 if(mode.rfind("flow-",0)==0){
  uint64_t root=PC;state.gpr.rdi.qword=BASE+128;state.gpr.rsi.qword=BASE+1024;
  if(mode=="flow-branch-zero"||mode=="flow-branch-nonzero"){root+=0x100;state.gpr.rcx.qword=mode=="flow-branch-nonzero";}
  else if(mode=="flow-loop"){root+=0x200;state.gpr.rdi.qword-=3;}
  else if(mode=="flow-inner"||mode=="flow-outer"){root+=0x300;if(mode=="flow-inner"){state.gpr.rsi.qword=BASE+128;state.gpr.rdi.qword=BASE+1024;}}
  else if(mode=="flow-span")root+=0x400;else return 2;
  const bb_runtime::FpProfile profile{"authored-guard-profile",uint64_t(0xffff)<<32,0xffff,nullptr,0};bb_runtime::validate_fp_profile(profile);if(mode=="flow-span")memory.fp_profile=&profile;
  state.gpr.rip.qword=root;memory.entry=root;bb_runtime::dispatch(&state,root,&memory);return 2;
 }
 if(argc!=4)return 2;unsigned offset=std::strtoul(argv[2],nullptr,10),width=std::strtoul(argv[3],nullptr,10);if(width>32)return 2;std::array<uint8_t,32> buffer{};uint64_t at=BASE+offset;
 if(mode=="read")space.read(&memory,at,buffer.data(),width);
 else if(mode=="write")space.write(&memory,at,buffer.data(),width);
 else if(mode=="cas"){uint64_t expected=0;__remill_compare_exchange_memory_64(&memory,at,expected,1);}
 else if(mode=="atomic-read"){__remill_atomic_begin(&memory);space.read(&memory,at,buffer.data(),width);}
 else if(mode=="aot-read"||mode=="aot-write"){uint64_t pc=PC+(mode=="aot-write"?16:0);state.gpr.rip.qword=pc;state.gpr.rdi.qword=at;memory.entry=pc;bb_runtime::dispatch(&state,pc,&memory);}
 else return 2;return 2;
}
