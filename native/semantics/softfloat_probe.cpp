// SPDX-License-Identifier: GPL-2.0-or-later
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <thread>
#include <atomic>
extern "C" {
#include <softfloat.h>
}
using Hardware=void(*)(const void*,void*,void*,void*);
#include "numeric-entries.h"
extern "C" void save_host(void*);extern "C" void restore_host(const void*);
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint64_t get64(const void* p){uint64_t v;std::memcpy(&v,p,8);return v;}
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static unsigned flags_to_x87(unsigned f){return ((f&16)>>4)|((f&8)>>1)|((f&4)<<1)|((f&2)<<3)|((f&1)<<5);}
static const extFloat80_t values[]={
 {0,0},{0,0x8000},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0xbfff},{0x8000000000000000ULL,0x4000},{0x8000000000000000ULL,0x3ffe},
 {0x8000000000000001ULL,0x3fff},{0xffffffffffffffffULL,0x3fff},{0x8000008000000000ULL,0x3fff},{0x8000000000000400ULL,0x3fff},
 {0x8000000000000000ULL,0x7fff},{0x8000000000000000ULL,0xffff},{0xc000000000000123ULL,0x7fff},{0xc000000000000123ULL,0xffff},{0x8000000000000123ULL,0x7fff},{0x8000000000000123ULL,0xffff},
 {1,0},{1,0x8000},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,1},{0xffffffffffffffffULL,0x7ffe},{0xffffffffffffffffULL,0xfffe},
 {0x8000000000000000ULL,0x3c01},{0xffffffffffffffffULL,0x3c00},{0x8000000000000000ULL,0x3f81},{0xffffffffffffffffULL,0x3f80},
 {0x8000000000000000ULL,0x403e},{0x8000000000000000ULL,0xc03e},{0xffffffffffffffffULL,0x403d},{0xffffffffffffffffULL,0xc03d},
 {0x8000000000000000ULL,0x3fe7},{0x8000000000000000ULL,0x3fca}
};
static const uint64_t memory_values[]={0,0x8000000000000000ULL,1,0xffffffffffffffffULL,0x3ff0000000000000ULL,0xbff0000000000000ULL,0x7ff0000000000000ULL,0xfff0000000000000ULL,0x7ff8000000000123ULL,0x7ff0000000000123ULL,0x0010000000000000ULL,0x000fffffffffffffULL,0x7fefffffffffffffULL,0x7fffffffffffffffULL,0x80000000,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc00123,0x7f800123,0x00800000,0x007fffff,0x7f7fffff};
static uint64_t counts[9]{},bad[9]{},result_bad[9]{},flag_bad[9]{},host_bad[9]{};
static const unsigned round_modes[]={softfloat_round_near_even,softfloat_round_min,softfloat_round_max,softfloat_round_minMag};
static void run_case(unsigned form,extFloat80_t a,extFloat80_t b,uint64_t memory,unsigned setting,const uint8_t* original){
 unsigned precision=setting%3,rounding=setting/3;const unsigned pc[]={0,2,3},bits[]={32,64,80};
 alignas(16) uint8_t input[512]{},observed[512]{},saved[512],before[512],after[512];uint64_t output=memory;
 put16(input,uint16_t(0x7f|(pc[precision]<<8)|(rounding<<10)));put16(input+2,0);input[4]=3;uint32_t mxcsr=0x5f80;std::memcpy(input+24,&mxcsr,4);std::memcpy(input+32,&a.signif,8);put16(input+40,a.signExp);std::memcpy(input+48,&b.signif,8);put16(input+56,b.signExp);
 hardware[form](input,observed,saved,&output);restore_host(original);save_host(before);
 softfloat_roundingMode=round_modes[rounding];softfloat_detectTininess=softfloat_tininess_afterRounding;extF80_roundingPrecision=bits[precision];softfloat_exceptionFlags=0;extFloat80_t result{};uint64_t scalar=0;
 if(form==0)result=f32_to_extF80({uint32_t(memory)});
 else if(form==1)result=f64_to_extF80({memory});
 else if(form==2){int64_t integer;std::memcpy(&integer,&memory,8);result=i64_to_extF80(integer);}
 else if(form==3)scalar=extF80_to_f32(a).v;
 else if(form==4)scalar=extF80_to_f64(a).v;
 else if(form==5){auto integer=extF80_to_i64_r_minMag(a,true);std::memcpy(&scalar,&integer,8);}
 else if(form==6)result=extF80_add(b,a);
 else if(form==7)result=extF80_sub(b,a);
 else result=extF80_mul(b,a);
 unsigned soft_flags=flags_to_x87(softfloat_exceptionFlags);save_host(after);restore_host(original);
 bool rb=form<3||form>=6?result.signif!=get64(observed+32)||result.signExp!=get16(observed+40):form==3?uint32_t(scalar)!=uint32_t(output):scalar!=output;
 bool fb=soft_flags!=(get16(observed+2)&0x3d),hb=std::memcmp(before,after,28)||std::memcmp(before+32,after+32,128);++counts[form];bad[form]+=rb||fb||hb;result_bad[form]+=rb;flag_bad[form]+=fb;host_bad[form]+=hb;
 if((rb||fb||hb)&&bad[form]<=6)std::fprintf(stderr,"form=%u setting=%u a=%04x:%016llx b=%04x:%016llx mem=%llx result=%04x:%016llx hw=%04x:%016llx scalar=%llx hwscalar=%llx flags=%x/%x diff=%u,%u,%u\n",form,setting,a.signExp,(unsigned long long)a.signif,b.signExp,(unsigned long long)b.signif,(unsigned long long)memory,result.signExp,(unsigned long long)result.signif,get16(observed+40),(unsigned long long)get64(observed+32),(unsigned long long)scalar,(unsigned long long)output,soft_flags,get16(observed+2)&0x3d,unsigned(rb),unsigned(fb),unsigned(hb));
}
static uint64_t random_state=0x626c6f6f64626f72ULL;
static uint64_t next(){uint64_t x=random_state;x^=x<<13;x^=x>>7;x^=x<<17;return random_state=x;}
static extFloat80_t number(){uint16_t exp=uint16_t(next());uint64_t sig=next();if(exp&0x7fff)sig|=0x8000000000000000ULL;else sig&=0x7fffffffffffffffULL;return {sig,exp};}
int main(){alignas(16) uint8_t original[512];save_host(original);
 for(unsigned form=0;form<9;++form){
  if(form<3)for(uint64_t mem:memory_values)for(unsigned setting=0;setting<12;++setting)run_case(form,values[2],values[3],mem,setting,original);
  else if(form<6)for(auto a:values)for(unsigned setting=0;setting<12;++setting)run_case(form,a,values[2],0x5a5a5a5a5a5a5a5aULL,setting,original);
  else for(auto a:values)for(auto b:values)for(unsigned setting=0;setting<12;++setting)run_case(form,a,b,0,setting,original);
  for(unsigned i=0;i<4096;++i){auto a=number(),b=number();auto mem=next();for(unsigned setting=0;setting<12;++setting)run_case(form,a,b,mem,setting,original);}
  std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"result_differences\":%llu,\"IEEE_flag_differences\":%llu,\"host_state_differences\":%llu}\n",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)result_bad[form],(unsigned long long)flag_bad[form],(unsigned long long)host_bad[form]);std::fflush(stdout);
 }
 // Independent expected constants test TLS state under concurrent numeric calls.
 std::atomic<unsigned> ready{0};std::atomic<bool> go{false};uint64_t thread_bad[4]{};std::thread workers[4];
 for(unsigned id=0;id<4;++id)workers[id]=std::thread([&,id]{++ready;while(!go.load())std::this_thread::yield();for(unsigned i=0;i<65536;++i){softfloat_roundingMode=round_modes[id];softfloat_exceptionFlags=0;extF80_roundingPrecision=32;softfloat_detectTininess=id&1;auto result=extF80_add(values[2],values[30]);uint64_t expected=id==2?0x8000010000000000ULL:0x8000000000000000ULL;thread_bad[id]+=result.signExp!=0x3fff||result.signif!=expected||softfloat_exceptionFlags!=softfloat_flag_inexact||softfloat_roundingMode!=round_modes[id]||softfloat_detectTininess!=(id&1);}});
 while(ready.load()!=4)std::this_thread::yield();go=true;for(auto& t:workers)t.join();uint64_t total=0;for(auto v:thread_bad)total+=v;
 std::printf("{\"form\":\"thread-local-controls\",\"cases\":262144,\"differing_cases\":%llu}\n",(unsigned long long)total);restore_host(original);return 0;
}
