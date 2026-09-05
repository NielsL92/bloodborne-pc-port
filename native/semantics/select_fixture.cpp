// SPDX-License-Identifier: GPL-2.0-or-later
#include "vector_fixture.h"
static uint32_t get32(const uint8_t* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(uint8_t* p,uint32_t v){std::memcpy(p,&v,4);}
__declspec(noinline) static void reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec,unsigned op,unsigned imm){
 std::memcpy(out,m.vectors,sizeof out);const auto* a=m.vectors[1];const auto* b=spec.memory?m.backing+3:m.vectors[2];auto* dst=out[spec.destination];
 if(op==OP_VPSRLD||op==OP_VPSRAD){
  for(unsigned byte=0;byte<spec.width;byte+=4){uint32_t value=get32(b+byte),result=0;for(unsigned bit=0;bit<32;++bit){unsigned source=bit+imm;bool set=source<32?bool((value>>source)&1):(op==OP_VPSRAD&&bool(value&0x80000000));if(set)result|=uint32_t(1)<<bit;}put32(dst+byte,result);}
 }else if(op==OP_VPALIGNR){
  for(unsigned lane=0;lane<spec.width;lane+=16){uint8_t concat[48]{};std::memcpy(concat,b+lane,16);std::memcpy(concat+16,a+lane,16);if(imm>=32)std::memset(dst+lane,0,16);else std::memcpy(dst+lane,concat+imm,16);}
 }else if(op==OP_VSHUFPD){
  for(unsigned lane=0;lane<spec.width/16;++lane){unsigned left=(imm>>(2*lane))&1,right=(imm>>(2*lane+1))&1;std::memcpy(dst+16*lane,a+16*lane+8*left,8);std::memcpy(dst+16*lane+8,b+16*lane+8*right,8);}
 }else if(op==OP_VPERMILPD){
  for(unsigned lane=0;lane<spec.width/16;++lane)for(unsigned half=0;half<2;++half){unsigned choose=(imm>>(2*lane+half))&1;std::memcpy(dst+16*lane+8*half,b+16*lane+8*choose,8);}
 }else if(op==OP_VBLENDPS||op==OP_VBLENDPD){
  for(unsigned element=0;element<spec.width/spec.element_bytes;++element)std::memcpy(dst+element*spec.element_bytes,(((imm>>element)&1)?b:a)+element*spec.element_bytes,spec.element_bytes);
 }else fail("unknown reference operation");
 if(spec.width==16)std::memset(dst+16,0,16);
}
int main(){uint64_t cases=0;static const uint32_t edge[]={0,1,0x7fffffff,0x80000000,0xffffffff,0xaaaaaaaa,0x55555555,0x80000001};
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned trial=0;trial<32;++trial){
  const auto& spec=specs[form];Memory m{};State s;setup(m,s,spec);
  if(trial<8)for(unsigned word=0;word<8;++word){put32(m.vectors[1]+4*word,edge[(trial+word)%8]);put32(m.vectors[2]+4*word,edge[(trial+word+2)%8]);put32(m.backing+3+4*word,edge[(trial+word+5)%8]);}
  for(unsigned r=1;r<=2;++r)std::memcpy(&s.vec[r].ymm,m.vectors[r],32);
  Memory initial=m;State expected=s;alignas(32) uint8_t ref[4][32],observed[4][32];reference(ref,m,spec,operations[form],immediates[form]);std::memcpy(&expected.vec[spec.destination].ymm,ref[spec.destination],32);
  auto* result=lifted[form](&s,spec.pc,&m);hardware[form](m.vectors,observed,m.backing+3);
  if(std::memcmp(ref,observed,sizeof ref))fail("hardware/reference",form,trial,immediates[form]);compare(m,initial,s,expected,result,spec,form,trial,immediates[form]);++cases;
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":46,\"immediates\":256,\"operations\":7,\"game_code_execution\":false}\n",(unsigned long long)cases);
}
