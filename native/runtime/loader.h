// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include "runtime.h"
#include <memory>
namespace bb_runtime {
struct LoadRegion {uint64_t base,size,declared;uint32_t rights;std::vector<uint8_t> expected;};
struct LoadValidation {uint64_t mapped_bytes,verified_bytes,guarded_bytes;std::string sha256;};
class LoadedImage {
 std::vector<LoadRegion> regions_;std::vector<AccessGuard> guards_;size_t relocations_=0;
 friend std::unique_ptr<LoadedImage> load_private_image(const char*,const std::string&,const std::string&);
 public:
 AddressSpace space;
 const std::vector<AccessGuard>& guards()const noexcept{return guards_;}
 size_t region_count()const noexcept{return regions_.size();}
 size_t relocation_count()const noexcept{return relocations_;}
 // Host validation only: compare all unguarded private bytes with independently checked inputs.
 LoadValidation validate(Memory*);
};
std::unique_ptr<LoadedImage> load_private_image(const char* path,const std::string& expected_sha256,const std::string& registry_identity);
}
