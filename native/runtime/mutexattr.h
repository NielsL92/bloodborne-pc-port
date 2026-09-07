// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
#include <map>
namespace bb_runtime {
// Native opaque identifiers are not host pointers or guest-readable object layouts.
constexpr uint64_t MUTEX_ATTR_BASE=0x71000000000ULL,MUTEX_ATTR_END=0x71100000000ULL;
struct MutexAttribute {uint64_t owner_cell;uint32_t type=1,protocol=0;int32_t ceiling=0;};
class MutexAttributes {
 AddressSpace* space_;CRITICAL_SECTION lock_{};std::map<uint64_t,MutexAttribute> live_;uint64_t next_=MUTEX_ATTR_BASE+16;size_t limit_;
 void validate(Memory*)noexcept;
 public:
 explicit MutexAttributes(AddressSpace&,size_t live_limit=4096);~MutexAttributes();
 MutexAttributes(const MutexAttributes&)=delete;MutexAttributes& operator=(const MutexAttributes&)=delete;
 uint32_t initialize(Memory*,uint64_t)noexcept;
 uint32_t set_type(Memory*,uint64_t,uint32_t)noexcept;
 uint32_t destroy(Memory*,uint64_t)noexcept;
 uint32_t snapshot(Memory*,uint64_t,MutexAttribute&)noexcept;
};
Memory* mutexattr_init(State*,uint64_t,Memory*)noexcept;
Memory* mutexattr_settype(State*,uint64_t,Memory*)noexcept;
Memory* mutexattr_destroy(State*,uint64_t,Memory*)noexcept;
}
