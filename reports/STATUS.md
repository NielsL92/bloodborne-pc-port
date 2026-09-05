# Native recompilation execution status

Updated 2026-09-05 14:28 UTC. PLAN.md execution was explicitly authorized by the user.

**No native game boot, native gameplay or playable port. P2 is not passed.**

| Phase | State | Concrete evidence |
| --- | --- | --- |
| P0 | Passed with explicit optional-data limitations | Verified packages, repeated extraction, full PFS plus corrected system-metadata view, CUSA03173 01.09, hardware/tool lock. Latest effective-v2 has 28,840 files. DLC entitlement unverified; trophy decryption key absent. |
| P1 | Reproducible baseline obtained; route/profiling work incomplete | Unmodified optimized baseline plus preserved unmodified symbols/Tracy build. Separate research captures reach offline character creation. No clinic/save/reload route or detailed workload profile. |
| P2 | Failed performance gate; broad expansion stopped | Ten real whole-function/call-graph contracts / 11,472 cases pass. CMPSS semantic bug fixed and retested. 1,000 objects compile, but 842 retain unresolved execution boundaries. After verified memory lowering, two kernels remain about 2.0-4.6x slower. Critical runtime-control fixtures remain unimplemented. |
| P3-P9 | Not started; gated | No broad recovery, service integration or native vertical slice. |

Read reports/input-validation.md, reports/baseline.md and reports/compiler-spike.md for gates, failed attempts and limits. Read HANDOFF.md for exact continuation commands. Source control preserves the initial proof and this execution work. Game-derived materials remain under excluded local/build paths.

Latest input view: local/game/effective-v2; manifest local/game/view-v2-manifest.json. The older local/game/effective and view-manifest.json intentionally remain unchanged for earlier captures. All views are hardlinked and must be treated as read only. Original packages were not modified or repeatedly rehashed.

P2 decision: retain Remill and the harness; do not integrate its current state representation broadly. Demonstrate state/flag promotion or another bounded compiler design on the same correctness and performance contracts first. A static-reassembly comparison runs near original speed but is explicitly a different approach; it is not adopted as the deliverable.

User/tool dependencies:
- LLVM/clang-cl/CMake/Ninja and the Windows Remill path work. WSL is not required.
- Codex's Windows sandbox/computer-use helper failed to initialize. Approved elevated shell calls work, and renderer readback supplied images. Restart Codex before relying on interactive UI control; this is not a missing compiler component.
- Optional trophy extraction lacks a configured ReleaseTrophyKey. It did not block the baseline reaching character creation. No PS4 access is requested.
- No current installation request or approval question is pending.

Next bounded work: address the failed P2 performance representation gate and demonstrate service callbacks/nonlocal flow/TLS/atomics before expansion; independently continue P1 from character creation to a measured clinic route. Do not mistake the shadPS4 images, reassembly comparison or old leaf proof for a native port.

Final consistency audit: reports/execution-audit.json. Both preserved third-party patches pass git apply --reverse --check. All recorded captures and builds are finished; no background work is left running.
