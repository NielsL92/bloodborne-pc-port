# Retained LLVM control-exit census

Current update — 2026-09-06 20:00 UTC. Reports/comi-semantics.md and reports/comi-semantics-evidence.json supersede the comparison investigation below. All sixteen COMI/UCOMI forms pass authored tests; the fourteen affected objects are replaced in comi-integration-manifest-v1/active-objects.json. Current census control-exit-inventory-v6-comi-repeat matches v5-comi byte-for-byte. It has **56 division error calls and 58 explicit SIMD fault calls**; the 49 legacy comparison error paths are removed. All other control counts below are unchanged. The remaining division semantics and source/exit intent are next. P3 remains open.

The following records the pre-correction census; its artifacts and exact source snapshot remain preserved.


2026-09-06 19:39 UTC. Every retained bitcode module has been parsed and verified through the pinned LLVM API, with its function definitions matched to the current COFF-backed active object manifest. **P3 remains open.** No input was JIT compiled, linked or executed. Canonical recovery and the 386-object compilation census are unchanged.

| Emitted intrinsic call sites | Count |
| --- | ---: |
| Function call | 9,134 |
| Function return | 20,149 |
| Jump | 442 |
| Missing block | 4,818 |
| Error | 105 |
| Asynchronous / synchronous hypercall | 5 / 4 |

These are optimized LLVM call sites across 21,282 compiled function roots, not execution counts or unique guest instruction counts. The compiler's separate 4,366 missing-start records remain valid but are a different measurement. Multiple starts can merge, and TraceLifter adds dynamic unexpected-return guards outside the missing-start hook. Do not subtract the two totals to infer an exact count of those guards.

All 4,818 missing-block sites take a loaded PC value. The intrinsic ABI does not explicitly carry the originating guest instruction and reason. Main 0x210b730 remains the concrete target-availability conflict: it is both an existing compiled entry and the excluded continuation after the conditional helper call at 0x210b72b. Unexpected returns must not become ordinary dispatch merely because their target is present.

All ordinary Remill control call sites in this census carry `nounwind`; none is an LLVM `invoke`. Compiled root definitions themselves are C ABI `ptr(ptr, i64, ptr)` and do not carry `nounwind`. Native code must honor the call-site contract or deliberately change and validate it. The availability of C++ exceptions does not establish safe unwinding through these calls. There are zero indirect LLVM calls in these modules: recovered guest indirect flow goes through explicit control intrinsics.

## Error attribution and the next semantic check

Retained inlined successor names identify all 105 error sites: 56 division-family sites (26 DIVrdxrax, 10 DIVedxeax, 10 IDIVrdxrax, 10 IDIVedxeax) and 49 scalar-comparison sites (32 COMISS, 17 COMISD). Pinned Operators.h defines StopFailure through __remill_error; BINARY.cpp uses it for division checks, and SSE.cpp uses it in comparison semantics. Thus an error-intrinsic reference alone is not evidence of failed lifting. The names establish semantic-family attribution, not correct fault behavior or precise guest fault-PC attribution. Pinned UCOMI/VUCOMI selectors also use these COMISS/COMISD implementations, so the names do not distinguish ordered from unordered guest instruction forms.

The COMISS/COMISD source is a concrete investigation lead: its unordered path tests signaling-NaN status after a host floating addition, and lacks explicit guest MXCSR mask/status/DAZ handling. Independent authored hardware/AOT checks are next; this census does not yet claim or correct a hardware disagreement. Division fault-PC/overflow handling also remains to be checked. Every discovered boundary must receive an explicit native contract.

Native hook counts are recorded completely in the machine evidence, including 16 UD2, 9 SIMD faults, 2 MXCSR faults, 352 x87 faults and 17 unsupported-x87 sites. Most fault hooks are `nounwind` and `noreturn`; the UD2 hook is `noreturn` without `nounwind`. Other x87 span/state/policy hooks are also inventoried. These declarations are not production handler validation or PS4 exception delivery.

## Reproduction

Current evidence: `local/compiler-spike/control-exit-inventory-v4-repeat`, byte-identical to v3-origins for summary.json, all four aggregate artifacts and all 386 per-module reports. The read-only inspector is `build/control-audit-v4-context/control-audit.exe`, SHA256 `e10f1493271935120a015128e9f7a90cb28be826abc19beb350c810fa2c4a63e`. It uses LLVM ModuleSlotTracker for bounded SSA formatting. Every active object and bitcode identity is retained; each module is verified and root sets must match exactly.

`tools/build_control_audit.py`, `tools/control_exit_inventory.py` and `tools/summarize_control_exits.py` reproduce the build, census and evidence audit through tools/run_record.py. Preserve the failed control-audit-build-v1 LLVM API/include attempt and all earlier inventory versions. Reports/control-exits-evidence.json verifies repeat artifacts, current object/bitcode hashes, pinned source identities and run source snapshots.

Next: independently characterize the comparison semantics and preserve source/exit intent in native boundaries, then validate native handlers and whole-set linkage. No native game boot or playable port exists. P1 baseline observations are unchanged.
