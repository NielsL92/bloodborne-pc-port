// SPDX-License-Identifier: Apache-2.0
// Experimental bindings for fully mapped RAM spans. Runtime image profile and
// pointer metadata are explicit per-thread services, never inferred from host CPU.
#include "x87_environment.h"
extern "C" void __bb_native_x87_check_span(Memory*,State*,addr_t,uint32_t,uint32_t,uint32_t);
extern "C" uint64_t __bb_native_x87_image_policy(Memory*,State*);
extern "C" uint32_t __bb_native_x87_pointer_segments(Memory*,State*);
extern "C" void __bb_native_x87_set_pointer_segments(Memory*,State*,uint32_t);
namespace {
ALWAYS_INLINE bb_x87::Profile BBX87ImageProfile(Memory* m,State& s){auto v=__bb_native_x87_image_policy(m,&s);return {bool(v&1),bool(v&2),uint32_t(v>>32)};}
ALWAYS_INLINE bb_x87::PointerSegments BBX87Segments(Memory* m,State& s){auto v=__bb_native_x87_pointer_segments(m,&s);return {uint16_t(v),uint16_t(v>>16)};}
DEF_SEM(BBX87StoreEnvironment28,M8W dst){
 auto address=AddressOf(dst);__bb_native_x87_check_span(memory,&state,address,28,1,1);auto profile=BBX87ImageProfile(memory,state);auto segments=BBX87Segments(memory,state);uint8_t buffer[28];
 bb_x87::store_environment28(state,segments,profile,buffer);for(unsigned i=0;i<28;++i)memory=__remill_write_memory_8(memory,address+i,buffer[i]);return memory;
}
DEF_SEM(BBX87LoadEnvironment28,M8 src){
 BBX87Pending(memory,state);auto address=AddressOf(src);__bb_native_x87_check_span(memory,&state,address,28,0,1);auto profile=BBX87ImageProfile(memory,state);uint8_t buffer[28];for(unsigned i=0;i<28;++i)buffer[i]=__remill_read_memory_8(memory,address+i);
 auto segments=bb_x87::load_environment28(state,profile,buffer);__bb_native_x87_set_pointer_segments(memory,&state,uint32_t(segments.code)|(uint32_t(segments.data)<<16));return memory;
}
template<bool Wide> DEF_SEM(BBX87SaveImage,M8W dst){
 auto address=AddressOf(dst);__bb_native_x87_check_span(memory,&state,address,512,1,16);auto profile=BBX87ImageProfile(memory,state);auto segments=BBX87Segments(memory,state);uint8_t buffer[512];
 // Only the defined written subranges are emitted. In particular, never read
 // destination bytes merely to preserve AMD's omitted pointers/software tail.
 bb_x87::save_fx(state,segments,profile,Wide,buffer);bool pointers=!profile.save_pointers_only_with_exception||(bb_x87::status(state)&0x80);
 for(unsigned i=0;i<416;++i)if(pointers||i<6||i>=24)memory=__remill_write_memory_8(memory,address+i,buffer[i]);return memory;
}
}
DEF_ISEL(FNSTENV_MEMmem28)=BBX87StoreEnvironment28;
DEF_ISEL(FLDENV_MEMmem28)=BBX87LoadEnvironment28;
DEF_ISEL(FXSAVE_MEMmfpxenv)=BBX87SaveImage<false>;
DEF_ISEL(FXSAVE64_MEMmfpxenv)=BBX87SaveImage<true>;
