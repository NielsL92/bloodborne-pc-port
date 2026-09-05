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
int main(int argc,char** argv) {
 if(argc<3)fail("supply fixture directory and RVA");
 auto rva=std::strtoull(argv[2],nullptr,16);auto translated=lookup(0x100000000+rva);if(!translated)fail("unknown entry");
 auto code=static_cast<uint8_t*>(VirtualAlloc(reinterpret_cast<void*>(0x100000000ULL),0x100000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 auto arena=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x100000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 auto stack=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 if(!code||!arena||!stack)fail("allocations");
 for(auto addr:{0x2550,0x65d0,0xb820,0x2fa30,0x3df50,0x3240,0x5e4e0,0x77e80,0x2b2b0}) {
  char name[64];std::snprintf(name,sizeof(name),"/%x/original.bin",addr);
  std::ifstream f(std::string(argv[1])+name,std::ios::binary);std::vector<uint8_t> data((std::istreambuf_iterator<char>(f)),{});
  if(data.empty())fail("fixture file absent");std::memcpy(code+addr,data.data(),data.size());
 }
 FlushInstructionCache(GetCurrentProcess(),code,0x100000);
 unsigned passed=0,failed=0,total_calls=0;
 for(int id=0;id<1024;++id) {
  int length=id%9,variant=(id/9)%16;
  std::memset(arena,0x5a,0x100000);std::memset(stack,0xcc,0x10000);
  CpuFrame input{};
  for(int i=0;i<16;++i) {
   input.gpr[i]=0x9abcde0012340000ULL+id*4096+i;
   for(int j=0;j<32;++j)input.ymm[i][j]=uint8_t(i*17+j+id);
  }
  input.gpr[5]=uint64_t(arena);input.gpr[4]=variant&1;
  input.gpr[7]=uint64_t(stack+0x8000-8);input.flags=0xad7;input.mxcsr=0x1f80;
  put(stack,0x8000-8,uint64_t(&oracle_return));
  uint64_t flag_mask=0xcc5;unsigned expected_calls=0;
  uint64_t expected_hash=0;
  if(rva==0x2550) {
   // The page's slot index is exactly zero: (page+0x38 - (page+0x38))/56.
   for(int i=0;i<=length;++i) {
    auto node=arena+i*0x100;auto page=arena+0x10000+i*0x1000;auto owner=arena+0x30000+i*0x100;
    put(node,0x48,((variant&2)&&i==0)?uint64_t(0):uint64_t(page+0x38));
    put(page,0x20,uint64_t(owner));put(owner,0x28,uint64_t(owner+0x60));
    put(owner+0x60,0xb,uint8_t(((id+i)%3==0)?2:0));
    put(node,0x38,i==length?uint64_t(0):uint64_t(node+0x100));
   }
  } else if(rva==0x65d0) {
   input.gpr[4]=uint64_t(arena);input.gpr[5]=uint64_t(arena+((variant&1)?length/2+1:20)*0x100);
   for(int i=0;i<=length;++i)put(arena+i*0x100,0x38,i==length?uint64_t(0):uint64_t(arena+(i+1)*0x100));
   if((variant&1)&&length)flag_mask|=0x10;
  } else if(rva==0xb820) {
   put(arena,0x10,(variant==15)?uint64_t(0):uint64_t(arena+0x100));
   put(arena+0x100,0,uint64_t(arena+0x1000));put(arena+0x100,8,uint64_t(length));
   bool all=true;
   for(int i=0;i<length;++i) {
    auto obj=arena+0x2000+i*0x400;put(arena+0x1000,i*8,uint64_t(obj));put(obj,0x40,uint64_t(obj+0x100));
    int value=(variant&1)&&i==length/2 ? -id : 2+id;put(obj+0x100,0xe4,int32_t(value));if(value<=1)all=false;
   }
   if(variant!=15&&all)flag_mask|=0x10;
  } else if(rva==0x2fa30) {
   auto text=arena+0x1000;put(arena,0x18,uint64_t(text)|(variant&3));put(text,0,uint64_t(length)|((variant&4)?0x8000000000000000ULL:0));
   put(arena,0xc,uint32_t(id*31));expected_hash=0x1505;
   for(int i=0;i<length;++i)text[0xc+i]=uint8_t(id*17+i);
   for(int i=length;i>0;--i)expected_hash=(expected_hash*33)^text[0xc+i-1];
   expected_hash^=uint32_t(id*31);expected_calls=1;
  } else if(rva==0x3df50) {
   put(arena,0,uint64_t(arena+0x1000));put(arena,8,uint64_t(length));
   input.gpr[4]=uint64_t(arena+((variant&1)?0x20:0x80));put(reinterpret_cast<uint8_t*>(input.gpr[4]),0,uint32_t(id*713));
   for(int i=0;i<length;++i) {
    auto obj=arena+0x2000+i*0x1000;auto dst=obj+0x400;
    put(arena+0x1000,i*0x10,uint64_t(obj));
    bool active=((variant+i)%3)!=0;put(obj,0x178,active?uint64_t(dst):0);
    put(dst,0,uint64_t(obj+0x800));put(dst,8,uint64_t((id+i)%5));
    if(active)++expected_calls;
   }
   if(length)flag_mask|=0x10;
  } else if(rva==0x3240) {
   input.gpr[5]=length?uint64_t(arena):0;flag_mask|=0x10;
   auto vtable=arena+0x90000;put(vtable,0x80,uint64_t(code+0x2b2b0));
   bool stopped=false;
   for(int i=0;i<length;++i) {
    auto node=arena+i*0x6000;put(node,0,uint64_t(vtable));put(node,0x38,i==length-1?uint64_t(0):uint64_t(node+0x6000));
    int value=(variant&1)&&i==length/2?3:2;put(node,0x5488,int32_t(value));
    if(!stopped)++expected_calls;if(value>2)stopped=true;
   }
  }
  std::vector<uint8_t> initial_arena(arena,arena+0x100000),initial_stack(stack,stack+0x10000);
  CpuFrame original=input;protect(code,PAGE_EXECUTE_READ);oracle_enter(&original,code+rva);
  std::vector<uint8_t> oracle_arena(arena,arena+0x100000),oracle_stack(stack,stack+0x10000);
  std::memcpy(arena,initial_arena.data(),0x100000);std::memcpy(stack,initial_stack.data(),0x10000);
  protect(code,PAGE_READONLY);MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(code,&mbi,sizeof(mbi));if(mbi.Protect!=PAGE_READONLY)fail("original code not NX");
  State state;to_state(input,state);
  Memory memory{{{uint64_t(arena),0x100000},{uint64_t(stack),0x10000},{uint64_t(code),0x100000}},0};
  calls=0;completed_calls=0;auto result=translated(&state,0x100000000+rva,&memory);total_calls+=calls;
  const char* issue=nullptr;int detail=-1;uint64_t got=0,want=0;
  if(result!=&memory||memory.returned_pc!=uint64_t(&oracle_return)||state.gpr.rip.qword!=uint64_t(&oracle_return))issue="return";
  if(!issue&&completed_calls!=expected_calls){issue="completed_call_count";got=completed_calls;want=expected_calls;}
  if(!issue&&rva==0x2fa30&&(original.gpr[0]!=expected_hash||state.gpr.rax.qword!=expected_hash))issue="independent_hash";
  for(int i=0;i<16&&!issue;++i)if(*state_reg(state,i)!=original.gpr[i]){issue="gpr";detail=i;got=*state_reg(state,i);want=original.gpr[i];}
  if(!issue&&((flags(state)^original.flags)&flag_mask)){issue="flags";got=flags(state)&flag_mask;want=original.flags&flag_mask;}
  for(int i=0;i<16&&!issue;++i)if(std::memcmp(&state.vec[i],original.ymm[i],32)){issue="ymm";detail=i;}
  if(!issue&&state.x87.fxsave64.mxcsr.flat!=original.mxcsr)issue="mxcsr";
  if(!issue&&std::memcmp(arena,oracle_arena.data(),0x100000))issue="arena";
  if(!issue&&std::memcmp(stack,oracle_stack.data(),0x10000))issue="stack";
  if(issue){++failed;if(failed<=20)std::printf("{\"effect\":\"%s\",\"case\":%d,\"detail\":%d,\"got\":\"0x%llx\",\"expected\":\"0x%llx\"}\n",issue,id,detail,got,want);}else ++passed;
 }
 std::printf("{\"rva\":\"0x%llx\",\"passed\":%u,\"failed\":%u,\"native_dispatch_calls\":%u,\"original_code_NX_during_aot\":true}\n",rva,passed,failed,total_calls);
 return failed?1:0;
}
