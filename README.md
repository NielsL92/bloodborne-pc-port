# Bloodborne native recompilation research

**Status: a tested CPU recompilation proof, not a playable Bloodborne port.**

Execution of [PLAN.md](PLAN.md) began on 2026-09-05. Read
[reports/STATUS.md](reports/STATUS.md) and [HANDOFF.md](HANDOFF.md) to continue.

- P0 extraction is verified; corrected effective-v2 has 28,840 files.
- Separate shadPS4 baseline/research builds reach offline character creation.
  This is original-code execution in shadPS4, not the native deliverable.
- Ten real Remill whole-function/call-graph contracts pass 11,472 cases.
- P2's performance gate fails: after tested memory lowering, two kernels remain
  about 2.0-4.6x slower. Broad integration is stopped pending a verified mitigation.
  Critical runtime-control requirements remain open.

See [input validation](reports/input-validation.md),
[baseline](reports/baseline.md), [compiler experiment](reports/compiler-spike.md)
and [dependency lock](reports/dependency-lock.json).
No native game boot or playable port is demonstrated. No PS4 access is available.

## Earlier leaf proof (preserved regression experiment)

This project uses the locally supplied CUSA03173 European Bloodborne packages,
including update 1.09. It reads the real executable, inventories its dependencies,
recovers indexed unwind ranges, and statically translates a restricted set of
integer leaf routines into C++. MSVC compiles those translations into a Windows
x64 executable. The verification program compares their RAX results with the
original routines running directly on the CPU.

The earlier leaf build translates **19 routines, totaling 538 original instruction
bytes**, and passes **205,048 differential cases**. A separate set of 28
hand-authored CPU cases passes 302,176 comparisons. There are also 26 Python
tests. These results cover only the stated scalar return-value contract. They
do not show that the game boots, renders, or plays, and they do not measure
overall port completion.

Run the complete verification from this directory in PowerShell:

```powershell
.\tools\verify.ps1
```

The existing Windows compiler and the project Python environment are already
configured. The compiled game-code proof is `build/bb-recomp-proof.exe`. Running
it prints a JSON verification result. It is a console test, not a game launcher.

The inputs and output directories are:

| Location | Contents |
| --- | --- |
| `tools/formats.py` | Bounded PKG/SFO and decrypted SELF/ELF readers; import and unwind parsing |
| `tools/analyze.py` | Version, hash, relocation, import and bundled-library inventory |
| `tools/recompile.py` | Conservative instruction-to-C++ translator |
| `native/verify.cpp` | Native CPU oracle and differential test driver |
| `local/update/uroot/eboot.bin` | Executable extracted from the supplied 1.09 package |
| `local/base-code/uroot/sce_module` | Seven executable libraries extracted from the supplied base package |
| `local/analysis/inventory.json` | Executable details and dependency evidence |
| `local/analysis/imports.csv` | All 701 imports with resolved names and potential providers |
| `local/analysis/functions.json` | 162,959 indexed unwind ranges |
| `local/analysis/eboot.elf` | Analysis ELF reconstructed from the readable SELF segments |
| `local/recompiled/functions.inc` | Generated C++ and original bytes used by the oracle |
| `local/recompiled/verification.json` | Result of the game-code verification |
| `reports/feasibility.md` | Findings, architecture choices and remaining work |

The ELF reconstruction retains all inspected execution, dynamic-linking, TLS,
and unwind data. Its unavailable `SCE_LIBVERSION` metadata is explicitly
reported and zero-filled. It is an analysis artifact, not a byte-exact recovery
of the original pre-SELF ELF.

The translator accepts only supported straight-line integer code with six
System V integer inputs and RAX as the output. It rejects memory accesses,
stack use, calls, branches, flag consumers, floating point, SIMD, TLS and
unspecified incoming registers. It does not discover or compile a whole program,
and these functions have not been integrated back into a running game. The
original instruction bytes are used only by the test oracle; the translated
functions execute as statically compiled C++.

For a fresh environment, install Python 3.10 or newer and Visual Studio C++
Build Tools with a Windows SDK, then create the local environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The analysis requires the shadPS4 source at `external/shadPS4`; exact inspected
upstream revisions are recorded in `THIRD_PARTY.md`. The build script locates
the compiler installed on this machine and a standard VS 2022 Build Tools path.
Other installations can run it from an x64 Developer Command Prompt.

The input extraction is already done. To extract executable files from another
local package into an **empty** directory, place the official PkgTool release's
`LibOrbisPkg.dll` under `external/bin/PkgTool` and run:

```powershell
.\tools\prepare-input.ps1 -Package 'E:\ROMS\PS4\Bloodborne.pkg' -OutputDirectory 'E:\bloodborne PC port\local\fresh-base'
```

This selective extractor reads packages through a read-only mapping. It extracts
the executable and PRX/SPRX modules and checks that their paths remain inside
the output directory. The full base game's assets have not been extracted.

Game files, generated game-derived translations, binaries, the Python
environment and upstream checkouts are excluded by `.gitignore`. No game or
firmware files are downloaded. The project's original Python/C++ tooling is
GPL-2.0-or-later; the small C# extraction wrapper is MIT. Upstream components
retain their own licenses. See `THIRD_PARTY.md`.
