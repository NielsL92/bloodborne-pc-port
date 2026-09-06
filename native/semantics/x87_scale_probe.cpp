// SPDX-License-Identifier: Apache-2.0
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
using Hardware=void(*)(const void*,void*,void*);
#include "entries.h"
static void put16(void* p,uint16_t x){std::memcpy(p,&x,2);}static void put64(void* p,uint64_t x){std::memcpy(p,&x,8);}static uint16_t get16(const void* p){uint16_t x;std::memcpy(&x,p,2);return x;}static uint64_t get64(const void* p){uint64_t x;std::memcpy(&x,p,8);return x;}
struct Value{uint64_t sig;uint16_t exp;};
static const Value values[]={{0,0},{0x8000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x7fff},{0xc000000000000123ULL,0x7fff},{0x8000000000000123ULL,0x7fff},{1,0},{0x7fffffffffffffffULL,0},{0x8000000000000000ULL,0},{0x1234,0x3fff},{0,0x7fff},{0xffffffffffffffffULL,0x7ffe},{0x8000000000000001ULL,0x3fff},{0x8000000000000000ULL,0x3fe7},{0x8000000000000000ULL,0x3fca},{0x8000000000000000ULL,0x3fbf},{0x8000000000000000ULL,1},{0x8000000000000001ULL,1},{0xffffffffffffffffULL,1},{0x8000000000000000ULL,0x7ffe},{0xc000000000000000ULL,0x7ffe},{0x8000000000000000ULL,0x3ffe},{0xc000000000000000ULL,0x3fff},{0x8000000000000000ULL,0x5fff},{0x8000000000000000ULL,0x1fff}};
static Value integer_value(uint64_t n){if(!n)return {0,0};uint16_t exponent=0x403e;while(!(n>>63)){n<<=1;--exponent;}return {n,exponent};}
int main(){const unsigned masks[]={63,62,61,55,47,31,0,60};std::vector<Value> scales;
 for(unsigned n:{0u,1u,2u,63u,64u,16382u,16383u,16384u,24575u,24576u,24577u,32766u,32767u,32768u,49150u,49151u,65535u,65536u,131072u})scales.push_back(integer_value(n));
 for(unsigned i:{2u,3u,4u,5u,6u,7u,8u,9u,10u,11u,20u,21u})scales.push_back(values[i]);
 for(unsigned form=0;form<1;++form)for(unsigned type=0;type<sizeof(values)/sizeof(values[0]);++type)for(unsigned pair=0;pair<scales.size();++pair)for(unsigned signs=0;signs<4;++signs)for(unsigned mask:masks)for(unsigned rounding=0;rounding<4;++rounding)for(unsigned precision=0;precision<4;++precision)for(unsigned c1=0;c1<2;++c1){
  auto a=values[type],b=scales[pair];a.exp|=uint16_t((signs&1)<<15);b.exp|=uint16_t((signs&2)<<14);
  alignas(16) uint8_t input[512]{},output[512]{},saved[512];uint16_t cw=uint16_t(0x40|mask|(precision<<8)|(rounding<<10));put16(input,cw);put16(input+2,uint16_t(c1<<9));input[4]=3;uint32_t csr=0x1f80;std::memcpy(input+24,&csr,4);put64(input+32,a.sig);put16(input+40,a.exp);put64(input+48,b.sig);put16(input+56,b.exp);hardware[form](input,output,saved);
  std::printf("{\"form\":%u,\"type\":%u,\"pair\":%u,\"signs\":%u,\"control\":%u,\"input_c1\":%u,\"status\":%u,\"top\":%u,\"tags\":%u,\"sig0\":\"%llx\",\"exp0\":%u,\"sig1\":\"%llx\",\"exp1\":%u}\n",form,type,pair,signs,cw,c1,get16(output+2),(get16(output+2)>>11)&7,output[4],(unsigned long long)get64(output+32),get16(output+40),(unsigned long long)get64(output+48),get16(output+56));
 }
 return 0;
}
