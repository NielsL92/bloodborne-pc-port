// SPDX-License-Identifier: Apache-2.0
// Read LLVM bitcode only. This program never JITs, links or executes input code.
#include <llvm/ADT/StringExtras.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/CFG.h>
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
// Read-only reaching-definition analysis for the compiler's nonescaping local
// source slot. This is not a memory model for State or guest addresses.
static bool source_slot_is_local(llvm::AllocaInst* slot){
  if(!slot||slot->getName()!="BB_SOURCE_PC")return false;
  for(auto* user:slot->users()){
    if(auto* load=llvm::dyn_cast<llvm::LoadInst>(user)){if(load->getPointerOperand()!=slot||load->isVolatile())return false;}
    else if(auto* store=llvm::dyn_cast<llvm::StoreInst>(user)){if(store->getPointerOperand()!=slot||store->getValueOperand()==slot||store->isVolatile())return false;}
    else return false;
  }
  return true;
}
static void source_definitions(llvm::BasicBlock* block,llvm::BasicBlock::iterator before,llvm::AllocaInst* slot,std::set<llvm::BasicBlock*>& seen,std::set<uint64_t>& values,bool& complete,unsigned depth=0){
  if(depth>256){complete=false;return;}
  for(auto it=before;it!=block->begin();){--it;if(auto* store=llvm::dyn_cast<llvm::StoreInst>(&*it))if(store->getPointerOperand()==slot){auto* value=llvm::dyn_cast<llvm::ConstantInt>(store->getValueOperand());if(value&&value->getBitWidth()<=64)values.insert(value->getZExtValue());else complete=false;return;}}
  if(!seen.insert(block).second)return;
  if(llvm::pred_empty(block)){complete=false;return;}
  for(auto* predecessor:llvm::predecessors(block))source_definitions(predecessor,predecessor->end(),slot,seen,values,complete,depth+1);
}
// Conservative origin sets, not correlated paths or execution coverage.
// Unsupported arithmetic/load/argument origins remain explicitly incomplete.
static void integer_origins(llvm::Value* value,std::set<llvm::Value*>& seen,std::set<uint64_t>& values,bool& complete,unsigned depth=0){
  if(depth>256||seen.size()>65536){complete=false;return;}if(!seen.insert(value).second)return;
  if(auto* c=llvm::dyn_cast<llvm::ConstantInt>(value)){if(c->getBitWidth()<=64)values.insert(c->getZExtValue());else complete=false;}
  else if(auto* phi=llvm::dyn_cast<llvm::PHINode>(value)){for(auto& input:phi->incoming_values())integer_origins(input.get(),seen,values,complete,depth+1);}
  else if(auto* select=llvm::dyn_cast<llvm::SelectInst>(value)){integer_origins(select->getTrueValue(),seen,values,complete,depth+1);integer_origins(select->getFalseValue(),seen,values,complete,depth+1);}
  else if(auto* freeze=llvm::dyn_cast<llvm::FreezeInst>(value))integer_origins(freeze->getOperand(0),seen,values,complete,depth+1);
  else if(auto* load=llvm::dyn_cast<llvm::LoadInst>(value)){
    auto* slot=llvm::dyn_cast<llvm::AllocaInst>(load->getPointerOperand());
    if(source_slot_is_local(slot)){std::set<llvm::BasicBlock*> blocks;source_definitions(load->getParent(),load->getIterator(),slot,blocks,values,complete);}else complete=false;
  } else complete=false;
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
  if(v->getType()->isIntegerTy()){
    std::set<llvm::Value*> seen;std::set<uint64_t> values;bool complete=true;integer_origins(v,seen,values,complete);llvm::json::Array origins;for(auto n:values)origins.push_back(llvm::utohexstr(n));row["possible_integer_values_hex"]=std::move(origins);row["integer_origins_complete"]=complete&&!values.empty();
  }
  return row;
}
static bool sourced_control(const std::string& name){
 return name.rfind("__bb_sourced_",0)==0&&name.rfind("__bb_sourced_read_memory_",0)!=0&&name.rfind("__bb_sourced_write_memory_",0)!=0&&name.rfind("__bb_sourced_compare_exchange_memory_",0)!=0&&name.rfind("__bb_sourced_atomic_",0)!=0&&name.rfind("__bb_sourced_barrier_",0)!=0;
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
    int64_t indirect_calls=0;std::map<std::string,int64_t> memory_counts;std::set<uint64_t> memory_sources;llvm::json::Array memory_errors;int64_t legacy_memory_calls=0;
    llvm::ModuleSlotTracker slots(module.get());
    for(auto& f:*module) {
      auto name=f.getName().str();bool boundary=controls.count(name)||name.rfind("__bb_native_",0)==0||sourced_control(name);
      if(f.isDeclaration()) {
        if(boundary)declarations.push_back(llvm::json::Object{{"name",name},{"type",type_text(f.getFunctionType())},{"calling_convention",int64_t(f.getCallingConv())},{"nounwind",f.doesNotThrow()},{"noreturn",f.doesNotReturn()},{"attributes",attrs(f)}});
        continue;
      }
      if(name.rfind("sub_",0)!=0)throw std::runtime_error("unexpected non-root definition: "+name);
      if(f.arg_size()!=3||!f.getReturnType()->isPointerTy()||!f.getArg(0)->getType()->isPointerTy()||!f.getArg(1)->getType()->isIntegerTy(64)||!f.getArg(2)->getType()->isPointerTy())throw std::runtime_error("unexpected compiled ABI");
      functions.push_back(llvm::json::Object{{"name",name},{"calling_convention",int64_t(f.getCallingConv())},{"nounwind",f.doesNotThrow()},{"noreturn",f.doesNotReturn()},{"attributes",attrs(f)}});
      std::set<llvm::BasicBlock*> reachable;std::vector<llvm::BasicBlock*> pending{&f.getEntryBlock()};
      while(!pending.empty()){auto* block=pending.back();pending.pop_back();if(!reachable.insert(block).second)continue;for(auto* successor:llvm::successors(block))pending.push_back(successor);}
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
            bool sourced=target.rfind("__bb_sourced_",0)==0;
            bool legacy_memory=target.rfind("__remill_read_memory_",0)==0||target.rfind("__remill_write_memory_",0)==0||target.rfind("__remill_compare_exchange_memory_",0)==0||target.rfind("__remill_fetch_and_",0)==0||target.rfind("__remill_atomic_",0)==0||target.rfind("__remill_barrier_",0)==0;
            if(legacy_memory)++legacy_memory_calls;
            if(sourced){
              ++memory_counts[target];std::set<llvm::Value*> seen;std::set<uint64_t> values;bool complete=true;
              if(call->arg_size()<3)complete=false;else integer_origins(call->getArgOperand(1),seen,values,complete);
              if(!complete||values.size()!=1||values.count(0)||call->getArgOperand(0)!=f.getArg(0)||!call->doesNotThrow()||call->getCallingConv()!=0||llvm::isa<llvm::InvokeInst>(call))memory_errors.push_back(llvm::json::Object{{"function",name},{"callee",target},{"block_index",block_index},{"instruction_index",instruction_index},{"complete_source",complete},{"source_count",int64_t(values.size())},{"exact_state_argument",call->arg_size()&&call->getArgOperand(0)==f.getArg(0)}});
              memory_sources.insert(values.begin(),values.end());
            }
            if(!callee||controls.count(target)||target.rfind("__bb_native_",0)==0||sourced_control(target)) {
              llvm::json::Array args;for(auto& arg:call->args())args.push_back(value_info(arg.get(),slots));
              std::string ir;llvm::raw_string_ostream printed(ir);i.print(printed,slots);
              llvm::json::Array successor_names;auto* terminator=b.getTerminator();for(unsigned k=0;k<terminator->getNumSuccessors();++k)successor_names.push_back(terminator->getSuccessor(k)->getName().str());
              sites.push_back(llvm::json::Object{{"function",name},{"cfg_reachable_from_entry",reachable.count(&b)!=0},{"block_name",b.getName().str()},{"successor_names",std::move(successor_names)},{"block_index",block_index},{"instruction_index",instruction_index},{"callee",target},{"calling_convention",int64_t(call->getCallingConv())},{"nounwind",call->doesNotThrow()},{"noreturn",call->doesNotReturn()},{"is_invoke",llvm::isa<llvm::InvokeInst>(i)},{"arguments",std::move(args)},{"ir",ir}});
              ++counts[target];
            }
          }
          ++instruction_index;
        }
        ++block_index;
      }
    }
    llvm::json::Object memory_count_json;for(const auto& row:memory_counts)memory_count_json[row.first]=row.second;
    llvm::json::Array memory_source_json;for(auto at:memory_sources)memory_source_json.push_back(llvm::utohexstr(at));
    llvm::json::Object memory_audit{{"counts",std::move(memory_count_json)},{"source_pcs",std::move(memory_source_json)},{"invalid_sites",std::move(memory_errors)},{"legacy_memory_calls",legacy_memory_calls},{"scope","All saved pre-O2 bridged call sites, including structurally unreachable blocks. Source must have one complete nonzero local constant origin; State must be the root argument. Not execution coverage."}};
    llvm::json::Object count_json;for(auto& kv:counts)count_json[kv.first]=kv.second;
    llvm::json::Object report{{"status","read-only LLVM control-site census"},{"memory_source_audit",std::move(memory_audit)},{"target_triple",module->getTargetTriple().str()},{"data_layout",module->getDataLayoutStr()},{"functions",std::move(functions)},{"declarations",std::move(declarations)},{"sites",std::move(sites)},{"site_counts",std::move(count_json)},{"indirect_llvm_calls",indirect_calls},{"execution","none; bitcode parsing and verification only"},{"integer_origin_scope","Conservative constants/PHI/select/freeze and reaching constant stores to verified nonescaping BB_SOURCE_PC allocas. Other expressions stay incomplete; sets do not retain path correlation."},{"cfg_reachability_scope","Structural paths from each LLVM function entry, including both conditional successors. This is not proof of guest execution or backend emitted machine paths."}};
    std::error_code ec;llvm::raw_fd_ostream out(argv[2],ec);if(ec)throw std::runtime_error("cannot write census");out<<llvm::formatv("{0:2}\n",llvm::json::Value(std::move(report)));
    return 0;
  }catch(const std::exception& e){llvm::errs()<<e.what()<<"\n";return 2;}
}
