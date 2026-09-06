// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <xmmintrin.h>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t stack[8];uint8_t bytes[32];unsigned offset=0,reads=0,writes=0,returns=0,policies=0,host_helpers=0;uint32_t mask=0xffff;bool available=true;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,void*,void*);
#include "x87-entries.h"
extern "C" void save_host(void*);extern "C" void restore_host(const void*);
static void fail(const char* why){std::fprintf(stderr,"MXCSR fixture infrastructure: %s\n",why);std::exit(2);}
static Memory guest;static State guest_state;static void* escape[5];static Memory* returned_memory;static unsigned native_fault;static uint32_t native_value,native_invalid;
static uint8_t* operand(Memory* m){return m->bytes+8+m->offset;}
extern "C" uint32_t __bb_native_mxcsr_mask(Memory* m,State* s){if(m!=&guest||s!=&guest_state)fail("profile identity");++m->policies;return m->mask;}
extern "C" [[noreturn]] void __bb_native_mxcsr_fault(Memory* m,State* s,uint32_t value,uint32_t invalid){if(m!=&guest||s!=&guest_state||!invalid)fail("fault identity");native_fault=1;native_value=value;native_invalid=invalid;__builtin_longjmp(escape,1);}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");if(__builtin_setjmp(escape)==0)returned_memory=fn(&guest_state,pc,&guest);}
static uint64_t map_fault_pc(uint64_t host_pc){for(unsigned i=0;i<sizeof(host_ips)/sizeof(host_ips[0]);++i)if(host_ips[i]==host_pc)return guest_ips[i];fail("unknown hardware fault instruction");return 0;}
struct HardwareFault {DWORD code;uint64_t pc,flags;alignas(16) uint8_t fp[512];};static HardwareFault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.pc=map_fault_pc(info->ContextRecord->Rip);fault.flags=info->ContextRecord->EFlags;std::memcpy(fault.fp,&info->ContextRecord->FltSave,512);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const void* in,void* out,void* saved,void* data,const void* original){fault={};__try{fn(in,out,saved,data);}__except(capture(GetExceptionInformation())){}restore_host(original);if(fault.code){if(fault.code!=EXCEPTION_ACCESS_VIOLATION)fail("unexpected hardware exception");std::memcpy(out,fault.fp,512);std::memcpy(static_cast<uint8_t*>(out)+544,&fault.flags,8);}}
static void address(Memory* m,uint64_t at){if(m!=&guest||at!=uint64_t(operand(m)))fail("memory address");if(!m->available){native_fault=2;__builtin_longjmp(escape,1);}}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t at){++m->reads;address(m,at);uint32_t v;std::memcpy(&v,reinterpret_cast<void*>(at),4);return v;}
extern "C" Memory* __remill_write_memory_32(Memory* m,uint64_t at,uint32_t v){++m->writes;address(m,at);std::memcpy(reinterpret_cast<void*>(at),&v,4);return m;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("stack read");return m->stack[4];}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){if(pc!=0xfeed0001)fail("return");s->gpr.rip.qword=pc;++m->returns;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error");return nullptr;}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");return nullptr;}
// Only the retained original-semantics characterization calls these services.
extern "C" int32_t __remill_fpu_get_rounding(){++guest.host_helpers;uint16_t cw;asm volatile("fnstcw %0":"=m"(cw));return (cw>>10)&3;}
extern "C" void __remill_fpu_set_rounding(int32_t mode){++guest.host_helpers;uint16_t cw;asm volatile("fnstcw %0":"=m"(cw));cw=(cw&~0xc00)|(mode<<10);asm volatile("fldcw %0"::"m"(cw));unsigned csr=_mm_getcsr();_mm_setcsr((csr&~0x6000)|(mode<<13));}
extern "C" uint8_t __remill_undefined_8(){return 0;}
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint32_t get32(const void* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}
static void status(State& s,uint16_t v){s.x87.fxsave.swd.flat=v;s.sw.ie=v&1;s.sw.de=(v>>1)&1;s.sw.ze=(v>>2)&1;s.sw.oe=(v>>3)&1;s.sw.ue=(v>>4)&1;s.sw.pe=(v>>5)&1;s.sw.sf=(v>>6)&1;s.sw.c0=(v>>8)&1;s.sw.c1=(v>>9)&1;s.sw.c2=(v>>10)&1;s.sw.c3=(v>>14)&1;}
static unsigned flags(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
static const char* labels[]={"hardware-import","memory","full-state","host-fp-state","flags","fault-class","fault-pc","fault-values","service-order","host-helper-call"};
static uint64_t counts[6]{},bad[6]{},findings[6][10]{},hardware_faults[6]{},native_faults[6]{},policy_cases[6]{},unsupported_cases[6]{};
static void run_case(unsigned form,uint32_t value,unsigned seed,uint32_t mask,const uint8_t* original,bool unavailable=false){
 Memory& m=guest;m={};m.offset=seed%8;m.mask=mask;m.available=!unavailable;m.stack[4]=0xfeed0001;for(unsigned i=0;i<32;++i)m.bytes[i]=uint8_t(0xa5+i*13+seed);put32(operand(&m),value);
 State& s=guest_state;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=uint64_t(operand(&m));s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];s.x87.fxsave.cwd.flat=uint16_t(0x37f-((seed>>3)&1));status(s,uint16_t(((seed%8)<<11)|((seed&8)?0x8081:0)));s.x87.fxsave.ftw.flat=255;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x123;s.x87.fxsave.mxcsr.flat=(value^0xa581)&mask;s.x87.fxsave.mxcsr_mask.flat=0xdeadbeef;
 s.aflag.cf=s.aflag.af=s.aflag.sf=seed&1;s.aflag.pf=s.aflag.zf=s.aflag.of=(seed>>1)&1;s.rflag.flat=0x202|flags(s);
 alignas(16) uint8_t input[528]{},observed[1072]{},saved[512],before[512],after[512];uint8_t hw_bytes[32],prior[32];
 std::memcpy(input,&s.x87,32);input[5]=0;put32(input+28,0);uint64_t initial_flags=s.rflag.flat;std::memcpy(input+512,&initial_flags,8);
 for(unsigned st=0;st<8;++st){uint64_t bits=0x8000000000000000ULL+st*131;uint16_t exp=uint16_t(0x3fff+st);std::memcpy(&s.st.elems[st].val,&bits,8);std::memcpy(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,&exp,2);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
 for(unsigned reg=0;reg<16;++reg){for(unsigned i=0;i<16;++i)input[160+reg*16+i]=uint8_t(reg*16+i+seed);std::memcpy(&s.vec[reg].xmm,input+160+reg*16,16);}
 State expected=s;std::memcpy(hw_bytes,m.bytes,32);std::memcpy(prior,m.bytes,32);bool load_first=form==0||form==2||form==4,store_first=form==1||form==3||form==5;
 uint32_t requested=load_first?value:s.x87.fxsave.mxcsr.flat;bool invalid=load_first&&(requested&~mask);bool policy_only=invalid&&!(requested&~0xffffu);bool hardware_used=!policy_only&&!unavailable;
 bool import_difference=false;if(hardware_used){hardware_run(hardware[form],input,observed,saved,hw_bytes+8+m.offset,original);import_difference=get16(input)!=get16(observed+560)||get16(input+2)!=get16(observed+562)||input[4]!=observed[564]||get32(input+24)!=get32(observed+584)||std::memcmp(input+32,observed+592,384)!=0;}else fault={};
 restore_host(original);save_host(before);native_fault=0;native_value=native_invalid=0;returned_memory=nullptr;invoke(lifted[form],pcs[form]);save_host(after);restore_host(original);
 unsigned expected_fault=unavailable?2:invalid?1:0;if(hardware_used&&bool(fault.code)!=invalid)fail("hardware reserved-bit contract mismatch");
 if(hardware_used)expected.x87.fxsave.mxcsr.flat=get32(observed+24);
 else if(!expected_fault&&load_first)expected.x87.fxsave.mxcsr.flat=requested;
 if(expected_fault)expected.gpr.rip.qword=hardware_used?fault.pc:pcs[form];else{expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;}
 unsigned reads=load_first?1:form==5&&!unavailable?1:0,writes=store_first?1:form==4&&!expected_fault?1:0,policies=(load_first||form==5)&&!unavailable?1:0;
 bool differences[]={import_difference,std::memcmp(m.bytes,hardware_used?hw_bytes:prior,32)!=0,std::memcmp(&s,&expected,sizeof s)!=0,std::memcmp(before,after,28)!=0||std::memcmp(before+32,after+32,128)!=0,hardware_used&&flags(s)!=(get16(observed+544)&0x8d5),native_fault!=expected_fault,s.gpr.rip.qword!=expected.gpr.rip.qword,expected_fault==1&&(native_value!=requested||native_invalid!=(requested&~mask)),m.reads!=reads||m.writes!=writes||m.policies!=policies||m.returns!=unsigned(!expected_fault)||(!expected_fault&&returned_memory!=&m),m.host_helpers!=0};
 bool any=false;for(unsigned i=0;i<10;++i){findings[form][i]+=differences[i];any|=differences[i];}++counts[form];bad[form]+=any;hardware_faults[form]+=bool(fault.code);native_faults[form]+=native_fault==1;policy_cases[form]+=policy_only&&!unavailable;unsupported_cases[form]+=unavailable;
 if(any&&bad[form]<=4){std::fprintf(stderr,"form=%u value=%x seed=%u mask=%x unavailable=%u fault=%u/%u csr=%x/%x counts=%u,%u,%u expected=%u,%u,%u findings:",form,value,seed,mask,unsigned(unavailable),native_fault,expected_fault,s.x87.fxsave.mxcsr.flat,expected.x87.fxsave.mxcsr.flat,m.reads,m.writes,m.policies,reads,writes,policies);for(unsigned i=0;i<10;++i)if(differences[i])std::fprintf(stderr," %s",labels[i]);std::fprintf(stderr,"\n");}
}
int main(){alignas(16) uint8_t original[512];save_host(original);
 for(unsigned form=0;form<form_count;++form){
  for(unsigned value=0;value<65536;++value)run_case(form,value,value,0xffff,original);
  for(unsigned bit=16;bit<32;++bit)for(unsigned setting=0;setting<256;++setting)run_case(form,(1u<<bit)|(setting*257),setting,0xffff,original);
  for(unsigned setting=0;setting<256;++setting)run_case(form,0xffff0000|(setting*257),setting,0xffff,original);
  for(unsigned value=0;value<65536;++value)run_case(form,value,value,0xffbf,original);
  for(unsigned i=0;i<16;++i)run_case(form,i&1?0xffff0000:0x1f80,i,0xffff,original,true);
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"hardware_faults\":%llu,\"native_faults\":%llu,\"policy_cases\":%llu,\"unsupported_cases\":%llu,\"differences\":{",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)hardware_faults[form],(unsigned long long)native_faults[form],(unsigned long long)policy_cases[form],(unsigned long long)unsupported_cases[form]);for(unsigned i=0;i<10;++i)std::printf("%s\"%s\":%llu",i?",":"",labels[i],(unsigned long long)findings[form][i]);std::printf("}}\n");std::fflush(stdout);
 }restore_host(original);return 0;}
