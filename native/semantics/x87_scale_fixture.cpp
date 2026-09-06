// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <xmmintrin.h>
#include <intrin.h>
#include <initializer_list>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {uint64_t stack[8];uint8_t bytes[64];unsigned offset=0,reads=0,writes=0,returns=0,spans=0,records=0,policies=0;bool exception_only=false,available=true;uint32_t segments=0x00770066;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,void*,void*);
#include "x87-entries.h"
extern "C" void save_host(void*);extern "C" void restore_host(const void*);
static void fail(const char* why){std::fprintf(stderr,"image fixture infrastructure: %s\n",why);std::exit(2);}
static Memory guest;static State guest_state;static void* escape[5];static Memory* returned_memory;
// Pending x87 faults and unsupported fixture mappings are distinct.
static unsigned native_fault=0,native_pending=0;
static unsigned active_form;
static uint8_t* operand(Memory* m){return m->bytes+16+m->offset;}
static void identity(Memory* m,State* s){if(m!=&guest||s!=&guest_state)fail("runtime identity");}
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory* m,State* s,uint32_t pending){identity(m,s);if(!pending)fail("empty pending exception");native_fault=1;native_pending=pending;__builtin_longjmp(escape,1);}
extern "C" [[noreturn]] void __bb_native_x87_unsupported(Memory* m,State* s,uint32_t reason){identity(m,s);if(reason!=1||((s->x87.fxsave.cwd.flat>>8)&3)!=1)fail("unexpected numeric unsupported boundary");native_fault=2;__builtin_longjmp(escape,1);}
extern "C" void __bb_native_x87_check_span(Memory*,State*,uint64_t,uint32_t,uint32_t,uint32_t){fail("unexpected register arithmetic memory span");}
extern "C" uint64_t __bb_native_x87_image_policy(Memory* m,State* s){identity(m,s);++m->policies;return m->exception_only?12:0;}
extern "C" void __bb_native_x87_record_instruction(Memory* m,State* s,uint64_t pc,uint32_t memory,uint64_t at){
 identity(m,s);bool found=false;for(unsigned j=0;j<instruction_counts[active_form];++j)if(step_pcs[active_form][j]==pc){found=true;bool mem=step_kinds[active_form][j]==1||step_kinds[active_form][j]==2;bool update=mem&&(!m->exception_only||(s->x87.fxsave.swd.flat&~s->x87.fxsave.cwd.flat&63));if(memory!=(unsigned(mem)|(unsigned(update)<<1))||at!=(mem?uint64_t(operand(m)):0)||s->x87.fxsave.ip!=pc||((!m->exception_only||(s->x87.fxsave.swd.flat&~s->x87.fxsave.cwd.flat&63))&&s->x87.fxsave.fop!=step_fops[active_form][j]))fail("record instruction metadata");}
 if(!found)fail("unknown record PC");++m->records;m->segments=(m->segments&0xffff0000)|s->seg.cs.flat;if(memory&2)m->segments=(m->segments&0xffff)|(uint32_t(s->seg.ds.flat)<<16);
}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");if(__builtin_setjmp(escape)==0)returned_memory=fn(&guest_state,pc,&guest);}
static uint64_t map_fault_pc(uint64_t host_pc){for(unsigned i=0;i<sizeof(host_ips)/sizeof(host_ips[0]);++i)if(host_ips[i]==host_pc)return guest_ips[i];fail("unknown hardware fault instruction");return 0;}
struct HardwareFault {DWORD code;uint64_t pc,flags;alignas(16) uint8_t fp[512];};static HardwareFault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.pc=map_fault_pc(info->ContextRecord->Rip);fault.flags=info->ContextRecord->EFlags;std::memcpy(fault.fp,&info->ContextRecord->FltSave,512);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const void* in,void* out,void* saved,void* data,const void* original){fault={};__try{fn(in,out,saved,data);}__except(capture(GetExceptionInformation())){}restore_host(original);if(fault.code){if(fault.code!=EXCEPTION_ACCESS_VIOLATION&&(fault.code<EXCEPTION_FLT_DENORMAL_OPERAND||fault.code>EXCEPTION_FLT_UNDERFLOW))fail("unexpected SEH exception");std::memcpy(out,fault.fp,512);std::memcpy(static_cast<uint8_t*>(out)+544,&fault.flags,8);}}
static void address(Memory* m,uint64_t at,unsigned width){if(m!=&guest||at<uint64_t(operand(m))||at+width>uint64_t(operand(m))+10||!m->available)fail("memory access");}
extern "C" uint8_t __remill_read_memory_8(Memory* m,uint64_t at){address(m,at,1);++m->reads;return *reinterpret_cast<uint8_t*>(at);}
extern "C" uint16_t __remill_read_memory_16(Memory* m,uint64_t at){address(m,at,2);m->reads+=2;uint16_t v;std::memcpy(&v,reinterpret_cast<void*>(at),2);return v;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("stack read");return m->stack[4];}
extern "C" Memory* __remill_write_memory_8(Memory* m,uint64_t at,uint8_t v){address(m,at,1);++m->writes;*reinterpret_cast<uint8_t*>(at)=v;return m;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){identity(m,s);if(pc!=0xfeed0001)fail("return PC");s->gpr.rip.qword=pc;++m->returns;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error");return nullptr;}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");return nullptr;}
extern "C" uint8_t __remill_undefined_8(){return 0;}

static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint64_t get64(const void* p){uint64_t v;std::memcpy(&v,p,8);return v;}
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}
static void status(State& s,uint16_t v){s.x87.fxsave.swd.flat=v;s.sw.ie=v&1;s.sw.de=(v>>1)&1;s.sw.ze=(v>>2)&1;s.sw.oe=(v>>3)&1;s.sw.ue=(v>>4)&1;s.sw.pe=(v>>5)&1;s.sw.sf=(v>>6)&1;s.sw.c0=(v>>8)&1;s.sw.c1=(v>>9)&1;s.sw.c2=(v>>10)&1;s.sw.c3=(v>>14)&1;}
static unsigned flags(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
struct Value{uint64_t sig;uint16_t exp;};
static const Value values[]={{0,0},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x7fff},{0xc000000000000123ULL,0x7fff},{0x8000000000000123ULL,0x7fff},{1,0},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,0},{0x1234,0x3fff},{0,0x7fff},{0xffffffffffffffffULL,0x7ffe},{0x8000000000000001ULL,0x3fff},{0x8000000000000000ULL,0x3fe7},{0x8000000000000000ULL,0x3fca},{0x8000000000000000ULL,0x3fbf},{0x8000000000000000ULL,1},{0x8000000000000001ULL,1},{0xffffffffffffffffULL,1},{0x8000000000000000ULL,0x7ffe},{0xc000000000000000ULL,0x7ffe},{0x8000000000000000ULL,0x3ffe},{0xc000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x5fff},{0x8000000000000000ULL,0x1fff}};
static uint64_t random_bits(uint64_t x){x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);}
static Value source_value(unsigned type){constexpr unsigned count=sizeof(values)/sizeof(values[0]);if(type<count*2){auto v=values[type%count];if(type>=count)v.exp|=0x8000;return v;}auto bits=random_bits(type);return {random_bits(bits),uint16_t(bits)};}
static const char* labels[]={"hardware-import","memory","full-state","host-fp-state","flags","fault-class","fault-pc","pending-mask","memory-and-record-counts","pointer-metadata"};
static uint64_t counts[form_count]{},bad[form_count]{},findings[form_count][10]{},hardware_faults[form_count]{},native_faults[form_count]{},unsupported_cases[form_count]{},hardware_pointer_differences[form_count]{},hardware_opcode_differences[form_count]{};
static void run_case(unsigned form,unsigned top,unsigned tags,unsigned type,unsigned setting,unsigned mask,unsigned sticky,unsigned eflags,const uint8_t* original,bool reserved_control=false,bool exception_only=false,const Value* override_source=nullptr,const Value* override_second=nullptr){
 active_form=form;guest={};Memory& m=guest;m.available=true;m.exception_only=exception_only;m.offset=setting%8;m.stack[4]=0xfeed0001;for(unsigned i=0;i<64;++i)m.bytes[i]=uint8_t(0xa5+i*17+setting);uint8_t* data=operand(&m);
 State& s=guest_state;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=uint64_t(data);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];s.seg.cs.flat=0x43;s.seg.ds.flat=0x4b;
 s.x87.fxsave.cwd.flat=uint16_t(0x40|mask|((setting%4)<<10)|(((setting/4)%4)<<8));status(s,uint16_t((top<<11)|sticky|((sticky&~mask&63)?0x8080:0)|((setting&1)?0x4700:0)));s.x87.fxsave.ftw.flat=uint8_t(tags);s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xdeadbeef;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x612;
 s.aflag.cf=eflags&1;s.aflag.pf=(eflags>>1)&1;s.aflag.zf=(eflags>>2)&1;s.aflag.af=s.aflag.sf=s.aflag.of=(eflags>>2)&1;s.rflag.flat=0x202|flags(s);
 alignas(16) uint8_t input[528]{},observed[3120]{},saved[512],before[512],after[512],hw_bytes[64],prior[64];
 std::memcpy(input,&s.x87,32);input[5]=0;put32(input+28,0);uint64_t initial_flags=s.rflag.flat;std::memcpy(input+512,&initial_flags,8);
 for(unsigned st=0;st<8;++st){auto v=st==0&&override_source?*override_source:st==source_indices[form]&&override_second?*override_second:source_value(type+st);std::memcpy(&s.st.elems[st].val,&v.sig,8);put16(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,v.exp);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
 for(unsigned reg=0;reg<16;++reg){for(unsigned i=0;i<16;++i)input[160+reg*16+i]=uint8_t(reg*16+i+setting);std::memcpy(&s.vec[reg].xmm,input+160+reg*16,16);}
 State expected=s;std::memcpy(hw_bytes,m.bytes,64);std::memcpy(prior,m.bytes,64);bool import_difference=false;
 if(!reserved_control){hardware_run(hardware[form],input,observed,saved,hw_bytes+16+m.offset,original);if(fault.code==EXCEPTION_ACCESS_VIOLATION)fail("unexpected hardware access fault");import_difference=get16(input)!=get16(observed+560)||get16(input+2)!=get16(observed+562)||input[4]!=observed[564]||std::memcmp(input+32,observed+592,384)!=0;}else fault={};
 restore_host(original);save_host(before);native_fault=0;native_pending=0;returned_memory=nullptr;invoke(lifted[form],pcs[form]);save_host(after);restore_host(original);
 unsigned initial_pending=sticky&~mask&63,expected_fault=reserved_control?(initial_pending?1:2):fault.code?1:0;
 // Reserved precision controls terminate before arithmetic effects, after pending checks.
 unsigned reads=0,writes=0,spans=0,records=0,policies=0;uint32_t segments=0x00770066;uint64_t last_pc=expected.x87.fxsave.ip,last_dp=expected.x87.fxsave.dp;uint16_t last_fop=expected.x87.fxsave.fop;int last_step=-1;
 if(reserved_control){}
 else for(unsigned j=0;j<instruction_counts[form];++j){
  unsigned kind=unsigned(step_kinds[form][j]);if(fault.code&&step_pcs[form][j]>=fault.pc)break;if(!kind)continue;const uint8_t* prior_state=j?observed+1072+(j-1)*512:input;
  ++records;++policies;last_step=int(j);last_pc=step_pcs[form][j];const uint8_t* after_opcode=observed+1072+j*512;if(!exception_only||(get16(after_opcode+2)&~get16(after_opcode)&63))last_fop=uint16_t(step_fops[form][j]);segments=(segments&0xffff0000)|0x43;
  if(kind==1||kind==2){++spans;const uint8_t* after_state=observed+1072+j*512;bool update=!exception_only||(get16(after_state+2)&~get16(after_state)&63);if(update){last_dp=uint64_t(data);segments=0x004b0043;}if(!(get16(after_state+2)&~get16(after_state)&0x19))writes+=store_widths[form][j];}
 }
 if(!reserved_control){
  expected.x87.fxsave.cwd.flat=get16(observed);status(expected,uint16_t((get16(observed+2)&~0x4500)|(s.x87.fxsave.swd.flat&0x4500)));expected.x87.fxsave.ftw.flat=observed[4];
  for(unsigned st=0;st<8;++st)std::memcpy(&expected.st.elems[st].val,observed+32+st*16,10);
 }
 expected.x87.fxsave.ip=last_pc;expected.x87.fxsave.dp=last_dp;expected.x87.fxsave.fop=last_fop;
 expected.gpr.rip.qword=expected_fault?(reserved_control?pcs[form]:fault.pc):0xfeed0001;if(!expected_fault)expected.gpr.rsp.qword+=8;
 bool differences[]={import_difference,std::memcmp(m.bytes,reserved_control?prior:hw_bytes,64)!=0,std::memcmp(&s,&expected,sizeof s)!=0,std::memcmp(before,after,28)!=0||std::memcmp(before+32,after+32,128)!=0,!reserved_control&&flags(s)!=(get16(observed+544)&0x8d5),native_fault!=expected_fault,s.gpr.rip.qword!=expected.gpr.rip.qword,native_fault==1&&native_pending!=(reserved_control?initial_pending:get16(observed+2)&~get16(observed)&63),m.spans!=spans||m.reads!=reads||m.writes!=writes||m.records!=records||m.policies!=policies||m.returns!=unsigned(!expected_fault)||(!expected_fault&&returned_memory!=&m),m.segments!=segments};
 // Keep observed pointer behavior separate until its architecture profile is
 // established. Guest logical identifiers and metadata calls are still exact.
 if(!reserved_control&&last_step>=0){uint64_t host_ip=0;for(unsigned i=0;i<sizeof(guest_ips)/sizeof(guest_ips[0]);++i)if(guest_ips[i]==last_pc)host_ip=host_ips[i];bool dp_was_set=false;for(unsigned j=0;j<=unsigned(last_step);++j)if((step_kinds[form][j]==1||step_kinds[form][j]==2)&&(get16(observed+1072+j*512+2)&~get16(observed+1072+j*512)&63))dp_was_set=true;uint64_t host_dp=dp_was_set?uint64_t(hw_bytes+16+m.offset):0x87654321;bool pointer_difference=uint32_t(get64(observed+8))!=uint32_t(host_ip)||uint32_t(get64(observed+16))!=uint32_t(host_dp);hardware_pointer_differences[form]+=pointer_difference;differences[9]|=pointer_difference;if(pointer_difference&&hardware_pointer_differences[form]<=3)std::fprintf(stderr,"pointer form=%u tags=%x mask=%x sticky=%x status=%x ip=%llx expected-host=%llx dp=%llx expected-host=%llx fop=%x\n",form,tags,mask,sticky,get16(observed+2),(unsigned long long)get64(observed+8),(unsigned long long)host_ip,(unsigned long long)get64(observed+16),(unsigned long long)host_dp,get16(observed+6));}
 if(!reserved_control){uint16_t expected_opcode=0x612;for(unsigned j=0;j<instruction_counts[form];++j){if(fault.code&&step_pcs[form][j]>=fault.pc)break;if(!step_kinds[form][j])continue;const uint8_t* after_step=observed+1072+j*512;if(get16(after_step+2)&~get16(after_step)&63){uintptr_t ip=0;for(unsigned k=0;k<sizeof(guest_ips)/sizeof(guest_ips[0]);++k)if(guest_ips[k]==step_pcs[form][j])ip=host_ips[k];if(!ip)fail("opcode PC mapping");auto bytes=reinterpret_cast<const uint8_t*>(ip);if((*bytes&0xf0)==0x40)++bytes;expected_opcode=uint16_t((bytes[0]&7)*256+bytes[1]);}}bool opcode_difference=get16(observed+6)!=expected_opcode;hardware_opcode_differences[form]+=opcode_difference;differences[9]|=opcode_difference;}
 if(counts[form]==0)std::fprintf(stderr,"first-opcode form=%u observed=%x initial=%x guest=%x\n",form,get16(observed+6),get16(input+6),last_fop);
 bool any=false;for(unsigned i=0;i<10;++i){findings[form][i]+=differences[i];any|=differences[i];}++counts[form];bad[form]+=any;hardware_faults[form]+=bool(fault.code);native_faults[form]+=native_fault==1;unsupported_cases[form]+=native_fault==2;
 if(any&&bad[form]<=5){std::fprintf(stderr,"source sig=%llx exp=%x\n",(unsigned long long)get64(input+32),get16(input+40));std::fprintf(stderr,"form=%u top=%u tags=%x type=%u setting=%u mask=%x sticky=%x eflags=%x reserved_control=%u fault=%u/%u status=%x/%x tag=%x/%x counts=%u,%u,%u,%u expected=%u,%u,%u,%u findings:",form,top,tags,type,setting,mask,sticky,eflags,unsigned(reserved_control),native_fault,expected_fault,s.x87.fxsave.swd.flat,expected.x87.fxsave.swd.flat,s.x87.fxsave.ftw.flat,expected.x87.fxsave.ftw.flat,m.spans,m.reads,m.writes,m.records,spans,reads,writes,records);for(unsigned i=0;i<10;++i)if(differences[i])std::fprintf(stderr," %s",labels[i]);std::fprintf(stderr,"\n");if(differences[2]){auto a=reinterpret_cast<uint8_t*>(&s),b=reinterpret_cast<uint8_t*>(&expected);for(unsigned i=0,n=0;i<sizeof s&&n<12;++i)if(a[i]!=b[i]){std::fprintf(stderr," state[%u]=%02x/%02x",i,a[i],b[i]);++n;}std::fprintf(stderr,"\n");}}
}
extern "C" void verify_numeric_scope();
static Value integer_value(uint64_t n){if(!n)return {0,0};uint16_t exponent=0x403e;while(!(n>>63)){n<<=1;--exponent;}return {n,exponent};}
int main(){verify_numeric_scope();alignas(16) uint8_t original[512];save_host(original);
 int cpu[4];__cpuidex(cpu,7,0);std::fprintf(stderr,"host-cpuid7-ebx=%08x fdp-exception-only=%u cs-ds-deprecated=%u\n",unsigned(cpu[1]),(unsigned(cpu[1])>>6)&1,(unsigned(cpu[1])>>13)&1);// CPUID does not alone characterize the observed FDP/FOP behavior; see the independent pointer-update probe.
 for(unsigned form=0;form<form_count;++form){
 for(unsigned profile=0;profile<2;++profile){
  for(unsigned top=0;top<8;++top)for(unsigned occupancy=0;occupancy<4;++occupancy)for(unsigned type=0;type<48;++type)for(unsigned mode=0;mode<8;++mode)for(unsigned flags=0;flags<2;++flags){unsigned masks[]={63,62,61,55,47,31,0,60};unsigned tags=occupancy==0?0:occupancy==1?255:1<<((top+(occupancy==2?0:source_indices[form]))%8);run_case(form,top,tags,type,(mode+flags+type)%16,masks[mode],0,flags?7:0,original,false,profile!=0);}
  for(unsigned top=0;top<8;++top)for(unsigned tags=0;tags<256;++tags)for(unsigned flags=0;flags<2;++flags)run_case(form,top,tags,tags%48,tags%16,flags?62:63,0,flags?7:0,original,false,profile!=0);
  for(unsigned sample=48;sample<4144;++sample)run_case(form,sample%8,255,sample,sample%16,63,0,sample%8,original,false,profile!=0);
  for(unsigned sample=0;sample<128;++sample){auto bits=random_bits(sample+0xa501);unsigned exponent=1+unsigned(bits%0x7ffe),other=1+unsigned(random_bits(bits)%0x7ffe);switch(sample%8){case 0:exponent=1;other=1;break;case 1:exponent=0x7ffe;other=0x7ffe;break;case 2:other=exponent;break;case 3:exponent=0x7ffe;other=1;break;case 4:exponent=1;other=0x3ffe;break;case 5:exponent=1;other=0x4000;break;case 6:exponent=0x7ffe;other=0x3fff;break;default:break;}Value a{random_bits(bits)|0x8000000000000000ULL,uint16_t(exponent|((bits&1)<<15))},b{random_bits(bits+1)|0x8000000000000000ULL,uint16_t(other|((bits&2)<<14))};
   for(unsigned mode=0;mode<16;++mode)for(unsigned mask:{63u,62u,61u,55u,47u,31u,0u,60u})run_case(form,sample%8,255,2,mode,mask,0,sample%8,original,false,profile!=0,&a,&b);
  }
  for(unsigned masks=0;masks<64;++masks)for(unsigned sticky=0;sticky<64;++sticky)run_case(form,sticky%8,255,2,masks%16,masks,sticky,masks%8,original,false,profile!=0);
  for(unsigned type=0;type<24;++type)for(unsigned scale:{0u,1u,2u,63u,64u,16384u,24576u,24577u,32768u,65536u})for(unsigned signs=0;signs<4;++signs){auto a=values[type],b=integer_value(scale);a.exp|=uint16_t((signs&1)<<15);b.exp|=uint16_t((signs&2)<<14);for(unsigned mode=0;mode<16;++mode)for(unsigned mask:{63u,62u,61u,55u,47u,31u,0u,60u})run_case(form,type%8,255,type,mode,mask,0,signs,original,false,profile!=0,&a,&b);}

 }
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"hardware_faults\":%llu,\"native_faults\":%llu,\"unsupported_cases\":%llu,\"pointer_observation_differences\":%llu,\"opcode_observation_differences\":%llu,\"differences\":{",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)hardware_faults[form],(unsigned long long)native_faults[form],(unsigned long long)unsupported_cases[form],(unsigned long long)hardware_pointer_differences[form],(unsigned long long)hardware_opcode_differences[form]);for(unsigned i=0;i<10;++i)std::printf("%s\"%s\":%llu",i?",":"",labels[i],(unsigned long long)findings[form][i]);std::printf("}}\n");std::fflush(stdout);
 }restore_host(original);return 0;}
