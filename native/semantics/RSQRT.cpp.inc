// SPDX-License-Identifier: Apache-2.0
// Approximation is delegated to the LLVM x86 SSE rsqrt intrinsic, not 1/sqrt.
// This follows the host ISA contract; AMD Jaguar bit-exact estimates are unknown.
namespace {
using BB_Rsqrt4=float __attribute__((vector_size(16)));
template <typename D,typename S>
DEF_SEM(BB_VRSQRTPS,D dst,S src){
  auto input=UReadV32(src);auto result=UClearV32(input);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);i+=4){
    BB_Rsqrt4 packed;__builtin_memcpy(&packed,&input.elems[i],16);
    auto estimate=__builtin_ia32_rsqrtps(packed);
    __builtin_memcpy(&result.elems[i],&estimate,16);
  }
  UWriteV32(dst,result);return memory;
}
}
DEF_ISEL(VRSQRTPS_XMMdq_XMMdq)=BB_VRSQRTPS<VV128W,V128>;
DEF_ISEL(VRSQRTPS_XMMdq_MEMdq)=BB_VRSQRTPS<VV128W,MV128>;
DEF_ISEL(VRSQRTPS_YMMqq_YMMqq)=BB_VRSQRTPS<VV256W,V256>;
DEF_ISEL(VRSQRTPS_YMMqq_MEMqq)=BB_VRSQRTPS<VV256W,MV256>;
