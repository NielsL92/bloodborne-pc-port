// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "mutexattr.h"
#include <memory>
namespace bb_runtime {
constexpr uint64_t MUTEX_BASE=0x72000000000ULL,MUTEX_END=0x72100000000ULL;
struct MutexInfo {uint32_t type=1;DWORD owner=0;uint32_t depth=0,waiters=0;};
class Mutexes {
 struct Object {uint64_t owner_cell;MutexInfo info;CONDITION_VARIABLE changed=CONDITION_VARIABLE_INIT;};
 AddressSpace* space_;CRITICAL_SECTION lock_{};std::map<uint64_t,std::unique_ptr<Object>> live_;uint64_t next_=MUTEX_BASE+16;size_t limit_;
 void validate(Memory*)noexcept;Object* find(Memory*,uint64_t)noexcept;
 public:
 explicit Mutexes(AddressSpace&,size_t live_limit=65536);~Mutexes();Mutexes(const Mutexes&)=delete;Mutexes& operator=(const Mutexes&)=delete;
 uint32_t initialize(Memory*,uint64_t,uint64_t,uint64_t)noexcept;
 uint32_t acquire(Memory*,uint64_t,bool)noexcept;
 uint32_t release(Memory*,uint64_t)noexcept;
 uint32_t destroy(Memory*,uint64_t)noexcept;
 bool snapshot(Memory*,uint64_t,MutexInfo&)noexcept;
};
Memory* mutex_init(State*,uint64_t,Memory*)noexcept;
Memory* mutex_lock(State*,uint64_t,Memory*)noexcept;
Memory* mutex_trylock(State*,uint64_t,Memory*)noexcept;
Memory* mutex_unlock(State*,uint64_t,Memory*)noexcept;
Memory* mutex_destroy(State*,uint64_t,Memory*)noexcept;
}
