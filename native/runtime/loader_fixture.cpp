// SPDX-License-Identifier: GPL-2.0-or-later
#include "loader.h"
#include <cstdlib>
#include <cstring>
#include <exception>
int main(int argc,char** argv){
 if(argc!=5&&argc!=6)return 2;
 try{
  auto loaded=bb_runtime::load_private_image(argv[1],argv[2],argv[3]);State state{};Memory memory{};const bb_runtime::Tables tables{nullptr,0,nullptr,0,nullptr,0,argv[3]};memory.tables=&tables;memory.state=&state;memory.space=&loaded->space;memory.owner_thread=GetCurrentThreadId();
  if(std::strcmp(argv[4],"guard")==0){if(argc!=6)return 2;auto index=std::strtoul(argv[5],nullptr,10);if(index>=loaded->guards().size())return 2;const auto& guard=loaded->guards()[index];uint8_t value;loaded->space.read(&memory,guard.base,&value,1);return 2;}
  if(std::strcmp(argv[4],"validate")!=0||argc!=5)return 2;auto result=loaded->validate(&memory);
  std::printf("{\"status\":\"private-load-validated\",\"regions\":%llu,\"relocations\":%llu,\"guards\":%llu,\"mapped_bytes\":%llu,\"verified_bytes\":%llu,\"guarded_bytes\":%llu,\"sha256_unguarded\":\"%s\",\"game_execution\":false}\n",(unsigned long long)loaded->region_count(),(unsigned long long)loaded->relocation_count(),(unsigned long long)loaded->guards().size(),(unsigned long long)result.mapped_bytes,(unsigned long long)result.verified_bytes,(unsigned long long)result.guarded_bytes,result.sha256.c_str());return 0;
 }catch(const std::exception& e){std::fprintf(stderr,"Native loader rejected: %s\n",e.what());return 2;}
}
