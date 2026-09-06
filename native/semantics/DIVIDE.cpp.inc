// SPDX-License-Identifier: Apache-2.0
// Use unsigned magnitudes so signed minimum / -1 never reaches C/LLVM sdiv UB.
// Preserve the faulting PC and all destination state until checks complete.
extern "C" [[noreturn]] void __bb_native_divide_fault(Memory*,State*,uint32_t,uint32_t);
// BB_REPLACE_SELECTOR: IDIV_MEMb
// BB_REPLACE_SELECTOR: IDIV_GPR8
// BB_REPLACE_SELECTOR: IDIV_MEMv_8
// BB_REPLACE_SELECTOR: IDIV_MEMv_16
// BB_REPLACE_SELECTOR: IDIV_MEMv_32
// BB_REPLACE_SELECTOR: IDIV_MEMv_64
// BB_REPLACE_SELECTOR: IDIV_GPRv_8
// BB_REPLACE_SELECTOR: IDIV_GPRv_16
// BB_REPLACE_SELECTOR: IDIV_GPRv_32
// BB_REPLACE_SELECTOR: IDIV_GPRv_64
// BB_REPLACE_SELECTOR: DIV_MEMb
// BB_REPLACE_SELECTOR: DIV_GPR8
// BB_REPLACE_SELECTOR: DIV_MEMv_8
// BB_REPLACE_SELECTOR: DIV_MEMv_16
// BB_REPLACE_SELECTOR: DIV_MEMv_32
// BB_REPLACE_SELECTOR: DIV_MEMv_64
// BB_REPLACE_SELECTOR: DIV_GPRv_8
// BB_REPLACE_SELECTOR: DIV_GPRv_16
// BB_REPLACE_SELECTOR: DIV_GPRv_32
// BB_REPLACE_SELECTOR: DIV_GPRv_64

namespace {
#define BB_DIV_BODY(NAME,WIDTH,NARROW,WIDE,LOW,HIGH,QUOT,REM,SIGNED) \
 template<typename S> DEF_SEM(NAME,S src,PC next_pc){ \
  WIDE low=WIDE(Read(LOW)),high=WIDE(Read(HIGH)); \
  WIDE rhs=WIDE(Read(src)),lhs=(high<<WIDTH)|low; \
  constexpr WIDE sign=WIDE(1)<<(WIDTH-1),mask=(WIDE(1)<<WIDTH)-1; \
  if(!rhs)__bb_native_divide_fault(memory,&state,1,WIDTH); \
  bool negative_lhs=SIGNED&&(high&sign),negative_rhs=SIGNED&&(rhs&sign); \
  if(negative_lhs)lhs=WIDE(WIDE(0)-lhs); \
  if(negative_rhs)rhs=WIDE(WIDE(0)-rhs)&mask; \
  WIDE quotient=lhs/rhs,remainder=lhs%rhs; \
  bool negative_quotient=negative_lhs!=negative_rhs; \
  WIDE limit=SIGNED?(negative_quotient?sign:sign-1):mask; \
  if(quotient>limit)__bb_native_divide_fault(memory,&state,2,WIDTH); \
  if(negative_quotient)quotient=WIDE(WIDE(0)-quotient); \
  if(negative_lhs)remainder=WIDE(WIDE(0)-remainder); \
  WriteZExt(QUOT,NARROW(quotient));WriteZExt(REM,NARROW(remainder)); \
  WriteZExt(REG_PC,Read(next_pc));ClearArithFlags();return memory; \
 }
#define BB_DIV_FOR_SIGN(PREFIX,SIGNED) \
 BB_DIV_BODY(PREFIX##ax,8,uint8_t,uint16_t,REG_AL,REG_AH,REG_AL,REG_AH,SIGNED) \
 BB_DIV_BODY(PREFIX##dxax,16,uint16_t,uint32_t,REG_AX,REG_DX,REG_AX,REG_DX,SIGNED) \
 BB_DIV_BODY(PREFIX##edxeax,32,uint32_t,uint64_t,REG_EAX,REG_EDX,REG_XAX,REG_XDX,SIGNED) \
 BB_DIV_BODY(PREFIX##rdxrax,64,uint64_t,uint128_t,REG_RAX,REG_RDX,REG_RAX,REG_RDX,SIGNED)
BB_DIV_FOR_SIGN(BB_DIV,false)
BB_DIV_FOR_SIGN(BB_IDIV,true)
#undef BB_DIV_FOR_SIGN
#undef BB_DIV_BODY
}
DEF_ISEL(IDIV_MEMb)=BB_IDIVax<M8>;
DEF_ISEL(IDIV_GPR8)=BB_IDIVax<R8>;
DEF_ISEL(IDIV_MEMv_8)=BB_IDIVax<M8>;
DEF_ISEL(IDIV_MEMv_16)=BB_IDIVdxax<M16>;
DEF_ISEL(IDIV_MEMv_32)=BB_IDIVedxeax<M32>;
DEF_ISEL(IDIV_MEMv_64)=BB_IDIVrdxrax<M64>;
DEF_ISEL(IDIV_GPRv_8)=BB_IDIVax<R8>;
DEF_ISEL(IDIV_GPRv_16)=BB_IDIVdxax<R16>;
DEF_ISEL(IDIV_GPRv_32)=BB_IDIVedxeax<R32>;
DEF_ISEL(IDIV_GPRv_64)=BB_IDIVrdxrax<R64>;
DEF_ISEL(DIV_MEMb)=BB_DIVax<M8>;
DEF_ISEL(DIV_GPR8)=BB_DIVax<R8>;
DEF_ISEL(DIV_MEMv_8)=BB_DIVax<M8>;
DEF_ISEL(DIV_MEMv_16)=BB_DIVdxax<M16>;
DEF_ISEL(DIV_MEMv_32)=BB_DIVedxeax<M32>;
DEF_ISEL(DIV_MEMv_64)=BB_DIVrdxrax<M64>;
DEF_ISEL(DIV_GPRv_8)=BB_DIVax<R8>;
DEF_ISEL(DIV_GPRv_16)=BB_DIVdxax<R16>;
DEF_ISEL(DIV_GPRv_32)=BB_DIVedxeax<R32>;
DEF_ISEL(DIV_GPRv_64)=BB_DIVrdxrax<R64>;
