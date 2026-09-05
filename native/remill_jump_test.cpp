// SPDX-License-Identifier: GPL-2.0-or-later
#define NOMINMAX
#include <windows.h>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <immintrin.h>
#include <vector>
#include <remill/Arch/X86/Runtime/State.h>
struct alignas(32) CpuFrame {
    uint64_t gpr[16];
    uint64_t flags;
    uint32_t mxcsr;
    uint8_t padding[20];
    uint8_t ymm[16][32];
};
static_assert(offsetof(CpuFrame,flags)==128 && offsetof(CpuFrame,mxcsr)==136 && offsetof(CpuFrame,ymm)==160);
extern "C" void oracle_enter(CpuFrame*,void*);
extern "C" void oracle_return();
struct Region { uint64_t begin; size_t size; };
struct Memory { Region regions[4]; uint64_t returned_pc=0; };
extern "C" Memory* sub_100003360(State*,uint64_t,Memory*);
static void fail(const char* why) { std::fprintf(stderr,"FAIL: %s\n",why); std::exit(1); }
template<class T> static T read(Memory* m,uint64_t a) {
    for(auto r:m->regions) if(a>=r.begin && a-r.begin<=r.size && sizeof(T)<=r.size-(a-r.begin)) {
        T v; std::memcpy(&v,reinterpret_cast<void*>(a),sizeof(v)); return v;
    }
    std::fprintf(stderr,"unmapped read at 0x%llx, width %zu\n",a,sizeof(T)); std::exit(2);
}
extern "C" uint8_t __remill_read_memory_8(Memory* m,uint64_t a) { return read<uint8_t>(m,a); }
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t a) { return read<uint64_t>(m,a); }
// These are annotation intrinsics: the boolean is already computed by the lifter.
extern "C" bool __remill_flag_computation_zero(bool v,...) { return v; }
extern "C" bool __remill_flag_computation_sign(bool v,...) { return v; }
extern "C" bool __remill_compare_eq(bool v) { return v; }
extern "C" bool __remill_compare_neq(bool v) { return v; }
// AF after TEST/XOR is architecturally undefined and is excluded from comparison.
extern "C" uint8_t __remill_undefined_8() { return 0; }
static unsigned completed_calls=0;
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m) {
    if(pc!=uint64_t(&oracle_return)) ++completed_calls;
    m->returned_pc=pc; s->gpr.rip.qword=pc; return m;
}
static uint64_t* state_reg(State& s,int i) {
    uint64_t* p[]={&s.gpr.rax.qword,&s.gpr.rbx.qword,&s.gpr.rcx.qword,&s.gpr.rdx.qword,
      &s.gpr.rsi.qword,&s.gpr.rdi.qword,&s.gpr.rbp.qword,&s.gpr.rsp.qword,
      &s.gpr.r8.qword,&s.gpr.r9.qword,&s.gpr.r10.qword,&s.gpr.r11.qword,
      &s.gpr.r12.qword,&s.gpr.r13.qword,&s.gpr.r14.qword,&s.gpr.r15.qword};
    return p[i];
}
static void to_state(const CpuFrame& f,State& s) {
    std::memset(&s,0,sizeof(s));
    for(int i=0;i<16;++i) { *state_reg(s,i)=f.gpr[i]; std::memcpy(&s.vec[i],f.ymm[i],32); }
    s.rflag.flat=f.flags;
    s.aflag.cf=(f.flags>>0)&1; s.aflag.pf=(f.flags>>2)&1; s.aflag.af=(f.flags>>4)&1;
    s.aflag.zf=(f.flags>>6)&1; s.aflag.sf=(f.flags>>7)&1; s.aflag.df=(f.flags>>10)&1; s.aflag.of=(f.flags>>11)&1;
    s.x87.fxsave64.mxcsr.flat=f.mxcsr;
}
static uint64_t flags(const State& s) {
    return s.aflag.cf | (uint64_t(s.aflag.pf)<<2) | (uint64_t(s.aflag.af)<<4) |
      (uint64_t(s.aflag.zf)<<6) | (uint64_t(s.aflag.sf)<<7) | (uint64_t(s.aflag.df)<<10) | (uint64_t(s.aflag.of)<<11);
}
template<class T> static void put(uint8_t* p,size_t off,T v) { std::memcpy(p+off,&v,sizeof(v)); }
static void protect(void* p,DWORD prot) {
    DWORD old;
    if(!VirtualProtect(p,0x100000,prot,&old)) fail("VirtualProtect");
}

extern "C" Memory* sub_100001a50(State*,uint64_t,Memory*);
extern "C" Memory* sub_100003500(State*,uint64_t,Memory*);
extern "C" Memory* sub_100003530(State*,uint64_t,Memory*);
extern "C" uint16_t __remill_read_memory_16(Memory* m,uint64_t a) { return read<uint16_t>(m,a); }
extern "C" float __remill_read_memory_f32(Memory* m,uint64_t a) { return read<float>(m,a); }
template<class T> static Memory* write(Memory* m,uint64_t a,T v) {
    for(auto r:m->regions) if(a>=r.begin && a-r.begin<=r.size && sizeof(T)<=r.size-(a-r.begin)) {
        std::memcpy(reinterpret_cast<void*>(a),&v,sizeof(v));return m;
    }
    std::fprintf(stderr,"unmapped write at 0x%llx width %zu\n",a,sizeof(T));std::exit(2);
}
extern "C" Memory* __remill_write_memory_64(Memory* m,uint64_t a,uint64_t v) {return write(m,a,v);}
extern "C" Memory* __remill_write_memory_16(Memory* m,uint64_t a,uint16_t v) {return write(m,a,v);}
extern "C" Memory* __remill_write_memory_f32(Memory* m,uint64_t a,float v) {return write(m,a,v);}
extern "C" Memory* __remill_error(State*,uint64_t pc,Memory*) {
    std::fprintf(stderr,"explicit Remill failure at guest PC 0x%llx\n",pc);std::exit(3);
}

#include <string>
extern "C" Memory* sub_100002550(State*,uint64_t,Memory*);
extern "C" Memory* sub_1000065d0(State*,uint64_t,Memory*);
extern "C" Memory* sub_10000b820(State*,uint64_t,Memory*);
extern "C" Memory* sub_10002fa30(State*,uint64_t,Memory*);
extern "C" Memory* sub_10003df50(State*,uint64_t,Memory*);
extern "C" Memory* sub_100003240(State*,uint64_t,Memory*);
extern "C" Memory* sub_10005e4e0(State*,uint64_t,Memory*);
extern "C" Memory* sub_100077e80(State*,uint64_t,Memory*);
extern "C" Memory* sub_10002b2b0(State*,uint64_t,Memory*);

extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t a) { return read<uint32_t>(m,a); }
extern "C" Memory* __remill_write_memory_8(Memory* m,uint64_t a,uint8_t v) {return write(m,a,v);}
extern "C" Memory* __remill_write_memory_32(Memory* m,uint64_t a,uint32_t v) {return write(m,a,v);}
extern "C" bool __remill_compare_ult(bool v) {return v;}
extern "C" bool __remill_compare_ule(bool v) {return v;}
extern "C" bool __remill_compare_ugt(bool v) {return v;}
extern "C" bool __remill_compare_uge(bool v) {return v;}
extern "C" bool __remill_compare_slt(bool v) {return v;}
extern "C" bool __remill_compare_sle(bool v) {return v;}
extern "C" bool __remill_compare_sgt(bool v) {return v;}
extern "C" bool __remill_compare_sge(bool v) {return v;}
extern "C" bool __remill_flag_computation_carry(bool v,...) {return v;}
extern "C" bool __remill_flag_computation_overflow(bool v,...) {return v;}

using Fn=Memory*(*)(State*,uint64_t,Memory*);
extern "C" Memory* sub_1000401f0(State*,uint64_t,Memory*);
extern "C" Memory* sub_10004034d(State*,uint64_t,Memory*);
extern "C" Memory* sub_10004023c(State*,uint64_t,Memory*);
extern "C" Memory* sub_100040264(State*,uint64_t,Memory*);
extern "C" Memory* sub_100040292(State*,uint64_t,Memory*);
extern "C" Memory* sub_1000402c8(State*,uint64_t,Memory*);
static unsigned jumps=0, targets[5]{};
extern "C" Memory* __remill_jump(State*s,uint64_t pc,Memory*m){
 ++jumps;
 switch(pc){
 case 0x10004034d:++targets[0];return sub_10004034d(s,pc,m);
 case 0x10004023c:++targets[1];return sub_10004023c(s,pc,m);
 case 0x100040264:++targets[2];return sub_100040264(s,pc,m);
 case 0x100040292:++targets[3];return sub_100040292(s,pc,m);
 case 0x1000402c8:++targets[4];return sub_1000402c8(s,pc,m);
 default:std::fprintf(stderr,"unknown jump target=0x%llx caller=0x10004023a module_sha256=d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9 rsp=0x%llx\n",pc,s->gpr.rsp.qword);std::exit(4);
 }
}
static void load(uint8_t*p,const std::string&name,size_t expected){
 std::ifstream f(name,std::ios::binary);std::vector<char>b((std::istreambuf_iterator<char>(f)),{});
 if(b.size()!=expected)fail("input length");std::memcpy(p,b.data(),b.size());
}
int main(int argc,char**argv){
 if(argc!=2)fail("fixture directory");
 auto*code=(uint8_t*)VirtualAlloc((void*)0x100000000ULL,0x100000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 auto*global=(uint8_t*)VirtualAlloc((void*)0x102bc0000ULL,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 auto*arena=(uint8_t*)VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 auto*stack=(uint8_t*)VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 if(uint64_t(code)!=0x100000000ULL||uint64_t(global)!=0x102bc0000ULL||!arena||!stack)fail("allocation");
 load(code+0x401f0,std::string(argv[1])+"/original.bin",412);
 load(global+0xf50,std::string(argv[1])+"/global.bin",33);
 DWORD old;VirtualProtect(global,0x10000,PAGE_READONLY,&old);
 FlushInstructionCache(GetCurrentProcess(),code,0x100000);
 unsigned passed=0,failed=0;
 for(unsigned n=0;n<=32;++n)for(unsigned bit=0;bit<8;++bit)for(unsigned seed=0;seed<8;++seed){
  std::memset(arena,0x5a,0x10000);std::memset(stack,0xcc,0x10000);
  auto*data=arena+0x1000;
  for(unsigned k=0;k<32;++k)data[k]=uint8_t(k*31+seed*59);
  unsigned byte=seed%4;
  put(arena,0,uint64_t(data));put(arena,0x10,uint64_t(byte));put(arena,0x18,uint32_t(bit));
  uint32_t expected=0;
  for(unsigned k=0;k<n;++k){unsigned pos=byte*8+bit+k;expected=(expected<<1)|((data[pos/8]>>(7-pos%8))&1);}
  CpuFrame input{};
  for(int i=0;i<16;++i){input.gpr[i]=0x9abc000010000000ULL+seed*4096+i;for(int j=0;j<32;++j)input.ymm[i][j]=uint8_t(i*17+j+seed);}
  input.gpr[5]=uint64_t(arena);input.gpr[4]=n;input.gpr[7]=uint64_t(stack+0x8000-8);
  input.flags=0xad7;input.mxcsr=0x1f80;put(stack,0x8000-8,uint64_t(&oracle_return));
  std::vector<uint8_t> initial(arena,arena+0x10000),initial_stack(stack,stack+0x10000);
  CpuFrame original=input;protect(code,PAGE_EXECUTE_READ);oracle_enter(&original,code+0x401f0);
  std::vector<uint8_t> after(arena,arena+0x10000),after_stack(stack,stack+0x10000);
  if(original.gpr[0]!=expected||*(uint64_t*)(arena+0x10)!=byte+(bit+n)/8||*(uint32_t*)(arena+0x18)!=(bit+n)%8)fail("original independent bitstream");
  std::memcpy(arena,initial.data(),0x10000);std::memcpy(stack,initial_stack.data(),0x10000);
  protect(code,PAGE_READONLY);MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(code,&mbi,sizeof(mbi));if(mbi.Protect!=PAGE_READONLY)fail("original executable");
  State s;to_state(input,s);
  Memory m{{{uint64_t(arena),0x10000},{uint64_t(stack),0x10000},{uint64_t(code),0x100000},{uint64_t(global),0x10000}},0};
  auto*result=sub_1000401f0(&s,0x1000401f0,&m);
  const char*issue=nullptr;int detail=-1;uint64_t got=0,want=0;
  if(result!=&m||m.returned_pc!=uint64_t(&oracle_return)||s.gpr.rip.qword!=uint64_t(&oracle_return))issue="logical return";
  if(!issue&&(s.gpr.rax.qword!=expected||*(uint64_t*)(arena+0x10)!=byte+(bit+n)/8||*(uint32_t*)(arena+0x18)!=(bit+n)%8))issue="independent bitstream";
  for(int i=0;i<16&&!issue;++i)if(*state_reg(s,i)!=original.gpr[i]){issue="gpr";detail=i;got=*state_reg(s,i);want=original.gpr[i];}
  uint64_t mask=0xcd5; // CF/PF/AF/ZF/SF/DF/OF; AF undefined on final OR/XOR paths.
  if(n && ((bit+n)%8==0||bit+n>32))mask&=~0x10;
  if(!issue&&((flags(s)^original.flags)&mask)){issue="flags";got=flags(s)&mask;want=original.flags&mask;}
  for(int i=0;i<16&&!issue;++i)if(std::memcmp(&s.vec[i],original.ymm[i],32)){issue="ymm";detail=i;}
  if(!issue&&s.x87.fxsave64.mxcsr.flat!=original.mxcsr)issue="mxcsr";
  if(!issue&&std::memcmp(arena,after.data(),0x10000))issue="arena";
  if(!issue&&std::memcmp(stack,after_stack.data(),0x10000))issue="stack";
  if(issue){++failed;if(failed<10)std::printf("{\"effect\":\"%s\",\"n\":%u,\"bit\":%u,\"seed\":%u,\"detail\":%d,\"got\":\"0x%llx\",\"expected\":\"0x%llx\"}\n",issue,n,bit,seed,detail,got,want);}else ++passed;
 }
 for(auto count:targets)if(!count)fail("unexercised table target");
 std::printf("{\"rva\":\"0x401f0\",\"passed\":%u,\"failed\":%u,\"jump_dispatches\":%u,\"targets\":[%u,%u,%u,%u,%u],\"original_code_NX_during_aot\":true,\"independent_bitstream_reference\":true,\"effects\":\"all GPRs, defined arithmetic flags and DF, YMM0-15, MXCSR, arena and stack writes, logical return; AF excluded only on final logical-instruction paths\"}\n",passed,failed,jumps,targets[0],targets[1],targets[2],targets[3],targets[4]);
 return failed?1:0;
}
