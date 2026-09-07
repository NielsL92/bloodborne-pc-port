// SPDX-License-Identifier: GPL-2.0-or-later
// Bounded native entry diagnostic, not a completed process startup implementation.
#include "loader.h"
#include "registry.h"
#include "startup-config.h"
#include <algorithm>
#include <cstring>
#include <exception>
#include <filesystem>
#include <vector>
static Memory* exit_callback(State* s,uint64_t pc,Memory* m)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"startup-exit-callback-unimplemented",49,pc);}
int main(int argc,char** argv){
 if(argc!=2||(std::strcmp(argv[1],"--prepare-only")&&std::strcmp(argv[1],"--probe-entry")))return 2;
 try{
  if(std::strcmp(bb_registry::tables.identity,REGISTRY_ID))return 2;bb_runtime::validate_tables(bb_registry::tables);
  auto bundle_path=(std::filesystem::path(argv[0]).parent_path()/"startup.bin").string();auto image=bb_runtime::load_private_image(bundle_path.c_str(),BUNDLE_SHA256,REGISTRY_ID);std::vector<bb_runtime::Target> targets(bb_registry::tables.targets,bb_registry::tables.targets+bb_registry::tables.target_count);targets.push_back({EXIT_CALLBACK_PC,exit_callback});std::sort(targets.begin(),targets.end(),[](const auto& a,const auto& b){return a.pc<b.pc;});auto tables=bb_registry::tables;tables.targets=targets.data();tables.target_count=targets.size();tables.identity=TRACE_ID;bb_runtime::validate_tables(tables);
  State state{};state.gpr.rip.qword=ENTRY_PC;state.gpr.rsp.qword=INITIAL_RSP;state.gpr.rdi.qword=PARAMETERS;state.gpr.rsi.qword=EXIT_CALLBACK_PC;Memory memory{};memory.space=&image->space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.entry=ENTRY_PC;
  auto checked=image->validate(&memory);if(checked.sha256!=EXPECTED_IMAGE_SHA256||checked.mapped_bytes!=EXPECTED_MAPPED_BYTES)return 2;memory.operations=0;
  std::printf("{\"status\":\"native-entry-prepared\",\"entry\":\"%016llx\",\"initial_rsp\":\"%016llx\",\"parameters\":\"%016llx\",\"exit_callback\":\"%016llx\",\"private_image_sha256\":\"%s\",\"trace_identity\":\"%s\"}\n",(unsigned long long)ENTRY_PC,(unsigned long long)INITIAL_RSP,(unsigned long long)PARAMETERS,(unsigned long long)EXIT_CALLBACK_PC,checked.sha256.c_str(),TRACE_ID);std::fflush(stdout);
  if(!std::strcmp(argv[1],"--prepare-only"))return 0;
  bb_runtime::dispatch(&state,ENTRY_PC,&memory);bb_runtime::fault(&memory,"unexpected-startup-return",50,ENTRY_PC,state.gpr.rip.qword);
 }catch(const std::exception& e){std::fprintf(stderr,"Native entry preparation rejected: %s\n",e.what());return 2;}
}
