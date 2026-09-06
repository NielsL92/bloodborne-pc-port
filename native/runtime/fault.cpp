// SPDX-License-Identifier: GPL-2.0-or-later
#include "runtime.h"
namespace bb_runtime {
[[noreturn]] void fault(Memory* m,const char* boundary,uint32_t reason,uint64_t source,uint64_t actual,uint64_t wanted,uint64_t address,uint64_t width)noexcept{
 FILE* out=m&&m->fault_stream?m->fault_stream:stderr;State* s=m?m->state:nullptr;
 std::fprintf(out,"{\"status\":\"native-boundary-stop\",\"boundary\":\"%s\",\"reason\":%u,\"source\":\"%016llx\",\"actual\":\"%016llx\",\"wanted\":\"%016llx\",\"address\":\"%016llx\",\"width\":%llu,\"pc\":\"%016llx\",\"rsp\":\"%016llx\",\"entry\":\"%016llx\",\"thread\":%lu,\"compilation_identity\":\"%s\"}\n",boundary,reason,(unsigned long long)source,(unsigned long long)actual,(unsigned long long)wanted,(unsigned long long)address,(unsigned long long)width,(unsigned long long)(s?s->gpr.rip.qword:0),(unsigned long long)(s?s->gpr.rsp.qword:0),(unsigned long long)(m?m->entry:0),GetCurrentThreadId(),m&&m->tables?m->tables->identity:"unbound");
 if(m&&m->active_import){const auto& imp=*m->active_import;std::fprintf(out,"{\"active_import\":\"%016llx\",\"nid\":\"%s\",\"library\":\"%s\",\"module\":\"%s\"}\n",(unsigned long long)imp.pc,imp.nid,imp.library,imp.module);}
 std::fflush(out);ExitProcess(0xb0000000u|(reason&0xffffu));
}
void context(Memory* m,State* s)noexcept{
 if(!m||!m->space||!m->state||m->owner_thread!=GetCurrentThreadId()||(s&&s!=m->state))fault(m,"context",1);
 if(!m->space->sealed())fault(m,"unsealed-memory",2);
}
}
