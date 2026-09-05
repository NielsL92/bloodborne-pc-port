// SPDX-License-Identifier: Apache-2.0
// Read-only decoder/selector inspection. No input instruction execution.
#include <glog/logging.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/Support/JSON.h>
#include <llvm/Support/MemoryBuffer.h>
#include <llvm/Support/raw_ostream.h>
#include <remill/Arch/Arch.h>
#include <remill/Arch/Instruction.h>
#include <remill/BC/Util.h>
#include <stdexcept>
int main(int argc,char** argv){
  google::InitGoogleLogging(argv[0]);FLAGS_logtostderr=true;
  if(argc!=3)return 2;
  try{
    auto file=llvm::MemoryBuffer::getFile(argv[1]);if(!file)throw std::runtime_error("input unreadable");
    auto parsed=llvm::json::parse((*file)->getBuffer());if(!parsed){llvm::consumeError(parsed.takeError());throw std::runtime_error("invalid JSON");}
    auto* rows=parsed->getAsArray();if(!rows)throw std::runtime_error("array required");
    llvm::LLVMContext context;auto arch=remill::Arch::Get(context,"windows","amd64_avx");auto module=remill::LoadArchSemantics(arch.get());llvm::json::Array result;
    for(auto& value:*rows){
      auto* row=value.getAsObject();if(!row)throw std::runtime_error("object required");auto pc=row->getInteger("address");auto text=row->getString("bytes");
      if(!pc||*pc<0||!text||text->empty()||text->size()%2||text->size()>30)throw std::runtime_error("invalid instruction input");
      std::string bytes;
      for(size_t i=0;i<text->size();i+=2){unsigned n=0;if(text->substr(i,2).getAsInteger(16,n))throw std::runtime_error("invalid hex");bytes.push_back(char(n));}
      remill::Instruction ins;bool ok=arch->DecodeInstruction(uint64_t(*pc),bytes,ins,arch->CreateInitialContext());
      result.push_back(llvm::json::Object{{"address",*pc},{"bytes",text->str()},{"decoded",ok},{"same_boundary",ins.bytes==bytes},{"category",int64_t(ins.category)},
        {"is_error_category",ins.category==remill::Instruction::kCategoryError},{"is_invalid_category",ins.category==remill::Instruction::kCategoryInvalid},
        {"selector",ins.function},{"selector_present",module->getGlobalVariable("ISEL_"+ins.function)!=nullptr},{"instruction",ins.Serialize()}});
    }
    std::error_code error;llvm::raw_fd_ostream out(argv[2],error);if(error)throw std::runtime_error("output unreadable");out<<llvm::formatv("{0:2}\n",llvm::json::Value(std::move(result)));
    return 0;
  }catch(const std::exception& e){llvm::errs()<<e.what()<<"\n";return 2;}
}
