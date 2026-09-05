# Start here: Bloodborne recompilation continuation

Prepared 2026-09-05. This file is a handoff, not an instruction to start implementation during the planning task. The user asked for a plan first and will launch a new task when ready.

## Suggested user prompt for the new task

> Execute the plan in E:/bloodborne PC port/PLAN.md. Read HANDOFF.md and the existing evidence first. Begin with P0, then the baseline investigation and whole-function compiler experiment in P1/P2. Work through the approved scope autonomously, preserving reproducible results and continuing when gates pass. Report failed gates with concrete evidence and investigate them; do not silently substitute an emulator fork or direct-execution build for native recompilation. There is no PS4 access: use the supplied files and the independent checks in the plan. I am willing to install necessary tools. Tell me exactly which component requires my action when that occurs. Do not claim a playable port based on the existing leaf tests. Keep a durable status record for continuation.

## Fixed intent and constraints

- Target a native Windows x64 recompilation of the supplied Bloodborne CUSA03173 v1.09, with locally imported assets and an offline gameplay target. The user's example is re:Blue; an emulator launcher alone does not satisfy the request.
- The user is concerned with shadPS4's flaws. Treat it as a reusable implementation and observation source, not a correctness oracle. Measure improvements separately from proving native CPU execution.
- **No PS4 hardware will be available.** Do not plan a console dumping/capture phase or repeatedly ask for access.
- Preserve E:/ROMS/PS4 inputs. Work in E:/bloodborne PC port. Keep game-derived code, assets, traces, generated translations, saves, and binaries local and excluded from source control.
- Strict native milestones prohibit executing the original game's CPU bytes, including original bundled-module code. Instrumented and hybrid development builds must be labeled and separate.
- The planning task added documentation only. It did not install tools, compile code, run tests, launch the game, initialize project Git, or start a new task.

## Read first

1. [PLAN.md](<E:/bloodborne PC port/PLAN.md>) — scope, architecture, phases, acceptance gates, uncertainty, tools, and review allowances.
2. [README.md](<E:/bloodborne PC port/README.md>) and [reports/feasibility.md](<E:/bloodborne PC port/reports/feasibility.md>) — previous implemented proof and its limitations.
3. [reports/validation.json](<E:/bloodborne PC port/reports/validation.json>) and [local/analysis/inventory.json](<E:/bloodborne PC port/local/analysis/inventory.json>) — recorded measurements, not current verification.
4. [THIRD_PARTY.md](<E:/bloodborne PC port/THIRD_PARTY.md>) — dependency revisions and provenance.

## Exact supplied inputs and important hashes

| Item | Value |
| --- | --- |
| Base | E:/ROMS/PS4/Bloodborne.pkg; 31,351,111,680 bytes; SFO version 01.00. |
| Update | E:/ROMS/PS4/Bloodborne v1.09 patch.pkg; 181,338,112 bytes; SFO version 01.09. |
| Content ID | EP9000-CUSA03173_00-BLOODBORNE0000EU |
| Extracted update eboot.bin | E:/bloodborne PC port/local/update/uroot/eboot.bin |
| Update executable SHA-256 | d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9 |
| shadPS4 checkout | E:/bloodborne PC port/external/shadPS4 at 22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db. Submodules are not initialized. |
| LibOrbisPkg source | E:/bloodborne PC port/external/LibOrbisPkg at 643477263b2644e0803e0f58b8726ea4e3f3b7d4. |
| Extraction binary | Official PkgTool 0.2.231 under external/bin/PkgTool; separate from the source checkout. |
| PkgTool release ZIP SHA-256 | c639e591e35c2431f68410d1771541d95f7308863638f9e3a6eedf1818530097 |

Full base assets are not yet extracted. Base code and seven libraries are under local/base-code/uroot. The small update was extracted under local/update. Verify DLC contents and actual module requirements rather than assuming them.

## Existing code worth preserving

| File | Role and limit |
| --- | --- |
| tools/formats.py | Bounded PKG/SFO/SELF/ELF reader, dynamic metadata, imports/exports, relocations and unwind index. |
| tools/analyze.py | Input inventory; named NIDs; static registration and bundled-export candidates. Matches are not semantic compatibility. |
| tools/ExtractCode.cs and tools/prepare-input.ps1 | Selective code extraction using LibOrbisPkg. Read-only package mapping, confined output paths, empty output directory required. Do not assume this extracts full base assets. |
| tools/recompile.py | Restricted straight-line integer leaf translator. No memory/stack, branches/calls, flags consumers, SIMD, TLS, or exceptions. |
| native/verify.cpp | Original-instruction versus generated-C++ harness for that restricted subset. Six incoming SysV integer argument registers, RAX result only. |
| tools/recompiler_selftest.py | Authored scalar regression corpus. |
| tools/verify.ps1 and tools/build-proof.cmd | Existing end-to-end proof verification/build entry points. |

The prior checks recorded 26 passing Python tests, 19 game routines / 205,048 comparisons, and 28 synthetic routines / 302,176 comparisons. Only 538 original game bytes are translated. The game has never booted in this project. build/bb-recomp-proof.exe is a console test, not a launcher; its recorded SHA-256 is cbfbb221862976f81925375dd46bbd9c0197a51d0d4ea083380b9d681da8e453.

The executable has 701 imports, 235,000 relocations, and 162,959 indexed unwind ranges. There are three imports with neither static provider candidate: sceNpNotifyPlusFeature, sceKernelTruncate, and sceKernelReleaseFlexibleMemory. **These are not the only unimplemented features.** Stubs, signatures, module versions, transitive dependencies, and dynamically loaded code all remain relevant.

The reconstructed local/analysis/eboot.elf preserves inspected execution/dynamic/TLS/unwind data but zero-fills unavailable SCE_LIBVERSION metadata. Use the SELF hash as the primary input identity and retain the parser's caveat.

## Host and tool facts

- Windows / PowerShell. Git is available. System Python is C:/Python314; the project has a working .venv with Capstone 5.0.6.
- MSVC is installed at C:/Program Files (x86)/Microsoft Visual Studio/18/BuildTools/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x64/cl.exe. The build wrapper uses the corresponding vcvars64 environment. Windows SDK components exist; inventory the exact versions.
- The Framework64 v4.0.30319 C# compiler worked for the extraction wrapper when called with absolute paths.
- During planning, java, cmake, ninja, clang, and clang-cl were not on PATH. This does not prove they are absent everywhere. Check before installing.
- wsl.exe exists; distribution availability is unverified. Remill's Windows support is documented as experimental. Prove Windows-target code generation early, even if the compiler front end runs under Linux.
- CPU/GPU/VRAM/RAM are not inventoried. Do not invent performance expectations or advise a hardware purchase before measuring them.
- The project root is not yet a Git repository. Existing external source checkouts have their own Git metadata. No applicable AGENTS.md was found during planning; check current instructions when starting.

## First implementation work items

1. Read the plan and local instructions; inspect for user changes. Create a concise durable status record with the current milestone and exact next action.
2. Perform P0: input/version integrity, full asset view, required-data assessment, host/tool inventory, source control/provenance, and one reproduction of the existing proof.
3. Set up only dependencies needed for P1/P2. Keep compatible toolchain versions isolated; do not install every optional diagnostic tool at once.
4. Build an unmodified pinned shadPS4 baseline and a separate research configuration. Gather the first failure or measured scene with the supplied data. The source has a libc-internal HLE fallback; inspect it before declaring an absent firmware file fatal.
5. Build Remill/LLVM and a Windows AOT object; choose difficult real routines and valid fixtures, then test a closed call graph, service callback, and nonlocal-control-flow prototype. Evaluate speed, code size, and compilation scale.
6. Record whether the proposed architecture passes P2, which independent correctness checks apply, what remains uncertain, and the next measured game improvement to pursue.

Do not start by decompiling every function to guessed C++, extending the leaf opcode list indefinitely, recreating the whole engine, or polishing a launcher. The first important result is evidence that the difficult CPU/runtime boundary works and that the game-improvement strategy addresses measured costs or defects.
