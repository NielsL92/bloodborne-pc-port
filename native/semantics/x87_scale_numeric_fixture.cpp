// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstddef>
#include <initializer_list>
#include <vector>
#include "x87_numeric.h"
#define SOFTFLOAT_FAST_INT64
#define LITTLEENDIAN 1
#define THREAD_LOCAL thread_local
extern "C" {
#include <softfloat.h>
}
extern "C" void save_host(void*);
static_assert(sizeof(BBX87ArithmeticResult)==16 && offsetof(BBX87ArithmeticResult,sign_exponent)==8 && offsetof(BBX87ArithmeticResult,flags)==10 && offsetof(BBX87ArithmeticResult,rounded_up)==11 && offsetof(BBX87ArithmeticResult,unsupported)==12,"arithmetic ABI");
static uint64_t counts[5]{},bad[5]{},reserved[5]{};
using Hardware=void(*)(const void*,void*,void*);
#include "entries.h"
static void put16(void* p,uint16_t x){std::memcpy(p,&x,2);}static void put64(void* p,uint64_t x){std::memcpy(p,&x,8);}static uint16_t get16(const void* p){uint16_t x;std::memcpy(&x,p,2);return x;}static uint64_t get64(const void* p){uint64_t x;std::memcpy(&x,p,8);return x;}
struct Value{uint64_t sig;uint16_t exp;};
static const Value values[]={{0,0},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x7fff},{0xc000000000000123ULL,0x7fff},{0x8000000000000123ULL,0x7fff},{1,0},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,0},{0x1234,0x3fff},{0,0x7fff},{0xffffffffffffffffULL,0x7ffe},{0x8000000000000001ULL,0x3fff},{0x8000000000000000ULL,0x3fe7},{0x8000000000000000ULL,0x3fca},{0x8000000000000000ULL,0x3fbf},{0x8000000000000000ULL,1},{0x8000000000000001ULL,1},{0xffffffffffffffffULL,1},{0x8000000000000000ULL,0x7ffe},{0xc000000000000000ULL,0x7ffe},{0x8000000000000000ULL,0x3ffe},{0xc000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x5fff},{0x8000000000000000ULL,0x1fff}};
static void check(unsigned form,unsigned type,unsigned pair,unsigned signs,Value a,Value b,uint16_t cw,unsigned c1){unsigned precision=(cw>>8)&3;
  alignas(16) uint8_t input[512]{},output[512]{},saved[512];put16(input,cw);put16(input+2,uint16_t(c1<<9));input[4]=3;uint32_t csr=0x1f80;std::memcpy(input+24,&csr,4);put64(input+32,a.sig);put16(input+40,a.exp);put64(input+48,b.sig);put16(input+56,b.exp);hardware[form](input,output,saved);
  BBX87ArithmeticResult actual{};softfloat_roundingMode=4;softfloat_detectTininess=0;extF80_roundingPrecision=32;softfloat_exceptionFlags=31;alignas(16) uint8_t before[512],after[512];save_host(before);
  __bb_x87_scale(a.sig,a.exp,b.sig,b.exp,cw,&actual);save_host(after);
  bool scope=softfloat_roundingMode!=4||softfloat_detectTininess!=0||extF80_roundingPrecision!=32||softfloat_exceptionFlags!=31||std::memcmp(before,after,28)||std::memcmp(before+32,after+32,128);bool difference=scope;
  {
   difference|=actual.unsupported!=0||actual.flags!=(get16(output+2)&63)||actual.rounded_up!=((get16(output+2)>>9)&1);
   if(!(get16(output+2)&~cw&3))difference|=actual.significand!=get64(output+32)||actual.sign_exponent!=get16(output+40);
  }
  ++counts[form];bad[form]+=difference;
  if(difference&&bad[form]<=8)std::fprintf(stderr,"form=%u type=%u pair=%u signs=%u cw=%x a=%llx:%x b=%llx:%x result=%llx:%x/%llx:%x flags=%x/%x c1=%u/%u unsupported=%u scope=%u\n",form,type,pair,signs,cw,(unsigned long long)a.sig,a.exp,(unsigned long long)b.sig,b.exp,(unsigned long long)actual.significand,actual.sign_exponent,(unsigned long long)get64(output+32),get16(output+40),actual.flags,get16(output+2)&63,actual.rounded_up,(get16(output+2)>>9)&1,actual.unsupported,unsigned(scope));
}
static Value integer_value(uint64_t n){if(!n)return {0,0};uint16_t exponent=0x403e;while(!(n>>63)){n<<=1;--exponent;}return {n,exponent};}
int main(){const unsigned masks[]={63,62,61,55,47,31,0,60};std::vector<Value> scales;
 for(unsigned n:{0u,1u,2u,63u,64u,16382u,16383u,16384u,24575u,24576u,24577u,32766u,32767u,32768u,49150u,49151u,65535u,65536u,131072u})scales.push_back(integer_value(n));
 for(unsigned i:{2u,3u,4u,5u,6u,7u,8u,9u,10u,11u,20u,21u})scales.push_back(values[i]);
 for(unsigned form=0;form<1;++form)for(unsigned type=0;type<sizeof(values)/sizeof(values[0]);++type)for(unsigned pair=0;pair<scales.size();++pair)for(unsigned signs=0;signs<4;++signs)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision=0;precision<4;++precision)for(unsigned c1=0;c1<2;++c1){
  auto a=values[type],b=scales[pair];a.exp|=uint16_t((signs&1)<<15);b.exp|=uint16_t((signs&2)<<14);
  check(form,type,pair,signs,a,b,uint16_t(0x40|mask|(precision<<8)|(rounding<<10)),c1);
 }
 for(unsigned exponent:{1u,2u,3u,0x3fffu,0x7ffeu})for(uint64_t sig:{0x8000000000000000ULL,0x8000000000000001ULL,0x8000000000000800ULL,0xfffffffffffffffeULL,0xffffffffffffffffULL})for(int target:{-24576,-24575,-64,-63,-1,0,1,0x7ffe,0x7fff,0xdffe,0xdfff})for(unsigned fraction=0;fraction<3;++fraction)for(unsigned sign=0;sign<2;++sign){
  int n=target-int(exponent);auto b=integer_value(unsigned(n<0?-n:n));if(fraction&&b.sig){if(fraction==1){if(b.sig==0x8000000000000000ULL){b.sig=UINT64_MAX;--b.exp;}else --b.sig;}else ++b.sig;}if(n<0)b.exp|=0x8000;Value a{sig,uint16_t(exponent|(sign<<15))};
  for(unsigned mask:masks)for(unsigned rc=0;rc<4;++rc)for(unsigned pc=0;pc<4;++pc)check(0,10000+exponent,unsigned(target),fraction,a,b,uint16_t(0x40|mask|(pc<<8)|(rc<<10)),1);
 }
 uint64_t seed=0x891370dbc21225a9ULL;auto next=[&](){seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return seed;};
 for(unsigned sample=0;sample<8192;++sample){Value a{next(),uint16_t(next())},b{next(),uint16_t(next())};if(sample>=4096){a.sig|=1ULL<<63;b.sig|=1ULL<<63;a.exp=uint16_t((a.exp&0x8000)|(sample%16==0?0:1+unsigned(next()%0x7ffe)));b.exp=uint16_t((b.exp&0x8000)|(1+unsigned(next()%0x7ffe)));}
  for(unsigned mask:masks)for(unsigned rc=0;rc<4;++rc)for(unsigned pc=0;pc<4;++pc)check(0,100000+sample,0,0,a,b,uint16_t(0x40|mask|(pc<<8)|(rc<<10)),1);
 }
 std::printf("{\"form\":0,\"cases\":%llu,\"differing_cases\":%llu,\"reserved_control_cases\":0}\n",(unsigned long long)counts[0],(unsigned long long)bad[0]);return 0;
}
