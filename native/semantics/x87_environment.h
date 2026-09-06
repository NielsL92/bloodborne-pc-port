#pragma once
// SPDX-License-Identifier: Apache-2.0
// Pure state-image operations; callers own memory validation, waiting faults and
// guest profile selection. Experimental bindings require the same canonical State.
#include <cstdint>
#include <remill/Arch/X86/Runtime/State.h>
namespace bb_x87 {
struct Bits {uint64_t significand;uint16_t sign_exponent;};
inline __attribute__((always_inline)) Bits bits(const float80_t& value){Bits out;__builtin_memcpy(&out.significand,&value,8);__builtin_memcpy(&out.sign_exponent,reinterpret_cast<const uint8_t*>(&value)+8,2);return out;}
inline __attribute__((always_inline)) void put_bits(float80_t& value,Bits in){__builtin_memcpy(&value,&in.significand,8);__builtin_memcpy(reinterpret_cast<uint8_t*>(&value)+8,&in.sign_exponent,2);}
inline __attribute__((always_inline)) uint16_t read16(const uint8_t* p){uint16_t v;__builtin_memcpy(&v,p,2);return v;}
inline __attribute__((always_inline)) uint32_t read32(const uint8_t* p){uint32_t v;__builtin_memcpy(&v,p,4);return v;}
inline __attribute__((always_inline)) void write16(uint8_t* p,uint16_t v){__builtin_memcpy(p,&v,2);}
inline __attribute__((always_inline)) void write32(uint8_t* p,uint32_t v){__builtin_memcpy(p,&v,4);}
inline __attribute__((always_inline)) void write64(uint8_t* p,uint64_t v){__builtin_memcpy(p,&v,8);}
inline __attribute__((always_inline)) uint16_t normalize_control(uint16_t v){return uint16_t((v&0x1f3f)|0x40);}
inline __attribute__((always_inline)) uint16_t status(const State& s){uint16_t v=s.x87.fxsave.swd.flat&~uint16_t(0x477f);v|=(s.sw.ie&1)|((s.sw.de&1)<<1)|((s.sw.ze&1)<<2)|((s.sw.oe&1)<<3)|((s.sw.ue&1)<<4)|((s.sw.pe&1)<<5)|((s.sw.sf&1)<<6)|((s.sw.c0&1)<<8)|((s.sw.c1&1)<<9)|((s.sw.c2&1)<<10)|((s.sw.c3&1)<<14);return v;}
inline __attribute__((always_inline)) void set_status(State& s,uint16_t v){s.x87.fxsave.swd.flat=v;s.sw.ie=v&1;s.sw.de=(v>>1)&1;s.sw.ze=(v>>2)&1;s.sw.oe=(v>>3)&1;s.sw.ue=(v>>4)&1;s.sw.pe=(v>>5)&1;s.sw.sf=(v>>6)&1;s.sw.c0=(v>>8)&1;s.sw.c1=(v>>9)&1;s.sw.c2=(v>>10)&1;s.sw.c3=(v>>14)&1;}
inline __attribute__((always_inline)) uint16_t recompute_summary(uint16_t sw,uint16_t cw){return uint16_t((sw&~0x8080)|((sw&~cw&63)?0x8080:0));}
struct PointerSegments {uint16_t code,data;};
struct Profile {bool save_pointers_only_with_exception;bool zero_legacy_selectors;uint32_t mxcsr_mask;};
inline __attribute__((always_inline)) uint16_t full_tags(const State& s){unsigned top=(status(s)>>11)&7,word=0;for(unsigned physical=0;physical<8;++physical){unsigned tag=3;if(s.x87.fxsave.ftw.flat&(1<<physical)){auto v=bits(s.st.elems[(physical+8-top)&7].val);unsigned exponent=v.sign_exponent&0x7fff;tag=!exponent&&!v.significand?1:exponent&&exponent!=0x7fff&&(v.significand>>63)?0:2;}word|=tag<<(physical*2);}return uint16_t(word);}
inline __attribute__((always_inline)) void store_environment28(State& s,PointerSegments segments,const Profile& profile,uint8_t* dst){
 const uint16_t sw=status(s);write16(dst,s.x87.fxsave.cwd.flat);write16(dst+2,0xffff);write16(dst+4,sw);write16(dst+6,0xffff);write16(dst+8,full_tags(s));write16(dst+10,0xffff);
 write32(dst+12,uint32_t(s.x87.fxsave.ip));write16(dst+16,profile.zero_legacy_selectors?0:segments.code);write16(dst+18,s.x87.fxsave.fop&0x7ff);write32(dst+20,uint32_t(s.x87.fxsave.dp));write16(dst+24,profile.zero_legacy_selectors?0:segments.data);write16(dst+26,0xffff);
 s.x87.fxsave.cwd.flat|=63;set_status(s,recompute_summary(sw,s.x87.fxsave.cwd.flat));
}
inline __attribute__((always_inline)) PointerSegments load_environment28(State& s,const Profile& profile,const uint8_t* src){
 const unsigned old_top=(status(s)>>11)&7;const uint16_t cw=normalize_control(read16(src)),sw=recompute_summary(read16(src+4),cw),tags=read16(src+8);const unsigned top=(sw>>11)&7;
 Bits values[8];for(unsigned i=0;i<8;++i)values[i]=bits(s.st.elems[i].val);for(unsigned i=0;i<8;++i)put_bits(s.st.elems[i].val,values[(top+i+8-old_top)&7]);
 s.x87.fxsave.cwd.flat=cw;set_status(s,sw);s.x87.fxsave.ftw.flat=0;for(unsigned physical=0;physical<8;++physical)if(((tags>>(2*physical))&3)!=3)s.x87.fxsave.ftw.flat|=uint8_t(1<<physical);
 s.x87.fxsave.ip=read32(src+12);s.x87.fxsave.fop=read16(src+18)&0x7ff;s.x87.fxsave.dp=read32(src+20);
 return {uint16_t(profile.zero_legacy_selectors?0:read16(src+16)),uint16_t(profile.zero_legacy_selectors?0:read16(src+24))};
}
inline __attribute__((always_inline)) void save_fx(State& s,PointerSegments segments,const Profile& profile,bool offset64,uint8_t* dst){
 const uint16_t sw=status(s);write16(dst,s.x87.fxsave.cwd.flat);write16(dst+2,sw);dst[4]=s.x87.fxsave.ftw.flat;dst[5]=0;
 if(!profile.save_pointers_only_with_exception||(sw&0x80)){
  write16(dst+6,s.x87.fxsave.fop&0x7ff);
  if(offset64){write64(dst+8,s.x87.fxsave.ip);write64(dst+16,s.x87.fxsave.dp);}
  else{write32(dst+8,uint32_t(s.x87.fxsave.ip));write16(dst+12,profile.zero_legacy_selectors?0:segments.code);write16(dst+14,0);write32(dst+16,uint32_t(s.x87.fxsave.dp));write16(dst+20,profile.zero_legacy_selectors?0:segments.data);write16(dst+22,0);}
 }
 write32(dst+24,s.x87.fxsave.mxcsr.flat);write32(dst+28,profile.mxcsr_mask);
 for(unsigned i=0;i<8;++i){__builtin_memcpy(dst+32+i*16,&s.st.elems[i].val,10);__builtin_memset(dst+42+i*16,0,6);}
 for(unsigned i=0;i<16;++i)__builtin_memcpy(dst+160+i*16,&s.vec[i].xmm,16);
 // The software-owned tail (bytes 416..511) remains untouched. MMX/x87 alias
 // coherence and the original guest's pointer feature profile remain open.
}
}
