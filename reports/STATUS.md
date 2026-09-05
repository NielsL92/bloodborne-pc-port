# Native recompilation execution status

Updated 2026-09-05 20:57 UTC. PLAN.md execution is authorized, including routine cost-free actions. No native game boot, native vertical slice, or playable port exists.

| Phase | State | Evidence |
| --- | --- | --- |
| P0 | Passed with optional-data limits | Exact CUSA03173 01.09; independently repeated extraction; 28,840-file effective-v2 view. DLC entitlement unverified; trophy key absent. |
| P1 | Clinic movement and save/quit/reload demonstrated; investigation continues | Separate instrumented shadPS4 baseline. Hunter's Dream, overhead/cost separation and intermittent audio mutex crash remain open. |
| P2 | Bounded feasibility gate met for P3 | Eleven real roots / 13,584 full-state cases; promoted state, callback/nonlocal, TLS/atomic and real jump-table contracts. |
| P3 | Startup gate remains open; callback/control recovery advanced | 18,444 roots, 21,160 manifest entries across eight modules; 28 independently checked control summaries; 65 new entries; 52 new objects, 12 sparse and 1 disputed entry excluded. |
| P4-P9 | Not started; required runtime/game gates remain | 9,029 indirect-call records, 430 indirect-jump records, 9 fallthrough findings, 170 unknown callback-argument records and native import/callback/exception/control contracts remain open. |

No unwind range, pointer candidate, decoded body or built object is execution coverage. The prior 128 constructor objects and current 52 dependency objects are compilation evidence only. P3 performed no game CPU execution. No emulator, reassembly, interpreter, JIT or original-game CPU fallback replaces the native recompilation deliverable.

Continue with `local/cfg/startup-recovery-v7-repeat/analysis.sqlite` and its `recovery_*` tables, `compilation-manifest.jsonl`, `frontier.jsonl`, and `constructor-order.json`. These four files are byte-identical to v6. The old startup-db-v1 and all prior runs are preserved. Fence findings fell from 146 to 9; new callback dependencies expose additional indirect work.

Details and next experiments: `reports/startup-closure.md`, `reports/startup-closure-evidence.json`, `reports/startup-recovery.md`, the integrated recovery/control-flow evidence, `reports/compiler-spike.md`, `reports/baseline.md` and HANDOFF.md. Twenty-eight focused checks pass. Ghidra checks all 65 new entries and all remaining boundary entries; the continuation evidence audit passes.

User action: none. Ordinary shell calls now work under the updated unrestricted, never-ask permission policy. Do not supply sandbox_permissions or request another restart/read approval. Existing LLVM, Remill, Ghidra, JDK and Tracy work. No PS4 access is requested.
