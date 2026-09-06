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
 explicit Scope(uint16_t cw,uint_fast8_t requested_precision=80):rounding(softfloat_roundingMode),tininess(softfloat_detectTininess),precision(extF80_roundingPrecision),flags(softfloat_exceptionFlags){
  const uint_fast8_t modes[]={softfloat_round_near_even,softfloat_round_min,softfloat_round_max,softfloat_round_minMag};softfloat_roundingMode=modes[(cw>>10)&3];softfloat_detectTininess=softfloat_tininess_afterRounding;extF80_roundingPrecision=requested_precision;softfloat_exceptionFlags=0;
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

namespace {
template<unsigned Operation> extFloat80_t arithmetic(extFloat80_t a,extFloat80_t b){if constexpr(Operation==0)return extF80_add(a,b);else if constexpr(Operation==1)return extF80_sub(a,b);else return extF80_mul(a,b);}
// Normalize finite operands without narrowing their signed exponent. Recenter
// the arithmetic before rounding; restore the result exponent only afterwards.
int normalized_exponent(extFloat80_t& value){
 int exponent=value.signExp&0x7fff;if(!value.signif)return 0;
 if(!exponent){exponent=1;while(!(value.signif>>63)){value.signif<<=1;--exponent;}}
 return exponent;
}
template<unsigned Operation> int prepare_wrapped(extFloat80_t& a,extFloat80_t& b,int adjustment){
 int ea=normalized_exponent(a),eb=normalized_exponent(b);
 if constexpr(Operation==2){
  a.signExp=uint16_t((a.signExp&0x8000)|0x3fff);b.signExp=uint16_t((b.signExp&0x8000)|0x3fff);
  return ea+eb-2*0x3fff+adjustment;
 }else{
  int highest=!a.signif?eb:!b.signif?ea:(ea>eb?ea:eb),shift=0x3fff-highest;
  auto center=[&](extFloat80_t& operand,int exponent){if(!operand.signif)return;
   // A gap beyond 256 bits can only contribute a nonzero rounding tail:
   // opposite signs cannot cancel even two leading bits, and precision <=64.
   // Preserve its sign and sticky contribution without underflowing the input.
   if(highest-exponent>256){operand.signif=0x8000000000000000ULL;exponent=highest-256;}
   operand.signExp=uint16_t((operand.signExp&0x8000)|(exponent+shift));
  };center(a,ea);center(b,eb);return adjustment-shift;
 }
}
bool adjust_exponent(extFloat80_t& value,int adjustment){int exponent=(value.signExp&0x7fff)+adjustment;if(exponent<1||exponent>0x7ffe)return false;value.signExp=uint16_t((value.signExp&0x8000)|exponent);return true;}
template<unsigned Operation> void arithmetic_result(uint64_t sa,uint16_t ea,uint64_t sb,uint16_t eb,uint16_t cw,BBX87ArithmeticResult* out){
 *out={};unsigned pc=(cw>>8)&3;if(pc==1){out->unsupported=1;return;}Scope scope(cw,pc==0?32:pc==2?64:80);
 if(unsupported(sa,ea)||unsupported(sb,eb)){out->significand=0xc000000000000000ULL;out->sign_exponent=0xffff;out->flags=1;return;}
 int result_adjustment=0;auto a=canonical(sa,ea),b=canonical(sb,eb);auto value=arithmetic<Operation>(a,b);unsigned flags=mapped_flags();bool nan=(value.signExp&0x7fff)==0x7fff&&value.signif!=0x8000000000000000ULL;
 unsigned denormal=(!nan&&((!(ea&0x7fff)&&sa)||(!(eb&0x7fff)&&sb)))?2:0;
 if(flags&1)flags=1;else if(denormal&&!(cw&2))flags=2;else {
  flags|=denormal;int adjustment=0;if((flags&8)&&!(cw&8))adjustment=-24576;else if(!(cw&16)&&((flags&16)||(value.signif&&!(value.signExp&0x7fff))))adjustment=24576;
  if(adjustment){result_adjustment=prepare_wrapped<Operation>(a,b,adjustment);softfloat_exceptionFlags=0;value=arithmetic<Operation>(a,b);auto wrapped_flags=mapped_flags();if(wrapped_flags&~32u){out->unsupported=3;return;}flags=denormal|(adjustment<0?8:16)|wrapped_flags;}
 }
 auto packed=value;if(result_adjustment&&!adjust_exponent(packed,result_adjustment)){out->unsupported=2;return;}out->significand=packed.signif;out->sign_exponent=packed.signExp;out->flags=uint8_t(flags);
 if((flags&32)&&!(flags&~cw&3)){softfloat_roundingMode=softfloat_round_minMag;softfloat_exceptionFlags=0;auto truncated=arithmetic<Operation>(a,b);out->rounded_up=uint8_t(magnitude_greater(value,truncated));}
}
}
extern "C" void __bb_x87_add(uint64_t sa,uint16_t ea,uint64_t sb,uint16_t eb,uint16_t cw,BBX87ArithmeticResult* out){arithmetic_result<0>(sa,ea,sb,eb,cw,out);}
extern "C" void __bb_x87_sub(uint64_t sa,uint16_t ea,uint64_t sb,uint16_t eb,uint16_t cw,BBX87ArithmeticResult* out){arithmetic_result<1>(sa,ea,sb,eb,cw,out);}
extern "C" void __bb_x87_mul(uint64_t sa,uint16_t ea,uint64_t sb,uint16_t eb,uint16_t cw,BBX87ArithmeticResult* out){arithmetic_result<2>(sa,ea,sb,eb,cw,out);}

extern "C" void __bb_x87_scale(uint64_t sa,uint16_t ea,uint64_t sb,uint16_t eb,uint16_t cw,BBX87ArithmeticResult* out){
 Scope scope(cw);*out={};auto invalid=[&](){out->significand=0xc000000000000000ULL;out->sign_exponent=0xffff;out->flags=1;};
 if(unsupported(sa,ea)||unsupported(sb,eb)){invalid();return;}
 auto a=canonical(sa,ea),b=canonical(sb,eb);unsigned ax=a.signExp&0x7fff,bx=b.signExp&0x7fff;bool an=ax==0x7fff&&sa!=0x8000000000000000ULL,bn=bx==0x7fff&&sb!=0x8000000000000000ULL;
 if(an||bn){auto value=extF80_add(a,b);out->significand=value.signif;out->sign_exponent=value.signExp;out->flags=mapped_flags();return;}
 bool az=!sa,ai=ax==0x7fff,bi=bx==0x7fff,negative=(ea>>15)!=0,scale_negative=(eb>>15)!=0;
 if(bi&&((az&&!scale_negative)||(ai&&scale_negative))){invalid();return;}
 unsigned denormal=((!(ea&0x7fff)&&sa)||(!(eb&0x7fff)&&sb))?2:0;out->flags=uint8_t(denormal);out->significand=a.signif;out->sign_exponent=a.signExp;
 if(denormal&&!(cw&2))return;
 if(bi){out->significand=scale_negative?0:0x8000000000000000ULL;out->sign_exponent=uint16_t((ea&0x8000)|(scale_negative?0:0x7fff));return;}
 // An exactly zero scale preserves a denormal destination without a new UE.
 // Nonzero fractions truncating to zero still pass through exponent handling.
 if(az||ai||!sb)return;
 int scale=0,k=int(bx)-0x3fff;if(k>=0)scale=k>=17?131072:int(sb>>(63-k));if(scale_negative)scale=-scale;
 int exponent=normalized_exponent(a)+scale;out->significand=a.signif;unsigned rc=(cw>>10)&3;bool outward=rc==(negative?1u:2u);
 if(exponent>0x7ffe){
  out->flags|=8;
  if(!(cw&8)){exponent-=24576;if(exponent<=0x7ffe){out->sign_exponent=uint16_t((ea&0x8000)|exponent);return;}}
  bool infinity=!(cw&8)||rc==0||outward;out->significand=infinity?0x8000000000000000ULL:UINT64_MAX;out->sign_exponent=uint16_t((ea&0x8000)|(infinity?0x7fff:0x7ffe));out->flags|=32;out->rounded_up=uint8_t(infinity);return;
 }
 if(exponent<=0){
  if(!(cw&16)){exponent+=24576;out->flags|=16;if(exponent>0){out->sign_exponent=uint16_t((ea&0x8000)|exponent);return;}out->significand=0;out->sign_exponent=uint16_t(ea&0x8000);out->flags|=32;return;}
  unsigned shift=unsigned(1-exponent);uint64_t truncated=0,tail=a.signif,half=0;
  if(shift<64){truncated=a.signif>>shift;tail=a.signif&((1ULL<<shift)-1);half=1ULL<<(shift-1);}else if(shift==64)half=1ULL<<63;
  bool increment=tail&&(rc==0?(shift<=64&&(tail>half||(tail==half&&(truncated&1)))):outward);out->significand=truncated+unsigned(increment);out->sign_exponent=uint16_t((ea&0x8000)|unsigned(out->significand>>63));out->rounded_up=uint8_t(increment);if(tail)out->flags|=48;return;
 }
 out->sign_exponent=uint16_t((ea&0x8000)|exponent);
}
