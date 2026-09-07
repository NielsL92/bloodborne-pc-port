// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
#include <array>
namespace bb_runtime {
using CanarySeed=std::array<uint8_t,8>;
CanarySeed native_canary_seed();
class ProcessCanary {
 AddressSpace* space_;uint64_t address_;bool initialized_=false;
 public:
 ProcessCanary(AddressSpace& space,uint64_t address):space_(&space),address_(address){}
 void initialize_from_seed(Memory*,const CanarySeed&);
 bool initialized()const noexcept{return initialized_;}
};
}
