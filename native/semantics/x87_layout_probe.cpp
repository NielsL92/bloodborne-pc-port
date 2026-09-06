// SPDX-License-Identifier: GPL-2.0-or-later
#include <cstdint>
#include <cstdio>
#include <cstring>
extern "C" void probe_store(const void*,const void*,void*,void*);
extern "C" void probe_load(const void*,const void*,void*,void*);
extern "C" void probe_legacy(const void*,const void*,void*,void*);
extern "C" void probe_control(const void*,const void*,void*,void*);
static void put16(void* p,uint16_t v){std::memcpy(p,&v,2);}static void put32(void* p,uint32_t v){std::memcpy(p,&v,4);}static void put64(void* p,uint64_t v){std::memcpy(p,&v,8);}static unsigned get16(const void* p){uint16_t v;std::memcpy(&v,p,2);return v;}
static void hex(const void* data,unsigned size){auto p=static_cast<const uint8_t*>(data);for(unsigned i=0;i<size;++i)std::printf("%02x",p[i]);}
int main(){
 alignas(16) uint8_t initial[512]{},env[32]{},observed[1040]{},saved[512]{};put16(initial,0x37f);put32(initial+24,0x1f80);
 unsigned control_match=0,environment_match=0,control_first=0,control_actual=0,env_first=0,env_actual=0;
 for(unsigned cw=0;cw<65536;++cw){put16(env,cw);probe_control(initial,env,observed,saved);unsigned want=(cw&0x1f3f)|0x40;control_match+=get16(observed)==want;if(get16(observed)!=want&&!control_actual){control_first=cw;control_actual=get16(observed);}probe_load(initial,env,observed,saved);environment_match+=get16(observed)==want;if(get16(observed)!=want&&!env_actual){env_first=cw;env_actual=get16(observed);}}
 std::printf("{\"kind\":\"control-normalization\",\"cases_per_form\":65536,\"fldcw_matches\":%u,\"fldenv_matches\":%u,\"prediction\":\"(input & 0x1f3f) | 0x40\",\"first_control_difference\":[%u,%u],\"first_environment_difference\":[%u,%u]}\n",control_match,environment_match,control_first,control_actual,env_first,env_actual);
 for(unsigned top=0;top<8;++top)for(unsigned mode=0;mode<4;++mode){
  std::memset(initial,0,sizeof initial);put16(initial,mode&1?0x37e:0x37f);put16(initial+2,uint16_t((top<<11)|(mode&1?0x8081:mode&2?0x41:0)));initial[4]=mode&2?0x55:0xff;put16(initial+6,0x612);put64(initial+8,0x12345678abcd1000ULL+top);put64(initial+16,0x23456789def02000ULL+top);put32(initial+24,0x5f80);
  for(unsigned st=0;st<8;++st){put64(initial+32+st*16,st?0x8000000000000000ULL+st:0);put16(initial+40+st*16,st?0x3fff:0);}
  for(unsigned i=160;i<416;++i)initial[i]=uint8_t(i+top+mode);
  std::memset(observed,0xa5,sizeof observed);probe_store(initial,env,observed,saved);std::printf("{\"kind\":\"store\",\"top\":%u,\"mode\":%u,\"input\":\"",top,mode);hex(initial,32);std::printf("\",\"environment\":\"");hex(observed,32);std::printf("\",\"post\":\"");hex(observed+32,32);std::printf("\"}\n");
  std::memset(observed,0xa5,sizeof observed);probe_legacy(initial,env,observed,saved);std::printf("{\"kind\":\"legacy\",\"top\":%u,\"mode\":%u,\"input\":\"",top,mode);hex(initial,416);std::printf("\",\"saved\":\"");hex(observed,512);std::printf("\",\"post\":\"");hex(observed+512,32);std::printf("\"}\n");
  // FLDENV must start without pending exceptions; its imported state may become pending.
  put16(initial,0x37f);put16(initial+2,uint16_t(top<<11));std::memset(env,0xa5,sizeof env);put16(env,mode&1?0x37e:0x37f);put16(env+4,uint16_t((((top+3)%8)<<11)|(mode&1?0x8081:0)));put16(env+8,0x1234);put32(env+12,0xabcdef12);put16(env+16,0x43);put16(env+18,0xffff);put32(env+20,0xfedcba98);put16(env+24,0x4b);
  std::memset(observed,0xa5,sizeof observed);probe_load(initial,env,observed,saved);std::printf("{\"kind\":\"load\",\"top\":%u,\"mode\":%u,\"environment\":\"",top,mode);hex(env,28);std::printf("\",\"loaded\":\"");hex(observed,160);std::printf("\",\"resaved\":\"");hex(observed+512,28);std::printf("\"}\n");
 }
 std::printf("{\"kind\":\"complete\"}\n");return 0;
}
