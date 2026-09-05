// SPDX-License-Identifier: Apache-2.0
// Additional observed VEX selectors; PACKED.cpp.inc supplies lane-aware unpack.
namespace {
DEF_SEM(BB_EXTRACT128,VV128W dst,V256 src,I8 control){
  auto input=UReadV128(src);auto result=UClearV128(UReadV128(dst));
  result.elems[0]=input.elems[Read(control)&1];UWriteV128(dst,result);return memory;
}
template <typename S>
DEF_SEM(BB_INSERTPS,VV128W dst,V128 src1,S src2,I8 control){
  auto result=UReadV32(src1);auto second=UReadV32(src2);auto imm=Read(control);
  auto source_index=NumVectorElems(second)==1?0:(imm>>6)&3;result.elems[(imm>>4)&3]=second.elems[source_index];
  _Pragma("unroll") for(std::size_t i=0;i<4;++i)if((imm>>i)&1)result.elems[i]=0;
  UWriteV32(dst,result);return memory;
}
template <typename S>
DEF_SEM(BB_PINSRD,VV128W dst,V128 src1,S src2,I8 control){
  auto result=UReadV32(src1);result.elems[Read(control)&3]=Read(src2);UWriteV32(dst,result);return memory;
}
template <typename S,unsigned ElementBytes>
DEF_SEM(BB_MOVMASK,R32W dst,S src){
  auto input=UReadV8(src);uint32_t mask=0;
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(input)/ElementBytes;++i)mask|=uint32_t(input.elems[(i+1)*ElementBytes-1]>>7)<<i;
  WriteZExt(dst,mask);return memory;
}
}
DEF_ISEL(VEXTRACTF128_XMMdq_YMMdq_IMMb)=BB_EXTRACT128;
DEF_ISEL(VINSERTPS_XMMdq_XMMdq_XMMdq_IMMb)=BB_INSERTPS<V128>;
DEF_ISEL(VINSERTPS_XMMdq_XMMdq_MEMd_IMMb)=BB_INSERTPS<MV32>;
DEF_ISEL(VPINSRD_XMMdq_XMMdq_GPR32d_IMMb)=BB_PINSRD<R32>;
DEF_ISEL(VPINSRD_XMMdq_XMMdq_MEMd_IMMb)=BB_PINSRD<M32>;
DEF_ISEL(VMOVMSKPS_GPR32d_XMMdq)=BB_MOVMASK<V128,4>;
DEF_ISEL(VMOVMSKPS_GPR32d_YMMqq)=BB_MOVMASK<V256,4>;
DEF_ISEL(VMOVMSKPD_GPR32d_XMMdq)=BB_MOVMASK<V128,8>;
DEF_ISEL(VMOVMSKPD_GPR32d_YMMqq)=BB_MOVMASK<V256,8>;
DEF_ISEL(VLDDQU_XMMdq_MEMdq)=MOVDQx<VV128W,MV128>;
DEF_ISEL(VLDDQU_YMMqq_MEMqq)=MOVDQx<VV256W,MV256>;
DEF_ISEL(VUNPCKHPD_YMMqq_YMMqq_YMMqq)=BB_UNPACK<VV256W,V256,V256,8,true>;
DEF_ISEL(VUNPCKHPD_YMMqq_YMMqq_MEMqq)=BB_UNPACK<VV256W,V256,MV256,8,true>;
