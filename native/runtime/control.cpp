// SPDX-License-Identifier: GPL-2.0-or-later
// Static native target tables only. No instruction fetch, decoder or fallback.
#include "runtime.h"
#include <algorithm>
#include <stdexcept>
extern "C" uint64_t __remill_read_memory_64(Memory*,uint64_t)noexcept;
namespace bb_runtime {
static void trace(Memory* m,State* s,const char* event,uint64_t target)noexcept{
 if(!m->control_trace)return;
 if(m->control_trace_events++>=65536)fault(m,"control-trace-limit",51,s->gpr.rip.qword,target);
 std::fprintf(m->control_trace,"{\"event\":\"%s\",\"target\":%llu,\"pc\":%llu,\"rsp\":%llu,\"rbp\":%llu,\"rdi\":%llu,\"rsi\":%llu,\"rdx\":%llu,\"rcx\":%llu,\"r8\":%llu,\"r9\":%llu,\"rax\":%llu,\"memory_operations\":%llu}\n",event,(unsigned long long)target,(unsigned long long)s->gpr.rip.qword,(unsigned long long)s->gpr.rsp.qword,(unsigned long long)s->gpr.rbp.qword,(unsigned long long)s->gpr.rdi.qword,(unsigned long long)s->gpr.rsi.qword,(unsigned long long)s->gpr.rdx.qword,(unsigned long long)s->gpr.rcx.qword,(unsigned long long)s->gpr.r8.qword,(unsigned long long)s->gpr.r9.qword,(unsigned long long)s->gpr.rax.qword,(unsigned long long)m->operations);
 std::fflush(m->control_trace);
}
struct TraceScope {
 Memory* m;State* s;uint64_t pc;const char* end;
 TraceScope(Memory* memory,State* state,uint64_t target,const char* begin,const char* finish)noexcept:m(memory),s(state),pc(target),end(finish){trace(m,s,begin,pc);}
 ~TraceScope()noexcept{trace(m,s,end,pc);}
};
static const Target* find_target(const Tables& t,uint64_t pc)noexcept{
 if(!t.target_count)return nullptr;auto* end=t.targets+t.target_count;auto* it=std::lower_bound(t.targets,end,pc,[](const Target& target,uint64_t at){return target.pc<at;});return it!=end&&it->pc==pc?it:nullptr;
}
static const Import* find_import(const Tables& t,uint64_t pc)noexcept{
 if(!t.import_count)return nullptr;auto* end=t.imports+t.import_count;auto* it=std::lower_bound(t.imports,end,pc,[](const Import& target,uint64_t at){return target.pc<at;});return it!=end&&it->pc==pc?it:nullptr;
}
void validate_tables(const Tables& t){
 if(!t.identity||!*t.identity||(t.target_count&&!t.targets)||(t.pair_count&&!t.pairs)||(t.import_count&&!t.imports))throw std::runtime_error("invalid static table storage");
 for(size_t i=0;i<t.target_count;++i)if(!t.targets[i].function||(i&&t.targets[i-1].pc>=t.targets[i].pc))throw std::runtime_error("invalid or duplicate compiled target");
 for(size_t i=0;i<t.import_count;++i){const auto& imp=t.imports[i];if((i&&t.imports[i-1].pc>=imp.pc)||find_target(t,imp.pc)||!imp.nid||!imp.library||!imp.module||(imp.native&&imp.compiled_export)||(imp.compiled_export&&!find_target(t,imp.compiled_export)))throw std::runtime_error("invalid import identity/binding");}
 for(size_t i=0;i<t.pair_count;++i){const auto& pair=t.pairs[i];if((i&&(t.pairs[i-1].source>pair.source||(t.pairs[i-1].source==pair.source&&t.pairs[i-1].requested>=pair.requested)))||(!find_target(t,pair.requested)&&!find_import(t,pair.requested)))throw std::runtime_error("invalid source/request pair");}
}
static const Tables& tables(Memory* m)noexcept{if(!m->tables)fault(m,"unconfigured-target-tables",20);return *m->tables;}
static Memory* returned(Memory* result,Memory* expected)noexcept{if(result!=expected)fault(expected,"memory-context-return",21);return result;}
Memory* imported(State* s,uint64_t pc,Memory* m)noexcept{
 context(m,s);if(s->gpr.rip.qword!=pc)fault(m,"import-entry-pc",22,0,s->gpr.rip.qword,pc);const auto& t=tables(m);const auto* imp=find_import(t,pc);if(!imp)fault(m,"unknown-import",23,0,pc);
 TraceScope trace_scope(m,s,pc,"import","import-return");const auto* previous=m->active_import;m->active_import=imp;Memory* result=nullptr;
 if(imp->native)result=imp->native(s,pc,m);
 else if(imp->compiled_export){const auto* target=find_target(t,imp->compiled_export);if(!target)fault(m,"missing-bundled-export",24,pc,imp->compiled_export);s->gpr.rip.qword=target->pc;result=target->function(s,target->pc,m);}
 else fault(m,"unimplemented-import",25,0,pc);
 m->active_import=previous;return returned(result,m);
}
Memory* dispatch(State* s,uint64_t pc,Memory* m)noexcept{
 context(m,s);if(s->gpr.rip.qword!=pc)fault(m,"dispatch-entry-pc",26,0,s->gpr.rip.qword,pc);const auto& t=tables(m);TraceScope trace_scope(m,s,pc,"dispatch","dispatch-return");
 if(const auto* target=find_target(t,pc))return returned(target->function(s,pc,m),m);
 if(find_import(t,pc))return imported(s,pc,m);fault(m,"unknown-compiled-target",27,0,pc);
}
Memory* return_from_import(State* s,Memory* m)noexcept{
 context(m,s);uint64_t pc=__remill_read_memory_64(m,s->gpr.rsp.qword);s->gpr.rsp.qword+=8;s->gpr.rip.qword=pc;m->returned_pc=pc;return m;
}
}
extern "C" Memory* __remill_function_call(State* s,uint64_t pc,Memory* m)noexcept{return bb_runtime::dispatch(s,pc,m);}
extern "C" Memory* __remill_jump(State* s,uint64_t pc,Memory* m)noexcept{return bb_runtime::dispatch(s,pc,m);}
extern "C" Memory* __remill_function_return(State* s,uint64_t pc,Memory* m)noexcept{bb_runtime::context(m,s);if(s->gpr.rip.qword!=pc)bb_runtime::fault(m,"logical-return-pc",28,0,s->gpr.rip.qword,pc);m->returned_pc=pc;return m;}
extern "C" Memory* __bb_native_block_transfer(State* s,uint64_t target,Memory* m,uint64_t source,uint64_t requested)noexcept{
 bb_runtime::context(m,s);if(target!=requested||s->gpr.rip.qword!=target)bb_runtime::fault(m,"block-transfer-target",29,source,target,requested);if(!m->tables)bb_runtime::fault(m,"unconfigured-target-tables",20,source,target,requested);const auto& t=*m->tables;
 bool allowed=false;if(t.pair_count){auto* end=t.pairs+t.pair_count;auto* it=std::lower_bound(t.pairs,end,bb_runtime::SourcePair{source,requested},[](const bb_runtime::SourcePair& a,const bb_runtime::SourcePair& b){return a.source<b.source||(a.source==b.source&&a.requested<b.requested);});allowed=it!=end&&it->source==source&&it->requested==requested;}
 if(!allowed)bb_runtime::fault(m,"unregistered-source-transfer",30,source,target,requested);return bb_runtime::dispatch(s,target,m);
}
extern "C" [[noreturn]] void __bb_native_control_fault(State* s,uint64_t source,Memory* m,uint32_t reason,uint64_t wanted,uint64_t actual)noexcept{
 bb_runtime::context(m,s);if(reason<1||reason>3||s->gpr.rip.qword!=actual)bb_runtime::fault(m,"control-fault-identity",31,source,actual,wanted);bb_runtime::fault(m,"control-return",reason,source,actual,wanted);
}
extern "C" Memory* __remill_async_hyper_call(State* s,uint64_t pc,Memory* m)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"unimplemented-async-hypercall",32,pc,uint32_t(s->hyper_call),s->hyper_call_vector);}
extern "C" Memory* __remill_sync_hyper_call(State* s,Memory* m,uint32_t kind)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"unimplemented-sync-hypercall",33,s->gpr.rip.qword,kind);}
extern "C" [[noreturn]] Memory* __bb_native_ud2(State* s,uint64_t pc,Memory* m)noexcept{bb_runtime::context(m,s);bb_runtime::fault(m,"ud2",34,pc);}
