// SPDX-License-Identifier: GPL-2.0-or-later
#include "vector_fixture.h"
extern "C" double __remill_read_memory_f64(Memory* m,uint64_t at){check_read(m,at,8);double value;std::memcpy(&value,reinterpret_cast<const void*>(at),8);return value;}
struct HardwareState {alignas(32) uint8_t vectors[4][32];uint64_t rax;};
static uint32_t get32(const uint8_t* p){uint32_t v;std::memcpy(&v,p,4);return v;}
static void put32(uint8_t* p,uint32_t v){std::memcpy(p,&v,4);}
__declspec(noinline) static void reference(HardwareState& out,const Memory& m,const Spec& spec,unsigned op,unsigned imm,uint64_t rax){
 std::memcpy(out.vectors,m.vectors,sizeof out.vectors);out.rax=rax;auto* dst=out.vectors[spec.destination];const auto* source=spec.memory?m.backing+3:m.vectors[2];
 unsigned width=spec.width;
 if(op==OP_VEXTRACTF128)std::memcpy(dst,m.vectors[2]+16*(imm%2),16);
 else if(op==OP_VINSERTPS){std::memcpy(dst,m.vectors[1],16);unsigned choice=spec.memory?0:(imm/64)%4;std::memcpy(dst+4*((imm/16)%4),source+choice*4,4);for(unsigned word=0;word<4;++word)if(imm&(1<<word))std::memset(dst+4*word,0,4);width=16;}
 else if(op==OP_VPINSRD){std::memcpy(dst,m.vectors[1],16);put32(dst+4*(imm%4),spec.memory?get32(source):uint32_t(rax));width=16;}
 else if(op==OP_VMOVMSKPS||op==OP_VMOVMSKPD){out.rax=0;for(unsigned i=0;i<width/spec.element_bytes;++i)if(m.vectors[2][(i+1)*spec.element_bytes-1]>=128)out.rax+=uint64_t(1)<<i;return;}
 else if(op==OP_VLDDQU)std::memcpy(dst,source,width);
 else if(op==OP_VUNPCKHPD){for(unsigned lane=0;lane<width;lane+=16){std::memcpy(dst+lane,m.vectors[1]+lane+8,8);std::memcpy(dst+lane+8,source+lane+8,8);}}
 else fail("unknown reference operation");
 if(width==16)std::memset(dst+16,0,16);
}
int main(){uint64_t cases=0;
 for(unsigned form=0;form<sizeof(specs)/sizeof(*specs);++form)for(unsigned trial=0;trial<256;++trial){
  const auto& spec=specs[form];Memory m{};State s;setup(m,s,spec);s.gpr.rax.qword=0xdeadbeef00000000ULL|next();
  if(operations[form]==OP_VMOVMSKPS||operations[form]==OP_VMOVMSKPD){for(unsigned word=0;word<spec.width/spec.element_bytes;++word){auto& sign=m.vectors[2][(word+1)*spec.element_bytes-1];sign=uint8_t((sign&0x7f)|(((trial>>word)&1)<<7));}std::memcpy(&s.vec[2].ymm,m.vectors[2],32);}
  Memory initial=m;State expected=s;HardwareState input{},ref{},observed{};std::memcpy(input.vectors,m.vectors,sizeof input.vectors);input.rax=s.gpr.rax.qword;
  reference(ref,m,spec,operations[form],immediates[form],input.rax);for(unsigned reg=0;reg<4;++reg)std::memcpy(&expected.vec[reg].ymm,ref.vectors[reg],32);expected.gpr.rax.qword=ref.rax;
  auto* result=lifted[form](&s,spec.pc,&m);hardware[form](&input,&observed,m.backing+3);
  if(std::memcmp(ref.vectors,observed.vectors,sizeof ref.vectors)||ref.rax!=observed.rax)fail("hardware/reference",form,trial,immediates[form]);compare(m,initial,s,expected,result,spec,form,trial,immediates[form]);++cases;
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"instruction_roots\":%llu,\"operations\":7,\"game_code_execution\":false}\n",(unsigned long long)cases,(unsigned long long)(sizeof(specs)/sizeof(*specs)));
}
