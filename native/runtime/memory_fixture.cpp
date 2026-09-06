// SPDX-License-Identifier: GPL-2.0-or-later
#include "runtime.h"
#include <algorithm>
#include <array>
#include <cstring>
#include <string>
#include <thread>
#include <vector>
#define DECL(bits,type) extern "C" type __remill_read_memory_##bits(Memory*,uint64_t)noexcept; extern "C" Memory* __remill_write_memory_##bits(Memory*,uint64_t,type)noexcept;
DECL(8,uint8_t) DECL(16,uint16_t) DECL(32,uint32_t) DECL(64,uint64_t) DECL(f32,float) DECL(f64,double)
extern "C" Memory* __remill_compare_exchange_memory_32(Memory*,uint64_t,uint32_t&,uint32_t)noexcept;
extern "C" Memory* __remill_compare_exchange_memory_64(Memory*,uint64_t,uint64_t&,uint64_t)noexcept;
extern "C" Memory* __remill_atomic_begin(Memory*)noexcept;extern "C" Memory* __remill_atomic_end(Memory*)noexcept;
static void require(bool test,const char* why){if(!test){std::fprintf(stderr,"FAIL %s\n",why);std::exit(2);}}
constexpr uint64_t BASE=0x70000000,RO=0x80000000,CODE=0x100000000;
int main(int argc,char** argv){
 if(argc!=2)return 2;std::string mode=argv[1];bb_runtime::AddressSpace space;std::array<uint8_t,4096> seed{};for(unsigned i=0;i<seed.size();++i)seed[i]=uint8_t(i*29+7);
 space.add(BASE,4096,bb_runtime::Read|bb_runtime::Write,seed.data(),seed.size());space.add(BASE+4096,4096,mode=="cross-permission"?bb_runtime::Read:bb_runtime::Read|bb_runtime::Write);space.add(RO,4096,bb_runtime::Read,seed.data(),seed.size());space.add(CODE,16,bb_runtime::Read|bb_runtime::Code,seed.data(),16);
 if(mode=="overlap"||mode=="writable-code"){
  bool rejected=false;try{space.add(mode=="overlap"?BASE+1:BASE+16384,16,mode=="overlap"?bb_runtime::Read:bb_runtime::Read|bb_runtime::Write|bb_runtime::Code);}catch(const std::exception&){rejected=true;}require(rejected,"invalid mapping rejected");std::puts("{\"status\":\"setup-rejected\"}");return 0;
 }
 if(mode!="unsealed")space.seal();State state{};state.gpr.rip.qword=0x123456789;state.gpr.rsp.qword=BASE+4096;Memory memory;memory.space=&space;memory.state=&state;memory.owner_thread=GetCurrentThreadId();memory.entry=state.gpr.rip.qword;
 if(mode=="read-unmapped"){__remill_read_memory_64(&memory,BASE+8192);return 2;}
 if(mode=="overflow"){__remill_read_memory_64(&memory,UINT64_MAX-3);return 2;}
 if(mode=="write-ro"){__remill_write_memory_64(&memory,RO,0);return 2;}
 if(mode=="cross-permission"){__remill_write_memory_64(&memory,BASE+4092,0);return 2;}
 if(mode=="code-write"){__remill_write_memory_8(&memory,CODE,0);return 2;}
 if(mode=="alignment"){space.check(&memory,BASE+1,8,false,8);return 2;}
 if(mode=="nested-atomic"){__remill_atomic_begin(&memory);__remill_atomic_begin(&memory);return 2;}
 if(mode=="unpaired-atomic"){__remill_atomic_end(&memory);return 2;}
 if(mode=="unsealed"){__remill_read_memory_8(&memory,BASE);return 2;}
 if(mode=="wrong-state"){State other{};bb_runtime::context(&memory,&other);return 2;}
 if(mode=="wrong-thread"){std::thread worker([&]{__remill_read_memory_8(&memory,BASE);});worker.join();return 2;}
 require(mode=="positive","known mode");std::vector<uint8_t> reference(8192);std::copy(seed.begin(),seed.end(),reference.begin());seed.fill(0);require(__remill_read_memory_8(&memory,RO)==7,"private input copy");
 uint64_t random=0xf00ddead12345678ULL,cases=0;
 for(unsigned trial=0;trial<4096;++trial)for(unsigned width:{1u,2u,4u,8u}){
  random^=random<<13;random^=random>>7;random^=random<<17;unsigned offset=trial<32?4080+trial%16:unsigned(random%(8192-width+1));uint64_t at=BASE+offset;
  if(width==1)__remill_write_memory_8(&memory,at,uint8_t(random));if(width==2)__remill_write_memory_16(&memory,at,uint16_t(random));if(width==4)__remill_write_memory_32(&memory,at,uint32_t(random));if(width==8)__remill_write_memory_64(&memory,at,random);
  for(unsigned j=0;j<width;++j)reference[offset+j]=uint8_t(random>>(j*8));uint64_t wanted=0;for(unsigned j=0;j<width;++j)wanted|=uint64_t(reference[offset+j])<<(j*8);
  uint64_t got=width==1?__remill_read_memory_8(&memory,at):width==2?__remill_read_memory_16(&memory,at):width==4?__remill_read_memory_32(&memory,at):__remill_read_memory_64(&memory,at);require(got==wanted,"scalar byte order / span");++cases;
 }
 for(unsigned i=0;i<8192;++i)require(__remill_read_memory_8(&memory,BASE+i)==reference[i],"complete mapped bytes");
 for(uint64_t bits:{0ULL,0x8000000000000000ULL,0x7ff0000000000001ULL,0x7ff8000000001234ULL,0xffffffffffffffffULL,0x3ff0000000000000ULL})for(unsigned offset=4089;offset<4097;++offset){
  double value;std::memcpy(&value,&bits,8);__remill_write_memory_f64(&memory,BASE+offset,value);auto actual=__remill_read_memory_f64(&memory,BASE+offset);uint64_t got;std::memcpy(&got,&actual,8);require(got==bits,"f64 raw bits");++cases;
 }
 for(uint32_t bits:{0u,0x80000000u,0x7f800001u,0x7fc01234u,0xffffffffu,0x3f800000u})for(unsigned offset=4093;offset<4097;++offset){
  float value;std::memcpy(&value,&bits,4);__remill_write_memory_f32(&memory,BASE+offset,value);auto actual=__remill_read_memory_f32(&memory,BASE+offset);uint32_t got;std::memcpy(&got,&actual,4);require(got==bits,"f32 raw bits");++cases;
 }
 for(unsigned offset=0;offset<16;++offset){__remill_write_memory_32(&memory,BASE+offset,123);uint32_t expected=122;__remill_compare_exchange_memory_32(&memory,BASE+offset,expected,456);require(expected==123&&__remill_read_memory_32(&memory,BASE+offset)==123,"CAS32 failure");__remill_compare_exchange_memory_32(&memory,BASE+offset,expected,456);require(expected==123&&__remill_read_memory_32(&memory,BASE+offset)==456,"CAS32 success");cases+=2;}
 constexpr unsigned THREADS=4,ITER=4096;std::vector<uint64_t> tickets(THREADS*ITER);std::vector<std::thread> workers;
 for(unsigned protocol=0;protocol<2;++protocol){__remill_write_memory_64(&memory,BASE,0);workers.clear();for(unsigned n=0;n<THREADS;++n)workers.emplace_back([&,n]{State s{};Memory m;m.space=&space;m.state=&s;m.owner_thread=GetCurrentThreadId();for(unsigned i=0;i<ITER;++i){uint64_t value;
   if(protocol==0){value=__remill_read_memory_64(&m,BASE);for(;;){uint64_t proposed=value;__remill_compare_exchange_memory_64(&m,BASE,value,proposed+1);if(value==proposed)break;}}
   else{__remill_atomic_begin(&m);value=__remill_read_memory_64(&m,BASE);__remill_write_memory_64(&m,BASE,value+1);__remill_atomic_end(&m);}tickets[n*ITER+i]=value;}require(!m.atomic_depth,"released atomic group");});for(auto& worker:workers)worker.join();require(__remill_read_memory_64(&memory,BASE)==THREADS*ITER,"shared counter total");std::sort(tickets.begin(),tickets.end());for(unsigned i=0;i<tickets.size();++i)require(tickets[i]==i,"linearizable ticket permutation");cases+=tickets.size();}
 std::printf("{\"status\":\"pass\",\"cases\":%llu,\"atomic_tickets\":32768,\"threads\":4,\"private_mappings_NX\":true,\"game_execution\":false}\n",(unsigned long long)cases);
}
