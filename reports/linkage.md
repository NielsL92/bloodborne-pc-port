# Complete object linkage inventory

Current comparison correction (2026-09-06 20:00 UTC): reports/comi-semantics.md and its evidence record 851,968 zero-difference authored cases and fourteen exact replacement objects. The active manifest is comi-integration-manifest-v1/active-objects.json. Updated LLVM census v6-comi-repeat has 4,818 missing-block calls, 56 division errors and 58 explicit SIMD faults; COFF audit v7-comi-repeat retains 240 unresolved binding names. Earlier counts/manifests below are historical. Recovery is unchanged; P3 and native startup remain open.

2026-09-06 19:16 UTC. All 21,181 current manifest entries compile into 386 objects, but **P3 remains open**. No linker or game code was executed during this audit. Canonical recovery and the complete active object manifest remain startup-recovery-v31-conditional-repeat and conditional-control-evidence-audit-v2-exits/active-objects.json.

`tools/whole_program_linkage.py` verifies each active object hash and retained module mapping, then reads its actual COFF symbol table with pinned LLVM nm. All **21,282 compiled roots** have exactly matching function definitions. The additional roots include landing pads and explicitly recovered internal targets; this is not an execution-coverage count.

| Remaining symbol binding | Names / stub addresses |
| --- | ---: |
| Import PLT stubs with one supplied compiled-export candidate | 67 |
| External import PLT stubs without a supplied-export candidate | 110 |
| Native support / host-library symbols | 63 |
| Unclassified direct logical targets | 0 |

The 177 stubs are addresses/symbols, not necessarily 177 distinct service APIs. Every imported stub is decoded as a RIP-relative indirect jump and checked against its actual type-7 relocation and exact NID/library/provider. Supplied candidates still require native loader binding; no original module code may execute. The support list includes Remill memory/flags/control/atomics, native FP/trap hooks, SoftFloat wrappers, 128-bit division helpers and `_fltused`. Some authored implementations already exist; their availability does not establish a production runtime binding or validated service behavior.

There are 35 duplicated global constant names, comprising 90 definitions in 12 objects. `tools/check_coff_constants.py` independently checks raw COFF headers, symbol/auxiliary records, section metadata and bytes against LLVM readobj. Every duplicate is read-only, relocation-free, has selection Any, and contains the same exact payload encoded by its constant name. No compiled function root is duplicated. These checks support compatible constant coalescing; they do not link or execute the objects.

## Missing starts and exit intent

The compiler's missing-instruction-start audit contains 4,366 object/address records:

| Recorded context | Records |
| --- | ---: |
| Immediately after an annotated control contract | 4,178 |
| Explicit transfer to an already compiled root | 165 |
| Tail transfer to a verified import stub | 23 |

All 23 import-tail records are checked against their actual stub bytes and type-7 relocation, preserving the source jump and symbol identity. These records are not all missing code: many represent intentionally excluded ordinary continuation or a required native dispatch boundary.

One address demonstrates why source context matters. Main 0x210b730 is a valid compiled entry, but it is also the missing continuation after main 0x210b72b's conditional error-helper call. If that call returns unexpectedly, looking up 0x210b730 and executing its compiled function would incorrectly hide the violated contract. A native handler must preserve the reason for the exit, not infer permission from the target map.

The **4,366 count is not a complete emitted-IR exit census**. It records failed instruction-start requests during lifting. Optimization can merge multiple starts into one emitted call, and the pinned TraceLifter separately emits missing-block calls when a callee returns with an unexpected logical PC. These dynamic guards do not pass through the missing-start hook. Next inspect actual emitted LLVM calls and retain source/exit intent in the native interface before deciding the P3 gate.

## Reproduction

Current evidence is `local/compiler-spike/whole-program-linkage-v5-repeat`. It reproduces v4-stubs for objects.json, unresolved-symbols.json, duplicate-definitions.json, explicit-missing-blocks.json, known-target-after-contract.json and every raw nm log. The earlier v2-context and v3-import-tail inventories remain preserved. Their actual object/symbol identities are unchanged as source context was added.

The constant comparison is `local/compiler-spike/coff-constants-v1/checked.json`. The report auditor verifies its original v2 input identities and connects them to the unchanged current object symbols and hashes. Pinned readobj's COFF JSON output contains valid Sections/Symbols JSON fragments after a non-JSON file preamble; the tool parses only those exact fragments and preserves the complete raw output.

Every experiment uses tools/run_record.py. Preserve whole-program-linkage-v1: it rejected an input-format assumption because units.json contains entry identities rather than full bodies. V2 reads current manifests once, keeps compact edge context and verifies each retained instruction-set hash. `tools/summarize_linkage.py` checks all artifacts, repeated output identities, source snapshots and the known-target/contract conflict before producing reports/linkage-evidence.json.

Native memory/control/service implementations, complete emitted-exit handling, linkage and startup remain unvalidated. No successful return stub, CPU interpreter, JIT, emulator or original-game execution substitutes for native recompilation. P1 observations remain unchanged.
