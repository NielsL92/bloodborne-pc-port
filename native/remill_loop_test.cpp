// SPDX-License-Identifier: GPL-2.0-or-later
#define NOMINMAX
#include <windows.h>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
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
int main(int argc,char** argv) {
    if(argc!=2) fail("supply private original function bytes");
    std::ifstream f(argv[1],std::ios::binary);
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(f)),{});
    if(bytes.size()!=42) fail("unexpected original fixture size");
    auto code=static_cast<uint8_t*>(VirtualAlloc(reinterpret_cast<void*>(0x100000000ULL),0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    auto arena=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    auto stack=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
    if(!code||!arena||!stack) fail("fixture allocation");
    std::memcpy(code+0x3360,bytes.data(),bytes.size());
    FlushInstructionCache(GetCurrentProcess(),code,0x10000);
    unsigned cases=0;
    for(unsigned length=0;length<=8;++length) for(int marked=-1;marked<int(length);++marked) for(unsigned seed=0;seed<16;++seed) {
        std::memset(arena,0x5a,0x10000); std::memset(stack,0xcc,0x10000);
        for(unsigned n=0;n<length;++n) {
            auto node=arena+n*256;
            put(node,0x38,n+1<length ? uint64_t(arena+(n+1)*256) : uint64_t(0));
            put(node,0x20,uint64_t(arena+4096+n*256));
            put(node,0x6a,uint8_t((seed&0x7f)|(int(n)==marked ? 0x80 : 0)));
            put(arena+4096+n*256,0x10,uint64_t(0x123456789abcdef0ULL ^ (seed*31+n)));
        }
        CpuFrame input{};
        for(int i=0;i<16;++i) {
            input.gpr[i]=0x9abcde0012340000ULL+seed*4096+i;
            for(int j=0;j<32;++j) input.ymm[i][j]=uint8_t(i*17+j+seed);
        }
        input.gpr[5]=length ? uint64_t(arena) : 0;
        input.gpr[7]=uint64_t(stack+0x8000-8);
        input.flags=0x202|((seed&1)?0x8d5:0);
        input.mxcsr=0x1f80;
        put(stack,0x8000-8,uint64_t(&oracle_return));
        std::vector<uint8_t> initial_arena(arena,arena+0x10000),initial_stack(stack,stack+0x10000);
        CpuFrame original=input;
        protect(code,PAGE_EXECUTE_READ);
        oracle_enter(&original,code+0x3360);
        std::vector<uint8_t> oracle_arena(arena,arena+0x10000),oracle_stack(stack,stack+0x10000);
        std::memcpy(arena,initial_arena.data(),0x10000);std::memcpy(stack,initial_stack.data(),0x10000);
        // Strict translated call: the only original guest-code mapping is now non-executable.
        protect(code,PAGE_READONLY);
        MEMORY_BASIC_INFORMATION mbi{};
        VirtualQuery(code,&mbi,sizeof(mbi));
        if(mbi.Protect!=PAGE_READONLY) fail("original bytes executable in translated run");
        State s;to_state(input,s);
        Memory memory{{{uint64_t(arena),0x10000},{uint64_t(stack),0x10000}},0};
        auto result=sub_100003360(&s,0x100003360ULL,&memory);
        if(result!=&memory || memory.returned_pc!=uint64_t(&oracle_return) || s.gpr.rip.qword!=memory.returned_pc) fail("return target");
        for(int i=0;i<16;++i) if(*state_reg(s,i)!=original.gpr[i]) {
            std::fprintf(stderr,"case %u len %u marked %d seed %u GPR %d got %llx expected %llx\n",cases,length,marked,seed,i,*state_reg(s,i),original.gpr[i]);return 1;
        }
        constexpr uint64_t defined_flags=0xcc5; // CF/PF/ZF/SF/OF/DF; AF undefined after TEST/XOR.
        if((flags(s)^original.flags)&defined_flags) fail("defined flags differ");
        for(int i=0;i<16;++i) if(std::memcmp(&s.vec[i],original.ymm[i],32)) fail("YMM state differs");
        if(s.x87.fxsave64.mxcsr.flat!=original.mxcsr) fail("MXCSR differs");
        if(std::memcmp(arena,oracle_arena.data(),0x10000)||std::memcmp(stack,oracle_stack.data(),0x10000)) fail("memory writes differ");
        uint64_t expected=marked>=0 ? (0x123456789abcdef0ULL ^ (seed*31+marked)) : 0;
        if(s.gpr.rax.qword!=expected) fail("independent linked-list contract");
        ++cases;
    }
    std::printf("{\"status\":\"pass\",\"real_functions\":1,\"cases\":%u,\"rva\":\"0x3360\",\"contract\":\"all 16 GPRs; CF PF ZF SF OF; YMM0-15; MXCSR; arena and stack bytes; return target; independent list result\",\"guest_code_non_executable_during_aot\":true,\"not_playable\":true}\n",cases);
    VirtualFree(code,0,MEM_RELEASE);VirtualFree(arena,0,MEM_RELEASE);VirtualFree(stack,0,MEM_RELEASE);
}
