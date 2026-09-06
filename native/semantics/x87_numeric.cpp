// SPDX-License-Identifier: Apache-2.0
// Ordinary native numerical helpers; there is no guest instruction fetch or
// decode here. Keep third-party controls scoped around each numeric operation.
#include "x87_numeric.h"
#define SOFTFLOAT_FAST_INT64
#define LITTLEENDIAN 1
#define THREAD_LOCAL thread_local
extern "C" {
#include <softfloat.h>
}
namespace {
struct Scope {
 uint_fast8_t rounding,tininess,precision,flags;
 explicit Scope(uint16_t cw):rounding(softfloat_roundingMode),tininess(softfloat_detectTininess),precision(extF80_roundingPrecision),flags(softfloat_exceptionFlags){
  const uint_fast8_t modes[]={softfloat_round_near_even,softfloat_round_min,softfloat_round_max,softfloat_round_minMag};softfloat_roundingMode=modes[(cw>>10)&3];softfloat_detectTininess=softfloat_tininess_afterRounding;extF80_roundingPrecision=80;softfloat_exceptionFlags=0;
 }
 ~Scope(){softfloat_roundingMode=rounding;softfloat_detectTininess=tininess;extF80_roundingPrecision=precision;softfloat_exceptionFlags=flags;}
 Scope(const Scope&)=delete;Scope& operator=(const Scope&)=delete;
};
void result(BBX87NumericResult* out,extFloat80_t value,uint8_t extra){auto flags=softfloat_exceptionFlags;out->significand=value.signif;out->sign_exponent=value.signExp;out->flags=uint8_t(extra|((flags&16)>>4)|((flags&8)>>1)|((flags&4)<<1)|((flags&2)<<3)|((flags&1)<<5));out->rounded_up=0;}
}
extern "C" void __bb_x87_from_f32(uint32_t value,uint16_t cw,BBX87NumericResult* out){Scope scope(cw);auto number=f32_to_extF80({value});result(out,number,uint8_t((value&0x7fffffff)&&!(value&0x7f800000)?2:0));}
extern "C" void __bb_x87_from_f64(uint64_t value,uint16_t cw,BBX87NumericResult* out){Scope scope(cw);auto number=f64_to_extF80({value});result(out,number,uint8_t((value&0x7fffffffffffffffULL)&&!(value&0x7ff0000000000000ULL)?2:0));}
extern "C" void __bb_x87_from_i64(int64_t value,uint16_t cw,BBX87NumericResult* out){Scope scope(cw);result(out,i64_to_extF80(value),0);}

namespace {
uint8_t mapped_flags(){auto flags=softfloat_exceptionFlags;return uint8_t(((flags&16)>>4)|((flags&8)>>1)|((flags&4)<<1)|((flags&2)<<3)|((flags&1)<<5));}
bool unsupported(uint64_t sig,uint16_t exp){return (exp&0x7fff)&&!(sig>>63);}
extFloat80_t canonical(uint64_t sig,uint16_t exp){extFloat80_t value{};value.signif=sig;value.signExp=exp;if(!(exp&0x7fff)&&(sig>>63))value.signExp=uint16_t(exp|1);return value;}
bool magnitude_greater(extFloat80_t a,extFloat80_t b){auto ea=a.signExp&0x7fff,eb=b.signExp&0x7fff;return ea>eb||(ea==eb&&a.signif>b.signif);}
template<unsigned Width> void store_float(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){
 Scope scope(cw);*out={};if(unsupported(sig,exp)){out->bits=Width==32?0xffc00000:0xfff8000000000000ULL;out->flags=1;return;}
 auto value=canonical(sig,exp);uint64_t bits=Width==32?extF80_to_f32(value).v:extF80_to_f64(value).v;out->bits=bits;out->flags=mapped_flags();out->tiny=uint8_t(sig&&!(bits&(Width==32?0x7f800000:0x7ff0000000000000ULL)));
 if(out->flags&32){auto rounded=Width==32?f32_to_extF80({uint32_t(bits)}):f64_to_extF80({bits});out->rounded_up=uint8_t(magnitude_greater(rounded,value));}
}
template<unsigned Width> void store_integer(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){
 Scope scope(cw);*out={};const uint64_t indefinite=uint64_t(1)<<(Width-1);if(unsupported(sig,exp)){out->bits=indefinite;out->flags=1;return;}
 auto integer=extF80_to_i64_r_minMag(canonical(sig,exp),true);out->flags=mapped_flags();bool outside=(out->flags&1)!=0;if(Width==16)outside|=integer<INT16_MIN||integer>INT16_MAX;else if(Width==32)outside|=integer<INT32_MIN||integer>INT32_MAX;
 if(outside){out->bits=indefinite;out->flags=1;}else{out->bits=uint64_t(integer);if constexpr(Width<64)out->bits&=(uint64_t(1)<<Width)-1;}
}
}
extern "C" void __bb_x87_to_f32(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){store_float<32>(sig,exp,cw,out);}
extern "C" void __bb_x87_to_f64(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){store_float<64>(sig,exp,cw,out);}
extern "C" void __bb_x87_to_i16_trunc(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){store_integer<16>(sig,exp,cw,out);}
extern "C" void __bb_x87_to_i32_trunc(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){store_integer<32>(sig,exp,cw,out);}
extern "C" void __bb_x87_to_i64_trunc(uint64_t sig,uint16_t exp,uint16_t cw,BBX87StoreResult* out){store_integer<64>(sig,exp,cw,out);}
