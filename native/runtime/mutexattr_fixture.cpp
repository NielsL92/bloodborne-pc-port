// SPDX-License-Identifier: GPL-2.0-or-later
#include "mutexattr.h"
#include <cstring>
#include <cstdlib>
static constexpr uint64_t PC=0x100100000ULL,CELL=0x74000000ULL,STACK=0x75000000ULL,RET=0xfeed3001ULL;
extern "C" Memory* sub_100100000(State*,uint64_t,Memory*);
extern "C" Memory* sub_100100100(State*,uint64_t,Memory*);
extern "C" Memory* sub_100100200(State*,uint64_t,Memory*);
static const bb_runtime::Target targets[]={{PC,sub_100100000},{PC+0x100,sub_100100100},{PC+0x200,sub_100100200}};
static const bb_runtime::Import imports[]={{0x900000100ULL,"F8bUHwAG284","libkernel","libkernel",bb_runtime::mutexattr_init,0},{0x900000110ULL,"iMp8QpE+XO4","libkernel","libkernel",bb_runtime::mutexattr_settype,0},{0x900000120ULL,"smWEktiyyG0","libkernel","libkernel",bb_runtime::mutexattr_destroy,0}};
static const bb_runtime::Tables tables{targets,3,nullptr,0,imports,3,"authored-mutex-attributes-v1"};
static void require(bool v){if(!v)std::abort();}
int main(int argc,char** argv){
 if(argc!=2)return 2;bb_runtime::AddressSpace space;uint8_t data[128];std::memset(data,0xa5,sizeof(data));space.add(CELL,sizeof(data),3,data,sizeof(data));space.add(STACK,512,3);space.seal();State state{};Memory memory{};memory.state=&state;memory.space=&space;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();bb_runtime::MutexAttributes attrs(space,2);memory.mutex_attributes=&attrs;bb_runtime::validate_tables(tables);
 auto read=[&](uint64_t at){uint64_t v=0;space.read(&memory,at,&v,8);return v;};auto write=[&](uint64_t at,uint64_t v){space.write(&memory,at,&v,8);};
 uint64_t cases=0;
 auto call=[&](unsigned operation,uint64_t cell,uint64_t type=0){state=State{};state.gpr.rip.qword=PC+operation*0x100;state.gpr.rsp.qword=STACK+504;state.gpr.rdi.qword=cell;state.gpr.rsi.qword=type;state.gpr.rbx.qword=0xabcdef0011223344ULL;state.gpr.rbp.qword=0x1122334455667788ULL;state.gpr.r12.qword=0x91;state.gpr.r13.qword=0x92;state.gpr.r14.qword=0x93;state.gpr.r15.qword=0x94;memory.entry=state.gpr.rip.qword;write(STACK+504,RET);require(bb_runtime::dispatch(&state,state.gpr.rip.qword,&memory)==&memory);require(state.gpr.rip.qword==RET&&state.gpr.rsp.qword==STACK+512&&state.gpr.rbx.qword==0xabcdef0011223344ULL&&state.gpr.rbp.qword==0x1122334455667788ULL&&state.gpr.r12.qword==0x91&&state.gpr.r13.qword==0x92&&state.gpr.r14.qword==0x93&&state.gpr.r15.qword==0x94);++cases;return state.gpr.rax.qword;};
 const uint64_t cell=CELL+16;
 if(!std::strcmp(argv[1],"bad-pointer")){call(0,CELL+124);return 3;}
 if(!std::strcmp(argv[1],"missing-provider")){memory.mutex_attributes=nullptr;call(0,cell);return 3;}
 if(!std::strcmp(argv[1],"double-init")){call(0,cell);call(0,cell);return 3;}
 if(!std::strcmp(argv[1],"opaque-read")){call(0,cell);read(read(cell));return 3;}
 if(std::strcmp(argv[1],"positive"))return 2;
 uint64_t previous=0;
 for(uint32_t i=0;i<4096;++i){
  write(cell,0xdeadbeefdeadbeefULL);require(call(0,cell)==0);uint64_t token=read(cell);require(token>previous&&token>=bb_runtime::MUTEX_ATTR_BASE&&token<bb_runtime::MUTEX_ATTR_END);previous=token;
  bb_runtime::MutexAttribute value{};require(attrs.snapshot(&memory,cell,value)==0&&value.type==1&&value.protocol==0&&value.ceiling==0);
  uint32_t type=1+i%4;require(call(1,cell,0xfeed00000000ULL|type)==0);require(attrs.snapshot(&memory,cell,value)==0&&value.type==type);
  for(uint32_t bad:{0u,5u,0xffffffffu}){require(call(1,cell,bad)==0x80020016u);require(attrs.snapshot(&memory,cell,value)==0&&value.type==type);}
  require(call(0,CELL+32)==0);uint64_t other=read(CELL+32);require(other!=token);write(CELL+48,0x12345678);require(call(0,CELL+48)==0x8002000cu&&read(CELL+48)==0x12345678);
  require(call(2,CELL+32)==0&&read(CELL+32)==0);write(CELL+64,other);require(call(1,CELL+64,2)==0x80020016u);
  require(call(2,cell)==0&&read(cell)==0);require(call(2,cell)==0x80020016u);
  require(read(CELL+8)==0xa5a5a5a5a5a5a5a5ULL&&read(CELL+24)==0xa5a5a5a5a5a5a5a5ULL);
 }
 for(unsigned op=0;op<3;++op)require(call(op,0,2)==0x80020016u);
 std::printf("{\"status\":\"pass\",\"aot_service_calls\":%llu,\"lifecycles\":4096,\"live_limit\":2,\"guard_bytes_unchanged\":true}\n",(unsigned long long)cases);
}
