// SPDX-License-Identifier: Apache-2.0
// Correctly rounded binary32 sqrt from a 48-bit integer radicand. The restoring
// root/remainder avoids changing host FP state and has no CPU execution fallback.
namespace {
template <typename D,typename S>
DEF_SEM(BB_SQRTPS,D dst,S src){
  auto input=UReadV32(src);auto result=UClearV32(input);auto control=state.x87.fxsave.mxcsr.flat;uint32_t raised=0;bool precision=false;
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){
    auto bits=input.elems[i];auto magnitude=bits&0x7fffffffU;auto sign=bits&0x80000000U;
    if(magnitude>0x7f800000U){if(!(bits&0x400000U))raised|=1;result.elems[i]=bits|0x400000U;continue;}
    if((control&64)&&magnitude<0x800000U){result.elems[i]=sign;continue;}
    if(!magnitude){result.elems[i]=bits;continue;}
    if(sign){raised|=1;result.elems[i]=0xffc00000U;continue;}
    if(magnitude==0x7f800000U){result.elems[i]=bits;continue;}
    uint32_t mantissa=bits&0x7fffffU;int exponent=int(bits>>23)-127;
    if(bits&0x7f800000U)mantissa|=0x800000U;
    else {raised|=2;exponent=-126;while(mantissa<0x800000U){mantissa<<=1;--exponent;}}
    bool odd=(exponent%2)!=0;uint64_t remainder=uint64_t(mantissa)<<(odd?24:23);uint64_t root=0;
    for(uint64_t step=uint64_t(1)<<46;step;step>>=2){if(remainder>=root+step){remainder-=root+step;root=(root>>1)+step;}else root>>=1;}
    precision|=remainder!=0;auto mode=(control>>13)&3;
    if((mode==0&&remainder>root)||(mode==2&&remainder))++root;
    exponent=(exponent-(odd?1:0))/2;if(root==0x1000000U){root>>=1;++exponent;}
    result.elems[i]=(uint32_t(exponent+127)<<23)|(uint32_t(root)&0x7fffffU);
  }
  if(precision&&!(raised&~(control>>7)&3))raised|=32;
  state.x87.fxsave.mxcsr.flat=control|raised;uint32_t unmasked=raised&~(control>>7)&63;
  if(unmasked)__bb_native_simd_fault(memory,&state,raised,unmasked);
  UWriteV32(dst,result);return memory;
}
}
DEF_ISEL(VSQRTPS_XMMdq_XMMdq)=BB_SQRTPS<VV128W,V128>;
DEF_ISEL(VSQRTPS_XMMdq_MEMdq)=BB_SQRTPS<VV128W,MV128>;
DEF_ISEL(VSQRTPS_YMMqq_YMMqq)=BB_SQRTPS<VV256W,V256>;
DEF_ISEL(VSQRTPS_YMMqq_MEMqq)=BB_SQRTPS<VV256W,MV256>;
