// SPDX-License-Identifier: Apache-2.0
// Explicit guest MXCSR and flags; integer bit ordering never touches host FP.
extern "C" [[noreturn]] void __bb_native_simd_fault(Memory*,State*,uint32_t,uint32_t);
// BB_REPLACE_SELECTOR: COMISD_XMMsd_MEMsd
// BB_REPLACE_SELECTOR: COMISD_XMMsd_XMMsd
// BB_REPLACE_SELECTOR: COMISS_XMMss_MEMss
// BB_REPLACE_SELECTOR: COMISS_XMMss_XMMss
// BB_REPLACE_SELECTOR: VCOMISD_XMMq_MEMq
// BB_REPLACE_SELECTOR: VCOMISD_XMMq_XMMq
// BB_REPLACE_SELECTOR: VCOMISS_XMMd_MEMd
// BB_REPLACE_SELECTOR: VCOMISS_XMMd_XMMd
// BB_REPLACE_SELECTOR: UCOMISD_XMMsd_MEMsd
// BB_REPLACE_SELECTOR: UCOMISD_XMMsd_XMMsd
// BB_REPLACE_SELECTOR: UCOMISS_XMMss_MEMss
// BB_REPLACE_SELECTOR: UCOMISS_XMMss_XMMss
// BB_REPLACE_SELECTOR: VUCOMISD_XMMdq_MEMq
// BB_REPLACE_SELECTOR: VUCOMISD_XMMdq_XMMq
// BB_REPLACE_SELECTOR: VUCOMISS_XMMdq_MEMd
// BB_REPLACE_SELECTOR: VUCOMISS_XMMdq_XMMd

namespace {
ALWAYS_INLINE static void BB_COMI_BITS(Memory* memory,State& state,uint64_t a,uint64_t b,bool wide,bool unordered) {
  const uint64_t sign=wide?0x8000000000000000ULL:0x80000000ULL;
  const uint64_t inf=wide?0x7ff0000000000000ULL:0x7f800000ULL;
  const uint64_t quiet=wide?0x8000000000000ULL:0x400000ULL;
  const uint64_t mask=sign|(sign-1);
  auto ma=a&(sign-1),mb=b&(sign-1);bool na=ma>inf,nb=mb>inf;
  auto control=state.x87.fxsave.mxcsr.flat;uint32_t raised=0;
  if(na||nb) {
    if(!unordered||(na&&!(a&quiet))||(nb&&!(b&quiet)))raised=1;
  } else {
    bool da=ma&&!(ma&inf),db=mb&&!(mb&inf);
    if(control&0x40){if(da)a&=sign;if(db)b&=sign;}
    else if(da||db)raised=2;
  }
  state.x87.fxsave.mxcsr.flat=control|raised;
  uint32_t unmasked=raised&~(control>>7)&63;
  if(unmasked)__bb_native_simd_fault(memory,&state,raised,unmasked);
  bool equal=a==b||((a|b)&(sign-1))==0;
  auto ka=a^((a&sign)?mask:sign),kb=b^((b&sign)?mask:sign);
  FLAG_ZF=(na||nb)||equal;FLAG_PF=na||nb;FLAG_CF=(na||nb)||(!equal&&ka<kb);
  FLAG_OF=false;FLAG_SF=false;FLAG_AF=false;
}
template <typename S1,typename S2,bool Unordered>
DEF_SEM(BB_COMISS,S1 src1,S2 src2){
  auto a=UReadV32(src1);auto b=UReadV32(src2);
  BB_COMI_BITS(memory,state,a.elems[0],b.elems[0],false,Unordered);return memory;
}
template <typename S1,typename S2,bool Unordered>
DEF_SEM(BB_COMISD,S1 src1,S2 src2){
  auto a=UReadV64(src1);auto b=UReadV64(src2);
  BB_COMI_BITS(memory,state,a.elems[0],b.elems[0],true,Unordered);return memory;
}
}
DEF_ISEL(COMISD_XMMsd_MEMsd)=BB_COMISD<V128, MV64,false>;
DEF_ISEL(COMISD_XMMsd_XMMsd)=BB_COMISD<V128, V128,false>;
DEF_ISEL(COMISS_XMMss_MEMss)=BB_COMISS<V128, MV32,false>;
DEF_ISEL(COMISS_XMMss_XMMss)=BB_COMISS<V128, V128,false>;
DEF_ISEL(VCOMISD_XMMq_MEMq)=BB_COMISD<V128, MV64,false>;
DEF_ISEL(VCOMISD_XMMq_XMMq)=BB_COMISD<V128, V128,false>;
DEF_ISEL(VCOMISS_XMMd_MEMd)=BB_COMISS<V128, MV32,false>;
DEF_ISEL(VCOMISS_XMMd_XMMd)=BB_COMISS<V128, V128,false>;
DEF_ISEL(UCOMISD_XMMsd_MEMsd)=BB_COMISD<V128, MV64,true>;
DEF_ISEL(UCOMISD_XMMsd_XMMsd)=BB_COMISD<V128, V128,true>;
DEF_ISEL(UCOMISS_XMMss_MEMss)=BB_COMISS<V128, MV32,true>;
DEF_ISEL(UCOMISS_XMMss_XMMss)=BB_COMISS<V128, V128,true>;
DEF_ISEL(VUCOMISD_XMMdq_MEMq)=BB_COMISD<V128, MV64,true>;
DEF_ISEL(VUCOMISD_XMMdq_XMMq)=BB_COMISD<V128, V128,true>;
DEF_ISEL(VUCOMISS_XMMdq_MEMd)=BB_COMISS<V128, MV32,true>;
DEF_ISEL(VUCOMISS_XMMdq_XMMd)=BB_COMISS<V128, V128,true>;
