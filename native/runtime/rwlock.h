// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
#include <map>
#include <memory>
namespace bb_runtime {
constexpr uint64_t RWLOCK_BASE=0x73000000000ULL,RWLOCK_END=0x73100000000ULL;
struct RwlockInfo {DWORD writer=0;uint64_t readers=0;uint32_t waiting_readers=0,waiting_writers=0;};
class Rwlocks {
 struct Object {uint64_t owner_cell;RwlockInfo info;std::map<DWORD,uint32_t> readers;CONDITION_VARIABLE changed=CONDITION_VARIABLE_INIT;};
 AddressSpace* space_;CRITICAL_SECTION lock_{};std::map<uint64_t,std::unique_ptr<Object>> live_;uint64_t next_=RWLOCK_BASE+16;size_t limit_;
 void validate(Memory*)noexcept;Object* find(Memory*,uint64_t)noexcept;
 public:
 explicit Rwlocks(AddressSpace&,size_t limit=65536);~Rwlocks();Rwlocks(const Rwlocks&)=delete;Rwlocks& operator=(const Rwlocks&)=delete;
 uint32_t initialize(Memory*,uint64_t,uint64_t,uint64_t)noexcept;
 uint32_t acquire(Memory*,uint64_t,bool write,bool try_only)noexcept;
 uint32_t release(Memory*,uint64_t)noexcept;
 uint32_t destroy(Memory*,uint64_t)noexcept;
 bool snapshot(Memory*,uint64_t,RwlockInfo&)noexcept;
};
Memory* rwlock_init(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_rdlock(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_wrlock(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_tryrdlock(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_trywrlock(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_unlock(State*,uint64_t,Memory*)noexcept;
Memory* rwlock_destroy(State*,uint64_t,Memory*)noexcept;
}
