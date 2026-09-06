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
struct Memory {alignas(32) uint8_t vectors[4][32];uint8_t backing[16];uint64_t stack[8];unsigned bytes,returns;uint64_t returned;};
struct Spec {unsigned width;bool memory,unordered;uint64_t pc;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,const void*);
#include "comi-entries.h"
static Memory guest,initial_memory;static State state,expected;static void* escape[5];static Memory* returned;static unsigned exit_kind,raised_out,unmasked_out;static uint64_t error_pc;static const Spec* active;
[[noreturn]] static void fail(const char* why,unsigned form=0,unsigned trial=0,unsigned setting=0){std::fprintf(stderr,"FAIL %s form=%u trial=%u setting=%u\n",why,form,trial,setting);std::exit(2);}
static void read_check(Memory* m,uint64_t at,unsigned size){if(m!=&guest||!active->memory||at!=uint64_t(m->backing+3)||size!=active->width)fail("memory span");m->bytes+=size;}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t at){read_check(m,at,4);uint32_t v;std::memcpy(&v,reinterpret_cast<void*>(at),4);return v;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at==uint64_t(m->stack+4)){++m->returns;return m->stack[4];}read_check(m,at,8);uint64_t v;std::memcpy(&v,reinterpret_cast<void*>(at),8);return v;}
extern "C" float __remill_read_memory_f32(Memory* m,uint64_t at){uint32_t v=__remill_read_memory_32(m,at);float f;std::memcpy(&f,&v,4);return f;}
extern "C" double __remill_read_memory_f64(Memory* m,uint64_t at){uint64_t v=__remill_read_memory_64(m,at);double f;std::memcpy(&f,&v,8);return f;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" Memory* __remill_error(State* s,uint64_t pc,Memory* m){if(s!=&state||m!=&guest)fail("error arguments");exit_kind=2;error_pc=pc;__builtin_longjmp(escape,1);}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing authored block");}
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory* m,State* s,uint32_t raised,uint32_t unmasked){if(m!=&guest||s!=&state||!unmasked)fail("SIMD fault arguments");exit_kind=1;raised_out=raised;unmasked_out=unmasked;__builtin_longjmp(escape,1);}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){
 // Authored-test escape only, with the same explicit register bridge as P2.
 asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");
 if(__builtin_setjmp(escape)==0)returned=fn(&state,pc,&guest);
}
struct Snapshot {alignas(32) uint8_t vectors[4][32];uint64_t flags;};
struct Fault {DWORD code;unsigned csr,flags;uint64_t pc;uint8_t xmm[4][16];};static Fault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.csr=info->ContextRecord->MxCsr;fault.flags=info->ContextRecord->EFlags;fault.pc=info->ContextRecord->Rip;std::memcpy(fault.xmm,&info->ContextRecord->Xmm0,sizeof fault.xmm);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const Snapshot* in,Snapshot* out,const void* mem,unsigned control){fault={};_mm_setcsr(control);__try{fn(in,out,mem);fault.csr=_mm_getcsr();fault.flags=unsigned(out->flags);}__except(capture(GetExceptionInformation())){}_mm_setcsr(0x1f80);}
static unsigned flags(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
static void set_flags(State& s,unsigned f){s.aflag.cf=f&1;s.aflag.pf=(f>>2)&1;s.aflag.af=(f>>4)&1;s.aflag.zf=(f>>6)&1;s.aflag.sf=(f>>7)&1;s.aflag.of=(f>>11)&1;}
static unsigned initial_flags(unsigned n){return (n&1)|((n&2)<<1)|((n&4)<<2)|((n&8)<<3)|((n&16)<<3)|((n&32)<<6);}
static uint64_t rng=0xad831780265d4293ULL;static uint64_t next(){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return rng;}
// Host floating comparison is used only after raw NaNs/DAZ are handled and
// under a known masked, non-DAZ environment. Hardware is a separate reference.
__declspec(noinline) static unsigned reference(uint64_t x,uint64_t y,unsigned width,bool unordered,unsigned control,unsigned& raised){
 uint64_t sign=width==4?0x80000000ULL:0x8000000000000000ULL,inf=width==4?0x7f800000ULL:0x7ff0000000000000ULL,quiet=width==4?0x400000ULL:0x8000000000000ULL;
 uint64_t mx=x&(sign-1),my=y&(sign-1);bool nx=mx>inf,ny=my>inf,dx=mx&&!(mx&inf),dy=my&&!(my&inf);raised=0;
 if(nx||ny){if(!unordered||(nx&&!(x&quiet))||(ny&&!(y&quiet)))raised=1;return 0x45;}
 if(control&0x40){if(dx)x&=sign;if(dy)y&=sign;}else if(dx||dy)raised=2;
 double a,b;if(width==4){uint32_t xx=uint32_t(x),yy=uint32_t(y);float aa,bb;std::memcpy(&aa,&xx,4);std::memcpy(&bb,&yy,4);a=aa;b=bb;}else{std::memcpy(&a,&x,8);std::memcpy(&b,&y,8);}
 return a>b?0:a<b?1:0x40;
}
int main(){
 static const uint32_t values32[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0x3f7fffff,0x3f800001,0x7f7fffff,0xff7fffff};
 static const uint64_t values64[]={0,0x8000000000000000ULL,1,0x8000000000000001ULL,0xfffffffffffffULL,0x800fffffffffffffULL,0x10000000000000ULL,0x8010000000000000ULL,0x3ff0000000000000ULL,0xbff0000000000000ULL,0x4000000000000000ULL,0xc000000000000000ULL,0x7ff0000000000000ULL,0xfff0000000000000ULL,0x7ff8000000000000ULL,0xfff8000000000000ULL,0x7ff0000000000001ULL,0xfff0000000000001ULL,0x7fffffffffffffffULL,0xffffffffffffffffULL,0x3fefffffffffffffULL,0x3ff0000000000001ULL,0x7fefffffffffffffULL,0xffefffffffffffffULL};
 unsigned saved=_mm_getcsr();uint64_t cases=0,mismatches=0,hardware_faults=0,errors=0,differences[6]={};bool printed[16][6]={};
 for(unsigned form=0;form<16;++form)for(unsigned trial=0;trial<832;++trial)for(unsigned setting=0;setting<64;++setting){
  active=&specs[form];const auto& spec=*active;uint64_t x,y;if(trial<576){x=spec.width==4?values32[trial/24]:values64[trial/24];y=spec.width==4?values32[trial%24]:values64[trial%24];}else{x=next();y=next();if(spec.width==4){x=uint32_t(x);y=uint32_t(y);}}
  guest={};for(auto& v:guest.vectors)for(auto& b:v)b=uint8_t(next());std::memcpy(guest.vectors[1],&x,spec.width);std::memcpy(guest.vectors[2],&y,spec.width);std::memcpy(guest.backing+3,&y,spec.width);for(auto& q:guest.stack)q=0xccccccccccccccccULL;guest.stack[4]=0xfeed0001;
  std::memset(&state,0xa5,sizeof state);for(unsigned r=0;r<4;++r)std::memcpy(&state.vec[r].ymm,guest.vectors[r],32);state.gpr.rdi.qword=uint64_t(guest.backing+3);state.gpr.rsp.qword=uint64_t(guest.stack+4);state.gpr.rip.qword=spec.pc;
  unsigned control=(0x1f80&~((setting&3)<<7))|(((setting>>2)&3)<<13)|((setting&16)?0x40:0)|((setting&32)?0x8000:0)|((trial+setting*7)&63);unsigned before=initial_flags((trial+setting)&63);set_flags(state,before);state.x87.fxsave.mxcsr.flat=control;expected=state;initial_memory=guest;
  _mm_setcsr(0x1f80);unsigned raised=0,result_flags=reference(x,y,spec.width,spec.unordered,control,raised),unmasked=raised&~(control>>7)&63;bool should_fault=unmasked!=0;unsigned final_flags=should_fault?before:result_flags;
  Snapshot in={},out={};std::memcpy(in.vectors,guest.vectors,128);in.flags=0x202|before;hardware_run(hardware[form],&in,&out,guest.backing+3,control);
  if(bool(fault.code)!=should_fault||fault.csr!=(control|raised)||(fault.flags&0x8d5)!=final_flags){std::fprintf(stderr,"HW got code=%lx csr=%x flags=%x expected=%u/%x/%x x=%llx y=%llx\n",fault.code,fault.csr,fault.flags,unsigned(should_fault),control|raised,final_flags,(unsigned long long)x,(unsigned long long)y);fail("hardware/reference",form,trial,setting);}
  if(fault.code){if(fault.pc!=uint64_t(hardware_sites[form]))fail("hardware fault PC",form,trial,setting);for(unsigned r=0;r<4;++r)if(std::memcmp(fault.xmm[r],in.vectors[r],16))fail("hardware fault XMM",form,trial,setting);++hardware_faults;}else if(std::memcmp(in.vectors,out.vectors,128))fail("hardware vectors",form,trial,setting);
  expected.x87.fxsave.mxcsr.flat=control|raised;set_flags(expected,final_flags);if(!should_fault){expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;}
  unsigned host=0x1f80|((trial&3)<<13)|((trial&4)?0x40:0)|((trial&8)?0x8000:0)|((setting*3)&63);_mm_setcsr(host);exit_kind=raised_out=unmasked_out=0;error_pc=0;returned=nullptr;invoke(lifted[form],spec.pc);unsigned host_after=_mm_getcsr();_mm_setcsr(0x1f80);
  bool bad[6]={bool(exit_kind)!=should_fault||(exit_kind==1&&(raised_out!=raised||unmasked_out!=unmasked))||exit_kind==2,flags(state)!=final_flags,state.x87.fxsave.mxcsr.flat!=(control|raised),host_after!=host,std::memcmp(&state,&expected,sizeof state)!=0,guest.bytes!=(spec.memory?spec.width:0)||guest.returns!=(should_fault?0U:1U)||guest.returned!=(should_fault?0ULL:0xfeed0001ULL)||(!should_fault&&returned!=&guest)||std::memcmp(guest.vectors,initial_memory.vectors,128)||std::memcmp(guest.backing,initial_memory.backing,sizeof guest.backing)||std::memcmp(guest.stack,initial_memory.stack,sizeof guest.stack)};
  bool any=false;for(unsigned k=0;k<6;++k)if(bad[k]){++differences[k];any=true;if(!printed[form][k]){printed[form][k]=true;std::printf("{\"counterexample\":%u,\"form\":%u,\"trial\":%u,\"setting\":%u,\"x\":\"%llx\",\"y\":\"%llx\",\"control\":%u,\"expected_flags\":%u,\"actual_flags\":%u,\"expected_csr\":%u,\"actual_csr\":%u,\"expected_fault\":%u,\"exit_kind\":%u,\"host_before\":%u,\"host_after\":%u,\"error_pc\":\"%llx\"}\n",k,form,trial,setting,(unsigned long long)x,(unsigned long long)y,control,final_flags,flags(state),control|raised,state.x87.fxsave.mxcsr.flat,unsigned(should_fault),exit_kind,host,host_after,(unsigned long long)error_pc);}}
  mismatches+=any;errors+=exit_kind==2;++cases;
 }
 _mm_setcsr(saved);std::printf("{\"status\":\"characterized\",\"cases\":%llu,\"mismatched_cases\":%llu,\"hardware_faults\":%llu,\"remill_error_calls\":%llu,\"fault_differences\":%llu,\"flag_differences\":%llu,\"mxcsr_differences\":%llu,\"host_mxcsr_changes\":%llu,\"full_state_differences\":%llu,\"memory_exit_differences\":%llu,\"game_execution\":false}\n",(unsigned long long)cases,(unsigned long long)mismatches,(unsigned long long)hardware_faults,(unsigned long long)errors,(unsigned long long)differences[0],(unsigned long long)differences[1],(unsigned long long)differences[2],(unsigned long long)differences[3],(unsigned long long)differences[4],(unsigned long long)differences[5]);
}
