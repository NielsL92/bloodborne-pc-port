// SPDX-License-Identifier: GPL-2.0-or-later
// Authored service ABI/control test. Not an architectural full-state oracle.
// Original: CPU-native authored code -> native service -> CPU-native callback.
// AOT: Remill objects -> explicit native gateway -> Remill callback, code pages NX.
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include <remill/Arch/X86/Runtime/State.h>
constexpr uint64_t BASE=0x1001000000, CALLBACK_PC=BASE+0x100;
constexpr uint64_t SERVICE=0x2002000000, ESCAPE=0x2002000100;
constexpr uint64_t TOP_RETURN=0xfeed0001, CALLBACK_RETURN=0xfeed0002;
using Callback = uint64_t(__attribute__((sysv_abi)) *)(int64_t,uint64_t,uint64_t*);
using Root = uint64_t(__attribute__((sysv_abi)) *)(int64_t,Callback,uint64_t,uint64_t*);
struct Memory {
    uint8_t* stack; size_t stack_size;
    uint64_t* output;
    bool nonlocal=false;
    uint64_t escape_value=0,returned_pc=0;
    State saved{};
    unsigned events[8]{},event_count=0;
};
static const char* phase="startup";
static int active_case=-1;
#ifndef FIXTURE_SHA256
#error Fixture hash must be supplied by the experiment builder.
#endif
static LONG CALLBACK DiagnosticException(EXCEPTION_POINTERS* e) {
    std::fprintf(stderr,"exception=0x%lx pc=0x%llx rsp=0x%llx phase=%s case=%d\n",
        e->ExceptionRecord->ExceptionCode,e->ContextRecord->Rip,e->ContextRecord->Rsp,phase,active_case);
    if(e->ExceptionRecord->ExceptionCode==EXCEPTION_ACCESS_VIOLATION)
        std::fprintf(stderr,"access=%llu address=0x%llx module_sha256=%s\n",
            e->ExceptionRecord->ExceptionInformation[0],e->ExceptionRecord->ExceptionInformation[1],FIXTURE_SHA256);
    std::fflush(stderr);TerminateProcess(GetCurrentProcess(),e->ExceptionRecord->ExceptionCode);
    return EXCEPTION_CONTINUE_SEARCH;
}
static unsigned original_events[8],original_count;
static uint64_t* original_marker;
static uint64_t original_escape_value;
static void* jump_buffer[5];
static void fail(const char* msg) { std::fprintf(stderr,"FAIL %s\n",msg);std::exit(2); }
static void event(Memory* m,unsigned e) {
    if(m->event_count>=8)fail("event overflow");m->events[m->event_count++]=e;
}
extern "C" __attribute__((sysv_abi,noinline)) uint64_t original_escape(int64_t x) {
    original_events[original_count++]=3;
    original_escape_value=uint64_t(x)^0x55aa55aa55aa55aaULL;
    __builtin_longjmp(jump_buffer,1);
}
extern "C" __attribute__((sysv_abi,noinline)) uint64_t original_service(int64_t x,Callback callback,uint64_t,uint64_t*) {
    original_events[original_count++]=1;
    uint64_t v=callback(x+3,uint64_t(&original_escape),original_marker);
    original_events[original_count++]=2;
    return v+5;
}
// Keep the setjmp frame alive (disable_tail_calls) and the reference transfer within one ABI. Returning normally from this
// wrapper lets the Windows caller restore registers clobbered by System V calls.
extern "C" __attribute__((sysv_abi,noinline,disable_tail_calls)) uint64_t original_run(
    Root root, int64_t x, Callback callback, uint64_t* output) {
    if(__builtin_setjmp(jump_buffer)==0)
        return root(x,callback,uint64_t(&original_service),output);
    return original_escape_value;
}
extern "C" Memory* sub_1001000000(State*,uint64_t,Memory*);
extern "C" Memory* sub_1001000100(State*,uint64_t,Memory*);
static void valid(Memory* m,uint64_t address,size_t n) {
    uint64_t lo=uint64_t(m->stack);
    if(address>=lo && address-lo<=m->stack_size && n<=m->stack_size-(address-lo))return;
    lo=uint64_t(m->output);
    if(address>=lo && address-lo<=16 && n<=16-(address-lo))return;
    std::fprintf(stderr,"unmapped access pc=0x%llx width=%zu\n",address,n);std::exit(3);
}
extern "C" uint64_t __remill_read_memory_64(Memory*m,uint64_t a) {
    valid(m,a,8);uint64_t v;std::memcpy(&v,(void*)a,8);return v;
}
extern "C" Memory* __remill_write_memory_64(Memory*m,uint64_t a,uint64_t v) {
    valid(m,a,8);std::memcpy((void*)a,&v,8);return m;
}
extern "C" bool __remill_flag_computation_zero(bool b,...){return b;}
extern "C" bool __remill_flag_computation_sign(bool b,...){return b;}
extern "C" bool __remill_flag_computation_carry(bool b,...){return b;}
extern "C" bool __remill_flag_computation_overflow(bool b,...){return b;}
extern "C" bool __remill_compare_slt(bool b){return b;}
extern "C" bool __remill_compare_sge(bool b){return b;}
extern "C" uint8_t __remill_undefined_8(){return 0;}
extern "C" bool __bb_is_nonlocal(Memory*m){return m->nonlocal;}
extern "C" Memory* __remill_error(State*s,uint64_t pc,Memory*) {
    std::fprintf(stderr,"explicit error pc=0x%llx caller=0x%llx\n",pc,s->gpr.rip.qword);std::exit(5);
}
extern "C" Memory* __remill_function_return(State*s,uint64_t pc,Memory*m) {
    s->gpr.rip.qword=pc;m->returned_pc=pc;return m;
}
static void native_service(State*s,Memory*m) {
    event(m,1);
    int64_t x=s->gpr.rdi.qword;
    s->gpr.rdi.qword=uint64_t(x+3);
    s->gpr.rsi.qword=ESCAPE;
    s->gpr.rdx.qword=uint64_t(m->output+1);
    s->gpr.rsp.qword-=8;
    __remill_write_memory_64(m,s->gpr.rsp.qword,CALLBACK_RETURN);
    sub_1001000100(s,CALLBACK_PC,m);
    if(m->nonlocal)return;
    if(m->returned_pc!=CALLBACK_RETURN)fail("callback logical return");
    event(m,2);
    s->gpr.rax.qword+=5;
}
extern "C" Memory* __remill_function_call(State*s,uint64_t pc,Memory*m) {
    if(pc==ESCAPE) {
        event(m,3);
        m->escape_value=s->gpr.rdi.qword^0x55aa55aa55aa55aaULL;
        m->nonlocal=true;
        // Restore the explicit outer logical context; no host exception crosses LLVM nounwind.
        *s=m->saved;
        s->gpr.rax.qword=m->escape_value;
        s->gpr.rsp.qword+=8;
        s->gpr.rip.qword=TOP_RETURN;
        m->returned_pc=TOP_RETURN;
        return m;
    }
    if(pc!=SERVICE) {
        uint64_t caller=__remill_read_memory_64(m,s->gpr.rsp.qword)-2; // authored call rdx is 2 bytes
        std::fprintf(stderr,"unknown target=0x%llx caller=0x%llx module_sha256=%s rsp=0x%llx rax=0x%llx rbx=0x%llx fixture=authored-control\n",
                     pc,caller,FIXTURE_SHA256,s->gpr.rsp.qword,s->gpr.rax.qword,s->gpr.rbx.qword);
        std::exit(4);
    }
    native_service(s,m);
    if(m->nonlocal)return m;
    uint64_t ret=__remill_read_memory_64(m,s->gpr.rsp.qword);
    s->gpr.rsp.qword+=8;s->gpr.rip.qword=ret;
    return m;
}
static void protect(void* p,DWORD prot) {
    DWORD old;if(!VirtualProtect(p,0x10000,prot,&old))fail("protect");
    MEMORY_BASIC_INFORMATION mbi{};
    if(!VirtualQuery(p,&mbi,sizeof(mbi)) || mbi.Protect!=prot)fail("protection verification");
}
static void load(uint8_t* dst,const std::string& path) {
    std::ifstream f(path,std::ios::binary);
    std::vector<char>b((std::istreambuf_iterator<char>(f)),{});
    if(b.empty() || b.size()>128)fail("fixture bytes");
    std::memcpy(dst,b.data(),b.size());
}
int main(int argc,char**argv) {
    AddVectoredExceptionHandler(1,DiagnosticException);
    if(argc<2)fail("fixture folder");
    bool unknown=argc>2 && std::string(argv[2])=="--unknown";
    bool negative_only=argc>2 && std::string(argv[2])=="--negative-only";
    auto* code=(uint8_t*)VirtualAlloc((void*)BASE,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    auto* stack=(uint8_t*)VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
    if(uint64_t(code)!=BASE || !stack)fail("allocation");
    load(code,std::string(argv[1])+"/root/original.bin");
    load(code+0x100,std::string(argv[1])+"/callback/original.bin");
    FlushInstructionCache(GetCurrentProcess(),code,0x10000);
    auto root=(Root)code;auto callback=(Callback)(code+0x100);
    unsigned normal=0,escaped=0;
    for(int id=0;id<512;++id) {
        active_case=id;phase="original";
        int64_t x=id%2 ? -1000-id : id;
        if(negative_only)x=-1000-id;
        uint64_t reference[2]={0xcafebabe,0x12345678};
        uint64_t actual[2]={reference[0],reference[1]};
        uint64_t result=0;
        original_marker=&reference[1];original_count=0;
        protect(code,PAGE_EXECUTE_READ);
        result=original_run(root,x,callback,&reference[0]);
        std::memset(stack,0xa5,0x10000);
        State s{};
        s.gpr.rdi.qword=uint64_t(x);s.gpr.rsi.qword=CALLBACK_PC;
        s.gpr.rdx.qword=unknown?0xbadf00d:SERVICE;s.gpr.rcx.qword=uint64_t(actual);
        s.gpr.rbx.qword=BASE;s.gpr.rsp.qword=uint64_t(stack+0x8000-8);
        s.gpr.rip.qword=BASE;
        Memory m{stack,0x10000,actual};m.saved=s;
        __remill_write_memory_64(&m,s.gpr.rsp.qword,TOP_RETURN);
        phase="aot";
        protect(code,PAGE_READONLY);
        sub_1001000000(&s,BASE,&m);
        uint64_t expected=x>=0?uint64_t((x+3)*3+12):(uint64_t(x+3)^0x55aa55aa55aa55aaULL);
        if(s.gpr.rax.qword!=result || result!=expected)fail("return value");
        if(std::memcmp(reference,actual,sizeof(actual)))fail("ordered guest writes / skipped suffix");
        if(m.event_count!=original_count || std::memcmp(m.events,original_events,m.event_count*sizeof(unsigned)))
            fail("service event order");
        if(s.gpr.rbx.qword!=m.saved.gpr.rbx.qword || s.gpr.rsp.qword!=m.saved.gpr.rsp.qword+8 ||
           s.gpr.rip.qword!=TOP_RETURN)fail("logical outer context");
        if(m.nonlocal!=(x<0))fail("nonlocal token");
        if(x<0)++escaped;else ++normal;
    }
    std::printf("{\"normal_callbacks\":%u,\"nonlocal_callbacks\":%u,\"original_code_NX_during_aot\":true,\"contract\":\"authored ABI return, ordered services, guest output writes, preserved RBX, logical RSP/RIP; private native stack and caller-clobbered registers excluded\"}\n",normal,escaped);
}
