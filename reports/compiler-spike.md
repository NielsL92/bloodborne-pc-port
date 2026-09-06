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

## Full startup survey and v9 recovery (2026-09-05 22:34 UTC)

The repeated v9 recovery has 21,160 entries / 873,581 instruction addresses, eight fence findings and 155 unknown callback arguments. Twenty-nine control summaries / 265 instructions and all fifteen new null exception-destructor values are independently checked. The complete compilation survey attempts all 21,152 issue-free manifests and builds 21,104 entries, including 18,442 constructors, into 372 native objects. Its exact census is 858,411 compiled instruction addresses and 21,186 defined logical roots. Forty-eight semantic/decoder rejections and eight disputed manifests remain; see reports/startup-v9.md, reports/startup-batch.md and their machine-readable evidence. No game objects were linked or executed.

## BMI and explicit trap continuation (2026-09-05 23:04 UTC)

Tested isolated BLSR/BLSI semantics and explicit native UD2 boundaries compile fourteen more startup entries. Combined census: 21,118 entries; 34 semantic rejections and eight quarantined boundaries remain. Thirty-four thousand eight hundred sixteen authored BMI cases pass, alongside six trap declaration/control checks and the prior 8,192 authored sparse cases. Game-derived objects remain unlinked/unexecuted; all native fault delivery, services and dispatch contracts stay explicit. See reports/bmi-trap.md and reports/bmi-trap-evidence.json.

## Vector semantics and constructor compilation (2026-09-05 23:29 UTC)

All 18,444 initial constructor entries compile with the isolated, independently tested vector semantic extensions. Combined census: 21,121 entries; 31 compiler rejections and eight quarantined boundaries remain. Eight new objects reproduce byte-for-byte and supersede the seven BMI/trap objects for combined ownership. Authored checks pass 32,768 shuffle, 122,880 blend, 399,360 RSQRT and 34,816 BMI cases. RSQRT uses a native LLVM intrinsic; AMD Jaguar bit-exact estimates remain unverified. No game-derived object was linked or executed, and this does not pass startup runtime/control closure. See reports/vector-semantics.md and reports/vector-semantics-evidence.json.

## Packed integer and transfer continuation (2026-09-05 23:46 UTC)

Combined compiler census: 21,145 entries, all 18,444 initial constructors. Seven dependency entries reject and eight uncertain boundaries remain quarantined. Eleven extension objects repeat byte-for-byte, superseding earlier extension batches. Packed/select/transfer checks pass 262,144 / 376,832 / 593,408 authored cases; prior BMI/vector checks also pass in the final module. The remaining complete selector inventory covers floating-point min/max/sqrt/round and x87 environment/save operations. Guest/host MXCSR and native exception/state contracts require independent evidence. No game object was linked or executed. See reports/packed-semantics.md and reports/packed-semantics-evidence.json.

## Precise floating continuation (2026-09-06 00:18 UTC)

Combined census: 21,150 entries, all 18,444 initial constructors. Two x87 environment/save entries reject; eight uncertain boundaries remain quarantined. Integer min/max, scalar-round and sqrt semantics pass 1,572,864 / 4,194,304 / 3,145,728 authored cases, including precise guest faults and host MXCSR isolation. The complete earlier suite passes in the combined module. Eight extension objects repeat byte-for-byte, superseding earlier batches. Native Windows unwind and PS4 exception delivery are unimplemented; the authored nonlocal fixture uses an explicitly bounded System V frame. Existing x87 tag/layout/state inconsistencies require investigation before accepting FNSTENV/FLDENV/FXSAVE. See reports/fp-semantics.md/evidence. No game-derived object was linked or executed.

2026-09-06 x87 gate investigation: reports/x87-state.md/evidence preserves authored hardware/AOT counterexamples for tags, precision, split status and initialization. Twelve recovered entries own 355 x87 sites. Compiler census remains 21,150 with two rejections/eight quarantine cases; no game execution. State serialization requires a coherent native state contract. Independent callback/indirect closure work continues.

2026-09-06 callback relocation checkpoint: reports/callback-relocations.md/evidence establishes repeated v12/v13 recovery with 21,171 entries / 873,988 instruction addresses. Eleven new bodies compile into one repeated 34,421-byte object; combined 21,161 entries / 381 objects. Ghidra checks 94 windows / 4,030 shared identities plus 142 absolute slot operands. Existing instruction sets are unchanged. 9,041 indirect calls, 430 indirect jumps, 144 unknown callback arguments, two x87 compiler rejects and eight disputed manifests remain. No game execution.
