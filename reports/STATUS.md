# Native recompilation execution status

Updated 2026-09-05 20:23 UTC. PLAN.md execution is authorized, including routine cost-free actions. No native game boot, native vertical slice, or playable port exists.

| Phase | State | Evidence |
| --- | --- | --- |
| P0 | Passed with optional-data limits | Exact CUSA03173 01.09; independently repeated extraction; 28,840-file effective-v2 view. DLC entitlement unverified; trophy key absent. |
| P1 | Clinic movement and save/quit/reload demonstrated; investigation continues | Separate instrumented shadPS4 baseline. Hunter's Dream, overhead/cost separation and intermittent audio mutex crash remain open. |
| P2 | Bounded feasibility gate met for P3 | Eleven real roots / 13,584 full-state cases; promoted state, callback/nonlocal, TLS/atomic and real jump-table contracts. |
| P3 | All initial constructor bodies recovered; startup gate remains open | 18,444 roots, 21,095 manifest entries across eight modules; reproducible database/manifest/frontier; 128 constructor objects; independent Ghidra boundary and table checks. |
| P4-P9 | Not started; required runtime/game gates remain | 8,980 indirect-call records, 421 indirect-jump records, 146 fallthrough findings and import/callback/exception/control contracts remain open. |

No unwind range, pointer candidate, decoded body or built object is execution coverage. All 128 new objects are compilation evidence only; 25 retain declared CPU boundaries. P3 performed no game CPU execution. No emulator, reassembly, interpreter, JIT or original-game CPU fallback replaces the native recompilation deliverable.

Continue with `local/cfg/startup-recovery-v4/analysis.sqlite` and its `recovery_*` tables, `compilation-manifest.jsonl`, `frontier.jsonl`, and `constructor-order.json`. The old startup-db-v1 and all prior runs are preserved. v4 and v5-repeat are byte-identical for database, manifest and frontier.

Details and next experiments: `reports/startup-recovery.md`, `reports/startup-recovery-evidence.json`, `reports/control-flow.md`, `reports/control-flow-evidence.json`, `reports/compiler-spike.md`, `reports/baseline.md` and HANDOFF.md. Sixteen focused reader/recovery checks and both evidence audits pass.

User action: none. The normal Windows sandbox/Node helpers still fail; approved elevated shell execution works. A reusable Get-Content permission is now present. Do not request another restart or repeatedly ask for authorized reads. Existing LLVM, Remill, Ghidra, JDK and Tracy work. No PS4 access is requested.
