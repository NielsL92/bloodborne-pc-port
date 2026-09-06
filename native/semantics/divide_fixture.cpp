// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <xmmintrin.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint8_t backing[16];uint64_t stack[8];unsigned bytes,returns;uint64_t returned;};
struct Spec {unsigned width,operand;bool signed_divide;uint64_t pc;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,const void*);
#include "divide-entries.h"
struct Case {uint64_t ra,rd,rc,rhs,flags,expected_ra,expected_rd,fault;};static_assert(sizeof(Case)==64);
static Memory guest,initial_memory;static State state,expected;static void* escape[5];static Memory* returned;static unsigned exit_kind,reason_out,width_out,undefined_calls;static uint64_t error_pc;static const Spec* active;
[[noreturn]] static void fail(const char* why,unsigned form=0,unsigned trial=0){std::fprintf(stderr,"FAIL %s form=%u trial=%u\n",why,form,trial);std::exit(2);}
static void read_check(Memory* m,uint64_t at,unsigned bytes){if(m!=&guest||active->operand!=3||at!=uint64_t(m->backing+3)||bytes!=active->width/8)fail("memory span");m->bytes+=bytes;}
#define READ(N,T) extern "C" T __remill_read_memory_##N(Memory* m,uint64_t at){read_check(m,at,N/8);T v;std::memcpy(&v,reinterpret_cast<void*>(at),N/8);return v;}
READ(8,uint8_t) READ(16,uint16_t) READ(32,uint32_t)
#undef READ
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at==uint64_t(m->stack+4)){++m->returns;return m->stack[4];}read_check(m,at,8);uint64_t v;std::memcpy(&v,reinterpret_cast<void*>(at),8);return v;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" Memory* __remill_error(State* s,uint64_t pc,Memory* m){if(s!=&state||m!=&guest)fail("error arguments");exit_kind=2;error_pc=pc;__builtin_longjmp(escape,1);}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing authored block");}
extern "C" uint8_t __remill_undefined_8(){return uint8_t((++undefined_calls)&1);}
extern "C" [[noreturn]] void __bb_native_divide_fault(Memory* m,State* s,uint32_t reason,uint32_t width){if(m!=&guest||s!=&state||!reason)fail("division fault arguments");exit_kind=1;reason_out=reason;width_out=width;__builtin_longjmp(escape,1);}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){
 // Authored-test escape only; not a guest/native production unwind protocol.
 asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");
 if(__builtin_setjmp(escape)==0)returned=fn(&state,pc,&guest);
}
struct Output {uint64_t ra,rd,rc,flags;};struct Fault {DWORD code;uint64_t pc;Output out;};static Fault hardware_fault,aot_fault;static volatile bool in_aot=false;
static int capture(EXCEPTION_POINTERS* info,Fault* f){f->code=info->ExceptionRecord->ExceptionCode;f->pc=info->ContextRecord->Rip;f->out={info->ContextRecord->Rax,info->ContextRecord->Rdx,info->ContextRecord->Rcx,info->ContextRecord->EFlags};return EXCEPTION_EXECUTE_HANDLER;}
// Confine unexpected hardware arithmetic faults to this authored subprocess.
// Escaping the live POD-only bridge records a failure; it is not guest delivery.
static LONG CALLBACK capture_aot_veh(EXCEPTION_POINTERS* info){
 if(in_aot&&(info->ExceptionRecord->ExceptionCode==EXCEPTION_INT_DIVIDE_BY_ZERO||info->ExceptionRecord->ExceptionCode==EXCEPTION_INT_OVERFLOW)){
  capture(info,&aot_fault);exit_kind=3;__builtin_longjmp(escape,1);
 }
 return EXCEPTION_CONTINUE_SEARCH;
}
__declspec(noinline) static void hardware_run(Hardware fn,const Case* in,Output* out,const void* mem){hardware_fault={};__try{fn(in,out,mem);}__except(capture(GetExceptionInformation(),&hardware_fault)) {}}
__declspec(noinline) static void aot_run(Lifted fn,uint64_t pc){aot_fault={};in_aot=true;__try{invoke(fn,pc);}__except(capture(GetExceptionInformation(),&aot_fault)){exit_kind=3;}in_aot=false;}
static void set_flags(State& s,unsigned f){s.aflag.cf=f&1;s.aflag.pf=(f>>2)&1;s.aflag.af=(f>>4)&1;s.aflag.zf=(f>>6)&1;s.aflag.sf=(f>>7)&1;s.aflag.of=(f>>11)&1;}
static void copy_undefined_flags(State& dst,const State& src){dst.aflag.cf=src.aflag.cf;dst.aflag.pf=src.aflag.pf;dst.aflag.af=src.aflag.af;dst.aflag.zf=src.aflag.zf;dst.aflag.sf=src.aflag.sf;dst.aflag.of=src.aflag.of;}
int main(int argc,char** argv){
 if(argc!=2)return 2;std::setvbuf(stdout,nullptr,_IONBF,0);void* handler=AddVectoredExceptionHandler(1,capture_aot_veh);if(!handler)fail("register authored exception capture");unsigned saved=_mm_getcsr();uint64_t cases=0,mismatches=0,hardware_faults=0,errors=0,host_faults=0,native_faults=0,differences[7]={};bool printed[32][7]={};
 for(unsigned form=0;form<32;++form){
  active=&specs[form];const auto& spec=*active;char path[2048];std::snprintf(path,sizeof path,"%s/cases-%02u.bin",argv[1],form);FILE* f=std::fopen(path,"rb");if(!f)fail("open Python oracle",form);Case c;unsigned trial=0;
  while(std::fread(&c,sizeof c,1,f)==1){
   guest={};std::memcpy(guest.backing+3,&c.rhs,spec.width/8);for(auto& q:guest.stack)q=0xccccccccccccccccULL;guest.stack[4]=0xfeed0001;
   std::memset(&state,0xa5,sizeof state);state.gpr.rax.qword=c.ra;state.gpr.rdx.qword=c.rd;state.gpr.rcx.qword=c.rc;state.gpr.rdi.qword=uint64_t(guest.backing+3);state.gpr.rsp.qword=uint64_t(guest.stack+4);state.gpr.rip.qword=spec.pc;set_flags(state,unsigned(c.flags));state.x87.fxsave.mxcsr.flat=0x9fc0|((trial*7)&63);expected=state;initial_memory=guest;
   Output observed={};hardware_run(hardware[form],&c,&observed,guest.backing+3);bool should_fault=c.fault!=0;
   if(bool(hardware_fault.code)!=should_fault)fail("hardware/Python fault decision",form,trial);
   if(should_fault){if(hardware_fault.pc!=uint64_t(hardware_sites[form])||hardware_fault.out.ra!=c.ra||hardware_fault.out.rd!=c.rd||hardware_fault.out.rc!=c.rc||(hardware_fault.out.flags&0x8d5)!=(c.flags&0x8d5))fail("hardware precise fault state",form,trial);++hardware_faults;}
   else if(observed.ra!=c.expected_ra||observed.rd!=c.expected_rd||observed.rc!=c.rc){std::fprintf(stderr,"got=%llx/%llx wanted=%llx/%llx\n",(unsigned long long)observed.ra,(unsigned long long)observed.rd,(unsigned long long)c.expected_ra,(unsigned long long)c.expected_rd);fail("hardware/Python result",form,trial);}
   expected.gpr.rax.qword=c.expected_ra;expected.gpr.rdx.qword=c.expected_rd;if(!should_fault){expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;}
   unsigned host=0x1f80|((trial&3)<<13)|((trial&4)?0x40:0)|((trial&8)?0x8000:0)|((trial*3)&63);_mm_setcsr(host);exit_kind=reason_out=width_out=undefined_calls=0;error_pc=0;returned=nullptr;aot_run(lifted[form],spec.pc);unsigned host_after=_mm_getcsr();_mm_setcsr(0x1f80);if(!should_fault)copy_undefined_flags(expected,state);
   bool bad[7]={bool(exit_kind)!=should_fault,should_fault&&(state.gpr.rip.qword!=spec.pc||(exit_kind==2&&error_pc!=spec.pc)),state.gpr.rax.qword!=c.expected_ra||state.gpr.rdx.qword!=c.expected_rd||state.gpr.rcx.qword!=c.rc,std::memcmp(&state,&expected,sizeof state)!=0,guest.bytes!=(spec.operand==3?spec.width/8:0)||guest.returns!=(should_fault?0U:1U)||guest.returned!=(should_fault?0ULL:0xfeed0001ULL)||(!should_fault&&returned!=&guest)||(should_fault&&undefined_calls)||std::memcmp(guest.backing,initial_memory.backing,sizeof guest.backing)||std::memcmp(guest.stack,initial_memory.stack,sizeof guest.stack),host_after!=host,should_fault&&(exit_kind!=1||reason_out!=c.fault||width_out!=spec.width)};
   bool any=false;for(unsigned k=0;k<7;++k)if(bad[k]){++differences[k];any=true;if(!printed[form][k]){printed[form][k]=true;std::printf("{\"counterexample\":%u,\"form\":%u,\"trial\":%u,\"rax\":\"%llx\",\"rdx\":\"%llx\",\"divisor\":\"%llx\",\"expected_fault\":%llu,\"exit_kind\":%u,\"host_exception\":%lu,\"actual_pc\":\"%llx\",\"expected_pc\":\"%llx\",\"error_pc\":\"%llx\"}\n",k,form,trial,(unsigned long long)c.ra,(unsigned long long)c.rd,(unsigned long long)c.rhs,(unsigned long long)c.fault,exit_kind,aot_fault.code,(unsigned long long)state.gpr.rip.qword,(unsigned long long)spec.pc,(unsigned long long)error_pc);}}
   if(exit_kind==3)std::printf("{\"host_exception_case\":true,\"form\":%u,\"trial\":%u,\"rax\":\"%llx\",\"rdx\":\"%llx\",\"divisor\":\"%llx\",\"code\":%lu}\n",form,trial,(unsigned long long)c.ra,(unsigned long long)c.rd,(unsigned long long)c.rhs,aot_fault.code);
   mismatches+=any;errors+=exit_kind==2;host_faults+=exit_kind==3;native_faults+=exit_kind==1;++cases;++trial;
  }
  if(std::ferror(f)||trial!=10240)fail("Python oracle case count/read",form,trial);std::fclose(f);
 }
 RemoveVectoredExceptionHandler(handler);_mm_setcsr(saved);std::printf("{\"status\":\"characterized\",\"cases\":%llu,\"mismatched_cases\":%llu,\"hardware_faults\":%llu,\"remill_error_calls\":%llu,\"aot_host_exceptions\":%llu,\"native_fault_calls\":%llu,\"fault_decision_differences\":%llu,\"fault_pc_differences\":%llu,\"result_differences\":%llu,\"full_state_differences\":%llu,\"memory_exit_differences\":%llu,\"host_mxcsr_changes\":%llu,\"explicit_fault_contract_differences\":%llu,\"game_execution\":false}\n",(unsigned long long)cases,(unsigned long long)mismatches,(unsigned long long)hardware_faults,(unsigned long long)errors,(unsigned long long)host_faults,(unsigned long long)native_faults,(unsigned long long)differences[0],(unsigned long long)differences[1],(unsigned long long)differences[2],(unsigned long long)differences[3],(unsigned long long)differences[4],(unsigned long long)differences[5],(unsigned long long)differences[6]);
}
