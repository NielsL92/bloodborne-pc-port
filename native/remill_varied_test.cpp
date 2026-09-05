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
struct Memory { Region regions[2]; uint64_t returned_pc=0; };
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
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m) {
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
    if(!VirtualProtect(p,0x10000,prot,&old)) fail("VirtualProtect");
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
int main(int argc,char** argv) {
    if(argc<3) fail("supply original bytes and fixture RVA");
    auto rva=std::strtoull(argv[2],nullptr,16);
    using Fn=Memory*(*)(State*,uint64_t,Memory*);
    Fn translated=nullptr;size_t size=0;
    switch(rva) {
      case 0x1a50:translated=sub_100001a50;size=43;break;
      case 0x3500:translated=sub_100003500;size=38;break;
      case 0x3530:translated=sub_100003530;size=41;break;
      default:fail("unknown contract");
    }
    std::ifstream f(argv[1],std::ios::binary);
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});
    if(bytes.size()!=size) fail("unexpected fixture size");
    auto code=static_cast<uint8_t*>(VirtualAlloc(reinterpret_cast<void*>(0x100000000ULL),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    auto arena=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    auto stack=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    if(!code||!arena||!stack) fail("fixture allocation");
    std::memcpy(code+rva,bytes.data(),bytes.size());FlushInstructionCache(GetCurrentProcess(),code,0x10000);
    const uint32_t bits[]={0x00000000,0x80000000,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0x00000001,0x80000001,0x007fffff,0x00800000};
    unsigned passed=0,failed=0;int first=argc>3 ? std::atoi(argv[3]) : 0;
    int last=argc>3 ? first+1 : 1536;
    for(int id=first;id<last;++id) {
        unsigned index=id%12,mode=(id/12)%16,variant=(id/192)%8;
        std::memset(arena,0x5a,0x10000);std::memset(stack,0xcc,0x10000);
        CpuFrame input{};
        for(int i=0;i<16;++i) {
            input.gpr[i]=0x9abcde0012340000ULL+id*4096+i;
            for(int j=0;j<32;++j)input.ymm[i][j]=uint8_t(i*17+j+id);
        }
        input.gpr[5]=uint64_t(arena);input.gpr[4]=variant&1;
        input.gpr[7]=uint64_t(stack+0x8000-8);input.flags=0xad7;
        input.mxcsr=0x1f80|((mode&3)<<13)|((mode&4)?0x40:0)|((mode&8)?0x8000:0);
        uint32_t a=bits[index],b=(variant&2)?bits[(index+1)%12]:a;
        put(input.ymm[0],0,a);put(input.ymm[1],0,b);
        if(rva==0x1a50) {
            input.gpr[4]=uint64_t(arena);
            put(arena,0x58,(variant&1)?uint64_t(0):uint64_t(arena+256));
            put(arena+256,0x10,a);put(arena+256,0x14,b);
            // Equal and overlapping output buffers; both input scalars are loaded before stores.
            input.gpr[5]=uint64_t(arena+((variant&4)?0x110:0x400));
            if(variant&2)input.gpr[5]+=4;
        } else {
            put(arena,0x40,(variant&2)?bits[(index+1)%12]:a);
            put(arena,0x44,b);put(arena,0x6a,uint16_t((variant&1)?0:0x14));
        }
        put(stack,0x8000-8,uint64_t(&oracle_return));
        std::vector<uint8_t> initial_arena(arena,arena+0x10000),initial_stack(stack,stack+0x10000);
        CpuFrame original=input;protect(code,PAGE_EXECUTE_READ);oracle_enter(&original,code+rva);
        std::vector<uint8_t> oracle_arena(arena,arena+0x10000),oracle_stack(stack,stack+0x10000);
        std::memcpy(arena,initial_arena.data(),0x10000);std::memcpy(stack,initial_stack.data(),0x10000);
        protect(code,PAGE_READONLY);
        MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(code,&mbi,sizeof(mbi));
        if(mbi.Protect!=PAGE_READONLY)fail("original code executable during AOT");
        State state;to_state(input,state);
        Memory memory{{{uint64_t(arena),0x10000},{uint64_t(stack),0x10000}},0};
        // Synchronize the guest floating-point environment at this verified native boundary.
        unsigned host_csr=_mm_getcsr();_mm_setcsr(input.mxcsr);
        auto result=translated(&state,0x100000000ULL+rva,&memory);
        state.x87.fxsave64.mxcsr.flat=_mm_getcsr();_mm_setcsr(host_csr);
        const char* issue=nullptr;int detail=-1;uint64_t got=0,want=0;
        if(result!=&memory||memory.returned_pc!=uint64_t(&oracle_return)||state.gpr.rip.qword!=uint64_t(&oracle_return))issue="return_target";
        for(int i=0;i<16&&!issue;++i)if(*state_reg(state,i)!=original.gpr[i]) {
            issue="gpr";detail=i;got=*state_reg(state,i);want=original.gpr[i];
        }
        // UCOMISS early return defines AF. TEST/AND/XOR paths leave AF undefined.
        auto normalized=[&](uint32_t x) {
            if((input.mxcsr&0x40) && !(x&0x7f800000)) x&=0x80000000;
            return (x&0x7fffffff)==0 ? uint32_t(0) : x;
        };
        uint32_t compared=(variant&2)?bits[(index+1)%12]:a;
        bool nan=((a&0x7fffffff)>0x7f800000)||((compared&0x7fffffff)>0x7f800000);
        bool early_ucomiss=rva==0x3500 && !(variant&1) && (nan||normalized(a)!=normalized(compared));
        uint64_t flag_mask=0xcc5|(early_ucomiss?0x10:0);
        if(!issue&&((flags(state)^original.flags)&flag_mask)) {issue="flags";got=flags(state)&flag_mask;want=original.flags&flag_mask;}
        for(int i=0;i<16&&!issue;++i)for(int j=0;j<32&&!issue;++j)
          if(reinterpret_cast<uint8_t*>(&state.vec[i])[j]!=original.ymm[i][j]) {
            issue="ymm";detail=i*32+j;got=reinterpret_cast<uint8_t*>(&state.vec[i])[j];want=original.ymm[i][j];
          }
        if(!issue&&state.x87.fxsave64.mxcsr.flat!=original.mxcsr) {issue="mxcsr";got=state.x87.fxsave64.mxcsr.flat;want=original.mxcsr;}
        if(!issue&&(std::memcmp(arena,oracle_arena.data(),0x10000)||std::memcmp(stack,oracle_stack.data(),0x10000)))issue="memory";
        if(issue) {
            ++failed;
            if(failed<=20)std::printf("{\"status\":\"fail\",\"rva\":\"0x%llx\",\"case\":%d,\"lhs_bits\":\"0x%x\",\"rhs_bits\":\"0x%x\",\"mxcsr\":\"0x%x\",\"effect\":\"%s\",\"detail\":%d,\"got\":\"0x%llx\",\"expected\":\"0x%llx\"}\n",rva,id,a,b,input.mxcsr,issue,detail,got,want);
        }else ++passed;
    }
    std::printf("{\"rva\":\"0x%llx\",\"passed\":%u,\"failed\":%u,\"original_code_NX_during_aot\":true,\"scope\":\"GPR, defined flags, full YMM0-15, MXCSR, memory, return target; masked FP exceptions\"}\n",rva,passed,failed);
    return failed?1:0;
}
