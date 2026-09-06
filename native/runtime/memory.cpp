// SPDX-License-Identifier: GPL-2.0-or-later
// Registered private RAM only. All runtime/service accesses share this lock.
#include "runtime.h"
#include <algorithm>
#include <cstring>
#include <limits>
#include <stdexcept>
namespace bb_runtime {
AddressSpace::AddressSpace(){if(!InitializeCriticalSectionEx(&lock_,4000,0))throw std::runtime_error("critical section initialization");}
AddressSpace::~AddressSpace(){for(auto& region:regions_)VirtualFree(region.backing,0,MEM_RELEASE);DeleteCriticalSection(&lock_);}
const Region* AddressSpace::containing(uint64_t address)const noexcept{
 auto it=std::upper_bound(regions_.begin(),regions_.end(),address,[](uint64_t pc,const Region& r){return pc<r.base;});if(it==regions_.begin())return nullptr;--it;return address-it->base<it->size?&*it:nullptr;
}
void AddressSpace::add(uint64_t base,size_t size,uint32_t rights,const void* initial,size_t initial_size){
 if(sealed_||!size||uint64_t(size)>UINT64_MAX-base||!rights||(rights&~7u)||(rights&Write&&!(rights&Read))||(rights&Code&&rights&Write)||initial_size>size||(!initial&&initial_size))throw std::runtime_error("invalid RAM mapping");
 for(const auto& r:regions_)if(base<r.base+r.size&&r.base<base+size)throw std::runtime_error("overlapping logical mappings");
 auto* bytes=static_cast<uint8_t*>(VirtualAlloc(nullptr,size,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));if(!bytes)throw std::runtime_error("private RAM allocation");
 if(initial_size)std::memcpy(bytes,initial,initial_size);
 try{regions_.push_back({base,size,bytes,rights});}catch(...){VirtualFree(bytes,0,MEM_RELEASE);throw;}
 std::sort(regions_.begin(),regions_.end(),[](const Region& a,const Region& b){return a.base<b.base;});
}
void AddressSpace::seal(){
 if(sealed_)throw std::runtime_error("memory already sealed");
 for(auto& r:regions_){DWORD wanted=r.rights&Write?PAGE_READWRITE:r.rights&Read?PAGE_READONLY:PAGE_NOACCESS,old=0;if(!VirtualProtect(r.backing,r.size,wanted,&old))throw std::runtime_error("RAM protection");
  MEMORY_BASIC_INFORMATION info{};if(!VirtualQuery(r.backing,&info,sizeof info)||info.Protect!=wanted)throw std::runtime_error("RAM non-executable protection check");}
 sealed_=true;
}
bool AddressSpace::span(uint64_t address,size_t size,uint32_t rights)const noexcept{
 if(!size||uint64_t(size)>UINT64_MAX-address)return false;
 while(size){auto* r=containing(address);if(!r||(r->rights&rights)!=rights||(rights&Write&&r->rights&Code))return false;size_t count=static_cast<size_t>(std::min<uint64_t>(size,r->size-(address-r->base)));address+=count;size-=count;}
 return true;
}
void AddressSpace::copy(uint64_t address,void* buffer,size_t size,bool write)noexcept{
 auto* bytes=static_cast<uint8_t*>(buffer);
 while(size){auto* r=containing(address);size_t count=static_cast<size_t>(std::min<uint64_t>(size,r->size-(address-r->base)));auto* host=r->backing+(address-r->base);if(write)std::memcpy(host,bytes,count);else std::memcpy(bytes,host,count);bytes+=count;address+=count;size-=count;}
}
void AddressSpace::check(Memory* m,uint64_t address,size_t size,bool write,size_t alignment)noexcept{
 context(m);enter();if(!alignment||(alignment&(alignment-1))||address%alignment)fault(m,"memory-alignment",3,m->state->gpr.rip.qword,0,0,address,size);
 if(write&&size&&uint64_t(size)<=UINT64_MAX-address){uint64_t at=address;size_t remaining=size;while(remaining){auto* region=containing(at);if(!region)break;if(region->rights&Code)fault(m,"code-write-uncovered",7,m->state->gpr.rip.qword,0,0,address,size);size_t count=static_cast<size_t>(std::min<uint64_t>(remaining,region->size-(at-region->base)));at+=count;remaining-=count;}}
 if(!span(address,size,write?Write:Read))fault(m,write?"memory-write":"memory-read",4,m->state->gpr.rip.qword,0,0,address,size);leave();
}
void AddressSpace::read(Memory* m,uint64_t address,void* value,size_t size)noexcept{context(m);enter();check(m,address,size,false);copy(address,value,size,false);++m->operations;leave();}
void AddressSpace::write(Memory* m,uint64_t address,const void* value,size_t size)noexcept{context(m);enter();check(m,address,size,true);copy(address,const_cast<void*>(value),size,true);++m->operations;leave();}
}
#define BB_MEMORY(bits,type) \
extern "C" type __remill_read_memory_##bits(Memory* m,uint64_t at)noexcept{bb_runtime::context(m);type value;m->space->read(m,at,&value,sizeof value);return value;} \
extern "C" Memory* __remill_write_memory_##bits(Memory* m,uint64_t at,type value)noexcept{bb_runtime::context(m);m->space->write(m,at,&value,sizeof value);return m;}
BB_MEMORY(8,uint8_t) BB_MEMORY(16,uint16_t) BB_MEMORY(32,uint32_t) BB_MEMORY(64,uint64_t) BB_MEMORY(f32,float) BB_MEMORY(f64,double)
extern "C" Memory* __remill_atomic_begin(Memory* m)noexcept{bb_runtime::context(m);if(m->atomic_depth)bb_runtime::fault(m,"nested-atomic",5);m->space->enter();m->atomic_depth=1;return m;}
extern "C" Memory* __remill_atomic_end(Memory* m)noexcept{bb_runtime::context(m);if(m->atomic_depth!=1)bb_runtime::fault(m,"unpaired-atomic",6);m->atomic_depth=0;m->space->leave();return m;}
#define BB_BARRIER(kind) extern "C" Memory* __remill_barrier_##kind(Memory* m)noexcept{bb_runtime::context(m);MemoryBarrier();return m;}
BB_BARRIER(load_load) BB_BARRIER(load_store) BB_BARRIER(store_load) BB_BARRIER(store_store)
#define BB_COMPARE(bits,type) \
extern "C" Memory* __remill_compare_exchange_memory_##bits(Memory* m,uint64_t at,type& expected,type desired)noexcept{bb_runtime::context(m);m->space->enter();m->space->check(m,at,sizeof(type),true);type actual;m->space->read(m,at,&actual,sizeof actual);if(actual==expected)m->space->write(m,at,&desired,sizeof desired);expected=actual;m->space->leave();return m;}
BB_COMPARE(32,uint32_t) BB_COMPARE(64,uint64_t)
