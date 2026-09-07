// SPDX-License-Identifier: GPL-2.0-or-later
#include "mutex.h"
#include <new>
#include <stdexcept>
namespace bb_runtime {
static constexpr uint32_t Invalid=0x80020016u,NoMemory=0x8002000cu,Busy=0x80020010u,Permission=0x80020001u,Deadlock=0x8002000bu,Again=0x80020023u;
struct Locked {CRITICAL_SECTION* lock;explicit Locked(CRITICAL_SECTION& l)noexcept:lock(&l){EnterCriticalSection(lock);}~Locked()noexcept{LeaveCriticalSection(lock);}};
Mutexes::Mutexes(AddressSpace& s,size_t limit):space_(&s),limit_(limit){if(!limit)throw std::runtime_error("zero native mutex limit");InitializeCriticalSection(&lock_);}
Mutexes::~Mutexes(){DeleteCriticalSection(&lock_);}
void Mutexes::validate(Memory* m)noexcept{context(m);if(m->space!=space_)fault(m,"mutex-context",55);}
Mutexes::Object* Mutexes::find(Memory* m,uint64_t cell)noexcept{uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);return it==live_.end()?nullptr:it->second.get();}
uint32_t Mutexes::initialize(Memory* m,uint64_t cell,uint64_t attribute,uint64_t name)noexcept{
 validate(m);if(!cell)return Invalid;if(name)fault(m,"named-mutex-interface-unimplemented",57,0,name);m->space->check(m,cell,8,true);MutexAttribute value{};
 if(attribute){if(!m->mutex_attributes)fault(m,"unconfigured-mutex-attributes",54);uint32_t result=m->mutex_attributes->snapshot(m,attribute,value);if(result)return result;}
 if(value.type<1||value.type>4)return Invalid;if(value.protocol)fault(m,"mutex-protocol-unimplemented",58,0,value.protocol);Locked locked(lock_);
 for(const auto& item:live_)if(item.second->owner_cell==cell)fault(m,"mutex-live-reinitialize",59,0,cell);
 if(live_.size()>=limit_||next_>=MUTEX_END)return NoMemory;uint64_t token=next_;
 try{auto object=std::make_unique<Object>();object->owner_cell=cell;object->info.type=value.type;live_.emplace(token,std::move(object));}catch(const std::bad_alloc&){return NoMemory;}
 next_+=16;m->space->write(m,cell,&token,8);return 0;
}
uint32_t Mutexes::acquire(Memory* m,uint64_t cell,bool try_only)noexcept{
 validate(m);if(!cell)return Invalid;Locked locked(lock_);auto* object=find(m,cell);if(!object){uint64_t token=0;m->space->read(m,cell,&token,8);if(token<2)fault(m,"static-mutex-initialization-unimplemented",60,0,cell);return Invalid;}auto& info=object->info;
 if(info.owner==m->owner_thread){
  if(info.type==2){if(info.depth==0x7fffffffu)return Again;++info.depth;return 0;}
  if(try_only)return Busy;if(info.type==1||info.type==4)return Deadlock;fault(m,"normal-mutex-self-deadlock",56,0,cell);
 }
 if(try_only&&info.owner)return Busy;
 while(info.owner){++info.waiters;BOOL ok=SleepConditionVariableCS(&object->changed,&lock_,INFINITE);--info.waiters;if(!ok)fault(m,"native-mutex-wait-failed",61,0,GetLastError());}
 info.owner=m->owner_thread;info.depth=1;return 0;
}
uint32_t Mutexes::release(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;Locked locked(lock_);auto* object=find(m,cell);if(!object)return Invalid;auto& info=object->info;if(info.owner!=m->owner_thread)return Permission;
 if(--info.depth==0){info.owner=0;WakeConditionVariable(&object->changed);}return 0;
}
uint32_t Mutexes::destroy(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;Locked locked(lock_);uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);if(it==live_.end())return Invalid;const auto& info=it->second->info;if(info.owner||info.waiters)return Busy;m->space->check(m,cell,8,true);uint64_t dead=2;m->space->write(m,cell,&dead,8);live_.erase(it);return 0;
}
bool Mutexes::snapshot(Memory* m,uint64_t cell,MutexInfo& info)noexcept{validate(m);if(!cell)return false;Locked locked(lock_);auto* object=find(m,cell);if(!object)return false;info=object->info;return true;}
static Mutexes& mutexes(State* s,Memory* m)noexcept{context(m,s);if(!m->mutexes)fault(m,"unconfigured-native-mutexes",62,s->gpr.rip.qword);return *m->mutexes;}
Memory* mutex_init(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=mutexes(s,m).initialize(m,s->gpr.rdi.qword,s->gpr.rsi.qword,s->gpr.rdx.qword);return return_from_import(s,m);}
Memory* mutex_lock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=mutexes(s,m).acquire(m,s->gpr.rdi.qword,false);return return_from_import(s,m);}
Memory* mutex_trylock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=mutexes(s,m).acquire(m,s->gpr.rdi.qword,true);return return_from_import(s,m);}
Memory* mutex_unlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=mutexes(s,m).release(m,s->gpr.rdi.qword);return return_from_import(s,m);}
Memory* mutex_destroy(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=mutexes(s,m).destroy(m,s->gpr.rdi.qword);return return_from_import(s,m);}
}
