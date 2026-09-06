// SPDX-License-Identifier: GPL-2.0-or-later
// Compiler bridge: explicit State and executed instruction PC for terminating faults.
// Successful helpers preserve architectural State; scopes never surround dispatch.
#include "runtime.h"
namespace {
class SourceScope {
 Memory* memory_;bb_runtime::SourceContext source_;
 public:
 SourceScope(State* state,uint64_t pc,Memory* memory)noexcept:memory_(memory),source_{state,pc,nullptr}{
  bb_runtime::context(memory,state);source_.previous=memory->active_source;memory->active_source=&source_;
 }
 ~SourceScope()noexcept{memory_->active_source=source_.previous;}
 SourceScope(const SourceScope&)=delete;SourceScope& operator=(const SourceScope&)=delete;
};
}
extern "C" uint8_t __remill_read_memory_8(Memory* m,uint64_t address)noexcept;
extern "C" uint8_t __bb_sourced_read_memory_8(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_8(m,address);}
extern "C" Memory* __remill_write_memory_8(Memory* m,uint64_t address,uint8_t value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_8(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint8_t value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_8(m,address,value);}
extern "C" uint16_t __remill_read_memory_16(Memory* m,uint64_t address)noexcept;
extern "C" uint16_t __bb_sourced_read_memory_16(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_16(m,address);}
extern "C" Memory* __remill_write_memory_16(Memory* m,uint64_t address,uint16_t value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_16(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint16_t value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_16(m,address,value);}
extern "C" uint32_t __remill_read_memory_32(Memory* m,uint64_t address)noexcept;
extern "C" uint32_t __bb_sourced_read_memory_32(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_32(m,address);}
extern "C" Memory* __remill_write_memory_32(Memory* m,uint64_t address,uint32_t value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_32(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint32_t value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_32(m,address,value);}
extern "C" uint64_t __remill_read_memory_64(Memory* m,uint64_t address)noexcept;
extern "C" uint64_t __bb_sourced_read_memory_64(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_64(m,address);}
extern "C" Memory* __remill_write_memory_64(Memory* m,uint64_t address,uint64_t value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_64(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint64_t value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_64(m,address,value);}
extern "C" float __remill_read_memory_f32(Memory* m,uint64_t address)noexcept;
extern "C" float __bb_sourced_read_memory_f32(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_f32(m,address);}
extern "C" Memory* __remill_write_memory_f32(Memory* m,uint64_t address,float value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_f32(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,float value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_f32(m,address,value);}
extern "C" double __remill_read_memory_f64(Memory* m,uint64_t address)noexcept;
extern "C" double __bb_sourced_read_memory_f64(State* source_state,uint64_t source_pc,Memory* m,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_read_memory_f64(m,address);}
extern "C" Memory* __remill_write_memory_f64(Memory* m,uint64_t address,double value)noexcept;
extern "C" Memory* __bb_sourced_write_memory_f64(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,double value)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_write_memory_f64(m,address,value);}
extern "C" Memory* __remill_compare_exchange_memory_32(Memory* m,uint64_t address,uint32_t& expected,uint32_t desired)noexcept;
extern "C" Memory* __bb_sourced_compare_exchange_memory_32(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint32_t& expected,uint32_t desired)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_compare_exchange_memory_32(m,address,expected,desired);}
extern "C" Memory* __remill_compare_exchange_memory_64(Memory* m,uint64_t address,uint64_t& expected,uint64_t desired)noexcept;
extern "C" Memory* __bb_sourced_compare_exchange_memory_64(State* source_state,uint64_t source_pc,Memory* m,uint64_t address,uint64_t& expected,uint64_t desired)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_compare_exchange_memory_64(m,address,expected,desired);}
extern "C" Memory* __remill_atomic_begin(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_atomic_begin(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_atomic_begin(m);}
extern "C" Memory* __remill_atomic_end(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_atomic_end(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_atomic_end(m);}
extern "C" Memory* __remill_barrier_load_load(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_barrier_load_load(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_barrier_load_load(m);}
extern "C" Memory* __remill_barrier_load_store(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_barrier_load_store(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_barrier_load_store(m);}
extern "C" Memory* __remill_barrier_store_load(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_barrier_store_load(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_barrier_store_load(m);}
extern "C" Memory* __remill_barrier_store_store(Memory* m)noexcept;
extern "C" Memory* __bb_sourced_barrier_store_store(State* source_state,uint64_t source_pc,Memory* m)noexcept{SourceScope scope(source_state,source_pc,m);return __remill_barrier_store_store(m);}
extern "C" [[noreturn]] void __bb_native_divide_fault(Memory* m,State* state,uint32_t kind,uint32_t width)noexcept;
extern "C" [[noreturn]] void __bb_sourced_divide_fault(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t kind,uint32_t width)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_divide_fault(m,state,kind,width);}
extern "C" [[noreturn]] void __bb_native_mxcsr_fault(Memory* m,State* state,uint32_t value,uint32_t invalid)noexcept;
extern "C" [[noreturn]] void __bb_sourced_mxcsr_fault(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t value,uint32_t invalid)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_mxcsr_fault(m,state,value,invalid);}
extern "C" uint32_t __bb_native_mxcsr_mask(Memory* m,State* state)noexcept;
extern "C" uint32_t __bb_sourced_mxcsr_mask(State* source_state,uint64_t source_pc,Memory* m,State* state)noexcept{SourceScope scope(source_state,source_pc,m);return __bb_native_mxcsr_mask(m,state);}
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory* m,State* state,uint32_t raised,uint32_t unmasked)noexcept;
extern "C" [[noreturn]] void __bb_sourced_simd_fault(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t raised,uint32_t unmasked)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_simd_fault(m,state,raised,unmasked);}
extern "C" void __bb_native_x87_check_span(Memory* m,State* state,uint64_t address,uint32_t size,uint32_t write,uint32_t alignment)noexcept;
extern "C" void __bb_sourced_x87_check_span(State* source_state,uint64_t source_pc,Memory* m,State* state,uint64_t address,uint32_t size,uint32_t write,uint32_t alignment)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_x87_check_span(m,state,address,size,write,alignment);}
extern "C" [[noreturn]] void __bb_native_x87_fault(Memory* m,State* state,uint32_t pending)noexcept;
extern "C" [[noreturn]] void __bb_sourced_x87_fault(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t pending)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_x87_fault(m,state,pending);}
extern "C" uint64_t __bb_native_x87_image_policy(Memory* m,State* state)noexcept;
extern "C" uint64_t __bb_sourced_x87_image_policy(State* source_state,uint64_t source_pc,Memory* m,State* state)noexcept{SourceScope scope(source_state,source_pc,m);return __bb_native_x87_image_policy(m,state);}
extern "C" uint32_t __bb_native_x87_pointer_segments(Memory* m,State* state)noexcept;
extern "C" uint32_t __bb_sourced_x87_pointer_segments(State* source_state,uint64_t source_pc,Memory* m,State* state)noexcept{SourceScope scope(source_state,source_pc,m);return __bb_native_x87_pointer_segments(m,state);}
extern "C" void __bb_native_x87_record_instruction(Memory* m,State* state,uint64_t pc,uint32_t flags,uint64_t address)noexcept;
extern "C" void __bb_sourced_x87_record_instruction(State* source_state,uint64_t source_pc,Memory* m,State* state,uint64_t pc,uint32_t flags,uint64_t address)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_x87_record_instruction(m,state,pc,flags,address);}
extern "C" void __bb_native_x87_set_pointer_segments(Memory* m,State* state,uint32_t value)noexcept;
extern "C" void __bb_sourced_x87_set_pointer_segments(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t value)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_x87_set_pointer_segments(m,state,value);}
extern "C" [[noreturn]] void __bb_native_x87_unsupported(Memory* m,State* state,uint32_t kind)noexcept;
extern "C" [[noreturn]] void __bb_sourced_x87_unsupported(State* source_state,uint64_t source_pc,Memory* m,State* state,uint32_t kind)noexcept{SourceScope scope(source_state,source_pc,m);__bb_native_x87_unsupported(m,state,kind);}
