// SPDX-License-Identifier: Apache-2.0
// Canonical guest CSR only. The runtime supplies the guest feature mask and
// owns delivery of the reserved-bit #GP boundary (distinct from SIMD #XM).
// BB_REPLACE_SELECTOR: LDMXCSR_MEMd
// BB_REPLACE_SELECTOR: STMXCSR_MEMd
// BB_REPLACE_SELECTOR: VLDMXCSR_MEMd
// BB_REPLACE_SELECTOR: VSTMXCSR_MEMd
extern "C" uint32_t __bb_native_mxcsr_mask(Memory*,State*);
extern "C" [[noreturn]] void __bb_native_mxcsr_fault(Memory*,State*,uint32_t,uint32_t);
namespace {
DEF_SEM(BBLoadMxcsr,M32 src){
 const uint32_t value=Read(src);const uint32_t mask=__bb_native_mxcsr_mask(memory,&state);const uint32_t invalid=value&~mask;
 if(invalid)__bb_native_mxcsr_fault(memory,&state,value,invalid);
 state.x87.fxsave.mxcsr.flat=value;return memory;
}
DEF_SEM(BBStoreMxcsr,M32W dst){Write(dst,state.x87.fxsave.mxcsr.flat);return memory;}
}
DEF_ISEL(LDMXCSR_MEMd)=BBLoadMxcsr;
DEF_ISEL(STMXCSR_MEMd)=BBStoreMxcsr;
DEF_ISEL(VLDMXCSR_MEMd)=BBLoadMxcsr;
DEF_ISEL(VSTMXCSR_MEMd)=BBStoreMxcsr;
