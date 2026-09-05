# Bloodborne native port assessment — 2026-09-05

**A complete native PC recompilation is not delivered.** The result is a
working, narrowly scoped static CPU recompilation experiment and a reproducible
inventory of the user's game. No title screen or gameplay has been reached by
this project. There is no technical evidence here supporting a claim that a
complete port is nearly finished or can be produced by a single automatic
conversion.

The supplied packages both identify **CUSA03173**, content ID
`EP9000-CUSA03173_00-BLOODBORNE0000EU`. Their SFO application versions are
`01.00` and `01.09`. The patch executable's SHA-256 is
`d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9`.
Its decrypted SELF program data is readable. Seven PRX libraries from the base
package are also readable, including `libc.prx` and `libSceFios2.prx`.

| Measured property of patch 1.09 | Result |
| --- | ---: |
| Executable container size | 93,825,704 bytes |
| Architecture | x86-64, little endian |
| ELF type | `0xfe10`, SCE dynamic executable |
| Entry relative virtual address | `0xa0` |
| Imported symbols | 701 |
| Distinct imported library interfaces | 39 |
| Declared module filenames | 42 |
| Relocation entries | 235,000 |
| Indexed unwind ranges | 162,959 |
| Imports with a textual shadPS4 registration match | 465 |
| Imports with a matching bundled-library export candidate | 233 |
| Imports with neither match | 3 |

The three imports without candidates in this lookup are
`sceNpNotifyPlusFeature`, `sceKernelTruncate` and
`sceKernelReleaseFlexibleMemory`. This is **not** a list of the only missing
features. Matching an import to a source registration or an export does not
prove ABI, module-version or behavioral compatibility. Registration bodies can
be stubs; bundled modules have their own imports; libraries can be requested
later. Dynamic loading and all execution paths remain untested.

The unwind index supplies useful function boundaries for analysis, but it may
omit code and need not map one-to-one to source-level functions. The executable
load segment also contains data. Neither its size nor the number of unwind
entries should be treated as an exact count of gameplay code.

The central architectural difference from the example is the CPU instruction
set. re:Blue uses static translation plus an Xbox 360 runtime; its build links
ReXGlue and a shader recompiler. Those are console-specific dependencies, not
a ready-made PS4 conversion tool.
[re:Blue build](https://github.com/zolaware/reblue/blob/main/CMakeLists.txt),
[ReXGlue project](https://github.com/rexglue/rexglue-sdk).

On x86-64, shadPS4 loads the PS4 executable and jumps into its machine code. A
CPU static recompiler is therefore not required merely to execute PS4 arithmetic
on an x64 PC. Windows still differs in calling convention, loader behavior,
thread-local storage, virtual memory, exceptions and available services.
[shadPS4 entry and linker](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/core/linker.cpp).

The GPU is a separate problem: PS4 command streams, resource layouts and shader
instructions need a working graphics backend. shadPS4 already has substantial
code for that work. Reusing and adapting it is a credible engineering route;
translating CPU instructions does not make that work disappear.
[shadPS4 GPU command processing](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/video_core/amdgpu/liverpool.cpp),
[shader compiler](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/shader_recompiler/recompiler.cpp).

The implemented pipeline reads package metadata, maps the decrypted SELF
segments, parses dynamic imports and relocations, resolves NID names from the
open-source reference and recovers the unwind index. It translates **19 small
register-only leaf routines, 538 original bytes in total**, into C++ expressions.
MSVC builds a Windows x64 executable from those translations.

Each routine is compared against the original bytes executed on the CPU with a
small Windows-to-System-V argument bridge. The game-code run passes **205,048
cases**, using boundary values, per-argument bit patterns and seeded random
inputs. The contract checks six incoming integer argument registers and the
RAX result. It does not establish every observable machine-state effect or a
drop-in binary patch. The routines' source-level names and gameplay roles have
not been identified.

A separate test corpus of **28 hand-authored synthetic routines** passes
**302,176 cases**, exercising arithmetic width, aliasing, sign extension, shift
masking, rotations and byte swaps. **26 Python tests** check malformed inputs
and rejection of instructions outside the supported subset. These are CPU and
tooling tests, not compatibility or game-performance measurements.

The project deliberately refuses unsupported instructions instead of generating
successful no-op replacements. It cannot yet translate the executable entry
path, memory accesses, calls, branches, indirect control flow, floating point,
SIMD, TLS accesses or exception handling. No translated routines have been
connected to a game runtime.

The following milestones are needed for a credible native recompilation:

| Milestone | Concrete acceptance evidence | Present state |
| --- | --- | --- |
| Exact input and executable analysis | Versioned inputs, readable executable, import and relocation inventory | Implemented |
| Restricted scalar static translation | Native compiler output agrees with original code on tests | Implemented for 19 ranges |
| Whole-program CPU execution | Correct entry, calls, returns, indirect targets, memory, SIMD, TLS and exceptions across the loaded modules | Unimplemented |
| PS4 runtime integration | Correct allocation, threads, synchronization, file access, library loading, input, audio and save behavior | Unimplemented |
| Graphics backend | Correct shader translation, resource handling, command processing and presentation | Unimplemented |
| First game frame | Boot through initialization to a recognizable title screen | Unverified |
| Playable local build | Create/load a character, render gameplay, handle input, audio, save and reload | Unverified |
| Release-quality port | Broad main-game/DLC coverage, stable saves and representative hardware testing | Unverified |

Planning clarification: use a pinned shadPS4 runtime as an implementation
reference, observation source, and potential source of reusable PS4 services
and GPU code. Agreement with it is not proof of correctness. No PS4 hardware
will be available. The detailed proposed approach and independent validation
strategy are in [PLAN.md](../PLAN.md). The next
substantial implementation milestone for the requested recompilation is a
whole-program execution path connected to those services. A single-game runtime
that directly loads the x64 game binary could reach playability sooner, but
that would be a different deliverable from a full static recompilation and must
be labeled accordingly.

There is no demonstrated missing-input blocker for the work completed so far.
The remaining obstacle is the amount and complexity of unimplemented software
and validation. This session establishes a real starting point; it does not
support a promise of a finished native port or a reliable completion date.
