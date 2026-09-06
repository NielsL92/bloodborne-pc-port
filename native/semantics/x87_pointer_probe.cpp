// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstring>
extern "C" void probe_pointer(const void*,unsigned,void*,void*);
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}static void put64(void* p,uint64_t v){std::memcpy(p,&v,8);}static uint64_t get64(const void* p){uint64_t v;std::memcpy(&v,p,8);return v;}
int main(){DWORD_PTR process_mask=0,system_mask=0;GetProcessAffinityMask(GetCurrentProcess(),&process_mask,&system_mask);DWORD_PTR single=process_mask&(~process_mask+1);
 for(unsigned pin=0;pin<2;++pin){DWORD_PTR previous=0;if(pin){previous=SetThreadAffinityMask(GetCurrentThread(),single);if(!previous)return 2;}
  for(unsigned pending=0;pending<2;++pending)for(unsigned slow=0;slow<2;++slow){unsigned iterations=slow?256:65536,changed=0,zero_upper=0,other=0;uint64_t first_ip=0,first_dp=0;
   for(unsigned i=0;i<iterations;++i){alignas(16) uint8_t input[512]{},output[512]{},saved[512]{};put16(input,pending?0x37e:0x37f);put16(input+2,pending?0x8081:0);put16(input+6,0x612);put64(input+8,0x00005678abcd1000ULL);put64(input+16,0x00006789def02000ULL);put32(input+24,0x1f80);
    probe_pointer(input,slow?500000:1,output,saved);auto ip=get64(output+8),dp=get64(output+16);bool different=ip!=get64(input+8)||dp!=get64(input+16);changed+=different;zero_upper+=different&&ip==uint32_t(get64(input+8))&&dp==uint32_t(get64(input+16));other+=different&&!(ip==uint32_t(get64(input+8))&&dp==uint32_t(get64(input+16)));if(different&&!first_ip){first_ip=ip;first_dp=dp;}
   }
   std::printf("{\"pinned\":%u,\"pending\":%u,\"delay_iterations\":%u,\"cases\":%u,\"changed\":%u,\"upper_halves_cleared\":%u,\"other_pointer_changes\":%u,\"first_ip\":%llu,\"first_dp\":%llu}\n",pin,pending,slow?500000:1,iterations,changed,zero_upper,other,(unsigned long long)first_ip,(unsigned long long)first_dp);std::fflush(stdout);
  }if(pin)SetThreadAffinityMask(GetCurrentThread(),previous);
 }return 0;
}
