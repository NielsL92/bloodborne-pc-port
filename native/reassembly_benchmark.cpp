// SPDX-License-Identifier: GPL-2.0-or-later
// Static reassembly comparison only. This is not the lifted native-port deliverable.
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
using Fn=uint64_t(__attribute__((sysv_abi)) *)(uint8_t*);
extern "C" __attribute__((sysv_abi)) uint64_t reassembled_loop(uint8_t*);
extern "C" __attribute__((sysv_abi)) uint64_t reassembled_hash(uint8_t*);
template<class T>void put(uint8_t*p,size_t off,T v){std::memcpy(p+off,&v,sizeof(v));}
static volatile uint64_t checksum;
int main(int argc,char**argv){
 if(argc!=2)return 2;
 auto code=static_cast<uint8_t*>(VirtualAlloc(reinterpret_cast<void*>(0x100000000ULL),0x100000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 auto arena=static_cast<uint8_t*>(VirtualAlloc(nullptr,0x10000,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE));
 if(!code||!arena)return 3;
 for(int rva:{0x3360,0x2fa30,0x5e4e0}){
  char name[40];std::snprintf(name,sizeof(name),"/%x.bin",rva);
  std::ifstream f(std::string(argv[1])+name,std::ios::binary);std::vector<uint8_t>d((std::istreambuf_iterator<char>(f)),{});
  if(d.empty())return 4;std::memcpy(code+rva,d.data(),d.size());
 }
 FlushInstructionCache(GetCurrentProcess(),code,0x100000);
 for(int kernel=0;kernel<2;++kernel)for(int length:{8,64}){
  std::memset(arena,0,0x10000);
  if(!kernel){
   for(int i=0;i<length;++i){auto node=arena+i*256;put(node,0x38,i+1<length?uint64_t(node+256):0);
    put(node,0x6a,uint8_t(i==length-1?0x80:0));put(node,0x20,uint64_t(arena+0x8000));}
   put(arena+0x8000,0x10,uint64_t(0x1122334455667788ULL));
  }else{
   auto text=arena+0x1000;put(arena,0x18,uint64_t(text));put(text,0,uint64_t(length));put(arena,0xc,uint32_t(71));
   for(int i=0;i<length;++i)text[0xc+i]=uint8_t(i*31);
  }
  auto original=reinterpret_cast<Fn>(code+(kernel?0x2fa30:0x3360));
  Fn rewritten=kernel?reassembled_hash:reassembled_loop;constexpr int N=1000000;
  for(int rep=-1;rep<5;++rep){
   uint64_t sums[2]={};double ns[2]={};
   for(int step=0;step<2;++step){
    int side=(rep+step)&1;DWORD old;
    if(!VirtualProtect(code,0x100000,side?PAGE_READONLY:PAGE_EXECUTE_READ,&old))return 5;
    MEMORY_BASIC_INFORMATION mbi{};VirtualQuery(code,&mbi,sizeof(mbi));if(side&&mbi.Protect!=PAGE_READONLY)return 6;
    Fn fn=side?rewritten:original;auto begin=std::chrono::steady_clock::now();
    for(int n=0;n<N;++n)sums[side]+=fn(arena);
    ns[side]=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-begin).count()/N;
   }
   if(sums[0]!=sums[1])return 7;checksum=sums[0];
   if(rep>=0)std::printf("{\"kernel\":\"%s\",\"length\":%d,\"rep\":%d,\"native_ns\":%.3f,\"reassembled_ns\":%.3f,\"ratio\":%.4f,\"original_code_NX_during_reassembly\":true}\n",kernel?"hash":"loop",length,rep,ns[0],ns[1],ns[1]/ns[0]);
  }
 }
}
