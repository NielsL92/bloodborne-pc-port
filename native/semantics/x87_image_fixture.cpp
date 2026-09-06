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
struct Memory {
 uint64_t stack[8];alignas(16) uint8_t bytes[640];unsigned offset=0,available=512;
 unsigned reads=0,writes=0,returns=0,spans=0,policies=0,segment_reads=0,segment_writes=0;
 uint64_t policy=0;uint32_t segments=0;
};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,void*,void*);
#include "x87-entries.h"
extern "C" void save_host(void*);extern "C" void restore_host(const void*);
static void fail(const char* why){std::fprintf(stderr,"image fixture infrastructure: %s\n",why);std::exit(2);}
static Memory guest;static State guest_state;static void* escape[5];static Memory* returned_memory;
// 1 is a pending x87 exception; 2 is the checked alignment condition;
// 3 means the fixture cannot represent this mapping. It is not a guest #PF.
static unsigned native_fault=0,native_pending=0;
static uint8_t* operand(Memory* m){return m->bytes+16+m->offset;}
static void identity(Memory* m,State* s){if(m!=&guest||s!=&guest_state)fail("runtime identity");}
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory* m,State* s,uint32_t pending){identity(m,s);if(!pending)fail("empty pending exception");native_fault=1;native_pending=pending;__builtin_longjmp(escape,1);}
extern "C" void __bb_native_x87_check_span(Memory* m,State* s,uint64_t at,uint32_t size,uint32_t write,uint32_t alignment){
 identity(m,s);++m->spans;if(at!=uint64_t(operand(m))||!((size==28&&alignment==1)||(size==512&&alignment==16&&write==1))||write>1)fail("span request");
 if(at%alignment){native_fault=2;__builtin_longjmp(escape,1);}if(size>m->available){native_fault=3;__builtin_longjmp(escape,1);}
}
extern "C" uint64_t __bb_native_x87_image_policy(Memory* m,State* s){identity(m,s);++m->policies;return m->policy;}
extern "C" uint32_t __bb_native_x87_pointer_segments(Memory* m,State* s){identity(m,s);++m->segment_reads;return m->segments;}
extern "C" void __bb_native_x87_set_pointer_segments(Memory* m,State* s,uint32_t value){identity(m,s);++m->segment_writes;m->segments=value;}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");if(__builtin_setjmp(escape)==0)returned_memory=fn(&guest_state,pc,&guest);}
static uint64_t map_fault_pc(uint64_t host_pc){for(unsigned i=0;i<sizeof(host_ips)/sizeof(host_ips[0]);++i)if(host_ips[i]==host_pc)return guest_ips[i];fail("unknown hardware fault instruction");return 0;}
struct HardwareFault {DWORD code;uint64_t pc,flags;alignas(16) uint8_t fp[512];};static HardwareFault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.pc=map_fault_pc(info->ContextRecord->Rip);fault.flags=info->ContextRecord->EFlags;std::memcpy(fault.fp,&info->ContextRecord->FltSave,512);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const void* in,void* out,void* saved,void* data,const void* original){fault={};__try{fn(in,out,saved,data);}__except(capture(GetExceptionInformation())){}restore_host(original);if(fault.code){if(fault.code!=EXCEPTION_ACCESS_VIOLATION&&(fault.code<EXCEPTION_FLT_DENORMAL_OPERAND||fault.code>EXCEPTION_FLT_UNDERFLOW))fail("unexpected SEH exception");std::memcpy(out,fault.fp,512);std::memcpy(static_cast<uint8_t*>(out)+544,&fault.flags,8);}}
static void address(Memory* m,uint64_t at,unsigned width){if(m!=&guest||at<uint64_t(operand(m))||at+width>uint64_t(operand(m))+m->available)fail("memory access");}
extern "C" uint8_t __remill_read_memory_8(Memory* m,uint64_t at){address(m,at,1);++m->reads;return *reinterpret_cast<uint8_t*>(at);}
extern "C" uint16_t __remill_read_memory_16(Memory* m,uint64_t at){address(m,at,2);m->reads+=2;uint16_t v;std::memcpy(&v,reinterpret_cast<void*>(at),2);return v;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("stack read");return m->stack[4];}
extern "C" Memory* __remill_write_memory_8(Memory* m,uint64_t at,uint8_t v){address(m,at,1);++m->writes;*reinterpret_cast<uint8_t*>(at)=v;return m;}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){identity(m,s);if(pc!=0xfeed0001)fail("return PC");s->gpr.rip.qword=pc;++m->returns;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error");return nullptr;}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");return nullptr;}
extern "C" uint8_t __remill_undefined_8(){return 0;}
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint32_t get32(const void* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}
static void status(State& s,uint16_t v){s.x87.fxsave.swd.flat=v;s.sw.ie=v&1;s.sw.de=(v>>1)&1;s.sw.ze=(v>>2)&1;s.sw.oe=(v>>3)&1;s.sw.ue=(v>>4)&1;s.sw.pe=(v>>5)&1;s.sw.sf=(v>>6)&1;s.sw.c0=(v>>8)&1;s.sw.c1=(v>>9)&1;s.sw.c2=(v>>10)&1;s.sw.c3=(v>>14)&1;}
static unsigned flags(const State& s){return s.aflag.cf|(s.aflag.pf<<2)|(s.aflag.af<<4)|(s.aflag.zf<<6)|(s.aflag.sf<<7)|(s.aflag.of<<11);}
static const uint64_t significands[]={0,0x8000000000000000ULL,0x8000000000000000ULL,0xc000000000000123ULL,0x8000000000000123ULL,1,0x8000000000000000ULL,0x1234};
static const uint16_t exponents[]={0,0x3fff,0x7fff,0x7fff,0x7fff,0,0,0x3fff};
static const char* labels[]={"hardware-import","memory-image","full-state","host-fp-state","flags","fault-class","fault-pc","pending-mask","memory-service-counts","pointer-metadata"};
static uint64_t counts[8]{},bad[8]{},findings[8][10]{},hardware_faults[8]{},native_faults[8]{},unsupported_spans[8]{};
static void run_case(unsigned form,unsigned top,unsigned tags,unsigned setting,unsigned mask,unsigned sticky,unsigned profile,unsigned offset,unsigned raw_word,const uint8_t* original,bool unsupported=false,unsigned raw_tags=65536){
 guest={};Memory& m=guest;m.offset=offset;m.available=unsupported?1:512;m.stack[4]=0xfeed0001;m.policy=(uint64_t(0xffff)<<32)|(profile?1:2);m.segments=0x004b0043;
 for(unsigned i=0;i<sizeof m.bytes;++i)m.bytes[i]=uint8_t(0x5a+i*17+setting);uint8_t* data=operand(&m);
 // Inputs vary TOP, raw tags, reserved bits and pending exceptions independently.
 uint16_t target_cw=raw_word<65536?uint16_t(raw_word):uint16_t(0x40|((setting%4)<<8)|(((setting/4)%4)<<10)|(mask^63));
 unsigned target_sticky=(sticky*13+setting)&63;uint16_t target_sw=uint16_t((((top+setting+1)&7)<<11)|target_sticky|((setting&1)?0x4500:0));
 put16(data,target_cw);put16(data+4,target_sw);put16(data+8,uint16_t(raw_tags<65536?raw_tags:tags*257u+setting*37u));put32(data+12,0xabcdef12);put16(data+16,0x53);put16(data+18,0xffff);put32(data+20,0xfedcba98);put16(data+24,0x5b);
 State& s=guest_state;std::memset(&s,0xa5,sizeof s);s.gpr.rdi.qword=uint64_t(data);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pcs[form];
 s.x87.fxsave.cwd.flat=uint16_t(0x40|((setting%4)<<8)|(((setting/4)%4)<<10)|mask);status(s,uint16_t((top<<11)|sticky|((sticky&~mask&63)?0x8080:0)|((setting&1)?0x4500:0)));s.x87.fxsave.ftw.flat=uint8_t(tags);s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xdeadbeef;s.x87.fxsave.ip=0x12345678;s.x87.fxsave.dp=0x87654321;s.x87.fxsave.fop=0x612;
 s.aflag.cf=s.aflag.af=s.aflag.sf=setting&1;s.aflag.pf=s.aflag.zf=s.aflag.of=(setting>>1)&1;s.rflag.flat=0x202|flags(s);
 alignas(16) uint8_t input[528]{},observed[1072]{},saved[512],before[512],after[512],hw_bytes[640],prior[640];
 std::memcpy(input,&s.x87,32);input[5]=0;put32(input+28,0);uint64_t initial_flags=s.rflag.flat;std::memcpy(input+512,&initial_flags,8);
 for(unsigned st=0;st<8;++st){unsigned type=(st+setting)%8;std::memcpy(&s.st.elems[st].val,&significands[type],8);std::memcpy(reinterpret_cast<uint8_t*>(&s.st.elems[st].val)+8,&exponents[type],2);std::memcpy(input+32+st*16,&s.st.elems[st].val,10);}
 for(unsigned reg=0;reg<16;++reg){for(unsigned i=0;i<16;++i)input[160+reg*16+i]=uint8_t(reg*16+i+setting);std::memcpy(&s.vec[reg].xmm,input+160+reg*16,16);}
 std::memcpy(hw_bytes,m.bytes,sizeof hw_bytes);std::memcpy(prior,m.bytes,sizeof prior);State expected=s;unsigned initial_pending=sticky&~mask&63;
 bool import_difference=false;
 if(!unsupported){
  hardware_run(hardware[form],input,observed,saved,hw_bytes+16+offset,original);
  import_difference=get16(input)!=get16(observed+560)||get16(input+2)!=get16(observed+562)||input[4]!=observed[564]||std::memcmp(input+32,observed+592,384)!=0;
 }else fault={};
 restore_host(original);save_host(before);native_fault=0;native_pending=0;returned_memory=nullptr;invoke(lifted[form],pcs[form]);save_host(after);restore_host(original);
 const bool load=form==1||form==4,roundtrip=form==5||form==6,save=form==0||roundtrip,fx=form==2||form==3;
 unsigned expected_fault=unsupported?((load&&initial_pending)?1:3):fault.code==EXCEPTION_ACCESS_VIOLATION?2:fault.code?1:0;
 if(!unsupported&&expected_fault==2&&!(fx&&offset))fail("unexpected hardware access violation");
 bool completed=expected_fault==0,early_pending=expected_fault==1&&((load||form==7)&&initial_pending);
 unsigned spans=0,reads=0,writes=0,policies=0,segment_reads=0,segment_writes=0;uint32_t segments=0x004b0043;
 if(save||fx||load&&!early_pending){spans=1;if(expected_fault!=2&&expected_fault!=3){policies=1;if(save||fx){segment_reads=1;writes=save?28:profile&&!(get16(input+2)&0x80)?398:416;}if(load){reads=28;segment_writes=1;segments=profile?0x005b0053:0;}}}
 if(roundtrip&&expected_fault!=3){++spans;++policies;reads=28;++segment_writes;segments=profile?0x004b0043:0;}
 if(form==7&&!early_pending)reads=2;
 if(!unsupported){
  uint8_t* hw=hw_bytes+16+offset;
  // Hardware is the oracle for all ordinary bytes. Profile deltas below are
  // explicit primary-manual write rules, not an AMD execution observation.
  if(profile&&save){put16(hw+16,0x43);put16(hw+24,0x4b);}
  if(profile&&fx&&expected_fault!=2){if(!(get16(input+2)&0x80))std::memcpy(hw+6,prior+16+offset+6,18);else if(form==2){put16(hw+12,0x43);put16(hw+20,0x4b);}}
  expected.x87.fxsave.cwd.flat=get16(observed);status(expected,get16(observed+2));expected.x87.fxsave.ftw.flat=observed[4];
  // All tested operations preserve full payload bits or rotate physical
  // registers on FLDENV; the hardware image supplies the independent result.
  for(unsigned st=0;st<8;++st)std::memcpy(&expected.st.elems[st].val,observed+32+st*16,10);
  if((load&&!early_pending)||roundtrip){expected.x87.fxsave.ip=get32(observed+8);expected.x87.fxsave.dp=get32(observed+16);expected.x87.fxsave.fop=get16(observed+6);}
 }
 if(completed){expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;}else expected.gpr.rip.qword=unsupported?pcs[form]:fault.pc;
 if(unsupported&&expected_fault==1)expected.gpr.rip.qword=pcs[form];
 bool differences[]={import_difference,!unsupported&&std::memcmp(m.bytes,hw_bytes,sizeof hw_bytes)!=0,std::memcmp(&s,&expected,sizeof s)!=0,std::memcmp(before,after,28)!=0||std::memcmp(before+32,after+32,128)!=0,!unsupported&&flags(s)!=(get16(observed+544)&0x8d5),native_fault!=expected_fault,s.gpr.rip.qword!=expected.gpr.rip.qword,native_fault==1&&native_pending!=(early_pending?initial_pending:get16(observed+2)&~get16(observed)&63),m.spans!=spans||m.reads!=reads||m.writes!=writes||m.policies!=policies||m.segment_reads!=segment_reads||m.segment_writes!=segment_writes||m.returns!=unsigned(completed)||(completed&&returned_memory!=&m),m.segments!=segments};
 if(unsupported)differences[1]=std::memcmp(m.bytes,prior,sizeof prior)!=0;
 bool any=false;for(unsigned i=0;i<10;++i){findings[form][i]+=differences[i];any|=differences[i];}++counts[form];bad[form]+=any;hardware_faults[form]+=bool(fault.code);native_faults[form]+=native_fault==1||native_fault==2;unsupported_spans[form]+=native_fault==3;
 if(any&&bad[form]<=4){std::fprintf(stderr,"form=%u top=%u tags=%x setting=%u masks=%x sticky=%x profile=%u offset=%u raw=%x unsupported=%u fault=%u/%u status=%x/%x control=%x/%x service=%u,%u,%u,%u,%u,%u expected=%u,%u,%u,%u,%u,%u findings:",form,top,tags,setting,mask,sticky,profile,offset,raw_word,unsigned(unsupported),native_fault,expected_fault,s.x87.fxsave.swd.flat,expected.x87.fxsave.swd.flat,s.x87.fxsave.cwd.flat,expected.x87.fxsave.cwd.flat,m.spans,m.reads,m.writes,m.policies,m.segment_reads,m.segment_writes,spans,reads,writes,policies,segment_reads,segment_writes);for(unsigned i=0;i<10;++i)if(differences[i])std::fprintf(stderr," %s",labels[i]);std::fprintf(stderr,"\n");if(differences[2]){auto a=reinterpret_cast<uint8_t*>(&s),b=reinterpret_cast<uint8_t*>(&expected);for(unsigned i=0,n=0;i<sizeof s&&n<12;++i)if(a[i]!=b[i]){std::fprintf(stderr," state[%u]=%02x/%02x",i,a[i],b[i]);++n;}std::fprintf(stderr,"\n");}}
}
int main(){
 alignas(16) uint8_t original[512];save_host(original);
 for(unsigned form=0;form<form_count;++form){
  for(unsigned profile=0;profile<2;++profile)for(unsigned top=0;top<8;++top)for(unsigned occupancy=0;occupancy<4;++occupancy)for(unsigned setting=0;setting<16;++setting)for(unsigned mode=0;mode<8;++mode){unsigned masks=mode==0?63:mode==1?0:63^(1<<(mode-2));unsigned sticky=mode==0?0:mode==1?63:1<<(mode-2);unsigned tags=occupancy==0?0:occupancy==1?255:1<<((top+occupancy-2)%8);run_case(form,top,tags,setting,masks,sticky,profile,0,65536,original);}
  if(form==1||form==4||form==7)for(unsigned raw=0;raw<65536;++raw)run_case(form,raw%8,raw%256,(raw/256)%16,63,0,raw&1,0,raw,original);
  if(form!=7)for(unsigned masks=0;masks<64;++masks)for(unsigned sticky=0;sticky<64;++sticky)for(unsigned top=0;top<8;++top)run_case(form,top,255,(masks+sticky)%16,masks,sticky,top&1,0,65536,original);
  if(form==1)for(unsigned raw_tags=0;raw_tags<65536;++raw_tags)run_case(form,raw_tags%8,raw_tags&255,(raw_tags>>8)%16,63,0,raw_tags&1,0,65536,original,false,raw_tags);
  if(form==0||form==1||form==4||form==5||form==6)for(unsigned offset=1;offset<16;++offset)for(unsigned pending=0;pending<2;++pending)for(unsigned profile=0;profile<2;++profile)run_case(form,offset%8,255,offset,pending?62:63,pending,profile,offset,65536,original);
  if(form==2||form==3)for(unsigned offset=1;offset<16;++offset)for(unsigned top=0;top<8;++top)for(unsigned pending=0;pending<2;++pending)run_case(form,top,255,3,pending?62:63,pending,0,offset,65536,original);
  if(form!=7)for(unsigned profile=0;profile<2;++profile)for(unsigned pending=0;pending<2;++pending)run_case(form,0,255,3,pending?62:63,pending,profile,0,65536,original,true);
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"hardware_faults\":%llu,\"native_faults\":%llu,\"unsupported_spans\":%llu,\"differences\":{",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)hardware_faults[form],(unsigned long long)native_faults[form],(unsigned long long)unsupported_spans[form]);for(unsigned i=0;i<10;++i)std::printf("%s\"%s\":%llu",i?",":"",labels[i],(unsigned long long)findings[form][i]);std::printf("}}\n");std::fflush(stdout);
 }
 restore_host(original);return 0;
}
