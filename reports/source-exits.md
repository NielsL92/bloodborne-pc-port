# Source-aware startup compilation exits

2026-09-06 21:35 UTC. **P3 remains open.** No game-derived object has been linked or executed. All 21,181 current entries, 21,282 unique compiled roots and 18,444 initial constructors now have a reproducible complete object set with source-aware call-return and missing-transfer interfaces.

Use `local/compiler-spike/source-exit-manifest-v2-regression/active-objects.json`, SHA256 `e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6`. Its 386 objects replace the entire preceding divide-integration set. All old objects and diagnostic runs remain preserved. The new objects total 67,835,213 bytes. Both complete builds match byte-for-byte for inputs, roots, units, audits, bitcode and objects; build times were 136.66 and 135.87 seconds.

Canonical recovery stays `local/cfg/startup-recovery-v31-conditional-repeat`, database SHA256 `f33d86bb063c338e4bebaf603ae6f32f53e9bbf49f9bf7dd70c8506edc7959ef`, manifest SHA256 `3f729683862cf6c3aa7ebbcfbaef625cff078d27e33d10b30d7f04c0a16b5f99`. The final evidence check compares every actual compiler instruction byte string against the recovery manifest: 874,279 matching module/RVA identities, each in exactly one input object. Unit identities, root ownership and constructor order are preserved. Compilation is not execution coverage.

## Compiler and input contracts

Use `build/sparse-lift-v11-source-exits/bb-sparse-lift.exe`, SHA256 `20fd7b06fafc7ae97c6cecccfb64ed0f5fd605d537e0c9125b0cbc10e469bbcf`, with unchanged v35-divide semantics, SHA256 `9fb5e55e7d5dde0482182afda9e3160f3d33298f3b724c1d21111df26446a8fa`. Original Remill source, libraries and semantics remain untouched. The previous v10 call-return correction is documented in reports/call-return.md.

All 4,305 exact `annotated_control_contract_requires_runtime` records now enter fresh compiler inputs as nonreturn assertions with database hash, module, owner, instruction bytes, target and annotation reason. Every site has one recovered owner; no conflicting owner scope was found. The five disputed endings retain their conditional provenance. No callee is marked globally noreturn. Source-exit-plan-v2-repeat reproduces every v1 input and manifest artifact.

Ordinary calls check actual returned State PC before restoring NEXT_PC. Fault reason 1 is an unexpected ordinary return PC; reason 2 is a normal return from an exact declared nonreturn site. Asynchronous hypercalls now use the same sourced fault interface with reason 3. The fault ABI is C, nounwind, noreturn: `void __bb_native_control_fault(State*, source, Memory*, reason32, wanted, actual)`.

Absent declared instruction bytes produce `Memory* __bb_native_block_transfer(State*, actual_target, Memory*, source, requested_target)`. A local, per-invocation source slot is written before each decoded instruction, so joins select the executed predecessor and nested calls cannot overwrite caller provenance. This boundary is C ABI and nounwind; it may return the result of a validated compiled transfer. A known target alone is insufficient: actual target must equal requested target and the source/request pair and code identity must be valid. Unclassified unterminated compiler blocks reject. No generic missing-block or error references remain in the complete set.

## Independent checks and census limits

The sourced-exit fixture passes 28,672 authored cases, including 24,576 hardware comparisons and sourced transfers across direct branches, ordinary fallthrough, conditional joins, loops and a nested callee. The other 4,096 cases use explicitly mocked hypercall responses, including 2,048 sourced unexpected-return faults. INT3 is not executed on the host. Full remaining State, memory and event order are compared; TEST AF is undefined and excluded. Source-exit-checks-v2-flags and v3-repeat match exactly. The ordinary-call regression still passes 14,336 cases and produces the identical final object and outcome; its pre-O2 bitcode changes because of provenance stores. Fourteen contract-input checks and the ten-case sparse-input / 8,192-case AOT regression pass. These authored escape bridges are not production guest unwind.

Pinned Remill OptimizeBareModule runs an inliner, not the full clang O2 pipeline. Saved `function.bc` is therefore semantic-inlined input to later optimization and code generation. Earlier reports calling these saved sites optimized/native emitted exits were too broad. The new LLVM inspector keeps all sites, reports structural reachability from each LLVM function entry, and conservatively resolves constant origins through PHI/select/freeze or reaching constant stores to the verified nonescaping local source slot. Dynamic values and escaped slots stay incomplete. Ten read-only provenance checks include both joins and negative cases. These analyses do not prove guest execution or count final native machine paths.

| Saved IR boundary | All sites | Structurally reachable sites |
| --- | ---: | ---: |
| Sourced control fault | 61,536 | 61,370 |
| Sourced block transfer | 4,813 | 552 |
| Function-call intrinsic | 9,134 | 9,108 |
| Return intrinsic | 20,149 | 20,131 |
| Jump intrinsic | 442 | 439 |
| Asynchronous / synchronous hypercall | 5 / 4 | 5 / 4 |

Reachable fault reasons are 56,993 ordinary-return mismatches, 4,372 nonreturn violations and five hypercall-return mismatches. All 4,305 unique nonreturn sources have a guard reachable in at least one compiled LLVM function. Multiple compiled roots can produce multiple guard instances. The separate 4,366 missing-start records remain unchanged and are not an emitted-site count. There are 4,261 structurally unreachable block-transfer sites. Generic error/missing-block references are zero; semantic divide/SIMD/x87 fault interfaces still require native implementations.

## Transfer and import registry

`source-exit-dispatch-v2-tail-imports/source-target-pairs.json` records 551 unique source/request pairs underlying 552 reachable transfer sites. Each pair independently decodes as a direct branch. Of the pairs, 524 lead to compiled roots and 27 to verified PLT import stubs; none remains unclassified. No source is a forbidden nonreturn continuation. Native dispatch is still marked unvalidated.

COFF reports 240 unresolved names: 177 verified PLT stubs and 63 support/library bindings. Five additional tail-only stubs have no undefined COFF symbol because they are reached through the block-transfer interface. The combined `native-import-stubs.json` therefore contains 182 stubs: 67 supplied compiled-export candidates and 115 external stubs. Binding/mutation/ABI assumptions remain explicit.

The five tail-only identities are main 0x2bc02f8 (sceHttpCreateEpoll), main 0x2bbe5e8 (pthread_mutex_destroy), Fios2 0x250 (sceKernelWrite), Fios2 0x550 (scePthreadSelf), and libc 0x300 (NID VADc3MNQ3cM, independently identified earlier as posix signal). Raw type-7 relocations and symbol records establish the stubs; Ghidra independently confirms all five six-byte indirect-jump boundaries in ghidra-tail-imports-v1. This does not implement those services.

The LLVM census v10-source-repeat reproduces v9-source-exits, including all 386 per-module reports. COFF v11-source-repeat reproduces v10-source-exits and every raw nm log. Coff-constants-v4-source-exits verifies 35 duplicated constants / 90 definitions / 12 objects as matching read-only relocation-free COMDAT selection-Any payloads.

## Continuation

`tools/summarize_source_exits.py` checks the complete evidence. Latest successful audit: source-exit-evidence-v2-instruction-bytes. All experiments use tools/run_record.py and fresh directories. Preserve the first fixture link failure (missing authored undefined-AF binding), the first integration audit's incorrect pre-O2 regression assertion, and the initial dispatch registry's five unresolved tail-only targets.

Next implement and validate native control/fault handling compatible with nounwind, source/target checks, and compiled/native import binding, then link the complete set. Keep unknown indirect/callback/nonlocal targets explicit. Do not use successful-return placeholders or any original-game CPU fallback. Recovery uncertainty and all native runtime obligations remain visible. P1 Hunter's Dream, overhead/cost measurements and audio mutex investigation are unchanged. User action is not needed.
