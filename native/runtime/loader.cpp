// SPDX-License-Identifier: GPL-2.0-or-later
// Static native loader. Module byte copies are data only and never executable.
#include "loader.h"
#include <bcrypt.h>
#include <algorithm>
#include <array>
#include <cstring>
#include <fstream>
#include <set>
#include <stdexcept>
#pragma comment(lib,"bcrypt.lib")
namespace bb_runtime {
namespace {
void require(bool value,const char* why){if(!value)throw std::runtime_error(why);}
class Sha256 {
 BCRYPT_ALG_HANDLE algorithm_=nullptr;BCRYPT_HASH_HANDLE hash_=nullptr;std::vector<uint8_t> object_;
 public:
 Sha256(){try{
  require(BCryptOpenAlgorithmProvider(&algorithm_,BCRYPT_SHA256_ALGORITHM,nullptr,0)==0,"SHA256 provider");
  DWORD size=0,got=0;require(BCryptGetProperty(algorithm_,BCRYPT_OBJECT_LENGTH,reinterpret_cast<PUCHAR>(&size),sizeof size,&got,0)==0&&got==sizeof size,"SHA256 state size");object_.resize(size);
  require(BCryptCreateHash(algorithm_,&hash_,object_.data(),size,nullptr,0,0)==0,"SHA256 state");
 }catch(...){if(hash_)BCryptDestroyHash(hash_);if(algorithm_)BCryptCloseAlgorithmProvider(algorithm_,0);throw;}}
 ~Sha256(){if(hash_)BCryptDestroyHash(hash_);if(algorithm_)BCryptCloseAlgorithmProvider(algorithm_,0);}
 void update(const uint8_t* bytes,size_t size){require(size<=UINT32_MAX,"SHA256 chunk size");if(size)require(BCryptHashData(hash_,const_cast<PUCHAR>(bytes),ULONG(size),0)==0,"SHA256 update");}
 std::string finish(){std::array<uint8_t,32> digest{};require(BCryptFinishHash(hash_,digest.data(),DWORD(digest.size()),0)==0,"SHA256 finish");std::string text;const char* hex="0123456789abcdef";for(auto byte:digest){text+=hex[byte>>4];text+=hex[byte&15];}return text;}
};
void hex_identity(const std::string& value){require(value.size()==64,"identity size");for(char c:value)require((c>='0'&&c<='9')||(c>='a'&&c<='f'),"identity encoding");}
struct Reader {
 const std::vector<uint8_t>& bytes;size_t offset=0;
 const uint8_t* take(size_t count){require(count<=bytes.size()-offset,"truncated load bundle");auto* p=bytes.data()+offset;offset+=count;return p;}
 template<typename T>T value(){T v;std::memcpy(&v,take(sizeof v),sizeof v);return v;}
 std::string text(size_t size){auto* p=take(size);return std::string(reinterpret_cast<const char*>(p),size);}
};
LoadRegion& owner(std::vector<LoadRegion>& regions,uint64_t address,uint64_t width){
 require(width&&width<=UINT64_MAX-address,"loader span overflow");for(auto& region:regions)if(address>=region.base&&address+width<=region.base+region.declared)return region;throw std::runtime_error("relocation/guard outside declared memory");
}
}
std::unique_ptr<LoadedImage> load_private_image(const char* path,const std::string& expected_sha256,const std::string& registry_identity){
 hex_identity(expected_sha256);hex_identity(registry_identity);std::ifstream file(path,std::ios::binary|std::ios::ate);require(bool(file),"load bundle open");auto size=file.tellg();require(size>=88&&size<=512LL*1024*1024,"load bundle size");std::vector<uint8_t> bytes(static_cast<size_t>(size));file.seekg(0);file.read(reinterpret_cast<char*>(bytes.data()),bytes.size());require(bool(file),"load bundle read");Sha256 source_hash;source_hash.update(bytes.data(),bytes.size());require(source_hash.finish()==expected_sha256,"load bundle SHA256 mismatch");Reader in{bytes};require(in.text(8)=="BBLOAD01","load bundle version");require(in.text(64)==registry_identity,"load bundle registry identity");auto region_count=in.value<uint32_t>(),relocation_count=in.value<uint32_t>(),guard_count=in.value<uint32_t>();require(in.value<uint32_t>()==0,"bundle reserved field");require(region_count&&region_count<=64&&relocation_count<=1000000&&guard_count<=10000,"bundle count limits");auto result=std::make_unique<LoadedImage>();auto& regions=result->regions_;uint64_t total=0;
 for(uint32_t n=0;n<region_count;++n){
  LoadRegion row{};row.base=in.value<uint64_t>();row.size=in.value<uint64_t>();row.declared=in.value<uint64_t>();auto initial_size=in.value<uint64_t>();row.rights=in.value<uint32_t>();require(in.value<uint32_t>()==0,"region reserved field");require(row.size&&row.size<=UINT64_MAX-row.base&&row.declared<=row.size&&initial_size<=row.declared,"invalid region sizes");require(row.base>=0xa00000000ULL||row.base+row.size<=0x900000000ULL,"native service slot collision");require(row.size<=256ULL*1024*1024&&total+row.size<=256ULL*1024*1024,"mapped byte limit");require(row.rights&&(row.rights&~7u)==0&&(!(row.rights&Write)||(row.rights&Read))&&!((row.rights&Code)&&(row.rights&Write)),"invalid region rights");
  for(const auto& old:regions)require(!(row.base<old.base+old.size&&old.base<row.base+row.size),"overlapping load regions");auto* initial=in.take(static_cast<size_t>(initial_size));row.expected.resize(static_cast<size_t>(row.size));std::memcpy(row.expected.data(),initial,static_cast<size_t>(initial_size));total+=row.size;regions.push_back(std::move(row));
 }
 std::sort(regions.begin(),regions.end(),[](const LoadRegion& a,const LoadRegion& b){return a.base<b.base;});std::set<uint64_t> relocations;
 for(uint32_t n=0;n<relocation_count;++n){uint64_t address=in.value<uint64_t>(),value=in.value<uint64_t>();auto& region=owner(regions,address,8);require((region.rights&Write)&&!(region.rights&Code),"relocation is not writable data");auto next=relocations.lower_bound(address);require((next==relocations.end()||address+8<=*next)&&(next==relocations.begin()||*std::prev(next)+8<=address),"overlapping relocation destinations");relocations.insert(address);std::memcpy(region.expected.data()+static_cast<size_t>(address-region.base),&value,8);}
 result->relocations_=relocation_count;
 for(uint32_t n=0;n<guard_count;++n){AccessGuard guard{};guard.base=in.value<uint64_t>();guard.size=in.value<uint64_t>();auto length=in.value<uint32_t>();require(length&&length<=256,"guard identity length");guard.identity=in.text(length);auto& region=owner(regions,guard.base,guard.size);require(region.rights&Read,"guard region unreadable");auto next=relocations.lower_bound(guard.base);require((next==relocations.end()||guard.base+guard.size<=*next)&&(next==relocations.begin()||*std::prev(next)+8<=guard.base),"guard overlaps resolved relocation");for(const auto& old:result->guards_)require(!(guard.base<old.base+old.size&&old.base<guard.base+guard.size),"overlapping loader guards");result->guards_.push_back(std::move(guard));}
 require(in.offset==bytes.size(),"trailing load bundle bytes");std::sort(result->guards_.begin(),result->guards_.end(),[](const AccessGuard& a,const AccessGuard& b){return a.base<b.base;});
 for(const auto& row:regions)result->space.add(row.base,static_cast<size_t>(row.size),row.rights,row.expected.data(),row.expected.size());
 for(const auto& guard:result->guards_)result->space.guard(guard.base,static_cast<size_t>(guard.size),guard.identity);result->space.seal();return result;
}
LoadValidation LoadedImage::validate(Memory* memory){
 context(memory);require(memory->space==&space,"loader validation context");LoadValidation result{};Sha256 hash;std::array<uint8_t,65536> chunk{};
 for(const auto& row:regions_){result.mapped_bytes+=row.size;uint64_t at=row.base,end=row.base+row.size;while(at<end){uint64_t stop=end;bool skipped=false;
   for(const auto& guard:guards_){if(guard.base<=at&&at<guard.base+guard.size){uint64_t count=std::min(end,guard.base+guard.size)-at;result.guarded_bytes+=count;at+=count;skipped=true;break;}if(guard.base>at){stop=std::min(stop,guard.base);break;}}
   if(skipped)continue;if(at>=end)break;if(stop<=at)continue;size_t count=static_cast<size_t>(std::min<uint64_t>(chunk.size(),stop-at));space.read(memory,at,chunk.data(),count);require(std::memcmp(chunk.data(),row.expected.data()+static_cast<size_t>(at-row.base),count)==0,"private load byte comparison");hash.update(chunk.data(),count);at+=count;result.verified_bytes+=count;
  }}result.sha256=hash.finish();return result;
}
}
