#pragma once
// SPDX-License-Identifier: GPL-2.0-or-later
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <xmmintrin.h>
#include "vector_fixture.h"
static Memory guest,initial_memory;
static State guest_state,expected_state;
static void* escape[5];
static Memory* returned_memory;
static bool native_fault;
static unsigned native_raised,native_unmasked;
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory* m,State* s,uint32_t raised,uint32_t unmasked){
 if(m!=&guest||s!=&guest_state||!unmasked)fail("native fault arguments");native_fault=true;native_raised=raised;native_unmasked=unmasked;__builtin_longjmp(escape,1);
}
__attribute__((sysv_abi,disable_tail_calls,noinline)) static void invoke(Lifted fn,uint64_t pc){
 // Keep the builtin escape in a System V frame, as in the P2 fixture. The
 // Windows caller accounts for its vector clobbers; preserve shared GPRs here.
 asm volatile("" ::: "rbx","rsi","rdi","r12","r13","r14","r15","xmm6","xmm7","xmm8","xmm9","xmm10","xmm11","xmm12","xmm13","xmm14","xmm15");
 if(__builtin_setjmp(escape)==0)returned_memory=fn(&guest_state,pc,&guest);
}
struct HardwareFault {DWORD code;unsigned csr;uint8_t vectors[4][16];};
static HardwareFault fault;
static int capture(EXCEPTION_POINTERS* info){fault.code=info->ExceptionRecord->ExceptionCode;fault.csr=info->ContextRecord->MxCsr;std::memcpy(fault.vectors,&info->ContextRecord->Xmm0,sizeof fault.vectors);return EXCEPTION_EXECUTE_HANDLER;}
__declspec(noinline) static void hardware_run(Hardware fn,const void* in,void* out,const void* mem,unsigned control){
 fault={};_mm_setcsr(control);__try {fn(in,out,mem);fault.csr=_mm_getcsr();}__except(capture(GetExceptionInformation())){}_mm_setcsr(0x1f80);
}
