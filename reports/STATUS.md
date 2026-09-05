# Native recompilation execution status

Updated 2026-09-05 18:02 UTC. PLAN.md execution is authorized. No native game boot, native vertical slice, or playable port exists.

| Phase | State | Evidence |
| --- | --- | --- |
| P0 | Passed with optional-data limits | Exact CUSA03173 01.09; repeated PFS/system metadata extraction; 28,840-file effective-v2 view. DLC entitlement unverified; trophy key absent. |
| P1 | Clinic baseline and local save/quit/reload demonstrated; profiling investigation continues | Separate instrumented shadPS4 runs create TestHunter, move in clinic, quit through the game menu, and reload the moved position. Windows save-file sharing failure isolated and corrected in a separate patch. |
| P2 | Bounded feasibility gate met for proceeding to P3 | Eleven real roots / 13,584 full-state cases. Five-way real jump table and RIP-relative data; 512 callback/nonlocal cases; four-thread TLS/XADD plus publication-order fixtures. State promotion removes representative loop slowdown. |
| P3 | Started; recovery gate open | 1,463-range recursive survey; 225 exception regions independently checked. Startup has 18,444 constructor roots (16,069 unindexed); current frontier stops at 18,437 undecoded entries. |
| P4-P9 | Not started; runtime/game gates remain | Recoverable faults, all startup targets, services, native gameplay, and whole-game improvement remain unproven. |

P2 is a compiler feasibility result under explicit valid-memory and synchronous-boundary contracts. It does not establish that every instruction, recovered function, exception path, or service works. The 1,000-object scale survey still has 842 unresolved execution boundaries. Ordinary memory lowering is forbidden for atomics/MMIO/untrusted mappings. No reassembly, emulator, interpreter, JIT, or original-game CPU fallback is adopted as the deliverable.

Latest evidence: reports/compiler-spike.md, reports/baseline.md, reports/decisions/0002-promoted-state-and-control-boundaries.md, reports/restart-evidence.json, reports/control-flow.md and reports/control-flow-evidence.json. Older results remain under local/runs and reports/archive. HANDOFF.md carries commands and continuation details.

Next work: recover the ordered startup constructor roots and expand missing bodies/exception/service closure from local/cfg/startup-db-v1; independently extend baseline route toward Hunter's Dream, measure profiler overhead and separate CPU/GPU/queue costs. Keep the diagnosed audio mutex crash open until independently isolated.

User action: none currently required. The Codex Windows sandbox/desktop helper still fails after restart; approved elevated shell execution works. This is not an approval rejection. LLVM, Remill, Tracy and the native compiler work without WSL. No PS4 access is requested.
