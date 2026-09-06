// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <xmmintrin.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
using Probe=void(*)(const void*,void*);
#include "probes.h"
struct Observation {DWORD code=0;unsigned csr=0;uint64_t pc=0;uint8_t fault_vector[16]{};};
static Observation observed;
static int capture(EXCEPTION_POINTERS* info){
 observed.code=info->ExceptionRecord->ExceptionCode;observed.csr=info->ContextRecord->MxCsr;observed.pc=info->ContextRecord->Rip;std::memcpy(observed.fault_vector,&info->ContextRecord->Xmm0,16);return EXCEPTION_EXECUTE_HANDLER;
}
__declspec(noinline) static void invoke(Probe probe,const void* in,void* out,unsigned control){
 observed={};_mm_setcsr(control);
 __try {probe(in,out);observed.csr=_mm_getcsr();}
 __except(capture(GetExceptionInformation())){}
 _mm_setcsr(0x1f80);
}
int main(){
 unsigned saved=_mm_getcsr();static const uint32_t singles[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0x3f7fffff,0x3f800001,0x7f7fffff,0xff7fffff};
 static const uint64_t doubles[]={0,0x8000000000000000ULL,1,0x8000000000000001ULL,0x000fffffffffffffULL,0x800fffffffffffffULL,0x0010000000000000ULL,0x8010000000000000ULL,0x3ff8000000000000ULL,0xbff8000000000000ULL,0x3fe0000000000000ULL,0xbfe0000000000000ULL,0x7ff0000000000000ULL,0xfff0000000000000ULL,0x7ff8000000000000ULL,0xfff8000000000000ULL,0x7ff0000000000001ULL,0xfff0000000000001ULL,0x7fffffffffffffffULL,0xffffffffffffffffULL,0x3fefffffffffffffULL,0x3ff0000000000001ULL,0x7fefffffffffffffULL,0xffefffffffffffffULL};
 static const unsigned masks[]={0x1f80,0,0x1f00,0x1e80,0xf80,0x1e00,0xe00,0x180};
 for(unsigned op=0;op<19;++op)for(unsigned setting=0;setting<128;++setting)for(unsigned test=0;test<32;++test){
  alignas(32) uint32_t input[12],output[4];for(auto& v:input)v=0xcccccccc;for(auto& v:output)v=0xeeeeeeee;
  if(op<3){for(unsigned lane=0;lane<4;++lane){input[lane]=singles[(test+lane)%24];input[4+lane]=singles[(test*7+lane*3)%24];}if(test>=24){input[0]=0x7fc00000;input[1]=1;input[2]=0x3f800000;input[3]=0x3f800000;for(unsigned lane=0;lane<4;++lane)input[4+lane]=0x3f800000;}}
  else{std::memcpy(input,doubles+(test+3)%24,8);std::memcpy(input+4,doubles+test%24,8);}
  unsigned control=masks[setting/16]|((setting%4)<<13)|((setting&4)?0x40:0)|((setting&8)?0x8000:0);if(test>=28)control|=0x3f;
  invoke(probes[op],input,output,control);
  if(observed.code&&(observed.pc!=uint64_t(sites[op])||std::memcmp(observed.fault_vector,input+8,16))){std::fprintf(stderr,"fault state mismatch op=%u setting=%u test=%u code=%lx csr=%x\n",op,setting,test,observed.code,observed.csr);return 2;}
  std::printf("{\"operation\":%u,\"test\":%u,\"control\":%u,\"code\":%lu,\"csr\":%u,\"input\":[%u,%u,%u,%u,%u,%u,%u,%u],\"output\":[%u,%u,%u,%u]}\n",op,test,control,observed.code,observed.csr,input[0],input[1],input[2],input[3],input[4],input[5],input[6],input[7],output[0],output[1],output[2],output[3]);
 }
 _mm_setcsr(saved);return 0;
}
