# Bloodborne recompilation continuation

Updated 2026-09-05. The user explicitly authorized PLAN.md execution. Read reports/STATUS.md, reports/input-validation.md, reports/baseline.md and reports/compiler-spike.md before doing more work. The original planning handoff remains in the initial Git commit fce504555023f7141212cefd74420a967f10bd72.

## Current gate decision

P0 is validated, with explicit optional trophy/DLC limitations. P1 has a reproducible original-code shadPS4 baseline reaching offline character creation; gameplay and detailed profiling remain incomplete. P2 has working Remill-generated Windows objects and ten real root contracts / 11,472 cases, but **fails the approximately 2x performance gate after verified memory lowering**. Do not start P3/P4 broad integration or call this a playable/native port.

The list kernel remains 2.02-4.60x slower after lowering; a closed string-hash graph remains 2.10-3.96x slower. Generated assembly shows repeated state/flag/PC stores in loops. The bounded static-reassembly comparison runs near native speed, but it has a narrower result-only contract and is a different approach. It was not adopted as the endpoint. Critical Remill service callbacks, nonlocal transfers, TLS, atomics and real jump-table/global-data contracts are still open.

The next bounded compiler experiment is verified state/flag promotion or another explicit design on the same contracts, including control-transfer boundaries. Preserve all defined effects and compare performance before expanding. The plan's native deliverable remains lifted Windows game code with no original CPU execution/interpreter/JIT fallback. A reassembly or emulator endpoint would need an explicit user decision; do not silently substitute one.

## Inputs and immutable evidence

- Original packages: E:/ROMS/PS4/Bloodborne.pkg and Bloodborne v1.09 patch.pkg. Hashes were computed once and are in reports/input-manifest.json. Do not rehash them routinely or change them.
- Effective executable: CUSA03173 01.09, SHA256 d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9.
- **Use local/game/effective-v2**, with local/game/view-v2-manifest.json: 28,840 files / 31,438,428,662 bytes.
- The old local/game/effective and view-manifest.json remain unchanged for earlier captures (28,810 files). Their initial PFS-plus-SFO view omitted other package system metadata; P1 exposed that defect.
- tools/package_metadata.py extracted named system metadata twice, using the existing PkgTool API. All repeated bytes match. npbind/nptitle/trophy and other system metadata now have update precedence in v2. Manifest: local/game/system-metadata/manifest.json.
- These views use hardlinks. Do not edit effective files in place. Make new copies/overlays for experiments.
- Seven readable bundled modules are inventoried. sce_sys/about/right.sprx is unsupported by the parser and is not a demonstrated needed-module dependency.
- m34/m35/m36 and DLC menu assets are present. No local DLC entitlement/access has been established. Trophies lack a configured ReleaseTrophyKey; this does not block the observed startup route. Do not ask for PS4 access.

## Builds and tools

Host: Windows 11, i7-13700K, 32 GiB RAM, RTX 4090 / driver 610.47 / Vulkan 1.4.341. E: is an HDD. Full details: reports/environment.md.

Existing VS18 Build Tools / MSVC 14.51 / Windows SDK 10.0.26100.0. Project-local LLVM 21.1.8, CMake 4.2.3 and Ninja 1.13.2 are installed and digest-verified. WSL is absent and not required for this working Windows compiler path.

Use .venv/Scripts/python.exe tools/dev.py TOOL ARGS to load the existing vcvars environment and project tools. For shadPS4 builds use --fast-git-metadata before TOOL to avoid a version-only git describe scan of all submodules. Actual pins are separately recorded.

- external/shadPS4: 22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db, all recursive submodules initialized.
- build/shadps4-baseline/shadps4.exe: unmodified Release baseline, SHA256 09b7bdc5561efcdeda4f7211baad10e4c880bc1d9f402fadf03b24410dbace57.
- build/shadps4-profile-unmodified: preserved unmodified symbols/Tracy exe and PDB.
- build/shadps4-profile: current research capture/input build. The external source checkout has patches/shadps4-research-capture.patch applied. Do not rebuild the normal baseline from this modified source and call it unmodified.
- external/remill: 56918a8c2554088e93389e97d292f4035286506c with patches/remill-windows-sdk.patch applied.
- build/remill/bin/lift/remill-lift-21.exe; semantics build/remill/lib/Arch/X86/Runtime/amd64_avx.bc.
- Remill dependencies: external/remill-deps, built via build/remill-deps. Exact source/dependency/binary hashes: reports/dependency-lock.json.

The Remill patch covers absent optional SPARC targets, a stale DIA import path, raw byte-file input for Windows command limits, and the verified CMPSS upper-vector fix. Do not expand the old leaf translator as a substitute for a semantic engine.

## Reproduce without overwriting evidence

tools/run_record.py requires a unique --id and records argv/cwd, source hashes, exit, timing and outputs under local/runs. Later runs also store sources.zip. The current source is committed in Git; earlier binaries/IR/logs remain local. The exact failing SIMD harness was recovered and verified against its original recorded SHA256.

Remill's Windows output path can log a rename-over-existing failure while exiting zero. Always use a fresh output folder when lifting. Do not overwrite a prior run because its last attempt failed.

Fresh varied SIMD contracts:

    .\.venv\Scripts\python.exe tools/run_record.py --id UNIQUE-LIFT -- .\.venv\Scripts\python.exe -m tools.varied_remill_lift local/compiler-spike/UNIQUE-SIMD
    .\.venv\Scripts\python.exe tools/run_record.py --id UNIQUE-TEST -- .\.venv\Scripts\python.exe -m tools.remill_varied_test local/compiler-spike/UNIQUE-SIMD

Fresh six additional root contracts/call graphs:

    .\.venv\Scripts\python.exe tools/run_record.py --id UNIQUE-GRAPHS -- .\.venv\Scripts\python.exe -m tools.graph_remill_test local/compiler-spike/UNIQUE-GRAPHS

Existing validated results:
- local/compiler-spike/initial: real 0x3360 loop, 720 cases.
- local/compiler-spike/varied-before-cmpss-fix: preserved 384-case vector-state failure; exact source reconstruction checked.
- local/compiler-spike/varied-cmpss-fixed: 3 x 1,536 passes.
- local/compiler-spike/graphs-return-count: 6 x 1,024 passes, including direct and virtual compiled calls.
- local/compiler-spike/scale-default: 1,000 objects / 286.05 seconds / 254.4 MiB peak process working set; 842 objects contain unresolved execution boundaries. Compilation is not execution coverage.
- local/compiler-spike/performance and hash-performance: original/helper/lowered timing, correctness runs, object identity and assembly.
- local/compiler-spike/reassembly-comparison: explicitly separate bounded alternative.

The performance scripts' build output folders are fixed and refuse overwrite. Before a new experiment, parameterize a new destination or preserve a separately named version; do not remove old evidence. Their --run-only modes also write timing files, so use a new destination for new measurements.

## P1 continuation

Last verified checkpoint: character creation, Enter Name incomplete. This is shown in local/captures/summary/character-creation-shadps4.jpg. The opening cinematic and character model rendered. No clinic route, completed character, gameplay save/reload or performance improvement has been demonstrated.

A repeat using a new empty profile:

    .\.venv\Scripts\python.exe tools/run_record.py --id UNIQUE-CAPTURE -- .\.venv\Scripts\python.exe tools/baseline_capture.py --id UNIQUE-PROFILE --build shadps4-profile --research-capture --game-view local/game/effective-v2 --input-script tools/fixtures/baseline-character-creation.tsv --seconds 135

Use separate backed-up test profiles. The capture tool precreates empty home/1000-1003 directories to avoid the baseline's first-run migration prompt; it does not migrate user saves. It terminates only its launched process at the bound and preserves the post-run profile. Bounded termination is not a crash.

The research patch invokes existing Vulkan screenshot readback every 300 game frames and reads the authored frame/button schedule from research-input.tsv. It changes no game CPU code. Raw PNGs remain preserved; tools/preview_capture.ps1 makes JPEG viewing copies if the app image reader cannot decode them.

Next P1 work: name a test character, reach the clinic, then capture an actual gameplay route and CPU/GPU/queue/file/allocation timings. Tracy is compiled in but no complete profiling session/overhead comparison has been collected. Do not infer a game optimization target from the compiler microbenchmarks or coarse 300-frame intervals.

## Environment issues and user action

Normal sandbox commands and the computer-use Node kernel failed with Windows sandbox/helper setup errors. Approved require_escalated shell calls work. This is not an auto-review rejection, and no user approval question remains pending. Root Git operations may need per-command -c safe.directory=E:/bloodborne PC port because initial Git ownership differs; do not change global safe.directory.

For interactive desktop control, the affected component is Codex's Windows sandbox/computer-use helper. Restart Codex before relying on it; installing LLVM, Remill or WSL will not fix that helper. Renderer readback supplied the current images. Character-name entry could alternatively be covered by an explicitly implemented IME test fixture, with the research build clearly labeled.

Optional trophy extraction needs its configured ReleaseTrophyKey; it is a data dependency, not a missing compiler/tool. No PS4 access is available or requested. No additional installation is required to reproduce the completed CPU experiments.

No native milestone is passed beyond isolated CPU experiments. Keep durable status current, investigate failed gates, and do not call the preserved baseline/reassembly/leaf evidence a playable port.
