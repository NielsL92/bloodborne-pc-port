# Native recompilation execution status

Updated 2026-09-05 23:04 UTC. PLAN.md execution is authorized, including routine cost-free actions. No native game boot, native vertical slice, or playable port exists.

| Phase | State | Evidence |
| --- | --- | --- |
| P0 | Passed with optional-data limits | Exact CUSA03173 01.09; independently repeated extraction; 28,840-file effective-v2 view. DLC entitlement unverified; trophy key absent. |
| P1 | Clinic movement and save/quit/reload demonstrated; investigation continues | Separate instrumented shadPS4 baseline. Hunter's Dream, overhead/cost separation and intermittent audio mutex crash remain open. |
| P2 | Bounded feasibility gate met for P3 | Eleven real roots / 13,584 full-state cases; promoted state, callback/nonlocal, TLS/atomic and real jump-table contracts. |
| P3 | Startup compiler and runtime gates remain open | 21,160 manifest entries; 29 independently checked control summaries; full survey plus tested BMI/trap extension builds 21,118 entries including 18,442 of 18,444 constructors. 34 compiler rejections and 8 disputed manifests remain. |
| P4-P9 | Not started; required runtime/game gates remain | 9,029 indirect-call records, 430 indirect-jump records, 8 fallthrough findings, 155 unknown callback-argument records and native import/callback/exception/control contracts remain open. |

No unwind range, pointer candidate, decoded body or built object is execution coverage. The prior 128 constructor objects and current 64 dependency objects are compilation evidence only. P3 performed no game CPU execution. No emulator, reassembly, interpreter, JIT or original-game CPU fallback replaces the native recompilation deliverable.

Continue with `local/cfg/startup-recovery-v9-repeat/analysis.sqlite` and its `recovery_*` tables, `compilation-manifest.jsonl`, `frontier.jsonl`, and `constructor-order.json`. These four files are byte-identical to v8. The old startup-db-v1 and all prior runs are preserved. Fence findings fell from 146 to 8; new callback dependencies expose additional indirect work.

Details and next experiments: `reports/startup-closure.md`, `reports/startup-closure-evidence.json`, `reports/startup-recovery.md`, the integrated recovery/control-flow evidence, `reports/compiler-spike.md`, `reports/baseline.md` and HANDOFF.md. Thirty-three recovery checks pass; sparse input checks and 8,192 authored AOT cases pass. Ghidra checks all 65 new entries and all remaining boundary entries; the continuation evidence audit passes.

User action: none. The managed sandbox helper again fails setup; approved require_escalated shell calls work. Use the working route without another restart/read approval. Existing LLVM, Remill, Ghidra, JDK and Tracy work. No PS4 access is requested.

The new isolated sparse lifter validates exact instruction boundaries and successful semantic lifting. All twelve formerly sparse-rejected bodies compile: 1,517 instructions, 46 roots, 159,654 object bytes, byte-identical fresh repeats. Twenty-seven explicit missing paths and all twelve objects retain runtime dependencies. No game-derived object was executed. See reports/sparse-compiler.md and reports/sparse-compiler-evidence.json. Next: thirty-four exact compiler rejections and eight remaining fence findings, callback provenance, indirect target closure and native runtime contracts.

Latest evidence: reports/startup-v9.md and reports/startup-batch.md. Complete compilation survey: 372 objects / 63,178,585 bytes, no duplicate logical roots. Rejected entries include two constructors; no native link or execution is claimed. Fifteen nullable exception-destructor arguments are now independently checked, with 155 callback arguments still unknown. Continue investigating the compiler and native control/runtime gates.

The added RIP-relative RVA-zero negative check passes; local/cfg/startup-recovery-v10-zero-guard reproduces the v8/v9 database, manifest, frontier and constructor order byte-for-byte. Keep v9 as the current analysis path; v10 is the unchanged guarded-code repeat.

BMI/native-trap evidence: reports/bmi-trap.md and reports/bmi-trap-evidence.json. BLSR/BLSI pass 34,816 authored hardware/reference cases. Explicit UD2 passes declaration/fault/return checks; PS4 exception delivery remains unimplemented. Fourteen prior rejected entries compile into seven byte-identical repeated objects. The two remaining constructor blockers are VSHUFPS at entries 0x10326c0 and 0x28772a0.
