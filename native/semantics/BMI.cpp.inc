// SPDX-License-Identifier: Apache-2.0
// Included after pinned Remill X86 Runtime/Instructions.cpp.
// Intel SDM Vol.2A BLSR/BLSI: defined CF/OF/SF/ZF; AF/PF undefined.
namespace {
template <typename D,typename S>
DEF_SEM(BB_BLSR,D dst,S src){
  auto value=Read(src);
  auto result=UAnd(value,USub(value,Literal<S>(1)));
  WriteZExt(dst,result);
  Write(FLAG_CF,ZeroFlag(value));Write(FLAG_OF,false);
  Write(FLAG_SF,SignFlag(result));Write(FLAG_ZF,ZeroFlag(result));
  UndefFlag(af);UndefFlag(pf);
  return memory;
}
template <typename D,typename S>
DEF_SEM(BB_BLSI,D dst,S src){
  auto value=Read(src);
  auto result=UAnd(value,USub(Literal<S>(0),value));
  WriteZExt(dst,result);
  Write(FLAG_CF,!ZeroFlag(value));Write(FLAG_OF,false);
  Write(FLAG_SF,SignFlag(result));Write(FLAG_ZF,ZeroFlag(result));
  UndefFlag(af);UndefFlag(pf);
  return memory;
}
}
DEF_ISEL(BLSR_GPR32d_GPR32d)=BB_BLSR<R32W,R32>;
DEF_ISEL(BLSR_GPR32d_MEMd)=BB_BLSR<R32W,M32>;
IF_64BIT(DEF_ISEL(BLSR_GPR64q_GPR64q)=BB_BLSR<R64W,R64>;)
IF_64BIT(DEF_ISEL(BLSR_GPR64q_MEMq)=BB_BLSR<R64W,M64>;)
DEF_ISEL(BLSI_GPR32d_GPR32d)=BB_BLSI<R32W,R32>;
DEF_ISEL(BLSI_GPR32d_MEMd)=BB_BLSI<R32W,M32>;
IF_64BIT(DEF_ISEL(BLSI_GPR64q_GPR64q)=BB_BLSI<R64W,R64>;)
IF_64BIT(DEF_ISEL(BLSI_GPR64q_MEMq)=BB_BLSI<R64W,M64>;)
