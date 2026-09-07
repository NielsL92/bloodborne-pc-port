// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
#include <map>
namespace bb_runtime {
constexpr uint64_t DIRECT_MAP_BASE=0x1000000000ULL,DIRECT_MAP_END=0x8000000000ULL,DIRECT_PAGE=0x4000;
class DirectMemory {
 struct Block {uint64_t size;uint32_t type;uint64_t mappings=0;};
 AddressSpace* space_;std::shared_ptr<void> backing_;uint64_t size_,next_map_=DIRECT_MAP_BASE;std::map<uint64_t,Block> blocks_;CRITICAL_SECTION lock_{};
 void validate(Memory*)noexcept;
 public:
 explicit DirectMemory(AddressSpace&,uint64_t);~DirectMemory();DirectMemory(const DirectMemory&)=delete;DirectMemory& operator=(const DirectMemory&)=delete;
 uint64_t size()const noexcept{return size_;}
 uint32_t allocate(Memory*,uint64_t,uint64_t,uint64_t,uint64_t,uint32_t,uint64_t)noexcept;
 uint32_t map(Memory*,uint64_t,uint64_t,uint32_t,uint32_t,uint64_t,uint64_t)noexcept;
 uint32_t release(Memory*,uint64_t,uint64_t)noexcept;
};
Memory* direct_memory_size(State*,uint64_t,Memory*)noexcept;
Memory* direct_memory_allocate(State*,uint64_t,Memory*)noexcept;
Memory* direct_memory_map(State*,uint64_t,Memory*)noexcept;
Memory* direct_memory_release(State*,uint64_t,Memory*)noexcept;
}
