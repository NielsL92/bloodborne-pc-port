// SPDX-License-Identifier: Apache-2.0
// Read LLVM bitcode only. This program never JITs, links or executes input code.
#include <llvm/ADT/StringExtras.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/ModuleSlotTracker.h>
#include <llvm/IR/Verifier.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/raw_ostream.h>
#include <map>
#include <set>
#include <stdexcept>
#include <string>

static std::string type_text(llvm::Type* type) {
  std::string s; llvm::raw_string_ostream out(s); type->print(out); return s;
}
static std::string attrs(const llvm::Function& f) {
  std::string s; llvm::raw_string_ostream out(s); f.getAttributes().print(out); return s;
}
static llvm::json::Object value_info(llvm::Value* v,llvm::ModuleSlotTracker& slots) {
  std::string text; llvm::raw_string_ostream out(text); v->printAsOperand(out,false,slots);
  llvm::json::Object row{{"type",type_text(v->getType())},{"operand",text}};
  if (auto* c=llvm::dyn_cast<llvm::ConstantInt>(v)) {
    row["kind"]="constant_integer";
    if(c->getBitWidth()<=64)row["value_hex"]=llvm::utohexstr(c->getZExtValue());
  } else if(auto* i=llvm::dyn_cast<llvm::Instruction>(v)) row["kind"]=i->getOpcodeName();
  else if(llvm::isa<llvm::Argument>(v))row["kind"]="argument";
  else row["kind"]="other_value";
  return row;
}
int main(int argc,char** argv) {
  if(argc!=3)return 2;
  try {
    llvm::LLVMContext context;llvm::SMDiagnostic error;
    auto module=llvm::parseIRFile(argv[1],error,context);
    if(!module){error.print(argv[0],llvm::errs());return 2;}
    if(llvm::verifyModule(*module,&llvm::errs()))throw std::runtime_error("invalid input module");
    const std::set<std::string> controls={"__remill_missing_block","__remill_function_call","__remill_function_return","__remill_jump","__remill_error","__remill_async_hyper_call","__remill_sync_hyper_call"};
    llvm::json::Array functions,sites,declarations;std::map<std::string,int64_t> counts;
    int64_t indirect_calls=0;
    llvm::ModuleSlotTracker slots(module.get());
    for(auto& f:*module) {
      auto name=f.getName().str();bool boundary=controls.count(name)||name.rfind("__bb_native_",0)==0;
      if(f.isDeclaration()) {
        if(boundary)declarations.push_back(llvm::json::Object{{"name",name},{"type",type_text(f.getFunctionType())},{"calling_convention",int64_t(f.getCallingConv())},{"nounwind",f.doesNotThrow()},{"noreturn",f.doesNotReturn()},{"attributes",attrs(f)}});
        continue;
      }
      if(name.rfind("sub_",0)!=0)throw std::runtime_error("unexpected non-root definition: "+name);
      if(f.arg_size()!=3||!f.getReturnType()->isPointerTy()||!f.getArg(0)->getType()->isPointerTy()||!f.getArg(1)->getType()->isIntegerTy(64)||!f.getArg(2)->getType()->isPointerTy())throw std::runtime_error("unexpected compiled ABI");
      functions.push_back(llvm::json::Object{{"name",name},{"calling_convention",int64_t(f.getCallingConv())},{"nounwind",f.doesNotThrow()},{"noreturn",f.doesNotReturn()},{"attributes",attrs(f)}});
      slots.incorporateFunction(f);
      int64_t block_index=0;
      for(auto& b:f) {
        int64_t instruction_index=0;
        for(auto& i:b) {
          auto* call=llvm::dyn_cast<llvm::CallBase>(&i);
          if(call) {
            auto* callee=llvm::dyn_cast<llvm::Function>(call->getCalledOperand()->stripPointerCasts());
            if(!callee)++indirect_calls;
            auto target=callee?callee->getName().str():std::string("<indirect LLVM call>");
            if(!callee||controls.count(target)||target.rfind("__bb_native_",0)==0) {
              llvm::json::Array args;for(auto& arg:call->args())args.push_back(value_info(arg.get(),slots));
              std::string ir;llvm::raw_string_ostream printed(ir);i.print(printed,slots);
              llvm::json::Array successor_names;auto* terminator=b.getTerminator();for(unsigned k=0;k<terminator->getNumSuccessors();++k)successor_names.push_back(terminator->getSuccessor(k)->getName().str());
              sites.push_back(llvm::json::Object{{"function",name},{"block_name",b.getName().str()},{"successor_names",std::move(successor_names)},{"block_index",block_index},{"instruction_index",instruction_index},{"callee",target},{"calling_convention",int64_t(call->getCallingConv())},{"nounwind",call->doesNotThrow()},{"noreturn",call->doesNotReturn()},{"is_invoke",llvm::isa<llvm::InvokeInst>(i)},{"arguments",std::move(args)},{"ir",ir}});
              ++counts[target];
            }
          }
          ++instruction_index;
        }
        ++block_index;
      }
    }
    llvm::json::Object count_json;for(auto& kv:counts)count_json[kv.first]=kv.second;
    llvm::json::Object report{{"status","read-only LLVM control-site census"},{"target_triple",module->getTargetTriple().str()},{"data_layout",module->getDataLayoutStr()},{"functions",std::move(functions)},{"declarations",std::move(declarations)},{"sites",std::move(sites)},{"site_counts",std::move(count_json)},{"indirect_llvm_calls",indirect_calls},{"execution","none; bitcode parsing and verification only"}};
    std::error_code ec;llvm::raw_fd_ostream out(argv[2],ec);if(ec)throw std::runtime_error("cannot write census");out<<llvm::formatv("{0:2}\n",llvm::json::Value(std::move(report)));
    return 0;
  }catch(const std::exception& e){llvm::errs()<<e.what()<<"\n";return 2;}
}
