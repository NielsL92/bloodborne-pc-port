// SPDX-License-Identifier: Apache-2.0
// Integer bit semantics preserve host FP state. Native runtime owns #XM delivery.
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory*,State*,uint32_t,uint32_t);
namespace {
template <typename D,typename S1,typename S2,bool Maximum>
DEF_SEM(BB_MINMAX_PS,D dst,S1 src1,S2 src2){
  auto first=UReadV32(src1);auto second=UReadV32(src2);auto result=UClearV32(first);
  auto control=state.x87.fxsave.mxcsr.flat;uint32_t raised=0;
  _Pragma("unroll") for(std::size_t i=0;i<NumVectorElems(result);++i){
    auto a=first.elems[i];auto b=second.elems[i];auto ma=a&0x7fffffffU;auto mb=b&0x7fffffffU;
    bool nan=ma>0x7f800000U||mb>0x7f800000U;bool da=ma&&ma<0x00800000U;bool db=mb&&mb<0x00800000U;
    if(control&0x40){if(da)a&=0x80000000U;if(db)b&=0x80000000U;}
    else if(!nan&&(da||db))raised|=2;
    if(nan){raised|=1;result.elems[i]=b;}
    else if(((a|b)&0x7fffffffU)==0)result.elems[i]=b;
    else {auto ka=(a&0x80000000U)?~a:a|0x80000000U;auto kb=(b&0x80000000U)?~b:b|0x80000000U;result.elems[i]=(Maximum?ka>kb:ka<kb)?a:b;}
  }
  state.x87.fxsave.mxcsr.flat=control|raised;uint32_t unmasked=raised&~(control>>7)&0x3f;
  if(unmasked)__bb_native_simd_fault(memory,&state,raised,unmasked);
  UWriteV32(dst,result);return memory;
}
}
#define BB_MINMAX_SELECTORS(OP,MAXIMUM) \
DEF_ISEL(OP##_XMMdq_XMMdq_XMMdq)=BB_MINMAX_PS<VV128W,V128,V128,MAXIMUM>; \
DEF_ISEL(OP##_XMMdq_XMMdq_MEMdq)=BB_MINMAX_PS<VV128W,V128,MV128,MAXIMUM>; \
DEF_ISEL(OP##_YMMqq_YMMqq_YMMqq)=BB_MINMAX_PS<VV256W,V256,V256,MAXIMUM>; \
DEF_ISEL(OP##_YMMqq_YMMqq_MEMqq)=BB_MINMAX_PS<VV256W,V256,MV256,MAXIMUM>;
BB_MINMAX_SELECTORS(VMINPS,false)
BB_MINMAX_SELECTORS(VMAXPS,true)
#undef BB_MINMAX_SELECTORS
