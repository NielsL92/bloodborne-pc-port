// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory {alignas(32) uint8_t vectors[4][32];uint8_t backing[40];uint64_t stack[8];unsigned width=0,vector_bytes=0,return_reads=0;bool memory_form=false;uint64_t returned=0;};
struct Spec {unsigned width,destination;bool memory;unsigned element_bytes;uint64_t pc;};
using Lifted=Memory*(*)(State*,uint64_t,Memory*);using Hardware=void(*)(const void*,void*,const void*);
#include "vector-entries.h"
[[noreturn]] static void fail(const char* why,unsigned form=0,unsigned trial=0,unsigned setting=0){std::fprintf(stderr,"FAIL %s form=%u trial=%u setting=%u\n",why,form,trial,setting);std::exit(2);}
static void check_read(Memory* m,uint64_t at,unsigned size){auto start=uint64_t(m->backing+3);if(!m->memory_form||at<start||at+size>start+m->width)fail("vector read boundary");m->vector_bytes+=size;}
extern "C" uint8_t __remill_read_memory_8(Memory* m,uint64_t at){check_read(m,at,1);return *reinterpret_cast<const uint8_t*>(at);}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t at){check_read(m,at,4);uint32_t v;std::memcpy(&v,reinterpret_cast<const void*>(at),4);return v;}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t at){if(at!=uint64_t(m->stack+4))fail("return memory boundary");++m->return_reads;return m->stack[4];}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m){s->gpr.rip.qword=pc;m->returned=pc;return m;}
extern "C" Memory* __remill_error(State*,uint64_t,Memory*){fail("compiler error");}
extern "C" Memory* __remill_missing_block(State*,uint64_t,Memory*){fail("missing block");}
static uint64_t rng=0x185746394234aefULL;
static uint32_t next(){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return uint32_t(rng);}
static void setup(Memory& m,State& s,const Spec& spec){
 m.width=spec.width;m.memory_form=spec.memory;for(auto& v:m.vectors)for(auto& b:v)b=uint8_t(next());for(auto& b:m.backing)b=uint8_t(next());
 for(auto& x:m.stack)x=0xccccccccccccccccULL;m.stack[4]=0xfeed0001;
 std::memset(&s,0xa5,sizeof s);for(unsigned r=0;r<4;++r)std::memcpy(&s.vec[r].ymm,m.vectors[r],32);
 s.gpr.rdi.qword=uint64_t(m.backing+3);s.gpr.rsp.qword=uint64_t(m.stack+4);s.gpr.rip.qword=spec.pc;
}
static void compare(Memory& m,const Memory& initial,State& s,State& expected,Memory* result,const Spec& spec,unsigned form,unsigned trial,unsigned setting=0){
 expected.gpr.rsp.qword+=8;expected.gpr.rip.qword=0xfeed0001;
 if(result!=&m||std::memcmp(&s,&expected,sizeof s))fail("AOT full State",form,trial,setting);
 if(m.vector_bytes!=(spec.memory?spec.width:0)||m.return_reads!=1||m.returned!=0xfeed0001||std::memcmp(m.vectors,initial.vectors,sizeof m.vectors)||std::memcmp(m.backing,initial.backing,sizeof m.backing)||std::memcmp(m.stack,initial.stack,sizeof m.stack))fail("AOT memory/return",form,trial,setting);
}
