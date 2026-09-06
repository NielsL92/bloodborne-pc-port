// SPDX-License-Identifier: Apache-2.0
// Sparse manifest consumer for the pinned Remill semantic engine. Never executes
// input instructions. Module cleanup/extraction follows Remill bin/lift/Lift.cpp
// (Trail of Bits, Apache-2.0). Trace hooks audit boundaries before lifting.
#include <glog/logging.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/BasicBlock.h>
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
#include <filesystem>
#include <map>
#include <set>
#include <stdexcept>

namespace {
std::map<uint64_t,std::string> instructions;
std::map<uint64_t,uint8_t> memory;
std::set<uint64_t> decoded,missing,declared_traps,emitted_traps;
struct X87Opcode {uint16_t original,corrected;};
std::map<uint64_t,X87Opcode> x87_opcodes;
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
void bb_sparse_instruction_decoded(uint64_t pc,remill::Instruction& ins) {
  if(!instructions.count(pc)||ins.bytes!=instructions.at(pc))reject("Remill instruction bytes/boundary disagree with manifest");
  // Canonical raw x87 storage is not yet coherent with Remill's independent
  // MMX slots. A future discovered MMX path must fail closed, not silently mix
  // representations. The current recovered startup graph contains no MMX.
  bool mmx=ins.function=="EMMS"||ins.function=="FEMMS";
  for(const auto& operand:ins.operands)if(operand.type==remill::Operand::kTypeRegister){const auto& name=operand.reg.name;mmx|=name.size()==3&&name[0]=='M'&&name[1]=='M'&&name[2]>='0'&&name[2]<='7';}
  if(mmx)reject("MMX/x87 shared-state semantics are not validated at "+std::to_string(pc)+" selector "+ins.function);
  if(ins.category==remill::Instruction::kCategoryInvalid||(ins.category==remill::Instruction::kCategoryError&&!(ins.function=="UD2"&&declared_traps.count(pc))))reject("Remill instruction error/invalid category at "+std::to_string(pc)+" selector "+ins.function);
  // Pinned Remill DecodeFpuOpcode uses &3 instead of &7. Normalize the
  // appended immediate from exact manifest bytes, before semantic lifting.
  // Control instructions without the implicit PC/FOP pair are untouched.
  if(ins.operands.size()>=2){
    auto& ip=ins.operands[ins.operands.size()-2];auto& fop=ins.operands.back();
    if(ip.type==remill::Operand::kTypeRegister&&ip.reg.name=="PC"&&fop.type==remill::Operand::kTypeImmediate&&fop.size==16){
      size_t n=0;
      for(;n<ins.bytes.size();++n){unsigned b=uint8_t(ins.bytes[n]);if((b>=0x40&&b<=0x4f)||b==0x66||b==0x67||b==0x26||b==0x2e||b==0x36||b==0x3e||b==0x64||b==0x65||b==0xf0||b==0xf2||b==0xf3)continue;break;}
      if(n+1>=ins.bytes.size()||(uint8_t(ins.bytes[n])&0xf8)!=0xd8)reject("implicit x87 opcode operand without an exact escape/ModRM pair");
      uint16_t opcode=uint16_t(((uint8_t(ins.bytes[n])&7)<<8)|uint8_t(ins.bytes[n+1]));
      if(fop.imm.val!=(opcode&0x3ff)&&fop.imm.val!=opcode)reject("unexpected pinned x87 opcode decoder output");
      x87_opcodes[pc]={uint16_t(fop.imm.val),opcode};fop.imm.val=opcode;
    }
  }
}
void bb_sparse_instruction_lifted(uint64_t pc,int status) {
  if(status!=int(remill::kLiftedInstruction))reject("unsupported Remill instruction semantics at "+std::to_string(pc));
  decoded.insert(pc);
}

// Only manifest-declared UD2 becomes an explicit native fault boundary.
bool bb_sparse_emit_trap(const remill::Instruction& ins,llvm::BasicBlock* block,const remill::IntrinsicTable& intrinsics){
  if(ins.function!="UD2"||!declared_traps.count(ins.pc))return false;
  auto* module=block->getModule();
  auto callee=module->getOrInsertFunction("__bb_native_ud2",intrinsics.error->getFunctionType());
  auto* function=llvm::cast<llvm::Function>(callee.getCallee());function->setCallingConv(intrinsics.error->getCallingConv());function->addFnAttr(llvm::Attribute::NoReturn);
  remill::StoreNextProgramCounter(block,llvm::ConstantInt::get(llvm::Type::getInt64Ty(block->getContext()),ins.pc));
  remill::AddTerminatingTailCall(block,callee.getCallee(),intrinsics);emitted_traps.insert(ins.pc);return true;
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
  if(argc!=5&&argc!=6){llvm::errs()<<"usage: bb-sparse-lift input.json output.bc output.ll report.json [semantics_directory]\n";return 2;}
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
    if(auto* value=object->get("native_traps")){
      auto* traps=value->getAsArray();if(!traps)reject("native_traps must be an array");
      for(auto& value:*traps){
        auto* row=value.getAsObject();if(!row)reject("invalid native trap row");auto pc=number(*row,"address");auto kind=row->getString("kind");
        if(!kind||*kind!="ud2"||!instructions.count(pc)||instructions.at(pc)!=std::string("\x0f\x0b",2)||!declared_traps.insert(pc).second)reject("native trap must identify exact unique UD2 bytes");
      }
    }
    std::vector<uint64_t> roots;std::set<uint64_t> unique;
    for(auto& value:*roots_json){auto at=value.getAsInteger();if(!at||*at<0||!instructions.count(uint64_t(*at))||!unique.insert(uint64_t(*at)).second)reject("invalid/duplicate/unmapped root");roots.push_back(uint64_t(*at));}
    llvm::LLVMContext context;auto arch=remill::Arch::Get(context,"windows","amd64_avx");
    std::vector<std::filesystem::path> semantics_dirs;
    if(argc==6){
      auto dir=std::filesystem::absolute(argv[5]);
      if(!std::filesystem::is_regular_file(dir/"amd64_avx.bc"))reject("explicit semantics module is missing");
      semantics_dirs.push_back(dir);
    }
    std::unique_ptr<llvm::Module> module(remill::LoadArchSemantics(arch.get(),semantics_dirs));
    remill::IntrinsicTable intrinsics(module.get());Manager manager(arch.get(),module.get());
    remill::TraceLifter lifter(arch.get(),manager);
    for(auto pc:roots){manager.active=pc;if(!lifter.Lift(pc))reject("trace lifting failed");}
    llvm::json::Array missing_rows,unvisited,decoded_rows,trace_rows,trap_rows,opcode_rows;
    for(const auto& row:x87_opcodes)opcode_rows.push_back(llvm::json::Object{{"address",int64_t(row.first)},{"original",int64_t(row.second.original)},{"corrected",int64_t(row.second.corrected)}});
    if(emitted_traps!=declared_traps)reject("declared native trap was not emitted");
    for(auto pc:emitted_traps)trap_rows.push_back(int64_t(pc));
    for(auto pc:missing)missing_rows.push_back(int64_t(pc));
    for(auto pc:decoded)decoded_rows.push_back(int64_t(pc));
    for(auto& row:instructions)if(!decoded.count(row.first))unvisited.push_back(int64_t(row.first));
    std::map<uint64_t,llvm::Function*> ordered(manager.traces.begin(),manager.traces.end());
    for(auto& row:ordered)trace_rows.push_back(int64_t(row.first));
    auto unvisited_count=unvisited.size();
    llvm::json::Object report{{"schema",1},{"input_instructions",int64_t(instructions.size())},{"input_bytes",int64_t(memory.size())},
      {"x87_opcode_immediates",std::move(opcode_rows)},{"explicit_native_trap_addresses",std::move(trap_rows)},{"semantic_instruction_count",int64_t(decoded.size()-emitted_traps.size())},
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
