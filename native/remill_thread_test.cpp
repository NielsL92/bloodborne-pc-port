// SPDX-License-Identifier: GPL-2.0-or-later
// Authored thread-boundary contracts, not a console kernel or arbitrary memory model.
#define NOMINMAX
#include <windows.h>
#include <winternl.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <vector>
#include <thread>
#include <mutex>
#include <barrier>
#include <algorithm>
#include <atomic>
#include <remill/Arch/X86/Runtime/State.h>
static_assert(offsetof(TEB,TlsSlots)==0x1480);
constexpr uint64_t BASE=0x1002000000, RET=0xfeedaa01;
constexpr unsigned THREADS=4, ITER=2048;
using Original=uint64_t(__attribute__((sysv_abi)) *)(uint64_t,uint64_t);
struct Region{uint64_t base;size_t size;};
struct Memory{Region regions[3];uint64_t returned=0;bool locked=false;unsigned atomic_count=0;};
static std::mutex atomic_lock;
static void fail(const char* msg){std::fprintf(stderr,"FAIL %s\n",msg);std::exit(2);}
static void check(Memory*m,uint64_t a,size_t n) {
 for(auto r:m->regions)if(a>=r.base&&a-r.base<=r.size&&n<=r.size-(a-r.base))return;
 fail("out-of-contract address");
}
extern "C" uint64_t __remill_read_memory_64(Memory*m,uint64_t a){check(m,a,8);if(a%8)fail("fixture requires aligned memory");return std::atomic_ref<uint64_t>(*(uint64_t*)a).load(std::memory_order_relaxed);}
extern "C" Memory* __remill_write_memory_64(Memory*m,uint64_t a,uint64_t v){check(m,a,8);if(a%8)fail("fixture requires aligned memory");std::atomic_ref<uint64_t>(*(uint64_t*)a).store(v,std::memory_order_relaxed);return m;}
extern "C" Memory* __remill_atomic_begin(Memory*m){if(m->locked)fail("nested atomic");atomic_lock.lock();m->locked=true;++m->atomic_count;return m;}
extern "C" Memory* __remill_atomic_end(Memory*m){if(!m->locked)fail("unpaired atomic");m->locked=false;atomic_lock.unlock();return m;}
// Seq-cst fences conservatively implement all four Remill barrier classes.
// The publication fixture exercises MFENCE plus relaxed aligned atomic memory.
extern "C" Memory* __remill_barrier_load_load(Memory*m){std::atomic_thread_fence(std::memory_order_seq_cst);return m;}
extern "C" Memory* __remill_barrier_load_store(Memory*m){std::atomic_thread_fence(std::memory_order_seq_cst);return m;}
extern "C" Memory* __remill_barrier_store_load(Memory*m){std::atomic_thread_fence(std::memory_order_seq_cst);return m;}
extern "C" Memory* __remill_barrier_store_store(Memory*m){std::atomic_thread_fence(std::memory_order_seq_cst);return m;}
extern "C" bool __remill_compare_eq(bool b){return b;}
extern "C" bool __remill_compare_neq(bool b){return b;}
extern "C" uint8_t __remill_undefined_8(){return 0;}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" Memory* __remill_function_return(State*s,uint64_t pc,Memory*m){m->returned=pc;s->gpr.rip.qword=pc;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("explicit remill error");return nullptr;}
extern "C" Memory* sub_1002000000(State*,uint64_t,Memory*);
extern "C" Memory* sub_1002000100(State*,uint64_t,Memory*);
extern "C" Memory* sub_1002000200(State*,uint64_t,Memory*);
extern "C" Memory* sub_1002000300(State*,uint64_t,Memory*);
using Aot=Memory*(*)(State*,uint64_t,Memory*);
static uint64_t invoke(Aot f,uint64_t pc,Memory&m,uint64_t*stack,uint64_t a,uint64_t b){
 State s{};s.gpr.rdi.qword=a;s.gpr.rsi.qword=b;s.gpr.rsp.qword=uint64_t(stack+127);
 s.addr.gs_base.qword=uint64_t(NtCurrentTeb());s.gpr.rip.qword=pc;
 stack[127]=RET; m.returned=0;
 f(&s,pc,&m);
 if(m.returned!=RET||s.gpr.rip.qword!=RET||s.gpr.rsp.qword!=uint64_t(stack+128)||m.locked)fail("return/lock contract");
 return s.gpr.rax.qword;
}
static void protect(void*p,DWORD value){DWORD old;if(!VirtualProtect(p,0x10000,value,&old))fail("protect");
 MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(p,&mbi,sizeof(mbi));if(mbi.Protect!=value)fail("NX verification");}
static void load(uint8_t*p,const std::string&name){std::ifstream f(name,std::ios::binary);std::vector<char>b((std::istreambuf_iterator<char>(f)),{});if(b.empty()||b.size()>128)fail("bytes");std::memcpy(p,b.data(),b.size());}
int main(int argc,char**argv){
 if(argc!=2)fail("fixture directory");
 auto*code=(uint8_t*)VirtualAlloc((void*)BASE,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 if(uint64_t(code)!=BASE)fail("allocation");
 load(code,std::string(argv[1])+"/tls/original.bin");load(code+256,std::string(argv[1])+"/atomic/original.bin");
 load(code+512,std::string(argv[1])+"/publish/original.bin");load(code+768,std::string(argv[1])+"/consume/original.bin");
 FlushInstructionCache(GetCurrentProcess(),code,0x10000);
 DWORD slot=TlsAlloc();if(slot>=64)fail("fixture requires an inline Windows TLS slot");
 uint64_t final_tls[2][THREADS]{};unsigned locked=0;
 for(unsigned mode=0;mode<2;++mode){
  protect(code,mode?PAGE_READONLY:PAGE_EXECUTE_READ);
  std::barrier start(THREADS);std::vector<std::thread> workers;
  for(unsigned t=0;t<THREADS;++t)workers.emplace_back([&,t]{
   uint64_t local=10000*t,stack[128]{};if(!TlsSetValue(slot,&local))fail("TlsSetValue");
   auto*teb=NtCurrentTeb();if(teb->TlsSlots[slot]!=&local)fail("TLS setup");
   Memory m{{{uint64_t(stack),sizeof(stack)},{uint64_t(&local),8},{uint64_t(teb),sizeof(TEB)}}};
   start.arrive_and_wait();
   for(unsigned i=0;i<ITER;++i){
    auto value=mode?invoke(sub_1002000000,BASE,m,stack,slot,t+1):((Original)code)(slot,t+1);
    if(value!=10000*t+uint64_t(i+1)*(t+1))fail("per-thread TLS isolation");
   }
   final_tls[mode][t]=local;TlsSetValue(slot,nullptr);
  });
  for(auto&w:workers)w.join();
 }
 if(std::memcmp(final_tls[0],final_tls[1],sizeof(final_tls[0])))fail("TLS differential");
 for(unsigned mode=0;mode<2;++mode){
  protect(code,mode?PAGE_READONLY:PAGE_EXECUTE_READ);
  alignas(64) uint64_t shared=0;
  std::vector<uint64_t> tickets(THREADS*ITER);std::barrier start(THREADS);std::vector<std::thread>workers;
  unsigned calls[THREADS]{};
  for(unsigned t=0;t<THREADS;++t)workers.emplace_back([&,t]{
   uint64_t stack[128]{};
   Memory m{{{uint64_t(stack),sizeof(stack)},{uint64_t(&shared),8},{0,0}}};
   start.arrive_and_wait();
   for(unsigned i=0;i<ITER;++i)
    tickets[t*ITER+i]=mode?invoke(sub_1002000100,BASE+256,m,stack,uint64_t(&shared),1):((Original)(code+256))(uint64_t(&shared),1);
   calls[t]=m.atomic_count;
  });
  for(auto&w:workers)w.join();
  if(shared!=THREADS*ITER)fail("atomic final count");
  std::sort(tickets.begin(),tickets.end());for(unsigned i=0;i<tickets.size();++i)if(tickets[i]!=i)fail("atomic linearizable tickets");
  if(mode)for(auto n:calls){if(n!=ITER)fail("locked-operation boundaries");locked+=n;}
 }
 for(unsigned mode=0;mode<2;++mode){
  protect(code,mode?PAGE_READONLY:PAGE_EXECUTE_READ);
  alignas(64) uint64_t mailbox[2]{};
  std::barrier start(2);
  std::thread writer([&]{
   uint64_t stack[128]{};Memory m{{{uint64_t(stack),sizeof(stack)},{uint64_t(mailbox),sizeof(mailbox)},{0,0}}};
   start.arrive_and_wait();
   for(unsigned i=1;i<=ITER*4;++i){
    while(std::atomic_ref<uint64_t>(mailbox[1]).load(std::memory_order_acquire)!=0)std::this_thread::yield();
    if(mode)invoke(sub_1002000200,BASE+512,m,stack,uint64_t(mailbox),i);
    else ((Original)(code+512))(uint64_t(mailbox),i);
   }
  });
  std::thread reader([&]{
   uint64_t stack[128]{};Memory m{{{uint64_t(stack),sizeof(stack)},{uint64_t(mailbox),sizeof(mailbox)},{0,0}}};
   start.arrive_and_wait();
   for(unsigned i=1;i<=ITER*4;++i){
    uint64_t value=mode?invoke(sub_1002000300,BASE+768,m,stack,uint64_t(mailbox),0):
                        ((Original)(code+768))(uint64_t(mailbox),0);
    if(value!=i)fail("MFENCE publication order");
   }
  });
  writer.join();reader.join();
  if(mailbox[0]!=ITER*4||mailbox[1]!=0)fail("mailbox final state");
 }
 TlsFree(slot);
 std::printf("{\"threads\":%u,\"tls_cases_per_path\":%u,\"atomic_cases_per_path\":%u,\"atomic_pairs\":%u,\"original_code_NX_during_aot\":true,\"contract\":\"TLS per-thread isolation and final values; locked XADD complete ticket permutation and total; logical returns; 8192 MFENCE publication handshakes per path; aligned relaxed atomic memory with conservative seq-cst barriers; no arbitrary unregistered writers or exhaustive memory-model proof\"}\n",THREADS,THREADS*ITER,THREADS*ITER,locked);
}
