// SPDX-License-Identifier: GPL-2.0-or-later
#include "direct_memory.h"
#include <algorithm>
#include <new>
#include <stdexcept>
namespace bb_runtime {
namespace {
constexpr uint32_t Invalid=0x80020016u,Again=0x80020023u,NoMemory=0x8002000cu;
struct Locked {CRITICAL_SECTION* lock;explicit Locked(CRITICAL_SECTION& l)noexcept:lock(&l){EnterCriticalSection(lock);}~Locked()noexcept{LeaveCriticalSection(lock);}};
bool alignment_ok(uint64_t value)noexcept{return value>=DIRECT_PAGE&&!(value&(value-1));}
uint64_t aligned(uint64_t value,uint64_t alignment)noexcept{if(value>UINT64_MAX-(alignment-1))return UINT64_MAX;return (value+alignment-1)&~(alignment-1);}
}
DirectMemory::DirectMemory(AddressSpace& space,uint64_t size):space_(&space),size_(size){
 if(!size||size%DIRECT_PAGE||size>8ULL*1024*1024*1024)throw std::runtime_error("invalid native direct-memory budget");
 void* bytes=VirtualAlloc(nullptr,static_cast<size_t>(size),MEM_RESERVE,PAGE_NOACCESS);if(!bytes)throw std::runtime_error("native direct-memory reservation failed");
 backing_=std::shared_ptr<void>(bytes,[](void* p){VirtualFree(p,0,MEM_RELEASE);});InitializeCriticalSection(&lock_);
}
DirectMemory::~DirectMemory(){DeleteCriticalSection(&lock_);}
void DirectMemory::validate(Memory* m)noexcept{context(m);if(m->space!=space_)fault(m,"direct-memory-context",63);}
uint32_t DirectMemory::allocate(Memory* m,uint64_t start,uint64_t end,uint64_t length,uint64_t alignment,uint32_t type,uint64_t out)noexcept{
 validate(m);if(!out||start>INT64_MAX||end>INT64_MAX||!length||length%DIRECT_PAGE||type>10)return Invalid;if(!alignment)alignment=DIRECT_PAGE;if(!alignment_ok(alignment))return Invalid;if(type!=0)fault(m,"direct-memory-type-unimplemented",64,0,type);
 if(end<=start||end>size_||length>end-start)return Again;m->space->check(m,out,8,true);Locked locked(lock_);uint64_t at=aligned(start,alignment);
 for(const auto& item:blocks_){if(item.first+item.second.size<=at)continue;if(at<=item.first&&length<=item.first-at)break;at=aligned(item.first+item.second.size,alignment);}
 if(at>end||length>end-at)return Again;auto* bytes=static_cast<uint8_t*>(backing_.get())+at;
 if(!VirtualAlloc(bytes,static_cast<size_t>(length),MEM_COMMIT,PAGE_READWRITE))return NoMemory;
 try{blocks_.emplace(at,Block{length,type});}catch(const std::bad_alloc&){VirtualFree(bytes,static_cast<size_t>(length),MEM_DECOMMIT);return NoMemory;}
 m->space->write(m,out,&at,8);return 0;
}
uint32_t DirectMemory::map(Memory* m,uint64_t out,uint64_t length,uint32_t protection,uint32_t flags,uint64_t physical,uint64_t alignment)noexcept{
 validate(m);if(!out||!length||length%DIRECT_PAGE||physical%DIRECT_PAGE)return Invalid;if(!alignment)alignment=DIRECT_PAGE;if(!alignment_ok(alignment))return Invalid;if(protection!=3||flags)fault(m,"direct-map-mode-unimplemented",65,0,protection,flags);m->space->check(m,out,8,true);Locked locked(lock_);
 auto it=blocks_.upper_bound(physical);if(it==blocks_.begin())return Invalid;--it;if(physical-it->first>it->second.size||length>it->second.size-(physical-it->first))return Invalid;
 uint64_t requested=0;m->space->read(m,out,&requested,8);if(requested)fault(m,"direct-map-address-hint-unimplemented",66,0,requested);
 uint64_t logical=aligned(next_map_,alignment);if(logical>DIRECT_MAP_END||length>DIRECT_MAP_END-logical)return NoMemory;
 auto* bytes=static_cast<uint8_t*>(backing_.get())+physical;if(!space_->map_private(m,logical,static_cast<size_t>(length),Read|Write,bytes,backing_))return NoMemory;
 next_map_=logical+length;++it->second.mappings;m->space->write(m,out,&logical,8);return 0;
}
uint32_t DirectMemory::release(Memory* m,uint64_t physical,uint64_t length)noexcept{
 validate(m);if(physical%DIRECT_PAGE||length%DIRECT_PAGE||physical>size_||length>size_-physical)return Invalid;if(!length)return 0;Locked locked(lock_);auto it=blocks_.find(physical);if(it==blocks_.end()||it->second.size!=length)fault(m,"partial-direct-release-unimplemented",67,0,physical,length);if(it->second.mappings)fault(m,"mapped-direct-release-unimplemented",68,0,physical,length);
 if(!VirtualFree(static_cast<uint8_t*>(backing_.get())+physical,static_cast<size_t>(length),MEM_DECOMMIT))fault(m,"native-direct-decommit-failed",69,0,GetLastError());blocks_.erase(it);return 0;
}
static DirectMemory& direct(State* s,Memory* m)noexcept{context(m,s);if(!m->direct_memory)fault(m,"unconfigured-direct-memory",70,s->gpr.rip.qword);return *m->direct_memory;}
Memory* direct_memory_size(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=direct(s,m).size();return return_from_import(s,m);}
Memory* direct_memory_allocate(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=direct(s,m).allocate(m,s->gpr.rdi.qword,s->gpr.rsi.qword,s->gpr.rdx.qword,s->gpr.rcx.qword,uint32_t(s->gpr.r8.qword),s->gpr.r9.qword);return return_from_import(s,m);}
Memory* direct_memory_map(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=direct(s,m).map(m,s->gpr.rdi.qword,s->gpr.rsi.qword,uint32_t(s->gpr.rdx.qword),uint32_t(s->gpr.rcx.qword),s->gpr.r8.qword,s->gpr.r9.qword);return return_from_import(s,m);}
Memory* direct_memory_release(State* s,uint64_t,Memory* m)noexcept{s->gpr.rax.qword=direct(s,m).release(m,s->gpr.rdi.qword,s->gpr.rsi.qword);return return_from_import(s,m);}
}
