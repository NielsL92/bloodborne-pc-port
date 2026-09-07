// SPDX-License-Identifier: GPL-2.0-or-later
#include "rwlock.h"
#include "rwlock-entries.h"
#include <atomic>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <vector>
constexpr uint64_t PC=0x100400000,DATA=0x78000000,STACK=0x79000000,RET=0xfeed9001;
static const bb_runtime::Target targets[]=RWLOCK_TARGETS;
static const bb_runtime::Import imports[]={
 {0x900003000,"init","libkernel","libkernel",bb_runtime::rwlock_init,0},{0x900003010,"read","libkernel","libkernel",bb_runtime::rwlock_rdlock,0},{0x900003020,"write","libkernel","libkernel",bb_runtime::rwlock_wrlock,0},{0x900003030,"tryread","libkernel","libkernel",bb_runtime::rwlock_tryrdlock,0},{0x900003040,"trywrite","libkernel","libkernel",bb_runtime::rwlock_trywrlock,0},{0x900003050,"unlock","libkernel","libkernel",bb_runtime::rwlock_unlock,0},{0x900003060,"destroy","libkernel","libkernel",bb_runtime::rwlock_destroy,0}};
static const bb_runtime::Tables tables{targets,7,nullptr,0,imports,7,"authored-native-rwlock-v1"};
static std::atomic<uint64_t> calls=0;
static void require(bool v){if(!v)std::abort();}
struct Context {
 State s{};Memory m{};uint64_t stack;
 Context(bb_runtime::AddressSpace& space,bb_runtime::Rwlocks& locks,unsigned index):stack(STACK+index*512+504){m.space=&space;m.state=&s;m.tables=&tables;m.owner_thread=GetCurrentThreadId();m.rwlocks=&locks;}
 uint64_t call(unsigned op,uint64_t cell=DATA,uint64_t attr=0,uint64_t name=0){s=State{};s.gpr.rip.qword=PC+256*op;s.gpr.rsp.qword=stack;s.gpr.rdi.qword=cell;s.gpr.rsi.qword=attr;s.gpr.rdx.qword=name;s.gpr.rbx.qword=0xdead111122223333;s.gpr.rbp.qword=0x444455556666aaaa;s.gpr.r12.qword=12;s.gpr.r13.qword=13;s.gpr.r14.qword=14;s.gpr.r15.qword=15;m.entry=s.gpr.rip.qword;m.space->write(&m,stack,&RET,8);require(bb_runtime::dispatch(&s,s.gpr.rip.qword,&m)==&m);require(s.gpr.rsp.qword==stack+8&&s.gpr.rip.qword==RET&&s.gpr.rbx.qword==0xdead111122223333&&s.gpr.rbp.qword==0x444455556666aaaa&&s.gpr.r12.qword==12&&s.gpr.r13.qword==13&&s.gpr.r14.qword==14&&s.gpr.r15.qword==15);++calls;return s.gpr.rax.qword;}
};
int main(int argc,char** argv){
 if(argc!=2)return 2;bb_runtime::AddressSpace space;space.add(DATA,256,3);space.add(STACK,4096,3);space.guard(DATA+128,8,"rwlock-unresolved");space.seal();bb_runtime::Rwlocks locks(space,2);Context main(space,locks,0);bb_runtime::validate_tables(tables);
 if(!std::strcmp(argv[1],"missing")){main.m.rwlocks=nullptr;main.call(0);return 3;}
 if(!std::strcmp(argv[1],"pointer")){main.call(0,DATA+252);return 3;}
 if(!std::strcmp(argv[1],"guard")){main.call(0,DATA+128);return 3;}
 if(!std::strcmp(argv[1],"attr")){main.call(0,DATA,DATA+16);return 3;}
 if(!std::strcmp(argv[1],"name")){main.call(0,DATA,0,DATA+16);return 3;}
 if(!std::strcmp(argv[1],"static")){main.call(1);return 3;}
 if(!std::strcmp(argv[1],"reinit")){main.call(0);main.call(0);return 3;}
 if(!std::strcmp(argv[1],"opaque")){main.call(0);uint64_t handle=0;space.read(&main.m,DATA,&handle,8);space.read(&main.m,handle,&handle,8);return 3;}
 if(std::strcmp(argv[1],"positive"))return 2;
 constexpr uint64_t Busy=0x80020010,Deadlock=0x8002000b,Invalid=0x80020016,Permission=0x80020001;
 for(unsigned i=0;i<4096;++i){require(main.call(0)==0);require(main.call(1)==0);require(main.call(3)==0);require(main.call(4)==Busy);require(main.call(2)==Deadlock);require(main.call(6)==Busy);require(main.call(5)==0);require(main.call(5)==0);require(main.call(2)==0);require(main.call(3)==Busy);require(main.call(1)==Deadlock);require(main.call(4)==Busy);require(main.call(5)==0);require(main.call(5)==Permission);require(main.call(6)==0);require(main.call(1)==Invalid);}
 require(main.call(0)==0&&main.call(0,DATA+8)==0);require(main.call(0,DATA+16)==0x8002000c);require(main.call(6,DATA+8)==0);
 require(main.call(1)==0);std::thread shared([&]{Context c(space,locks,1);require(c.call(1)==0);bb_runtime::RwlockInfo info;require(locks.snapshot(&c.m,DATA,info)&&info.readers==2);require(c.call(5)==0);});shared.join();require(main.call(1)==0);
 HANDLE writer_acquired=CreateEventW(nullptr,TRUE,FALSE,nullptr),release_writer=CreateEventW(nullptr,TRUE,FALSE,nullptr),reader_acquired=CreateEventW(nullptr,TRUE,FALSE,nullptr);require(writer_acquired&&release_writer&&reader_acquired);
 std::thread writer([&]{Context c(space,locks,1);require(c.call(5)==Permission);require(c.call(4)==Busy);require(c.call(6)==Busy);require(c.call(2)==0);SetEvent(writer_acquired);require(WaitForSingleObject(release_writer,5000)==WAIT_OBJECT_0);require(c.call(5)==0);});
 auto waiters=[&](bool write){auto deadline=GetTickCount64()+5000;for(;;){bb_runtime::RwlockInfo info;require(locks.snapshot(&main.m,DATA,info));if(write?info.waiting_writers>0:info.waiting_readers>0)break;require(GetTickCount64()<deadline);Sleep(1);}};
 waiters(true);require(main.call(3)==0);require(main.call(5)==0);require(main.call(5)==0);require(WaitForSingleObject(writer_acquired,0)==WAIT_TIMEOUT);require(main.call(5)==0);require(WaitForSingleObject(writer_acquired,5000)==WAIT_OBJECT_0);
 std::thread reader([&]{Context c(space,locks,2);require(c.call(3)==Busy);require(c.call(1)==0);SetEvent(reader_acquired);require(c.call(5)==0);});waiters(false);require(WaitForSingleObject(reader_acquired,0)==WAIT_TIMEOUT);require(main.call(6)==Busy);SetEvent(release_writer);writer.join();reader.join();require(WaitForSingleObject(reader_acquired,0)==WAIT_OBJECT_0);CloseHandle(writer_acquired);CloseHandle(release_writer);CloseHandle(reader_acquired);
 uint64_t zero=0;space.write(&main.m,DATA+64,&zero,8);std::vector<std::thread> workers;
 for(unsigned n=0;n<3;++n)workers.emplace_back([&,n]{Context c(space,locks,n+1);for(unsigned i=0;i<512;++i){require(c.call(2)==0);uint64_t value=0;space.read(&c.m,DATA+64,&value,8);++value;space.write(&c.m,DATA+64,&value,8);require(c.call(5)==0);}});
 for(auto& w:workers)w.join();uint64_t total=0;space.read(&main.m,DATA+64,&total,8);require(total==1536&&main.call(6)==0);
 std::printf("{\"status\":\"pass\",\"aot_service_calls\":%llu,\"lifecycles\":4096,\"shared_readers\":true,\"recursive_reader\":true,\"blocked_writer\":true,\"blocked_reader\":true,\"writer_increments\":1536,\"game_execution\":false}\n",(unsigned long long)calls.load());
}
