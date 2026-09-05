// SPDX-License-Identifier: Apache-2.0
// VEX SHUFPS uses the same immediate independently in each 128-bit lane.
namespace {
template <typename D,typename S1,typename S2>
DEF_SEM(BB_VSHUFPS,D dst,S1 src1,S2 src2,I8 control){
  auto first=UReadV32(src1);auto second=UReadV32(src2);auto result=UClearV32(first);auto imm=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){
    auto within=i%4;auto lane=i-within;auto index=lane+((imm>>(2*within))&3);
    result.elems[i]=within<2?first.elems[index]:second.elems[index];
  }
  UWriteV32(dst,result);return memory;
}
}
DEF_ISEL(VSHUFPS_XMMdq_XMMdq_XMMdq_IMMb)=BB_VSHUFPS<VV128W,V128,V128>;
DEF_ISEL(VSHUFPS_XMMdq_XMMdq_MEMdq_IMMb)=BB_VSHUFPS<VV128W,V128,MV128>;
DEF_ISEL(VSHUFPS_YMMqq_YMMqq_YMMqq_IMMb)=BB_VSHUFPS<VV256W,V256,V256>;
DEF_ISEL(VSHUFPS_YMMqq_YMMqq_MEMqq_IMMb)=BB_VSHUFPS<VV256W,V256,MV256>;
