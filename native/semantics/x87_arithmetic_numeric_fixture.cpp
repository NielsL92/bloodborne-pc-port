// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstddef>
#include <initializer_list>
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
static const Value values[]={{0,0},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x7fff},{0xc000000000000123ULL,0x7fff},{0x8000000000000123ULL,0x7fff},{1,0},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,0},{0x1234,0x3fff},{0,0x7fff},{0xffffffffffffffffULL,0x7ffe},{0x8000000000000001ULL,0x3fff},{0x8000000000000000ULL,0x3fe7},{0x8000000000000000ULL,0x3fca},{0x8000000000000000ULL,0x3fbf},{0x8000000000000000ULL,1},{0x8000000000000001ULL,1},{0xffffffffffffffffULL,1},{0x8000000000000000ULL,0x7ffe},{0xc000000000000000ULL,0x7ffe},{0x8000000000000000ULL,0x3ffe},{0xc000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x5fff},{0x8000000000000000ULL,0x1fff},{0xc000000000000000ULL,0x7fff},{0xffffffffffffffffULL,0x7fff},{0xc000000000000124ULL,0x7fff},{0x8000000000000001ULL,0x7fff},{0xbfffffffffffffffULL,0x7fff},{0x8000000000000124ULL,0x7fff}};
static void check(unsigned form,unsigned type,unsigned pair,unsigned signs,Value a,Value b,uint16_t cw,unsigned c1){unsigned precision=(cw>>8)&3;
  alignas(16) uint8_t input[512]{},output[512]{},saved[512];put16(input,cw);put16(input+2,uint16_t(c1<<9));input[4]=3;uint32_t csr=0x1f80;std::memcpy(input+24,&csr,4);put64(input+32,a.sig);put16(input+40,a.exp);put64(input+48,b.sig);put16(input+56,b.exp);hardware[form](input,output,saved);
  BBX87ArithmeticResult actual{};softfloat_roundingMode=4;softfloat_detectTininess=0;extF80_roundingPrecision=32;softfloat_exceptionFlags=31;alignas(16) uint8_t before[512],after[512];save_host(before);
  if(form==0)__bb_x87_add(b.sig,b.exp,a.sig,a.exp,cw,&actual);else if(form==1)__bb_x87_sub(b.sig,b.exp,a.sig,a.exp,cw,&actual);else if(form<4)__bb_x87_sub(a.sig,a.exp,b.sig,b.exp,cw,&actual);else __bb_x87_mul(a.sig,a.exp,b.sig,b.exp,cw,&actual);save_host(after);
  bool scope=softfloat_roundingMode!=4||softfloat_detectTininess!=0||extF80_roundingPrecision!=32||softfloat_exceptionFlags!=31||std::memcmp(before,after,28)||std::memcmp(before+32,after+32,128);bool difference=scope;
  if(precision==1){++reserved[form];difference|=actual.unsupported!=1;}else{
   difference|=actual.unsupported!=0||actual.flags!=(get16(output+2)&63)||actual.rounded_up!=((get16(output+2)>>9)&1);
   if(!(get16(output+2)&~cw&3))difference|=actual.significand!=get64(output+32)||actual.sign_exponent!=get16(output+40);
  }
  ++counts[form];bad[form]+=difference;
  if(difference&&bad[form]<=8)std::fprintf(stderr,"form=%u type=%u pair=%u signs=%u cw=%x a=%llx:%x b=%llx:%x result=%llx:%x/%llx:%x flags=%x/%x c1=%u/%u unsupported=%u scope=%u\n",form,type,pair,signs,cw,(unsigned long long)a.sig,a.exp,(unsigned long long)b.sig,b.exp,(unsigned long long)actual.significand,actual.sign_exponent,(unsigned long long)get64(output+32),get16(output+40),actual.flags,get16(output+2)&63,actual.rounded_up,(get16(output+2)>>9)&1,actual.unsupported,unsigned(scope));
}
static uint64_t random_state=0x7982def025913b7dULL;
static uint64_t random64(){random_state^=random_state<<13;random_state^=random_state>>7;random_state^=random_state<<17;return random_state;}
int main(){const unsigned masks[]={63,62,61,55,47,31,0,60};
 for(unsigned form=0;form<5;++form)for(unsigned type=0;type<sizeof(values)/sizeof(values[0]);++type)for(unsigned pair=0;pair<4;++pair)for(unsigned signs=0;signs<4;++signs)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision=0;precision<4;++precision)for(unsigned c1=0;c1<2;++c1){
  auto a=values[type],b=values[pair==0?1:pair==1?type:pair==2?15:18];a.exp|=uint16_t((signs&1)<<15);b.exp|=uint16_t((signs&2)<<14);
  check(form,type,pair,signs,a,b,uint16_t(0x40|mask|(precision<<8)|(rounding<<10)),c1);
 }
 // Cross all special values, including both NaN payload orderings.
 for(unsigned type=0;type<sizeof(values)/sizeof(values[0]);++type)for(unsigned pair=0;pair<sizeof(values)/sizeof(values[0]);++pair)for(unsigned signs=0;signs<4;++signs)for(unsigned form=0;form<5;++form)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision:{0u,2u,3u}){
  auto a=values[type],b=values[pair];a.exp|=uint16_t((signs&1)<<15);b.exp|=uint16_t((signs&2)<<14);check(form,100+type,pair,signs,a,b,uint16_t(0x40|mask|(precision<<8)|(rounding<<10)),1);
 }
 // Raw encodings and finite operands with close, extreme, and wide-gap exponents.
 for(unsigned sample=0;sample<8192;++sample){
  Value a{random64(),uint16_t(random64())},b{random64(),uint16_t(random64())};
  if(sample>=4096){a.sig|=1ULL<<63;b.sig|=1ULL<<63;unsigned exponent=1+unsigned(random64()%0x7ffe),other=1+unsigned(random64()%0x7ffe);switch(sample%8){case 0:exponent=1;other=1;break;case 1:exponent=0x7ffe;other=0x7ffe;break;case 2:other=exponent;break;case 3:exponent=0x7ffe;other=1;break;case 4:exponent=1;other=0x3ffe;break;case 5:exponent=1;other=0x4000;break;case 6:exponent=0x7ffe;other=0x3fff;break;default:break;}a.exp=uint16_t((a.exp&0x8000)|exponent);b.exp=uint16_t((b.exp&0x8000)|other);}
  for(unsigned form=0;form<5;++form)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision:{0u,2u,3u})check(form,1000+sample,0,0,a,b,uint16_t(0x40|mask|(precision<<8)|(rounding<<10)),1);
 }
 // Dense input tails at precision changes, cancellation and normal boundaries.
 unsigned edge=0;
 for(unsigned discard:{0u,11u,40u})for(unsigned exponent:{1u,2u,0x3ffeu,0x3fffu,0x7ffeu})for(unsigned upper=0;upper<3;++upper)for(unsigned low=0;low<6;++low)for(unsigned paired=0;paired<4;++paired)for(unsigned signs=0;signs<4;++signs){
  uint64_t unit=1ULL<<discard,half=unit>>1,tails[]={0,1,half?half-1:0,half,half+1,unit-1};uint64_t base=upper==0?0x8000000000000000ULL:upper==1?0x8000000000000000ULL+unit:~(unit-1);if(base>UINT64_MAX-tails[low])continue;
  Value a{base+tails[low],uint16_t(exponent|((signs&1)<<15))},b{0x8000000000000000ULL,uint16_t((paired==0?exponent:paired==1?1:paired==2?0x3ffe:0x4000)|((signs&2)<<14))};
  for(unsigned form=0;form<5;++form)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision:{0u,2u,3u})check(form,100000+edge,paired,signs,a,b,uint16_t(0x40|mask|(precision<<8)|(rounding<<10)),1);++edge;
 }
 for(unsigned form=0;form<5;++form)std::printf("{\"form\":%u,\"cases\":%llu,\"differing_cases\":%llu,\"reserved_control_cases\":%llu}\n",form,(unsigned long long)counts[form],(unsigned long long)bad[form],(unsigned long long)reserved[form]);return 0;
}
