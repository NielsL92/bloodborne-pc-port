// SPDX-License-Identifier: GPL-2.0-or-later
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <intrin.h>
using Hardware=void(*)(const void*,void*,void*,void*);
#include "pointer-entries.h"
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static uint64_t get64(const void* p){uint64_t v;std::memcpy(&v,p,8);return v;}
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}
static void put64(void* p,uint64_t v){std::memcpy(p,&v,8);}
int main(){int cpu[4];__cpuidex(cpu,7,0);std::printf("{\"cpuid7_ebx\":%u,\"fdp_exception_only\":%u,\"cs_ds_deprecated\":%u}\n",unsigned(cpu[1]),(unsigned(cpu[1])>>6)&1,(unsigned(cpu[1])>>13)&1);
 for(unsigned form=0;form<10;++form){uint64_t cases=0,updated[2]{},preserved[2]{},other[2]{},opcode_updated[2]{},opcode_preserved[2]{};
  for(unsigned top=0;top<8;++top)for(unsigned occupancy=0;occupancy<4;++occupancy)for(unsigned mask=0;mask<2;++mask)for(unsigned type=0;type<3;++type){
   alignas(16) uint8_t input[512]{},observed[512]{},saved[512],data[16]{};put16(input,uint16_t(mask?0x37e:0x37f));put16(input+2,uint16_t(top<<11));input[4]=uint8_t(occupancy==0?0:occupancy==1?255:1<<((top+occupancy-2)%8));put16(input+6,0x612);put64(input+8,0x12345678);put64(input+16,0x87654321);put32(input+24,0x1f80);
   uint64_t significand=type==0?0x8000000000000000ULL:type==1?0x8000000000000123ULL:1;uint16_t exponent=type==0?0x3fff:type==1?0x7fff:0;
   for(unsigned st=0;st<8;++st){put64(input+32+st*16,significand);put16(input+40+st*16,exponent);}
   if(form==0){put64(data,significand);put16(data+8,exponent);}else if(form==2||form==9)put32(data,type==0?0x3f800000:type==1?0x7f800123:1);else if(form==4)put64(data,type==0?1:type==1?0x8000000000000000ULL:0x7fffffffffffffffULL);else put64(data,type==0?0x3ff0000000000000ULL:type==1?0x7ff0000000000123ULL:1);
   hardware[form](input,observed,saved,data);unsigned exception=(get16(observed+2)>>7)&1;uint64_t dp=get64(observed+16);++cases;if(dp==uint64_t(data))++updated[exception];else if(dp==0x87654321)++preserved[exception];else ++other[exception];if(get16(observed+6)==0x612)++opcode_preserved[exception];else ++opcode_updated[exception];
  }
  std::printf("{\"form\":%u,\"cases\":%llu,\"dp_updated_no_unmasked_exception\":%llu,\"dp_updated_unmasked_exception\":%llu,\"dp_preserved_no_unmasked_exception\":%llu,\"dp_preserved_unmasked_exception\":%llu,\"dp_other_no_unmasked_exception\":%llu,\"dp_other_unmasked_exception\":%llu,\"fop_updated_no_unmasked_exception\":%llu,\"fop_updated_unmasked_exception\":%llu,\"fop_preserved_no_unmasked_exception\":%llu,\"fop_preserved_unmasked_exception\":%llu}\n",form,(unsigned long long)cases,(unsigned long long)updated[0],(unsigned long long)updated[1],(unsigned long long)preserved[0],(unsigned long long)preserved[1],(unsigned long long)other[0],(unsigned long long)other[1],(unsigned long long)opcode_updated[0],(unsigned long long)opcode_updated[1],(unsigned long long)opcode_preserved[0],(unsigned long long)opcode_preserved[1]);std::fflush(stdout);
 }return 0;}
