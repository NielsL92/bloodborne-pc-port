// SPDX-License-Identifier: GPL-2.0-or-later
// Bounded native entry diagnostic, not a completed process startup implementation.
#include "loader.h"
#include "canary.h"
#include "mutexattr.h"
#include "mutex.h"
#include "direct_memory.h"
#include "rwlock.h"
#include "registry.h"
#include "startup-config.h"
#include <algorithm>
#include <cstring>
#include <exception>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <vector>
static Memory* exit_callback(State* s,uint64_t pc,Memory* m)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"startup-exit-callback-unimplemented",49,pc);}
static bb_runtime::CanarySeed prepare_seed(const std::filesystem::path& path){
 bb_runtime::CanarySeed seed{};
 if(std::filesystem::exists(path)){
  if(std::filesystem::file_size(path)!=seed.size())throw std::runtime_error("runtime seed must contain exactly eight bytes");
  std::ifstream in(path,std::ios::binary);if(!in.read(reinterpret_cast<char*>(seed.data()),seed.size()))throw std::runtime_error("runtime seed read failed");return seed;
 }
 seed=bb_runtime::native_canary_seed();HANDLE file=CreateFileW(path.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(file==INVALID_HANDLE_VALUE)throw std::runtime_error("runtime seed create failed");DWORD written=0;BOOL ok=WriteFile(file,seed.data(),DWORD(seed.size()),&written,nullptr);BOOL flushed=ok&&FlushFileBuffers(file);CloseHandle(file);
 if(!ok||!flushed||written!=seed.size())throw std::runtime_error("runtime seed recording failed");return seed;
}
int main(int argc,char** argv){
 if(argc!=2||(std::strcmp(argv[1],"--prepare-only")&&std::strcmp(argv[1],"--probe-entry")))return 2;
 try{
  if(std::strcmp(bb_registry::tables.identity,REGISTRY_ID))return 2;bb_runtime::validate_tables(bb_registry::tables);
  auto bundle_path=(std::filesystem::path(argv[0]).parent_path()/"startup.bin").string();auto image=bb_runtime::load_private_image(bundle_path.c_str(),BUNDLE_SHA256,REGISTRY_ID);std::vector<bb_runtime::Target> targets(bb_registry::tables.targets,bb_registry::tables.targets+bb_registry::tables.target_count);for(const auto& target:SUPPLEMENT_TARGETS)if(target.pc)targets.push_back(target);targets.push_back({EXIT_CALLBACK_PC,exit_callback});std::sort(targets.begin(),targets.end(),[](const auto& a,const auto& b){return a.pc<b.pc;});std::vector<bb_runtime::Import> imports(bb_registry::tables.imports,bb_registry::tables.imports+bb_registry::tables.import_count);
  for(const auto& binding:NATIVE_BINDINGS){if(!binding.pc)continue;auto it=std::find_if(imports.begin(),imports.end(),[&](const auto& i){return i.pc==binding.pc;});if(it==imports.end()||it->native||it->compiled_export)throw std::runtime_error("native service binding mismatch");it->native=binding.function;}
  auto tables=bb_registry::tables;tables.imports=imports.data();tables.import_count=imports.size();tables.targets=targets.data();tables.target_count=targets.size();tables.identity=TRACE_ID;bb_runtime::validate_tables(tables);
  State state{};state.gpr.rip.qword=ENTRY_PC;state.gpr.rsp.qword=INITIAL_RSP;state.gpr.rdi.qword=PARAMETERS;state.gpr.rsi.qword=EXIT_CALLBACK_PC;Memory memory{};memory.space=&image->space;memory.state=&state;memory.tables=&tables;memory.owner_thread=GetCurrentThreadId();memory.entry=ENTRY_PC;
  bb_runtime::MutexAttributes mutex_attributes(image->space);if(MUTEX_ATTRIBUTES_ENABLED)memory.mutex_attributes=&mutex_attributes;
  bb_runtime::Mutexes mutexes(image->space);if(MUTEXES_ENABLED)memory.mutexes=&mutexes;
  std::unique_ptr<bb_runtime::DirectMemory> direct_memory;if(DIRECT_MEMORY_BUDGET){direct_memory=std::make_unique<bb_runtime::DirectMemory>(image->space,DIRECT_MEMORY_BUDGET);memory.direct_memory=direct_memory.get();}
  bb_runtime::Rwlocks rwlocks(image->space);if(RWLOCKS_ENABLED)memory.rwlocks=&rwlocks;
  auto checked=image->validate(&memory);if(checked.sha256!=EXPECTED_IMAGE_SHA256||checked.mapped_bytes!=EXPECTED_MAPPED_BYTES)return 2;
  bb_runtime::ProcessCanary process_word(image->space,CANARY_PC);
  if(CANARY_ENABLED){auto seed=prepare_seed(std::filesystem::path(argv[0]).parent_path()/"canary-seed.bin");process_word.initialize_from_seed(&memory,seed);if(!process_word.initialized())return 2;}
  memory.operations=0;
  std::printf("{\"status\":\"native-entry-prepared\",\"entry\":\"%016llx\",\"initial_rsp\":\"%016llx\",\"parameters\":\"%016llx\",\"exit_callback\":\"%016llx\",\"private_image_sha256\":\"%s\",\"trace_identity\":\"%s\",\"native_runtime_word_initialized\":%s}\n",(unsigned long long)ENTRY_PC,(unsigned long long)INITIAL_RSP,(unsigned long long)PARAMETERS,(unsigned long long)EXIT_CALLBACK_PC,checked.sha256.c_str(),TRACE_ID,process_word.initialized()?"true":"false");std::fflush(stdout);
  if(!std::strcmp(argv[1],"--prepare-only"))return 0;
  if(CONTROL_TRACE){auto path=(std::filesystem::path(argv[0]).parent_path()/"native-calls.jsonl").string();memory.control_trace=std::fopen(path.c_str(),"wb");if(!memory.control_trace)throw std::runtime_error("control trace open failed");}
  bb_runtime::dispatch(&state,ENTRY_PC,&memory);bb_runtime::fault(&memory,"unexpected-startup-return",50,ENTRY_PC,state.gpr.rip.qword);
 }catch(const std::exception& e){std::fprintf(stderr,"Native entry preparation rejected: %s\n",e.what());return 2;}
}
