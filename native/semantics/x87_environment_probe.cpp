// SPDX-License-Identifier: GPL-2.0-or-later
// Authored environment/tag import characterization; no game code or AOT claim.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <intrin.h>
extern "C" void probe_env(const void*,const void*,void*,void*);
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}
static uint16_t get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static void put64(void* p,uint64_t v){std::memcpy(p,&v,8);}
int main(){
 int cpu[4];__cpuid(cpu,0);char vendor[13]{};std::memcpy(vendor,cpu+1,4);std::memcpy(vendor+4,cpu+3,4);std::memcpy(vendor+8,cpu+2,4);__cpuid(cpu,1);
 std::printf("{\"kind\":\"host\",\"vendor\":\"%s\",\"signature\":%u}\n",vendor,unsigned(cpu[0]));
 const uint64_t significands[]={0x8000000000000000ULL,0,0x8000000000000000ULL,0xc000000000000123ULL,1,0x1234,0x8000000000000000ULL,0x8000000000000123ULL};
 const uint16_t exponents[]={0x3fff,0,0x7fff,0x7fff,0,0x3fff,0,0x7fff};
 const unsigned classes[]={0,1,2,2,2,2,2,2};
 for(unsigned rotation=0;rotation<4;++rotation)for(unsigned top=0;top<8;++top){
  uint64_t exact=0,reconstructed=0,occupancy_ok=0,control_ok=0,top_ok=0,payload_ok=0;unsigned first_input=0,first_output=0;bool found=false;
  for(unsigned tags=0;tags<65536;++tags){
   alignas(16) uint8_t initial[512]{},environment[32]{},observed[544]{},saved[512]{};
   put16(initial,0x37f);initial[4]=0xff;put16(initial+24,0x1f80);
   for(unsigned st=0;st<8;++st){unsigned type=(st+rotation)%8;put64(initial+32+st*16,significands[type]);put16(initial+40+st*16,exponents[type]);}
   put16(environment,0x37f);put16(environment+4,top<<11);put16(environment+8,uint16_t(tags));
   probe_env(initial,environment,observed,saved);
   unsigned actual=get16(observed+520),predicted=0,abridged=0;
   for(unsigned physical=0;physical<8;++physical){unsigned tag=(tags>>(physical*2))&3;predicted|=(tag==3?3:classes[(physical+rotation)%8])<<(physical*2);if(tag!=3)abridged|=1<<physical;}
   exact+=actual==tags;reconstructed+=actual==predicted;occupancy_ok+=observed[4]==abridged;control_ok+=get16(observed)==0x37f;top_ok+=((get16(observed+2)>>11)&7)==top;
   bool payload=true;
   for(unsigned logical=0;logical<8;++logical){unsigned physical=(top+logical)%8;if(abridged&(1<<physical))payload&=std::memcmp(observed+32+logical*16,initial+32+physical*16,10)==0;}
   payload_ok+=payload;
   if(actual!=tags&&!found){found=true;first_input=tags;first_output=actual;}
  }
  std::printf("{\"kind\":\"group\",\"rotation\":%u,\"top\":%u,\"cases\":65536,\"literal_full_tags\":%llu,\"reconstructed_full_tags\":%llu,\"abridged_tags\":%llu,\"control\":%llu,\"top_matches\":%llu,\"nonempty_payloads\":%llu,\"first_tag_difference\":[%u,%u]}\n",rotation,top,(unsigned long long)exact,(unsigned long long)reconstructed,(unsigned long long)occupancy_ok,(unsigned long long)control_ok,(unsigned long long)top_ok,(unsigned long long)payload_ok,first_input,first_output);
 }
 return 0;
}
