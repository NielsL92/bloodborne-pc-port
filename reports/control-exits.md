# Retained LLVM control-exit census

2026-09-06 20:26 UTC. Current evidence is control-exit-inventory-v8-divide-repeat, byte-identical to v7-divide. Every retained bitcode module has been parsed and verified through LLVM, and its roots matched to the COFF-backed active manifest. **P3 remains open.** No input was linked or executed.

Use `local/compiler-spike/divide-integration-manifest-v1/active-objects.json`: 386 objects / 21,181 entries / 21,282 compiled roots. Recovery remains startup-recovery-v31-conditional-repeat.

| Emitted intrinsic call sites | Count |
| --- | ---: |
| Function call | 9,134 |
| Function return | 20,149 |
| Jump | 442 |
| Missing block | 4,818 |
| Generic error | 0 |
| Explicit divide fault | 56 |
| Explicit SIMD fault | 58 |
| Asynchronous / synchronous hypercall | 5 / 4 |

These are optimized LLVM call sites, not execution counts or unique guest instruction counts. The separate 4,366 missing-start records remain a different measurement. Starts can merge, and TraceLifter adds unexpected-return guards outside the missing-start hook. Do not subtract these totals to infer the number of dynamic guards.

All 4,818 missing-block calls take a loaded PC value. Their intrinsic ABI does not explicitly carry source instruction and reason. Main 0x210b730 is both a compiled entry and the excluded continuation after the conditional call at 0x210b72b. A compiled target does not authorize treating an unexpected return as ordinary dispatch.

Ordinary Remill control calls carry nounwind and are not LLVM invokes. Root definitions use the C ABI ptr(ptr, i64, ptr) and do not themselves carry nounwind. Native handlers must honor the call contract, or it must be deliberately changed and validated. Availability of C++ exceptions does not justify unwinding through nounwind calls. Zero indirect LLVM calls appear in this census; guest indirect control goes through explicit intrinsics.

## Resolved semantic error paths

The original census contained 105 generic error paths: 49 comparison-family paths and 56 division paths. Independent authored tests exposed concrete state/fault defects. The COMI/UCOMI correction passes 851,968 cases; DIV/IDIV passes 327,680 cases, including 218,424 precise faults. Both repeat, and the comparison regression is unchanged in the new division module. See reports/comi-semantics.md and reports/divide-semantics.md.

All 105 generic error references have been replaced by explicit native fault contracts. This is a statement about tested instruction semantics and emitted interfaces, not production exception delivery. The remaining x87/memory/service/control/native binding obligations persist.

Other hook counts remain in machine evidence: 16 UD2, 2 MXCSR faults, 352 x87 faults, 17 unsupported-x87 calls, and x87 span/state/policy hooks. Most fault hooks carry nounwind and noreturn; UD2 carries noreturn without nounwind. Their declarations do not establish production handlers.

## Reproduction and next work

The read-only inspector remains build/control-audit-v4-context/control-audit.exe, SHA256 e10f1493271935120a015128e9f7a90cb28be826abc19beb350c810fa2c4a63e. Tools/control_exit_inventory.py verifies object hashes, parses/verifies saved bitcode and checks root identity. The current run reproduces every aggregate artifact and all 386 per-module reports. Tools/summarize_divide.py verifies current evidence, run source snapshots and the complete replacement manifest through tools/run_record.py.

Original census artifacts remain in control-exit-inventory-v4-repeat; the comparison checkpoint remains in v6-comi-repeat. No runs were overwritten. Current reports/control-exits-evidence.json and reports/divide-semantics-evidence.json point to the latest set.

Next add source/expected-continuation/exit-reason information at compiler boundaries and validate compatible native handling, then bind and link the full set before deciding P3. No native game boot or playable port exists. P1 observations are unchanged.
