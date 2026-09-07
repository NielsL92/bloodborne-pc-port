// SPDX-License-Identifier: GPL-2.0-or-later
#include "mutexattr.h"
#include <new>
#include <stdexcept>
namespace bb_runtime {
static constexpr uint32_t Invalid=0x80020016u,NoMemory=0x8002000cu;
struct Locked {CRITICAL_SECTION* lock;explicit Locked(CRITICAL_SECTION& l)noexcept:lock(&l){EnterCriticalSection(lock);}~Locked()noexcept{LeaveCriticalSection(lock);}};
MutexAttributes::MutexAttributes(AddressSpace& s,size_t limit):space_(&s),limit_(limit){if(!limit)throw std::runtime_error("zero native attribute limit");InitializeCriticalSection(&lock_);}
MutexAttributes::~MutexAttributes(){DeleteCriticalSection(&lock_);}
void MutexAttributes::validate(Memory* m)noexcept{context(m);if(m->space!=space_)fault(m,"mutex-attribute-context",52);}
uint32_t MutexAttributes::initialize(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;m->space->check(m,cell,8,true);Locked locked(lock_);
 // Reinitialization is outside the supported lifecycle; do not leak a live object.
 for(const auto& item:live_)if(item.second.owner_cell==cell)fault(m,"mutex-attribute-live-reinitialize",53,0,cell);
 if(live_.size()>=limit_||next_>=MUTEX_ATTR_END)return NoMemory;
 uint64_t token=next_;try{live_.emplace(token,MutexAttribute{cell});}catch(const std::bad_alloc&){return NoMemory;}
 next_+=16;m->space->write(m,cell,&token,8);return 0;
}
uint32_t MutexAttributes::set_type(Memory* m,uint64_t cell,uint32_t type)noexcept{
 validate(m);if(!cell||type<1||type>4)return Invalid;Locked locked(lock_);uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);if(it==live_.end())return Invalid;it->second.type=type;return 0;
}
uint32_t MutexAttributes::destroy(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;Locked locked(lock_);uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);if(it==live_.end())return Invalid;m->space->check(m,cell,8,true);token=0;m->space->write(m,cell,&token,8);live_.erase(it);return 0;
}
uint32_t MutexAttributes::snapshot(Memory* m,uint64_t cell,MutexAttribute& out)noexcept{
 validate(m);if(!cell)return Invalid;Locked locked(lock_);uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);if(it==live_.end())return Invalid;out=it->second;return 0;
}
static MutexAttributes& attributes(State* s,Memory* m)noexcept{context(m,s);if(!m->mutex_attributes)fault(m,"unconfigured-mutex-attributes",54,s->gpr.rip.qword);return *m->mutex_attributes;}
Memory* mutexattr_init(State* s,uint64_t,Memory* m)noexcept{auto result=attributes(s,m).initialize(m,s->gpr.rdi.qword);s->gpr.rax.qword=result;return return_from_import(s,m);}
Memory* mutexattr_settype(State* s,uint64_t,Memory* m)noexcept{auto result=attributes(s,m).set_type(m,s->gpr.rdi.qword,uint32_t(s->gpr.rsi.qword));s->gpr.rax.qword=result;return return_from_import(s,m);}
Memory* mutexattr_destroy(State* s,uint64_t,Memory* m)noexcept{auto result=attributes(s,m).destroy(m,s->gpr.rdi.qword);s->gpr.rax.qword=result;return return_from_import(s,m);}
}
