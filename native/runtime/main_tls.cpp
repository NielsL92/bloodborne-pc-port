// SPDX-License-Identifier: GPL-2.0-or-later
#include "main_tls.h"
#include <cstring>
#include <stdexcept>
#include <vector>
namespace bb_runtime {
void MainTls::initialize(Memory* m,const uint8_t* initial,size_t file_size){
 context(m);if(initialized_||m->space!=space_||m->active_import||m->active_source||m->state->addr.fs_base.qword)throw std::runtime_error("invalid main TLS initialization lifecycle");
 if(!size_||size_>1024*1024||!alignment_||(alignment_&(alignment_-1))||tcb_<size_||tcb_>UINT64_MAX-8||tcb_%alignment_||(tcb_-size_)%alignment_||file_size>size_||(file_size&&!initial))throw std::runtime_error("invalid main TLS template or layout");
 space_->check(m,tcb_-size_,size_+8,true);std::vector<uint8_t> bytes(static_cast<size_t>(size_),0);if(file_size)std::memcpy(bytes.data(),initial,file_size);space_->write(m,tcb_-size_,bytes.data(),bytes.size());space_->write(m,tcb_,&tcb_,8);m->state->addr.fs_base.qword=tcb_;initialized_=true;
}
}
