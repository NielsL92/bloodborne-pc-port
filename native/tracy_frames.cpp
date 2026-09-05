// SPDX-License-Identifier: GPL-2.0-or-later
// Read-only export of base FrameMark intervals from a pinned Tracy capture.
#include <cstdio>
#include <memory>
#include <thread>
#include <chrono>
#include "../external/tracy-tools/server/TracyFileRead.hpp"
#include "../external/tracy-tools/server/TracyWorker.hpp"
int main(int argc,char**argv){
 if(argc!=2)return 2;
 auto f=std::unique_ptr<tracy::FileRead>(tracy::FileRead::Open(argv[1]));
 if(!f)return 3;
 tracy::Worker worker(*f);
 const auto* frames=worker.GetFramesBase();if(!frames)return 4;
 const auto count=worker.GetFullFrameCount(*frames);
 std::printf("frame,start_ns,end_ns,duration_ns\n");
 for(size_t i=0;i<count;++i)
  std::printf("%zu,%lld,%lld,%lld\n",i,(long long)worker.GetFrameBegin(*frames,i),
    (long long)worker.GetFrameEnd(*frames,i),(long long)worker.GetFrameTime(*frames,i));
}
