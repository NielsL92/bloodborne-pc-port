// SPDX-License-Identifier: Apache-2.0
// Sparse manifest consumer for the pinned Remill semantic engine. Never executes
// input instructions. Module cleanup/extraction follows Remill bin/lift/Lift.cpp
// (Trail of Bits, Apache-2.0). Trace hooks audit boundaries before lifting.
#include <glog/logging.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/raw_ostream.h>
#include <remill/Arch/Arch.h>
#include <remill/Arch/Instruction.h>
#include <remill/BC/IntrinsicTable.h>
#include <remill/BC/Lifter.h>
#include <remill/BC/Optimizer.h>
#include <remill/BC/Util.h>
#include <algorithm>
#include <fstream>
#include <map>
#include <set>
#include <stdexcept>

namespace {
std::map<uint64_t,std::string> instructions;
std::map<uint64_t,uint8_t> memory;
std::set<uint64_t> decoded,missing;
[[noreturn]] void reject(const std::string& why) { throw std::runtime_error(why); }
uint64_t number(const llvm::json::Object& o,llvm::StringRef key) {
  auto v=o.getInteger(key);if(!v||*v<0)reject("missing/nonpositive address field: "+key.str());return uint64_t(*v);
}
std::string unhex(llvm::StringRef text) {
  if(text.empty()||text.size()%2||text.size()>30)reject("instruction byte length outside 1..15");
  std::string bytes;
  auto nibble=[](char c)->int { if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;return -1; };
  for(size_t n=0;n<text.size();n+=2){int a=nibble(text[n]),b=nibble(text[n+1]);if(a<0||b<0)reject("invalid lowercase hex");bytes.push_back(char((a<<4)|b));}
  return bytes;
}
}

// Called by a separately compiled, minimally instrumented copy of the pinned
// TraceLifter.cpp. Missing bytes remain absent; mid-instruction starts reject.
bool bb_sparse_instruction_start(uint64_t pc) {
  if(instructions.count(pc))return true;
  if(memory.count(pc))reject("control transfer enters an instruction interior");
  missing.insert(pc);return false;
}
void bb_sparse_instruction_decoded(uint64_t pc,const remill::Instruction& ins) {
  if(!instructions.count(pc)||ins.bytes!=instructions.at(pc))reject("Remill instruction bytes/boundary disagree with manifest");
  if(ins.category==remill::Instruction::kCategoryInvalid||ins.category==remill::Instruction::kCategoryError)reject("Remill cannot decode a manifest instruction");
}
void bb_sparse_instruction_lifted(uint64_t pc,int status) {
  if(status!=int(remill::kLiftedInstruction))reject("unsupported Remill instruction semantics at "+std::to_string(pc));
  decoded.insert(pc);
}

struct Manager final:remill::TraceManager {
  const remill::Arch* arch;llvm::Module* module;uint64_t active=0;
  remill::TraceMap traces;
  Manager(const remill::Arch* a,llvm::Module* m):arch(a),module(m){}
  void SetLiftedTraceDefinition(uint64_t pc,llvm::Function* f)override {traces[pc]=f;}
  llvm::Function* GetLiftedTraceDefinition(uint64_t pc)override {
    if(traces.count(pc))return traces.at(pc);
    if(pc==active)return nullptr;
    auto name=TraceName(pc);auto* f=module->getFunction(name);
    return f?f:arch->DeclareLiftedFunction(name,module);
  }
  bool TryReadExecutableByte(uint64_t pc,uint8_t* byte)override {
    auto it=memory.find(pc);if(it==memory.end())return false;if(byte)*byte=it->second;return true;
  }
};

int main(int argc,char** argv) {
  google::InitGoogleLogging(argv[0]);FLAGS_logtostderr=true;
  if(argc!=5){llvm::errs()<<"usage: bb-sparse-lift input.json output.bc output.ll report.json\n";return 2;}
  try {
    auto buffer=llvm::MemoryBuffer::getFile(argv[1]);if(!buffer)reject("cannot read manifest input");
    auto json=llvm::json::parse((*buffer)->getBuffer());if(!json){llvm::consumeError(json.takeError());reject("invalid JSON");}
    auto* object=json->getAsObject();if(!object)reject("input must be object");
    auto* rows=object->getArray("instructions");auto* roots_json=object->getArray("roots");
    if(!rows||!roots_json||rows->empty()||roots_json->empty())reject("nonempty instructions/roots required");
    for(auto& row:*rows){
      auto* o=row.getAsObject();if(!o)reject("invalid instruction row");auto pc=number(*o,"address");
      auto text=o->getString("bytes");if(!text)reject("missing bytes");auto bytes=unhex(*text);
      if(instructions.count(pc))reject("duplicate instruction start");instructions.emplace(pc,bytes);
      for(size_t n=0;n<bytes.size();++n){if(pc+n<pc||memory.count(pc+n))reject("overlapping/overflowing instruction bytes");memory[pc+n]=uint8_t(bytes[n]);}
    }
    std::vector<uint64_t> roots;std::set<uint64_t> unique;
    for(auto& value:*roots_json){auto at=value.getAsInteger();if(!at||*at<0||!instructions.count(uint64_t(*at))||!unique.insert(uint64_t(*at)).second)reject("invalid/duplicate/unmapped root");roots.push_back(uint64_t(*at));}
    llvm::LLVMContext context;auto arch=remill::Arch::Get(context,"windows","amd64_avx");
    std::unique_ptr<llvm::Module> module(remill::LoadArchSemantics(arch.get()));
    remill::IntrinsicTable intrinsics(module.get());Manager manager(arch.get(),module.get());
    remill::TraceLifter lifter(arch.get(),manager);
    for(auto pc:roots){manager.active=pc;if(!lifter.Lift(pc))reject("trace lifting failed");}
    llvm::json::Array missing_rows,unvisited,decoded_rows,trace_rows;
    for(auto pc:missing)missing_rows.push_back(int64_t(pc));
    for(auto pc:decoded)decoded_rows.push_back(int64_t(pc));
    for(auto& row:instructions)if(!decoded.count(row.first))unvisited.push_back(int64_t(row.first));
    std::map<uint64_t,llvm::Function*> ordered(manager.traces.begin(),manager.traces.end());
    for(auto& row:ordered)trace_rows.push_back(int64_t(row.first));
    auto unvisited_count=unvisited.size();
    llvm::json::Object report{{"schema",1},{"input_instructions",int64_t(instructions.size())},{"input_bytes",int64_t(memory.size())},
      {"decoded_addresses",std::move(decoded_rows)},{"missing_instruction_starts",std::move(missing_rows)},
      {"unvisited_manifest_instructions",std::move(unvisited)},{"compiled_roots",std::move(trace_rows)},
      {"execution","none; static lifting census is not execution coverage"}};
    std::error_code ec;llvm::raw_fd_ostream output(argv[4],ec);if(ec)reject("cannot write report");output<<llvm::formatv("{0:2}\n",llvm::json::Value(std::move(report)));output.close();
    if(unvisited_count)reject("manifest contains instructions unreachable from supplied compilation roots");
    if(auto* g=module->getGlobalVariable("llvm.compiler.used",true))g->eraseFromParent();
    std::vector<llvm::GlobalVariable*> erase;
    for(auto& g:module->globals())if(g.getName().starts_with("ISEL_"))erase.push_back(&g);
    for(auto* g:erase)g->eraseFromParent();
    if(auto* f=module->getFunction("__remill_intrinsics"))f->eraseFromParent();
    if(auto* f=module->getFunction("__remill_sync_hyper_call")){
      auto name=f->getName().str();auto replacement=module->getOrInsertFunction(name+"_",f->getFunctionType());
      f->replaceAllUsesWith(replacement.getCallee());f->eraseFromParent();replacement.getCallee()->setName(name);
    }
    for(auto& f:*module)if(f.getName().starts_with("__remill_")){
      f.removeFnAttr(llvm::Attribute::ReadNone);
      for(auto& arg:f.args())arg.removeAttr(llvm::Attribute::ReadNone);
      for(auto* user:f.users())if(auto* call=llvm::dyn_cast<llvm::CallInst>(user))call->removeFnAttr(llvm::Attribute::ReadNone);
    }
    remill::OptimizationGuide guide={};remill::OptimizeModule(arch,module,manager.traces,guide);
    llvm::Module dest("sparse_manifest",context);arch->PrepareModuleDataLayout(&dest);
    for(auto& row:ordered)remill::MoveFunctionIntoModule(row.second,&dest);
    if(llvm::verifyModule(dest,&llvm::errs()))reject("invalid lifted LLVM module");
    if(!remill::StoreModuleIRToFile(&dest,argv[3],true)||!remill::StoreModuleToFile(&dest,argv[2],true))reject("cannot write compiled IR/bitcode");
    llvm::outs()<<"Sparse lifting complete: "<<instructions.size()<<" instructions, "<<roots.size()<<" roots; no execution\n";
    return 0;
  }catch(const std::exception& e){llvm::errs()<<"REJECT: "<<e.what()<<"\n";return 2;}
}
