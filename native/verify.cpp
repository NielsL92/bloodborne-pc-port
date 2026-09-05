// SPDX-License-Identifier: GPL-2.0-or-later
// Differential oracle: execute ONLY validated register-only leaves from the
// user's local executable, and compare them with their statically compiled C++.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>

using Function = uint64_t (*)(const uint64_t*);
struct ProofFunction {
    uint64_t address;
    const unsigned char* original;
    size_t size;
    Function compiled;
};
#include "functions.inc"

int main() {
    // Windows receives an argument-array pointer in RCX. Preserve the two
    // Windows nonvolatile registers used by the System V integer argument ABI.
    // These leaves cannot touch other nonvolatile registers or the red zone.
    static constexpr unsigned char bridge[] = {
        0x57, 0x56,                         // push rdi; push rsi
        0x48, 0x89, 0xc8,                   // mov rax, rcx
        0x48, 0x8b, 0x38,                   // mov rdi, [rax]
        0x48, 0x8b, 0x70, 0x08,             // mov rsi, [rax+8]
        0x48, 0x8b, 0x50, 0x10,             // mov rdx, [rax+16]
        0x48, 0x8b, 0x48, 0x18,             // mov rcx, [rax+24]
        0x4c, 0x8b, 0x40, 0x20,             // mov r8, [rax+32]
        0x4c, 0x8b, 0x48, 0x28,             // mov r9, [rax+40]
        0x48, 0x83, 0xec, 0x08,             // sub rsp, 8 (align for call)
        0xe8, 0x07, 0x00, 0x00, 0x00,       // call leaf after epilogue
        0x48, 0x83, 0xc4, 0x08,             // add rsp, 8
        0x5e, 0x5f, 0xc3                    // pop rsi; pop rdi; ret
    };
    std::mt19937_64 random(UINT64_C(0xb100db09));
    uint64_t total = 0;
    for (const auto& test : proof_functions) {
        size_t allocation = sizeof(bridge) + test.size;
        auto* memory = static_cast<unsigned char*>(VirtualAlloc(nullptr, allocation, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE));
        if (!memory) { std::fprintf(stderr, "VirtualAlloc failed: %lu\n", GetLastError()); return 2; }
        std::memcpy(memory, bridge, sizeof(bridge));
        std::memcpy(memory + sizeof(bridge), test.original, test.size);
        DWORD old = 0;
        if (!VirtualProtect(memory, allocation, PAGE_EXECUTE_READ, &old) || !FlushInstructionCache(GetCurrentProcess(), memory, allocation)) {
            std::fprintf(stderr, "Executable memory setup failed: %lu\n", GetLastError());
            VirtualFree(memory, 0, MEM_RELEASE);
            return 2;
        }
        auto original = reinterpret_cast<Function>(memory);
        std::array<uint64_t, 6> args{};
        auto compare = [&]() {
            uint64_t expected = original(args.data());
            uint64_t actual = test.compiled(args.data());
            ++total;
            if (expected == actual) return true;
            std::fprintf(stderr, "FAIL RVA=%llx expected=%llx actual=%llx inputs=", test.address, expected, actual);
            for (auto value : args) std::fprintf(stderr, "%llx,", value);
            std::fprintf(stderr, "\n");
            return false;
        };
        bool ok = true;
        constexpr std::array<uint64_t, 12> edges = {0, 1, 2, 7, 31, 63, 0x7fffffff, 0x80000000, 0xffffffff,
                                                   0x100000000, 0x8000000000000000, UINT64_MAX};
        for (auto value : edges) {
            args.fill(value);
            if (!compare()) { ok = false; break; }
            for (size_t i = 0; i < 6; ++i) args[i] = edges[(value + i) % edges.size()];
            if (!compare()) { ok = false; break; }
        }
        for (size_t arg = 0; ok && arg < 6; ++arg) {
            for (unsigned bit = 0; bit < 64; ++bit) {
                args.fill(0); args[arg] = UINT64_C(1) << bit;
                if (!compare()) { ok = false; break; }
                args.fill(UINT64_MAX); args[arg] = ~(UINT64_C(1) << bit);
                if (!compare()) { ok = false; break; }
            }
        }
        for (int i = 0; ok && i < 10000; ++i) {
            for (auto& value : args) value = random();
            if (!compare()) { ok = false; break; }
        }
        VirtualFree(memory, 0, MEM_RELEASE);
        if (!ok) return 1;
    }
    std::printf("{\"status\":\"pass\",\"functions\":%zu,\"cases\":%llu,\"random_seed\":\"0xb100db09\",\"scope\":\"scalar leaf recompilation only; game not booted\"}\n",
                std::size(proof_functions), total);
    return 0;
}
