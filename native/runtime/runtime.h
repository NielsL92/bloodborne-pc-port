// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <vector>
#include <memory>
#include <string>
#include <remill/Arch/X86/Runtime/State.h>
struct Memory;
namespace bb_runtime {
class MutexAttributes;class Mutexes;class DirectMemory;
class Rwlocks;
using Lifted=Memory*(*)(State*,uint64_t,Memory*);
enum Rights:uint32_t {Read=1,Write=2,Code=4};
struct SourceContext {State* state;uint64_t pc;const SourceContext* previous;};
struct AccessGuard {uint64_t base,size;std::string identity;};
struct Region {uint64_t base,size;uint8_t* backing;uint32_t rights;std::shared_ptr<void> backing_owner;};
struct Target {uint64_t pc;Lifted function;};
struct SourcePair {uint64_t source,requested;};
struct Import {uint64_t pc;const char* nid;const char* library;const char* module;Lifted native;uint64_t compiled_export;};
struct Tables {const Target* targets;size_t target_count;const SourcePair* pairs;size_t pair_count;const Import* imports;size_t import_count;const char* identity;};
enum class Segment:uint8_t {None,ES,CS,SS,DS,FS,GS};
struct X87Site {uint64_t pc;uint16_t fop;Segment data_segment;};
struct FpProfile {const char* identity;uint64_t image_policy;uint32_t mxcsr_mask;const X87Site* sites;size_t site_count;};
void validate_fp_profile(const FpProfile&);
class AddressSpace {
 std::vector<Region> regions_;std::vector<AccessGuard> guards_;CRITICAL_SECTION lock_{};bool sealed_=false;
 const Region* containing(uint64_t)const noexcept;
 bool span(uint64_t,size_t,uint32_t)const noexcept;
 void copy(uint64_t,void*,size_t,bool) noexcept;
 public:
 AddressSpace();~AddressSpace();AddressSpace(const AddressSpace&)=delete;AddressSpace& operator=(const AddressSpace&)=delete;
 // Host setup only; copies are private and never executable.
 void add(uint64_t,size_t,uint32_t,const void* initial=nullptr,size_t initial_size=0);
 void guard(uint64_t,size_t,const std::string& identity);
 // Append a checked private NX data mapping; existing mappings/guards stay immutable.
 bool map_private(Memory*,uint64_t,size_t,uint32_t,void*,const std::shared_ptr<void>&)noexcept;
 size_t guard_count()const noexcept{return guards_.size();}
 void seal();bool sealed()const noexcept{return sealed_;}
 void enter()noexcept{EnterCriticalSection(&lock_);}void leave()noexcept{LeaveCriticalSection(&lock_);}
 void check(Memory*,uint64_t,size_t,bool,size_t alignment=1)noexcept;
 void read(Memory*,uint64_t,void*,size_t)noexcept;
 void write(Memory*,uint64_t,const void*,size_t)noexcept;
};
[[noreturn]] void fault(Memory*,const char* boundary,uint32_t reason,uint64_t source=0,uint64_t actual=0,uint64_t wanted=0,uint64_t address=0,uint64_t width=0) noexcept;
void context(Memory*,State* expected=nullptr)noexcept;
void validate_tables(const Tables&);
Memory* dispatch(State*,uint64_t,Memory*)noexcept;
Memory* imported(State*,uint64_t,Memory*)noexcept;
Memory* return_from_import(State*,Memory*)noexcept;
}
struct Memory {
 bb_runtime::AddressSpace* space=nullptr;State* state=nullptr;const bb_runtime::Tables* tables=nullptr;
 uint64_t entry=0,returned_pc=0,operations=0;DWORD owner_thread=0;unsigned atomic_depth=0;
 FILE* fault_stream=stderr;
 // Optional bounded diagnostic stream; disabled in ordinary runtime contexts.
 FILE* control_trace=nullptr;uint64_t control_trace_events=0;
 const bb_runtime::Import* active_import=nullptr;
 const bb_runtime::AccessGuard* active_guard=nullptr;
 const bb_runtime::SourceContext* active_source=nullptr;
 bb_runtime::MutexAttributes* mutex_attributes=nullptr;bb_runtime::Mutexes* mutexes=nullptr;bb_runtime::DirectMemory* direct_memory=nullptr;
  bb_runtime::Rwlocks* rwlocks=nullptr;
 const bb_runtime::FpProfile* fp_profile=nullptr;uint32_t pointer_segments=0;
};
