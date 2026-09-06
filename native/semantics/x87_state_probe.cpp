// SPDX-License-Identifier: GPL-2.0-or-later
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
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory*,State*,uint32_t){fail("unexpected pending x87 fault in masked fixture");}
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
int main(){
 alignas(16) uint8_t original[512];save_host(original);
 unsigned precisions[]={0,2,3};
 for(unsigned form=0;form<10;++form)for(unsigned top=0;top<8;++top)for(unsigned occupancy=0;occupancy<4;++occupancy)for(unsigned setting=0;setting<12;++setting)for(unsigned flags=0;flags<3;++flags){
  Memory m{};m.stack[4]=0xfeed0001;m.word=uint16_t(0x7f|(precisions[setting%3]<<8)|((setting/3)<<10));uint16_t hw_word=m.word;
  State s;std::memset(&s,0,sizeof s);s.gpr.rdi.qword=uint64_t(&m.word);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];
  s.x87.fxsave.cwd.flat=uint16_t(0x7f|(precisions[(setting+1)%3]<<8)|(((setting/3+1)%4)<<10));
  s.x87.fxsave.swd.flat=uint16_t((top<<11)|(flags==1?0x21:flags==2?0x4500:0));s.sw.ie=flags==1;s.sw.pe=flags==1;s.sw.c0=s.sw.c2=s.sw.c3=flags==2;
  s.x87.fxsave.ftw.flat=occupancy==0?0:occupancy==1?255:occupancy==2?0x55:uint8_t(~(1<<((top+7)%8)));
  s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xffff;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x123;
  alignas(16) uint8_t input[512]{},observed[544]{},saved[512],before[512],after[512];std::memcpy(input,&s.x87,512);
  for(unsigned st=0;st<8;++st){uint64_t mantissa=st%3==0?0:0x8000000000000000ULL+(uint64_t(st)<<59);uint16_t exponent=st%3==0?0:0x3fff;std::memcpy(&s.st.elems[st].val,&mantissa,8);std::memcpy(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,&exponent,2);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
  hardware[form](input,observed,saved,&hw_word);
  restore_host(original);save_host(before);Memory* result=lifted[form](&s,pcs[form],&m);save_host(after);restore_host(original);
  if(result!=&m||m.returns!=1||s.gpr.rsp.qword!=uint64_t(m.stack+5)||m.reads!=(form==5)||m.writes!=(form==6||form==9))fail("memory/return contract");
  unsigned tags=s.x87.fxsave.ftw.flat,hw_tags=observed[4],sw=merged(s),hw_sw=get16(observed+2),cw=s.x87.fxsave.cwd.flat,hw_cw=get16(observed);bool payload=false;
  for(unsigned st=0;st<8;++st)if(hw_tags&(1<<(((hw_sw>>11)+st)%8)))payload|=std::memcmp(&s.st.elems[st].val,observed+32+st*16,10)!=0;
  const char* findings[10];unsigned count=0;
  if(tags!=hw_tags)findings[count++]="tags";if(cw!=hw_cw)findings[count++]="control";
  unsigned mask=form==4?0xffff:form==5||form==6?0xb8ff:0xbaff;if((sw&mask)!=(hw_sw&mask))findings[count++]="defined-status";
  if(payload)findings[count++]="register-payload";if(m.word!=hw_word)findings[count++]="memory-word";
  if(s.x87.fxsave.mxcsr.flat!=get32(observed+24))findings[count++]="guest-mxcsr";
  if(get16(before)!=get16(after)||get32(before+24)!=get32(after+24))findings[count++]="host-fp-control";
  std::printf("{\"form\":%u,\"top\":%u,\"occupancy\":%u,\"setting\":%u,\"flags\":%u,\"tags\":%u,\"hardware_tags\":%u,\"control\":%u,\"hardware_control\":%u,\"status\":%u,\"cached_status\":%u,\"hardware_status\":%u,\"word\":%u,\"hardware_word\":%u,\"differences\":[",form,top,occupancy,setting,flags,tags,hw_tags,cw,hw_cw,sw,s.x87.fxsave.swd.flat,hw_sw,m.word,hw_word);
  for(unsigned i=0;i<count;++i)std::printf("%s\"%s\"",i?",":"",findings[i]);std::printf("]}\n");
 }
 restore_host(original);return 0;
}
