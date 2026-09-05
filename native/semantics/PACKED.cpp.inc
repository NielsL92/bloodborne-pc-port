// SPDX-License-Identifier: Apache-2.0
// Authored VEX packed integer/data-selection semantics. All arithmetic is unsigned
// unless signed ordering is explicitly expressed by flipping the sign bit.
namespace {
template <typename D,typename S,bool Arithmetic>
DEF_SEM(BB_SHIFT_DWORDS,D dst,S src,I8 control){
  auto input=UReadV32(src);auto result=UClearV32(input);auto count=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){
    auto value=input.elems[i];
    if constexpr(Arithmetic){auto amount=count>31?31:count;auto shifted=value>>amount;if(amount&&(value&0x80000000U))shifted|=~uint32_t(0)<<(32-amount);result.elems[i]=shifted;}
    else result.elems[i]=count>=32?0:value>>count;
  }
  UWriteV32(dst,result);return memory;
}
template <typename D,typename S1,typename S2,unsigned ElementBytes,bool High>
DEF_SEM(BB_UNPACK,D dst,S1 src1,S2 src2){
  auto first=UReadV8(src1);auto second=UReadV8(src2);auto result=UClearV8(first);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){auto lane=(i/16)*16;auto local=i%16;auto element=local/ElementBytes;auto source=lane+(High?8:0)+(element/2)*ElementBytes+(local%ElementBytes);result.elems[i]=(element&1)?second.elems[source]:first.elems[source];}
  UWriteV8(dst,result);return memory;
}
template <typename D,typename S1,typename S2,unsigned Operation>
DEF_SEM(BB_DWORD_BINARY,D dst,S1 src1,S2 src2){
  auto first=UReadV32(src1);auto second=UReadV32(src2);auto result=UClearV32(first);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){auto a=first.elems[i];auto b=second.elems[i];
    if constexpr(Operation==0)result.elems[i]=uint32_t(uint64_t(a)*uint64_t(b));
    else {bool less=(a^0x80000000U)<(b^0x80000000U);result.elems[i]=((Operation==1)?less:!less)?a:b;}
  }
  UWriteV32(dst,result);return memory;
}
template <typename D,typename S1,typename S2>
DEF_SEM(BB_PMULUDQ,D dst,S1 src1,S2 src2){
  auto first=UReadV32(src1);auto second=UReadV32(src2);auto result=UClearV64(UReadV64(src1));
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i)result.elems[i]=uint64_t(first.elems[2*i])*uint64_t(second.elems[2*i]);
  UWriteV64(dst,result);return memory;
}
template <typename D,typename S1,typename S2>
DEF_SEM(BB_PSHUFB,D dst,S1 src1,S2 src2){
  auto first=UReadV8(src1);auto control=UReadV8(src2);auto result=UClearV8(first);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i)result.elems[i]=(control.elems[i]&0x80)?0:first.elems[(i/16)*16+(control.elems[i]&15)];
  UWriteV8(dst,result);return memory;
}
template <typename D,typename S1,typename S2>
DEF_SEM(BB_PALIGNR,D dst,S1 src1,S2 src2,I8 control){
  auto first=UReadV8(src1);auto second=UReadV8(src2);auto result=UClearV8(first);auto shift=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){auto lane=(i/16)*16;auto index=i%16+shift;result.elems[i]=index>=32?0:index>=16?first.elems[lane+index-16]:second.elems[lane+index];}
  UWriteV8(dst,result);return memory;
}
template <typename D,typename S1,typename S2>
DEF_SEM(BB_SHUFPD,D dst,S1 src1,S2 src2,I8 control){
  auto first=UReadV64(src1);auto second=UReadV64(src2);auto result=UClearV64(first);auto imm=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){auto index=(i/2)*2+((imm>>i)&1);result.elems[i]=(i&1)?second.elems[index]:first.elems[index];}
  UWriteV64(dst,result);return memory;
}
template <typename D,typename S>
DEF_SEM(BB_PERMILPD,D dst,S src,I8 control){
  auto input=UReadV64(src);auto result=UClearV64(input);auto imm=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i)result.elems[i]=input.elems[(i/2)*2+((imm>>i)&1)];
  UWriteV64(dst,result);return memory;
}
template <typename D,typename S1,typename S2,unsigned ElementBytes>
DEF_SEM(BB_BLEND_IMM,D dst,S1 src1,S2 src2,I8 control){
  auto first=UReadV8(src1);auto second=UReadV8(src2);auto result=UClearV8(first);auto imm=Read(control);
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i)result.elems[i]=((imm>>(i/ElementBytes))&1)?second.elems[i]:first.elems[i];
  UWriteV8(dst,result);return memory;
}
}
#define BB_BINARY_SELECTORS(OP,SEM,...) \
DEF_ISEL(OP##_XMMdq_XMMdq_XMMdq)=SEM<VV128W,V128,V128,##__VA_ARGS__>; \
DEF_ISEL(OP##_XMMdq_XMMdq_MEMdq)=SEM<VV128W,V128,MV128,##__VA_ARGS__>; \
DEF_ISEL(OP##_YMMqq_YMMqq_YMMqq)=SEM<VV256W,V256,V256,##__VA_ARGS__>; \
DEF_ISEL(OP##_YMMqq_YMMqq_MEMqq)=SEM<VV256W,V256,MV256,##__VA_ARGS__>;
BB_BINARY_SELECTORS(VPUNPCKLWD,BB_UNPACK,2,false)
BB_BINARY_SELECTORS(VPUNPCKLDQ,BB_UNPACK,4,false)
BB_BINARY_SELECTORS(VPUNPCKHQDQ,BB_UNPACK,8,true)
DEF_ISEL(VPMULLD_XMMdq_XMMdq_XMMdq)=BB_DWORD_BINARY<VV128W,V128,V128,0>;
DEF_ISEL(VPMULLD_XMMdq_XMMdq_MEMdq)=BB_DWORD_BINARY<VV128W,V128,MV128,0>;
DEF_ISEL(VPMULLD_YMMqq_YMMqq_MEMqq)=BB_DWORD_BINARY<VV256W,V256,MV256,0>;
BB_BINARY_SELECTORS(VPMINSD,BB_DWORD_BINARY,1)
BB_BINARY_SELECTORS(VPMAXSD,BB_DWORD_BINARY,2)
DEF_ISEL(VPMULUDQ_XMMdq_XMMdq_XMMdq)=BB_PMULUDQ<VV128W,V128,V128>;
DEF_ISEL(VPMULUDQ_XMMdq_XMMdq_MEMdq)=BB_PMULUDQ<VV128W,V128,MV128>;
DEF_ISEL(VPMULUDQ_YMMqq_YMMqq_MEMqq)=BB_PMULUDQ<VV256W,V256,MV256>;
BB_BINARY_SELECTORS(VPSHUFB,BB_PSHUFB)
#undef BB_BINARY_SELECTORS
#define BB_IMM_BINARY(OP,SEM,...) \
DEF_ISEL(OP##_XMMdq_XMMdq_XMMdq_IMMb)=SEM<VV128W,V128,V128,##__VA_ARGS__>; \
DEF_ISEL(OP##_XMMdq_XMMdq_MEMdq_IMMb)=SEM<VV128W,V128,MV128,##__VA_ARGS__>; \
DEF_ISEL(OP##_YMMqq_YMMqq_YMMqq_IMMb)=SEM<VV256W,V256,V256,##__VA_ARGS__>; \
DEF_ISEL(OP##_YMMqq_YMMqq_MEMqq_IMMb)=SEM<VV256W,V256,MV256,##__VA_ARGS__>;
BB_IMM_BINARY(VPALIGNR,BB_PALIGNR)
BB_IMM_BINARY(VSHUFPD,BB_SHUFPD)
BB_IMM_BINARY(VBLENDPS,BB_BLEND_IMM,4)
BB_IMM_BINARY(VBLENDPD,BB_BLEND_IMM,8)
#undef BB_IMM_BINARY
DEF_ISEL(VPSRLD_XMMdq_XMMdq_IMMb)=BB_SHIFT_DWORDS<VV128W,V128,false>;
DEF_ISEL(VPSRLD_YMMqq_YMMqq_IMMb)=BB_SHIFT_DWORDS<VV256W,V256,false>;
DEF_ISEL(VPSRAD_XMMdq_XMMdq_IMMb)=BB_SHIFT_DWORDS<VV128W,V128,true>;
DEF_ISEL(VPSRAD_YMMqq_YMMqq_IMMb)=BB_SHIFT_DWORDS<VV256W,V256,true>;
DEF_ISEL(VPERMILPD_XMMdq_XMMdq_IMMb)=BB_PERMILPD<VV128W,V128>;
DEF_ISEL(VPERMILPD_XMMdq_MEMdq_IMMb)=BB_PERMILPD<VV128W,MV128>;
DEF_ISEL(VPERMILPD_YMMqq_YMMqq_IMMb)=BB_PERMILPD<VV256W,V256>;
DEF_ISEL(VPERMILPD_YMMqq_MEMqq_IMMb)=BB_PERMILPD<VV256W,MV256>;
