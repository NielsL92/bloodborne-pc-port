// SPDX-License-Identifier: GPL-2.0-or-later
// Contract-only state promotion. Input must first be canonicalized with LLVM O2.
// Guest memory cannot alias State. No asynchronous observation or exception recovery
// inside a promoted region. All recognized calls synchronize the external State.
#include <algorithm>
#include <cstdlib>
#include <vector>
#include <llvm/Analysis/ValueTracking.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/IntrinsicInst.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/Verifier.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/FileSystem.h>
using namespace llvm;
struct Access { Instruction* inst; Value* pointer; int64_t offset; uint64_t size; bool write; };
struct Range { int64_t lo, hi; AllocaInst* local = nullptr; };
[[noreturn]] static void reject(const Twine& why) {
    errs() << "REJECT: " << why << "\n"; std::exit(2);
}
// Explicit logical nonlocal exits; never unwind through LLVM nounwind frames.
static void add_control_exits(Function& f) {
    SmallVector<CallInst*,16> calls;
    for(auto& i:instructions(f)) if(auto* c=dyn_cast<CallInst>(&i)) {
        auto* callee=c->getCalledFunction();
        if(callee && (callee->getName().starts_with("sub_") ||
                      callee->getName()=="__remill_function_call")) calls.push_back(c);
    }
    auto& context=f.getContext();
    auto check=f.getParent()->getOrInsertFunction("__bb_is_nonlocal",
        FunctionType::get(Type::getInt1Ty(context),{PointerType::getUnqual(context)},false));
    for(auto* c:calls) {
        if(c->isMustTailCall() || !c->getType()->isPointerTy()) reject("invalid nonlocal boundary");
        c->setTailCallKind(CallInst::TCK_None);
        auto* block=c->getParent();
        auto* next=block->splitBasicBlock(c->getNextNode(),"continue_local");
        block->getTerminator()->eraseFromParent();
        auto* escape=BasicBlock::Create(context,"propagate_nonlocal",&f,next);
        IRBuilder<> b(block);
        auto* pending=b.CreateCall(check,{c});
        b.CreateCondBr(pending,escape,next);
        b.SetInsertPoint(escape);b.CreateRet(c);
    }
    outs()<<"control_checks="<<calls.size()<<"\n";
}
static void promote(Function& f) {
    if (f.arg_size() != 3 || !f.getArg(0)->getType()->isPointerTy())
        reject("unexpected lifted function signature");
    auto* state = f.getArg(0);
    auto& dl = f.getParent()->getDataLayout();
    std::vector<Access> accesses;
    std::vector<CallInst*> boundaries;
    std::vector<ReturnInst*> returns;
    // Audit the complete derived-pointer use graph before changing anything.
    SmallVector<Value*,32> work{state};
    SmallPtrSet<Value*,32> seen;
    while (!work.empty()) {
        Value* p = work.pop_back_val();
        if (!seen.insert(p).second) continue;
        int64_t off = 0;
        if (GetPointerBaseWithConstantOffset(p, off, dl) != state)
            reject("nonconstant state pointer");
        for (User* u : p->users()) {
            if (isa<GetElementPtrInst>(u) || isa<BitCastInst>(u)) {
                work.push_back(cast<Value>(u)); continue;
            }
            if (auto* l = dyn_cast<LoadInst>(u)) {
                if (l->getPointerOperand() != p || l->isVolatile() || l->isAtomic())
                    reject("nonordinary state load");
                auto size = dl.getTypeStoreSize(l->getType());
                if (size.isScalable()) reject("scalable state load");
                accesses.push_back({l,p,off,size.getFixedValue(),false}); continue;
            }
            if (auto* s = dyn_cast<StoreInst>(u)) {
                if (s->getPointerOperand() != p || s->getValueOperand() == p ||
                    s->isVolatile() || s->isAtomic()) reject("state escape/atomic store");
                auto size = dl.getTypeStoreSize(s->getValueOperand()->getType());
                if (size.isScalable()) reject("scalable state store");
                accesses.push_back({s,p,off,size.getFixedValue(),true}); continue;
            }
            if (auto* mem = dyn_cast<MemIntrinsic>(u)) {
                auto* length = dyn_cast<ConstantInt>(mem->getLength());
                if (mem->isVolatile() || !length) reject("nonconstant/volatile state memory intrinsic");
                bool dest = mem->getRawDest() == p;
                auto* transfer = dyn_cast<MemTransferInst>(mem);
                if (!dest && (!transfer || transfer->getRawSource()!=p))
                    reject("unrecognized state memory intrinsic use");
                accesses.push_back({mem,p,off,length->getZExtValue(),dest}); continue;
            }
            if (auto* call = dyn_cast<CallInst>(u)) {
                auto* target = call->getCalledFunction();
                if (p != state || !target || call->arg_size()!=3 || call->getArgOperand(0)!=state ||
                    !(target->getName().starts_with("sub_") ||
                      target->getName().starts_with("__remill_function_") ||
                      (target->getName()=="__remill_error" || target->getName()=="__remill_jump")))
                    reject("unrecognized state control boundary");
                continue;
            }
            reject("state pointer escape or unsupported use");
        }
    }
    for (auto& i : instructions(f)) {
        if (auto* r = dyn_cast<ReturnInst>(&i)) returns.push_back(r);
        if (auto* c = dyn_cast<CallInst>(&i)) {
            if (c->isMustTailCall()) reject("musttail boundary");
            auto* target = c->getCalledFunction();
            if (!target || !target->isIntrinsic()) boundaries.push_back(c);
        }
        if (isa<InvokeInst>(i) || isa<CallBrInst>(i)) reject("exceptional call boundary");
    }
    std::sort(accesses.begin(), accesses.end(), [](auto& a, auto& b){return a.offset<b.offset;});
    std::vector<Range> ranges;
    for (auto& a : accesses) {
        if (a.offset<0 || a.offset+a.size>3504) reject("state layout outside tested 3504-byte ABI");
        int64_t hi=a.offset+a.size;
        if (!ranges.empty() && a.offset<=ranges.back().hi)
            ranges.back().hi=std::max(ranges.back().hi,hi);
        else ranges.push_back({a.offset,hi});
    }
    IRBuilder<> entry(&*f.getEntryBlock().getFirstInsertionPt());
    for(auto& r:ranges)
        r.local=entry.CreateAlloca(ArrayType::get(entry.getInt8Ty(),r.hi-r.lo),nullptr,"promoted");
    auto sync = [&](Instruction* at, bool to_external) {
        IRBuilder<> b(at);
        for(auto& r:ranges) {
            auto* external=b.CreateConstGEP1_64(b.getInt8Ty(),state,r.lo);
            Value* src=to_external ? (Value*)r.local : external;
            Value* dst=to_external ? external : (Value*)r.local;
            b.CreateMemCpy(dst,MaybeAlign(1),src,MaybeAlign(1),r.hi-r.lo);
        }
    };
    // Initialize before all original instructions, after the newly created allocas.
    sync(&*entry.GetInsertPoint(),false);
    for(auto& a:accesses) {
        auto it=std::find_if(ranges.begin(),ranges.end(),[&](auto& r){
            return a.offset>=r.lo && a.offset+a.size<=r.hi;
        });
        IRBuilder<> b(a.inst);
        auto* local=b.CreateConstGEP1_64(b.getInt8Ty(),it->local,a.offset-it->lo);
        if(auto* l=dyn_cast<LoadInst>(a.inst)) l->setOperand(0,local);
        else if(auto* store=dyn_cast<StoreInst>(a.inst)) store->setOperand(1,local);
        else if(a.write) cast<MemIntrinsic>(a.inst)->setDest(local);
        else cast<MemTransferInst>(a.inst)->setSource(local);
    }
    for(auto* c:boundaries) {
        c->setTailCallKind(CallInst::TCK_None);
        sync(c,true);
        if(!c->doesNotReturn()) sync(c->getNextNode(),false);
    }
    for(auto* r:returns) sync(r,true);
    uint64_t bytes=0; for(auto& r:ranges) bytes+=r.hi-r.lo;
    outs()<<"function="<<f.getName()<<" accesses="<<accesses.size()
          <<" ranges="<<ranges.size()<<" state_bytes="<<bytes
          <<" boundaries="<<boundaries.size()<<"\n";
}
int main(int argc,char**argv) {
    if(argc!=3 && argc!=4) reject("input.ll output.ll [--control-exits] required");
    bool control=argc==4 && StringRef(argv[3])=="--control-exits";
    if(argc==4 && !control) reject("unknown option");
    LLVMContext context; SMDiagnostic diagnostic;
    auto module=parseIRFile(argv[1],diagnostic,context);
    if(!module) {diagnostic.print(argv[0],errs());return 1;}
    unsigned count=0;
    for(auto& f:*module) if(!f.isDeclaration() && f.getName().starts_with("sub_")) {
        if(control) add_control_exits(f);
        promote(f);++count;
    }
    if(!count) reject("no lifted functions");
    if(verifyModule(*module,&errs())) reject("LLVM verifier rejected transformation");
    std::error_code ec;
    raw_fd_ostream output(argv[2],ec,sys::fs::CD_CreateNew,sys::fs::FA_Write,sys::fs::OF_None);
    if(ec) reject(ec.message());
    module->print(output,nullptr);
}
