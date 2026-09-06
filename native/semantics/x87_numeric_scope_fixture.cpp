// SPDX-License-Identifier: Apache-2.0
// Separate TU avoids collisions between SoftFloat and Remill scalar typedefs.
#include "x87_numeric.h"
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <atomic>
#include <thread>
#define SOFTFLOAT_FAST_INT64
#define LITTLEENDIAN 1
#define THREAD_LOCAL thread_local
extern "C" {
#include <softfloat.h>
}
static_assert(sizeof(BBX87NumericResult)==16 && offsetof(BBX87NumericResult,sign_exponent)==8 && offsetof(BBX87NumericResult,flags)==10 && offsetof(BBX87NumericResult,rounded_up)==11,"numeric helper ABI");
static_assert(sizeof(BBX87StoreResult)==16 && offsetof(BBX87StoreResult,flags)==8 && offsetof(BBX87StoreResult,rounded_up)==9 && offsetof(BBX87StoreResult,tiny)==10,"store helper ABI");
extern "C" void verify_numeric_scope(){
 std::atomic<unsigned> bad{0};std::thread threads[4];
 for(unsigned worker=0;worker<4;++worker)threads[worker]=std::thread([worker,&bad](){
  for(unsigned i=0;i<65536;++i){
   uint_fast8_t rounding=(i+worker)%7,tininess=(i/3)%2,precision=(i%3==0?32:i%3==1?64:80),flags=(i+worker)%32;
   softfloat_roundingMode=rounding;softfloat_detectTininess=tininess;extF80_roundingPrecision=precision;softfloat_exceptionFlags=flags;
   BBX87NumericResult result{};uint64_t sig=0;uint16_t exp=0;uint8_t exceptions=0;
   switch((i+worker)%6){
    case 0:__bb_x87_from_f32(0x7f800001,uint16_t(i),&result);sig=0xc000010000000000ULL;exp=0x7fff;exceptions=1;break;
    case 1:__bb_x87_from_f32(1,uint16_t(i),&result);sig=0x8000000000000000ULL;exp=0x3f6a;exceptions=2;break;
    case 2:__bb_x87_from_f64(0xfff0000000000001ULL,uint16_t(i),&result);sig=0xc000000000000800ULL;exp=0xffff;exceptions=1;break;
    case 3:__bb_x87_from_f64(1,uint16_t(i),&result);sig=0x8000000000000000ULL;exp=0x3bcd;exceptions=2;break;
    case 4:__bb_x87_from_i64(INT64_MAX,uint16_t(i),&result);sig=0xfffffffffffffffeULL;exp=0x403d;break;
    case 5:__bb_x87_from_i64(INT64_MIN,uint16_t(i),&result);sig=0x8000000000000000ULL;exp=0xc03e;break;
   }
   bad+=result.significand!=sig||result.sign_exponent!=exp||result.flags!=exceptions||result.rounded_up||softfloat_roundingMode!=rounding||softfloat_detectTininess!=tininess||extF80_roundingPrecision!=precision||softfloat_exceptionFlags!=flags;
   BBX87StoreResult stored{};uint64_t bits=0;uint8_t raised=0,up=0;
   switch((i+worker)%6){
    case 0:__bb_x87_to_f32(0x8000008000000000ULL,0x3fff,uint16_t(i),&stored);up=((i>>10)&3)==2;bits=0x3f800000+up;raised=32;break;
    case 1:__bb_x87_to_f64(0x8000000000000400ULL,0x3fff,uint16_t(i),&stored);up=((i>>10)&3)==2;bits=0x3ff0000000000000ULL+up;raised=32;break;
    case 2:__bb_x87_to_i16_trunc(0xffff000000000000ULL,0x400d,uint16_t(i),&stored);bits=32767;raised=32;break;
    case 3:__bb_x87_to_i32_trunc(0xc000000000000000ULL,0xbfff,uint16_t(i),&stored);bits=0xffffffff;raised=32;break;
    case 4:__bb_x87_to_i64_trunc(0x8000000000000000ULL,0x403e,uint16_t(i),&stored);bits=0x8000000000000000ULL;raised=1;break;
    case 5:__bb_x87_to_f64(0,0x3fff,uint16_t(i),&stored);bits=0xfff8000000000000ULL;raised=1;break;
   }
   bad+=stored.bits!=bits||stored.flags!=raised||stored.rounded_up!=up||stored.tiny||softfloat_roundingMode!=rounding||softfloat_detectTininess!=tininess||extF80_roundingPrecision!=precision||softfloat_exceptionFlags!=flags;
  }
 });
 for(auto& t:threads)t.join();
 std::printf("{\"form\":\"numeric-scope\",\"cases\":524288,\"differing_cases\":%u}\n",bad.load());std::fflush(stdout);if(bad.load())std::exit(3);
}
