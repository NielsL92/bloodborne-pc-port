// SPDX-License-Identifier: GPL-2.0-or-later
// Authored VSHUFPS contracts: every immediate, both widths, aliases and memory.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {alignas(32) uint32_t vectors[3][8];uint64_t stack[8];unsigned width=0,vector_reads=0,return_reads=0;bool memory_form=false;uint64_t returned=0;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,const void*);
#include "shuffle-entries.h"
[[noreturn]] static void fail(const char* why,unsigned form,unsigned imm,unsigned trial){std::fprintf(stderr,"FAIL %s form=%u imm=%u trial=%u\n",why,form,imm,trial);std::exit(2);}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t at){
 auto start=uint64_t(&m->vectors[2][0]);if(!m->memory_form||at<start||at+4>start+m->width||((at-start)%4))fail("vector memory boundary",0,0,0);
 ++m->vector_reads;return m->vectors[2][(at-start)/4];
}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("return memory boundary",0,0,0);++m->return_reads;return m->stack[4];}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error",0,0,0);}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block",0,0,0);}
__declspec(noinline) static void reference(uint32_t (&out)[3][8],const uint32_t (&in)[3][8],unsigned width,unsigned dest,unsigned imm){
 std::memcpy(out,in,sizeof out);
 for(unsigned lane=0;lane<width/16;++lane){
  for(unsigned position=0;position<4;++position){unsigned choice=(imm>>(position*2))&3;out[dest][lane*4+position]=in[position<2?1:2][lane*4+choice];}
 }
 if(width==16)for(unsigned word=4;word<8;++word)out[dest][word]=0;
}
int main(){
 uint64_t random=0x92b5587632fae11ULL,cases=0;
 for(unsigned form=0;form<8;++form){unsigned width=form>=4?32:16,mode=form%4,dest=mode==1?1:mode==2?2:0;bool mem=mode==3;
  for(unsigned imm=0;imm<256;++imm)for(unsigned trial=0;trial<16;++trial){
   Memory m{};m.width=width;m.memory_form=mem;
   for(unsigned reg=0;reg<3;++reg)for(unsigned lane=0;lane<8;++lane){random^=random<<13;random^=random>>7;random^=random<<17;m.vectors[reg][lane]=trial?uint32_t(random):(0x80000000U|(reg<<16)|(lane<<8));}
   for(auto& x:m.stack)x=0xccccccccccccccccULL;m.stack[4]=0xfeed0001;Memory initial=m;
   alignas(64) State s;std::memset(&s,0xa5,sizeof s);for(unsigned reg=0;reg<3;++reg)std::memcpy(&s.vec[reg].ymm,m.vectors[reg],32);
   auto index=form*256+imm;auto pc=addresses[index];s.gpr.rdi.qword=uint64_t(&m.vectors[2][0]);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=pc;
   State expected=s;uint32_t expected_vectors[3][8];reference(expected_vectors,m.vectors,width,dest,imm);std::memcpy(&expected.vec[dest].ymm,expected_vectors[dest],32);expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;
   auto* result=lifted[index](&s,pc,&m);alignas(32) uint32_t observed[3][8];hardware[index](m.vectors,observed,m.vectors[2]);
   if(std::memcmp(observed,expected_vectors,sizeof observed))fail("hardware/reference",form,imm,trial);
   if(result!=&m||std::memcmp(&s,&expected,sizeof s))fail("AOT full State including upper vectors/flags",form,imm,trial);
   if(m.vector_reads!=(mem?width/4:0)||m.return_reads!=1||m.returned!=0xfeed0001||std::memcmp(m.vectors,initial.vectors,sizeof m.vectors)||std::memcmp(m.stack,initial.stack,sizeof m.stack))fail("AOT memory/return",form,imm,trial);
   ++cases;
  }
 }
 std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"forms\":8,\"immediates\":256,\"game_code_execution\":false}\n",(unsigned long long)cases);
}
