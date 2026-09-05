# P2 whole-function compiler experiment

Updated 2026-09-05. The bounded feasibility gate now supports proceeding to P3. No native gameplay or complete port is demonstrated. The earlier failed performance/coverage gate and all failed runs remain preserved in reports/archive/compiler-spike-pre-restart.md and local/runs.

Remill 56918a8c2554088e93389e97d292f4035286506c produces LLVM 21.1.8 Windows COFF objects using the existing MSVC/SDK environment. The original CMPSS correction remains covered by the existing full-state regressions. Static reassembly remains a separately labeled comparison, not the selected endpoint.

## State promotion and performance

native/state_promotion audits all uses of the State pointer before promoting constant byte ranges into local allocations. LLVM O2 can then remove repeated register/flag/PC stores in loops. The pass synchronizes external State at recognized calls and returns, rejects unrecognized escapes, atomics/volatile state accesses, variable offsets, and exceptional call instructions, and verifies the resulting LLVM module. The executable and each intermediate IR/object are preserved per experiment.

state-promotion-v3 passes all ten prior root contracts: 11,472 cases, including 3,411 indirect compiled calls. This compares GPRs, defined flags, YMM0-15, MXCSR, guest memory/stack writes and logical returns. Original guest code pages are read-only/non-executable during every AOT call.

Five paired repetitions were measured after builds and game captures ended. Ratios are medians of paired AOT/original observations, so they need not equal the ratio of the two displayed medians.

| Kernel / length | Original ns | Promoted AOT ns | Paired ratio |
| --- | ---: | ---: | ---: |
| List / 1 | 1.058 | 2.307 | 2.2221 |
| List / 8 | 3.110 | 2.842 | 0.8504 |
| List / 64 | 43.150 | 45.019 | 1.0205 |
| Hash / 8 | 5.287 | 7.452 | 1.3665 |
| Hash / 64 | 30.606 | 40.562 | 1.3138 |
| Hash / 1024 | 793.500 | 608.688 | 0.7665 |

Evidence: local/compiler-spike/state-promotion-v3/measurement/summary.json; runs 20260905-p2-promoted-contracts-v3 and 20260905-p2-promoted-timing. The representative longer kernels now demonstrate mitigation of the previous 2–4.6x slowdown. The one-element case still exceeds 2x at about 1.25 ns additional cost. These are kernel measurements, not whole-game speedups.

Failed promotion v1 rejected SIMD memset; v2 rejected the explicit Remill error boundary. Constant-sized memory intrinsics and error synchronization were then supported. Both failures remain immutable.

## Control, threads, and real jump-table data

| Contract | Result / evidence |
| --- | --- |
| Guest → native service → compiled callback | 256 normal cases, ordered services and output writes; control-flow-v7 |
| Logical nonlocal transfer through callback and service | 256 cases; explicit token propagation skips both compiled suffixes; control-flow-v7 |
| Unknown target | Exit 4 with module/fixture hash, caller, target and register diagnostics; no fallback |
| Missing nonlocal guard | Expected write fault at protected original-code page 0x1001000000; negative test checks exact AOT phase/address/exit |
| TLS | 4 threads × 2048 calls per path; thread-specific Windows GS/TLS fixture; thread-boundary-v2 |
| Locked XADD | 8192 calls per path; complete unique ticket permutation and final count under contention |
| Publication order | 8192 MFENCE handshakes per path; no stale payload observed |
| Real jump table and RIP-relative data | RVA 0x401f0; 2112 full-state cases, all five targets, independent bit-by-bit reference; real-jump-v1 |

The nonlocal reference harness initially crashed before the AOT side. A SysV wrapper alone did not fix it: disassembly showed Clang tail-calling out of the builtin-setjmp frame. Disabling that tail call kept the frame alive and the original reference passed. Failed v2–v4 and disassembly remain retained; this was a harness failure, not a demonstrated Remill semantic defect. The negative-test v6 address expectation was also corrected: Windows reports a noncanonical fault address as -1, so v7 uses a canonical protected page.

The service fixture compares the declared ABI return, ordered service events, two guest output words, preserved RBX and logical RSP/RIP. It excludes the reference's private native stack and caller-clobbered registers. It demonstrates an explicit logical transfer, not C++/SEH unwinding through LLVM nounwind frames.

Thread fixtures keep memory helpers external. They use aligned relaxed atomic memory, a serialized atomic section and conservative seq-cst fences. The TLS test uses an owned inline Windows TLS slot and explicitly verifies its TEB offset. It is not a PS4 TLS implementation or exhaustive proof of every memory-order/atomic operation.

The real bit-reader's 412-byte unwind range contains 20 bytes of table data after the code. Linear full-range decoding rejected it; targeted recovery reads five signed relative entries at RVA 0x40378 and a 33-byte lookup table at 0x2bc0f50. All five targets are compiled ahead of time and dispatched explicitly. This is one validated recovery contract, not a general jump-table discovery algorithm.

## Gate and limits

There are now eleven real root contracts / 13,584 full-state cases. Required tested control boundaries have credible demonstrations; the prior scale survey fits this host (1000 objects, 286 seconds, 254 MiB maximum observed per-process working set). Its 842 unresolved execution boundaries remain unresolved; the survey predates state promotion and the CMPSS correction and is not execution coverage.

Proceed to P3 recovery work using Remill as the selected candidate. P4 broad runtime execution still requires guarded guest mappings, recoverable fault/exception behavior, service ABI coverage, and startup target closure. Promoted State cannot be asynchronously observed inside a region; guest memory must not alias compiler State. Direct memory lowering applies only to the validated ordinary-memory contracts. Unmasked FP faults, arbitrary aliases, signals/SEH, MMIO, and unregistered host writers are not proven.

Reproduce with tools/state_promotion_experiment.py, tools/control_flow_experiment.py, tools/thread_boundary_experiment.py and tools/jump_table_experiment.py, always with fresh output directories and tools/run_record.py. Pin identities in reports/dependency-lock.json and per-run source ZIPs.

## P3 manifest compilation checkpoint

2026-09-05: 128 constructor ordinals spanning the recovered invocation list build Windows COFF objects directly from identity-checked manifest instruction bytes. All selected regions were contiguous; sparse regions are explicitly rejected by this consumer. Total object bytes: 401,948; 25 objects retain declared CPU boundaries. External memory/control helpers remain unresolved, no runtime link or execution was attempted, and this is not another P2 differential-case count or a startup gate pass. Evidence: local/compiler-spike/startup-manifest-v1 and reports/startup-recovery.md.

Continuation at 20:59 UTC: all 65 newly recovered callback/dependency entries were selected in module/RVA order. Fifty-two built Windows objects totaling 118,587 bytes; 42 retain CPU boundary declarations. Twelve sparse instruction sets require a sparse input adapter, and one entry retains a fence issue; all 13 were explicitly excluded with manifests/reasons preserved. No filler, runtime link, execution, differential-case count or speed result is claimed. The consumer now accepts an explicit module/RVA entry list and verifies the appropriate supplied module for each entry. Evidence: local/compiler-spike/callback-manifest-v1, reports/startup-closure.md and reports/startup-closure-evidence.json.

## Sparse compilation continuation (2026-09-05 22:14 UTC)

The isolated manifest lifter now compiles all twelve previously sparse-rejected dependency bodies: 1,517 instructions / 46 roots / 159,654 object bytes. Two fresh deterministic emissions are byte-identical; no filler is inserted, and every supplied instruction must match Remill boundaries and lift successfully. Ten input checks and 8,192 authored AOT cases pass. These are additional authored checks, separate from earlier real-function comparisons. The game-derived objects were not linked or executed and retain 27 explicit missing paths plus native runtime dependencies. The recovery graph remains v7 with nine fence findings and unresolved indirect/callback/exception/service contracts. See reports/sparse-compiler.md and reports/sparse-compiler-evidence.json.
