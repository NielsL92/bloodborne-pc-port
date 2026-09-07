// SPDX-License-Identifier: GPL-2.0-or-later
#include "canary.h"
#include <array>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <string>
extern "C" Memory* sub_1000f0000(State*,uint64_t,Memory*);
extern "C" Memory* sub_1000f1000(State* s,uint64_t pc,Memory* m){return bb_runtime::imported(s,pc,m);}
constexpr uint64_t PC=0x1000f0000,CELL=0x72000000,STACK=0x73000000,RETURN=0xfeed1001;
static void require(bool okay,const char* why){if(!okay){std::fprintf(stderr,"Canary fixture: %s\n",why);std::exit(2);}}
static void exercise(uint64_t seed_value,uint64_t mask,const std::string& mode){
 std::array<uint8_t,512> stack{};uint64_t ret=RETURN;std::memcpy(stack.data()+128,&ret,8);bb_runtime::AddressSpace space;space.add(CELL,8,bb_runtime::Read|bb_runtime::Write);space.add(STACK,stack.size(),bb_runtime::Read|bb_runtime::Write,stack.data(),stack.size());space.seal();State state{};state.gpr.rip.qword=PC;state.gpr.rsp.qword=STACK+128;state.gpr.rbp.qword=0x123456;state.gpr.rdi.qword=CELL;state.gpr.rsi.qword=seed_value^0x12345678abcdef00ULL;state.gpr.rdx.qword=mask;
 const bb_runtime::Target targets[]={{PC,sub_1000f0000}};const bb_runtime::Import imports[]={{PC+0x1000,"Ou3iL1abvng","libkernel","libkernel",nullptr,0}};const bb_runtime::Tables tables{targets,1,nullptr,0,imports,1,"authored-native-canary-v1"};bb_runtime::validate_tables(tables);Memory memory{};memory.space=&space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.entry=PC;bb_runtime::CanarySeed seed{};std::memcpy(seed.data(),&seed_value,8);bb_runtime::ProcessCanary canary(space,CELL);canary.initialize_from_seed(&memory,seed);require(canary.initialized(),"initialization status");
 if(mode=="double-init"){try{canary.initialize_from_seed(&memory,seed);}catch(const std::exception&){std::puts("{\"status\":\"setup-rejected\"}");return;}std::exit(2);}
 if(mode=="wide"||mode=="offset"){std::array<uint8_t,16> value{};space.read(&memory,CELL+(mode=="offset"),value.data(),mode=="wide"?16:8);std::exit(2);}
 auto* result=bb_runtime::dispatch(&state,PC,&memory);require(result==&memory&&state.gpr.rip.qword==RETURN&&state.gpr.rsp.qword==STACK+136&&state.gpr.rbp.qword==0x123456&&state.gpr.rax.qword==(seed_value^0x12345678abcdef00ULL)&&state.gpr.rcx.qword==seed_value,"returned State");uint64_t actual=0;space.read(&memory,CELL,&actual,8);require(actual==seed_value,"stable canary contents");
}
int main(int argc,char** argv){if(argc<2)return 2;std::string mode=argv[1];
 if(mode=="entropy"){auto seed=bb_runtime::native_canary_seed();if(seed.size()!=8)return 2;std::puts("{\"status\":\"native-entropy-acquired\",\"bytes\":8}");return 0;}
 if(mode=="positive"){uint64_t seed=0;for(unsigned n=0;n<4096;++n){exercise(seed,0,mode);seed=seed*6364136223846793005ULL+1442695040888963407ULL;}std::puts("{\"status\":\"pass\",\"aot_cases\":4096,\"canary_bytes\":8}");return 0;}
 if(mode=="negative"){if(argc!=3)return 2;unsigned bit=std::strtoul(argv[2],nullptr,10);if(bit>=64)return 2;exercise(0x0123456789abcdefULL,uint64_t(1)<<bit,mode);return 2;}
 if(mode=="double-init"||mode=="wide"||mode=="offset"){exercise(0x0123456789abcdefULL,0,mode);return 0;}return 2;}
