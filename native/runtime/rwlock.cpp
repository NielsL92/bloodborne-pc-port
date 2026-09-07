// SPDX-License-Identifier: GPL-2.0-or-later
#include "rwlock.h"
#include <new>
#include <stdexcept>
namespace bb_runtime {
namespace {
constexpr uint32_t Invalid=0x80020016u,NoMemory=0x8002000cu,Busy=0x80020010u,Permission=0x80020001u,Deadlock=0x8002000bu,Again=0x80020023u;
struct Locked {CRITICAL_SECTION* lock;explicit Locked(CRITICAL_SECTION& l)noexcept:lock(&l){EnterCriticalSection(lock);}~Locked()noexcept{LeaveCriticalSection(lock);}};
}
Rwlocks::Rwlocks(AddressSpace& s,size_t limit):space_(&s),limit_(limit){if(!limit)throw std::runtime_error("zero native rwlock limit");InitializeCriticalSection(&lock_);}
Rwlocks::~Rwlocks(){DeleteCriticalSection(&lock_);}
void Rwlocks::validate(Memory* m)noexcept{context(m);if(m->space!=space_)fault(m,"rwlock-context",71);}
Rwlocks::Object* Rwlocks::find(Memory* m,uint64_t cell)noexcept{uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);return it==live_.end()?nullptr:it->second.get();}
uint32_t Rwlocks::initialize(Memory* m,uint64_t cell,uint64_t attr,uint64_t name)noexcept{
 validate(m);if(!cell)return Invalid;if(attr)fault(m,"rwlock-attributes-unimplemented",74,0,attr);if(name)fault(m,"named-rwlock-unimplemented",75,0,name);m->space->check(m,cell,8,true);Locked held(lock_);
 for(const auto& item:live_)if(item.second->owner_cell==cell)fault(m,"rwlock-live-reinitialize",76,0,cell);
 if(live_.size()>=limit_||next_>=RWLOCK_END)return NoMemory;uint64_t token=next_;
 try{auto object=std::make_unique<Object>();object->owner_cell=cell;live_.emplace(token,std::move(object));}catch(const std::bad_alloc&){return NoMemory;}
 next_+=16;m->space->write(m,cell,&token,8);return 0;
}
uint32_t Rwlocks::acquire(Memory* m,uint64_t cell,bool write,bool try_only)noexcept{
 validate(m);if(!cell)return Invalid;Locked held(lock_);auto* object=find(m,cell);if(!object){uint64_t token=0;m->space->read(m,cell,&token,8);if(!token)fault(m,"static-rwlock-initialization-unimplemented",73,0,cell);return Invalid;}
 auto& info=object->info;DWORD self=m->owner_thread;auto own=object->readers.find(self);bool recursive=own!=object->readers.end();
 if(info.writer==self||(write&&recursive))return try_only?Busy:Deadlock;
 auto unavailable=[&](){return info.writer||(write?bool(info.readers):bool(info.waiting_writers&&!recursive));};
 if(try_only&&unavailable())return Busy;
 if(unavailable()){
  auto& waiting=write?info.waiting_writers:info.waiting_readers;if(waiting==0x7fffffffu)return Again;++waiting;
  while(unavailable())if(!SleepConditionVariableCS(&object->changed,&lock_,INFINITE))fault(m,"native-rwlock-wait-failed",72,0,GetLastError());
  --waiting;
 }
 if(write){info.writer=self;return 0;}
 if(info.readers==0x7fffffffu||(recursive&&own->second==0x7fffffffu))return Again;
 try{if(recursive)++own->second;else object->readers.emplace(self,1);}catch(const std::bad_alloc&){return NoMemory;}
 ++info.readers;return 0;
}
uint32_t Rwlocks::release(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;Locked held(lock_);auto* object=find(m,cell);if(!object)return Invalid;auto& info=object->info;
 if(info.writer==m->owner_thread)info.writer=0;
 else{auto it=object->readers.find(m->owner_thread);if(it==object->readers.end())return Permission;if(!--it->second)object->readers.erase(it);--info.readers;}
 WakeAllConditionVariable(&object->changed);return 0;
}
uint32_t Rwlocks::destroy(Memory* m,uint64_t cell)noexcept{
 validate(m);if(!cell)return Invalid;Locked held(lock_);uint64_t token=0;m->space->read(m,cell,&token,8);auto it=live_.find(token);if(it==live_.end())return Invalid;const auto& info=it->second->info;if(info.writer||info.readers||info.waiting_readers||info.waiting_writers)return Busy;m->space->check(m,cell,8,true);uint64_t dead=1;m->space->write(m,cell,&dead,8);live_.erase(it);return 0;
}
bool Rwlocks::snapshot(Memory* m,uint64_t cell,RwlockInfo& info)noexcept{validate(m);if(!cell)return false;Locked held(lock_);auto* object=find(m,cell);if(!object)return false;info=object->info;return true;}
static Rwlocks& rwlocks(State* s,Memory* m)noexcept{context(m,s);if(!m->rwlocks)fault(m,"unconfigured-native-rwlocks",77,s->gpr.rip.qword);return *m->rwlocks;}
Memory* rwlock_init(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).initialize(m,s->gpr.rdi.qword,s->gpr.rsi.qword,s->gpr.rdx.qword);return return_from_import(s,m);}
Memory* rwlock_rdlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).acquire(m,s->gpr.rdi.qword,false,false);return return_from_import(s,m);}
Memory* rwlock_wrlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).acquire(m,s->gpr.rdi.qword,true,false);return return_from_import(s,m);}
Memory* rwlock_tryrdlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).acquire(m,s->gpr.rdi.qword,false,true);return return_from_import(s,m);}
Memory* rwlock_trywrlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).acquire(m,s->gpr.rdi.qword,true,true);return return_from_import(s,m);}
Memory* rwlock_unlock(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).release(m,s->gpr.rdi.qword);return return_from_import(s,m);}
Memory* rwlock_destroy(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=rwlocks(s,m).destroy(m,s->gpr.rdi.qword);return return_from_import(s,m);}
}
