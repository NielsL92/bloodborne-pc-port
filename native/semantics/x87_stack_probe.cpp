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
static const uint64_t significands[]={0,0,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0x8000000000000000ULL,0xc000000000000123ULL,0xc000000000000123ULL,0x8000000000000123ULL,1,0x7fffffffffffffffULL,0x8000000000000000ULL,0x1234,0,0xffffffffffffffffULL};
static const uint16_t exponents[]={0,0x8000,0x3fff,0xbfff,0x4000,0x7fff,0xffff,0x7fff,0xffff,0x7fff,0,0,0,0x3fff,0x7fff,0x7ffe};
static unsigned flag_word(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
static void set_flags(State& s,unsigned v){s.aflag.cf=v&1;s.aflag.pf=(v>>2)&1;s.aflag.af=(v>>4)&1;s.aflag.zf=(v>>6)&1;s.aflag.sf=(v>>7)&1;s.aflag.of=(v>>11)&1;}
static uint64_t counts[19],bad[19],findings[19][11];
static const char* labels[]={"tags","control","defined-status","register-payload","memory-word","guest-mxcsr","host-fp-state","arithmetic-flags","status-ax","unaffected-state","split-status"};
static void run_case(unsigned form,unsigned top,unsigned tags,unsigned setting,unsigned flags,unsigned first,unsigned second,const uint8_t* original){
 const unsigned precisions[]={0,2,3};
 Memory m{};m.stack[4]=0xfeed0001;m.word=uint16_t(0x7f|(precisions[setting%3]<<8)|((setting/3)<<10));uint16_t hw_word=m.word;
 State s;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=uint64_t(&m.word);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];
 s.x87.fxsave.cwd.flat=uint16_t(0x7f|(precisions[(setting+1)%3]<<8)|(((setting/3+1)%4)<<10));
 s.x87.fxsave.swd.flat=uint16_t((top<<11)|(flags==1?0x21:flags==2?0x4500:0));
 s.sw.ie=flags==1;s.sw.pe=flags==1;s.sw.de=s.sw.ze=s.sw.oe=s.sw.ue=s.sw.sf=s.sw.c1=0;s.sw.c0=s.sw.c2=s.sw.c3=flags==2;
 s.x87.fxsave.ftw.flat=uint8_t(tags);s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xffff;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x123;
 set_flags(s,flags==1?0x8d5:flags==2?0x891:0);s.rflag.flat=0x202|flag_word(s);
 alignas(16) uint8_t input[528]{},observed[560]{},saved[512],before[512],after[512];
 std::memcpy(input,&s.x87,32);uint64_t initial_flags=0x202|flag_word(s);std::memcpy(input+512,&initial_flags,8);
 for(unsigned st=0;st<8;++st){unsigned type=st==0?first:st==1||st==7?second:(first+st)%16;std::memcpy(&s.st.elems[st].val,&significands[type],8);std::memcpy(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,&exponents[type],2);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
 State expected=s;
 hardware[form](input,observed,saved,&hw_word);
 restore_host(original);save_host(before);Memory* result=lifted[form](&s,pcs[form],&m);save_host(after);restore_host(original);
 if(result!=&m||m.returns!=1||s.gpr.rsp.qword!=uint64_t(m.stack+5)||m.reads!=(form==5)||m.writes!=(form==6||form==9))fail("memory/return contract");
 unsigned hw_tags=observed[4],sw=merged(s),hw_sw=get16(observed+2),cw=s.x87.fxsave.cwd.flat,hw_cw=get16(observed);bool payload=false;
 for(unsigned st=0;st<8;++st)if(hw_tags&(1<<(((hw_sw>>11)+st)%8)))payload|=std::memcmp(&s.st.elems[st].val,observed+32+st*16,10)!=0;
 unsigned mask=form==4?0xffff:form==5||form==6||form==9||form==17||form==18?0xffff:0xbaff;
 bool compare=form==8||form==14||form==15||form==16;
 expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;if(form==17)expected.gpr.rax.word=get16(observed+552);if(compare)set_flags(expected,get16(observed+544));
 expected.x87.fxsave.cwd.flat=cw;expected.x87.fxsave.swd.flat=s.x87.fxsave.swd.flat;expected.x87.fxsave.ftw.flat=s.x87.fxsave.ftw.flat;
 expected.x87.fxsave.ip=s.x87.fxsave.ip;expected.x87.fxsave.dp=s.x87.fxsave.dp;expected.x87.fxsave.fop=s.x87.fxsave.fop;
 expected.sw.ie=s.sw.ie;expected.sw.de=s.sw.de;expected.sw.ze=s.sw.ze;expected.sw.oe=s.sw.oe;expected.sw.ue=s.sw.ue;expected.sw.pe=s.sw.pe;expected.sw.sf=s.sw.sf;expected.sw.c0=s.sw.c0;expected.sw.c1=s.sw.c1;expected.sw.c2=s.sw.c2;expected.sw.c3=s.sw.c3;
 for(unsigned st=0;st<8;++st)std::memcpy(&expected.st.elems[st].val,&s.st.elems[st].val,10);
 bool differences[]={s.x87.fxsave.ftw.flat!=hw_tags,cw!=hw_cw,(sw&mask)!=(hw_sw&mask),payload,m.word!=hw_word,s.x87.fxsave.mxcsr.flat!=get32(observed+24),std::memcmp(before,after,24)!=0||std::memcmp(before+24,after+24,4)!=0||std::memcmp(before+32,after+32,128)!=0,flag_word(s)!=flag_word(expected),form==17&&s.gpr.rax.word!=get16(observed+552),std::memcmp(&expected,&s,sizeof s)!=0,s.x87.fxsave.swd.flat!=merged(s)};
 bool any=false;for(unsigned i=0;i<11;++i){findings[form][i]+=differences[i];any|=differences[i];}++counts[form];bad[form]+=any;
 if(any&&bad[form]<=3){std::fprintf(stderr,"form=%u top=%u tags=%u setting=%u flags=%u a=%u b=%u sw=%x hw=%x cw=%x hw=%x tag=%x hw=%x flags=%x hw=%x findings:",form,top,tags,setting,flags,first,second,sw,hw_sw,cw,hw_cw,s.x87.fxsave.ftw.flat,hw_tags,flag_word(s),get16(observed+544)&0x8d5);for(unsigned i=0;i<11;++i)if(differences[i])std::fprintf(stderr," %s",labels[i]);std::fprintf(stderr,"\n");}
}
int main(){
 alignas(16) uint8_t original[512];save_host(original);
 for(unsigned form=0;form<19;++form){
  for(unsigned top=0;top<8;++top)for(unsigned tags=0;tags<256;++tags)for(unsigned setting=0;setting<12;++setting)for(unsigned flags=0;flags<3;++flags)run_case(form,top,tags,setting,flags,(tags+setting)%16,(tags/16+flags)%16,original);
  if(form==8||form==14||form==15||form==16)for(unsigned a=0;a<16;++a)for(unsigned b=0;b<16;++b)for(unsigned top=0;top<8;++top)for(unsigned setting=0;setting<12;++setting)run_case(form,top,255,setting,0,a,b,original);
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"differences\":{",form,(unsigned long long)counts[form],(unsigned long long)bad[form]);for(unsigned i=0;i<11;++i)std::printf("%s\"%s\":%llu",i?",":"",labels[i],(unsigned long long)findings[form][i]);std::printf("}}\n");std::fflush(stdout);
 }
 restore_host(original);return 0;
}
