# Source and dependency provenance

The inspected shadPS4 checkout is commit
`22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db` from
[shadps4-emu/shadPS4](https://github.com/shadps4-emu/shadPS4/tree/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db).
It remains under `external/shadPS4`, with its license notices. The SELF/ELF
structures, dynamic tags, NID naming, module conventions and unwind format were
studied in `src/core/loader/elf.h`, `elf.cpp`, `dwarf.cpp`, `src/core/module.cpp`
and `src/core/aerolib`. These reference files identify GPL-2.0-or-later terms;
the DWARF implementation also credits the Free Software Foundation. Our Python
format implementation is original code informed by those interfaces. The
Python/C++ tools in this project are provided under GPL-2.0-or-later. The
shadPS4 runtime itself is not compiled or linked into the proof executable.

LibOrbisPkg source is commit
`643477263b2644e0803e0f58b8726ea4e3f3b7d4` from
[maxton/LibOrbisPkg](https://github.com/maxton/LibOrbisPkg/tree/643477263b2644e0803e0f58b8726ea4e3f3b7d4),
under LGPL-3.0. Its `PKG/Entry.cs`, `PKG/PkgReader.cs` and `PFS/PfsReader.cs`
document the metadata and extraction interfaces used here. The downloaded binary
is the separate official PkgTool **0.2.231** release, not a build of the inspected
HEAD commit:
[PkgTool v0.2 release](https://github.com/maxton/LibOrbisPkg/releases/tag/v0.2).
The zip SHA-256 is
`c639e591e35c2431f68410d1771541d95f7308863638f9e3a6eedf1818530097`.
It resides under `external/bin`, together with the upstream DLL and license.
`ExtractCode.cs` is an independently written MIT wrapper that dynamically uses
that DLL. It does not include the library's cryptographic implementation.

Capstone **5.0.6** is installed into `.venv` from its Windows wheel on PyPI.
[Capstone](https://github.com/capstone-engine/capstone) supplies the instruction
decoder and retains its BSD-style license and component notices. The dependency
is version-pinned in `requirements.txt`.

[re:Blue](https://github.com/zolaware/reblue) and
[ReXGlue](https://github.com/rexglue/rexglue-sdk) were researched as architectural
comparisons. No code was copied from them. Their PowerPC/Xbox 360 infrastructure
is not used by this PS4 x86-64 proof.

All original Bloodborne code used by the experiment comes from the two packages
supplied in `E:\ROMS\PS4`. Their metadata and the extracted executable's SHA-256
are recorded in the local analysis report. Those materials and generated
translations remain in ignored local directories and are not relicensed by
this project's tooling license.

## P0/P1/P2 execution dependencies

The pinned shadPS4 source and all recursive submodules were built into separate
normal Release and RelWithDebInfo/Tracy executables. The normal baseline remains
unmodified; research-only frame capture/controller schedules are preserved in
patches/shadps4-research-capture.patch and used only in the research build.
Neither executable is the native recompilation deliverable.

Remill is pinned at 56918a8c2554088e93389e97d292f4035286506c under
external/remill, with its upstream license retained. The Windows SDK/build,
byte-file CLI and CMPSS corrections are in patches/remill-windows-sdk.patch.
[Remill source](https://github.com/lifting-bits/remill/tree/56918a8c2554088e93389e97d292f4035286506c).

Official LLVM 21.1.8, CMake 4.2.3 and Ninja 1.13.2 archives were verified against
their release digests. Their original notices remain with the tools. Native
Remill dependency builds include gflags, glog, googletest, XED and mbuild; exact
source commits are in reports/dependency-lock.json. Remill's build also fetches
its pinned Ghidra/Sleigh sources. This does not constitute a completed Ghidra
headless game analysis.

All game-derived bytes, lifted IR, native objects, disassembly, screenshots,
profiles and saves remain in excluded local/build directories. Authored harness
sources and compiler-adapter tooling are tracked separately.
