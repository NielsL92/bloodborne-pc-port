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
struct Memory {uint64_t stack[8];uint16_t word;unsigned reads=0,writes=0,returns=0;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,void*,void*);
#include "x87-entries.h"
extern "C" void save_host(void*);extern "C" void restore_host(const void*);
static void fail(const char* why){std::fprintf(stderr,"probe infrastructure: %s\n",why);std::exit(2);}
static Memory guest;static State guest_state;static void* escape[5];static Memory* returned_memory;static bool native_fault;static unsigned native_pending;
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory* m,State* s,uint32_t pending){if(m!=&guest||s!=&guest_state||!pending)fail("fault callback");native_fault=true;native_pending=pending;__builtin_longjmp(escape,1);}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");if(__builtin_setjmp(escape)==0)returned_memory=fn(&guest_state,pc,&guest);}
static uint64_t map_fault_pc(uint64_t host_pc){for(unsigned i=0;i<sizeof(host_ips)/sizeof(host_ips[0]);++i)if(host_ips[i]==host_pc)return guest_ips[i];fail("unknown hardware fault instruction");return 0;}
struct HardwareFault {DWORD code;uint64_t pc;uint64_t flags;uint64_t ax;alignas(16) uint8_t fp[512];};static HardwareFault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.pc=map_fault_pc(info->ContextRecord->Rip);fault.flags=info->ContextRecord->EFlags;fault.ax=info->ContextRecord->Rax;std::memcpy(fault.fp,&info->ContextRecord->FltSave,512);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const void* in,void* out,void* saved,void* word,const void* original){fault={};__try{fn(in,out,saved,word);}__except(capture(GetExceptionInformation())){}restore_host(original);if(fault.code){if(fault.code<EXCEPTION_FLT_DENORMAL_OPERAND||fault.code>EXCEPTION_FLT_UNDERFLOW)fail("unexpected SEH exception");std::memcpy(out,fault.fp,512);std::memcpy(static_cast<uint8_t*>(out)+544,&fault.flags,8);std::memcpy(static_cast<uint8_t*>(out)+552,&fault.ax,8);}}

// These regressions retain their original payload/status scope; the separate
// metadata fixture checks both explicit profiles and segment service ordering.
extern "C" uint64_t __bb_native_x87_image_policy(Memory*,State*){return 0;}
extern "C" void __bb_native_x87_record_instruction(Memory*,State* s,uint64_t pc,uint32_t flags,uint64_t address){if(s->x87.fxsave.ip!=pc||flags||address)fail("register metadata service");}
extern "C" void __bb_native_x87_set_pointer_segments(Memory*,State*,uint32_t value){if(value)fail("initialization segment reset");}
extern "C" uint16_t __remill_read_memory_16(Memory* m,uint64_t at){if(at!=uint64_t(&m->word))fail("read16");++m->reads;return m->word;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("read64");return m->stack[4];}
extern "C" Memory* __remill_write_memory_16(Memory* m,uint64_t at,uint16_t v){if(at!=uint64_t(&m->word))fail("write16");m->word=v;++m->writes;return m;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){if(pc!=0xfeed0001)fail("return");s->gpr.rip.qword=pc;++m->returns;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error");return nullptr;}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");return nullptr;}
extern "C" int32_t __remill_fpu_get_rounding(){uint16_t cw;asm volatile("fnstcw %0":"=m"(cw));return (cw>>10)&3;}
extern "C" void __remill_fpu_set_rounding(int32_t mode){uint16_t cw;asm volatile("fnstcw %0":"=m"(cw));cw=(cw&~0xc00)|(mode<<10);asm volatile("fldcw %0"::"m"(cw));unsigned csr=_mm_getcsr();_mm_setcsr((csr&~0x6000)|(mode<<13));}
extern "C" void __remill_fpu_exception_clear(int32_t){asm volatile("fnclex");_mm_setcsr(_mm_getcsr()&~63u);}
extern "C" int32_t __remill_fpu_exception_test(int32_t mask){uint16_t sw;asm volatile("fnstsw %0":"=am"(sw));return sw&mask;}
extern "C" uint8_t __remill_undefined_8(){return 0;}
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint32_t get32(const void* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static uint16_t merged(const State& s){uint16_t sw=s.x87.fxsave.swd.flat;sw&=~uint16_t(0x477f);sw|=(s.sw.ie&1)|((s.sw.de&1)<<1)|((s.sw.ze&1)<<2)|((s.sw.oe&1)<<3)|((s.sw.ue&1)<<4)|((s.sw.pe&1)<<5)|((s.sw.sf&1)<<6)|((s.sw.c0&1)<<8)|((s.sw.c1&1)<<9)|((s.sw.c2&1)<<10)|((s.sw.c3&1)<<14);return sw;}
static const uint64_t significands[]={0,0,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0xc000000000000123ULL,0xc000000000000123ULL,0x8000000000000123ULL,1,0x7fffffffffffffffULL,0x8000000000000000ULL,0x1234,0,0xffffffffffffffffULL};
static const uint16_t exponents[]={0,0x8000,0x3fff,0xbfff,0x4000,0x7fff,0xffff,0x7fff,0xffff,0x7fff,0,0,0,0x3fff,0x7fff,0x7ffe};
static unsigned flag_word(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
static void set_flags(State& s,unsigned v){s.aflag.cf=v&1;s.aflag.pf=(v>>2)&1;s.aflag.af=(v>>4)&1;s.aflag.zf=(v>>6)&1;s.aflag.sf=(v>>7)&1;s.aflag.of=(v>>11)&1;}
static uint64_t counts[26],bad[26],findings[26][15],hardware_faults[26],native_faults[26];
static const char* labels[]={"tags","control","defined-status","register-payload","memory-word","guest-mxcsr","host-fp-state","arithmetic-flags","status-ax","unaffected-state","split-status","fault-presence","fault-pc","pending-mask","memory-access-counts"};
static void run_case(unsigned form,unsigned top,unsigned tags,unsigned setting,unsigned flags,unsigned first,unsigned second,unsigned mask_mode,unsigned pending_mode,const uint8_t* original,unsigned raw_status=0xffff){
 const unsigned precisions[]={0,2,3};
 unsigned base=base_forms[form];guest={};Memory& m=guest;m.stack[4]=0xfeed0001;m.word=uint16_t(0x7f|(precisions[setting%3]<<8)|((setting/3)<<10));uint16_t hw_word=m.word;
 State& s=guest_state;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=uint64_t(&m.word);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];
 s.x87.fxsave.cwd.flat=uint16_t(0x7f|(precisions[(setting+1)%3]<<8)|(((setting/3+1)%4)<<10));
 s.x87.fxsave.swd.flat=uint16_t((top<<11)|(flags==1?0x21:flags==2?0x4500:0));
 s.sw.ie=flags==1;s.sw.pe=flags==1;s.sw.de=s.sw.ze=s.sw.oe=s.sw.ue=s.sw.sf=s.sw.c1=0;s.sw.c0=s.sw.c2=s.sw.c3=flags==2;
 s.x87.fxsave.cwd.flat&=uint16_t(~mask_mode);
 const unsigned statuses[]={0,1,2,3,0x41,0x42,0x43,0x40};unsigned preset=raw_status==0xffff?statuses[pending_mode]:raw_status;if(preset&~s.x87.fxsave.cwd.flat&63)preset|=0x8080;s.x87.fxsave.swd.flat=uint16_t((top<<11)|preset);s.sw.ie=preset&1;s.sw.de=(preset>>1)&1;s.sw.ze=(preset>>2)&1;s.sw.oe=(preset>>3)&1;s.sw.ue=(preset>>4)&1;s.sw.pe=(preset>>5)&1;s.sw.sf=(preset>>6)&1;s.sw.c0=s.sw.c2=s.sw.c3=0;
 // FLDCW imports the complementary exception mask, exposing newly pending flags.
 if(base==5)m.word=uint16_t((m.word&~63u)|(mask_mode&63));hw_word=m.word;
 s.x87.fxsave.ftw.flat=uint8_t(tags);s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xffff;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x123;
 set_flags(s,flags==1?0x8d5:flags==2?0x891:0);s.rflag.flat=0x202|flag_word(s);
 alignas(16) uint8_t input[528]{},observed[1072]{},saved[512],before[512],after[512];
 std::memcpy(input,&s.x87,32);uint64_t initial_flags=0x202|flag_word(s);std::memcpy(input+512,&initial_flags,8);
 for(unsigned st=0;st<8;++st){unsigned type=st==0?first:st==1||st==7?second:(first+st)%16;std::memcpy(&s.st.elems[st].val,&significands[type],8);std::memcpy(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,&exponents[type],2);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
 State expected=s;
 hardware_run(hardware[form],input,observed,saved,&hw_word,original);
 if(get16(input)!=get16(observed+560)||get16(input+2)!=get16(observed+562)||input[4]!=observed[564])fail("initial hardware control/status/tag import mismatch");
 for(unsigned st=0;st<8;++st)if(tags&(1<<((top+st)%8)))if(std::memcmp(input+32+st*16,observed+592+st*16,10))fail("initial hardware payload import mismatch");
 restore_host(original);save_host(before);native_fault=false;native_pending=0;returned_memory=nullptr;invoke(lifted[form],pcs[form]);Memory* result=returned_memory;save_host(after);restore_host(original);
 if(native_fault?(m.returns!=0||s.gpr.rsp.qword!=uint64_t(m.stack+4)):(result!=&m||m.returns!=1||s.gpr.rsp.qword!=uint64_t(m.stack+5)))fail("memory/return contract");
 unsigned hw_tags=observed[4],sw=merged(s),hw_sw=get16(observed+2),cw=s.x87.fxsave.cwd.flat,hw_cw=get16(observed);bool payload=false;
 for(unsigned st=0;st<8;++st)if(hw_tags&(1<<(((hw_sw>>11)+st)%8)))payload|=std::memcmp(&s.st.elems[st].val,observed+32+st*16,10)!=0;
 unsigned mask=base==4?0xffff:base==5||base==6||base==9||base==17||base==18?0xffff:0xbaff;
 bool compare=base==8||base==14||base==15||base==16;
 if(!native_fault)expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=native_fault?s.gpr.rip.qword:0xfeed0001;if(base==17)expected.gpr.rax.word=get16(observed+552);if(compare)set_flags(expected,get16(observed+544));
 expected.x87.fxsave.cwd.flat=cw;expected.x87.fxsave.swd.flat=s.x87.fxsave.swd.flat;expected.x87.fxsave.ftw.flat=s.x87.fxsave.ftw.flat;
 expected.x87.fxsave.ip=s.x87.fxsave.ip;expected.x87.fxsave.dp=s.x87.fxsave.dp;expected.x87.fxsave.fop=s.x87.fxsave.fop;
 expected.sw.ie=s.sw.ie;expected.sw.de=s.sw.de;expected.sw.ze=s.sw.ze;expected.sw.oe=s.sw.oe;expected.sw.ue=s.sw.ue;expected.sw.pe=s.sw.pe;expected.sw.sf=s.sw.sf;expected.sw.c0=s.sw.c0;expected.sw.c1=s.sw.c1;expected.sw.c2=s.sw.c2;expected.sw.c3=s.sw.c3;
 for(unsigned st=0;st<8;++st)std::memcpy(&expected.st.elems[st].val,&s.st.elems[st].val,10);
 bool differences[]={s.x87.fxsave.ftw.flat!=hw_tags,cw!=hw_cw,(sw&mask)!=(hw_sw&mask),payload,m.word!=hw_word,s.x87.fxsave.mxcsr.flat!=get32(observed+24),std::memcmp(before,after,24)!=0||std::memcmp(before+24,after+24,4)!=0||std::memcmp(before+32,after+32,128)!=0,flag_word(s)!=flag_word(expected),base==17&&s.gpr.rax.word!=get16(observed+552),std::memcmp(&expected,&s,sizeof s)!=0,s.x87.fxsave.swd.flat!=merged(s),native_fault!=bool(fault.code),native_fault&&fault.code&&s.gpr.rip.qword!=fault.pc,native_fault&&fault.code&&native_pending!=(hw_sw&~hw_cw&63),m.reads!=(base==5&&(!fault.code||fault.pc!=pcs[form]))||m.writes!=(base==6||base==9)};
 bool any=false;for(unsigned i=0;i<15;++i){findings[form][i]+=differences[i];any|=differences[i];}++counts[form];bad[form]+=any;hardware_faults[form]+=bool(fault.code);native_faults[form]+=native_fault;
 if(any&&bad[form]<=6){std::fprintf(stderr,"form=%u top=%u tags=%u setting=%u flags=%u a=%u b=%u mode=%u pending=%u fault=%u hwfault=%x pc=%llx hwpc=%llx sw=%x hw=%x cw=%x hw=%x tag=%x hw=%x flags=%x hw=%x findings:",form,top,tags,setting,flags,first,second,mask_mode,pending_mode,unsigned(native_fault),unsigned(fault.code),(unsigned long long)s.gpr.rip.qword,(unsigned long long)(fault.pc),sw,hw_sw,cw,hw_cw,s.x87.fxsave.ftw.flat,hw_tags,flag_word(s),get16(observed+544)&0x8d5);for(unsigned i=0;i<15;++i)if(differences[i])std::fprintf(stderr," %s",labels[i]);std::fprintf(stderr,"\n");}
}
int main(){
 alignas(16) uint8_t original[512];save_host(original);const unsigned payloads[]={2,7,9,10,12,13};
 for(unsigned form=0;form<form_count;++form){
  for(unsigned top=0;top<8;++top)for(unsigned occupancy=0;occupancy<4;++occupancy)for(unsigned mode=0;mode<4;++mode)for(unsigned pending=0;pending<8;++pending)for(unsigned value=0;value<6;++value)for(unsigned flags=0;flags<3;++flags){unsigned tags=occupancy==0?0:occupancy==1?255:1<<((top+occupancy-2)%8);run_case(form,top,tags,(mode*3+value)%12,flags,payloads[value],payloads[(value+1)%6],mode,pending,original);}
  if(form==8||form==14||form==23||form==24)for(unsigned a=0;a<16;++a)for(unsigned b=0;b<16;++b)for(unsigned mode=0;mode<4;++mode)for(unsigned flags=0;flags<3;++flags)run_case(form,0,255,3,flags,a,b,mode,0,original);
  if(form==4||form==5||form==6||form==9||form==17||form==18||form==25)for(unsigned mask=0;mask<64;++mask)for(unsigned sticky=0;sticky<64;++sticky)for(unsigned top=0;top<8;++top)run_case(form,top,255,(mask+sticky)%12,sticky%3,2,2,mask,0,original,sticky);
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"hardware_faults\":%llu,\"native_faults\":%llu,\"differences\":{",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)hardware_faults[form],(unsigned long long)native_faults[form]);for(unsigned i=0;i<15;++i)std::printf("%s\"%s\":%llu",i?",":"",labels[i],(unsigned long long)findings[form][i]);std::printf("}}\n");std::fflush(stdout);
 }
 restore_host(original);return 0;
}
