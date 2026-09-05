# Bloodborne native PC recompilation: execution plan

Date: 2026-09-05. Status: proposed plan; implementation is not authorized by this document alone. This planning turn changes documentation only. The user will start a new task to execute the agreed plan.

The user has confirmed that there will be **no PS4 hardware access**. The plan uses the supplied files, the PC, public technical documentation, and open-source implementations. shadPS4 is an implementation reference, a source of reusable components, and a way to gather observations. Agreement with it is not proof of console correctness.

## 1. The deliverable and its boundaries

Build a Windows x64 application for the supplied European Bloodborne build, CUSA03173, update 1.09. Its game CPU code is regenerated ahead of time into native host code. It uses the user's locally imported assets and a game-specific runtime providing the required console services and graphics translation.

The user's example supplies a useful product pattern: re:Blue builds a native application around statically translated game code and the ReXGlue runtime. Its Xbox 360 toolchain is an architectural reference; the PS4 executable needs its own analysis, compilation, and service integration. [re:Blue](https://github.com/zolaware/reblue), [build configuration](https://github.com/zolaware/reblue/blob/main/CMakeLists.txt).

The first playable target is offline gameplay on this PC: create a character, play through the opening, use a controller, hear correct audio, save, quit, and reload. The complete target extends that to a main-game playthrough and broad area, boss, system, and save coverage. Include The Old Hunters if the supplied content and required local entitlement data support it; verify that in P0 rather than assuming it from the title ID. Record missing DLC separately.

Keep two success criteria distinct:

1. **Native recompilation:** all game and required bundled-module CPU paths exercised by the supported game run compiled host code or explicit native service replacements. The final runtime has no original-game CPU execution, CPU interpreter, or CPU JIT fallback. GPU shader compilation and console API compatibility code are permitted.
2. **A better working game:** demonstrate the agreed correctness, stability, and performance improvements against a pinned shadPS4 baseline on the same PC. A port can satisfy the first criterion while failing the second; report that honestly.

Use original timing at 30 fps as the initial correctness target. Make stable 1080p/60 fps an optimization goal, subject to the hardware inventory and measured workload. Higher resolutions, unlocked frame rates, extensive mod support, Linux/ARM targets, and online/PSN features come after the offline Windows target. Keyboard and mouse support follows controller playability. No completion date is defensible yet.

Distinguish milestones in every status report:

| Label | What it proves |
| --- | --- |
| CPU experiment | Selected translated routines pass their stated contracts. |
| Instrumented baseline | The original game runs through a modified shadPS4 research build. |
| Hybrid development build | Some paths are recompiled; original CPU execution still exists. Useful for isolation, never the final deliverable. |
| Native vertical slice | An actual gameplay route passes with original guest code pages non-executable and no CPU fallback. |
| Complete local port | The agreed content and system matrix passes on the recorded PC; wider hardware support is stated separately. |

## 2. What already exists

These are recorded results from the earlier implementation task, inspected during planning. They were not rerun in this planning turn.

| Evidence | Recorded state |
| --- | --- |
| Input packages | E:/ROMS/PS4/Bloodborne.pkg: 31,351,111,680 bytes; E:/ROMS/PS4/Bloodborne v1.09 patch.pkg: 181,338,112 bytes. |
| Patch executable SHA-256 | d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9 |
| Executable analysis | x86-64; entry RVA 0xa0; 701 imports; 235,000 relocations; 162,959 indexed unwind ranges. |
| Imported interfaces | 465 textual shadPS4 registration matches and 233 bundled-export candidates; three without candidates. These counts do not establish correct implementations. |
| Bundled code | Seven readable libraries, including libc.prx and libSceFios2.prx. Their transitive requirements remain to be validated. |
| Existing translator | 19 straight-line integer leaf routines; 538 original bytes; 205,048 RAX-result comparisons. |
| Other recorded checks | 28 authored CPU routines / 302,176 comparisons; 26 Python tests. |
| Game/runtime status | No game boot or frame from this project. shadPS4 source is present but has not been built here. Full base assets have not been extracted. |

An unwind range is not necessarily one complete function, and executable segments also contain data. Neither the import match count nor the leaf test count is a percentage of port completion. The reconstructed analysis ELF has explicitly zero-filled, unavailable SCE_LIBVERSION metadata; do not treat it as a byte-exact original ELF.

Keep the existing parser, inventories, extraction wrapper, and leaf tests. Treat the small translator as a regression experiment. Do not grow it instruction by instruction into a new general x86 implementation without first evaluating an existing semantic engine.

Local evidence: [README](<E:/bloodborne PC port/README.md>), [assessment](<E:/bloodborne PC port/reports/feasibility.md>), [validation record](<E:/bloodborne PC port/reports/validation.json>), [input inventory](<E:/bloodborne PC port/local/analysis/inventory.json>), [dependency provenance](<E:/bloodborne PC port/THIRD_PARTY.md>).

## 3. Architecture to test first

The proposed pipeline is:

    Supplied packages, read only
        -> verified executable/modules + base/update asset view
        -> control-flow and dependency database
        -> instruction lifting -> LLVM optimization -> native Windows objects
        -> game executable + native service adapters
        -> adapted graphics/audio/input/file runtime -> Windows/Vulkan

Alongside it, keep a separate instrumented shadPS4 build for profiling, capturing inputs to isolated functions, and locating integration differences. Keep an unmodified baseline as well. Fixes and instrumentation must not silently change the baseline used for comparison.

### CPU compilation

Start with **Remill + LLVM**, using Ghidra and the existing Capstone-based tooling to recover and cross-check code boundaries and control flow. Remill translates x86/amd64 instructions to LLVM bitcode; it is a library, not a complete PS4 executable converter. Its consumer must implement memory and control-flow intrinsics. This is a candidate architecture to test, not a claim that the difficult work is already solved. [Remill](https://github.com/lifting-bits/remill), [design](https://github.com/lifting-bits/remill/blob/master/docs/DESIGN.md).

Initially preserve explicit guest registers, flags, stack, TLS, and memory behavior. Improve native calls and register promotion only where verified contracts allow it. Retain guest addresses as logical identifiers so data pointers, vtables, callbacks, return addresses, and unwind information remain meaningful. Use an explicit mapping from guest code addresses to compiled entries. Original code bytes may remain readable as data, but are non-executable in strict native runs. Audit service-to-game callbacks as carefully as game-to-service calls.

An unknown indirect target produces an address, module hash, caller, and diagnostic state, then fails that run. Recover and compile it for the next build. It must never silently execute the original bytes. Development-only hybrid execution is useful for isolating failures, but is separately built and labeled.

### Runtime and graphics

Reuse selected shadPS4 service and GPU components first, behind interfaces that can be replaced. Reimplementing its entire GPU stack while also building a CPU recompiler would multiply the hardest work. The existing entry code directly jumps into mapped x64 game instructions, so CPU translation is not automatically the source of a speedup. The opportunity must come from measured changes to services, synchronization, memory handling, rendering, or particular game routines. [Pinned entry implementation](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/core/linker.cpp).

Useful initial integration seams in the pinned checkout are core/linker.cpp, core/module.cpp, core/memory.*, core/tls.cpp, core/libraries, video_core/amdgpu/liverpool.cpp, shader_recompiler/recompiler.cpp, and video_core/renderer_vulkan. Their current contracts need inspection during implementation; they are not promised drop-in APIs. Keep GPU submission and resource handling distinct from shader instruction translation. [Command processing](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/video_core/amdgpu/liverpool.cpp), [shader compiler](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/src/shader_recompiler/recompiler.cpp).

### Alternatives if the first compiler route fails

Run one bounded comparison against static x64 rewriting/reassembly if Remill's state representation or control-flow model proves impractical. It can preserve instruction semantics and native performance, but a reassembled original binary is a different result from the requested lifted recompilation. Document that tradeoff and return it to the user before substituting it as the endpoint.

Do not depend on McSema as a maintained turnkey pipeline: its repository is archived. Anvill's main README says its specification generator depends on an unreleased Ghidra plugin; an older Binary Ninja route exists, but that is not an essential dependency for this plan. Use ideas or isolated components only after testing their availability and compatibility. [McSema](https://github.com/lifting-bits/mcsema), [Anvill](https://github.com/lifting-bits/anvill).

## 4. Execution phases and acceptance gates

P0 comes first. P1 and P2 can advance independently after the input/tool inventory; a baseline boot problem does not prevent a CPU experiment. P3 builds on P2. P4 requires the selected compiler and dependency map. Graphics investigation begins in P1 and feeds P5; it need not wait for all CPU work. P6 joins the CPU/runtime and graphics paths. P7 improvements are driven by measurements collected throughout. P8 and P9 establish the complete local deliverable.

### P0 — Reproducible inputs and development environment

**Goal:** make every subsequent result attributable to exact input files, tools, and host hardware.

1. Inspect the existing workspace and preserve the earlier evidence. Establish source control for the project, retaining exclusions for game-derived materials, profiles, caches, binaries, and large third-party checkouts.
2. Hash the two package files once, verify the patch executable hash, inventory all required modules, and extract the full base assets to a new local directory. Reuse verified existing extractions. Mount base plus update as a reproducible view with update precedence; record which source supplies each overwritten file. Do not alter the packages in E:/ROMS/PS4.
3. Check the supplied edition's DLC assets and local entitlement dependencies. Determine whether any startup dependency needs a proprietary module absent from the supplied files. Prefer available open implementations; record a concrete missing-input blocker if no working replacement exists. Do not assume that a declared firmware filename means the file is required, or that a stub is an implementation.
4. Inventory CPU features, GPU/driver/Vulkan capabilities, VRAM, RAM, OS, and free disk. Record actual tools and versions. Pin a compatible compiler/LLVM/dependency set for each component.
5. Reproduce the existing proof once, then preserve its results as a baseline. Set up separate local test profiles and save backups before launching a game.

**Tools:** existing Python/Capstone/parser and LibOrbisPkg wrapper; Git; MSVC/Windows SDK; PowerShell; Vulkan capability tools when available.

**Outputs:** proposed reports/environment.md, reports/input-manifest.json, dependency lock records, and local/game base/update material. These names describe future outputs; they do not exist merely because this plan lists them.

**Gate:** repeatable extraction and proof validation, exact effective build identified, hardware recorded, and a written account of any missing required data. Lack of PS4 access is a fixed constraint, not an item to ask the user to resolve later.

### P1 — Measure the actual failures and performance costs

**Goal:** identify what needs improvement on this machine before choosing optimizations.

Build the pinned shadPS4 revision in a normal optimized configuration and a profiling configuration with symbols. Its submodules are not currently initialized. Compare a newer upstream revision only in a separate checkout if it contains relevant fixes; record the exact choice and settings. Use supported offline behavior and the supplied files. Inspect the existing libc-internal HLE fallback before declaring missing firmware fatal.

Reach the farthest reproducible point available: boot, title, character creation, the clinic, Hunter's Dream, then an early Central Yharnam route. Use runtime input injection and scripted checkpoints as those become available; save screenshots, logs, and frame timing automatically. If boot fails, capture a minimal failure and continue independent CPU work.

Measure CPU work, GPU work, queue waits, pipeline compilation, resource uploads, file reads, allocations, memory growth, and crashes separately. Prefer sampling plus targeted event instrumentation over tracing every instruction of the whole game. Measure profiler overhead by comparing instrumented and normal builds.

**Tools:** shadPS4 debug facilities and Tracy integration, PresentMon console CSV capture, Windows tracing/WinDbg where needed, RenderDoc for selected frames. Tracy exposes CPU/GPU and synchronization information; PresentMon exposes presentation timing but documents limitations for some Vulkan and scheduling metrics. Cross-check with internal timers rather than treating every reported number as exact. [Tracy](https://github.com/wolfpld/tracy), [PresentMon](https://github.com/GameTechDev/PresentMon).

**Outputs:** reports/baseline.md, local/captures, scene/profile/config manifests, and a ranked issue list. Every issue includes reproduction steps, evidence, suspected layer, confidence, and the next distinguishing experiment.

**Gate:** a reproducible baseline or a reproducible startup blocker; a measured first optimization target where gameplay is available. “The emulator is slow” is not sufficient evidence to pick a subsystem.

### P2 — Whole-function compiler feasibility experiment

**Goal:** determine whether the CPU architecture can handle real game behavior and scale to this executable.

First build the chosen Remill/LLVM combination and produce a **Windows x64 host object that links and runs**. Remill documents experimental Windows support with clang-cl; start there with a bounded setup effort. If necessary, use a supported Linux environment under WSL for the compiler front end, while keeping the game runtime on Windows. Prove the Windows target and ABI path immediately; producing Linux bitcode alone does not pass. [Remill build requirements](https://github.com/lifting-bits/remill#supported-platforms).

Use a deliberately varied set of at least 10–20 real, nontrivial routines and small closed call graphs. Cover stack and memory accesses, aliases and overlapping buffers, branches and loops, direct and indirect calls, jump tables, SIMD/floating point, global data, and callbacks. Add authored fixtures for TLS, atomics, nonlocal exits, and other critical behaviors not safely isolated from the game yet. Do not fill the set with additional constant-return leaves.

For each isolated fixture, execute original instructions on the host CPU in a controlled subprocess and compare with the AOT result under equivalent input state. Use valid allocated objects and, where available, captured boundary inputs. Isolate service side effects and restore both memory and external state between runs. Compare all architecturally defined observable effects required by the contract: registers/flags, vector state, memory writes, return targets, exceptions, and ordered service calls. Document undefined flags, floating-point rules, CPU-specific behavior, and excluded effects. Arbitrary random pointers are not useful test inputs.

Include signed zero, NaNs, infinities, rounding modes, and MXCSR denormal controls in the floating-point fixtures. Disable permissive floating-point optimizations until an individual transformation is justified. Exercise locked/atomic operations and memory ordering separately from ordinary single-threaded memory tests.

Prototype guest-to-host-to-guest calls and a nonlocal control transfer early. Establish how logical guest stacks and exceptional exits will work before generating a huge amount of code. Compare optimized execution time and inspect generated machine code for state spills and memory-helper overhead.

Scale compilation to a structurally varied batch of roughly 1,000 recovered functions, including difficult functions. Record accepted/rejected cases, compile time, peak RAM, code size, and incremental rebuild cost. This is a scalability experiment, not evidence that 1,000 functions execute correctly or that discovery is complete.

**Tools:** Ghidra headless scripts, Capstone/XED, Remill, LLVM/clang-cl, native differential harness, debugger, disassembly and compiler optimization reports.

**Outputs:** reports/compiler-spike.md, a feature/limitation matrix, minimized failing cases, reproducible native objects, and a documented decision on the compiler route.

**Gate:** the selected real call graphs run without original-code execution; required tested effects agree; callbacks and nonlocal flow have a credible demonstrated implementation; scaling fits the actual host. A persistent slowdown above roughly 2x in representative optimized kernels is a red flag requiring a demonstrated mitigation before broad integration. Kernel ratios do not substitute for later whole-game measurements.

If the route fails, isolate whether the problem is instruction semantics, CFG recovery, ABI, memory lowering, or build tooling. Try one concrete alternative for the failed layer. If neither route is credible, stop expansion and present the evidence; do not spend weeks adding easy opcode coverage.

### P3 — Recover the executable and module control-flow database

**Goal:** give the compiler a reproducible, queryable model of the code it must translate.

Combine executable metadata, relocations, imports/exports, unwind entries, recursive disassembly, jump-table analysis, vtables/RTTI, initializer arrays, and observed call targets. Import recovered names and annotations into Ghidra; use decompiler output for understanding, not as automatically correct compilable source. Automate with headless analysis so another task can resume. [Ghidra](https://github.com/NationalSecurityAgency/ghidra).

Identify each code location by input/module hash plus RVA. Record evidence and confidence for boundaries and edges. Detect overlapping decodes and code/data ambiguity rather than flattening the executable segment into instructions. Include required bundled libraries and dynamically requested modules; transitive dependencies matter as much as the 701 main-executable imports.

Build queries such as “unknown targets reachable from startup,” “callbacks passed to this service,” “writes into code pages,” and “hot routines calling this allocator.” Compare base and patch code only when it helps explain a specific ambiguous routine or compiler pattern. Library signatures and public source patterns are clues, not permission to substitute a guessed implementation.

Use the game's data as another source of structure. Evaluate SoulsFormats on copied sample archives to index asset paths, maps, parameters, and event data where its readers support this build. Correlate those identifiers with file traces and resource/shader captures so a faulty draw can be tied to an actual game asset or event. This can make scene selection and bug isolation much faster than naming every machine-code function. It does not replace the original game logic or imply complete format support. [SoulsFormats](https://github.com/JKAnderson/SoulsFormats).

**Tools:** Ghidra, Python/SQLite or structured JSON, Capstone/XED cross-checks, targeted traces from P1, existing format readers, and SoulsFormats when useful.

**Outputs:** local/analysis/program database, unresolved-target reports, module dependency graph, instruction-family inventory, and generated compilation manifests.

**Gate:** startup and the next milestone's reachable call graph can be compiled with explicit handling for all discovered exits. Unknown/unvisited coverage remains visible. Trace coverage alone never proves complete static discovery.

### P4 — Native CPU execution and console-service integration

**Goal:** start at the actual game entry point and execute initialization through the compiled program and host services.

Implement in dependency order:

1. Module loading as data, relocations, BSS, initialization order, and a stable guest address model. Prefer preserving addresses where feasible; validate host reservations. If an address translation model is needed, make it consistent across CPU, services, and GPU resources.
2. Guest stacks, TLS, per-thread machine state, direct/indirect calls, returns, and service callback gateways. Support tail calls, variadic calls, structure returns, reentrant callbacks, and all relevant argument classes without guessed signatures.
3. Memory allocation/mapping/protection, file paths and update overlays, error codes, timing, threads, synchronization, and event queues. Respect guest page semantics, alignment, memory ordering, and shared CPU/GPU storage. LLVM/C++ aliasing and data-race rules must not erase observable machine-code behavior.
4. Guest exception/unwind behavior, setjmp/longjmp, and observed stack-switching/fiber behavior. Original DWARF metadata does not automatically unwind newly generated Windows code. Test the chosen logical-stack or reconstructed-unwind design across compiled frames and host boundaries.
5. Input, audio, save services, and graphics submission through the adapted runtime. Classify APIs as implemented, intentionally unavailable in offline mode with a supported result, or blocking. Never use universal success-return stubs to advance boot.

Any bundled library that executes original code must also be recompiled or replaced by a validated native implementation before the strict target passes. Detect game code writes or runtime code generation explicitly; an unhandled path of that kind invalidates the current static coverage claim.

**Tools:** selected compiler, shadPS4 service source, WinDbg, structured boundary traces, ABI fixtures and synchronization tests, host memory diagnostics.

**Outputs:** native runtime prototype, service contract registry, startup trace, symbol/address maps, and crash bundles containing build/input IDs.

**Gate:** repeated startup reaches a real graphics submission or equivalent documented game milestone with original guest code pages non-executable, callback dispatch verified, and no unsupported CPU fallback. A hybrid title screen does not satisfy this gate.

### P5 — Render the game and isolate graphics correctness

**Goal:** obtain a recognizable, correctly constructed title and first gameplay frame, with a way to diagnose defects outside the whole game.

Start with adapted shadPS4 GPU components and Vulkan. Capture both the **original shader/command inputs before translation** and selected Vulkan frames after translation. Include shader bytes, specialization inputs, descriptors, resource contents/layouts, and enough preceding command/state information to reproduce a problem. Reduce failing workloads to a draw or compute-dispatch fixture when possible.

RenderDoc inspects the host graphics API workload. It cannot by itself establish that PS4 commands or shaders were translated correctly. Likewise, Vulkan validation checks API use, not visual fidelity to a PS4. Use each at the layer it can test. [RenderDoc](https://renderdoc.org/docs/introduction.html), [Vulkan validation](https://github.com/KhronosGroup/Vulkan-ValidationLayers).

For suspect shader operations, construct restricted CPU reference kernels or algebraic tests using applicable AMD instruction documentation. Verify the actual PS4 encoding and behavior instead of assuming a newer GPU ISA is identical. Test formats, swizzles/tiling, depth/stencil, resource aliasing, barriers, wave behavior, precision, skinning, and compute/render interactions as implicated by captures. Public AMD documentation is useful but does not describe every PS4-specific detail. [AMD architecture documentation](https://gpuopen.com/amd-gpu-architecture-programming-documentation/).

Store reusable fixtures independently of the main-game loop. Run expensive validation in diagnostic builds; benchmark normal builds. Cache shaders and pipelines with keys that include all relevant input/state/compiler/driver dependencies. A stale cache must not conceal a bug.

**Tools:** Vulkan SDK/validation, SPIR-V tools, RenderDoc and its scripting facilities, original-input capture hooks, restricted reference kernels, a GPU vendor profiler if supported by this PC.

**Outputs:** local graphics fixture corpus, render captures, issue-specific image/buffer comparisons, title/gameplay frame evidence.

**Gate:** native title and first gameplay scene with working presentation, core geometry, lighting/materials, and no unexplained validation failures on the path. List remaining visual errors explicitly; this is not yet full graphics coverage.

### P6 — A native playable vertical slice

**Goal:** turn startup into useful gameplay and establish an automated regression route.

Target the clinic, Hunter's Dream, Central Yharnam exploration/combat, and a first boss encounter. Exercise camera and lock-on, movement and dodging, melee and firearm actions, damage/death, loading transitions, inventory, pickups, NPC interaction, menu use, and audio. Verify progression through normal play as well as targeted diagnostic scenes.

Create a character and a local save. Test saving, exiting, restarting the process, and loading at several checkpoints. Use separate test profiles and copied saves. Validate interrupted-save recovery and backup behavior on disposable profiles. Preserve the game's serialized state where practical; do not assume host file writes alone make the save system compatible.

Build input playback, fixed setup/checkpoint routines, capture triggers, and semantic assertions into the research runtime. Input playback is not automatically deterministic with multiple threads; compare stable game-state observations and event ordering within justified tolerances. Human playtesting is useful for feel, but it must not be the only way to reproduce a regression.

**Tools:** native runtime, input/capture hooks, existing audio backend plus diagnostics, save parser/validator as needed, timed scenario runner.

**Outputs:** a launchable native development build, repeatable opening route, screenshots/video, save round-trip evidence, and a current defect list.

**Gate:** at least one hour of this route without a crash or progression blocker, repeated fresh process launches, successful save/load at multiple checkpoints, and zero original-game CPU execution. These thresholds establish a vertical slice only.

### P7 — Improve the measured bottlenecks and game defects

**Goal:** make the native build materially better for the user's actual complaint.

Take the highest-impact reproducible issue from P1/current profiling, isolate it, change one relevant layer, and rerun its fixture and gameplay route. Candidate changes are selected by evidence:

| Measured cause | Candidate response |
| --- | --- |
| Excessive lifted CPU state traffic | Register promotion, direct-call lowering, inlining across proven boundaries, and measured native replacements for well-understood hot routines. |
| Shader/pipeline stalls | Complete cache keys, background/precompiled variants where valid, and loading-stage warm-up. Keep cold-start cost visible. |
| Command submission or synchronization overhead | Game-specific command fast paths, batching, and precise resource lifetime/barrier handling. |
| Resource uploads or layout conversion | Reuse/alias tracking, fewer copies, or a validated GPU conversion path. |
| File or allocation stalls | Measured read scheduling, caching, and allocator/service changes with matching behavior. |
| A repeatable visual/audio/gameplay defect | Minimal failing case, evidence for the intended behavior, and a targeted fix that survives adjacent scenes. |

Treat generic frame-graph replacement, broad engine rewrites, and replacing unknown physics/middleware as later hypotheses, not starting commitments.

Only after 30 fps behavior is stable, implement or validate a version-specific 60 fps timing change. Audit simulation time, animation, physics, projectiles, invulnerability/event windows, audio, cutscenes, menus, and loading behavior. Faster rendering must not imply a faster game. Keep timing changes independently selectable and attributable to exact binary locations.

**Tools:** Tracy, presentation/host tracing, GPU captures, compiler profiles, targeted regression fixtures, native disassembly.

**Outputs:** measured before/after results, retained fixes, rejected hypotheses with evidence, and an updated performance/correctness matrix.

**Gate:** meet the improvement target fixed from P1 data, with unchanged comparison quality and no material regression in the other benchmark scenes. If the port is native but remains slower or inherits the relevant defects, explicitly mark this goal unmet.

### P8 — Full-game coverage and reliability

**Goal:** uncover problems that the opening cannot exercise and substantiate the claim of a working port.

Maintain separate matrices for progression, rendering, systems, and CPU target coverage. Cover all major main-game areas/bosses and representative optional routes, traversal/loading patterns, cutscenes, character equipment, upgrades/runes, NPC state changes, death/recovery, new characters, NG+, and available DLC. Include representative Chalice Dungeon types and recorded seeds; do not imply exhaustive coverage of every randomized dungeon.

Use isolated diagnostic saves or development warps for rapid rendering coverage, but do not count them as a successful progression test. Complete at least one normal main-game playthrough. A single ending does not prove every optional branch. Track which outcomes are tested, inferred, failing, or unknown.

Run extended sessions, repeated zone transitions, multiple save/load cycles, and recovery tests. Verify that memory/VRAM reaches a stable working range instead of accumulating leaks. Qualify on this PC first. Test other GPU/driver families when equipment is available and list the support matrix honestly; the project does not depend on obtaining a PS4.

**Tools:** scenario runner, target/coverage logs, frame/audio captures, profilers, disposable save fixtures, crash triage tooling.

**Outputs:** compatibility matrix tied to builds, full-playthrough evidence, soak results, unresolved issues and hardware limits.

**Gate:** the agreed local-play scope passes with no known progression or save-corruption blocker, acceptable remaining defects explicitly listed, and performance goals assessed across representative scenes.

### P9 — Repeatable local installation and handoff

**Goal:** make the result usable after the development session ends.

Provide a local import/build path that validates the user's package version, extracts assets, generates the required host code, builds it, and creates a runnable installation. Avoid requiring Ghidra interactively on every rebuild; persist and version the analysis/manifests needed for supported inputs. Preserve profiles and caches correctly across updates. Fail clearly on unsupported executable hashes.

Package the original tooling/runtime source and dependency information separately from private game-derived artifacts. Preserve third-party notices and resolve the actual combined dependency license requirements before any public distribution. No public upload is needed to complete the local project.

**Tools:** CMake/Ninja/build scripts, versioned manifests, local installer/import tooling, dependency/license inventory.

**Outputs:** reproducible release build, user instructions, known-issues/support statement, and an up-to-date continuation record.

**Gate:** reproduce the port in a clean build/output directory from the documented inputs and pinned dependencies, then pass launch, gameplay, and save/reload smoke checks. The old developer checkout must not be a hidden runtime dependency.

## 5. Correctness without PS4 hardware

Every test result must say what it actually establishes.

| Evidence | Useful for | Limitation |
| --- | --- | --- |
| Original isolated x64 code executed on this CPU | Defined instruction effects and controlled whole-function behavior. | Does not reproduce PS4 kernel behavior or every AMD Jaguar-specific/undefined result. |
| Intel/AMD instruction specifications | Designing and checking semantic tests. | Match the relevant architecture; do not invent defined behavior where specifications leave it open. |
| Public API descriptions and independently implemented fixtures | ABI, data formats, service contracts, and constrained operations. | Console-specific undocumented behavior can remain uncertain. |
| shadPS4 traces | Finding code paths, service calls, inputs, and integration divergences. | Can carry the same bug as reused runtime code. |
| Reduced graphics fixtures plus restricted reference calculations | Localizing shader, buffer, layout, and synchronization defects. | Partial coverage; not a complete PS4 GPU oracle. |
| Public original-console gameplay footage | Qualitative scene, animation, effect, audio, and progression checks. | Different camera, patch, compression, timing, and state; unsuitable for exact frame or latency comparisons. |
| Save round trips, invariants, multiple routes, and long sessions | Detecting broken game state, regressions, and leaks. | Passing observations are not proof of every reachable path. |

Use at least two different kinds of evidence for a disputed major bug where possible. Preserve unresolved disagreements rather than selecting the easiest output. Native hardware comparisons and specification checks are particularly valuable because they do not share shadPS4's implementation. [Intel architecture manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html).

## 6. Performance protocol

Freeze a small benchmark set as soon as P1 permits: a quiet scene, a traversal/streaming route, and a combat/effects route, then add a late-game stress scene when reachable. Record exact save/setup/input route, game hash, runtime commit, driver, resolution, effects, timing patch, frame cap, cache state, and build configuration.

Use at least three repeated runs per condition and extend to five or more when variance makes the comparison unclear. Separate cold shader/cache runs from warm runs. Report frame-time distributions including median/p95/p99, stalls above a fixed threshold such as 50 ms, CPU/GPU workload timing, load times, and memory/VRAM. Keep intentional loading screens separate from active-play stalls.

At a 30 fps cap, average FPS can conceal major differences. Use workload timing and missed frame budgets; conduct any uncapped or 60 fps comparison with identical timing modifications in both builds. Do not improve scores by disabling effects or selecting a different resolution. Keep diagnostic capture/validation overhead out of headline performance runs.

Before implementing the first optimization, set a concrete target based on the baseline. A reasonable initial proposal is a 20% improvement in p99 active-play frame time on the problem route or a 50% reduction in repeated >50 ms stalls, plus no meaningful regressions elsewhere. If the complaint is chiefly correctness, specify the visible defect and the scenarios that must pass instead. Choose the metric before seeing the optimized result, publish all benchmark scenes, and distinguish measured gains from noise.

## 7. Tools and installation order

Inventory before installing. Prefer pinned official releases and workspace-local dependencies. No purchases are required by the initial plan.

| When | Tool | Purpose / current knowledge |
| --- | --- | --- |
| Already available | Git, Python 3.14.5, project venv with Capstone 5.0.6, MSVC Build Tools, Windows SDK components, LibOrbisPkg/PkgTool | Existing proof and input analysis. Confirm exact SDK during P0. |
| P0/P1 | CMake, Ninja, LLVM/clang-cl | Reproducible native builds. These commands were not on PATH during planning; they may exist elsewhere. |
| P1/P5 | Vulkan SDK with validation and SPIR-V tools | Capability checks and graphics diagnostics. Use versions compatible with the chosen runtime. |
| P1 | Tracy client matching the runtime integration; PresentMon console | Internal and external performance evidence. |
| P1/P4 | WinDbg; Windows Performance Recorder/Analyzer when needed | Crashes, scheduling, and host runtime behavior. |
| P2/P3 | Official Ghidra release + its required 64-bit JDK | Automated disassembly/analysis. The current official release instructions specify JDK 21; development builds have different requirements. Pin a release and follow its own instructions. [Installation](https://github.com/NationalSecurityAgency/ghidra#install). |
| P2 | Remill plus its compatible LLVM/XED dependencies | Full instruction semantics and host-code generation. Keep its LLVM environment isolated if shadPS4 needs a different version. |
| P3, as useful | SoulsFormats and the compatible .NET build/runtime | Read copied game archives for an asset/event index; verify supported formats against actual samples. |
| Conditional in P2 | WSL/Linux development environment | Compiler-tool fallback if native Windows support blocks progress. wsl.exe exists; a usable distribution is not confirmed. The port itself remains Windows native. |
| P5 | RenderDoc | Capture and automate inspection of host Vulkan work. |
| Only when needed | GPU vendor profiler; GhidraOrbis or another compatible analysis extension; targeted dynamic instrumentation | Add for a demonstrated problem. Extension compatibility must be tested; none is required for the initial ELF analysis. |

The pinned shadPS4 Windows build guide and actual presets/CI should determine its build environment; do not choose unrelated latest dependency versions and assume compatibility. Reuse existing Build Tools instead of installing a second IDE without need. [Pinned Windows guide](https://github.com/shadps4-emu/shadPS4/blob/22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db/documents/building-windows.md).

If an installation needs user interaction, identify the exact component and why. Continue independent work that does not require it. The tool list is a staged plan, not a request to install everything before the next task starts.

## 8. Work cadence, review points, and stop conditions

The first allocation is a **feasibility investigation**, not a promise of gameplay within a fixed number of hours. Suggested review allowances are 4–8 active engineering hours for P0, 8–20 for initial P1 work, and 24–60 for P2 including the first scaling experiment. Builds, large analyses, downloads, tool failures, and investigations can change those numbers. They are budget-review points, not automatic timeouts or completion forecasts.

By the end of that investigation, require three concrete answers: can the supplied files support a useful baseline; can the selected toolchain run difficult real code as Windows AOT code; and where would a material game improvement come from? Re-estimate P3 onward using those results. A complete port remains an open-ended effort that could take many months or fail technically.

Each implementation task should pursue one measurable milestone or bug hypothesis, leave reproducible commands and evidence, and update a compact status record. Record source/input hashes, changes, checks, failures, next action, and any real user dependency. Preserve successful fixtures as regressions. Re-run relevant checks after changes; do not repeatedly rerun unrelated suites as a substitute for progress.

Use reports/STATUS.md for the current milestone and next action, reports/decisions for architectural choices, and local/runs/RUN_ID for private run manifests and artifacts. A run manifest should retain the exact command, tool/build/input IDs, configuration, exit status, and evidence paths. These are proposed conventions for implementation, not files created by this planning task.

At a failed gate, continue diagnosis or useful independent work. Escalate a fundamental architecture failure or missing necessary input with a concrete report and alternatives. Do not silently lower the definition of a native port. Reaching a review allowance requires a status/re-estimate, not pretending the phase succeeded or abandoning it without explanation.

Do not spend the early effort on launcher polish, exhaustive function naming, broad engine recreation, or more easy leaf-test counts. The valuable early outputs are a viable compiler boundary, a repeatable baseline, reduced failing cases, and evidence for the first improvement.

The next task's exact starting context and suggested prompt are in [HANDOFF.md](<E:/bloodborne PC port/HANDOFF.md>).
