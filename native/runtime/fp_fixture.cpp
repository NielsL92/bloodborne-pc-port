// SPDX-License-Identifier: GPL-2.0-or-later
#include "runtime.h"
#include <cstring>
#include <cstdlib>
#include <stdexcept>
#include <xmmintrin.h>
#include "runtime-fp-entries.h"
extern "C" uint64_t __remill_read_memory_64(Memory*,uint64_t)noexcept;
extern "C" Memory* __remill_write_memory_64(Memory*,uint64_t,uint64_t)noexcept;
extern "C" Memory* __remill_write_memory_32(Memory*,uint64_t,uint32_t)noexcept;
extern "C" void __bb_native_x87_check_span(Memory*,State*,uint64_t,uint32_t,uint32_t,uint32_t)noexcept;
static constexpr uint64_t PC=0x1000d0000,STACK=0x70000000,DATA=0x71000000,RETURN=0xfeed0001;
static void require(bool yes,const char* what){if(!yes){std::fprintf(stderr,"FP runtime fixture: %s\n",what);std::exit(2);}}
static uint64_t bits(double value){uint64_t result;std::memcpy(&result,&value,8);return result;}
int main(int argc,char** argv){
 if(argc!=2)return 2;const char* mode=argv[1];
 bb_runtime::AddressSpace space;space.add(STACK,4096,bb_runtime::Read|bb_runtime::Write);space.add(DATA,4096,bb_runtime::Read|bb_runtime::Write);space.add(PC,4096,bb_runtime::Read|bb_runtime::Code);space.seal();
 const bb_runtime::Tables tables{targets,sizeof(targets)/sizeof(*targets),nullptr,0,nullptr,0,"authored-fp-runtime-v1"};bb_runtime::validate_tables(tables);
 bb_runtime::FpProfile profile{"authored-explicit-profile",uint64_t(0xffff)<<32,0xffff,sites,sizeof(sites)/sizeof(*sites)};bb_runtime::validate_fp_profile(profile);
 State state{};Memory memory{};memory.space=&space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.fp_profile=&profile;
 auto reset=[&](uint64_t pc){state={};state.gpr.rip.qword=pc;state.gpr.rsp.qword=STACK+128;state.gpr.rdi.qword=DATA;state.gpr.rsi.qword=DATA+32;state.gpr.rbp.qword=DATA;state.x87.fxsave.cwd.flat=0x37f;state.x87.fxsave.mxcsr.flat=0x1f80;state.seg.es.flat=0x11;state.seg.cs.flat=0x22;state.seg.ss.flat=0x33;state.seg.ds.flat=0x44;state.seg.fs.flat=0x55;state.seg.gs.flat=0x66;memory.entry=pc;memory.pointer_segments=0;__remill_write_memory_64(&memory,STACK+128,RETURN);};reset(PC);
 if(!std::strcmp(mode,"bad-policy")||!std::strcmp(mode,"bad-mask")||!std::strcmp(mode,"duplicate-sites")){
  bb_runtime::X87Site duplicates[2]={sites[0],sites[0]};if(!std::strcmp(mode,"bad-policy"))profile.image_policy|=64;else if(!std::strcmp(mode,"bad-mask"))profile.mxcsr_mask=0xffbf;else{profile.sites=duplicates;profile.site_count=2;}
  try{bb_runtime::validate_fp_profile(profile);}catch(const std::exception&){std::puts("{\"status\":\"setup-rejected\"}");return 0;}return 2;
 }
 if(!std::strcmp(mode,"positive")){
  uint64_t cases=0;unsigned host=_mm_getcsr();
  for(unsigned form=0;form<7;++form)for(unsigned policy=0;policy<64;++policy)for(unsigned value=0;value<64;++value){
   uint64_t pc=PC+form*64;reset(pc);profile.mxcsr_mask=value&1?0xffff:0xffbf;profile.image_policy=(uint64_t(profile.mxcsr_mask)<<32)|policy;bb_runtime::validate_fp_profile(profile);
   if(form==5){state.addr.fs_base.qword=0x1000;state.gpr.rdi.qword=DATA-0x1000;}if(form==6){state.addr.gs_base.qword=0x2000;state.gpr.rdi.qword=DATA-0x2000;}
   State expected=state;expected.gpr.rip.qword=RETURN;expected.gpr.rsp.qword+=8;expected.x87.fxsave.ip=pc+4;expected.x87.fxsave.fop=policy&8?0:form==1?0x55d:0x51f;expected.x87.fxsave.dp=policy&4?0:DATA;
   uint64_t sig=0x8000000000000000ULL;uint16_t exponent=0x3fff;std::memcpy(&expected.st.elems[7].val,&sig,8);std::memcpy(reinterpret_cast<uint8_t*>(&expected.st.elems[7].val)+8,&exponent,2);
   require(bb_runtime::dispatch(&state,pc,&memory)==&memory,"return context");require(__remill_read_memory_64(&memory,DATA)==0x3ff0000000000000ULL,"segmented store value");
   uint16_t segment[]={0x44,0x33,0x11,0x22,0x44,0x55,0x66};require(memory.pointer_segments==(0x22u|(policy&4?0:uint32_t(segment[form])<<16)),"segment identity/profile");
   if(std::memcmp(&state,&expected,sizeof state)){const auto* a=reinterpret_cast<const uint8_t*>(&state);const auto* b=reinterpret_cast<const uint8_t*>(&expected);for(size_t i=0;i<sizeof state;++i)if(a[i]!=b[i]){std::fprintf(stderr,"state form %u policy %u offset %zu actual %u expected %u\n",form,policy,i,a[i],b[i]);break;}return 2;}++cases;
  }
  profile.mxcsr_mask=0xffff;profile.image_policy=uint64_t(0xffff)<<32;
  for(unsigned value=0;value<4096;++value){reset(PC+0x200);__remill_write_memory_64(&memory,DATA,bits(double(value)));bb_runtime::dispatch(&state,PC+0x200,&memory);require(__remill_read_memory_64(&memory,DATA+32)==bits(double(value+1)),"native numeric linkage");require(state.gpr.rip.qword==RETURN&&state.gpr.rsp.qword==STACK+136&&state.x87.fxsave.ftw.flat==0&&state.x87.fxsave.swd.top==0&&state.x87.fxsave.ip==PC+0x206&&state.x87.fxsave.dp==DATA+32&&state.x87.fxsave.fop==0x51e&&memory.pointer_segments==0x440022,"numeric state/metadata");++cases;}
  require(_mm_getcsr()==host,"host MXCSR preserved");std::printf("{\"status\":\"pass\",\"aot_cases\":%llu,\"profile_variants\":64,\"segment_forms\":7,\"private_mappings_NX\":true,\"game_execution\":false}\n",(unsigned long long)cases);return 0;
 }
 uint64_t pc=PC;
 bb_runtime::X87Site wrong{};
 if(!std::strcmp(mode,"no-profile"))memory.fp_profile=nullptr;
 else if(!std::strcmp(mode,"unknown-site")){pc=PC+0x200;profile.sites=nullptr;profile.site_count=0;}
 else if(!std::strcmp(mode,"bad-site-fop")){pc=PC+0x200;wrong={pc,0,bb_runtime::Segment::DS};profile.sites=&wrong;profile.site_count=1;}
 else if(!std::strcmp(mode,"span-write"))__bb_native_x87_check_span(&memory,&state,DATA,10,2,1);
 else if(!std::strcmp(mode,"span-unmapped"))__bb_native_x87_check_span(&memory,&state,DATA+4090,10,0,1);
 else if(!std::strcmp(mode,"image-alignment"))pc=PC+0x440;
 else if(!std::strcmp(mode,"divide-zero")||!std::strcmp(mode,"divide-overflow"))pc=PC+0x340;
 else if(!std::strcmp(mode,"mxcsr"))pc=PC+0x300;
 else if(!std::strcmp(mode,"simd"))pc=PC+0x380;
 else if(!std::strcmp(mode,"x87-pending"))pc=PC+0x3c0;
 else if(!std::strcmp(mode,"x87-unsupported"))pc=PC+0x400;
 else return 2;
 reset(pc);
 if(!std::strcmp(mode,"image-alignment"))state.gpr.rdi.qword=DATA+1;
 if(!std::strcmp(mode,"divide-overflow")){state.gpr.rdx.qword=1;state.gpr.rcx.qword=1;}
 if(!std::strcmp(mode,"mxcsr"))__remill_write_memory_32(&memory,DATA,0x80001f80);
 if(!std::strcmp(mode,"simd")){state.x87.fxsave.mxcsr.flat=0x1f00;uint32_t qnan=0x7fc00000;std::memcpy(&state.vec[0],&qnan,4);}
 if(!std::strcmp(mode,"x87-pending")){state.x87.fxsave.cwd.flat=0x37e;state.sw.ie=1;state.x87.fxsave.swd.flat=0x8081;}
 if(!std::strcmp(mode,"x87-unsupported"))state.x87.fxsave.cwd.flat=0x17f;
 bb_runtime::dispatch(&state,pc,&memory);return 2;
}
