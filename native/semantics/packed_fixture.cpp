// SPDX-License-Identifier: GPL-2.0-or-later
#include "vector_fixture.h"
static uint32_t get32(const uint8_t* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(uint8_t* p,uint32_t v){std::memcpy(p,&v,4);}
static int64_t signed32(uint32_t v){return v&0x80000000U?int64_t(v)-0x100000000LL:int64_t(v);}
__declspec(noinline) static void reference(uint8_t (&out)[4][32],const Memory& m,const Spec& spec,unsigned op){
 std::memcpy(out,m.vectors,sizeof out);const auto* a=m.vectors[1];const auto* b=spec.memory?m.backing+3:m.vectors[2];auto* dst=out[spec.destination];
 if(op==OP_VPUNPCKLWD||op==OP_VPUNPCKLDQ||op==OP_VPUNPCKHQDQ){
  for(unsigned lane=0;lane<spec.width;lane+=16)for(unsigned elem=0;elem<8/spec.element_bytes;++elem){unsigned offset=lane+(op==OP_VPUNPCKHQDQ?8:0)+elem*spec.element_bytes;std::memcpy(dst+lane+2*elem*spec.element_bytes,a+offset,spec.element_bytes);std::memcpy(dst+lane+(2*elem+1)*spec.element_bytes,b+offset,spec.element_bytes);}
 }else if(op==OP_VPSHUFB){
  for(unsigned lane=0;lane<spec.width;lane+=16)for(unsigned byte=0;byte<16;++byte)dst[lane+byte]=b[lane+byte]>=128?0:a[lane+(b[lane+byte]%16)];
 }else if(op==OP_VPMULUDQ){
  for(unsigned byte=0;byte<spec.width;byte+=8){uint64_t product=uint64_t(get32(a+byte))*get32(b+byte);std::memcpy(dst+byte,&product,8);}
 }else for(unsigned byte=0;byte<spec.width;byte+=4){auto x=get32(a+byte),y=get32(b+byte);uint32_t result=0;
  if(op==OP_VPMULLD){int64_t product=signed32(x)*signed32(y);result=uint32_t(uint64_t(product));}
  else if(op==OP_VPMINSD)result=signed32(x)<signed32(y)?x:y;
  else if(op==OP_VPMAXSD)result=signed32(x)>signed32(y)?x:y;
  else fail("unknown reference operation");put32(dst+byte,result);
 }
 if(spec.width==16)std::memset(dst+16,0,16);
}
int main(){uint64_t cases=0;static const uint32_t edge[]={0,1,0x7fffffff,0x80000000,0xffffffff,0xaaaaaaaa,0x55555555,0x80000001};
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned trial=0;trial<4096;++trial){
  const auto& spec=specs[form];Memory m{};State s;setup(m,s,spec);
  if(trial<64)for(unsigned word=0;word<8;++word){put32(m.vectors[1]+4*word,edge[(trial+word)%8]);put32(m.vectors[2]+4*word,edge[((trial/8)+word)%8]);put32(m.backing+3+4*word,edge[((trial/8)+word+3)%8]);}
  if(operations[form]==OP_VPSHUFB&&trial<256){std::memset(m.vectors[2],trial,32);std::memset(m.backing+3,trial,32);}
  for(unsigned r=1;r<=2;++r)std::memcpy(&s.vec[r].ymm,m.vectors[r],32);
  Memory initial=m;State expected=s;alignas(32) uint8_t ref[4][32],observed[4][32];reference(ref,m,spec,operations[form]);std::memcpy(&expected.vec[spec.destination].ymm,ref[spec.destination],32);
  auto* result=lifted[form](&s,spec.pc,&m);hardware[form](m.vectors,observed,m.backing+3);
  if(std::memcmp(ref,observed,sizeof ref))fail("hardware/reference",form,trial);compare(m,initial,s,expected,result,spec,form,trial);++cases;
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":64,\"operations\":8,\"game_code_execution\":false}\n",(unsigned long long)cases);
}
