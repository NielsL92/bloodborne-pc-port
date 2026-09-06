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
