// SPDX-License-Identifier: GPL-2.0-or-later
#include "main_tls.h"
#include "tls-entries.h"
#include <array>
#include <atomic>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <vector>
constexpr uint64_t PC=0x100500000,TCB=0x74000010000,TLS_BYTES=1872,STACK=0x79000000,RET=0xfeedb001;
static const bb_runtime::Target targets[]=TLS_TARGETS;
static const bb_runtime::Tables tables{targets,3,nullptr,0,nullptr,0,"authored-main-tls-v1"};
static void require(bool value){if(!value)std::abort();}
int main(int argc,char** argv){
 if(argc!=2)return 2;bool positive=!std::strcmp(argv[1],"positive");bb_runtime::AddressSpace space;
 for(unsigned i=0;i<8;++i){uint64_t tcb=TCB+i*0x10000;space.add(tcb-TLS_BYTES,TLS_BYTES+64,3);space.guard(tcb+8,56,"unimplemented-TCB-fields");}space.add(STACK,4096,3);space.seal();bb_runtime::validate_tables(tables);std::atomic<uint64_t> cases=0;std::vector<std::thread> workers;
 auto work=[&](unsigned index){State s{};Memory m{};m.space=&space;m.state=&s;m.tables=&tables;m.owner_thread=GetCurrentThreadId();m.entry=PC;uint64_t tcb=TCB+index*0x10000;bb_runtime::MainTls tls(space,tcb,TLS_BYTES,16);std::array<uint8_t,17> initial{};for(unsigned n=0;n<initial.size();++n)initial[n]=uint8_t(index*19+n+1);
  if(std::strcmp(argv[1],"missing")){tls.initialize(&m,positive?initial.data():nullptr,positive?initial.size():0);require(tls.initialized()&&s.addr.fs_base.qword==tcb);}
  auto call=[&](unsigned op,int64_t offset,uint64_t value){auto fs=s.addr.fs_base.qword;s=State{};s.addr.fs_base.qword=fs;s.gpr.rip.qword=PC+256*op;s.gpr.rsp.qword=STACK+index*512+504;s.gpr.rdi.qword=uint64_t(offset);s.gpr.rsi.qword=value;s.gpr.rbx.qword=0x123456789abcdef0;s.gpr.rbp.qword=0x11223344;s.gpr.r12.qword=12;s.gpr.r13.qword=13;s.gpr.r14.qword=14;s.gpr.r15.qword=15;space.write(&m,s.gpr.rsp.qword,&RET,8);require(bb_runtime::dispatch(&s,s.gpr.rip.qword,&m)==&m);require(s.gpr.rsp.qword==STACK+index*512+512&&s.gpr.rip.qword==RET&&s.addr.fs_base.qword==fs&&s.gpr.rbx.qword==0x123456789abcdef0&&s.gpr.rbp.qword==0x11223344&&s.gpr.r12.qword==12&&s.gpr.r13.qword==13&&s.gpr.r14.qword==14&&s.gpr.r15.qword==15);++cases;return s.gpr.rax.qword;};
  if(!std::strcmp(argv[1],"missing")){call(2,0,0);return;}
  if(!std::strcmp(argv[1],"guard")){call(1,8,0);return;}
  if(!std::strcmp(argv[1],"lower")){call(1,-int64_t(TLS_BYTES)-1,0);return;}
  if(!std::strcmp(argv[1],"duplicate")){bool rejected=false;try{tls.initialize(&m,nullptr,0);}catch(const std::exception&){rejected=true;}require(rejected);return;}
  require(positive&&call(2,0,0)==tcb);std::array<uint8_t,TLS_BYTES> observed{};space.read(&m,tcb-TLS_BYTES,observed.data(),observed.size());for(unsigned n=0;n<TLS_BYTES;++n)require(observed[n]==(n<initial.size()?initial[n]:0));
  for(unsigned n=0;n<TLS_BYTES/8;++n){uint64_t value=0x123456789abcdef0ULL^(uint64_t(index)<<52)^n;require(call(0,-int64_t(TLS_BYTES)+n*8,value)==value);require(call(1,-int64_t(TLS_BYTES)+n*8,0)==value);}
 };
 if(positive){for(unsigned i=0;i<8;++i)workers.emplace_back(work,i);for(auto& w:workers)w.join();State state{};Memory m{};m.space=&space;m.state=&state;m.owner_thread=GetCurrentThreadId();for(unsigned i=0;i<8;++i)for(unsigned n=0;n<TLS_BYTES/8;++n){uint64_t value=0;space.read(&m,TCB+i*0x10000-TLS_BYTES+n*8,&value,8);require(value==(0x123456789abcdef0ULL^(uint64_t(i)<<52)^n));}}
 else work(0);
 std::printf("{\"status\":\"pass\",\"aot_calls\":%llu,\"native_threads\":%u,\"template_bytes_per_thread\":1872,\"game_execution\":false}\n",(unsigned long long)cases.load(),positive?8:0);
}
