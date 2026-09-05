// SPDX-License-Identifier: GPL-2.0-or-later
// Authored compiler/Windows ABI probe. This does not establish Remill feasibility.
#include <cstdint>
#include <cstdio>
#include <intrin.h>
extern "C" uint64_t llvm_callback_probe(uint64_t, uint64_t*, uint64_t (*)(uint64_t,uint64_t*));
static uint64_t callback(uint64_t v, uint64_t* p) { *p += v; return v * 17; }
int main() {
    for (uint64_t i=0; i<1000; ++i) {
        uint64_t memory=0x8877665544332211ULL ^ i, old=memory, sum=i+old;
        uint64_t got=llvm_callback_probe(i,&memory,callback);
        if (memory != old+sum || got != ((sum*17)^(old+sum))) return 1;
    }
    int c1[4],c7[4],ext[4];
    __cpuid(c1,1); __cpuidex(c7,7,0); __cpuid(ext,0x80000001);
    unsigned long long xcr0=(c1[2]&(1<<27)) ? _xgetbv(0) : 0;
    std::printf("{\"status\":\"pass\",\"cases\":1000,\"scope\":\"authored LLVM Windows object, host callback and memory only; no game translation\",\"cpuid_1_ecx\":\"0x%x\",\"cpuid_7_ebx\":\"0x%x\",\"cpuid_ext_ecx\":\"0x%x\",\"xcr0\":\"0x%llx\"}\n",c1[2],c7[1],ext[2],xcr0);
}
