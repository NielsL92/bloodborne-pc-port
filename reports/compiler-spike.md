# P2 whole-function compiler experiment

Recorded 2026-09-05. **Gate failed / expansion stopped at P2.** The Windows Remill route produces working AOT routines, but its optimized state representation remains above the plan's approximately 2x slowdown threshold in both measured kernels after a concrete memory-lowering alternative. Required runtime-control and discovery coverage also remains incomplete. No native game boot or playable port is demonstrated.

## Decision

Retain Remill as a functioning semantic/compiler candidate and retain the regression harnesses. Do not begin broad P3/P4 integration on the current representation. A continuation must demonstrate state/flag promotion or another explicitly evaluated compiler design on these same contracts and benchmarks before widening coverage. No emulator fork, original-code execution build or static reassembly is being substituted as the requested endpoint.

The failed layer is primarily the generated state/memory representation in the tested kernels. Initial memory-helper overhead was large; replacing ordinary memory/annotation intrinsics with inlined loads/stores removes much of it, but generated loops still calculate and store flags, guest GPRs and logical PC values on each iteration. Disassembly is preserved in local/compiler-spike/performance/loop-lowered.asm.txt and hash-lowered.asm.txt. This does not prove that every Remill program is slow or that native recompilation cannot work. It establishes that this implementation has not passed the approved integration gate.

## Exact compiler path

Remill source 56918a8c2554088e93389e97d292f4035286506c, LLVM 21.1.8 full Windows SDK, clang-cl/MSVC ABI, installed VS18 DIA/Windows SDK, amd64_avx semantics. Native Windows COFF objects link and run. LLVM 21 is an explicitly tested external SDK; Remill's default dependency superbuild uses LLVM 17.0.6. WSL is absent and was not needed. Source/submodule/tool hashes are in reports/dependency-lock.json and reports/toolchain-downloads.json.

Preserved patch patches/remill-windows-sdk.patch:
- Omit unused SPARC codegen linkage when the selected LLVM SDK lacks that target.
- Redirect the SDK's stale VS2019 DIA import to the installed VS18 DIA SDK.
- Add a raw byte-file input to the example lifter for Windows command-length limits.
- Correct CMPSS/VCMPSS destination initialization to preserve source-1 bits 127:32.

Native upstream Remill testing is disabled because its native execution tests are not supported on this Windows path. The independent project harness described below supplies the actual execution checks; successful compilation is not treated as testing.

## Real routine contracts

Addresses are RVAs in effective eboot.bin SHA-256 d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9. These are behavioral fixture descriptions, not recovered source-level function names.

| Root RVA | Contract | Final cases |
| --- | --- | ---: |
| 0x3360 | Linked object traversal, marked ancestor and payload lookup | 720 |
| 0x1a50 | Two-float copy, nullable source, equal/overlapping output buffers | 1,536 |
| 0x3500 | Object flags and scalar float comparisons with early exits | 1,536 |
| 0x3530 | Scalar vector stores and conditional packed-flag updates | 1,536 |
| 0x2550 | Page-aligned metadata lookup and linked-object traversal | 1,024 |
| 0x65d0 | Membership traversal, null termination and partial-register return | 1,024 |
| 0xb820 | Nested array/object predicate with signed comparisons | 1,024 |
| 0x2fa30 -> 0x5e4e0 | Tagged pointer, reverse string hash, stack and direct call | 1,024 |
| 0x3df50 -> 0x77e80 | Nested collection calls, aliases and repeated memory writes | 1,024 |
| 0x3240 -> 0x2b2b0 | Virtual function table dispatch and early-exit list traversal | 1,024 |

Ten nontrivial root contracts, three additional callees, 11,472 final input cases. The small getter at 0x2b2b0 is part of a virtual-call graph, not an extra root counted toward the ten. An independently computed string hash and linked-list expectation supplement the instruction oracle.

The original instructions run only inside an isolated differential-test process. All object graphs and stacks are allocated and initialized to valid contract states. Before every AOT invocation the original-code mapping becomes PAGE_READONLY; VirtualQuery verifies that it is non-executable. Generated entries and explicit compiled-entry dispatch execute the AOT side. The fixture is not a standalone game/runtime implementation.

Comparison covers all 16 GPRs, defined arithmetic flags and preserved DF, all bytes of YMM0–15, MXCSR, the allocated object arena and guest stack, and final return target. The later loop validation adds DF to the original 720-case check. Undefined AF after logical instructions is excluded; AF is checked for paths ending in instructions that define it. SIMD fixtures cover signed zero, finite values, infinities, quiet/signaling NaNs, subnormals and the normal boundary, four rounding modes, DAZ and FTZ. Floating-point exceptions are masked; MXCSR status is compared. No permissive fast-math option is enabled. x87/MMX, unmasked exception delivery and Jaguar-specific differences are outside these contracts.

The direct call graphs link known AOT symbols. Virtual calls use an explicit logical-PC-to-compiled-entry dispatcher: 3,411 calls were exercised. The dispatcher has an unknown-target error path and no original-code fallback. Direct calls bypass this dispatcher; a first harness incorrectly expected them to increment the indirect-call counter. Counting completed guest calls fixed that accounting error, after which every contract passed. This was a harness failure, not a guest-state mismatch.

Evidence:
- local/runs/20260905-p2-real-loop-test
- local/runs/20260905-p2-cmpss-retest-fresh
- local/runs/20260905-p2-real-graphs-return-count
- local/compiler-spike/initial
- local/compiler-spike/varied-cmpss-fixed
- local/compiler-spike/graphs-return-count

## Failed semantic gate and its correction

Unmodified Remill semantics failed 384 of 1,536 cases for 0x3500. A minimal ordinary finite input also failed, so this was not merely a NaN policy disagreement. The first mismatch was YMM0 byte 4: AOT zeroed it while the original instruction copied the corresponding source-1 byte. Remill's CMPSS implementation initialized the destination vector with zero.

Intel specifies preservation of source-1 bits 127:32 for VEX VCMPSS, with the higher vector bits zeroed. The targeted correction initializes from source 1 and leaves Remill's existing VEX writer to handle the upper vector. All 1,536 cases then pass, together with both neighboring SIMD contracts. [Intel instruction-set reference](https://www.intel.com/content/dam/develop/external/us/en/documents/319433-024-697869.pdf).

The failing binary, bitcode, inputs and logs remain in local/compiler-spike/varied-before-cmpss-fix. Its original C++ harness was reconstructed from the small recorded changes and matches the exact SHA-256 in the failing run manifest; source-reconstruction.json records that check. The correction is confined to CMPSS; analogous instructions are not claimed validated.

A repeated lift into existing files also uncovered a Windows output problem: upstream emitted a rename-over-existing error yet returned zero. The retry workflow now creates fresh output directories. Failed attempts remain recorded and are not counted as successful relifts.

## Scaling

The deterministic, structurally stratified 1,000-function batch contains small, medium, large and very large ranges rather than 1,000 easy leaves. Capstone tags include 483 loop candidates, 750 direct-call candidates, 546 indirect-call candidates and 320 SIMD candidates; tags are overlapping and not correctness claims. Ninety-seven ranges are not fully decoded by linear Capstone traversal, including possible embedded-data/boundary ambiguity.

| Measurement | Observed |
| --- | ---: |
| Windows objects generated | 1,000 / 1,000 |
| Total survey wall time | 286.05 seconds |
| Summed lifting time | 111.01 seconds |
| Summed object compilation time | 158.22 seconds |
| Maximum observed per-process working set | 266,711,040 bytes |
| Total COFF object bytes | 22,770,632 |
| Objects retaining unresolved execution boundaries | 842 |

The unresolved boundaries include calls, jumps, missing blocks, errors and hypercalls. Therefore 1,000 objects do not mean 1,000 executable functions or any percentage of game completion. The example CLI is a trace lifter, not the P3 recovery system. Per-process bounds were 60 seconds and 4 GiB; none of the selected object builds exceeded them. Evidence: 20260905-p2-scale-1000 and local/compiler-spike/scale-default. This survey used the pre-CMPSS semantics and retains its recorded identities; it was not silently overwritten after the correction.

A single-function incremental rebuild measured 36.2 ms for the helper version and 32.2 ms for the lowered version. Their object sizes were 1,678 and 783 bytes; machine-code sections were 670 and 302 bytes. Raw COFF hashes changed on rebuild only because of the four-byte timestamp. Excluding that field, both complete objects and their code sections match exactly. See performance/builds.json and coff-reproducibility.json. These timings establish a local incremental compile measurement, not a complete large-project dependency/relink benchmark.

## Performance gate

Measured after the compiler/baseline builds finished and after bounded game captures ended. Same host, -O2, -march=haswell. Each kernel has an unreported warm-up and five recorded repetitions, alternating native/AOT order. The original runs as a normal SysV function call rather than through the expensive full-state oracle bridge. The AOT side resets its required argument/stack state and calls a generated entry. Both results are checked; timing excludes page protection changes. Medians below are host-only kernel measurements, not game frame-rate predictions.

| Kernel / input length | Original ns | AOT helpers ns | Helper slowdown | AOT lowered ns | Lowered slowdown |
| --- | ---: | ---: | ---: | ---: | ---: |
| List / 1 | 1.14 | 16.77 | 14.78x | 2.66 | 2.35x |
| List / 8 | 3.36 | 71.73 | 21.47x | 13.38 | 4.60x |
| List / 64 | 51.28 | 295.99 | 5.76x | 99.33 | 2.02x |
| Hash graph / 8 | 5.12 | 122.93 | 23.35x | 20.98 | 3.96x |
| Hash graph / 64 | 29.26 | 729.21 | 24.84x | 107.03 | 3.69x |
| Hash graph / 1,024 | 761.12 | 11,142.22 | 14.68x | 1,593.21 | 2.10x |

Original medians vary slightly between helper and lowered measurements; ratios use each paired run's own native measurement. All repetitions and pairings are in performance/*.jsonl and hash-performance/*.jsonl. The very shortest timings should be interpreted cautiously; the longer loop and closed hash graph also remain above the threshold.

The alternative tested is compiler-level inlining of ordinary memory and annotation intrinsics under explicit valid-memory contracts. It is not an instruction-by-instruction replacement translator. It is unsuitable for MMIO, atomics, untrusted mappings or cases where the guest can alias the compiler's State object. The lowered loop and hash graph pass the same full-state oracle checks before timing. The improvement is substantial, but it does not pass the performance gate. Do not deploy this contract-only lowering as a universal memory implementation.

## Remaining gate items

| Capability | State |
| --- | --- |
| Windows AOT link/run and bounded memory/stack contracts | Demonstrated |
| Branches, loops, aliases, SIMD/FP, direct and virtual calls | Demonstrated within listed contracts |
| Real jump-table and RIP-relative global-data contracts | Not yet demonstrated |
| Guest-to-host-to-guest service callback | Authored Windows ABI probe only; no complete Remill service gateway |
| Logical nonlocal transfer / exception propagation | Not demonstrated |
| TLS and per-thread machine-state isolation | Not demonstrated |
| Locked atomics and memory ordering | Not demonstrated |
| Recoverable unmasked guest exceptions | Not demonstrated |
| Broad CFG recovery / all startup targets | Not attempted; P3 remains gated |
| Representative optimized performance below warning threshold | Failed after memory-lowering alternative |

The missing items are not silently marked passed by the ten routines. Expansion stops because the plan explicitly requires a demonstrated mitigation for persistent slowdowns before broad integration. A next compiler experiment should address state promotion and boundary semantics together, preserve every defined output and fail closed on unknown control flow. The bounded static-reassembly comparison below remains an explicitly different approach, not an adopted replacement endpoint.

## Bounded static-reassembly comparison

The plan's separate comparison was completed in 20260905-p2-reassembly-comparison. Capstone-decoded instructions for the same loop and hash graph were assembled with LLVM's x64 assembler; known local branches/calls were rebound to compiled labels. This is static instruction reassembly, not Remill lifting or a new game runtime. It was not adopted as the endpoint.

Five measured repetitions per kernel/length, after warm-up, preserve scalar return equality on valid read-only objects. Original guest-code pages are non-executable while the reassembled COFF functions run. Full guest-state/logical-return-address equivalence is not claimed for this narrower comparison.

Median reassembled/original time ratios: loop length 8 = 1.081x, loop 64 = 0.989x, hash 8 = 0.627x, hash 64 = 0.994x. The short hash timing is particularly sensitive to host layout/alignment and is not a whole-game speedup. The comparison confirms that preserving native instructions avoids much of the tested explicit-state cost. It does not resolve the required lifted compiler's state/control-flow design, broad relocation, service boundaries, or logical addresses.

Evidence: local/compiler-spike/reassembly-comparison/summary.json and results.jsonl; authored driver tools/reassembly_comparison.py and native/reassembly_benchmark.cpp. P2's selected lifted route remains failed for broad integration.
