// SPDX-License-Identifier: GPL-2.0-or-later
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using Probe=void(*)(const void*,const void*,void*,void*);
#include "entries.h"
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static void put64(void* p,uint64_t v){std::memcpy(p,&v,8);}
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
int main(){
 const uint64_t sig[]={0,0x8000000000000000ULL,0x8000000000000123ULL,0xc000000000000123ULL,1,0x1234,0x8000000000000000ULL,0x8000000000000000ULL};
 const uint16_t exp[]={0,0x3fff,0x7fff,0x7fff,0,0x3fff,0,0x7fff};
 for(unsigned n=0;n<8;++n)for(unsigned mode=0;mode<4;++mode)for(unsigned flag=0;flag<32;++flag)for(unsigned a=0;a<8;++a)for(unsigned b=0;b<8;++b)for(unsigned c1=0;c1<2;++c1){
  alignas(16) uint8_t info[16]{},values[32]{},observed[544]{},saved[512]{};uint16_t cw=uint16_t(0x37f&~mode);unsigned flags=0x202|((flag&1)?1:0)|((flag&2)?4:0)|((flag&4)?0x40:0)|((flag&8)?0x810:0)|((flag&16)?0x80:0);
  put16(info,cw);put16(info+2,uint16_t(c1*0x200));put64(info+8,flags);put64(values,sig[a]);put16(values+8,exp[a]);put64(values+16,sig[b]);put16(values+24,exp[b]);probes[n](info,values,observed,saved);
  unsigned before=get16(observed+512)&0x8d5,after=get16(observed+520)&0x8d5;if(before!=(flags&0x8d5)||get16(observed)!=cw){std::fprintf(stderr,"initial flags/control mismatch\n");return 2;}
  std::printf("{\"c1\":%u,\"initial_status\":%u,\"form\":%u,\"mode\":%u,\"a\":%u,\"b\":%u,\"before\":%u,\"after\":%u,\"control\":%u,\"status\":%u,\"tags\":%u}\n",c1,get16(observed+528),n,mode,a,b,before,after,get16(observed),get16(observed+2),observed[4]);
 }
 return 0;
}
