// SPDX-License-Identifier: Apache-2.0
// Round an IEEE binary64 bit pattern to an integral binary64 value. No host FP
// instructions or host rounding-state changes are needed for this operation.
namespace {
template <typename S>
DEF_SEM(BB_ROUNDSD,VV128W dst,V128 src1,S src2,I8 control){
  auto first=UReadV64(src1);auto second=UReadV64(src2);auto input=second.elems[0];
  auto sign=input&0x8000000000000000ULL;auto magnitude=input&0x7fffffffffffffffULL;auto result=input;
  auto mxcsr=state.x87.fxsave.mxcsr.flat;auto imm=Read(control);uint32_t raised=0;bool inexact=false;
  if(magnitude>0x7ff0000000000000ULL){if(!(magnitude&0x0008000000000000ULL))raised|=1;result=input|0x0008000000000000ULL;}
  else if(magnitude&&magnitude<0x7ff0000000000000ULL){
    if((mxcsr&0x40)&&magnitude<0x0010000000000000ULL)result=sign;
    else {
      auto mode=(imm&4)?((mxcsr>>13)&3):(imm&3);int exponent=int(magnitude>>52)-1023;
      if(exponent<0){inexact=true;bool increment=mode==0?magnitude>0x3fe0000000000000ULL:mode==1?sign!=0:mode==2?sign==0:false;result=sign|(increment?0x3ff0000000000000ULL:0);}
      else if(exponent<52){unsigned shift=unsigned(52-exponent);uint64_t quantum=uint64_t(1)<<shift;auto fraction=magnitude&(quantum-1);auto integral=magnitude&~(quantum-1);inexact=fraction!=0;
        bool increment=false;if(inexact){if(mode==0)increment=fraction>quantum/2||(fraction==quantum/2&&((integral>>shift)&1));else if(mode==1)increment=sign!=0;else if(mode==2)increment=sign==0;}
        result=sign|(integral+(increment?quantum:0));
      }
    }
  }
  if(inexact&&!(imm&8))raised|=32;
  state.x87.fxsave.mxcsr.flat=mxcsr|raised;uint32_t unmasked=raised&~(mxcsr>>7)&63;
  if(unmasked)__bb_native_simd_fault(memory,&state,raised,unmasked);
  first.elems[0]=result;UWriteV64(dst,first);return memory;
}
}
DEF_ISEL(VROUNDSD_XMMdq_XMMdq_XMMq_IMMb)=BB_ROUNDSD<V128>;
DEF_ISEL(VROUNDSD_XMMdq_XMMdq_MEMq_IMMb)=BB_ROUNDSD<MV64>;
