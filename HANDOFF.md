# Bloodborne recompilation continuation

Updated 2026-09-05 20:23 UTC. Execute the authorized PLAN.md autonomously. Read reports/STATUS.md, reports/baseline.md, reports/compiler-spike.md and reports/decisions/0002-promoted-state-and-control-boundaries.md first. No PS4 access exists. No playable native port exists.

## Current result and next work

P0 passed with optional trophy/DLC limits. P1 reaches clinic movement, normal game quit and reload of the moved position in a separately instrumented shadPS4 build. A Windows guest save-file sharing bug was reproduced independently, identified as error 32 in the runtime, and fixed separately. The opening audio-thread mutex crash remains unresolved.

P2's bounded feasibility gate now supports proceeding to P3: eleven real roots / 13,584 full-state cases; real relative jump table/RIP data; callback/nonlocal transfer; TLS/locked XADD/MFENCE fixtures. State promotion reduces representative longer-kernel ratios below 2x; tiny list length 1 remains 2.22x. The 1000-object scale survey still has 842 unresolved execution boundaries and is not execution coverage.

Next: use local/cfg/startup-recovery-v4/analysis.sqlite, specifically its recovery_* tables, plus compilation-manifest.jsonl/frontier.jsonl/constructor-order.json. All 18,444 initial constructor bodies are now decoded, including 16,069 outside all unwind ranges. The database, manifest and frontier reproduce byte-for-byte in startup-recovery-v5-repeat. 21,095 entries / 870,923 instructions are recovered across eight modules. P3 remains open: 8,980 indirect-call records, 421 indirect-jump records, 146 final fallthrough findings and unvalidated import/callback/exception/control boundaries. Read reports/startup-recovery.md and reports/startup-recovery-evidence.json for commands and investigated failures. No P4 game execution is authorized by these incomplete gates.

## Inputs and immutable evidence

- Packages E:/ROMS/PS4/Bloodborne.pkg and Bloodborne v1.09 patch.pkg are read only. Hashes were computed once; do not rehash routinely.
- CUSA03173 01.09 eboot SHA256 d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9.
- Use local/game/effective-v2: 28,840 files / 31,438,428,662 bytes. All views use hardlinks; never modify them in place.
- System metadata was independently extracted twice. Seven readable bundled modules are inventoried. DLC assets exist but entitlement/access is unverified. Trophy ReleaseTrophyKey is absent; no observed clinic startup dependency.
- Earlier evidence remains in local/runs, reports/archive, and Git (initial proof fce5045; pre-restart execution 9973e63).

## Tool/build environment

Windows 11; i7-13700K, 32 GiB RAM, RTX4090/610.47/Vulkan1.4.341; E: is HDD. Existing VS18 Build Tools/MSVC14.51/WindowsSDK10.0.26100.0; workspace LLVM21.1.8/CMake4.2.3/Ninja1.13.2. WSL is not required.

Use .venv/Scripts/python.exe tools/dev.py TOOL ARGS. For shad builds add --fast-git-metadata before TOOL. Quote the complete CMake argument '-DCMAKE_POLICY_VERSION_MINIMUM=3.5' in PowerShell; unquoted dotted values were split incorrectly.

- shadPS4 pin 22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db.
- build/shadps4-baseline is unmodified Release; build/shadps4-profile-unmodified preserves unmodified symbols/Tracy.
- build/shadps4-profile is current research plus guest file-sharing fix. Apply capture, IME, diagnostics, then guest-file-sharing patches in that order. Previous research exe/PDBs are preserved as profile-capture-v1, profile-ime-v1 and profile-diagnostics-v1.
- Remill pin 56918a8c2554088e93389e97d292f4035286506c; patches/remill-windows-sdk.patch includes build fixes, bytes_file and CMPSS correction.
- Lifter build/remill/bin/lift/remill-lift-21.exe; semantics build/remill/lib/Arch/X86/Runtime/amd64_avx.bc.
- State promotion executable build/state-promotion/bb-state-promotion.exe; source native/state_promotion. --control-exits enables explicit nonlocal guards.
- Tracy tools pin 5d542dc09f3d9378d005092a4ad446bd405f819a, v0.11.1/protocol69. Build in build/tracy-capture. Patch builds CSV export and project frame exporter against the statistics-enabled server.

## Reproduction

Always wrap execution with tools/run_record.py --id UNIQUE -- COMMAND. Output directories/profile IDs must be new. Runs preserve argv/cwd, source ZIP/hash, binary IDs, stdout/stderr/exit/timing. Failed outputs remain retained.

Compiler experiments:
- .venv/Scripts/python.exe -m tools.state_promotion_experiment local/compiler-spike/NEW
- Add --measure only after correctness succeeds; timing must run without active builds/games. Existing reference state-promotion-v3.
- .venv/Scripts/python.exe -m tools.control_flow_experiment local/compiler-spike/NEW (reference control-flow-v7).
- .venv/Scripts/python.exe -m tools.thread_boundary_experiment local/compiler-spike/NEW (thread-boundary-v2).
- .venv/Scripts/python.exe -m tools.jump_table_experiment local/compiler-spike/NEW (real-jump-v1).

Baseline:
- Creation: tools/baseline_capture.py --id NEW --seconds 330 --build shadps4-profile --research-capture --input-script tools/fixtures/baseline-clinic.tsv --ime-text TestHunter.
- Movement/exit: --seconds 220 --input-script tools/fixtures/baseline-exit.tsv --axes-script tools/fixtures/baseline-clinic-axes.tsv --seed-profile research-clinic.
- Reload: --seconds 180 --input-script tools/fixtures/baseline-resume-continue.tsv --seed-profile research-clinic-proper-exit.
- Use --log-filter '*:Error Render.Vulkan:Info' for flushed diagnostic input/frame/open logs. No Tracy in timing comparisons until overhead is assessed.
- --tracy-seconds N captures bounded matching Tracy, limited to 10% physical RAM. The long clinic-inclusive trace hit this cap; it is diagnostic only.

Seed profiles are copied/backed up under local/saves/backups. Game saves use CUSA00207/SPRJ0005 even though app ID is CUSA03173; preserve this. Bounded termination at title follows normal in-game exit; bounded termination during play triggers the game's improper-quit warning. Capture-wrapper pass is not a gameplay checkpoint result.

## Limits and user action

Original code pages are NX only in the AOT harnesses, not shadPS4. No interpreter/JIT/original CPU fallback may be added to strict native execution. State promotion assumes no guest alias to State and no asynchronous observation inside a promoted region. Ordinary memory lowering is not an atomic/MMIO/mapping implementation.

Normal Codex sandbox shell calls still fail helper_unknown_error after restart. Approved require_escalated shell calls work. Two desktop Node initialization retries failed with trusted Node process exited unexpectedly. Do not ask for another restart as though it fixed this; no installation/approval request is pending. Use the renderer's existing PNG evidence, not a shell-based desktop automation workaround. Root Git may need per-command safe.directory; do not modify global configuration.

Maintain durable status and investigate failed gates. No PS4, proprietary SDK purchase, emulator endpoint or direct-execution substitution is authorized as a replacement for native recompilation.

P3 checkpoint: 128 evenly spaced constructor samples compile to Windows objects directly from manifest bytes; 25 retain CPU boundary declarations, none were executed. Nine recovery and seven exception-reader checks pass. Ghidra checks 112 windows and both newly recovered libc 13-case tables; all 79/81 instructions in those two routines agree. Abort/exit/__cxa_throw contracts preserve runtime obligations. The rejected pointer-overexpansion v1 and its stopped export remain retained; use v4. Historical source evidence is checked against immutable run ZIPs. The source tree started clean at e47c900 (parent 3f83339); this continuation is committed separately.

User preference: all cost-free actions in the plan are approved. Do not repeatedly ask for read confirmation. Normal shell and Node helpers still report helper_unknown_error; use approved elevated calls. Get-Content has a reusable approval. No paid component or user action is pending.
