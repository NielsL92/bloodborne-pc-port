// SPDX-License-Identifier: Apache-2.0
// Bit selection only: VEX upper-vector clearing is performed by VV* writes.
namespace {
template <typename D,typename S1,typename S2,typename M,unsigned ElementBytes>
DEF_SEM(BB_VBLEND,D dst,S1 src1,S2 src2,M mask){
  auto first=UReadV8(src1);auto second=UReadV8(src2);auto bits=UReadV8(mask);auto result=UClearV8(first);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){
    auto sign_index=(i/ElementBytes)*ElementBytes+ElementBytes-1;
    result.elems[i]=(bits.elems[sign_index]&0x80)?second.elems[i]:first.elems[i];
  }
  UWriteV8(dst,result);return memory;
}
}
#define BB_BLEND_SELECTORS(OP,E) \
DEF_ISEL(OP##_XMMdq_XMMdq_XMMdq_XMMdq)=BB_VBLEND<VV128W,V128,V128,V128,E>; \
DEF_ISEL(OP##_XMMdq_XMMdq_MEMdq_XMMdq)=BB_VBLEND<VV128W,V128,MV128,V128,E>; \
DEF_ISEL(OP##_YMMqq_YMMqq_YMMqq_YMMqq)=BB_VBLEND<VV256W,V256,V256,V256,E>; \
DEF_ISEL(OP##_YMMqq_YMMqq_MEMqq_YMMqq)=BB_VBLEND<VV256W,V256,MV256,V256,E>;
BB_BLEND_SELECTORS(VBLENDVPS,4)
BB_BLEND_SELECTORS(VBLENDVPD,8)
BB_BLEND_SELECTORS(VPBLENDVB,1)
#undef BB_BLEND_SELECTORS
