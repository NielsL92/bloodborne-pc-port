# Saved LLVM control-exit census

2026-09-06 21:35 UTC. Current census: `local/compiler-spike/control-exit-inventory-v10-source-repeat`, reproducing v9-source-exits and all 386 module reports. Current complete object set: source-exit-manifest-v2-regression, SHA256 e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6. P3 remains open; no game-derived object was linked or executed.

The pinned Remill optimizer only inlines semantic functions. This census inspects saved bitcode before clang O2 and backend code generation. Earlier descriptions of these counts as optimized/emitted native paths were too broad. Structural CFG reachability follows both conditional successors and is not execution coverage.

| Boundary | All saved sites | Structurally reachable |
| --- | ---: | ---: |
| Sourced control fault | 61,536 | 61,370 |
| Sourced block transfer | 4,813 | 552 |
| Function call | 9,134 | 9,108 |
| Function return | 20,149 | 20,131 |
| Jump | 442 | 439 |
| Async / sync hypercall | 5 / 4 | 5 / 4 |
| Divide / SIMD fault | 56 / 58 | 56 / 58 |
| Generic error / missing-block | 0 / 0 | 0 / 0 |

All reachable sourced boundaries have complete conservative source-origin sets. There are 4,261 unreachable block-transfer sites and 166 unreachable sourced-fault sites. The independent 4,366 missing-start records remain unchanged; do not subtract different census types to infer execution. Reachable fault reasons: 56,993 unexpected ordinary returns, 4,372 returns violating exact nonreturn assertions, five unexpected hypercall returns. All 4,305 unique annotated nonreturn sources have guards reachable from at least one LLVM root.

The native interfaces retain source, expected/requested target, actual target and fault reason. Their call sites carry nounwind; fault sites additionally carry noreturn. Root definitions use C ABI ptr(ptr,i64,ptr) without nounwind. Unknown behavior must fail explicitly or use a separately validated nonlocal mechanism; C++ exceptions cannot simply cross nounwind.

The 552 reachable transfers represent 551 distinct direct-branch pairs. Independent decoding and relocation checks identify 524 pairs to compiled roots and 27 to verified import stubs. A compiled target alone does not authorize dispatch. Main 0x210b730 remains both an entry and the excluded continuation after 0x210b72b; the source nonreturn guard prevents treating that unexpected return as normal flow.

Read reports/source-exits.md and reports/source-exits-evidence.json for exact artifacts, compiler/input checks, source-slot analysis, repeated object identities and five independently Ghidra-checked tail-only import stubs. Inspector: build/control-audit-v6-source-slot/control-audit.exe. The actual native handlers, complete linkage and game boot remain unvalidated. P1 observations are unchanged.
