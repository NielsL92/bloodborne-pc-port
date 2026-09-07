// SPDX-License-Identifier: GPL-2.0-or-later
// Opaque native process word; no console seed or fixed fallback value is inferred.
#include "canary.h"
#include <bcrypt.h>
#include <stdexcept>
#pragma comment(lib,"bcrypt.lib")
namespace bb_runtime {
CanarySeed native_canary_seed(){CanarySeed seed{};if(BCryptGenRandom(nullptr,seed.data(),ULONG(seed.size()),BCRYPT_USE_SYSTEM_PREFERRED_RNG)!=0)throw std::runtime_error("native canary entropy failed");return seed;}
void ProcessCanary::initialize_from_seed(Memory* memory,const CanarySeed& seed){
 context(memory);if(initialized_||memory->space!=space_||memory->active_import||memory->active_source)throw std::runtime_error("invalid canary initialization lifecycle");
 space_->write(memory,address_,seed.data(),seed.size());initialized_=true;
}
}
