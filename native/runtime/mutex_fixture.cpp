// SPDX-License-Identifier: GPL-2.0-or-later
#include "mutex.h"
#include <atomic>
#include <cstring>
#include <cstdlib>
#include <thread>
#include "mutex-entries.h"
static constexpr uint64_t PC=0x100200000ULL,DATA=0x76000000ULL,STACK=0x77000000ULL,RET=0xfeed4001ULL;
static const bb_runtime::Target targets[]=MUTEX_TARGETS;
static const bb_runtime::Import imports[]={
 {0x900001000ULL,"F8bUHwAG284","libkernel","libkernel",bb_runtime::mutexattr_init,0},
 {0x900001010ULL,"iMp8QpE+XO4","libkernel","libkernel",bb_runtime::mutexattr_settype,0},
 {0x900001020ULL,"smWEktiyyG0","libkernel","libkernel",bb_runtime::mutexattr_destroy,0},
 {0x900001030ULL,"cmo1RIYva9o","libkernel","libkernel",bb_runtime::mutex_init,0},
 {0x900001040ULL,"9UK1vLZQft4","libkernel","libkernel",bb_runtime::mutex_lock,0},
 {0x900001050ULL,"upoVrzMHFeE","libkernel","libkernel",bb_runtime::mutex_trylock,0},
 {0x900001060ULL,"tn3VlD0hG60","libkernel","libkernel",bb_runtime::mutex_unlock,0},
 {0x900001070ULL,"2Of0f+3mhhE","libkernel","libkernel",bb_runtime::mutex_destroy,0}};
static const bb_runtime::Tables tables{targets,8,nullptr,0,imports,8,"authored-native-mutex-v1"};
static std::atomic<uint64_t> calls=0;
static void require(bool v){if(!v)std::abort();}
struct Client{
 State state{};Memory memory{};uint64_t stack;
 Client(bb_runtime::AddressSpace& space,bb_runtime::MutexAttributes& attrs,bb_runtime::Mutexes& mutexes,unsigned index):stack(STACK+index*1024){memory.space=&space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.mutex_attributes=&attrs;memory.mutexes=&mutexes;}
 void write(uint64_t at,uint64_t value){memory.space->write(&memory,at,&value,8);}
 uint64_t read(uint64_t at){uint64_t v=0;memory.space->read(&memory,at,&v,8);return v;}
 uint64_t call(unsigned op,uint64_t cell,uint64_t arg=0,uint64_t name=0){state=State{};state.gpr.rip.qword=PC+op*256;state.gpr.rsp.qword=stack+1016;state.gpr.rdi.qword=cell;state.gpr.rsi.qword=arg;state.gpr.rdx.qword=name;state.gpr.rbx.qword=0xabcdef0011223344ULL;state.gpr.rbp.qword=0x1122334455667788ULL;state.gpr.r12.qword=0x91;state.gpr.r13.qword=0x92;state.gpr.r14.qword=0x93;state.gpr.r15.qword=0x94;memory.entry=state.gpr.rip.qword;write(stack+1016,RET);require(bb_runtime::dispatch(&state,state.gpr.rip.qword,&memory)==&memory);require(state.gpr.rip.qword==RET&&state.gpr.rsp.qword==stack+1024&&state.gpr.rbx.qword==0xabcdef0011223344ULL&&state.gpr.rbp.qword==0x1122334455667788ULL&&state.gpr.r12.qword==0x91&&state.gpr.r13.qword==0x92&&state.gpr.r14.qword==0x93&&state.gpr.r15.qword==0x94);++calls;return state.gpr.rax.qword;}
};
int main(int argc,char** argv){
 if(argc!=2)return 2;bb_runtime::AddressSpace space;space.add(DATA,256,3);space.add(STACK,4096,3);space.seal();bb_runtime::MutexAttributes attrs(space);bb_runtime::Mutexes mutexes(space,2);Client main(space,attrs,mutexes,0);bb_runtime::validate_tables(tables);const uint64_t attr=DATA+8,cell=DATA+24;
 if(!std::strcmp(argv[1],"bad-pointer")){main.call(3,DATA+252);return 3;}
 if(!std::strcmp(argv[1],"missing-provider")){main.memory.mutexes=nullptr;main.call(3,cell);return 3;}
 if(!std::strcmp(argv[1],"double-init")){main.call(3,cell);main.call(3,cell);return 3;}
 if(!std::strcmp(argv[1],"opaque-read")){main.call(3,cell);main.read(main.read(cell));return 3;}
 if(!std::strcmp(argv[1],"static-init")){main.write(cell,0);main.call(4,cell);return 3;}
 if(!std::strcmp(argv[1],"name")){main.call(3,cell,0,DATA+80);return 3;}
 if(!std::strcmp(argv[1],"normal-self")){main.call(0,attr);main.call(1,attr,3);main.call(3,cell,attr);main.call(4,cell);main.call(4,cell);return 3;}
 if(std::strcmp(argv[1],"positive"))return 2;
 uint64_t previous=0;
 for(uint32_t i=0;i<4096;++i){
  uint32_t type=1+i%4;require(main.call(0,attr)==0);require(main.call(1,attr,type)==0);require(main.call(3,cell,attr)==0);uint64_t token=main.read(cell);require(token>previous);previous=token;require(main.call(2,attr)==0);bb_runtime::MutexInfo info{};require(mutexes.snapshot(&main.memory,cell,info)&&info.type==type&&info.owner==0&&info.depth==0);
  require(main.call(4,cell)==0);require(main.call(7,cell)==0x80020010u);
  if(type==2){require(main.call(4,cell)==0);require(main.call(5,cell)==0);require(main.call(6,cell)==0);require(main.call(6,cell)==0);}else{require(main.call(5,cell)==0x80020010u);if(type!=3)require(main.call(4,cell)==0x8002000bu);}
  require(main.call(6,cell)==0);require(main.call(6,cell)==0x80020001u);require(main.call(7,cell)==0&&main.read(cell)==2);require(main.call(4,cell)==0x80020016u);
 }
 require(main.call(3,cell)==0);require(main.call(3,DATA+40)==0);main.write(DATA+56,0x1234);require(main.call(3,DATA+56)==0x8002000cu&&main.read(DATA+56)==0x1234);require(main.call(7,DATA+40)==0);require(main.call(7,cell)==0);
 // Blocked waiter cannot own the mutex until the final recursive release.
 require(main.call(0,attr)==0);require(main.call(1,attr,2)==0);require(main.call(3,cell,attr)==0);require(main.call(2,attr)==0);require(main.call(4,cell)==0);require(main.call(4,cell)==0);
 std::atomic<bool> ready=false,acquired=false;
 std::thread waiter([&]{Client child(space,attrs,mutexes,1);require(child.call(5,cell)==0x80020010u);require(child.call(6,cell)==0x80020001u);require(child.call(7,cell)==0x80020010u);ready=true;require(child.call(4,cell)==0);acquired=true;require(child.call(6,cell)==0);});
 auto wait_for_waiter=[&]{ULONGLONG end=GetTickCount64()+5000;for(;;){bb_runtime::MutexInfo info{};require(mutexes.snapshot(&main.memory,cell,info));if(ready&&info.waiters==1)return;require(GetTickCount64()<end);Sleep(1);}};
 wait_for_waiter();require(!acquired);require(main.call(6,cell)==0);bb_runtime::MutexInfo info{};require(mutexes.snapshot(&main.memory,cell,info)&&info.owner==GetCurrentThreadId()&&info.depth==1&&info.waiters==1&&!acquired);require(main.call(6,cell)==0);waiter.join();require(acquired);
 // Three native threads update shared registered memory through AOT lock/unlock calls.
 main.write(DATA+88,0);std::thread workers[3];
 for(unsigned n=0;n<3;++n)workers[n]=std::thread([&,n]{Client worker(space,attrs,mutexes,n+1);for(unsigned i=0;i<512;++i){require(worker.call(4,cell)==0);auto v=worker.read(DATA+88);worker.write(DATA+88,v+1);require(worker.call(6,cell)==0);}});
 for(auto& thread:workers)thread.join();require(main.read(DATA+88)==1536);require(main.call(7,cell)==0);
 std::printf("{\"status\":\"pass\",\"aot_service_calls\":%llu,\"lifecycles\":4096,\"threaded_increments\":1536,\"recursive_waiter_checked\":true}\n",(unsigned long long)calls.load());
}
