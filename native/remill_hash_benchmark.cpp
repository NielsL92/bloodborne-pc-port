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
struct Memory { Region regions[3]; uint64_t returned_pc=0; };
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
static Fn lookup(uint64_t pc) {
 switch(pc) {
 case 0x100002550:return sub_100002550;
 case 0x1000065d0:return sub_1000065d0;
 case 0x10000b820:return sub_10000b820;
 case 0x10002fa30:return sub_10002fa30;
 case 0x10003df50:return sub_10003df50;
 case 0x100003240:return sub_100003240;
 case 0x10005e4e0:return sub_10005e4e0;
 case 0x100077e80:return sub_100077e80;
 case 0x10002b2b0:return sub_10002b2b0;
 default:return nullptr;
 }
}
static unsigned calls=0;
extern "C" Memory* __remill_function_call(State* s,uint64_t pc,Memory* m) {
 auto target=lookup(pc);
 if(!target) {std::fprintf(stderr,"unknown native dispatch PC=0x%llx caller=0x%llx\n",pc,s->gpr.rip.qword);std::exit(4);}
 ++calls;return target(s,pc,m);
}

#include <chrono>
using Direct=uint64_t(__attribute__((sysv_abi)) *)(uint8_t*);
static volatile uint64_t checksum=0;
int main(int argc,char**argv) {
 if(argc!=2)fail("original fixture path");

 auto code=static_cast<uint8_t*>(VirtualAlloc(reinterpret_cast<void*>(0x100000000ULL),0x100000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 auto arena=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 auto stack=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 if(!code||!arena||!stack)fail("allocation");
 for(int rva:{0x2fa30,0x5e4e0}) {
  char name[64];std::snprintf(name,sizeof(name),"/%x/original.bin",rva);
  std::ifstream f(std::string(argv[1])+name,std::ios::binary);std::vector<uint8_t> data((std::istreambuf_iterator<char>(f)),{});
  if(data.empty())fail("fixture absent");std::memcpy(code+rva,data.data(),data.size());
 }
 FlushInstructionCache(GetCurrentProcess(),code,0x100000);
 auto direct=reinterpret_cast<Direct>(code+0x2fa30);constexpr int N=200000;
 for(int length:{8,64,1024}) {
  auto text=arena+0x1000;put(arena,0x18,uint64_t(text));put(text,0,uint64_t(length));put(arena,0xc,uint32_t(71));
  for(int i=0;i<length;++i)text[0xc+i]=uint8_t(i*31);
  CpuFrame input{};input.gpr[7]=uint64_t(stack+0x8000-8);input.mxcsr=0x1f80;
  put(stack,0x8000-8,uint64_t(0xfeedbabe));
  State state;to_state(input,state);Memory memory{{{uint64_t(arena),0x10000},{uint64_t(stack),0x10000},{uint64_t(code),0x100000}},0};
  for(int rep=-1;rep<5;++rep) {
   uint64_t sum1=0,sum2=0;double aot_ns=0,native_ns=0;
   // Alternate order, excluding the unreported warm-up and page protection changes.
   for(int order=0;order<2;++order) {
    bool aot=((rep+order)&1)==0;protect(code,aot?PAGE_READONLY:PAGE_EXECUTE_READ);
    MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(code,&mbi,sizeof(mbi));if(aot&&mbi.Protect!=PAGE_READONLY)fail("not NX");
    auto t=std::chrono::steady_clock::now();
    if(aot)for(int j=0;j<N;++j) {
     state.gpr.rdi.qword=uint64_t(arena);state.gpr.rsp.qword=input.gpr[7];
     sub_10002fa30(&state,0x10002fa30,&memory);sum2+=state.gpr.rax.qword;
    } else for(int j=0;j<N;++j)sum1+=direct(arena);
    double ns=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-t).count()/N;
    if(aot)aot_ns=ns;else native_ns=ns;
   }
   if(sum1!=sum2)fail("benchmark result mismatch");checksum=sum1^sum2;
   if(rep>=0)std::printf("{\"length\":%d,\"rep\":%d,\"iterations\":%d,\"native_ns\":%.3f,\"aot_ns\":%.3f,\"ratio\":%.4f}\n",length,rep,N,native_ns,aot_ns,aot_ns/native_ns);
  }
 }
}
