// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using Hardware=void(*)(const void*,void*,void*,void*);
#include "entries.h"
static void put16(void* p,uint16_t x){std::memcpy(p,&x,2);}static void put64(void* p,uint64_t x){std::memcpy(p,&x,8);}static uint16_t get16(const void* p){uint16_t x;std::memcpy(&x,p,2);return x;}static uint64_t get64(const void* p){uint64_t x;std::memcpy(&x,p,8);return x;}
struct Value{uint64_t sig;uint16_t exp;};
static const Value values[]={{0,0},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x7fff},{0xc000000000000123ULL,0x7fff},{0x8000000000000123ULL,0x7fff},{1,0},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,0},{0x1234,0x3fff},{0,0x7fff},{0x4000000000000000ULL,0x7fff},{0xffffffffffffffffULL,0x7ffe},{0x8000000000000001ULL,0x3fff},{0x8000000000000400ULL,0x3fff},{0x8000000000000401ULL,0x3fff},{0x8000008000000000ULL,0x3fff},{0x8000008000000001ULL,0x3fff},{0x8000000000000000ULL,0x3f81},{0x8000000000000000ULL,0x3f6a},{0x8000000000000000ULL,0x3f69},{0x8000000000000000ULL,0x3c01},{0x8000000000000000ULL,0x3bcd},{0x8000000000000000ULL,0x3bcc},{0x8000000000000000ULL,0x407e},{0x8000000000000000ULL,0x407f},{0x8000000000000000ULL,0x43fe},{0x8000000000000000ULL,0x43ff},{0x8000000000000000ULL,0x3ffe},{0xc000000000000000ULL,0x3fff},{0xffff000000000000ULL,0x400d},{0x8000000000000000ULL,0x400e},{0xffffffff00000000ULL,0x401d},{0x8000000000000000ULL,0x401e},{0xfffffffffffffffeULL,0x403d},{0x8000000000000000ULL,0x403e},{0x8000000000000001ULL,0x403e},{0xfffffe0000000000ULL,0x3f80},{0xfffffeffffffffffULL,0x3f80},{0xffffff0000000000ULL,0x3f80},{0xffffff0000000001ULL,0x3f80},{0xfffffffffffff000ULL,0x3c00},{0xfffffffffffff7ffULL,0x3c00},{0xfffffffffffff800ULL,0x3c00},{0xfffffffffffff801ULL,0x3c00}};
int main(){const unsigned masks[]={63,62,55,47,31,0,39,15};const unsigned widths[]={4,8,4,8,2,4,8};
 for(unsigned form=0;form<7;++form)for(unsigned type=0;type<sizeof(values)/sizeof(values[0]);++type)for(unsigned sign=0;sign<2;++sign)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned c1=0;c1<2;++c1)for(unsigned occupied=0;occupied<2;++occupied){
  alignas(16) uint8_t input[512]{},output[512]{},saved[512],data[32];std::memset(data,0xa5,sizeof data);uint16_t cw=uint16_t(0x340|mask|(rounding<<10));put16(input,cw);put16(input+2,uint16_t(c1<<9));input[4]=uint8_t(occupied);uint32_t csr=0x1f80;std::memcpy(input+24,&csr,4);put64(input+32,values[type].sig);put16(input+40,uint16_t(values[type].exp|(sign<<15)));hardware[form](input,output,saved,data+8);
  for(unsigned i=0;i<32;++i)if((i<8||i>=8+widths[form])&&data[i]!=0xa5){std::fprintf(stderr,"out-of-width write\n");return 2;}
  uint64_t bits=0;std::memcpy(&bits,data+8,widths[form]);uint64_t sentinel=widths[form]==2?0xa5a5:widths[form]==4?0xa5a5a5a5:0xa5a5a5a5a5a5a5a5ULL;
  std::printf("{\"form\":%u,\"type\":%u,\"sign\":%u,\"control\":%u,\"input_c1\":%u,\"occupied\":%u,\"status\":%u,\"top\":%u,\"tags\":%u,\"stored\":%s,\"bits\":\"%llx\"}\n",form,type,sign,cw,c1,occupied,get16(output+2),(get16(output+2)>>11)&7,output[4],bits!=sentinel?"true":"false",(unsigned long long)bits);
 }
 return 0;
}
