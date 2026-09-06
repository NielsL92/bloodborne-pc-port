// SPDX-License-Identifier: GPL-2.0-or-later
#include "x87_environment.h"
#include <cstdio>
#include <cstring>
#include <cstdlib>
using namespace bb_x87;
extern "C" void probe_store(const void*,const void*,void*,void*);
extern "C" void probe_load(const void*,const void*,void*,void*);
extern "C" void probe_legacy(const void*,const void*,void*,void*);
extern "C" void probe_wide(const void*,const void*,void*,void*);
static uint64_t cases=0,differences=0,amd_policy_cases=0,host_pointer_loss_cases=0,full_pointer_hardware_matches=0;
static const uint64_t significands[]={0x8000000000000000ULL,0,0x8000000000000000ULL,0xc000000000000123ULL,1,0x1234,0x8000000000000000ULL,0x8000000000000123ULL};
static const uint16_t exponents[]={0x3fff,0,0x7fff,0x7fff,0,0x3fff,0,0x7fff};
static void check(bool ok,const char* name,unsigned top,unsigned tags,unsigned pattern,unsigned setting){++cases;if(!ok){++differences;if(differences<=12)std::fprintf(stderr,"%s top=%u tags=%x pattern=%u setting=%u\n",name,top,tags,pattern,setting);}}
static void input_state(State& s,uint8_t* initial,unsigned top,unsigned tags,unsigned pattern,unsigned setting,unsigned pending){
 std::memset(&s,0xa5,sizeof s);std::memset(initial,0,512);const unsigned precision[]={0,2,3};uint16_t cw=uint16_t(0x7f|(precision[setting%3]<<8)|((setting/3)<<10));if(pending)cw&=~1u;
 s.x87.fxsave.cwd.flat=cw;set_status(s,uint16_t((top<<11)|(pending?0x8081:0)));s.x87.fxsave.ftw.flat=uint8_t(tags);s.x87.fxsave.fop=0x612;s.x87.fxsave.ip=0x00005678abcd1000ULL+top;s.x87.fxsave.dp=0x00006789def02000ULL+top;s.x87.fxsave.mxcsr.flat=0x5f80;s.x87.fxsave.mxcsr_mask.flat=0xdeadbeef;
 std::memcpy(initial,&s.x87,32);initial[5]=0;write32(initial+28,0);
 for(unsigned st=0;st<8;++st){unsigned v=(st+pattern)%8;put_bits(s.st.elems[st].val,{significands[v],exponents[v]});std::memcpy(initial+32+16*st,&s.st.elems[st].val,10);}
 for(unsigned reg=0;reg<16;++reg){uint8_t value[16];for(unsigned i=0;i<16;++i)value[i]=uint8_t(reg*16+i+pattern+setting);std::memcpy(&s.vec[reg].xmm,value,16);std::memcpy(initial+160+reg*16,value,16);}
}
static void expect_load(State& expected,const uint8_t* hardware){
 expected.x87.fxsave.cwd.flat=read16(hardware);set_status(expected,read16(hardware+2));expected.x87.fxsave.ftw.flat=hardware[4];expected.x87.fxsave.fop=read16(hardware+6);std::memcpy(&expected.x87.fxsave.ip,hardware+8,8);std::memcpy(&expected.x87.fxsave.dp,hardware+16,8);
 for(unsigned st=0;st<8;++st)std::memcpy(&expected.st.elems[st].val,hardware+32+st*16,10);
}
int main(){
 const Profile intel{false,true,0xffff},amd{true,false,0xffff};const PointerSegments segments{0x43,0x4b};
 alignas(16) uint8_t initial[512],hardware[1040],saved[512],environment[32],output[544],prior[544];State s,expected,original;
 for(unsigned top=0;top<8;++top)for(unsigned tags=0;tags<256;++tags)for(unsigned pattern=0;pattern<8;++pattern)for(unsigned setting=0;setting<12;++setting){
  unsigned pending=(tags+pattern+setting)&1;input_state(s,initial,top,tags,pattern,setting,pending);original=s;std::memset(hardware,0xa5,sizeof hardware);std::memset(output,0xa5,sizeof output);probe_store(initial,environment,hardware,saved);store_environment28(s,segments,intel,output);expected=original;expected.x87.fxsave.cwd.flat=read16(hardware+32);set_status(expected,read16(hardware+34));check(!std::memcmp(output,hardware,32)&&!std::memcmp(&s,&expected,sizeof s),"store28",top,tags,pattern,setting);
  for(unsigned wide=0;wide<2;++wide){s=original;std::memset(hardware,0xa5,sizeof hardware);std::memset(output,0xa5,sizeof output);if(wide)probe_wide(initial,environment,hardware,saved);else probe_legacy(initial,environment,hardware,saved);save_fx(s,segments,intel,wide!=0,output);bool image_match=!std::memcmp(output,hardware,512);
   if(wide){uint64_t actual_ip,actual_dp,encoded_ip,encoded_dp;std::memcpy(&actual_ip,hardware+8,8);std::memcpy(&actual_dp,hardware+16,8);std::memcpy(&encoded_ip,output+8,8);std::memcpy(&encoded_dp,output+16,8);
    check(encoded_ip==s.x87.fxsave.ip&&encoded_dp==s.x87.fxsave.dp,"canonical-64-bit-pointers",top,tags,pattern,setting);
    if(actual_ip==encoded_ip&&actual_dp==encoded_dp)++full_pointer_hardware_matches;
    else if(actual_ip==uint32_t(encoded_ip)&&actual_dp==uint32_t(encoded_dp)){++host_pointer_loss_cases;image_match=true;for(unsigned offset=0;offset<512;++offset)if(!((offset>=12&&offset<16)||(offset>=20&&offset<24)))image_match&=output[offset]==hardware[offset];}
   }
   if(!image_match&&differences<12){std::fprintf(stderr,"save-fx bytes wide=%u:",wide);for(unsigned offset=0;offset<512;++offset)if(output[offset]!=hardware[offset])std::fprintf(stderr," %u:%02x/%02x",offset,output[offset],hardware[offset]);std::fprintf(stderr,"\n");}
   check(image_match&&!std::memcmp(&s,&original,sizeof s),"save-fx",top,tags,pattern,setting);}
  // Policy witness: all non-pointer fields equal the Intel image; ES=0 must
  // retain destination pointer bytes, while ES=1 writes explicit selectors.
  s=original;std::memset(prior,0x5a,sizeof prior);std::memcpy(output,prior,sizeof output);save_fx(s,segments,amd,false,output);bool policy=!std::memcmp(&s,&original,sizeof s)&&!std::memcmp(output+416,prior+416,128);
  if(!pending)policy&=!std::memcmp(output+6,prior+6,18);else policy&=read16(output+12)==segments.code&&read16(output+20)==segments.data&&read32(output+8)==uint32_t(s.x87.fxsave.ip)&&read32(output+16)==uint32_t(s.x87.fxsave.dp)&&read16(output+6)==s.x87.fxsave.fop;
  check(policy,"AMD-policy",top,tags,pattern,setting);++amd_policy_cases;
 }
 // Arbitrary full tags and TOP changes exercise physical-register occupancy,
 // rotation of raw payloads, and legacy pointer/opcode imports.
 for(unsigned top=0;top<8;++top)for(unsigned tags=0;tags<65536;++tags)for(unsigned pattern=0;pattern<4;++pattern){
  input_state(s,initial,top,255,pattern,0,0);original=s;std::memset(environment,0xa5,sizeof environment);write16(environment,0x37f);write16(environment+4,uint16_t(((top+pattern+1)%8)<<11));write16(environment+8,uint16_t(tags));write32(environment+12,0xabcdef12);write16(environment+16,0x43);write16(environment+18,0xffff);write32(environment+20,0xfedcba98);write16(environment+24,0x4b);
  probe_load(initial,environment,hardware,saved);auto loaded_segments=load_environment28(s,intel,environment);expected=original;expect_load(expected,hardware);check(!std::memcmp(&s,&expected,sizeof s)&&loaded_segments.code==0&&loaded_segments.data==0,"load28",top,tags,pattern,0);
  std::memset(output,0xa5,sizeof output);store_environment28(s,loaded_segments,intel,output);check(!std::memcmp(output,hardware+512,28),"load28-full-tags",top,tags,pattern,0);
 }
 // Every possible control word, including reserved precision/reserved bits.
 for(unsigned cw=0;cw<65536;++cw){input_state(s,initial,0,0,0,0,0);std::memset(environment,0,32);write16(environment,uint16_t(cw));write16(environment+8,0xffff);probe_load(initial,environment,hardware,saved);load_environment28(s,intel,environment);check(s.x87.fxsave.cwd.flat==read16(hardware),"control-normalization",0,0,0,cw);}
 std::printf("{\"checks\":%llu,\"differences\":%llu,\"stack_profile_inputs\":196608,\"full_tag_imports\":2097152,\"control_word_imports\":65536,\"AMD_policy_cases\":%llu,\"host_pointer_loss_cases\":%llu,\"full_pointer_hardware_matches\":%llu}\n",(unsigned long long)cases,(unsigned long long)differences,(unsigned long long)amd_policy_cases,(unsigned long long)host_pointer_loss_cases,(unsigned long long)full_pointer_hardware_matches);return 0;
}
