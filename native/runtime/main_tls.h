// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
namespace bb_runtime {
class MainTls {
 AddressSpace* space_;uint64_t tcb_,size_,alignment_;bool initialized_=false;
 public:
 MainTls(AddressSpace& space,uint64_t tcb,uint64_t size,uint64_t alignment):space_(&space),tcb_(tcb),size_(size),alignment_(alignment){}
 void initialize(Memory*,const uint8_t* initial,size_t file_size);
 bool initialized()const noexcept{return initialized_;}
};
}
