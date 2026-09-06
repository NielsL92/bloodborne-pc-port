// SPDX-License-Identifier: GPL-2.0-or-later
// Host-only registry validation. There is deliberately no game-entry invocation.
#include "registry.h"
#include <cstring>
#include <exception>
#include <cstdlib>
int main(int argc,char** argv){
 if(argc<2)return 2;
 try{bb_runtime::validate_tables(bb_registry::tables);}catch(const std::exception& e){std::fprintf(stderr,"registry setup: %s\n",e.what());return 3;}
 size_t compiled=0;const auto& t=bb_registry::tables;
 if(bb_registry::import_gateway_count!=t.import_count)return 4;
 for(size_t i=0;i<t.import_count;++i)if(bb_registry::import_gateways[i].pc!=t.imports[i].pc||!bb_registry::import_gateways[i].function)return 4;
 if(argc==3&&!std::strcmp(argv[1],"--probe-native-import")){
  char* end=nullptr;unsigned long index=std::strtoul(argv[2],&end,10);if(!end||*end||index>=t.import_count||t.imports[index].compiled_export||t.imports[index].native)return 5;
  bb_runtime::AddressSpace space;space.seal();State state{};state.gpr.rip.qword=t.imports[index].pc;Memory memory{};memory.space=&space;memory.state=&state;memory.tables=&t;memory.owner_thread=GetCurrentThreadId();memory.entry=state.gpr.rip.qword;
  bb_registry::import_gateways[index].function(&state,state.gpr.rip.qword,&memory);return 6;
 }
 if(argc==2&&!std::strcmp(argv[1],"--probe-unknown")){
  bb_runtime::AddressSpace space;space.seal();State state{};Memory memory{};memory.space=&space;memory.state=&state;memory.tables=&t;memory.owner_thread=GetCurrentThreadId();bb_runtime::dispatch(&state,0,&memory);return 6;
 }
 if(argc!=2||std::strcmp(argv[1],"--validate-only"))return 2;
 for(size_t i=0;i<t.import_count;++i)if(t.imports[i].compiled_export)++compiled;
 for(size_t i=0;i<bb_registry::x87_site_count;++i){const auto& site=bb_registry::x87_sites[i];if((i&&bb_registry::x87_sites[i-1].pc>=site.pc)||site.fop>0x7ff||unsigned(site.data_segment)>unsigned(bb_runtime::Segment::GS))return 4;}
 std::printf("{\"status\":\"host registry validation pass\",\"compiled_roots\":%zu,\"source_pairs\":%zu,\"imports\":%zu,\"conditional_compiled_exports\":%zu,\"explicit_native_stops\":%zu,\"x87_sites\":%zu,\"identity\":\"%s\",\"game_entry_called\":false,\"guest_mappings_created\":false,\"fp_profile_selected\":false}\n",t.target_count,t.pair_count,t.import_count,compiled,t.import_count-compiled,bb_registry::x87_site_count,t.identity);return 0;
}
