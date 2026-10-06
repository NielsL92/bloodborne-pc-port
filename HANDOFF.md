# Project closed — 7 October 2026

The user ended this project and authorized a final commit/push followed by deletion
of C:\Projects\Bloodborne PC port, including nested checkouts and ignored private
files. All prior continuation instructions below are historical and inactive.

The final active-runtime checkpoint is on lud-berthe/Bloodborne-Recompiled,
branch Uptownfrog, commit2b2ebd434f4ec83677decb782c101b9aa48204d8:
https://github.com/lud-berthe/Bloodborne-Recompiled/blob/Uptownfrog/docs/checkpoints/2026-10-07-project-closed.md

The last optimization retained the native renderer and passed518/520 full-suite
checks (two known failing targets), but Game560 never started. No FPS gain or
beyond30FPS result is claimed. A small authored backend patch, policy and tests
are preserved in the final runtime commit. Private dependencies, game inputs,
binaries, saves and experiment archives are not being published and will not
survive local cleanup. Tracked donor Remill/AOT research remains in Git history.

# PAUSED at user request - 2026-09-28

All current checks completed; no game/test/build remains. No commit/push. Latest
fix explicitly retires the inactive RGBA8 menu predecessor blocking native depth
birth. Exact pre-fix repro retained;18focused checks pass including full physical
planes, newer GPU buffer data and refusal of live/shifted/mismatched predecessors.
Game executables still match315 and MUST be rebuilt before post-fix Game316,
which remains unused. Detailed continuation:
[Native depth pause](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-28-native-depth-pause.md).

User now wants ONE X PER SECOND FOR THE FIRST90SECONDS. Private load_minute.py
implements this; no delayed loading. Timing harness currently60..120s must move
past90s before use. No end-to-end gain claimed. Resume only when user asks.

# Game315 stale menu image reproduced; loading cadence updated - 2026-09-28

Game315 failed on first native clear at170.557264s before admission: inactive
RGBA8 tile14 menu view shares Z base/allocation with larger new depth target.
Both processes closed, seed unchanged, exact sources/binaries retained. Next add
an explicit validated publication/retirement transition and regression fixtures.
Matching D32S8 transfers pass prior physical parity and isolated cost checks;
the failed game never reached them. No FPS improvement claim.
User now specifies one X each second for the first90s. Loading helper updated;
use prompt automated loading in future runs, no long menu delay. Continue working.

# Game314 real clinic outputs match original shaders - 2026-09-28

Both actual native depth steps match all 2,592,000 logical output pixels against
authenticated original VS/PS/fetch, using retained game source/prior/constants.
Half output equals quarter input. Zero Vulkan errors. Agent loaded Timmy, captured
and closed the test; seed unchanged. Game314 binaries/sources retained. First
replay setup lacked validation path (no GPU); corrected v2 uses unchanged captures.
Next measure native GPU and transfer costs separately, then end-to-end performance.
Game312 intermittent first-clear profile refusal is still open. Keep working.

# Game313 reaches clinic with native GPU execution - 2026-09-28

Automated first-minute X loading succeeds. User looked around and reports normal
clinic; captures agree. Hundreds of native draws/clears positively complete and
persistent image sets are reused. Game312 first-clear profile refusal did not
reproduce and remains unresolved. Current task adds retained input snapshots
for original-shader parity on actual game data, then separate cost measurement.
Do not infer speedup. Continue autonomously; keep gameplay manual.

# Game312 clear target failure - 2026-09-28

User confirms another loading crash. Clear serial 1 rejects an existing target
profile at 188.353206s, before admission; plain source fix was not reached. Both
processes exited, seed unchanged, exact sources/binaries retained. Add target
refusal diagnostics before altering admission. Agent must mash X through the
first minute of loading on future runs; user keeps gameplay control. Continue.

# Plain native input fixed and GPU-tested; Game312 next — 2026-09-28

plain-source-gpu-v3 passes small/4K/async original-shader parity for the exact
Game311 missing-stencil boundary. The source is a plain R32 view; new bridge
acquires protected current Z and retains its backing, without reading S/HTile.
Three invocations include GPU DMA and raw CPU source writes, full plane parity,
source preservation, auth mutation checks and retirement. All 21 existing native
checks and three coupled-source original cases pass. Failed repro/build/fixture
attempts are retained in the recipient checkpoint. Game312 is prepared; game
pixels/performance remain unproved. X bursts are authorized only to load Timmy,
then manual gameplay. Game310/311 binaries retained. Continue autonomously.

# Game311 identifies plain depth input — 2026-09-28

The source reference image covers Z only, with no S/HTile and no GPU image
writer. Native serial 2 demands its nonexistent stencil plane and fails before
clinic at 25.804700s. User confirms crash; processes exited and seed unchanged.
Recipient checkpoint and private game311 review retain exact evidence. Implement
an owned plain-Z input transition; do not reinterpret absent metadata or treat
clean registry flags as leases. Original shader fixture needs this source case.
User now authorizes X/confirm automation to load Timmy only; gameplay stays manual.
Continue autonomously. Next run 312, verify ledger; Game310 binaries retained.

# Game310 native ownership transition failure — 2026-09-28

User reports a crash before clinic. First native draw serial 2 refused a missing
reference image at 47.004419s, before admission. Both processes exited; seed
unchanged. No game pixel or performance proof. Source receipt game310-sources,
private run native-depth-review.json, and recipient native-depth-execution
checkpoint retain the result. Identify the exact surface/plane, then reproduce
and implement its ownership transition. Existing fixtures always create reference
image producers; no evidence yet identifies the missing owner. Native progress
needs its own reporting budget. Continue autonomously; next unused run is 311
(subject to ledger verification). Preserve prior binaries, builds and launcher.

# Native depth GPU layer and transfers tested; engine replacement incomplete — 2026-09-27

2026-09-28: game-binding-gpu-v1 passes small/4K/async 4K with the independent
original compute clear plus original VS/PS/fetch. Authenticated production clear
and draw callbacks pass 124+594 mutation checks and complete physical-plane parity.
The explicit BB_NATIVE_DEPTH_EXECUTE game binding is implemented; candidate
game-execution-build-v1 passes three focused integration checks. Old candidate
binaries are retained privately. Game310 copied-Timmy preflight is ready for a
manual clinic check on WinSta0/Default. In-game omission/visuals/performance remain
unproved; see recipient checkpoint for exact receipts. Continue autonomously.

Newest: captured-fetch-gpu-v1 passes small/4K/async 4K with original VS/PS/fetch,
constructor-recovered quad and captured fixed state. Authenticated production
draw adapter rejects 594 profile mutations and foreign threads; full physical
Z/S/HTile output, CPU restoration, constant reuse and retirement pass. Captured
state exposed corrected sampler Z-filter and raster-word admission errors;
captured-state-cpu-v1 passes 512 original CPU transactions. Failed/inconclusive
dump/profile attempts are recorded in recipient native-depth-execution checkpoint
and gray-screen index. Next make original compute clear an independent GPU oracle
and connect the authenticated game binding. No game relink/launch; Game310 unused.
Keep working autonomously; no approval or user input is needed for these steps.

Newest connected result: engine-gpu-v2 passes small, 4K and async 4K through
actual compound wrapper -> CPU body -> clear/draw engine adapters -> journal ->
five submissions -> native GPU -> reference return. Both outputs match the
original shaders; ten retained flushes, target-stack restoration and immediate
constant-ring reuse are checked. Engine helper endpoints and geometry are authored.
v1 failed because late HLE bridge creation reset mappings; v2 initializes first.
Next authenticate live shader/header/vertex declaration/geometry state before
game installation. Static native-shader-geometry-v1 investigates that boundary.
No game binary relink/launch; Game310 unused. Keep working autonomously.

Newest result: original-gpu-v3 passes authenticated original VS/PS versus native
full-plane GPU comparisons at 256x128 and 3840x2160, three invocations including
prior depth, clear-to-1 and changed CPU input. Geometry/fetch/state are authored;
this is not full original game pass parity. v1/v2 stopped before GPU work because
coherent fault dispatch requires the isolated debugger runner; v3 corrects the
fixture. No validation errors. Exact sources/receipts and failed logs are private.
Next connect the complete C++ wrapper and engine clear/draw adapters to the real
journal/GPU fixture, then authenticate the real game shader/state boundary.
No game binding, binary relink or launch; Game310 unused. Keep working.

Newest continuation: standalone `draw` now imports/retains current destination
depth and executes LOAD/LEQUAL instead of repeating clear-to-1. destination-load-v1
passes 21 GPU checks; extra-v1 passes large timing, loaded-owner quarantine and
async large/failure with zero validation errors. engine-draw-v2 passes 512 CPU
transactions. engine-bindings-v4 passes all focused CPU/original-body comparisons;
v1/v2/v3 exposed undefined upper stack-argument bits in the fixture, corrected to
the original DWORD width with LLVM evidence. Latest source receipts are saved.
Continue with original GCN shader pixel comparison and engine-to-GPU integration.
The pinned original 40-byte VS and 168-byte PS are already in private/prepared/
clinic-cleanup/programs/<code-sha>-104 or -106/program.gcn; request.json/asset-linkage
record the exact hashes. Preserve them. No game binding/launch; Game310 unused.

Latest results: `surface-source-v1` passes bound-source metadata admission,
276 saved target definitions, 32 saved raw shader descriptors and live mapping/
thread checks. `engine-draw-v1` passes 512 draw CPU transactions (3,728 effects)
against original wrapper/constant lookup/barrier/cleanup bodies; main render-state,
previous resolves, flush and SDK endpoints are authored. Both clear and draw CPU
adapters now exist, but remain disconnected from the actual game binding.
Next fix the GPU semantic gap found by inspection: a standalone LEQUAL draw must
load current target depth rather than repeat the compound reduction's clear-to-1.
Implement an explicit draw operation with a retained ordered destination snapshot,
then connect/test the full engine-to-GPU fixture and original GPU shader parity.
Latest exact source archive: engine-draw-v1-sources.zip/json. No game binary
rebuild/launch; Game310 unused. Continue working until stopped or truly stuck.

Newest clear-adapter result: `engine-clear-v4` verifies
`ExecuteOrbisNativeDepthClear` in 512 comparisons against original clear adapters
and hazard/range routines. It retains allocation writes, prior-work barriers,
cleanup and both flushes, while replacing compute work with a typed native clear.
Temporary physical compute emission caches intentionally remain unchanged; SDK
and queued-job endpoints are authored fixture callbacks. Failed build and missing
private helper attempts v1/v2/v3 are recorded. Exact sources: engine-clear-v4
archive/receipt. Continue with the draw adapter and full original GPU parity.
The active static study native-draw-bindings-v1 targets hidden CPU/resource effects
in main-emitter helpers. No game binding/launch yet; Game310 remains unused.

Newest continuation: `surface-v2` verifies the fixed-profile engine surface decoder
against six sizes, 276 saved Game307 definitions and live mapping/thread checks.
Captured descriptors are requests, not leases. `attachment-return-v1` verifies
the new previous-resolve/unknown-bank transition in 1,024 cases using original
constructor/binder/clear-helper instructions and authored SDK callbacks: no repeated
old resolves, expected reference bindings and pending-clear values. Engine-builder
v4 also rejects invalid operations/counts. Exact source archives are saved before
new builds; latest is `attachment-return-v1-sources.zip/json`. The original cache
constructor is 26d1720; earlier reset candidates were value packing/resolves.
Continue implementing complete clear/draw CPU, hazard and flush adapters. No game
binding enabled, game binary rebuilt, launch or original-pass pixel parity yet.

Latest continuation: `clear-physical-v2.json` passes eighteen GPU/journal/parser
checks. Typed commands are frozen by the actual GNM HLE under its lifetime gate;
the engine builder append preserves growth callbacks and owns request values.
Fixed-profile native HTile clear creates first-use reference targets without
original producer draws. The 4K -> 1080p -> 540p chain, full physical planes,
reference consumers, raw CPU faults, reuse, retirement and failure quarantine
pass, plus three asynchronous clear/birth/failure checks. A new immediate CPU
read found raw Z expansion after HTile-only clear (`clear-physical-v1`); preserving
the physical mirror and materializing earlier writers fixes that mismatch.
`engine-builder-v3` passes five CPU contracts and private original comparisons;
its two earlier fixture build errors remain in the checkpoint. Continue with
complete engine clear/draw bookkeeping and flush adapters. Old attachment cache
pointers cannot simply remain unchanged: they can repeat previous resolves
across native steps. No game binding enabled or full original pixel parity yet.

Previous continuation: `engine-cpu-v2.json` verifies the C++ reduction CPU body and
quad setup against 256 original-body cases, the previous-attachment prefix
against 2,048 cases, and sixteen bound-wrapper configurations using native
clear/draw callbacks. Four CPU contracts pass, including the checked eight-arg
guest bridge. The native GPU callbacks/engine flush adapter are not yet complete;
the actual game still binds the reference reductions. `staged-v2.json` verifies
eleven GPU/parser/lifecycle checks: native steps can be separated by reference
work or submitted completion, with full output checks and persistent target reuse.
`staged-v1` found pool churn between distinct sizes; the correction is tested.
Continue through engine emission, first resource birth and clear semantics.
Do not stop because this implementation slice is finished. The user's instruction
is to keep working until asked to stop or genuinely unable to progress.

Continue the native renderer implementation autonomously on Uptownfrog. Read
recipient docs/checkpoints/2026-09-27-native-depth-execution.md first, then its
links. NativeDepthChain now executes two real Vulkan reductions with persistent
resources, immutable constant versions, bounded ownership, positive retirement
and quarantine after accepted failure. The exact protected reference input
bridge, production output transaction and owned typed command insertion pass
eight GPU/lifecycle/parser checks. The registered frontend exercises reference
producers -> native chain -> reference depth-test consumer, raw CPU read/write
faults, changed input, all depth/stencil/padding/HTile, reuse and retirement at
the recovered 4K -> 1080p -> 540p sizes. A failure after native execution retains
the submitted graph and withholds completion. Async large/failure and two
reference-parser regression checks pass. Evidence and failed attempts: recipient private/perf-lab/
native-depth-execution-20260927. Only build/vulkan-native-pass-v1 was rebuilt.

This is NOT a completed game rendering replacement: e5b2d0 still calls both
original reductions. No original game commands omitted, full original-pass
parity or in-game result established. The typed submission API has a runtime
opt-in, but no game CLI/environment switch. Its bridge accepts existing protected
reference owners; first resource birth and engine clear semantics are incomplete.
The engine must omit the original work and create the typed record. Raw CPU
faults after submitted work are tested; not every concurrent guest-thread race.
Game306 retained/hashes complete transfers but did not export their bytes;
the saved hashes cannot serve as an offline original-pass pixel oracle.

The previous-attachment prefix now has a C++ implementation in recipient
src/execution/orbis_native_depth_engine.cpp. `engine-v1.json` records two passing
contracts and 2,048 differential cases against an authenticated private clone of
the original prefix. All helper arguments/order and authored control-object
storage match, including callback changes to banks/counts/views. Original helper
bodies are callbacks in that fixture; the split is not yet game-enabled. Continue
through main-emitter CPU bookkeeping and clear semantics; do not stop at this slice.

The remaining boundary is CPU emission state and the pending-job protocol:
26d2230 can call26b5a70/26b6810 on previous producers before target binding;
26b9850 updates pending barrier state;26af700 can flush/callback. Preserve those
effects while removing the covered clear/draw emissions. The 15-function static
native-state-v2 and five-function native-transition-v1 studies are in
performance-command-ownership-20260927; LLVM byte/instruction checks pass.
26cbd50 cleanup also emits commands;26d1f80 can emit prior color clears, and
26b09e0 can allocate builder-tail storage/call back while emitting a wait. Do not skip
the complete adapter or silently run the original work alongside the new pass.

No game launched; Game310 remains next, with user-controlled gameplay on the
actual host desktop. Wolf-format repair stays parked. Game277, ordinary/phase3
builds, launcher and original saves were not edited. No commits, pushes,
subagents or FPS claim. Historical instructions below are superseded where they
conflict with the current native implementation priority.

---

# Native Bloodborne pass next; Game309 freeze saved and closed — 2026-09-27

Continue autonomously; caps are guidelines. Next unused game310. User controls gameplay.
The user challenged continued generic-renderer work. The running implementation still
uses PS4/PM4/Vulkan; Bloodborne hooks/snapshots/generation observations replace no GPU work.
Park further wolf texture-format repair. Implement the recovered two-stage native depth
reduction with owned GPU targets, immutable constants, an explicit reference-input/output
bridge, original rendering commands omitted, preserved CPU/completion effects and retirement.
Verify complete outputs and in-game pixels, then native/bridge/end-to-end cost separately.
Read recipient docs/checkpoints/2026-09-27-native-renderer-priority.md and performance-status.md.
No further unchanged observation run substitutes for execution. Escaped CPU aliases remain
unproved; generation observations are not storage retains or writer exclusion.

Game309: user attacked wolf and froze. Raw512×512 R16_UNORM view rejected at88.173624s,
depth=false/no HTILE descriptor; binding role and pending producer are not yet established.
Death/loading not reached. Full23,492,677,219-byte dump saved in recipient private/perf-lab/
performance-command-ownership-20260927/game-309, SHA2561fc36ad3d9bab7ea...; both processes
closed and seed unchanged. Candidate child27ce8cd12dc7f03c... passes28 D16/25 harness checks,
but route still fails. Exact archive/logs in performance-wolf-d16-20260927. No R16 fix made.
Game308 was inaccessible on sandbox desktop and inconclusive; use host executor for manual games.
Computer Use was stopped with physical Escape; do not issue more app input this turn.
Game277, ordinary/phase3 binaries, launcher and original seeds preserved. Uptownfrog only.
No native GPU replacement or FPS gain yet; no commits or pushes.

---

# Game 307 complete; continuing with wolf D16 support — 2026-09-27

User authorization: continue autonomously across useful items and past planning caps.
Game308 is next. Uptownfrog only; private artifacts and original seed rules remain.
Game307 resource-generation-v1 joins414 observations to3 actual allocation births.
All138 sampled commands and276 constants match;9 ordered copies survive publication
and see live, unmapped generations at release.4514 births/213 frees, no tracking loss.
Both clinic captures directly reviewed correct; seed unchanged; no renderer errors.
Eight focused native checks and24 benchmark tests pass. No game remains running.
The exact Game307 source/player archive and analyses are in recipient private
performance-command-ownership-20260927; read progress.json and resource checkpoint.

Observed generations do not retain guest storage or exclude escaped CPU writers.
No native replacement or FPS gain is claimed. Preserve original publication.
Further unchanged clinic observations cannot prove the missing writer contract.
Next selected item: strict512×512 D16/HTILE support for the known wolf-attack freeze,
which blocks the user-driven route needed for future renderer ownership work.
Recover the exact register tuple from Game298 evidence, qualify CPU/GPU layout,
clear/publication and padding tests, then prepare the route for user control.
Game277, ordinary/phase3 builds, launcher and original seeds are preserved.
No commits, pushes, subagents, new Python source overlays or route automation.

---

# Autonomous continuation authorized — 2026-09-27

The user explicitly changed time/launch caps to guidelines against dead ends.
Continue past a threshold when another experiment is useful; record why. Proceed
to the next useful step without asking for renewed permission. This supersedes
all older pending-budget and phase/item approval notes below. Preserve the existing
branch/private-data/seed rules and user-controlled gameplay.

Current work: resource generations and a GPU-native handoff, continuing from the
qualified Games 303–306 command/copy observations. Game 307 is next. The harness
now records guideline usage and experiment rationale without blocking useful runs;
all 24 benchmark tests pass. Eight focused native checks now pass, including the
seven-argument bridge, generation reuse and retirement/map changes during publication.
The preserving factory hook identifies actual allocation births; final frees and map
attempts invalidate diagnostic acquisitions. Game307 is prepared with exact source/
player archive and a recorded new-information rationale. Read recipient checkpoint
2026-09-27-resource-generations.md. No native replacement or speed gain is claimed. Read recipient performance
status and private performance-command-ownership-20260927/progress.json.
Game 277 and earlier builds remain preserved; Uptownfrog only; no commits or pushes.

---

# Command ownership investigation: four-launch cap reached — 2026-09-27

Games 303–306 completed unattended. Game 307 is next, but this item's four-launch
allowance is exhausted. The user asked for continued work until stopped; do not
silently exceed the accepted cap or claim the native ownership contract is proved.

Each run joins 139 complete pass commands and 278 full constants to frozen HLE input.
Ordered reference copies and publication/retirement are qualified for sampled operations.
All eight clinic captures look correct; no logged renderer errors; original seeds intact.
Seven native checks and 24 benchmark checks pass. Failed and inconclusive work is saved.
Game 306 publication/acquisition excluding hashing costs 58.22 / 36.46 / 37.92 ms per
55.1 MiB compound; hashing adds about 144 ms. These are sparse diagnostic elapsed costs.
No native replacement, FPS gain or engine-resource ownership certificate exists.

The missing authority is individual engine resource generation plus complete writer/
alias sequencing. Mapping identity is insufficient. A further item must prove those
and a GPU-native handoff before replacement, with a new run allowance and route evidence.
Read recipient `docs/checkpoints/2026-09-27-command-ownership.md`, then private
`performance-command-ownership-20260927/progress.json`, `ownership-contract-audit.json`
and `closeout.json`. `final-source-and-player.zip` preserves the exact final diagnostic.

Game 277, ordinary/phase-3 builds and launcher match their entry hashes. No game is
running. The wolf D16/HTILE route remains blocked and user-controlled. Stay on
Uptownfrog; no commits, pushes, subagents or new overlays. Older next-run notes below
are historical and superseded by this entry.

---

# Command ownership investigation after Game 305 — 2026-09-27

Continue unattended within the accepted 3-working-day / 4-launch investigation.
Three launches used; Game 306 next. Games 303–305 completed without elevation.
All six clinic captures look correct; no logged renderer errors; original seed intact.
Each run joins 139 complete passes and 278 full constants to frozen HLE input.
Their command owners survive GPU completion/publication.

Games 304–305 acquired nine ordered reference copies each, at the source,
intermediate and final boundaries of three compounds. CE/DE order remains intact.
Game 305 directly proves complete copied buffers survive publication and release
before the retirement callback returns. Seven native / 24 benchmark checks pass.
The 55.1 MiB diagnostic acquisitions cost 203.77 / 179.36 / 181.40 ms per compound,
including publication, copying and hashing. No native replacement or speedup is claimed.

Next: separate those costs and audit mapping identity versus engine resource
generations and escaped writers before the final launch. The shared mapping ID
cannot certify individual resource ownership. Read recipient checkpoint
`docs/checkpoints/2026-09-27-command-ownership.md` and private
`performance-command-ownership-20260927/progress.json` and `game-305/review.json`.
Game 277, earlier builds, launcher and seed saves remain preserved. The wolf
D16/HTILE route remains open and user-controlled. Stay on Uptownfrog; no commits,
pushes, subagents or new source overlays. Earlier pending-decision notes are superseded.

---

# Command ownership investigation after Game 303 — 2026-09-27

The user accepted the recommended 3-working-day / 4-launch investigation and
asked for continued unattended work. One launch used; Game 304 next.
Game 303 completed without elevation or clicks. Both clinic captures are correct;
no logged renderer errors; original seed unchanged. No display timing is available.

Nine original-body resource/allocation hooks observe the retained renderer.
All 139 sampled complete passes match frozen HLE command words, and all 278 full
256-byte constants match independently. Their diagnostic owners survive through
GPU completion/publication before release. Six native checks / 24 benchmark tests pass.
No native rendering replacement, resource-ownership certificate or speed gain is claimed.

Next: qualify source acquisition and output publication at exact in-stream pass
boundaries while preserving CE/DE order. Read recipient
`docs/checkpoints/2026-09-27-command-ownership.md` and private
`performance-command-ownership-20260927/progress.json` and `game-303/command-analysis.json`.
Game 277, both earlier builds, launcher and original saves remain preserved.
The wolf D16/HTILE route remains open; gameplay is user-controlled.
Stay on Uptownfrog; no commits, pushes, subagents or new source overlays.
Earlier phase 5 pending-decision notes below are superseded by the user's acceptance.

---

# Phase 5 decision ready after unattended Game 302 — 2026-09-27

The user authorized work while AFK through phase 5. Game 302 completed without
Windows elevation, desktop automation or user input: observation-only mode uses
runtime captures/logs and process counters, with no display-timing claims.
Both clinic captures are correct; no logged renderer errors; original seed intact.
Seven authenticated hooks join 280 sampled depth uses to observed creation.

Phase 4 ends with a feasibility limit, not an implemented native rendering path.
Actual dynamic updates copy 256 bytes; the pass computes 64 bytes of offsets.
No payload comparison occurred. All 140 command builders allocate after entry;
candidate ranges join later submissions but do not prove frozen identity, visibility
or retirement. No rendering work was bypassed and no native speed gain is claimed.
Read recipient docs/checkpoints/2026-09-27-performance-phase5-decision.md and
2026-09-27-performance-phase4-feasibility.md. Private phase4 BRIDGE-AUDIT.md,
phase4-feasibility-closeout.json and resume-20260927.json preserve the full handoff.

Recommend a user-selected 3-day / 4-launch investigation of command ownership;
alternative: exact retained D16/HTILE route repair. Do not start phase 6 automatically.
Five native contracts and 23 benchmark tests pass. Prior failed fixture log preserved.
3/20 phase-4 launches used; Game 303 next, 17 unused. No game or collector running.
Preserve Game 277, both previous builds, launcher and saves; hashes are exact.
User controls gameplay; wolf-attack route remains open. Uptownfrog/hooks unchanged.
No commits, pushes, new overlays or subagents. Old permission-blocked notes below
are historical and superseded by the successful unattended Game 302.

---

# Phase4 blocked on Windows elevation; Game302 unused — 2026-09-27

Game301 completed with reviewed clinic imagery,278 sampled creation/use joins and
27.5FPS diagnostic timing. No native renderer or performance gain is implemented.
Observer-v4 is ready to observe constant payloads and command-builder boundaries;
five native contracts and22 benchmark tests pass. All preserved binary/launcher
hashes match.2/20 phase4 launches used; Game302 next,18 remain. Uptownfrog only.

The subsequent Windows elevation was not granted. Owner3128/exec30936 have exited;
no game/collector is running. The pending notes below are superseded. Desktop
control exposed no consent window; a separate app-inspection approval timed out.
User authorization persists, including accepting prompts, but OS consent is needed
for a fresh collector. Do not wait on the expired request or consume a run number.
Read recipient docs/checkpoints/2026-09-27-performance-phase4-pause.md and private
phase4 resume-20260927.json. Game302-preflight.json and BRIDGE-AUDIT.md preserve
ready commands and the specific native/reference ordering gaps. After302, analyze
observer data then command boundaries; range containment is not ownership proof.

Gameplay stays user-controlled. Retained wolf-attack D16/HTILE failure stays open.
Preserve277, original ordinary/phase3 builds, launcher and seeds. No commits,
pushes, subagents or new overlays. Continue only within phase4; phase5 is a user gate.

---

# Phase4 Game301 complete; Game302 Windows consent pending — 2026-09-27

Continue until blocked or phase5; this authority includes accepting prompts.
Game301 completed140s:278 creation/use joins,423 paired observer calls, normal
startup/loading/clinic captures,27.5FPS diagnostic window, no logged renderer errors.
Original seed preserved. Game300 failure did not recur; its cause remains unknown.
No native rendering path exists yet. Constants, exact queued versions, aliases and
fence retirement remain open; raw pointer joins do not establish ownership.

Observer-v4 adds dynamic64-byte update and command-builder boundary observations.
Five native contracts pass;21 benchmark tests passed. Game302 is ready but NOT
launched:2/20 phase4 launches used,18 remain. Python owner3128 / exec30936 waits
for Windows collector permission. Existing request: recipient private/perf-lab/
performance-phase4-20260926/timing-sessions/0a48a0d282c04633b7160df75ce49649/request.json.
Do not duplicate it. Desktop tool exposed no consent window; user was asked to
click the OS prompt. A prior game-window inspection hit app-approval timeout.

Resume private phase4 resume-20260927.json; inspect Game302 if approval has arrived.
Analyze with analyze_observer.py302 then analyze_boundaries.py302. Private
BRIDGE-AUDIT.md records exact stream/constant limitations and the next proof.
Public report: recipient docs/checkpoints/2026-09-27-performance-phase4-game301.md.
Preserve277, ordinary/phase3 builds, launcher and seed. Uptownfrog/hooks unchanged.
User controls gameplay; wolf-attack D16/HTILE route failure open. No commits,
pushes, subagents or new source overlays. Do not silently start phase6.

---

# Phase4 Game300 analyzed; improved diagnostic ready — 2026-09-27

User authority continues through a blocker or phase5; gameplay is user-controlled.
Game300 did run after approval. Old PID/session consent notes below are superseded.
No game or collector is running. Phase4 used1/20; Game301 next,19 remain.
256 sampled depth-chain uses join observed births. Presentation stopped at about
27 seconds while commands continued; no capture survived, exact abort was lost.
User did not observe the run. Cause unknown; no pixel/lifetime/speed claim.

Observer-v3 separates lifecycle logging from a bounded map sample and adds
window-state events. The benchmark preserves failures, input and timing rows.
Early captures are diagnostic only. Five native contracts and 21 benchmark tests
pass. Reusable timing collection permits one Windows approval per bounded batch.
Next: Game301 with materially better diagnostics, then a qualified native bridge.
Read recipient docs/checkpoints/2026-09-27-performance-phase4-game300.md.
Private game300-followup.json and observer-v3 logs preserve evidence.

Retain277, prior ordinary/phase3 builds, launcher and original saves. Uptownfrog,
hooks/push guards unchanged. No commits/pushes/subagents/new source overlays.
Native ownership, ordered reference transfer and fence retirement remain open;
no native rendering replacement exists. Wolf-attack D16/HTILE route failure open.

---

# Phase 4 observer ready; Windows consent pending — 2026-09-26

The user authorized continuing until blocked or phase5; discovery is approved.
Six original-body resource hooks and bounded pass metadata are implemented in
recipient build/vulkan-native-pass-v1. Five native contracts and18 benchmark tests
pass. Initial clang-cl fixture linkage failed; existing NT_TIB access fixed it.
No native rendering replacement, live identity join or speed claim exists yet.
Game277, both retained builds and manual launcher remain hash-exact. Uptownfrog;
no commit/push/subagents/new overlays. Gameplay is user-controlled.

Game300 is waiting on the Windows PresentMon elevation prompt:0/20 launches used.
Exec session20815, benchmark_session.py owner PID8048. Its pending request is
recipient private/perf-lab/performance-phase4-20260926/timing-sessions/
bd47ec093529450ca6af48aa39430cfe/request.json. Do not start a duplicate collector.
OS approval lets the140-second copied-Timmy stationary diagnostic proceed and
close automatically. The async question requests the OS click, not new authority.

Resume from recipient docs/checkpoints/2026-09-26-performance-phase4-observer.md
and private phase4 observer-handoff.json. Inspect trace/captures before implementing
a native/reference bridge. Preserve frozen command order, output visibility and
fence-delayed retirement. The wolf-attack D16/HTILE route failure remains open.
Prior snapshots, successful checks and unsuccessful build logs are preserved.

# Phase 4 discovery complete; await discovery review — 2026-09-26

The user authorized phase4 with “On to phase 4 then.” Discovery finished early;
phase4 itself is NOT complete. Its roadmap explicitly requires a discovery report
and user review before continuing. No prototype implementation or game launch yet.

Candidate: complete two-stage native depth reduction, persistent targets/views,
versioned constants, explicit reference/native transitions. New static evidence
locates initialization e5b140, scheduled entry e5b220, execution e5b2d0/e5b350,
updates2168a20/26adb90, map-end callers and disposal consumer e45d80. Earlier
wrapper/backing/free analysis is preserved. Ghidra60functions/49,583bytes;
LLVM3,073 instruction starts in24spans agree after six exact LOCK-prefix groups.
Four pseudocode windows remain unsuitable as whole-body semantic proof.
Live birth/use/free joins, raw aliases and mixed-renderer completion remain open.
Native disposal counts do not replace host fences; no current FPS gain is inferred.

Read recipient docs/checkpoints/2026-09-26-performance-phase4-discovery.md and
private/perf-lab/performance-phase4-20260926/DISCOVERY.md, discovery-closeout.json.
Negative setup/decompiler/cache experiments are recorded; ghidra-v5 is qualified
by a unique script class/runtime version. Do not rerun older private scripts blindly.

After review: new plain-C++ bounded identity/observer work, focused lifecycle/order
checks, then Game300 to join successful births to the selected targets/constants
while original rendering remains active. That observation is not the native-path
success condition. The actual prototype must bypass PM4/address reconstruction
for the closed pair, show pixels/work and account for bridge overhead.

0/20 phase4 launches used; Game300 next. User controls gameplay. No game/collector
running. Game277, original ordinary build/manual launcher and phase3 build preserved.
Uptownfrog/hooks/push.default=nothing; no commits/pushes/subagents/new overlays.
The wolf-attack D16/HTILE route failure remains OPEN. Do not silently widen this
prototype into general D16 support or resume the donor's paused AOT startup work.

---

# Phase 3 complete; await phase 4 authorization — 2026-09-26

The active Vulkan runtime now builds ordinary C++ from third_party/shadps4-gpu.
235 imported files are byte-exact; 103 compilation units retain equivalent flags.
Three verified archives preserve all current workspace work, retained 277 inputs,
effective sources, dependencies, manifests and build configuration. No commits/pushes.

Game 299 smoke: 27.5 FPS; median/p95/p99 37.50/41.67/45.79 ms, inside phase 2 calibration.
Both clinic captures correct, no logged renderer errors, one ETW drop. Three startup
frame-ID values are missing outside the window, also seen in retained Game 298.
Seven runtime/two shader contracts, visible presenter validation, both launcher
checks and 16 timing tests pass. Final build does no work and binaries match Game 299.

The new normal build is build/vulkan-materialized-v1. Retained277, the original
ordinary binaries, original map and manual launcher remain preserved. Uptownfrog only.
The wolf-attack 512×512 D16/HTILE route failure remains OPEN; no renderer fix attempted.
The user controls future gameplay. Phase 3 used 1 of 2 launches; Game 300 is next unused.
No test game/collector is running. Phase 4 has not started; await user authorization.

Read recipient [phase 3 report](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-26-performance-phase3-materialization.md)
and [source layout](external/Bloodborne-Recompiled/docs/vulkan-gpu-rewrite.md).
Private evidence: recipient private/perf-lab/performance-phase3-20260926/closeout.json.

---

# Phase 2 measurements complete; wolf route blocked — 2026-09-26

Timing, three-run calibration, exclusive Tracy analysis and overhead measurement
are complete. Clean clinic: 27.2/28.0/27.8 FPS; Tracy adds 12.59/10.17 ms per
interval in two pairs. GPU execution/overlap remains unmeasured. No sustained-30 claim.

Game 297 reached the lower hallway. The user controlled Game 298, which froze
DURING the wolf attack on retained 277: unsupported 512×512 D16 depth with HTILE.
The 23.5 GB full dump, logs, fault, last captures and exact binary/map identities
are preserved. The benchmark rejects the missing 43.8-second window tail and
free-text renderer errors; 16 focused timing tests pass. The route remains failed.

All original seeds, retained/ordinary binaries and manual launcher are hash-exact.
No test game/collector is running. Eleven of twelve launches used; 299 is unused.
Future gameplay belongs to the user: use manual input, audio on, overlay off.
New D16 layout/publication/HTILE support exceeds phase 2; await a scope decision.
No optimization or phase 3 started, no commits/pushes/subagents; Uptownfrog only.

Read the recipient [phase 2 report](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-26-performance-phase2-measurement.md),
[profile](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-26-performance-phase2-profile.md), and
[route failure](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-26-wolf-attack-d16.md).
Private evidence: recipient private/perf-lab/performance-roadmap-20260926/.

---

# ACTIVE: Phase 2 calibrated; Tracy overhead block under way — 2026-09-26

Windows timing permission was granted. Standalone PresentMon2.3.1 streams raw-QPC
timing through private timing-admin-session-v4.ps1 (collector60788, wrapper12036;
bounded one hour, task stop marker supported). Games289/290/291 delivered
27.2/28.0/27.8displayFPS; all six captures correct, seeds unchanged, no renderer
errors/frame-ID gaps. CSV sharing/encoding failures were repaired from original
data without repeating runs. Twelve timing tests pass.

Game292 attached to launcher, excluded; Game293 hit trace RAM cap at17seconds.
293 first five steady seconds have validated exclusive zones/clock alignment.
Game294 active with14second trace plus five-second CPU boundaries.
Overhead291A/293B/294B/295A, then route296. Seven of twelve launches started.
Clock-aligned exclusive extraction: tools/tracy_window.cpp and benchmark_tracy.py.
Read recipient docs/performance-status.md and phase2-measurement checkpoint.
Preserve277; Uptownfrog only; no commits/pushes/subagents/optimization/phase3.

---

# BLOCKED: Phase 2 timing needs Windows ETW permission — 2026-09-26

The user resumed phase 2; the accepted stock shadPS4 reference is unchanged.
NVIDIA PresentMon exits silently; installed standalone PresentMon 2.3.1 reports
ETW access denied outside the sandbox. No successful UAC trace is established.
Benchmark preflight now rejects before spending a game launch; ten timing tests
pass. Game 277 frozen/ordinary binaries and manual launcher remain hash-exact.
Game 289 is still next, with 11 of 12 phase-2 launches remaining. No game is running.

Read recipient docs/performance-status.md and
[the current checkpoint](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-26-performance-phase2-timing-blocker.md).
Obtain successful administrator timing access, then finish three-run calibration,
exclusive Tracy analysis, balanced overhead measurement and the copied-Timmy route.
No optimization, phase 3, commits, pushes or subagents. Uptownfrog only; preserve
all private evidence, original game views and seed saves. This is an OS-permission
block, not a user pause or a completed phase.

---

# PAUSED: Game69 gains 51 percent; current batch complete and work paused — 2026-09-16 20:40 UTC

Paused at user request after completing game69. The transient-acquisition and pixel-counter batch passed25/25 focused checks (20.25s). Early clinic5.960899FPS and late6.208714FPS versus game68 4.011427/4.113467: +48.60%/+50.94%. Pink remains absent in directly inspected200.78/276.95s clinic frames. Normal300.821s run,3901presents,0logged renderer errors,299Crosspairs;seed and186sources unchanged. MatchedDX11late10.614763FPS remains ahead. Movement stays shelved. No new implementation is pending; wait for explicit resume.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Work paused by user request after the current test. Do not test, launch, schedule or resume automatically; wait for explicit user resume.

---

# ACTIVE: Transient acquisitions and deferred pixel counters qualified — 2026-09-16 20:31 UTC

Game69 ready: transient owned upload/copy acquisitions omit unused cache versions; pixel counter groups use bounded deferred completion.25/25 focused checks pass20.25s.186sources and frozen player/map verified,5586sidecars. Retain pink fix;300s stationary, movement shelved. Game68late4.113467FPS; matchedDX11target10.614763 remains open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Adaptive copies preserve rendering; profile moves to code-page reads — 2026-09-16 20:19 UTC

Game68 clean300.715s,3488presents,0logged renderererrors,299Crosspairs,seed/186sources unchanged. Pink absent at201.24/277.59s. Early4.011427FPS,late4.113467 (+6.07%67late butequal65): no robustendpointwin. CPU segmented validation waits disappear; shader-code reads from shared GPU-owned pages now29wait stacks, source-pressure13,packetprefix9. Continue pixel-query deferred completion and uncached transient acquisition; movement remains shelved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Adaptive copy routing qualified for stationary game68 — 2026-09-16 20:10 UTC

Game68 adaptive native-validation copy batch ready:13distinct scoped checks pass. Sparse copies/fills and aligned disjoint ordinary copies use GPU route with pending validation; ordinary-copy destination now retains native ownership. CPU overlaps/unaligned copies retain guarded CPU semantics. Existing CMASKpositive/bad-tag cases now execute dependent sparse/DMA/fill and whole-byte/ownership oracles;64slotqueue contract passes.186sources frozen,5586sidecars/map verified. Run300s stationary; user shelved movement.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native validation waits shifted to CPU copies; movement shelved — 2026-09-16 19:59 UTC

Game67 native validation batch completes420.801s with4006presents and0logged renderer errors;pink absent in viewed201.02/277.12s clinic frames. Early4.065154FPS,late3.878043: no improvement overgame66/65 ormatchedDX1110.614763. Native conversion waits shifted toRecordSegmentedCopy CPU-publication gate(45 sampled wait stacks).186sources unchanged;419Crosspairs,seed unchanged. Movement capture missed due eight-frame cap; inconclusive, and user subsequently shelved movement. Future runs stationary300s. Continue adaptive copy routing to preserve GPU batching.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native validation batching and descriptor reuse qualified for game67 — 2026-09-16 19:45 UTC

Game67 native validation batch qualified:63 distinct scoped checks pass across recorded invocations,186-source frozen player/map.64 bounded status slots batch depth encode/decode and CMASK; descriptors and immutable layouts reused. All CPU publication gates validate, including PM4 immediate markers and CPU fallback copies. Pink fix retained. Launch420s: stationary0..300 for matched FPS, camera/player movement305..400 with captures. Performance remains priority; record movement defects.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Submission waits reduced; add captured movement phase to subsequent runs — 2026-09-16 19:21 UTC

Game66 completes cleanly, pink absent in viewed200.86/277.16s clinic frames. Stationary182..220FPS4.008175 (+0.65%65): no demonstrated endpoint gain. Completion wait stacks36->7; other packet waits remain. User now requires camera/player movement toward door in every game run; game66 late input missed capture, inconclusive. Future runs extend after stationary measurements with captures. Continue native conversion waits/descriptor reuse; matchedDX11target10.614763 still open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bounded submission overlap qualified for game66 — 2026-09-16 19:13 UTC

Game66 qualified: bounded eight-job asynchronous submission with retained task owners and positive retirement at capacity, idle, yields and administrative consumers.29 distinct focused checks pass across two recorded invocations;184 sources and frozen map verified. Pink remains fixed. Launch matched300sTimmy run and continue depth/CMASK and descriptor lifetime work; DX11target10.614763FPS remains open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Range batch removes repeated sorts; clinic remains below matched DX11 — 2026-09-16 18:59 UTC

Game65 completed normally; pink absent in directly viewed162.90/277.18s clinic frames. Late4.107034FPS (+2.67% versus game64);early3.982441 (-1.27%), so no robust endpoint gain claim. Prior repeated Seal sorting has33->0 raw IP samples, renderer CPU time essentially unchanged.20lookup checks plus4final affected checks pass. Continue eight-job bounded submission overlap; matchedDX11target10.614763 remains open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Incremental image ranges and shared buffer sorting qualified — 2026-09-16 18:51 UTC

Game65 qualified: incremental negative image indexes plus one shared buffer-owner sort and coalesced sorted enrollment.20/20lookup checks19.30s; final self-move guard followed by4/4affected checks7.95s.184source hashes and frozen player/map verified. Pink fixed; game64late4.000166FPS;matchedDX11 10.614763FPS. Run visible300s Timmy comparison and continue.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Fault cache preserves rendering but does not improve measured clinic FPS — 2026-09-16 18:39 UTC

Game64 completed cleanly: late clinic4.000166FPS versus game63 3.994062 (+0.15%; no demonstrated endpoint gain), early4.033760. Pink remains fixed in directly viewed162.74/277.11s clinic frames.19/19focused fault/register/TLS/coherent checks passed. Normal300.722s,3182presents,0renderer errors,299Crosspairs,seed unchanged;184sources unchanged. Continue renderer CPU work and GPU wait reduction toward matchedDX11 10.614763FPS.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Fault dispatcher bookkeeping batch qualified for game64 — 2026-09-16 18:29 UTC

Game64 ready:thread-handle reuse andvalidated mailbox-slot cache;19/19focusedchecks3.90s,184sourcesqualified. Pinkfixed anddeferredheap batch retained. Game63late3.994062FPS;matchedDX11target10.614763. Launchvisible300sTimmy comparisonandcontinue.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Deferred retirement removes producer stalls and improves clinic12percent — 2026-09-16 18:24 UTC

Game63 lateclinic3.994062FPS,12.08% over correctedgame61 3.563619;early3.943380. Pinkremainsfixed. Normal300.699s,3601presents,0renderererrors,299Crosspairs,seedunchanged.9/9focusedchecks. CPU retirementwaitstacks279->0,rendereridle74->3 versusgame57. MatchedDX11game62 10.614763FPS remainsahead. Next batch targets repeated fault-dispatch bookkeeping, withGPUwaitspreserved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Deferred heap retirement batch qualified for game63 — 2026-09-16 18:16 UTC

Game63 ready:bounded deferred small-heap retirement plus removalofunneededowner scans.9/9focused checks pass8.22s,real HLE release nowreturns0.09–0.32ms whilependingbytesstayalive. Pink fix retained;freshmatchedDX11target10.614763FPS. Launch one300sTimmyrunwithCPUstackwindow230..250s;continuework.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Matched DX11 baseline measured; producer retirement stall reproduced — 2026-09-16 18:11 UTC

Fresh matched-settings DX11 game62 completes300.499s:late10.614763FPS versus correctedVulkan game61 3.563619FPS. Same clinic/4K240/AAOFF/Timmy/currentbinaries. Pink absent in both. Reproduced small-heap deletion blocking active Vulkan snapshot:focused real-HLE regression fails after263.564ms instead of returning. Implement bounded deferred retirement and skip small-block owner scans together.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Pink fixed in early and late live clinic; resume performance work — 2026-09-16 17:58 UTC

Pink fixed and visually verified in game61 at48.42s and277.36s. Guest descriptor requests alpha8; initialized blend object and original PM4 now both contain8 instead ofD. Normal300.698s session,3331presents,0logged renderer errors,299Crosspairs,seed unchanged.21focused checks passed. Late clinic 3.563619FPS; matchedDX11 performance goal remains open. Continue critical-path performance work.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Pink traced to uninitialized guest blend accumulator; repair qualified — 2026-09-16 17:49 UTC

Pink cause found in game60: guest blend accumulator is uninitialized0xBAADF00D, ORed with requested descriptor channels, yielding maskD. Signature-verified initialization fixes all128seed/channel cases. Child-only normal Windows heap retains fault dispatch.21focused checks pass across recorded invocations; game61 will validate colors.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native1080p color control blocked by depth validation — 2026-09-16 17:34 UTC

Game59 native1080p/no profile control fails depth/HTile validation at32.009s before clinic; inconclusive for pink. Original masks now traced to guest setter1072fd0; Yebis caller ANDs context+2ec0 with blend object+164. Observe those objects on working4K path next.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game58 proves wrong-channel state in submitted guest commands — 2026-09-16 17:27 UTC

Game58 complete;2042whole buffers/33531188B capture includes both damaging post passes. Original guest PM4 explicitly writes CB_TARGET_MASK0xD for fbe7c4b6 and bf368417; Vulkan does not invent it. Pink priority continues. Next control restores native1080p/no display patches to distinguish guest profile state.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game57 diagnosed host waits; user prioritizes pink correction — 2026-09-16 17:11 UTC

Game57 clean and real host stacks obtained; lateFPS contaminated by build, no performance claim. User priority now pink first. Expand bounded PM4 capture to locate wrong-channel state; CPU tuning parked until color issue addressed.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game56 complete; mutex microbenchmark win, FPS effectively unchanged — 2026-09-16 16:59 UTC

Game56 clean,late3.69965FPS,pink persists;mutex benchmark win did not move the endpoint beyond prior variation. Renderer affinity is unrestricted. Depth validation and scheduler waits remain large; active investigation continues.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game56 qualified with mutex membership and lifetime batch — 2026-09-16 16:46 UTC

Game56 ready: mutex lookup cache and pin-transfer batch;12 relevant contracts pass, focused benchmark29.4xfaster. No game speedup claim yet. Callback fixture clang build problem fixed. Launch and continue; rendering/matchedDX11 goals open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game55 raw export much faster; frame rate still limited elsewhere — 2026-09-16 16:31 UTC

Game55 clean,raw4Kexport6.6–9.4xfaster onGPU butFPS3.63 unchangedwithinrunvariation,pinkremains. No FPS winclaimed. Next serialCPU investigation:guestmutexhandling andmemoryprotection, beforeanotherGPU-onlybatch. Activeworkcontinues.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game55 qualified with direct raw color export — 2026-09-16 16:24 UTC

Game55 ready: two color copies removed together;19/19 focused checks clean,169sources qualified. Launch next; pink correctness and matchedDX11 goal still open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Raw export byte oracle passes; padding visibility barrier corrected — 2026-09-16 16:20 UTC

Raw export first gate18/19; all pixel bytes exact, sync validator caught omitted untouched-padding dependency. Barrier fixed; requalifying before game55. Active work continues.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game54 isolates conversion copies and resource-pressure waits — 2026-09-16 16:11 UTC

Game54 completed cleanly; pink unchanged,late3.707883FPS. Wait attribution identifies repeated depth/CMASK/retention waits; raw color export copies expensive. Active next batch removes two color GPU copies without changing128MiB retention bound or padding contract. No final acceptance or matchedDX11 claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game54 qualified for encoder wait attribution — 2026-09-16 15:53 UTC

Game54 is ready: label all existing encoder wait phases, retain eight tags per stage using a separate resident-wait stage, and enable existing bounded depth GPU timing.12/12 focused checks pass24.53s;168 source/binary receipt and matching map frozen. No synchronization semantics changed. Continue through profiling and combined fixes toward correct rendering faster than matched DX11; do not end work at a batch checkpoint.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game53 combined batch improves late clinic by8.30 percent — 2026-09-16 15:12 UTC

Game53 combined backing/query batch passes23/23 targeted checks (48.01s). Same Timmy clinic:260..299s3.591724FPS versus3.316572game52 (+8.30%) and3.048129game51 (+17.83%);182..220s3.504951 (+10.38%game52). Normal300.709s run,2796presents,zero logged renderer errors,299Crosspairs,seed unchanged. Pink persists; historicalDX11AAON remains unmatched. Verified sampler outside FPS windows; ValidateGpuBacking rawIPs30->7. GPU waits now largest measured stage; attribute validation/readback/pressure phases before altering synchronization. No speculative wait removal. Routine lookup gate20 checks; only23 for this expanded batch;326 full remains for broad/final qualification. User requests batching fixes. See detailed checkpoint and game-53 private evidence; primary resume file is updated to current state.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Combined backing query batch passes23 scoped checks — 2026-09-16 15:01 UTC

The next combined batch passes23/23 targeted checks in48.01s. Game53 is READY from168 frozen sources. Mapping/ownership-scoped backing validation reuse, exact written-union GPU-modified queries, and readonly diagnostic proof-count access are measured together in one300s run.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game52 lookup batch improves clinic FPS; next combined batch — 2026-09-16 14:55 UTC

Game52 completes cleanly at3.316572FPS in260..299s versus3.048129game51 (+8.81%);182..220s3.175395 versus2.838600 (+11.86%). All326 checks passed before launch. Pink remains. Routine lookup iterations now use20 checks (~39.64s); user reiterates batching multiple measured fixes before testing/game runs.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Lookup batch qualified; routine testing reduced to20 checks — 2026-09-16 14:43 UTC

Vulkan lookup batch passes326/326 checks in483.21s; game52 READY from168 frozen sources. User requested less repeated testing: routine lookup gate is now20 selected checks (39.64s in this run); full sweep remains explicit for broad changes/final qualification. Proceed with one300s visible Timmy comparison.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Vulkan lookup batch fixes reproduced index regression — 2026-09-16 14:33 UTC

User explicitly resumed Vulkan work. The pending lookup batch compiles and all12 focused checks pass24.11s. The previously failing real-GPU native-input test now completes all6 CPU/GPU/remap phases with0 repeated index rebuilds and0 repeated decodes. Full-build qualification is next; no new game or performance claim yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# PAUSED: Paused after native index regression; resume tomorrow — 2026-09-15 23:18 UTC

User requested stop after the current test and a prompt for tomorrow. Work is paused. Game51 reached3.048129FPS (65% faster than game50), pink remains. Final native-input regression reproduced8 redundant index rebuilds across8 unchanged GPU operations. No renderer/test/build processes remain. Await explicit user resume.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Work paused by user request after the current test. Do not test, launch, schedule or resume automatically; wait for explicit user resume.

---

# ACTIVE: Game51 reaches3.05FPS; next lookup batch identified — 2026-09-15 23:10 UTC

Game51 page/range batch reaches3.048129FPS in the late unprofiled window,1.6502xgame50 and5.8155xgame48.182..220s2.838600FPS(1.6294xgame50). Pink remains. Continue with measured redundant union rebuilds and texture lookup scans as the next batch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game51 page/range batch passes326 checks — 2026-09-15 23:02 UTC

Game51 page/range CPU batch passes326/326 checks in469.32s.168 sources and3 frozen binaries verified. Proceed with one300s visible run, matched game50 settings and automatic CPU sampling after230s.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game51 page and range batch prepared — 2026-09-15 22:57 UTC

Third measured CPU batch compiles and passes10 focused checks. Game51 is frozen from168 sources; the full326-test suite is running. Same matched clinic settings and automatic230s CPU sample. No new FPS result yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game50 reaches1.85FPS; next CPU range batch identified — 2026-09-15 22:40 UTC

Game50 finishes cleanly:1.742116 FPS in182..220s (1.2097xgame49,3.5305xgame48);late unprofiled260..299s1.847095 FPS (1.1507xgame49,3.5241xgame48). Pink remains. CPU sample identifies protection bookkeeping and native-range tree rebuilding; batch those next.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game50 second batch passes326 checks — 2026-09-15 22:30 UTC

Game50 is READY: second CPU batch passes326/326 selected tests in474.36s,168sources verified. Proceed with one300s visible run and automatic verified after230s CPU sampling.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game50 temporary-read and pending-index batch prepared — 2026-09-15 22:26 UTC

Second performance batch compiles from168 sources and passes12 focused checks, including3 new native/metadata regressions. Game50 prepared with the full326-test suite still running; launch remains gated.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game49 CPU batch triples frame rate; pink remains — 2026-09-15 22:07 UTC

Game49 CPU batch improves matched clinic presentation throughput to 1.440100 FPS from 0.493446 FPS in game48 (2.918x), and 0.396157 in game47 (3.635x). First verified clinic capture103.514053s versus prior178.708463s; cadence bounds progression, not an exact load-time benchmark. Strong pink remains; performance is not accepted. Continue batching measured CPU/publication/synchronization costs.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CPU batch passes323 checks; game49 ready — 2026-09-15 21:58 UTC

Game49 is READY with the complete CPU batch:323/323 current Vulkan/shared native checks pass475.40s;167 sources and three binary hashes verified. Proceed with one300s visible run to measure the combined gain.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Batched CPU fixes locally pass; full suite running — 2026-09-15 21:51 UTC

Batched CPU fixes compile and pass9 existing shared checks plus4 new regressions. Game49 is frozen but gated on the full Vulkan/shared native suite. User explicitly requests combining known costs before the next game run.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game48 upload reduction; batch remaining known costs — 2026-09-15 21:31 UTC

Game48 cuts uploads22.13GB->0.267GB and improves in-game presentation throughput; pink remains. User requests batching all identified bottleneck fixes before the next game run. Prioritize redundant page protection, shader acquisition overhead and layout-plan rebuilding.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Overlapping input reuse qualified; game48 ready — 2026-09-15 21:21 UTC

Overlapping input upload fix passes its real-GPU regression and 19 shared checks. Game48 is frozen from164 sources to measure performance with game47 settings; no game speedup claim yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game47 proves overlapping input upload churn — 2026-09-15 21:06 UTC

Game47 identifies overlapping CPU buffer views as the upload cause:21.59GB missed because a single cached range did not cover the request; all22.13GB of new snapshots had valid versions. Implement reuse of covered subranges and upload only gaps.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game47 ready for CPU cache miss attribution — 2026-09-15 20:55 UTC

Game47 is ready to attribute CPU buffer cache misses;6focused checks and the enabled observer fixture pass. Performance is the user priority from any justified angle, not exclusively CPU.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game46 complete; CPU optimization takes priority — 2026-09-15 20:48 UTC

Game46 again reaches pink clinic at180.673811s and ends normally at300.765s. User explicitly prioritizes CPU/loading optimization after this run; park color investigation and analyze repeated buffer uploads.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game46 prepared to trace post-processing masks — 2026-09-15 20:38 UTC

Game46 is ready from unchanged game43 binaries/163 sources for a late-arm PM4 capture. The pink frame overwrites red/blue/alpha in two post-processing passes; current shader execution and identity mask conversion are verified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game45 frame captured; pink localized to post-processing — 2026-09-15 20:11 UTC

Game45 reproduces verified pink clinic gameplay and saves a complete Vulkan frame. Offline replay reproduces the defect; scene colors are plausible at event44548 and pink by44620. Trace the intervening post-processing channel writes. No renderer edit or FPS win yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game44 capture wrapper stalls before renderer entry — 2026-09-15 19:50 UTC

Game44's RenderDoc child-hook wrapper stalled before renderer entry. Verified parent51636 was stopped; child/wrapper/controller all retired, seed unchanged. No capture or renderer result; next use the Vulkan layer directly, leaving the native parent launch unchanged.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game44 prepared for pink frame capture — 2026-09-15 19:44 UTC

Game44 prepared from the unchanged qualified game43 binary for one pink-clinic GPU capture and an in-game timing window. 420s observation, telemetry only, cold cache/copied Timmy, 2160p/cap240/AA OFF. No source edits or rebuild.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game43 reaches clinic gameplay with pink output — 2026-09-15 19:34 UTC

Game43 reaches visually verified Timmy gameplay in the clinic by180.135297s, with a severe pink world tint and about 0.394 FPS. No renderer rejection or memory stop. The loading blocker is cleared for this copied save; visual correctness and higher-than-DX11 performance remain incomplete.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: User resume before game43 — 2026-09-15 19:25 UTC

User explicitly resumed. Game43 source and all three frozen binary hashes match its qualified receipt (163 sources); the telemetry monitor hash also matches. No game43 session exists and no renderer process was running. Proceed with the prepared 300-second visible Vulkan observation.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# PAUSED: Paused before game43 for Dota — 2026-09-15 17:52 UTC

User requested a pause before the next game run while playing Dota. Game43 is prepared but has not launched; its session.txt is absent. Wait for explicit user resume. Do not build, test, launch, schedule, or resume automatically.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. GPU work paused by user request while they play Dota. Do not test, launch, schedule or resume automatically; wait for explicit user resume.

---

# ACTIVE: Game43 ready with memory telemetry only — 2026-09-15 17:47 UTC

Game43 is ready with tested volume fix and lightweight snapshot caller tags. The verified-child monitor now records memory only; the arbitrary8GiB stop is removed as explicitly requested.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game42 clears volume; remove diagnostic memory stop — 2026-09-15 17:44 UTC

Game42 passes the RGBA32F volume rejection and reaches1490presents; no renderer errors. It ends because the private8GiB diagnostic monitor terminates the child at129.521s. User explicitly removed that arbitrary cap; next run retains memory telemetry.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Thin volume verified; game42 ready — 2026-09-15 17:30 UTC

Thin-volume output passes10 focused regressions and36 enabled GPU timing pairs. Game42 is frozen from163 sources to test progression past the mode13 RGBA32F16-cubed rejection, with allocation census0 and an earlier70s observer.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game41 confirms allocation diagnostic slowdown — 2026-09-15 17:20 UTC

Game41 confirms major allocation-census overhead. Disabling only that diagnostic cuts time to the same16-cubed volume rejection from222.674477s to120.903479s. Last six frame intervals fall from6.62–7.59s to2.20–2.74s. No gameplay yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game41 allocation census comparison ready — 2026-09-15 17:13 UTC

Game41 is ready for a causal allocation-census A/B: identical qualified game40 binary, cold cache, 300s configuration and late observers; only BB_VULKAN_ALLOCATION_CENSUS changes1 to0.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game40 identifies volume output and CPU cost — 2026-09-15 17:07 UTC

Game40 reaches 222.674477 s before a new rejection: RGBA32F mode13 16x16x16 storage-volume output. Late CPU work is dominated by snapshot/publication handling (16.752381 s exclusive combined); GPU work has 11,384 complete available samples. Still loading, no gameplay/FPS claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game40 late loading cost diagnostic ready — 2026-09-15 16:56 UTC

Game40 is ready with the same qualified binary and162 sources. A300-second run moves the bounded CPU/GPU sample to the late slow phase, starting120000ms from worker epoch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game39 clears errors; late loading cost next — 2026-09-15 16:55 UTC

Game39 passes both known shader and shared-depth edge stops and keeps presenting through175.824488 s without renderer errors. Still Hunter Chief Emblem loading at0.1 FPS. Next move the cost/GPU sample into this new late slow section and observe for300 s.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Shared edge fully qualified; game39 ready — 2026-09-15 16:47 UTC

Game39 is ready from 162 frozen sources after all 297 Vulkan tests, 12 focused depth tests, and the enabled quarter-edge fixture passed.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Shared quarter-depth edge regression passes — 2026-09-15 16:41 UTC

The shared quarter-depth edge fix passes the six-phase native regression and all 12 focused depth contracts. The full 297-test Vulkan suite is running. Game39 will test progression beyond the confirmed game38 edge rejection.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game38 proves shared quarter-depth edge blocker — 2026-09-15 16:32 UTC

Game38 identifies the exact blocker: changed logical depth in a shared 960x540 quarter-resolution edge tile. All 8,160 tiles completed and every depth value passed; the current converter rejects the bottom four logical rows when their shared metadata remains cleared.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game38 depth failure evidence ready — 2026-09-15 16:21 UTC

Game38 is ready to classify the game37 depth failure, using failure-only reporting of the existing validation status and resource profile. All 12 focused native tests pass on the 296-test functional baseline.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game37 clears constant shader; depth failure next — 2026-09-15 16:17 UTC

Game37 gets past the c31bd920 shader DMA rejection, then stops on resident depth/HTile conversion or validation at 131.637809 s. Loading remains visible; gameplay and a DX11 FPS win are unverified. Next capture the existing depth result and exact failing profile.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bounded shader constants fully qualified; game37 ready — 2026-09-15 16:11 UTC

Bounded shader constants pass all 296 Vulkan contracts, the SRT unit test, and the enabled GPU timing fixture. Game37 is ready from 161 frozen sources to test progression beyond the game36 shader rejection.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bounded shader constants pass native regression — 2026-09-15 16:10 UTC

The game36 shader rejection is eight fixed constant reads through user registers 14/15. A narrow lowering now uses their proved owned snapshot. Four focused contracts pass; the full 296-test Vulkan suite is running. Gameplay and the DX11 performance goal remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game36 upload improvement exposes shader DMA rejection — 2026-09-15 15:47 UTC

Game36 proves native-input reuse removes the repeated-upload majority:10,089 to523 uploads across the three 4K inputs; loading improves to1.8–2.0FPS. It then stops on an explicit unbounded shader DMA rejection at121.684624s. Next implement a proven bounded constant-read plan, not further speculative FPS work.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native input reuse fully qualified; game36 ready — 2026-09-15 15:36 UTC

Native input reuse passes all293 Vulkan contracts and two enabled diagnostic fixtures. Game36 is frozen from157 sources for180s loading/progression comparison. Child130602ebfa7a05151541816cf2b043b8979ee2525bb413bc4bb5ef0eaf38d252. No gameplay/FPS claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native GPU input reuse regression passes; full suite pending — 2026-09-15 15:29 UTC

Native GPU input reuse now passes its six-phase pixel regression. The full 293-test Vulkan suite is running; gameplay and FPS remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game35 confirms repeated native texture uploads — 2026-09-15 15:08 UTC

Game35 confirms repeated 4K image conversions/uploads between UI draws. Textures c8290000,d9ba8000,d7bb0000 each refresh3244–3534 times; their uploads total5.604s before the32768-sample cap. Still Hunter Axe loading1.1FPS. Next retain decoded native-GPU inputs under explicit write/mapping/image-content versions.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Internal GPU workload timing ready for game35 — 2026-09-15 15:03 UTC

Internal GPU timing passes6/6 focused and9 enabled fixtures, including all7 payload kinds with complete available queries. Game35 frozen from156sources for90s attribution. Child4398c9cc31d78287ba336311a107a03202ea127fdfdf5036b719ca51a551c45c. No gameplay/FPS claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game34 localizes GPU cost between UI draws — 2026-09-15 14:57 UTC

Game34 remains Top Hat loading at1.1FPS.11,778 complete GPU payload queries show44.349ms compute and102.293ms overlapping graphics intervals. Same-tick gaps total11.454s;8.504s occurs between repeated UI quad draws using VS8747a367/FS7cc2c044. Next attribute internal detile/upload/native-encode work in those gaps.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game GPU workload timing ready for game34 — 2026-09-15 14:51 UTC

Draw/dispatch GPU timing passes15/15 focused tests and7 enabled fixtures with64 complete available queries and clean Vulkan/native-byte validation. Game34 frozen from156sources for90s attribution. Child58f5ef5eaf0de58ac3c56d9a4b1c5c262203ab441f3ca082eb1c4f29c096ad16. No gameplay/FPS claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game33 rules out resident depth compute cost — 2026-09-15 14:38 UTC

Game33 remains Surgical Gloves loading1.1FPS. All511 available resident-depth GPU samples total323.346ms, with only44.962ms conversion compute and no invalid validation result. Depth conversion is not the dominant queued work. Next timestamp actual game draw/dispatch payloads.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Resident depth GPU timing ready for game33 — 2026-09-15 14:25 UTC

Resident-depth GPU timing passes18/18 focused tests and two enabled native fixtures(4valid timestamp records each). Game33 is frozen from156sources for one90s attribution run;no gameplay/FPS claim. Child6197ec16f6ef0743d3cf7307bd2e8711e8f954e5e3b2c881f5fb8c88b67dd6af.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game32 removes shader waits; depth GPU work next — 2026-09-15 14:19 UTC

Game32 removes all sampled program-prefix readback waits, but remains Tomb Mould loading1.1FPS and reports resident-depth validation timeout at166.030106s. The roughly10s wait cost moves to GPU encoding. Mixed ownership is verified, no gameplay/FPS win. Next measure GPU execution inside resident-depth conversion rather than removing another wait point.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Mixed CPU/GPU segmented copy ready for game32 — 2026-09-15 14:11 UTC

Mixed CPU/GPU segmented copy passes full292/292 Vulkan tests. Game32 frozen from156-source receipt,3 verified binaries,5586 copied sidecars and15 unchanged Timmy seed files. Next180s visible progression probe; no gameplay or FPS claim yet. Childea74dbedbdebaf36039d23321bb99b486004340a60fdc272c7844126e98064b4.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Mixed segmented copy qualification running — 2026-09-15 14:05 UTC

Mixed CPU/GPU segmented copies pass the sibling-page regression and real-GPU/shared-page/late-identity cases. All156 qualified sources and binaries are sealed; full292-test Vulkan suite is running. No game32 result yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game31 confirms independent output coupling — 2026-09-15 13:49 UTC

Game31 remains Bone Marrow Ash loading at1.1FPS. Admission trace positively identifies seven batches where the192-byte shader-neighbor output was CPU-eligible but an864-byte GPU-owned sibling on another page forced the whole batch onto GPU. Next qualify mixed CPU/GPU copies with independent native pages. No gameplay/FPS win.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CPU admission diagnostic ready for game31 — 2026-09-15 13:34 UTC

CPU admission observer passes16/16 focused tests and its enabled fixture attributes all8 GPU-neighbor batches correctly:5 segments,4 individually CPU-eligible,one GPU-owned destination. Game31 prepared from156-source receipt;90s diagnostic next. Childdc49c5e807219eed4614493c4dd9866d4c2824a8c95e7b23cf61fbfc9942ad43.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game30 CPU route active; shader-page stalls remain — 2026-09-15 13:28 UTC

Game30 still shows Tomb Mould loading at1.0FPS after180.652s. CPU route is active in1561/4096 observed batches, but34 program-prefix readbacks still wait10.254s. No end-to-end win. Next observe which segment/page blocks CPU admission for the batches touching shader code.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CPU-owned segmented copy ready for game30 — 2026-09-15 13:20 UTC

CPU-owned segmented copy passes full289/289 Vulkan tests. Game30 frozen from156-source receipt,3 verified binaries,5586 copied sidecars and15 unchanged Timmy seed files. Next180s visible progression probe; no gameplay or FPS claim yet. Child85574f304b9395226844258bd2a87ae236431007417ef0adce39960e4ec2636f.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CPU-owned segmented copy qualification — 2026-09-15 13:15 UTC

CPU-only segmented copies pass six focused Vulkan tests and an added atomic publication fixture. The red case reproduced a protected shader page; green leaves it readable and a cached GPU consumer sees fresh bytes. The full289-test suite is running. No game30 outcome yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game29 confirms CPU-sourced segmented writes share program pages — 2026-09-15 12:57 UTC

Game29 still Silencing Blank loading1.1FPS;192-byte writer is exact segmented shaderfefebf9f, not DMA/fill.37 program reads wait10.277s. Late game28 census4096batches shows all351,621,312sourcebytes CPU snapshots/zeroGPU. Next qualify atomic CPU-owned segmented publication and preserve mixed GPU route. See [bounded-copy detail](2026-09-15-vulkan-bounded-copy.md).

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Transfer attribution ready for game29 — 2026-09-15 12:44 UTC

Transfer observer passes14/14 focused tests plus enabled runtime/native-GNM DMA fixtures. Game29 frozen from153-source receipt with3binaries,5586sidecars and15unchanged Timmy seed files;90s diagnostic next. Child38a3f6591e421e44fb989df4f914faa40be6fa5a5af955a1682d8e5203a37a0c.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game28 moves wait to shared program page — 2026-09-15 12:37 UTC

Game28 still shows Pebble loading at1.0FPS after180.726s. Bounded segmented copies are active and the old fetch-code readbacks disappear, but10.263s of sampled waits move to8-byte program reads on a page also containing a192-byte GPU output. No net gameplay/performance improvement. Next identify that small transfer and its source ownership.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bounded-copy full suite passes; game28 ready — 2026-09-15 12:26 UTC

Bounded-copy full qualification passed287/287,zero skips,445.43s. Game28 frozen from153-source receipt and verified3binaries/5586sidecars/15seed files; next visible180s progression probe. Child6052d5c545058bae990fa96b2ef2318b5beb4def92a7f28ba637950322001482. No game28 outcome yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bounded copy correction; full qualification running — 2026-09-15 12:09 UTC

Bounded segmented-copy correction passes31 focused GPU checks plus an added control-dependent self-alias fallback check. Authored red reproduced an untouched shader page becoming PAGE_NOACCESS and requiring4096-byte readback; green keeps PAGE_READWRITE with zero readback. Full153-source build passed;287-test Vulkan suite is running. No game28 result yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game27 copy writer identified — 2026-09-15 12:01 UTC

Game27 identifies exact copy shader 0xfefebf9f / base 0x176ff0100 / destination sharp12 as the recurring writer of the 76,324,032-byte descriptor covering fetch code. Still Monocular loading at 1.2 FPS; no gameplay. Investigate extending the proven segmented-copy route below its current 256 MiB threshold.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game26 confirms fetch reads; correct writer observer emission — 2026-09-15 11:50 UTC

Game26 confirms fetch-shader scanning accounts for10.084s of sampled waits, and recurrent native reservations span76,319,936bytes including the slow code page. Shader identity attribution was inconclusive because its overlay selector missed full paths. Corrected emission is verified and passes4/4 focused tests; game27 is prepared for one90s diagnostic.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Shader-page owner diagnostic qualified for game26 — 2026-09-15 11:43 UTC

Shader-page owner observer passes8/8 focused regressions. Game26 is frozen from153-source receipt with3verified binaries,5586copied sidecars and15unchanged seed files;90s/8GiB bounded visible diagnostic next. No ownership or synchronization correction is claimed.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game25 isolates recurring four-byte shader readbacks — 2026-09-15 11:36 UTC

Game25 attributes10.270s of sampled waits to four-byte shader reads, mostly one recurring address. It still shows a Poison Knife loading card at1.2FPS;90.507s timeout,1431presents,89Cross pairs,unchanged Timmy seed,7,825,506,304-byte sampled peak. No renderer rejection. Gameplay and DX11 FPS comparison remain unmet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Readback request observer qualified for game25 — 2026-09-15 11:31 UTC

Readback source diagnostic passes20/20 relevant memory/shader/completion regressions. Game25 is frozen from153-source receipt, three verified binaries,5586copied sidecars and15unchanged Timmy seed files. One90s visible diagnostic follows; gameplay and FPS acceptance remain unmet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game24 batches EOP labels; CPU buffer readbacks still stall loading — 2026-09-15 11:22 UTC

Game24 removes all observed synchronous constant-label EOPs, but remains on the Shining Coins loading card at about1.2FPS. Bounded180.604s,1449presents,179Cross pairs,15unchanged Timmy seed files; sampled private peak7,590,817,792bytes. No renderer rejection or memory stop. Gameplay and matched DX11 FPS remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# PAUSED: User pause after full Vulkan qualification — 2026-09-15 04:41 UTC

PAUSED by explicit user request after suite completion. cached-label-full-suite passed284/284, zero skips,444.43s. Game24 is prepared from the152-source receipt but has never launched. Do not compile, test, launch a game, schedule work or resume automatically; wait for the user to explicitly resume. Gameplay and higher-than-DX11 FPS remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. User explicitly paused after suite completion. Await explicit resume; no tests, game launches or scheduled continuation.

---

# ACTIVE: Cached CPU label batching passes GPU ordering regressions — 2026-09-15 04:33 UTC

Cached CPU input labels now batch by native-page ownership instead of being refused solely because a buffer exists. All16 focused completion/parser/display checks pass. Authored workloads reduce65 prefixes to2 while verifying all136MiB of pixels, labels and padding. The full284-test Vulkan suite is running before game24.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game23 identifies constant-label EOP stalls — 2026-09-15 04:21 UTC

Game23 narrows the remaining EOP stalls to non-interrupt constant 32-bit and 64-bit labels. Across observed census boundaries 32.403–70.352s, 2,711 synchronous EOPs consumed 16.187s. Peak private memory was 7,818,407,936 bytes. This run did not verify gameplay.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: EOP mode diagnostic qualified for game23 — 2026-09-15 04:16 UTC

The optional EOP mode observer passes 10/10 relevant GPU/parser regressions after an all-target build. Game23 is frozen for one 90-second diagnostic with continuous Cross, neutral axes, Timmy seed copies, 2160p/cap240/AA OFF/validation OFF and an 8GiB sampled memory stop. No synchronization behavior changed.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game22 isolates end-of-pipe completion cost during loading — 2026-09-15 04:05 UTC

Game22 confirms a loading card during the slow interval and identifies EventWriteEop as the dominant completion caller. Across observed census boundaries31.302–69.637s,2347 EOP prefixes consumed15.434s CPU wall time; other prefix families totaled under0.4s. Peak private memory stayed7.872GB. Gameplay and target FPS remain unmet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion caller diagnostic qualified for game22 — 2026-09-15 03:59 UTC

Completion caller diagnostics are qualified:279/279 regressions, zero skips,442.16s. Game22 is frozen from the152-source receipt and unlaunched. One90-second diagnostic follows, with captures1180/every10/max8 and an8GiB sampled stop. Existing source and detiler memory fixes remain active.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion caller diagnostics pass GPU census checks — 2026-09-15 03:52 UTC

Optional completion-caller profiling passes ten focused regressions. Its actual GPU clock and alias cases account for exactly all 3 and 65 completion prefixes, respectively. No synchronization behavior changed. Full 279-test qualification is running from a rebuilt 152-source receipt before the next diagnostic.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game21 memory spike resolved; frequent completion waits remain — 2026-09-15 03:43 UTC

Game21 completed its 180-second diagnostic without the memory stop. Peak private memory was 7,829,262,336 bytes; later usage stayed near 7.0–7.1GB. Detiler-triggered device blocks fell to two allocations / 67,108,864 retained bytes. Presentation still runs near 1FPS. Only frame1100 was captured (title menu), so late visual state and gameplay remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Detiler scratch lifetime correction qualified for game21 — 2026-09-15 03:33 UTC

Final detiler scratch correction passes 277/277 Vulkan regressions, zero skips, in 433.24s. Game21 is frozen from the 151-source receipt and remains unlaunched. Next is one 180-second loading diagnostic with an 8GiB sampled stop threshold, continuous Cross, copied Timmy saves, neutral axes, 2160p/cap240/AA OFF/validation OFF.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Detiler scratch growth retains later submission consumers — 2026-09-15 03:26 UTC

Detiler scratch reuse passed277/277 in432.09s. Follow-up lifetime review found and reproduced a cross-submission consumer hazard during pool growth, now fixed andgreen withzero validationerrors. A fresh151-source all-target build isunderfull277-test qualification beforegame21. Gameplay remains unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Detiler scratch burst reproduced and bounded with GPU-ordered reuse — 2026-09-15 03:15 UTC

Authored detiler reproduction now remains at301.3MB peak private memory, versus4.756GB before the scratch reuse correction. It checks132 complete4K physical planes, two simultaneously held outputs, andtwo64-operation bursts without splitting submissions. Zero Vulkan validation errors. Full rebuild and277-test qualification next; game causality andgameplay remain unproved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game20 catches detiler-triggered device memory spike — 2026-09-15 03:05 UTC

Game20 allocation-time trace catches the terminal spike: private memory15,096,528,896 bytes at37.326411s, live VMA12,435,300,352 bytes. Detiler scratch requests triggered7,985,954,816 bytes of retained device blocks, including repeated256MiB blocks. Exactchild21036 stopped;37 Cross pairs and15 unchanged Timmy seed files verified. Frame1100 is a dark fading loading card, not gameplay. No FPS acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Allocation-time tracing qualified for game20 — 2026-09-15 02:46 UTC

Allocation-time instrumentation qualified by276/276 Vulkan regressions, zero skips,422.21s. Game20 frozen and unlaunched from149-source receipt. One60s diagnostic with an8GiB sampled stop threshold, continuousCross, copiedTimmy seed,2160p/cap240/AAOFF/validationOFF; captures800/every100/max8. It tests allocation attribution, not a further memory fix or gameplay FPS.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Allocation-time owner diagnostics pass actual GPU ledger tests — 2026-09-15 02:45 UTC

Allocation-time tracing now reports VMA device blocks and raw encoder/presenter allocations with process-private/working-set samples. VMA requests carry buffer/image/detiler provenance. Both real GPU allocation/free ledger regressions pass, with all recorded owners released. Full276-test qualification is running; no game20 has been prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game19 retains abrupt memory spike despite bounded conversion sources — 2026-09-15 02:27 UTC

Game19 still hits abrupt loading memory growth after the qualified source fix. The exact child was terminated at sampled12,621,340,672 private bytes, 39.119s execution, 1,108 presents and38 Cross press/release pairs. Timmy seed unchanged. The fix is valid for its authored reproduction but has not solved the actual game spike. Captures800/1000 show startup, not gameplay. No matched FPS success.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Retained source correction qualified for bounded game diagnostic — 2026-09-15 02:23 UTC

Retained source correction qualified: 274/274 Vulkan regressions, zero skips, 425.99 s. Game19 is frozen from the qualified 147-source receipt and unlaunched. One 90-second loading diagnostic next, continuous Cross, 2160p/cap240, Vulkan validation OFF and AA OFF, copied Timmy seed. Independent nominal100ms memory monitor stops the exact private child at a sampled10GiB threshold; this is not a hard allocation cap. Captures start800/every200/max8.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Retained image source pressure bounded in authored reproduction — 2026-09-15 02:15 UTC

The 64-transition reproduction now passes with peak private memory 3.232 GB, versus 7.411 GB before the fix. Completed VMA allocations fall from 74 to 10. Distinct retained image sources are bounded to 128 MiB, with positive GPU completion under pressure and cleanup at normal completion. Four focused regression families pass; full qualification is running. Actual game causality, gameplay and a matched DX11 performance comparison remain unproved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Large image transitions reproduce memory pressure inside one submission — 2026-09-15 02:01 UTC

Game18 diagnostic stopped at43.28s after private memory jumped7.47GB to20.04GB between1s samples;41Cross pairs and unchanged15-file seed. Its last allocation census at32.98s predates the largest jump, so attribution remains incomplete. New authored single-submission64-transition test reproduces peak growth2.73GB to7.41GB, exact136MiB pixels/padding, and2.11GB retained Vulkan allocations outside active cache. No gameplay or FPS success.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Full CPU texture uploads remain bounded; measure actual allocation owners — 2026-09-15 01:41 UTC

Fresh full4K CPU texture updates remain bounded:84cycles, complete native/padding oracle, private2.995GB at20 to2.994GB at84, fixed VMA/cache/retirement counts. Existing272-test production binaries unchanged. A short allocation-owner diagnostic is being prepared to measure the actual workload, bounded to90s/12GiB private memory; no gameplay or FPS acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: 272 regressions and game cache isolation pass — 2026-09-15 01:23 UTC

Allocation diagnostics and nine memory profiles pass272/272 regressions, zero skips,419.29s. Standalone preload of all107 game17 pipelines adds only19,955,712 private bytes versus an empty service; VMA remains identical. No game18. Excess execution-time graphics allocations remain the leading unproved cause; physical remap persistence and generic HLE handshake limitations remain open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Allocation lifetime families remain bounded — 2026-09-15 01:11 UTC

Allocation/retirement census is implemented for diagnostics; nine synthetic memory profiles remain bounded, not a reproduction or fix of game17 growth. New ordinary descriptor fallback and repeated mapping retirement pass. Separate physical-memory persistence control fails before GPU draws and is preserved. Full272-test qualification is next. No game18.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Focused allocation reproductions remain bounded — 2026-09-15 00:47 UTC

OPT-031 focused memory tests stay bounded; game17 growth is not reproduced. Baseline and production 276-cycle 4K reinterpretation tests pass, as do 5,376 draws, 84 CPU-page read/edit cycles, and 169 coupled depth conversions. No game18. Allocation-census work remains in progress; current test additions are not yet fully qualified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game17 loading timeout; write-combined allocation growth captured — 2026-09-15 00:21 UTC

Game17 times out at300.561s:1,560 presents, last298.102117s, no renderer rejection and no verified clinic/gameplay. Completion batching is active, but late progress stays about0.5-0.7presents/s. One capture at1400 shows black with startup overlay; it misses the late interval, so late visual rendering is inconclusive. All299 Cross press/release pairs and15 unchanged seed files verified; child51396 is gone. No game18.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion batching qualified; game17 frozen for progression test — 2026-09-15 00:08 UTC

completion-qualified-build passes all263 regressions, zero skips, in372.03s. Game17 is frozen and unlaunched: child6c33069c5eb1373e7a7cf159b093b4261e5655ec31def3120bca07987385f629,146 matching source hashes,5,586 verified sidecars and15 unchanged Timmy seed files. OPT-030 implemented at the tested renderer scope; one300s visible progression run next, AAOFF/4K/cap240.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Native completion handshake passes; HLE mid-submission read remains open — 2026-09-15 00:00 UTC

completion-family-final passes8/9; the added HLE-read handshake child times out at20.22s. That fixture calls the generic HLE read API, which waits for the whole accepted submission. A separate native x86 load/store handshake passes completion-native-handshake1/1 in1.94s with exact136MiB output,64 deferred labels and protected GPU pages. Full68-target completion-qualified-build is running; no game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion family passes; CPU handshake stall reproduced and fixed — 2026-09-14 23:56 UTC

Completion GPU family passes8/8 in11.24s: ordinary batching, future GPU consumer, cached buffer alias fallback, late budget rejection, interrupt ordering and clocks, plus both CPU parser contracts. A prospective CPU handshake then reproduced a stall in completion-handshake-red (0.93s); publishing queued labels before an unsatisfied WAIT fixes it in completion-handshake-green (0.12s). No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: First GPU completion batching case passes after reproduced barrier cost — 2026-09-14 23:42 UTC

completion-gpu-red reproduces65 prefix barriers for64 real GPU writes/96 waits:32.6771ms, correct full136MiB output, protected pages and actual CPU fault behavior. After enabling conservative coherent eligibility, completion-gpu-trial passes3/3 in2.10s:22.0169ms,64 deferred writes,96 logical reads,1 batch and1 submission-prefix barrier. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion journal CPU ordering and failure family passes — 2026-09-14 23:38 UTC

completion-journal-family passes both facade/imported-parser CPU tests in0.22s. The actual parser now handles64 EOP writes/96 waits with2 prefix barriers,64 queued writes,96 logical reads and1 batch. Game runtime batching remains disabled pending GPU-family qualification. completion-gpu-red-build is building the real64-dispatch/96-wait fixture and runtime consumer guards; no game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Completion-barrier multiplication reproduced in imported parser — 2026-09-14 23:22 UTC

completion-imported-red reproduces66 prefix barriers for64 non-interrupt EOP writes plus96 ordered PM4 waits in0.13s, using the actual imported parser without a GPU. Data/padding and job completion pass; the batching requirement fails. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Layout cache qualified; test-address underflow corrected — 2026-09-14 23:17 UTC

Immutable layout cache is implemented and qualified across256 distinct regressions: full suite255/256 in359.28s plus corrected shader fixtures2/2 in5.09s, with production source/binaries unchanged. The full-run failure was a test tail-address underflow; its immediate unchanged-binary rerun passed, and controlled low-base arithmetic reproduces malformed stride/flags. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Immutable layout reuse qualified in focused family; completion waits attributed — 2026-09-14 23:10 UTC

layout-cache-family passes24/24 in53.39s. The same32 full4K transitions drop from3494.89ms/32builds to108.49ms/0builds/32hits, with848cached metadata bytes, full native oracles, no transition pixel readback and stable memory. All68 targets rebuilt; full256-test suite is running. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Repeated4K layout cost reproduced; memory stable in fixture — 2026-09-14 22:57 UTC

layout-repeat-red reproduces repeated static layout work without another game: 32 full4K CMASK transitions take3494.89ms and rebuild32 identical plans. All35 GPU generations, full136MiB pixels/metadata/padding and exact4KiB CPU publication pass; the reuse assertion correctly fails. Private memory stays near2.79GB and encoder storage66,600,992bytes/pending outputs8 stay fixed. This fixture does not reproduce game16 memory growth. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game16 times out loading; plan cost and memory pressure recorded — 2026-09-14 22:43 UTC

Game16 reached the300s limit while loading:1,454 presents, last289.605549s, entry_timeout301.658s. Frame1400 shows Top Hat loading at0.6FPS/1682.2ms, AA OFF. No renderer rejection was logged, but the run ended before game15 reached1,475 presents; progression beyond its exact blocker is unproven. All299 Cross press/release pairs and15 unchanged Timmy seed files verified. Child10016 is gone. No game17.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game16 active; loading remains slow — 2026-09-14 22:35 UTC

Game16 is running once in session20260914T223159-3190ea82 (verified child10016). At98.165s it had1,339 presents and no renderer rejection; later loading progress is very slow, with no planned1400 capture yet. This is not gameplay or performance acceptance. The bounded session is300s, AA OFF, captures1400/interval100/max8. Inspect new CMASK diagnostics and captures before any further launch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK qualified; game16 frozen — 2026-09-14 22:31 UTC

cmask-qualified-build-3 passes the full255/255 regressions with zero skips in367.11s. Game16 is frozen and unlaunched: childcc05c4a5ab826ce8d17413894b5bb6d2a55a71c1a3446aa618ab8413c2e6686c,145 verified source hashes,5,586 sidecars and15 unchanged Timmy seed files. CMASK GPU conversion, ownership reuse, invalid-content rejection and complete failure diagnostics are qualified. One300s visible progression run next; AA OFF,2160p/cap240, captures1400/interval100/max8. No gameplay or performance success yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK failure evidence verified; final full run active — 2026-09-14 22:26 UTC

cmask-qualified-build-3 rebuilt all68 targets and recorded145 source hashes. cmask-diagnostic-trial passes: every invalid tag reports exact tile2/tag, both buffers and padding remain unchanged, and only16 status bytes return after positive completion. cmask-final-suite-3 is running on these binaries. The preceding build passed255/255; that is not substituted for final-build qualification. No game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK full suite passes; complete failure diagnostics next — 2026-09-14 22:22 UTC

cmask-final-suite-2 passes255/255 with zero skips in365.53s, including the unchanged empty fast-clear regression and adjacent4K metadata placement. Before launch, an additional diagnostic packs the rejected tile and tag into the existing16-byte validation result and logs the original CMASK descriptor on all failures. The direct all16-tag contract now verifies the exact reported tile/tag; this logging revision still needs its own build and qualification. No game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Empty fast-clear regression corrected; adjacent layout passes — 2026-09-14 22:15 UTC

cmask-empty-fce-family passes22/22 in49.80s, including the unchanged ten-draw depth empty-probe contract, all20 coherent CMASK profiles and the all16-tag direct encoder test. The new adjacent4K case uses the game15 placement: CMASK immediately after33,423,360 native color bytes. Real metadata remains GPU-validated; only the explicit address0 empty FCE returns before acquisition. Full68-target rebuild and full255-test rerun next. No game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Full suite catches empty fast-clear probe regression — 2026-09-14 22:12 UTC

cmask-final-suite passes253/254 in363.06s; the unchanged depth_empty_fast_clear_probe regression fails. A non-null64x64 linear color target with fast_clear=1 but CMASK address0 is an explicit empty probe. The new handler incorrectly began an output operation and rejected its absent metadata. Restore the no-resource early return for address0 only; nonzero CMASK remains GPU-validated. No game16 prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK clear, ownership and rejection family passes — 2026-09-14 22:04 UTC

cmask-qualified-family passes20/20 GPU tests with core/synchronization validation in43.51s. Coverage now includes mixed clear/expanded tiles, CPU metadata publication followed by disjoint same-page GPU ownership, explicit fast-clear elimination, RGBA16F/RG32F, real shader metadata aliases and rejected flags/extents. The direct encoder verifies all16 tag codes and complete unchanged color/metadata/padding for all14 invalid codes. Full68-target build and full254-test qualification next. No game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK GPU expansion passes reproduced family — 2026-09-14 21:52 UTC

cmask-first-candidate passes all 8 reproduced CMASK cases with core/synchronization validation in 20.51s. Three complete GPU generations are retained in GPU snapshots and verified by the final 136MiB byte oracle; native transitions perform no pixel readback, and the actual CPU fault publishes exactly 4KiB. This is focused qualification only. Mixed tiles, CPU metadata edits, explicit fast-clear commands and rejection/lifetime cases remain before another game. No game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: CMASK color failure reproduced across eight GPU cases — 2026-09-14 21:22 UTC

cmask-corrected-family-red reproduces CMASK admission failure in all8 GPU renderer cases on unchanged game15 production (14.75s): seven stop at output-layout admission and the mode10 display-layout case at its input-layout guard. The set covers4K clear/expanded inputs, half/quarter/small dimensions, SRGB, mode10 and padded edges. No CMASK production correction or game16.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game15 color-metadata rejection during loading — 2026-09-14 21:02 UTC

Game15 FAILED at127.124895s: 3840x2160 RGBA8 mode14 color output with CMASK was rejected. 1,475 presents; last125.281353s. Capture1400 shows Small Resonant Bell loading at1.9FPS/560.3ms, AA OFF; it misses the terminal interval by75 presents. No clinic or responsive gameplay. Captured65 command buffers (1,197,424bytes), then stopped the verified child51952. Parent178.304s entry_fault;177 Cross press/release pairs; all15 seed files unchanged.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Resource preparation qualified; game15 frozen — 2026-09-14 20:56 UTC

binding-qualified-build rebuilt all 68 targets; binding-final-suite passes 234/234 with zero skips in 319.50s. Operation-wide buffer preparation and simultaneous read-only GPU image interpretations are qualified together, including real conflict rejection. Game15 is frozen and unlaunched: child 5894456981b565245af5964d08a28e2b0791efaed698b327a73ab03615b44524, 140 source hashes, 5,586 verified sidecars and 15 unchanged Timmy seed files.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: GPU image aliases and writer conflicts pass — 2026-09-14 20:51 UTC

Concurrent image interpretations pass both positive GPU cases and both read/write conflict orders. binding-image-reads-trial passes 2/2 in 4.78s; binding-image-conflicts-trial passes 2/2 in 4.35s. The full 234-test suite is running against the rebuilt 68 targets. No game15 has been prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Early alias guarantees restored; concurrent image-view failure found — 2026-09-14 20:40 UTC

binding-full-suite222/230 in317.46s: eight legacy alias tests failed at the changed rejection message before their remaining assertions. Early logical-range declaration restored; binding-early-alias-selected now passes those8 unchanged tests and all12 buffer/depth/indirect cases. A prospective two-stage image-view test fails at late bound-image replacement. No game15.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Complete binding-order family passes before another game — 2026-09-14 20:26 UTC

All12 backing-order renderer tests pass in27.46s, with complete136MiB byte/padding oracles and core/synchronization validation. Cases cover left/right stage growth, CPU and GPU inputs, index/fetched vertex buffers, direct/indexed/counted indirect draws, indirect compute and coupled depth/stencil/HTile sharing a physical allocation. Full68-target build passes; full230-test suite running. Game15 has not been prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Operation-wide resource preparation passes coherent sweep — 2026-09-14 20:18 UTC

Operation-wide preparation passes the five focused binding tests and all48 coherent regressions (124.99s), including true image aliases and invalid depth/metadata/edge rejection. New indirect/fetched-vertex siblings are being validated before full qualification. No game15.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Bound-allocation failure reproduced; control ordering corrected next — 2026-09-14 20:01 UTC

binding-family-red reproduced the game14 lifetime guard in4/5 renderer cases; the disjoint image-growth case passes. No production correction or further game launch. The planned reverse control was incorrectly shaped: LogicalStage visits Fragment before Vertex, so it also grows a held allocation to the left. Correct the control and isolate index growth before fixing operation-wide preparation.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game14 loading failure: late bound-buffer growth — 2026-09-14 19:47 UTC

Game14 FAILED at135.276516s: Vulkan late alias growth would replace an already bound buffer.1349 presents; last133.150774s. The inspected1300 capture shows Kirkhammer loading at1.8FPS/523.1ms, AAOFF; it misses the terminal interval by49 presents. No clinic or responsive gameplay. Verified child34300 was captured and stopped; parent215.701s entry_fault,214Cross press/release pairs, all15 seed files unchanged.

Reproduce late native backing growth within one operation, including multiple shader buffers and depth/image reservations, before another launch. Preserve bound handles and GPU pixels; do not merely remove the lifetime guard. Game15 is not prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Depth-only HTile qualified; game14 frozen — 2026-09-14 19:40 UTC

depth-only-full-build rebuilt all68 targets. depth-only-full-suite passes218/218, zero skipped,290.44s. The optional-stencil depth/HTile converter and its9-case GPU family are qualified together with existing regressions. Game14 is frozen and unlaunched: child256a69faceaedad985f3939a29db71b8246af7144475edcb0210b4de9ec1e147,139 source hashes,5586 verified sidecars and15 unchanged Timmy seed files.

One300s visible run next, validationOFF for the normal driver path after validated tests, AAOFF,2160p/cap240. Capture first1000 then every100/max8; worker cost window60..90s. No clinic, responsive gameplay, AA integration or matched gameplay performance acceptance yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Depth-only HTile GPU family passes — 2026-09-14 19:33 UTC

depth-only-family-trial passes all9 cases in19.63s with core/synchronization validation. The recovered4096x4096 Z32-only HTile family and2048/quarter/small/hint/stencil variants preserve complete136MiB fixtures, metadata/padding and GPU edits; actual CPU faults publish exactly4KiB. Invalid NaN/metadata/shared-edge cases reject without stale publication or false EOP. This qualifies renderer behavior, not game13 attribution or gameplay performance. Full rebuild/suite follows; no game14 yet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: GPU work resumed for HTile validation — 2026-09-14 19:31 UTC

The user explicitly resumed work. GPU tests and the next qualified game run are authorized again. Verified Uptownfrog, protected hooks, push.default, HEAD, all139 candidate source hashes and all3 player hashes against the pause receipt. Run the nine new HTile cases and related depth regressions, then qualify the full suite before game14. No game14 is prepared or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# PAUSED: Depth-only HTile candidate compiled; GPU validation paused — 2026-09-14 17:48 UTC

PAUSED at the user's request while they play Dota. No GPU tests, game launches or automatic resume until the user explicitly resumes. The depth-only HTile candidate compiles; its GPU behavior is unverified. Game14 is not prepared or launched.

`depth-only-family-red` reproduced the base HTile rejection in all9 authored renderer cases (18.64s) on game13 production. `depth-only-cpu-build` regenerated all9 overlays and compiled the three players plus coherent/HTile contracts with2 workers (117.48s). CPU-only `depth-only-cpu-htile` passes1/1. OPT-023 remains in progress. All15 seed files are unchanged.

On resume: run the nine HTile renderer cases and existing coupled/quarter/depth validation cases, fix any failures, then rebuild all68 targets and run the full suite before preparing game14. Clinic rendering, responsive Timmy gameplay, AA integration and matched gameplay performance remain unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. GPU work paused by user request while they play Dota. Do not test, launch, schedule or resume automatically; wait for explicit user resume.

---

# ACTIVE: Game13 loading failure; HTile metadata captured for renderer reproduction — 2026-09-14 17:24 UTC

Game13 FAILED128.212782s: Vulkan HTile requires a proven base Z-only layout.1447presents,last128.105870s. Owned1400 capture shows Hunter Blunderbuss loading2.0FPS/481.8ms AAOFF, misses terminal interval. Verified child40420 stopped;258.764s entry_fault,257Crosspairs,15 seed files unchanged. No clinic/gameplay.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Macro GPU array/mip family qualified; game13 frozen — 2026-09-14 17:14 UTC

Macro array/mip family qualified: exact game12 six-layer case, odd arrays, cube/array chains and1x1 tails retain GPU pixels;4KiB CPU faults exact. Full208 passes plus corrected obsolete CPU test1/1 give209 qualified tests. Game13 frozen, unlaunched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-12 macro array/mip family reproduced before another launch — 2026-09-14 16:55 UTC

Macro family reproduced: exact game12 six-layer descriptor and all8 prospective array/mip cases reject; encoder plan rejects. Production correction pending; no game13.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-12 exact macro cube input failure — 2026-09-14 16:40 UTC

Game-12 FAILED126.897189s: macro-tiled input mip/layer admission. Exact descriptor addr0xa4350000,1572864bytes,256x256,pitch/physical_h256,VkFormat83,raw5/7,32bits,type9,1level,6layers,mode14,swizzle0,no metadata/depth/block/volume.1272presents,last126.817001s. Owned1175 capture shows Hunter Pistol loading1.7FPS/578.9ms AAOFF, misses terminal interval. Development validation was OFF; zero VUIDs is not validation evidence. Stopped verified child18584; parent198.382s entry_fault,197Crosspairs,15 seed files unchanged. No clinic/gameplay.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-12 qualification and normal driver experiment — 2026-09-14 16:34 UTC

fragment-full-build68 targets; fragment-full-suite200/200 PASS,0 skipped,249.24s with core/sync validation. Game-12 frozen child6149d5bcb10e880903089b179498f27c38c0b560f47f7e90047d4acd51cb4548;137 source hashes,5586 verified sidecars,15 unchanged Timmy seed files. One300s visible run next. GPU transfer fragmentation and prospective fragmented-image failure corrected and fully qualified. BB_VULKAN_VALIDATION=0 for the normal driver path; renderer bounds,ownership and completion remain active. OPT019 in progress; no matched on/off or gameplay-performance claim. Captures825/interval50/max8 and60..90s worker cost window;AA integration remains pending.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: GPU transfers and fragmented image family qualified — 2026-09-14 16:28 UTC

fragment-combined-green44/44 PASS. Independently reproduced fragmented source,destination,both backing failures now use bounded GPU copies across2/3 physical regions; partial-page gap passes. Prospective cross-backing image failure was reproduced before another launch and fixed by GPU joining when an image converter requires one buffer. Complete320MiB native bytes, zero transition readback,4KiB CPU publication, mapping retirement and core/sync validation pass. Full68-target rebuild and complete suite next. No game since failedgame11.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Fragmented image backing reproduced before another launch — 2026-09-14 16:25 UTC

fragment-copy-green4/4 passes with2 physical regions for fragmented source/destination and3 for mismatched boundaries; missing-page control passes. Broader fragment-image-red fails before copy: a128KiB image across two64MiB native backings reports Vulkan resident image lost its native GPU backing. This prospective sibling gap was found in renderer tests before another game launch. GPU ownership coverage alone does not prove one contiguous buffer.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Fragmented GPU transfers reproduce game-11 failure — 2026-09-14 16:21 UTC

fragment-family-red reproduces the game11 backing rejection in3/4 renderer cases: fragmented GPU source,destination,both fail; partial-page gap positive passes. Each authored case retains320MiB of native bytes. No launch sincegame11. Implement bounded transfer splitting at physical source/destination backing boundaries, then qualify all copies/zeros/lifetimes.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-11 loading failure and GPU backing evidence — 2026-09-14 16:17 UTC

Game-11 FAILED132.715308s: Vulkan segmented copy needs a backing merge, phase3/attempt652 after651 committed batches.1020presents,last132.699674s; loading1.8..2.0FPS AAOFF. Owned875/975 captures show Powder Keg Hunter Badge loading;975 misses the terminal interval. No VUID. Stopped verified child12056 after failure; parent212.724s entry_fault,211Crosspairs,15 seed files unchanged. No clinic/gameplay. Reproduce fragmented source/destination backings and partially present pages before another launch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-11 combined semantic qualification — 2026-09-14 16:10 UTC

lane-full-build rebuilt68 targets; lane-full-suite195/195 PASS,zero skipped,239.17s. Game-11 hash-frozen with137 source hashes,5586 unchanged sidecars and15 unchanged Timmy seed files. Child27104d9ef4a34dd947b0741d55807cbe6c9892c48c479fb57b0e2234e447e1d6. One300s visible run next; active-range aliases and original-shader lane/clip/zero/wrap semantics qualified together. Validation remains enabled. Captures825/interval50/max8; worker cost window60..90s. No clinic,movement,AA or gameplay-performance acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Original GPU shader copy semantics qualified — 2026-09-14 16:04 UTC

lane-family-green passes26/26 in34.86s. The original translated GPU shader independently passes16 lane/mask/clip/zero/wrap byte cases; specialized path reproduced rejection at last=64, then passes all16 with GPU copies/fills and zero transition readback. Shared304MiB backing, maximum logical capacities, actual-alias negatives,1,025-group mixed zero/copy and16,384-group terminal-overlap all pass. Full68-target rebuild and complete suite next; no game since failedgame10.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Resumed after Dota — 2026-09-14 15:55 UTC

User explicitly resumed work. GPU tests and the next qualified visible game run are authorized again. Current source: active-alias-green27/27; full193 suite predates active-alias changes. Audit original segmented shader lane masks, clipping and indexed arithmetic with GPU byte oracles before correction/full qualification. Game10 remains failed; game11 is neither frozen nor launched. No gameplay/AA/performance acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Paused for Dota at GPU validation boundary — 2026-09-14 14:36 UTC

PAUSED at user request while they play Dota. Do not run GPU tests or Bloodborne, resume automatically, or schedule work; wait for the user to say resume. Last actual run game10 FAILED at33.029478s on whole-descriptor alias rejection. Subsequent active-alias-green passes27/27 in34.35s: GPU copies within shared304MiB backing, maximum logical descriptor capacities, active-overlap negatives and segmented families. Latest full suite193/193 predates these active-alias changes; full rebuild/suite and gameplay remain pending. No game11 is frozen or launched.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-10 descriptor-domain overlap failure — 2026-09-14 14:23 UTC

Game-10 FAILED33.029478s: segmented whole-descriptor alias guard,773groups and matching773 controls;833presents. Exact source0x12a4d0460/0x13ed0 records, controls0x12a4108c0, destination0x801d3b40/0x2fa9a2b4 records. No actual control values captured. Frame800 shows menu/checking-save-data40.6FPS AAOFF; misses terminal interval. Stopped verified child after failure; parent121.395s entry_fault,120Crosspairs,seed unchanged,0VUID. Cost window never began; performance effect inconclusive. No next launch until active-range alias and broader admission audit.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-10 qualified launch — 2026-09-14 14:18 UTC

padding-empty-full-suite193/193 PASS,0 skipped,229.85s after68-target rebuild. Game-10 frozen child9b0dbbe8ebeb13a3144f3634701ed994e0a96cfbbc8c7adebe04415df90cc4c7;136 source hashes,5586 verified sidecars,seed unchanged. Exact ignored-padding family and empty completion optimization qualified. One300s visible run next, first capture800/interval200/max8, slow-window profile60..90s worker time. Clinic/movement/AA/gameplay comparison unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Descriptor padding and empty completion family — 2026-09-14 14:13 UTC

game9-padding-green3/3 and empty-finish-family38/38 pass66.96s. Exact ignored-padding failure fixed across1024 variants plus147 semantic negatives and real312-group GPU byte/EOP oracles. Empty completion calls no longer submit new GPU work; blocked prior work, callbacks, rendering-only, explicit semaphores and cancellation remain correct. Full rebuild/suite follows; no game since failedgame9.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-9 exact descriptor failure — 2026-09-14 14:00 UTC

Game-9 FAILED at134.026573s: exact segmented descriptor padding rejection (source/destination0xb0);913 presents, loading~1.6..1.7FPS,300.653s timeout,299Crosspairs,seed unchanged,0VUID. Captures500/750 miss failure. Reproduce full ignored-padding family and investigate completion waits before another launch. No clinic/gameplay/AA acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: 189 renderer tests pass; game-9 frozen for progression and slowdown check — 2026-09-14 13:50 UTC

189/189 tests pass after game-8 backing/ticket and publication-cost reproductions. Game-9 frozen for one300s visible run with copied Timmy seed, later frame captures and a late cost window. Clinic/movement/AA/performance remain open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-8 backing rejection and disjoint-publication work reproduced — 2026-09-14 13:41 UTC

Both remaining game-8 work items have renderer reproductions:304MiB selected-backing refusal, cross-token destination authority, and1,048,576 copies/scans for2,048 disjoint CPU reads. Implement and qualify together before another game.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-8 restores loading graphics but retains slowdown and fails segmented backing admission — 2026-09-14 13:27 UTC

Game-8: startup/loading graphics restored;~1.1FPS remains.873presents,selected segmented backing-capacity rejection176.718791s,timeout180.635s;seed unchanged. Late profile identifies11.2s/30s buffer-publication overhead and7.27s scheduler wait. Reproduce these and large-backing segmented interaction before any next launch; no clinic/movement/AA/performance acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: 186 renderer tests pass; game-8 frozen for combined regression check — 2026-09-14 13:21 UTC

186/186 renderer tests pass after independent pixel, ownership-cost and native-growth reproductions. Game-8 hash-frozen; one180s visible Timmy run next, late cost window and early/late frame capture attempts. Gameplay, AA and matched performance remain open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: GPU backing growth and boundary-crossing images qualified — 2026-09-14 13:15 UTC

native-growth-family31/31 passes;304/832MiB GPU backing, cross-token image,4KiB CPU read and full native bytes verified. Three shader-semantics fixes and ownership scaling also pass. Full rebuild/suite next; no game since failed game-7.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Overlapping bounded GPU buffers reproduce range rejection — 2026-09-14 13:06 UTC

native-growth-red independently reproduces the range rejection with six valid64MiB overlapping descriptors (304MiB envelope). Fix and qualify bounded ownership plus shared GPU backing before any game launch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: GPU pixel semantics and ownership scaling qualified; game-7 still failed — 2026-09-14 13:02 UTC

Three typed/native wrong-pixel regressions fixed in renderer tests; ownership pair scan removed. ownership-scale-green29/29 passes; no in-game claim. Game-7 gray/slowdown/range failure still requires validation. Next: overlapping native allocation-growth regression, full qualification, then a single instrumented launch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Three wrong-pixel shortcut cases reproduced without another game — 2026-09-14 12:46 UTC

Renderer-only gray investigation reproduces three wrong-pixel defects in unproved compute copy/clear shortcuts: arithmetic omitted, native tiling changed and a non-clear shader replaced by clear. Red tests2/2 plus1/1 fail on unchanged product; mixed color/depth and explicit metadata tests pass, so those are inconclusive for game gray. Fix executes original GPU shaders; no game launch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-7 gray regression and sustained slowdown; renderer-only investigation — 2026-09-14 12:29 UTC

Game-7 FAILED visually: user reports gray throughout; owned frame830 confirms gray at1.0FPS/928.9ms,AAOFF. 888 presents; sustained~1.1FPS after~40s; buffer-range rejection at173.939588s, then180.693s timeout. Seed unchanged,179Crosspairs. Full178-test pass did not establish correct game rendering. No more game launches until renderer reproductions; gray image and slowdown take priority. Cost trace ends44.693s and misses late slowdown; failed range tuple is absent.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Full178-test Vulkan suite passes; frozen game-7 progression attempt next — 2026-09-14 12:19 UTC

Full178/178 Vulkan regressions pass,0 skipped,203.21s,after67-target rebuild. Frozen game-7 childd8ce059f is ready for one visible Timmy progression run. Scaled segmented copies and coherent image/source/destination transitions are qualified; game-6 remains failed and its exact dispatch predicate unproven. Gameplay and matchedAA/FPS acceptance remain open.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Segmented dispatch family and coherent copy transitions qualify; full regression suite running — 2026-09-14 12:15 UTC

After game-6, broader segmented red/green qualification passes23/23 (40.13s):1,025 sparse and4,096/16,384 contiguous groups, exact native/gaps/GPU-source oracles and invalid-final-control rejection. A separate coherent test reproduced pending-image source rejection; source and previously GPU-written destination now stay on GPU with zero transition readback. All67 targets rebuilt; full178-test suite running. No new game, clinic or FPS acceptance. Idea statuses/evidence updated in docs/optimization-ideas.md.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-6 reaches a later segmented-copy restriction; broad renderer reproduction next — 2026-09-14 11:57 UTC

Game-6 FAILED at86.103629s: segmented-copy dispatch subset refusal, after passing game-5 time/frame frontier. resident-build-23; session20260914T115127-1cf54d31;86.772s,85Crosspairs,seed unchanged,0VUID. Last owned capture730 isgray/AAOFF and misses fatal interval; clinic/movement/FPS unverified. Exact failed dispatch tuple absent; source/test reproduction precedes another launch. New docs/optimization-ideas.md tracks to do/in progress/implemented/rejected with evidence and rejection reasons.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# PAUSED: Paused by user after174/174 passes; game-6 ready but unlaunched — 2026-09-14 04:14 UTC

PAUSED at user request. resident-build-23 / full-suite-2 passes174/174,201.06s,0 skipped. Game-6 prepared but NOT LAUNCHED. Last actual game-5 failed before clinic at~32FPS/AAOFF. Full tomorrow prompt: recipient docs/checkpoints/2026-09-14-vulkan-resume.md; private pause-state.json contains hashes. Do not resume, launch, or schedule work until the user returns.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. User requested stopping after the completed regression run. Await explicit user resumption; game-6 remains unlaunched.

---

# ACTIVE: Scratch pressure and broader depth routing qualified; final rebuild active — 2026-09-14 04:07 UTC

False scratch budget refusal reproduced and fixed; queued/completed growth7/7 passes without pixel readback. Broader coupled depth sizes qualify; adversarial fixture precondition corrected. GPU buffer->3D LUT route already passes, new regression added. Depth layout tables now cached in VRAM; complete build23/174 suite pending. No new game since failed game-5.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-5 stops at native GPU conversion; deterministic pressure audit next — 2026-09-14 03:46 UTC

Game-5 FAILED at36.122s on resident image-to-native conversion (missing status/shape detail);699 native presents,180s bounded run,seed unchanged,0VUID,AAOFF. Deterministic allocation/layout tests and diagnostics precede any further game launch. Previous174/174 remains functional coverage, not gameplay proof.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Complete Vulkan regression suite passes; one qualified game test next — 2026-09-14 03:40 UTC

Full174/174 Vulkan suite passes on resident-build-20 (child e8073825). Qualified transitions keep GPU pixels; CPU reads publish4KiB pages; coupled depth retains16B validation/wait. Broad batch now ready for one instrumented game-5 progression run. No gameplay/FPS acceptance yet; all earlier failures and artifacts preserved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Resident transition and adversarial tests pass; full regression build next — 2026-09-14 03:26 UTC

All6 coherent/adversarial fixtures pass after stencil barrier and disjoint-binding fixes. Color/buffer/mip/depth transitions retain GPU pixels; CPU reads publish requested pages; coupled depth reads16 validation bytes per conversion. Invalid depth/HTile/edge cases reject without false completion. Full174-test rebuild is next. No game launch since game-4.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Page-sized CPU reads and coupled depth GPU conversion qualified; stencil validation active — 2026-09-14 03:13 UTC

Actual CPU pixel reads now transfer4KiB, not32MiB. Coherent4K/quarter Z/S/HTile transitions pass with GPU planes and16-byte validation results. Stencil-only testing found ignored-control classification and oversized S8 barriers; fixes are being qualified. No game launch since game-4.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Mips, growing buffers and standalone depth transitions qualified — 2026-09-14 02:39 UTC

Coherent mips, ordinary buffer growth, D16 layers1..64 and D32/buffer transitions now pass3/3 full fixtures with zero transition readback. The initial D16 oracle missed bank rotation; corrected and verified. Page-sized real CPU readback is being qualified; coupled HTile still needs work. No new game or performance acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Color aliases and reciprocal GPU transitions qualified; coherent mip work active — 2026-09-14 02:26 UTC

Color aliases and image/buffer transitions pass real coherent tests with zero readback; tests6/6 then25/25. A separate coherent mip snapshot bypass was found and repaired, awaiting its new regression. Depth/HTile still under audit. All compile failures retained. No game launch since failed game-4; no FPS/gameplay claim.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Broad format batch qualified; GPU transition ownership work started — 2026-09-14 01:51 UTC

No game launch since game-4. Broad batch built:171 Vulkan cases covered by169/171 plus two exact-counter corrections passing; new general texture reuse format/LUT tests3/3. Latest user explicitly requires all possible resource transitions to remain GPU-resident. Implementation of shared native-layout GPU ownership is active; current tested game4 stillfailed and clinic/FPS unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Broader Vulkan batch: alias and format cases qualified; LUT oracle corrected — 2026-09-14 01:06 UTC

Broader no-game batch passes37/38: generic pending image replacement, exact HDR shapes, buffer-to-mip ordering, typed mips and D16 GPU routing. D16 performance regression fixed; wide texture range limit expanded with exact padding preservation. Remaining LUT test failure traced to its linear-output pitch oracle and corrected, awaiting qualification. No game launches; no gameplay/FPS acceptance. See detailed checkpoint and renderer-reassessment private evidence.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Game-4 passed R8; game launches paused for D3D11 coverage audit — 2026-09-14 00:38 UTC

Game-4 passes R8 but stops at471x397 HDR target admission. User asked to pause repeated game launches for a broader D3D11 comparison and fixes. Five parameterized HDR shapes reproduce the failure in unit tests; build-12 still needs ingress repair. Audit now targets generic pending-image replacement, buffer/mip transitions, 3D LUT coverage, depth restrictions and remaining GPU/CPU transfers. No more game runs until a broader qualified batch.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Typed color mip chains qualified; game-4 prepared — 2026-09-14 00:17 UTC

Build-11 and all23 typed-mip/coherent/display/encoder tests pass. Exact game-3 R8 loading layout is now qualified, plus broad ordinary formats and small mips. Failed view/GPU-path qualification attempts retained. Frozen game-4 visible Timmy run next; gameplay and matched FPS still unverified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Combined Vulkan game-3: display works, R8 mip chain blocks loading — 2026-09-13 23:58 UTC

Game-3 (session 20260913T234907-31c68c4b): protected GPU display is now visually verified (~30 FPS startup, zero full display-source snapshots), but loading FAILED on R8 UNORM64x64 mode13 two-mip support at37.178s. Last native frame498; no clinic result, AAOFF. Build-8 now implements ordinary color element widths plus byte/halfword encoder packing; actual multi-format mip tests pending. Seed unchanged; see linked detail and game-3 evidence.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Protected Vulkan display and typed-buffer transitions qualified — 2026-09-13 23:48 UTC

Protected GPU display and typed image/buffer reads now pass the actual renderer fixture through complete swapchain pixels and full native memory/padding, zero VUIDs and no full display-source readback. Six focused checks pass. Game-3 frozen, live test pending; prior game-2 remains failed, not a performance result.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Combined Vulkan game-2: typed image reads and display admission gaps — 2026-09-13 23:43 UTC

Game-2 (combined-build-6, session 20260913T233412-176e13cf) FAILED: user-visible freeze, only two CPU fallback frames actually presented. GPU-owned frames were prepared but rejected by the old CPU-version proof guard. Loading advanced past prior error, then hit unconditional GPU-image/texel-buffer-read refusal at 35.830185s. No FPS improvement established. Build-7 repairs both gaps and adds full swapchain pixel and typed-buffer regression coverage; validation pending. Timmy seed unchanged. See linked detailed checkpoint and game-2/analysis.json.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Combined Vulkan game run failed: producer transition and per-flip readback — 2026-09-13 23:29 UTC

Combined-build-4 game-1 FAILED (session 20260913T231346-fab02563): user-confirmed loading freeze, last present 417, renderer error at 57.963182s: non-HTile image producer overlap. No performance improvement; startup progression worsened. Full per-flip RAM publication defeated GPU retention. Build-5 repairs sequential cross-cache writes and coherent flip visibility; qualification pending. Seed unchanged; detailed evidence and revisit conditions appended to linked checkpoint.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Combined renderer fixes qualified; first coherent game run — 2026-09-13 23:12 UTC

Combined build passes46 focused +30 broader regressions and the real coherent GPU test: six4Kdraws/fourGPU-owned surfaces/zero readback; one native read publishes only its producer. Actual dispatcher1496cases pass. EOP/EOS eager download bug fixed. First combined Timmy game-1 prepared180s; VulkanAApending means no matchedFPSclaim. All failed/inconclusive artifacts retained; no commits/pushes.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Renderer reassessment: coordinated implementation underway — 2026-09-13 22:40 UTC

All renderer fixes are being implemented as one coordinated change. Actual authored exception dispatcher passes136 register/red-zone cases; failed RSP-only approach recorded. Full source/players backed up. Combined compilation, expanded native/mip/cache/lifetime checks and visible Timmy game validation remain. Evidence: private/perf-lab/renderer-reassessment-20260913-v1. No commits or pushes.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Exact storage mip1 output qualified; next visible game attempt — 2026-09-13 18:43 UTC

V3n passes baseline-red/green mip1 validation: actual writes and later sampling of mip1, preserved late mip0 edits, full native/EOP/owners and three refusal cases. Four conditional cases and quarter/packed regressions also pass,0VUID. Next visible run tests game progression and cache pressure. DMA stays off; no pushes; performance targets still unachieved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V47 proves conditional stores but exposes display history churn; mip1 qualification next — 2026-09-13 18:34 UTC

V47 actualconditional samples omit298.6MB via9unchangedmode14outputs, butall11mode10samplesmiss among3displaytargets with2historyslots. NoFPSgain/30gameplayproof.26.649s/439presents/25Crosspairs,seedunchanged,0VUID;freshf410title21.1FPS/AAOFF. Fix measuredhistorychurn withinbudget whilequalifyingactualmip1 continuation; DMAOFF/no pushes.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Conditional 4K color stores qualified; V47 measures actual game eligibility — 2026-09-13 18:30 UTC

Conditional stores pass actualmode10/mode14 nine-publication native/GPU/EOP/owner oracle and nativepage/lateedit/failure tests0VUID; fresh outputstores0. Six focused old regressions pass. V47 next actualgame eligibility/census; no FPSgainclaimed. DMAOFF, allplayers/seeds/hooks/uncommittedworkpreserved, no pushes.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V46 proves storage mip1 loading blocker; conditional color stores ready for qualification — 2026-09-13 18:13 UTC

V46 proves FindImage Storage mip1/128x128/65536B in two-levelRGBA8mode13; quarter passes.26.380s/451presents/25Crosspairs,seedunchanged,0VUID. Freshf410FromSoftware logo24.5panelFPS/AAOFF, no gameplayproof. Private mip fix and conditionalcolor qualification next; isolated D3D11 merge read-only audit underway. DMAOFF/no pushes/protections preserved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V45 passes quarter depth; color scatter cost and two-mip blocker proved — 2026-09-13 17:35 UTC

V45 actualquarter publication succeeds(all120edges), then new256x256/two-mipcoloroutputgate; exactwriter/viewnotyetowned.27.537s/441presents/26Crosspairs,seedunchanged,0VUID; capture450missedinterval,no gameplayproof. ActualGPUcolorhostscatter medians3.60/4.07ms support transferreductionpriority. Next exactmipcallerdiagnostic and typedconditionalstoredesign; DMAOFF/protections preserved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V3k quarter-depth blocker qualified; V45 gameplay attempt next — 2026-09-13 17:30 UTC

V3k exactquarter depth passes red/green renderer, rawGPU/FP, splitmemory and focused existing regressions0VUID. Optional timingON fixtures show~0.59ms copy/~3.3–3.47ms hostscatter per4K output, notgame/FPSproof. V45 visible TimmycontinuousCross next; allplayers/seeds/protections preserved,DMAOFF.120title/stableminimum30gameplay4K+AA stillunachieved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Quarter renderer reproduces V44 blocker; native proof qualification next — 2026-09-13 17:12 UTC

Quarter renderer fixture now reproduces exact V44 dimension gate on unchangedV3j with0VUID; redbinary preserved. Contiguous-plane fixture correction kept all native/padding/EOP assertions. Productedge path and GPU/native proofs remain private pendingqualification. Performancegoal120title/stableminimum30gameplay4K+AA stillunachieved; DMAOFF.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V44 proves coupled quarter depth; bounded edge path next — 2026-09-13 16:51 UTC

V44 proves quarter surface is coupled depth (control0x700736), so S8-only shortcut does not apply. Exact Z2621440/S655360/H65536 and tiled DBprofile/clear1.0 now owned.24.264s/467presents/23Crosspairs,seedunchanged; freshf464blacktransition16.5panelFPS/AAOFF, no gameplay/30FPS proof. Private bounded shared-edge implementation and GPU/nativeoracle underway; performance work preserved/DMAOFF.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V43 identifies quarter-resolution HTile edge blocker — 2026-09-13 16:36 UTC

V43 exactnewblocker:960x540D32S8/HTile in1024x640storage,Z2621440B,Haddr0xc8280000. Logical540 createspartial8x8edge; simpleguardrelaxationbreaksindexing/metadataauthority.23.832s/468presents/23Crosspairs,seedunchanged,8freshcaptures(lastblacktransition+overlay,AAOFF),nogameplayproof. ThreeGPUsegmentedbatchesstillcomplete900segments/229088B. Nextboundededgeimplementation/oracleprivate; preserveallpriorperfwork/DMAOFF/protections.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V42 passes packed gate; HTile dimension evidence next — 2026-09-13 16:31 UTC

V42 advances past packed layout gate and completes3segmentedGPUcopies/900segments/229088bytes.23.811s/465presents/22Crosspairs,seedunchanged; lastfreshf438capturetitle23.9panelFPS/AAOFF, no gameplayproof. NewHTilephysicaldimensions rejection lacks exacttuple. V3i failure-only diagnostic preservespredicate; V43next tolearnlayout, no speculativealignmentrelaxation. Performancegoalremainsunachieved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V3h packed HDR output red/green qualified; V42 next — 2026-09-13 16:25 UTC

V3h packed HDR mode14 output has actual red/green and rawbit qualification0VUID, with depth/S8/segmented regressions passing. RawAMD6/Float+ordinarylayout provenance retained; raw7 cannot borrow cacheplan. DistinctGPUinitialdecode/existingGPUencode,CPUdecode/encode0; sharedRGBAreuse/DMA unchanged. Private player packed-v3h-player; V42 next. No gameplay/30FPS/final4K+AA acceptance.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V41 passes actual segmented copies; new 4K packed-format output blocker — 2026-09-13 16:05 UTC

V41 passes real segmented copies:2GPUbatches/782segments/199232activebytes; old oversized-arena blocker gone.469presents/22.268s/21Crosspairs,seedunchanged,3freshcaptures show loading card (22.8panelFPS/AAOFF), no gameplay/30FPS proof. New4K output admission rejection format122 B10G11R11UfloatPack32,33423360B at0xea570000. The earlier64bpp stage1 compute-clear probe is separate; source does not link it to this fatal writer. Investigate packed-format admission next. All-clear savings remain. V40wait audit v2 identifies largecolorPublishAll cost; native synchronization preserved. No unchanged game retry.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V3g bounded GPU segmented copy qualified; V41 ready — 2026-09-13 16:00 UTC

V3g exact19 bounded GPU segmented copy built and13 actual GPU cases pass0VUID, with depth/all-clear/S8 regressions passing. Copies active segments while retaining unchanged acquisition cap and native visibility. One terminal fixture diagnostic mismatch corrected without weakening its complete byte/version/owner/zero-payload oracle; failed artifacts preserved. Child400463a3, private receipts resume-20260913-v1/segmented-copy-promotion-v1; V41 prepared, not yet run, continuousCross/Timmy/COLOR_HOST_DMA=0. Actual game controls and ≥30FPS gameplay remain unqualified.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V40 proves depth ingress savings; exact nine-group copy blocker — 2026-09-13 15:27 UTC

V40 proves the all-clear shortcut in game: at least256 Z omissions/8.556GB requested bytes; native56..180 snapshot requests5.239GB to1.331GB and elapsed6.296s to4.880s. Captured title15.1FPS, AAOFF; gameplay/120/30 targets still unmet. Startup blocked on exact19-word segmented copy:9 groups,12-byte controls/108B total,7984B source,280839280B destination arena. Current descriptors/registers proved; control payload not yet captured. Next prepared GPU-only sparse-copy path plus native/EOP/owner fixture; remaining encode waits audited in parallel. See V40/result-summary.json, selected-diagnostics.json and latest detail.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Exact all-clear depth ingress qualified; game benefit pending — 2026-09-13 15:09 UTC

Integrated-v3e-all-clear is qualified: exact all-clear HTile omits Z ingress with current DB clear; six-draw fixture proves two omissions/66,846,720 requested bytes plus mixed/late/invalid fallback, native bytes/EOP/owners. Ten focused GPU cases0VUID plus memory contract. Initial pending-S8 fixture failure was an obsolete preflight-stage assumption, corrected with stronger initial-vs-later read witnesses; failure retained. No gameplay/FPS acceptance. Next visible run checks real eligibility and V39 arena-blocker exact current shader/descriptor state. See latest detail and private all-clear ingress/fixture/promotion/qualification artifacts.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V39 removes Abort; depth H writes and scatter arena remain — 2026-09-13 14:47 UTC

V39 confirms the unwanted Abort is gone and actual H writer0xa224d59e now causes the legitimate depth reason7 invalidation; depth reuse stays0. Direct-color hits increase715→1298 and contained startup snapshot requests fall13.33GB→5.24GB. No isolated FPS claim: captured title11.6FPS,AAOFF,4Ksource/1440pfinal; no gameplay. Next gate is shader0xfefebf9f's270.112MiB scatter-copy arena. Private all-clear Z-ingress omission/fixture and exact bounded GPU scatter-copy research are active. See latest detail and V39 receipts. Dota hold lifted; continuousCross/Timmy/DMAOFF/protections preserved.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: Compute-clear cache repair qualified; V39 prepared — 2026-09-13 14:32 UTC

Dota resource hold explicitly lifted by the user. Clear-size regression now proves red on V3c and green on V3d: actual fallback dispatch preserves depth receipt,next draw1reuse hit/noZ/Supload,fullnative/padding/EOP/owner checks;8focused cases pass0VUID. Live V3d contains the narrow repair plus unchanged-cap budget diagnostic. V39 visible Timmy/continuousCross is prepared; DMAOFF. No game FPS gain or30FPS acceptance yet. See the detailed checkpoint and resume-20260913-v1 qualification receipts.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V38 clear-size abort proved; source ready under Dota resource hold — 2026-09-13 13:49 UTC

V38 identifies the early redundant-depth cause:16/16 aborted clear recognizers fail a pure size check before image lookup, erasing otherwise matching depth receipts. Source-reviewed fix, actual dispatch regression and separate shader-buffer budget diagnostic are privately frozen and UNPROMOTED/UNBUILT in private/perf-lab/resume-20260913-v1/next-resource-window-v1. See [the detailed checkpoint](2026-09-08-gray-screen-provenance-and-loading.md) and its latest V38 section.

V38:39continuousCross pairs,427presents,seed unchanged; ownedf410 title9.9FPS,AAOFF,4Ksource/1440pfinal. Prior HTile fatal replaced by an unidentified oversized shader-buffer rejection; no gameplay or FPS gain verified. All9focused stencil/depth checks previously pass0VUID; target120title/stableminimum30gameplay4K+AA remains unmet. Color DMA staysOFF.

User is playing Dota. Builds/GPU/game runs are paused; light source work is complete and the red/green/next-run sequence is saved. Current live baseline remains V3c/97e46dfd for qualification. The old sleep hold is lifted; do not treat elapsed time as renewed resource availability.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE: V37 negative game result; stencil path qualified — 2026-09-13 13:18 UTC

V37 empty-FCE fixture repair is qualified but the game never exercises that path: depth reuse still0 and title11.2panelFPS, same stencil gate. No FPS gain claimed; unchanged repeat parked. V3c explicit S8-only path plus exact abort-origin diagnostic now built/qualified9focused checks0VUID, including pending real depth producer→fresh S8 and strict depth re-entry. Next V38 visible TimmycontinuousCross; DMAOFF. Target120title/stableminimum30gameplay4K+AA remains unmet.

Read latest recipient index/detail and private/perf-lab/resume-20260913-v1. C:only/noE:/explicitcwd/Uptownfrog/hooks/push.default=nothing; preserve normaldev0b6610b4, private players, all uncommitted work, seeds/views and separate translations/_recomp. No commits/pushes. ContinuousCross throughout visible Timmy runs; no Computer Use. Sleep hold lifted, active work continues.

---

# ACTIVE performance continuation — 2026-09-13 12:52 UTC

The user lifted the September13 sleep hold. Latest V36 diagnostic proves all16 depth reuse gates pass but AbortGpuOperation erases matching stored proofs before entries2..16. Root preparing narrow empty-FCE early rejection plus actual dependent-depth fixture; global Abort/version/barriers stay literal. Explicit stencil-only S8 implementation/fixture are private parallel work. Stronger oracle-v2 now promoted and qualified. Current integrated-v3a-fix1 childe78bce763506d4e04484c706dc3f368aee5f7a0547a3047a7b6ebf602ac12f22.

V36 visible WinSta0/Default,38continuousCrosspairs/38.824s,426presents,seed unchanged. Ownedf426loading10.9FPS,AAOFF,4Ksource/1440pfinal; same stencil0x701/render0 HTile gate. Native56..18010.628030s, no speedup/gameplay acceptance. Performance120title/stableminimum30gameplay4K+AA remains the priority. Keep color DMAOFF. Read latest recipient experiment index/detail and private/perf-lab/resume-20260913-v1; all raw prior docs preserved there. C:only/noE:/explicitcwd/Uptownfrog/hooks/pushnothing, normaldev0b6610b4 and all prior work/seeds/views/translations/_recomp preserved. No commits/pushes.

---

# SHUTDOWN HOLD — 2026-09-13 03:59 UTC

The user requested stop after the current test to sleep. All game/build/GPU tests are finished; do not continue until the user resumes. Start from private/perf-lab/shutdown-20260913T0359 in the recipient, especially checkpoint.md, NEXT-STEPS.txt and RESUME-PROMPT.txt. This supersedes earlier active-run notes below. No V36 run.

Performance priority remains120FPS title and stable minimum30FPS gameplay at4K+AA, substantially beyond the old12–15FPS gameplay. V35 reached only Play Online / Play Offline at14.9panelFPS (AAOFF,4Ksource/1440pfinal), then an HTile gate on a stencil-only draw. Native56..180 interval was17.3% shorter thanV34; this is progression, not a gameplay/steady-FPS result. No acceptance achieved.

Current integrated-v2z child0e344eee39b986e2b93e84c2db6f664db3fa3932d0aa93c98be2a9e184f5419d is built/preserved,11focused contracts pass/0VUID. DMA helper ABBA: display mode10 ~32% slower,mode14 variable/~5% lower phase medians. Keep BB_VULKAN_COLOR_HOST_DMA OFF and park unchanged candidate. No game FPS gain; do not spend the next run enabling it. Previous integrated-v2y/c37c5068 V35 player remains preserved in its private run.

Major remaining work: depth publication now reads only12status bytes and fast display avoids the captured full CPU snapshot, but depth reuse has zero comparisons/hits in game despite stored proofs. Read gpu-depth-receipt-v35-audit-v1: add the bounded first16 reason rows, then repair only the proved invalidation. Read gpu-stencil-only-handoff-v1: explicit S8-only operation can avoid touching unused native Z/HTile and pass the new gate; implementation not started. Preserve all CPU visibility, pending publication, padding, FP validation, overlay and lifetime rules.

Private gpu-depth-rejection-oracle-v2 is ready but UNPROMOTED/UNBUILT (freeze738855a9,patchb7e4224d); v1 has a runner-env integration problem and is superseded. Current live texture LFb6fc43fb/helperf286253c, current depth fixture8f740f75. All detailed receipts and next commands are in the shutdown bundle/index/detail.

C:ONLY; NEVER E:; explicit working directory for every command. Donor and recipient Uptownfrog; recipientHEADfa47b5b3c99b13b91c12692a2e108bf5a1b60412. Verify repo/branch/protections before mutations. Preserve .githooks,push.default=nothing, all uncommitted work. Never mutate another branch or push donor; any authorized recipient publication only exact refspec to refs/heads/Uptownfrog. No commits/pushes tonight. Normal dev0b6610b4 remains unchanged.

Visible game tests only, Timmy isolated save copies, readonly seed/hardlinked views. Cross once/second throughout the entire run (seconds2..600 while alive,450ms/framecap1), no screen-driven navigation. No Computer Use/CUA. Local language preferences private. Preserve unrelated translations and tools/liverpool/_recomp for their separate owner. Native x86-64/HLE/player foundation; Remill/AOT paused; no cleanup merge. All subagents stopped.

---


# Performance continuation — 2026-09-13 03:26 UTC

V35 visible game run active: isolated Timmy save copies,1HzCross seconds2..600 until exit, no screen-driven navigation. Build integrated-v2y child c37c50688bb46962c848a5d2ec06500ee0dc9e862d6d930b5b9304c3875ecdfe. Root owns game/result/scene inspection; no competing build/GPU fixture while timing it.

V2y combines native GPU depth/stencil/HTile publication and unchanged-depth reuse, proved mode10 display without full CPU snapshots, exact D16 singleton arrays1..64 and pending growth.13focused tests pass (13.76s,0VUID); visible display passes (1.77s,0VUID). Corrected an importer that treated optional prefers-dedicated as mandatory; exact leased extent remains unchanged. Positive depth reads12status bytes per publication instead of42,434,572 legacy bytes. Full byte/padding/late-CPU/remap/Stop tests pass.

No FPS/gameplay/AA acceptance yet. V34 remained at Checking save data… (~9.9panelFPS,AAoff), then stopped on3-layerD16. Performance remains the criterion:120FPS title and stable≥30FPS gameplay at4K+AA. DMA candidate privately frozen; independent review pending. Stronger invalid-depth route trace oracle privately being authored.

Recipient index/detail updated; prior raw documents preserved in private/perf-lab/resume-20260912-v1/depth-array-display-qualified-v32. C:only, Uptownfrog, hooks and push.default=nothing; normal0b6610b4 player and uncommitted work preserved. No commits/pushes. Translations and tools/liverpool/_recomp remain with their separate owner.

---

## Active continuation — 2026-09-13 02:46 UTC
V34 complete: fasterstartupinterval9.7159nativeIDS/s vsV32 7.951,rootcapture9.9FPStitleChecking save data,AAoff; stillno gameplay. Integrated-v2w child e4fe2a6043c91af329c22f622118054a9080b008fb1a8ea6f4d05eda98f100a6. Mode10+probe+exactD16growthqualified;45continuousCrosspairs/45.868s/419presents/seedunchanged. Session20260913T023728-b41bf325. Newgate3layerD16singleton196608bytes afterpassing1→2; encoderagentnowownsprivate1..64singletonarray/growthimplementation. Rootownsreview/qualificationofdepth-nativepublicationcandidate; detiler_barrierownsprivatefastdisplayreceiptobservation toomitcanonical33MBcopywithunchangedfallback. NoGPU/buildcurrentlyactive. Mode10 actualGPUfreshcapture0memcmp/33177600versionverifiedbytes; usecorrectproof counters. Auditprivate reuse-game-v34-audit-v1 frozen.
Continue performancepriority, visibleTimmycontinuousCrossentiresession, allC:/noE:,explicitcwd, Uptownfrog/hooks/pushnothing, preserveuncommittedtranslations/_recomp/normaldev0b6610b4. No120title/30game/AA/full4Kfinalacceptance. See latestexperimentindexdetail forexactfailure/results.

## Active continuation — 2026-09-13 02:26 UTC
V33 diagnostic complete: still6.5FPSChecking save data, no gameplay. Exact blocker is pending D16 singleton1→2layers at same address, oldlayer0written and newviewlayer1; oldGPU producer is unbound. Root implementing narrow priorpublication/growth, with agent authoring combined-draw exactbytes/padding/EOPfixture. PrivateV33session20260913T021316-d9c58b43,55Crosspairs,56.668s,seedunchanged. Diagnostic2build4a2f5f77… qualified1CPUwriter smoke; initialdiagnostic1signednarrowing compile failure is superseded by explicitu32cast.
Performance priority: mode10 retained directpublication/proof promoted(unqualified)15files; integrated-v2v building. Deferred OutputOperation construction past pure negative recognizers and depth nativepublication are private candidates. V32/V33writerreuse saves repeat requests but has NO measuredFPSgain; do not present it as improvement. CurrentCPU/native→GPU roundtrips remain dominant target; nextgame must continuouslyCross forentire session and attempt gameplay. Preserve normaldev0b6610b4…,Uptownfrog/hooks/pushnothing,alluncommittedwork,C:only/noE:,translations/_recomp untouched. No30FPSgameplay/120FPStitle/AA/full4Kfinal claim.

## Resume update - 2026-09-13 02:10 UTC

V32 childe049ee4f:4/4focusedtests0VUID; actual256writerreusehits omit8.556GB
repeat requests. NoFPSgain:startup15.595609s versus14.918556s; viewedtitle7.2FPS,
AAoff,no gameplay. Remaining ordinaryupload repeats andwhole display/depth
roundtrips are the nextperformance targets; these candidates areprivateinprogress.

V32 samependingD16alias gate54.605739s,54continuousX pairs,seedunchanged.
Fataldescriptor stringtruncatedat512bytes; failure-only numeric tracing is now
building asintegrated-v2u-diagnostic1 for exactnextloading evidence.
Normaldev0b6610b4 andalluncommittedwork/protectionspreserved; nocommit/push.

## Resume update - 2026-09-13 01:47 UTC

V31 completed54.838s,54continuousX pairs,418presents,unchangedTimmyseeds.
Two-layer D16 nowqualified6/6,0VUID in integrated-v2t-fix1 child17ba9b01.
An uninitialized RenderState caused first-build phantom-stencil validation;
value initialization fixed it, failed evidence preserved.

Next loading gate is pending-producer image alias; exact descriptors needed.
Viewedtitle/Checking save data6.7FPS,AAoff; gameplay remains unconfirmed.
Performance work now targets the measured same-image CPU-upload->writer reuse
omission (64/64 decisions),not hypothetical format aliasing. Depth-clear cohort
has0fullclear/384countedstates:park that hypothesis. Private candidatework is
in progress; perform next changed visible continuousX run after qualification.

## Resume update - 2026-09-13 01:11 UTC

V30 child1c1b8d62 finished54.215s with53continuous X pairs,426presents and
unchanged seeds. It still stops at the two-layer D16 input gate. Ownedf410
shows title/Checking save data at7.9FPS,AAoff; no gameplay confirmation.

CPU-before-cache route reaches256 actual certified uploads, but0checks/hits:
no game upload omission established. Retained native imports remain1/1024.
User emphasizes performance above implementation elegance or support breadth.
Primary next work removes GPU/native/GPU passes; two-layer support only unblocks
gameplay measurement. Exact parent-private audit and candidate work continue.
Normal dev/Uptownfrog/hooks/prior edits preserved, no commit/push.

## Resume update - 2026-09-13 00:58 UTC

V29 passed the former one-layer D16 writer and stopped on newly observed
two-layer D16 input (131072B).94 continuous X pairs,95.368s,417 presents,
seed unchanged. Ownedf410 is black with5.2FPS/AAoff overlay; gameplay remains
unconfirmed. Startup timing regressed; no performance success claimed.

Latest integrated v2s child1c1b8d62 includes the qualified early complete CPU
snapshot path before cached-buffer lookup. Five GPU checks pass; new actual
fixture proves9 skipped uploads among19 samples with two GPU producers.
V30 is running visibly with continuous X to test actual game effectiveness.
Two-layer D16 work remains private, using verified bank-rotated0x13800 offset.

Normal dev0b6610b4 and prior work preserved. Uptownfrog, hooks and push.default
remain intact. No commit/push. See experiment index/detail and private receipts.

## Resume update - 2026-09-13 00:51 UTC

Exact singleton D16 output is now integrated and GPU-qualified: v2r-fix1 child
8529e2a6, 11/11 targeted cases passed with zero validation errors. Four real
depth draws preserve native padding/guards and prove EOP/owners/Stop. V29
is running visibly with continuous X for up to 600 seconds to test progression
beyond the former writer gate; no outcome is claimed yet.

The next CPU texture-copy reduction remains private in
gpu-cpu-texture-before-cache-v1, awaiting independent review and execution.
Normal dev 0b6610b4, uncommitted work, Uptownfrog and protections remain intact.
No commit or push. Experiment index and detailed checkpoint hold receipts.

## Resume update - 2026-09-13 00:34 UTC

Current integrated build v2q-fix1 childfafd0f35 passed15CPU/GPU checks(0VUID).
Retained native imports are now integrated and used: v28 report1024publications
with1import/1023hits. Separate CPU texture receipt path had0game certificates
or hits; its fixture passes but its target game path still needs work.
V28 continuousX56pairs stopped57.559s at the known singleton D16 writer gate,
417presents,seed unchanged. Startup interval6.84IDs/s vsprior5.25; this is not
title/gameplay performance. Ownedf360stillFromSoftwarecard(8FPS,AAoff);
priorv27f410showedloading. No world/4Kfinal/AA/30FPS/120FPStitle proof.

Exact singleton D16 output support is private and being checked before build.
All uncommitted work and normaldev0b6610b4 remain preserved; Uptownfrog/hooks/
push.default=nothing intact, no commit/push. See experimentindex/detailedcheckpoint.

## Resume update - 2026-09-13 00:22 UTC

V27 now visibly reached a loading/tip screen (owned f410), then rejected the same
1x1 mode0 D16 texture as an OUTPUT:65536bytes,pitch256,physical128,addr0x177230000.
76continuous X/release pairs,77.391s,411presents,seed unchanged. Gameplay/world
still unverified; overlay5.3FPS,AAoff,4Ksource but1440p final. Exact singleton
D16 output plan/GPU transfer/fixture is being authored privately.

D16 INPUT qualification now passes2/2 with0VUID. The prior midpoint failure was
an overstrict mathematical comparator oracle: pinned Khronos CTS permits either
Boolean there. New robust separated values and all native/padding/EOP/lifetime
checks pass. No native GCN threshold-parity claim. Normal dev0b6610b4 preserved.
Retained-import and CPU-texture reuse compositions are still private pending
final review/build/qualification; no performance gain claimed. See updated index.

## Resume update - 2026-09-13 00:14 UTC

Latest visible continuous-X v26 still did not prove gameplay:84press/release
pairs,84.999s then exact output-layout-plan failure at415presents. Only f360
capture exists and shows FromSoftware card (~5.5FPS), not gameplay. Timmy copy
isolated, seed unchanged. The exact singleton D16 input gate is now built
(v2o-fix1), but its original near-threshold comparison fixture failed; source/
padding/EOP/owner checks passed and precision review is pending qualification.
V27 is currently running visibly on failure-diagnostic v2p; its only code change
adds the failed output profile to the existing exception. Continuous X stays
active until process exit, fixed captures390/every4. See experiment index/detail.

All retention and CPU-upload-receipt performance candidates remain private,
unpromoted/unbuilt. Normal dev0b6610b4 is preserved; Uptownfrog/hooks and
push.default=nothing remain intact. No commit/push, other-branch/toolchain or
translation changes. Stable30FPS4K+AA and120FPS title remain unmet.

# Active performance/progression checkpoint — 2026-09-12 23:47 UTC

Latest user instruction overrides the old2–30s input limit: keep pressing X throughout every visible game run, using isolatedTimmy, with no directional or screen-driven navigation. V25 tested this with qualifiedintegrated-v2n and a600s limit. It exited after67.746s on a new mode0 D16_UNORM1x1 sampled-depth admission gate (65536B,pitch256,physicalheight128,no metadata), after416presents and66Cross pairs. The onlycapture(frame120) missed the failure interval; gameplay rendering is NOT confirmed. Fix/qualify the exact supported GPU input profile and use a new continuous-X run with denser fixed captures to assess progression.

Performance remains poor: v24 late title5.233877FPS vs v23 5.509974; sampled supplement passes authoredGPU cases but at4096gamepublications it adds no proven hits (both1345). Vulkan label fixed.4K source/1440p final andAAOFF; target30FPSgameplay/120FPStitle unmet. Native host-import setup dominance is only a hypothesis until timed; old vsnew scopes differ. CPU snapshot/upload receipts and explicitly frontend-owned persistent imports remain private ongoing work, alongside root unbuilt retained runtime/glue draft. Do not promote without strict byte/padding/latewrite/identity/retirement qualification. All work stays C:/Uptownfrog with hooks/push.default=nothing; preserve normaldev0b6610b4, uncommitted work, seeds/hardlinkedviews and separate translations/toolchain. Detailed experiment index updated; no push.

---

# Active performance checkpoint — 2026-09-12 23:24 UTC

V23 completed and reached the title menu at5.509974FPS, worse than v22 5.976936; the performance target is not met. Integrated-v2m staged direct publication passed11/11 focused checks, executes real direct native GPU writes and valid prepared-image reuse, but per-publication import setup and repeated sampled input acquisition remain. The final owned capture confirms the corrected Vulkan label, AA OFF and2560x1440 final from4K input. Do not present this as a speedup or4K+AA acceptance.

Next: qualify the frozen sampled-image receipt supplement6e2d31c5… as integrated-v2n, then measure a changed visible run. In parallel audit a sound way to retain imported native backing across publications and a separate receipt from complete successful CPU snapshot/uploads. Keep CPU visibility, watch notifications, padding, producer overlap, full identity and lifetimes intact. GPU/CPU page-protection failures remain parked; no unchanged repeats. All work stays C:/Uptownfrog with hooks and push.default=nothing; preserve uncommitted work, normal dev, private seeds/hardlinked game views and separate translations/toolchain. Detailed evidence is appended to the recipient index and linked checkpoint.

---


## 2026-09-12 23:12 UTC — Staged direct GPU color qualified; v23 visible run active

Integrated-v2m child da4238575483917782b3f8bab5b57415360b17ad1c9cfa2c364308a57f0144f2 passed11/11 focused CPU/GPU tests. The strict original direct fixture now yields11 exact native publications/8 checks/4 reuse hits/7 uploads, with no encoded CPU vectors/staging readbacks and exact padding, CPU visibility, EOP and retirement. Import pin→durable watch harvest BEFORE DMA→active overwrite→positive wait/unpin fixes the demonstrated false miss; no post-DMA reset or receipt rebase.

v23 is RUNNING visibly,300s, session20260912T230639-e3e9120c, wrapper session73254. Do not build/run other GPU work until completion. Early census1024pubs/322hits/0fallback proves direct route executes; FPS result stillpending. Latest completed game remains v22 at5.97694FPS;120title/30gameplay4K+AA unmet. Run adds only directcolor flag and separate census to v22 profile; fixedCross2–30/Timmy/isolatedcopy.

Next: finish/analyze v23 with strict existing cost parser plus separate13-field direct census; inspect owned final capture. Sampled receipt extension+actualGCN consumer is PRIVATE and unbuilt; root reviewing. Save new meaningful results to index/detail/handoff. All source originals backed up; no commits/pushes, C only/explicit cwd/Uptownfrog/hooks/nothing, normaldev0b6610b4 and unrelated translations/tools/liverpool/_recomp preserved.


## 2026-09-12 22:43 UTC — Direct color v2l built; import-writewatch blocker isolated

Latest game remains v22 at5.97694 late title FPS, target120/30FPS4K+AA unfulfilled. Direct color integrated-v2l-fix1 is built but NOT game-qualified:8/9 focused cases passed, with exact real GPU native writes/padding/import retirement; positive runtime receipt fixture misses its first expected unchanged-image hit on draw2. Keep the failed evidence and strict oracle.

Controlled import-only test proves vkAllocateMemory marks all8112 initially clean watched pages before any GPU commands. Fix is being authored privately: import prepare→pre-DMA durable write-watch harvest→exact active overwrite→positive wait/unpin in one external lease, with a separate active-overwrite contract. No post-DMA reset/rebase and no masquerading as full padding overwrite. Encoder owns backend stages; htile owns HLE/facade; detiler owns glue/sampled IMAGE_LOAD fixture. Root promotes/builds/runs. No game/build/GPU currently active.

Evidence: resume-20260912-v1/direct-color-v2l-qualification, direct-color-counter-diagnostic-v1-run, vulkan-import-pin-writewatch-v1. Default-off direct flag; source12-file promotion8a2448a6 backed up. No commits/pushes; normal dev0b6610b4 preserved; C only/explicit cwd/Uptownfrog/hooks/nothing and separate toolchain/translation ownership unchanged.


## 2026-09-12 22:28 UTC — Vulkan v22 finished:6 FPS, active reuse works; direct publication next

Latest measured visible title result is5.97694 FPS (v21 5.40829); the120 FPS title and30 FPS4K+AA gameplay targets remain unfulfilled. v22 integrated-v2k, session20260912T221519-77e284aa, intended300294ms timeout;29 presses/releases, seed unchanged,8/8 GPU-input-fresh captures. Owned capture confirms corrected Vulkan label, title menu, AA OFF; final output2560x1440 from4K source.

Active-pixel path hit346/346 comparisons in519 eligible attempts, removing those full ingress uploads. Still31.927GB snapshot request spans and6.436s encode waits in29.907s audit. Do not repeat unchanged. Direct mode14 native host GPU encoding + successful-publication receipt/cache is next; backend source frozen, facade integration private/finalizing, neither built yet. No game/build/GPU currently active. Preserve all runtime visibility/padding/lifetime rules; final mode10/AA route unchanged.

See latest gray-screen experiment index/detail; private v22-analysis.json and vulkan-compatibility-v22 preserve evidence. Normal dev child0b6610b4 remains preserved. C only/explicit cwd, Uptownfrog only, hooks/push.default=nothing intact, no donor push, no unrelated translation or tools/liverpool/_recomp edits.

## 2026-09-12 22:18 UTC — active mode14 fix qualified; visible v22 in progress

Integrated-v2k c283f59553dafeb15cf4cffc613bef154f60e639261dff4072040f5f1290fa61 passed focused CPU/GPU qualification. The11-draw active-pixel test achieves5 exact reuse hits/6 uploads, including both native-padding false misses, with active edits/barriers/padding/EOP/lifetimes correct. V22 is now visibly measuring it for300s with the standard isolated Timmy/fixed Cross protocol and prior audit flags plus BB_VULKAN_COLOR_ACTIVE_REUSE=1. The Vulkan label/glyph fix is included. No game FPS gain claimed yet; latest completedv21 remains5.4083FPS. Dev0b6610b4 intact.

Larger direct mode14 GPU→native publication and version-receipt reuse are private/unbuilt under review, using the existing external GPU memory lease; no general memory subsystem/page traps. See recipient experiment index/detail and private active-color-v2k-qualification, integrated-v2k and vulkan-compatibility-v22. Current objective remains120 title FPS and minimum30FPS gameplay at4K+AA, unmet. C-only/Uptownfrog/protections and all existing work preserved.

## 2026-09-12 21:50 UTC — Vulkan performance work continues: v21 5.4FPS, active-padding reuse next

V21 completed: late title5.4083 IDs/s, no meaningful gain overv20. Six sampled mode14 full-reference misses differ only in padding; exact active texel reuse is being implemented in the existing path, preserving padding/native visibility/lifetime and raw CPU-edit fallback. The standalone coherent Vulkan host-pointer buffer import passed both owned-memory cases, all bytes/late edits/12fences/retirement, but is not game-integrated and establishes no FPS gain. Missing K/lowercase glyphs and the Vulkan label are fixed in live source, awaiting the next substantive build.

Latest built private player is integrated-v2j aa824800e76159eefc142cab3c17aabbe4fc0a057f5cedc5d287eaa1a2c31498. Dev0b6610b4 remains intact. Eight v21 final GPU-fresh captures pass; actualoutput1440p/AAoff, gameplay4K+AA and120titleFPS remain unmet. Native protection stays parked (older live-YMM red-zone corruption plus tracker11/16). Do not repeat unchanged matrices or cleanup merge. Evidence and next bounded implementation are appended to recipient docs/checkpoints/gray-screen-experiments.md and its detailed checkpoint. Work remains C-only/Uptownfrog; no other branch/push or desktop control. Existing uncommitted/translation/toolchain-owned work preserved.

## 2026-09-12 21:29 UTC — v2j qualified; visible v21 game measurement active

V2j fixes command-owner retirement ordering and passed2 CPU/parser plus8 affected GPU/visible cases, including the original failing audit-enabled sealed-color fixture unchanged. Childaa824800…, source/receipt resume-20260912-v1/retirement-promotion-v2j and integrated-v2j. V21 is running visibly for300s with isolated Timmy/fixed Cross2–30, validation, shared color-reference reuse, compared native publication, bounded mismatch classification and cost window240–270s. No native-protection or host-import candidate in this player. Analyze only after completion with both required counter schemas, then owned final capture/input/seed evidence. Latest completed actual game remains v20=5.4446 late title IDs/s against >100 title/12 gameplay baseline; no accepted FPS/4K+AA result yet.

Next choose one measured GPU reuse/transfer bottleneck from v21. Pending-GpuModified and recognized compute-copy GPU paths already exist; ordinary image-source DMA missing support is not attributed to title. Native protection remains parked; CPU-current tracker failed5/16 and known live-YMM red-zone failure persists. Preserve all original C-only/cwd/Uptownfrog/hooks/push.default/dev0b6610b4/shutdown/uncommitted/seed/privacy/separate toolchain restrictions; no desktop-control tools or publication.

## 2026-09-12 21:21 UTC — focused next delivery; CPU-current tracker failed and parked

Finish command-owner retirement correction, run targeted affected tests, then one visible v21 Timmy measurement of already-composed changes only. Latest actual game remains v20 at5.4446 late title IDs/s, unacceptable against >100 title/12 gameplay. Then pursue one measured existing D3D11/Vulkan GPU reuse case before required CPU publication. Minimum30FPS gameplay at4K+AA remains unfinished.

CPU-current tracker now built/executed:11/16 pass,5 fail; evidence resume-20260912-v1/cpu-current-tracker-v1, binaryad929f36…. Four aggregate native-state failures remain unclassified; mapping-lock observation also failed. No game memory protection. Known archived YMM red-zone corruption remains a separate blocker. Preserve and park this prototype; do not repeat unchanged or infer source/model review was execution success. Direct Vulkan host import is still a bounded source-only follow-up to the4096-alignment capability query, not a runtime/FPS result. Preserve all existing C-only/cwd/Uptownfrog/hooks/dev0b6610b4/private artifacts/uncommitted/Timmy inputs and separate toolchain/translation restrictions.

## 2026-09-12 21:14 UTC — current performance direction and corrected native-fault limit

V21 remains pending command-retirement fix/validation; latest game v20=5.4446 title IDs/s versus >100 title/12 gameplay baseline. No accepted Vulkan performance gain or30FPS4K+AA result. The existing old-renderer GPU reuse paths are now an explicit parity/port item before required CPU publication boundaries; zero color-comparison hits does not mean zero GPU reuse generally.

Do not treat new XMM-only native-fault passes as clearing the archived live-YMM red-zone failures. Required prior gate1/dispatcher/static-bracket/coverage experiments remain in force; no game-page protection or repeated unchanged native fault experiment is authorized by those passes. CPU-current tracker is private state-machine evidence only.

Query-only Vulkan probe on this4090 supports VK_EXT_external_memory_host with4096-byte alignment, evidence resume-20260912-v1/native-storage-vulkan-capabilities-v1. A new standalone owned-buffer import/publication fixture is being authored; no import/GPU-transfer result yet. This path aims at reducing staged transfer/copy costs while preserving native publication. All original C-only/cwd/Uptownfrog/hooks/push.default/dev0b6610b4/uncommitted/privacy/Timmy input and separate toolchain restrictions persist. No desktop-control tools or publication. Optional cross-task forwarding was auto-review-rejected and not retried; local implementation continues.

## 2026-09-12 20:57 UTC — Vulkan performance continuation: lifetime qualification before v21

Latest game remains v20:5.4446 late title IDs/s, severe regression against >100 title /12 gameplay baseline. Minimum30FPS gameplay at4K+AA is unfinished. Integrated-v2i(child14dac313…) compiled; four CPU contracts and audit-enabled macro GPU passed, but audit-enabled sealed-color fixture exposed a command-retirement race after visible notification. Failure preserved in private/perf-lab/resume-20260912-v1/classification-v2i-enabled. V21 has NOT launched. Fix completion/owner-release ordering and validate failure retention; do not weaken the assertion or repeat unchanged.

Native-fault v2 all10 isolated cases passed (DF-set controls/retries and exact refusal identities), evidence resume-20260912-v1/native-fault-v2, a narrow prerequisite only. CPU-current write-protection prototype remains private under review; no game mapping protection/publication suppression. Next visible Timmy run measures shared-reference reuse, exact compare-before-store and bounded active/padding classifications. Continue C-only/explicit cwd/Uptownfrog/hooks/push.default=nothing; preserve dev0b6610b4/shutdown/uncommitted work, seeds/private preferences and separate toolchain ownership. Cross2–30 only. Desktop-control tools remain off. Experiment index/detail updated.

## 2026-09-12 20:35 UTC — v2h publication tests pass; isolated native read/write faults resume correctly

Integrated-v2h child8d5ea2a524f2dfa50fe2275b35ebb6f4839dab9c9cee437d3442ab360e6e7658 built and passed ten CPU plus seven GPU/visible cases. Default-off compared publication avoids native stores on identical chunks, repairs late CPU edits, and preserves full readbacks/waits, padding, HLE completion and retirement. Its strict private parser passed nine methods; require its counter set when measuring an enabled game run.

The separate CPU-only native fault fixture passed all six cases on this host, including complete128-byte red zones and all tested architectural state through protected read/write retry. Private evidence: resume-20260912-v1/native-fault-v1. This is a prerequisite only. A fixed one-allocation CPU-current write-protection prototype is being authored with explicit participant scopes and no game integration; generic unscoped native-thread lifetime, aliases and host I/O still need proofs.

Next game build awaits the bounded active/padding mismatch diagnostic and composed parser. Do not repeat v20 unchanged. Last actual game result is still v20 at5.4446 title IDs/s, a severe regression versus >100 title /12 gameplay. Native game AA, world correctness and minimum30 FPS at4K+AA remain unmet. C:-only, explicit workdirs, Uptownfrog, hooks/push.default=nothing, private Timmy copies/fixed input sequence and desktop-control-off constraints remain. No commits/pushes; normal0b6610b4 player, all uncommitted work, translations and tools/liverpool/_recomp are preserved.

## 2026-09-12 20:18 UTC — shared color references pass correctness; game performance still unresolved

Integrated-v2g built successfully after a fixture-only const correction (failed build and original candidate preserved). Child hash 5d86b0eb78034e0d1941313aaeff47fb30fab1aef2154ed465fbcbb71097ed5f. Eight CPU and twelve GPU/visible presentation cases pass, including actual omitted ingress upload while scanout and refresh share immutable encoded storage, raw CPU edits, exact old/new captures, padding, aliases, allocation failure and retirement. No v2g game run yet; v20 remains the latest game evidence at 5.4446 title IDs/s versus the user's >100 title / 12 gameplay baseline.

Next: complete the separate bounded comparison mismatch diagnostic and compare-before-store candidate; preserve all existing publication semantics. Investigate the native resource-coherency architecture, starting with an isolated CPU page-fault/resumption fixture. No current read interceptor or safe blanket PublishAll suppression gate exists. The source-only architecture review is in private/perf-lab/native-page-coherence-architecture-v1. Native game AA, world correctness, true 4K final output and stable minimum30 FPS remain unverified.

Normal dev player 0b6610b4 is preserved. Desktop-control tools stay off; visible tests use isolated resources. All C:-only/Uptownfrog/protection/private-save constraints remain. No commits or pushes, no Remill/AOT resumption, no changes to translations or tools/liverpool/_recomp. Details and failed/inconclusive evidence are recorded in the experiment index and detailed checkpoint below.

## 2026-09-12 20:08 UTC — Vulkan v20 completed; architecture/performance deficit remains

V20 integrated-v2f completed visibly with isolated Timmy copies, 29 Cross presses/releases and unchanged seeds. Late title rate 5.4446 native IDs/s; owned title capture 5.5 FPS / 179.0 ms. This is still a severe regression against the user's >100 title / 12 gameplay FPS baseline. Eight captures prove exact GPU input freshness; source is 4K, final output 2560x1440, AA off. No stable-minimum/gameplay/AA acceptance exists.

The final-depth GPU validator ran for 159 late-window pairs and removed the CPU HTile scan. Color ingress reuse had ZERO hits: mode10 160 key misses; mode14 320 unequal comparisons plus 160 key misses. Do not assume padding is responsible. Eager native publication and fresh uploads remain; PublishPrefix/Finish still drain both caches. No native-read coherence bridge or replacement visibility policy is implemented.

Scene-AA helper and existing sealed-display/HLE-sealed contracts now pass visibly with zero validation errors; native game AA placement/parity remains unverified. A separate immutable shared color-reference source candidate has completed peer review and awaits root promotion/build/tests. Bounded active/padding mismatch diagnostics and Windows native page-access interception feasibility are being investigated separately. These are intermediate work, not a 30 FPS claim.

See the experiment index and detailed checkpoint for v20 metrics and evidence paths. Normal dev player 0b6610b4 and all private baselines remain preserved. Desktop-control tools remain off. Dota resource restriction was released. C: only, explicit working directories, Uptownfrog only, no donor push, no other branch mutation, hooks and push.default=nothing preserved. No commits/pushes. Remill/AOT stays paused; translations and tools/liverpool/_recomp remain untouched.

## 2026-09-12 19:54 UTC — active performance continuation: v2f validated, v20 running

C: only/Uptownfrog/.githooks/push.default=nothing remain mandatory. Desktop-control tools remain off. Normal dev0b6610 preserved. No commits/pushes/cleanup merge/AOT work. Keep unrelated translations and separate tools/liverpool/_recomp untouched.

User baseline >100FPS title/12FPS gameplay; current~5FPS title is a severe regression. v19 color reuse finished with late4.713IDs/s and all8 finalGPU freshness proofs; no acceptable performance gain. Its late240–270s audit showed298 comparisons but could not identify hits. Fullrendering/AA/4K-final-output/min30FPS remain unverified.

Current integrated-v2f child e6cdd28b81d5b231875f63db630225592000238ae4318212e8acbd9e28afeadd adds corrected finalGPUHTile validator plus fixed outcome counters.11CPU+17GPU cases passed,zeroVUID; realCPUFP1152cases,actual4Kroute and invalid-last-depth/submit/invalidation failures covered. Root caught and corrected final admission requiring prepared input state; supplementb59863... mandatory, original preserved. Per4Kpair readback removes32,522,228 logicalbytes withsamepositivefence+Batch3. Generator10fa3dfe..., privateparserf7626c1a...; frozencompositionsbackedup.

v20 is running visibly300s with samev19 reuse+sealed selectors and lateaudit240–270s, Timmy isolated seed and Cross2–30s. Finish analysis next: proof of newHTileroute/cost, exactreusehits/misses, late title throughput, finalcapturefreshness; record failures/inconclusiveevidence too. Shared immutable color reference and opt-in compare-before-native-store candidates are independently being authored privately. The later GPU sparse output design is frozen but unimplemented; all current full color readbacks/waits remain. See index/detail for exact hashes/evidence; no FPS acceptance claim.

## 2026-09-12 19:35 UTC — active performance continuation: v18 complete, v19 running

Work remains on C: only and Uptownfrog with .githooks/push.default=nothing preserved. User baseline is >100 FPS at title and12 FPS gameplay; ~5 FPS Vulkan title is a severe regression. No acceptable FPS gain,4K-final-output/AA/full-world acceptance established. Desktop-control tools remain off; visible shell-launched tests continue with Timmy isolated copies and fixed Cross2–30s.

v18 completed300s on integrated-v2d:1513 observed IDs, late1020–1140=5.027/s, owned title capture4.9FPS. All8 captures prove final GPU image freshness against33,177,600 published active bytes. Still AAoff,4K source but actual2560×1440 swapchain. Private `vulkan-compatibility-v18/capture-inspection/receipt.json` records hashes/results. Ordinary CPU publication remains.

Current live/build integrated-v2e adds exact full-byte prepared color refresh reuse and configurable bounded audit start;10CPU+16visibleGPU tests pass,zeroVUID. Child8c1180d7a0910fb479b55f94858cea94baa3db3b55ad93902f7df69812aef56d. Color candidate defaultoff preserves final scanout priority; mode10 sealed publication currently prevents sharing its encoded vector with refresh, so output transfers/fences/final snapshot remain. v19 is actively testing reuse+sealed with late240–270s title audit over300s. Complete its result/traffic/freshness analysis next. Private candidate output reuse/shared ownership and GPU HTile final validation remain separate unfinished work. No cleanup merge or AOT restart; normal dev0b6610 preserved. See gray-screen index/detail for full hypotheses and evidence.

# Active continuation - 2026-09-12 19:16 UTC

User baseline: previous renderer >100FPS title,12FPS gameplay. Vulkan~4FPS title
is a severe regression. Prioritize safe elimination of repeated GPU↔CPU texture
transfers/waits; correctness alone is insufficient. Existing30FPS at4K+AA gameplay
target and title performance recovery remain. Baseline is user-reported.

Integrated-v2d child2ddb53a6 built;7CPU state/memory/lifetime contracts pass.
Corrected actual HLE fixtureb410ca97 (patch7b99ccbd,binary670998b5) PASSED visibly,
including late CPU bytes/firstword after capacity exhaustion and exact production
refusal event,skipped content,Close/Open and retirement;zeroVUID.
V18 visible300s game is RUNNING with sealed selector1,validation/cost/census,
fixedCross2–30/releases,isolatedTimmy. Finish/analyze before otherGPUwork.
Normaldev0b6610b4,.githooks,push.default=nothing,Uptownfrog-only,C-only explicitcwd,
all uncommitted work/saves/privacy/translations/tools/liverpool/_recomp preserved.
No desktop control/commit/push. Exact color refresh reuse,GPU HTile final validator
and late-title cost-window offset are private ongoing candidates. AA unbuilt.

# Active continuation - 2026-09-12 19:07 UTC

Dota resource hold is over. Native GPU-only work continues on Uptownfrog,C only,
explicit cwd; desktop control off. Preserve normaldev0b6610b4,all uncommitted work,
.hooks/push.default=nothing,private saves/game views,translations and separate
tools/liverpool/_recomp. No commits/pushes/Remill/AOT/cleanup merge.

Latest gamev17 (v2b,faf603d5) completed300s,Timmyseed unchanged,29 Cross2–30+
29 releases. Title at~4.1 observed IDs/s,ownedf1140overlay3.8FPS,AAoff,
4Ksource but2560x1440finalswapchain,CPUupload/freshness0. Census proves123pairs,
1097planes/974waits; no FPS gain. v15/v16 validation-off control did not help.

Sealed GPU final-image core now validated on paired source: integrated-v2c,
7 CPU+8 GPU passes,including visible baseline/alias/PrepareStop,zeroVUID.
Its first baseline failed only a fresh-remap fixture setup:guardbytes0 versus
expected0xa5. First-diff+complete guarded-span initialization fixed the fixture;
source9e5ffb6f; all byte/CPUpublication/lifetime assertions preserved.
Failed and corrected receipts:sealed-v2c-contracts,sealed-first-diff-contracts,
sealed-remap-guards-contracts. No game GPU freshness claim yet.

Native HLE production94882a68 and original fixtures now promoted for experimental
integrated-v2d build (compiling). The actual HLE fixture MUST get its additive
capacity proof before execution:late distinct CPU bytes+firstword after both
tickets exist,skips keep old,processed7 new,and exact refusal event. Agent preparing.
Original frozen sources remain private/unchanged. Next run CPU state and corrected
visible HLE fixture,then attributable sealed-enabled game; AA still unbuilt.
GPU HTile final validator and safe exact color refresh reuse are private ongoing
source tasks. Stableminimum30FPS,4Kfinaloutput,fullworld,AAremain incomplete.

# Active continuation - 2026-09-12 18:50 UTC

User is done with Dota; resource hold released. Work continues on native GPU-only
Vulkan under Uptownfrog. Desktop control stays off. C only; every command explicit
cwd; preserve all existing protections/private assets/uncommitted work and normal
dev0b6610b4. Read the newest recipient index/detail entry before any repeat.

Validated: integrated-v2a child e401474b,6 CPU+21 GPU cases. Visible300s v15 and v16
both reach the title. Owned f1140 overlay5.2FPS(validation on) versus3.9FPS(off);
no controlled validation benefit or general speedup established. AAoff,source4K
but swapchain2560x1440;CPU final-upload route,freshness0. Stable minimum30FPS,
full world,4K final output andAA remain unfinished.

Paired D32/S8 complete patch af36fc5e is now live with raw originals saved in
recipient private/perf-lab/resume-20260912-v1/pair-promotion-v2b.
Integrated-v2b child faf603d5 built and passed6 CPU+13 GPU cases, including actual
4K exact bytes,one paired wait,HTile/Batch3,padding,stale identity and quarantine.
Visible v17 is RUNNING300s with validation,cost/schema3 census and fixed Cross2–30
plus releases,isolated Timmy copy. Finish/analyze it before another GPU/game job.
V15 census found at most one dirty image per publication:1121 singles+161 pairs;
do not pursue broad batching without new evidence. v15/v16 analysis pending.

Next sealed core c1d275a1 is still private/unbuilt,with required baseline/Stop
unmap fixes and owned first-word metadata. Native HLE production94882a68 reviewed;
fixture capacity proof gets additive late CPU bytes and exact refusal-event check.
Then validate native HLE/sealed freshness andAA separately. No CPU visibility or
lifetime shortcut. Update recipient index/detail and this handoff after results.

# Active continuation - 2026-09-12 18:18 UTC

User is still playing Dota and will say when done. Keep heavy builds and all
GPU/game tests deferred; lightweight source/review only. No new run bundle or
process launched. Live source stays three copy reductions plus schema2 census,
all unbuilt/unexecuted. Latest validated player/game stays v1z/v14; normal
dev0b6610b4 preserved. First next validation is this live layer, not later drafts.

Read recipient index/detail and private/perf-lab/post-dota-validation-queue-v1/
queue.json (d2e75b7c89277eb3): exact current pins, extra CMake targets, sequential
contracts, proposed300s visible loading/later captures and validation controls.
This is a static queue, not scheduled work. Fixed Cross2–30/releases and Timmy
save-copy protections remain.

Paired helper + same-boundary HTile integration is frozen in
gpu-depth-stencil-pair-handoff-v1 (manifest237612a8), with root complete composition
gpu-depth-stencil-pair-complete-v1 (patchaf36fc5e). All nine normalized source
chains and eight generator CLI checks pass. Added paired target/runner glue.
Schema3 integrity supplementbf1618cc and negative cached-stat correctionffd1df1a
are included. No C++ build/runtime result yet; failure counters can remain stale.

Sealed core complete composition gpu-sealed-videoout-complete-core-v1
(patchc1d275a1) includes census rebase, concurrent Stop/unmap correction,
new REQUIRED baseline remap-lease correctione85cd203 and metadata accessor.
Fixture now explicitly selects Vulkan before worker/mapping creation. Independent
source review found no blocker; baseline/alias/Prepare-Stop execution still needed.
Actual HLE registration/session/content wiring is being reviewed separately.
AA analytic candidate remains private/unexecuted. Preserve all original freezes.

No later pair/sealed/HLE/AA candidate is promoted. No desktop-control tools,
commit or push. All C-only/Uptownfrog/hooks/push.default/privacy/native-runtime/
uncommitted-work/translation/separate-toolchain restrictions remain. Full world,
AA parity, GPU final freshness and stable minimum30FPS at4K remain unfinished.

# Active continuation - 2026-09-12 17:49 UTC

Live source now includes the three reviewed copy reductions plus default-off
publication census, all C++ unbuilt/unexecuted. Latest validated player/game
remains v1z/v14; normal dev0b6610b4 is preserved. Generator raw8fc83f20 / LF6c824769.
Read publication-census-v1/root-promotion-receipt.json and current index/detail.

User is playing Dota and will say when done. Keep game/GPU tests and heavy builds
deferred. No process or new game bundle has launched. The private preparer now
supports longer/later-capture/census and explicit validation controls, default on.
V14 is Release/O2 but includes core/synchronization validation; its overhead
has not been isolated. Inputs stay Cross seconds2–30 with explicit releases.

Private pending work: sealed-core census rebase e5e866c0; actual Prepare/Stop
extension27fc46 plus REQUIRED unmap correctionaea17bf6; first-word metadata API
and HLE registration/session/content-ID wiring; AA analytic fixture4b9ad4f5;
paired D32/S8 helper54d8e604 plus S8-only-fill080c39b1, exact-counter migration
and same-boundary TextureCache integration. None of these candidates is built,
executed or promoted. Read each frozen receipt and preserve original candidates.

Next validation starts with the live copy reductions/census; keep later work
attributable. Longer visible loading and clean validation-overhead controls follow
only after required correctness checks and user resource update. Full world,
AA parity, GPU final freshness and stable minimum30FPS remain unmet.
All C-only/Uptownfrog/protections/privacy/uncommitted/native-runtime restrictions
remain. No desktop-control tools, commit or push.

# Active continuation - 2026-09-12 17:21 UTC

Three copy reductions remain applied but unbuilt/untested; validated v1z/v14
is still the latest player/game evidence. Normal dev0b6610b4 is preserved.
User is playing Dota and will say when done: defer game/GPU tests and heavy builds.

Private sealed GPU final-source core ae6a7a63 has independent source review with
no blocking issue; no HLE glue or runtime validation yet. Separate actual
Prepare/Stop race coverage is being authored. Read gpu-sealed-videoout-v1 and
its review bundle. Native AA stays off: native-vulkan-aa-design-v1 identifies
the required pre-HUD scene/UI proof. Private scene-aa-contract-v1 now authors
an analytic final-swapchain helper oracle, unbuilt/unexecuted/unpromoted.
Publication census and narrow same-boundary D32/S8 batching preparation follow.

Read recipient experiment index/detail and private source-ready/review receipts.
Next executable validation is the existing three copy reductions first; keep
later source candidates attributable and default-off. Then longer visible
loading coverage with fixed Cross seconds2–30 and isolated Timmy copies.
Full world, AA parity, GPU final freshness and stable min30FPS remain unmet.
All C-only/Uptownfrog/protections/privacy/uncommitted-work/native-runtime
restrictions remain. No desktop-control tools, commit or push.

# Active continuation - 2026-09-12 16:57 UTC

Source is now ahead of validated v1z: reviewed HTile mask, owned-snapshot copy and
encoder owned-copy changes are applied, unbuilt and untested. Original bytes and
root-promotion-receipt.json are preserved under recipient private/perf-lab/
htile-clear-mask-v1, owned-snapshot-copy-v1 and encoder-owned-copy-v1.
Latest validated player stays v1z (v14 bundle), normal dev0b6610b4 unchanged.
V14 reached publisher/studio logos with corrected input, roughly4FPS; full world,
AA, GPU-final freshness and min30FPS remain unmet. Read current experiment index.

User is playing Dota and will say when done. Keep game/GPU tests and heavy builds
deferred; source review continues. Next is coordinated compilation/CPU/GPU
regressions of these three changes, then longer visible loading coverage with
the same Cross seconds2–30 and isolated Timmy copies. Sealed GPU final-source
core/fixtures and AA design are still private. All C-only/Uptownfrog/protections/
privacy/uncommitted-work/native-runtime restrictions remain. No desktop-control
tools, commit or push.

# Active continuation - 2026-09-12 16:47 UTC

V14/v1z passed the warning and displays publisher/studio logos. It ran90.309s,
386 unique native IDs/398 presents, unchanged Timmy seed. All29 scripted presses
and29 releases consumed;23 guest presses/releases after early startup polling.
Captures end73.680s at studio logo; title/full world remains unverified.
Cost trace confirms large CPU D32/S8 decodes are gone. Remaining costs are owned
snapshots/publication (33.15%) and encoder host work/fence waits (37.38%).
Different workload/input/captures and possible external load prevent FPS comparison.

User is playing Dota and will tell us when done. Defer game/GPU tests and heavy
builds until then; continue lightweight private code/review. New unpromoted
candidates: htile-clear-mask-v1, owned-snapshot-copy-v1, GPU final-source prototype.
Encoder zero-pass removal and same-publication-boundary batching design follow.
After validation, extend the next visible loading bound; keep Cross seconds2–30,
isolated Timmy copies and private captures. No screen-driven input.

Latest validated player remains integrated-v1z, normal dev0b6610b4 preserved.
Read recipient experiment index and v14 private cost/capture receipts. Full world,
AA parity, GPU final freshness and minimum30FPS remain unmet. All earlier C-only,
Uptownfrog/protections/native-runtime/privacy/uncommitted-work constraints remain.
No desktop-control tools, commit or push.

# Active continuation - 2026-09-12 16:32 UTC

Integrated v1z validates GPU initial 4K HTile D32/S8 decoding: the CPU baseline,
GPU paired exact-byte fixture, three rejection cases and all shared regressions
pass with zero validation errors. Eight initial planes use GPU decoding, with
padding, CPU freshness, mixed clear precision, EOP and retirement preserved.
Evidence: recipient private/perf-lab/resume-20260912-v1/
initial-htile-v1z-validation.json. V13 cost analysis is complete: remaining CPU
D32/S8 decode consumed 42.38% of its measured window. Different workloads prevent
an FPS comparison. V14 is visibly running v1z with corrected timed press/releases
and final captures spaced 45 frame IDs apart; consumed input and game result pending.
Normal dev 0b6610b4 preserved. Full world, AA, final GPU freshness and min30FPS unmet.
Private mask-validator optimization and certified GPU final-source work continue.
All earlier C-only/Uptownfrog/protections/native-runtime/privacy/uncommitted-work
constraints remain. No desktop-control tools, commit or push.

# Active continuation - 2026-09-12 16:17 UTC

v13 proves native display corruption fixed: readable warning/ornaments/overlays
in final GPU frames46/106;211 unique IDs across90.306s, no rejection. Full world
still unverified. Found harness bug:29 issued six-frame commands overlapped into
one long Cross hold. Earlier claims of29 completed taps mean issued commands,
not29 game-observed taps. Future private runner corrected to one-frame capped
presses atseconds2–30 plus explicit450ms releases; needs live validation.
Evidence recipient private/perf-lab/vulkan-compatibility-v13/
layout-and-input-result.json and resume-20260912-v1/timed-tap-release-fix-v1.
Cost comparison pending; initial depth/stencil GPU decode is private/in-progress,
and strict sealed GPU final-frame prototype is privately being authored.
Latest validated player v1y, normaldev0b6610b4 preserved. AA/fullworld/GPUfreshness/
min30FPS unmet. All earlier C-only/Uptownfrog/hooks/privacy/uncommitted-work/native
runtime constraints remain. No desktop-control tools, commit or push.

# Active continuation - 2026-09-12 16:09 UTC

Integrated v1y validates GPU depth/stencil encoding + unchanged HTile Batch3 and
native VideoOut full physical mode10 GPU sampling. Seven GPU encoder/HTile and
nine visible WSI invocations pass; validation0, exactpixels/padding/visibility/
retirement. Explicit legacy-title/native-tiled combination rejects, native
overlays retained. Two compile corrections and WSI fixture no-op correction
preserved privately. Evidence recipient private/perf-lab/resume-20260912-v1/
depth-layout-v1y-validation.json. V13 visible game/capture/cost test now running.
Initial depth/stencil GPU decode is private/in-progress. Fullworld/AA/GPUfinal
freshness/min30FPS remain unmet. Normaldev0b6610b4, all earlier constraints,
uncommitted/unrelated work/protections preserved. No desktop-control tools,
commit or push. Read recipient index/detail; game result pending.

# Active continuation - 2026-09-12 15:54 UTC

Integrated v1v validates exact prepared 4K GPU mode14/10 initial decode: 3 positive
profiles each6GPU/0CPU, ring rollover/current CPU pixels/padding/guard/EOP/retirement
pass; real PS alias rejects unchanged. Six CPU and ten shared GPU regressions pass,
validation0. Evidence recipient private/perf-lab/resume-20260912-v1/
initial-decode-v1v-validation.json. GPU mode10 encoding remains validated.
Native VideoOut tiled-layout fix remains private while optional legacy compositor
and latched-window route guards are completed. Then visible game/cost comparison.
Fullworld/AA/GPUfinal freshness/min30FPS still unmet; depth/stencil GPU conversion
is being authored privately. Normaldev0b6610b4 preserved, all earlier constraints
remain; no desktop-control tools, no commit/push. Read recipient index/detail.

# Active continuation - 2026-09-12 15:54 UTC

Integrated v1u validates GPU display-mode10 encoding: exact helper and production
tests pass pixels, padding, CPU visibility/EOP and retirement; production4GPU/0CPU,
validation0. Actual cost scopes corrected. Evidence recipient private/perf-lab/
resume-20260912-v1/color10-v1u-validation.json. Reviewed prepared4K GPU mode14/10
initial decode is promoted and building as v1v; its new GPU fixture is pending.
Native tiled display candidate remains private until explicit unsupported legacy
title-compositor admission is guarded; native performance overlays remain.
v12 measured CPU codecs at76.8%; full world/AA/GPU final freshness/min30FPS unmet.
Normaldev0b6610b4 preserved; no commit/push, no desktop-control tools. C-only,
Uptownfrog, recipient installed hooks and push.default=nothing preserved; donor
push.default=nothing preserved (donor has no core.hooksPath setting or .githooks).
All uncommitted/private and separately owned work preserved; native foundation,
paused Remill. Read recipient index and linked detailed checkpoint.

# Active continuation - 2026-09-12 15:33 UTC

v12 measured CPU texture Decode/Encode at 23.194 of30.209s (76.8%).
Exact mode14/display10/depth0/stencil0 breakdown in recipient experiment index;
raw private/perf-lab/vulkan-cost-audit-v1/v12-analysis.json. Latest built v1t;
50s visible test finished bound with 53 native IDs, all29taps, unchanged Timmy seed.
Observer rasterizer/scheduler dispatch gaps corrected in source, next build pending;
CPU codec measurements valid. Current private work: preparedGPU4Kmode14/10 decode,
native displaymode10 physical-tail/GPU sampling fix, display10/depthGPU encoder.
v11 captures establish scrambled scene output and correct overlays. Fullworld/AA/
GPUfinal freshness/min30FPS remain unmet. Normaldev0b6610b4 preserved; all work
continues without desktop-control tools. C-only/Uptownfrog/protections/private
artifacts/native runtime/paused Remill/all uncommitted and unrelated work preserved.
Read recipient index and linked detail. No commit or push.

# Active continuation - 2026-09-12 15:21 UTC

v11 native final GPU captures prove scene corruption (gray then black/scrambled
horizontal pixels) with correct overlays. Registered tiling is dropped in native
CPU display route; exact GPU correction/fixture pending. Former HTile/RT gates
stay clear through the90s run; 87 native IDs, all29 taps, Timmy seed unchanged.
Evidence recipient private/perf-lab/vulkan-compatibility-v11/final-capture-result.json.
Current built v1s capture fixtures all pass; normaldev0b6610b4 preserved.
Next: stage timings, GPU initial mode14 decode, native display layout correction.
Work continues without desktop-control tools. All branch/protection/C-only/private
work/native-runtime restrictions remain. Full world/AA/freshness/min30FPS unmet.
Read recipient experiment index and linked detailed checkpoint.

# Active continuation - 2026-09-12 15:17 UTC

Integrated v1s final-swapchain capture is built and passes five visible GPU/WSI
contracts, exact pixels/overlay/encoding/frame identity and full retirement;
no-capture allocates zero readback. Evidence recipient private/perf-lab/
resume-20260912-v1/final-capture-v1s-validation.json. Next visible v11 captures
actual renderer output. Cost-stage profiling and GPU decode candidates in progress.
All work continues with desktop-control tools off. Normal dev 0b6610b4 preserved.
No full world/AA/GPU final freshness/min30FPS acceptance. Read recipient index/detail.
All previous branch/protection/C-only/privacy/native-runtime constraints remain.

# Active continuation - 2026-09-12 15:07 UTC

User explicitly corrected the stop: Computer Use stop was not permission to
abandon work. Continue code/GPU/performance work; desktop-control tools off.
v10 partial logs prove v9 RT gate cleared:70 frame IDs/74presents, continued
through69.5s, no logged rejection. All29 taps/unchanged seed recorded. Agent's
termination makes the run incomplete; no FPS/rendering acceptance.
Next: validate private final-swapchain capture and inspect renderer-owned pixels,
audit per-submission/publication costs. All v1r tests/normaldev/protections and
uncommitted work preserved. Read recipient index/detail for exact evidence.

# User stopped Computer Use - 2026-09-12 14:57 UTC

User pressed physical Escape during v10 window selection. No further UI calls;
owned v10 launcher/test tree stopped and partial logs preserved. v10 is
interrupted/inconclusive, not FPS/rendering acceptance. No new build/test after.
Latest VALIDATED: integratedv1r narrow render-target admission fix + GPU mode14
encoder;7 focused regressions pass. Normaldev0b6610b4 and all work preserved.
Private final-swapchain capture candidate is frozen/unpromoted/unbuilt:
recipientprivate/perf-lab/native-vulkan-capture-v1 (README and exact hashes).
Read recipient index/detail and v10/computer-use-stop.json before continuing.
No commit/push; all prior branch/protection/C-only/privacy constraints remain.
Do not resume Computer Use in this turn.

# Validated continuation - 2026-09-12 14:54 UTC

v1r validates the narrow duplicate-render-target-refresh fix with baseline
reproduction and real tiled/linear GPU draw regression; true PS buffer alias still
rejects. GPU mode14 encoder passes exact4K/odd/swizzle helper and production tests
(4GPU/0CPU), padding/visibility/EOP/Stop validation. All7 focused regressions pass.
Initial macro fixture mode assertion10->14 corrected; failed source/log retained.
Evidenceprivate/perf-lab/resume-20260912-v1/rt-mode14-v1r-validation.json.
Next: fresh visible game run against v9 gate with early titled-window captures.
Fullworld/AA/GPUfinal freshness/min30FPS at4K remain unverified. Native final
swapchain capture candidate private/inprogress. Normaldev/protections/all work
and earlier constraints preserved; no commit/push. Read recipient index/detail.

# Current continuation - 2026-09-12 14:47 UTC

v9 identifies exact image-upload hold (request/backing907a0000+1fe0000), not
coalescence or a raw shader binding. BeginRendering redundantly calls UpdateImage
before FindRenderTarget's prepared refresh; narrow removal and warmed-buffer
render-target fixture are being prepared. All lifetime/alias guards stay.
Caption fix verified; two live game-window snapshots are black. 33 nativeframe
IDs logged; final GPU pixels/AA/fullworld/min30FPS still unverified.
Mode14 GPU encoder extension promoted, not yet built/validated; native final
swapchain capture is a separate private candidate. Read recipient index/detail.
Evidenceprivate/perf-lab/vulkan-compatibility-v9/exact-image-upload-binding-result.json.
Preserve normaldev0b6610b4/all uncommitted work/protections and prior constraints.

# Current continuation - 2026-09-12 14:37 UTC

v8 diagnostic proved current buffer binding only (mask2), no prior GPU producer:
base907a0000/bytes1fe0000,4K RGBA8 mode14. Exact request/backing/purpose
diagnostics and default native window caption initialization are now building
asv1p. Prior ordered-publication candidate remains private; cannot fix v8 alone.
Live capture returned unrelated foreground pixels and is unusable; retry needs
verified titled window, early activation/capture. 33 native frame IDs recorded.
Latest evidenceprivate/perf-lab/vulkan-compatibility-v8/current-binding-result.json.
Read recipient index/detail before repeats. Stable30FPS/AA/fullworld/GPUfinal
freshness remain unverified. Preserve all constraints and earlier validated work.

# Current continuation - 2026-09-12 14:27 UTC

Validated integrated v1n: exact game HTile profile, production GPU encoder
(4GPU/0CPU fixture encodes, exact native bytes, allocation0 afterStop),
same-batch buffer->detiler dependency and prior image/WSI regressions pass.
Initial dependency fixture's linear pitch error and log classifier false-positive
are recorded, originals preserved. Read recipient index/detail before repeats.

Visible game v7 cleared HTile and logged33 unique native Vulkan frame IDs.
New gate at32.376397s: image writer overlaps buffer producer or current binding.
90s bounded sessionprivate/workspaces/20260912T141616-23dd7ae2 ended timeout239.
Screenshot attempt missed live interval: visual result inconclusive.
Next: bounded alias diagnostics and ordered-publication GPU fixture, then a
fresh visible run with early screenshots. All publication/lifetime/alias guards
stay. Stable30FPS at4K+AA, full world and GPU final-image freshness remain unmet.
Latest evidenceprivate/perf-lab/vulkan-compatibility-v7/native-wsi-and-alias-result.json.
Normal dev0b6610b4 preserved; HEADfa47b5b3/Uptownfrog/hooks/pushnothing remain.
All changes uncommitted; C-only/explicitcwd/Timmycopies/Cross2-30/private data,
translations/tools/liverpool/_recomp/native runtime/paused Remill preserved.

# Validated continuation - 2026-09-12 14:02 UTC

Integrated v1m strict HTile/Batch3 builds and passes six CPU contracts plus
four positive real GPU draws and all four intended rejection cases. Positive
Z/S/HTile bytes, padding/guards and EOP match; zero validation errors through
device destruction. Evidence: recipient private/perf-lab/resume-20260912-v1/
strict-htile-v1. Actual game profile (v6 surface8/depth_info1d0c41) still needs
its separately justified support and tests. Encoder wiring and buffer-to-detiler
integration are next, not yet validated. No Vulkan FPS/AA/full-render acceptance.
Normal dev unchanged; C-only, explicitcwd, Uptownfrog/hooks/pushnothing,
private inputs/Timmy copies/visible tests/Cross2-30/unrelated work preserved.

# Current continuation - 2026-09-12 13:50 UTC

User resumed the 02:43 shutdown checkpoint. All12 frozen source hashes,
all3 preserved v1l binary hashes and original normal dev0b6610b4 match.
Visible v6 with v1l and BB_VULKAN_PRESENT=1 captured the missing raw depth
registers: DEPTH_INFO=0x1d0c41, HTILE_SURFACE=8 (PRELOAD, no FULL_CACHE).
The strict private HTile profile does not cover this state. After50 submissions,
the same output gate rejected at2.118470s; 45s bound ended at45241ms,
entry_timeout/239. Native game WSI output, AA/freshness and FPS remain unverified.
Timmy seed unchanged; visible desktop and all Cross2-30 taps recorded.
Evidence: recipient private/perf-lab/vulkan-compatibility-v6/raw-depth-result.json.

Strict HTile/Batch3 source promotion plus CPU/GPU fixtures, GPU encoder wiring,
and a same-batch buffer-to-detiler fixture are in progress, unbuilt. Read the
latest recipient experiment index/detail before any new run. Stable30FPS at4K+AA
remains unmet. Preserve C-only/explicitcwd/Uptownfrog/.githooks/pushnothing,
all uncommitted work/translations/tools/liverpool/_recomp/private inputs, native
x86-64/HLE/player and original normal dev; Remill/AOT stays paused. No commit/push.

# SHUTDOWN HOLD - 2026-09-12 02:43 UTC

USER REQUESTED STOP FOR PC SHUTDOWN. Resume only after a new user instruction.
No game/build/test remains running. All agent work frozen. Stable30FPS at4K+AA
unmet; reliable normal performance remains about13.3FPS. No Vulkan FPS gain.

Latest integrated build v1l succeeds. Actual runtime Vulkan display mailbox/WSI
tests passed visibly in1.882/1.746s, including resize/minimize/reopen and both
retirement paths; zero validation errors through destruction. Evidence:
recipient private/perf-lab/vulkan-runtime-display-v1/runtime-wsi-v1.
Earlier v1k mode10 full4K native write/read tests and GPU tileencoder full4K HDR
pass with exact bytes/padding/EOP, validation0; combined evidence
private/perf-lab/vulkan-combined-v1k. Encoder is NOT wired to TextureCache yet.

Game v5 child38cda318... sessionprivate/workspaces/20260912T023449-40d28ceb:
passesmode10/50submissions; new HTile output gate at2.013665s. D32S8mode0,
3840x2160,pitch3840,physical2176,one mip/layer/sample,htile0x94f58000.
One rawframe from oldD3D11presentation, no complete rendering/FPS. Timed out
120231ms/entry_timeout/239. Live-read attempt afterward refused; no reads.
Existing rawdepth LOG_WARNING was not captured; v1l now sends22rawfields to
gnm-vulkan event log beforeFindImage. That improved diagnostic has not run in game.

Root wired native FrameWindowHost behind BB_VULKAN_PRESENT=1; existingGPUworker
owns bounded display queue, UI pumps, producer reads occur outside frame mutex,
positive retirement precedes HWND destruction, reattach requires proof.
Native game-window WSI path untested. Final-image AA, capture parity and GPU
freshness remain pending. New tiled-input compute-read barrier compiled;
same-batch GPUbuffer-producer→detiler fixture still pending.

Private HTile/Batch3 candidate is UNPROMOTED/UNBUILT:
private/perf-lab/vulkan-htile-display-rebase-v1/promotion.patch SHAb4fb15df...
based on current mode10/array/volume/compute-input barrier. Strict eligibility
requires stencilbit29, HTILE_SURFACE2or3, DEPTH_INFO0; no combined compression.
HTile GPU fixture unfinished at stop. Packed raw6/raw9 private draft also pending.
See latest recipient experiment index/detail for all exact hashes and repeat rules.

Next: verify protections, finish strict HTile CPU/GPU validation, capture actual
raw depth state in fresh visible game run, trial validated runtime WSI, integrate
the verified GPU encoder without removing CPU visibility/publication barriers.
Native x86-64/HLE/player retained; Remill/AOT paused; cleanup merge not repeated.

HEADfa47b5b3c99b13b91c12692a2e108bf5a1b60412/Uptownfrog. Normal dev full
0b6610b406a46ccdb6dfbb4d29f6abd3c3459066811bb9da9dc9a94186430afe reverified.
All current changes uncommitted. No normaldev overwrite/commit/push. Preserve
C-only explicitcwd, .githooks/pushnothing/exactUptownfrog recipient refs/no donor
push, private inputs/preferences/Timmy copies/visible runs/Cross2-30, translations
and tools/liverpool/_recomp ownership. Never access another drive.

# Current continuation - 2026-09-12 02:19 UTC

Volume support passes CPU and real GPU tests (16-cubed, odd11x9x5, XYZ padding,
native bytes/EOP, zero validation errors). Integrated v1j; exact evidence
recipient private/perf-lab/vulkan-combined-v1j. Prior arrays still pass.

Actual game v4 (private/workspaces/20260912T021224-c5a597e0, child6825dfdf...)
clears the volume gate and completes46 submissions. Next exact gate at1.252104s:
RGBA8 UNORM3840x2160,pitch3840,physicalheight2176,mode10Display2DThin,one
mip/layer/sample,no metadata/depth. No game window/frame or FPS. Root stopped
the identified failed child deliberately; final faultstatus follows thatstop.
Timmy seed unchanged, all Cross2-30, WinSta0/Default confirmed.

Memory agent implements mode10 codec/admission; resource authors its GPU
input/output fixture. Dxvk agent implements GPU tile encoding. Root authored
bounded GPU-worker display mailbox, unbuilt; native window wiring/visible
integration test pending. Standalone WSI passed earlier. Private HTile and packed
drafts are frozen/unpromoted. No repeated old microbenchmarks.

Stable30FPS unmet; normal dev full0b6610b4 reverified beforev4. Native x86-64/HLE/
player foundation retained; Remill/AOT paused. All hot runtime code is C++.
No current game/build/test, no commit/push. C-only explicitcwd, Uptownfrog/hooks/
pushnothing, privacy/Timmy copies/visible tests/Cross2-30/translations/_recomp
ownership remain. Latest recipient index/detail holds exact receipts.

# Current continuation - 2026-09-12 02:08 UTC

Integrated v1i passes CPU texture/memory plus real GCN graphics, array and native
HLE/ASC GPU contracts with zero validation errors. Exact private evidence:
recipient private/perf-lab/vulkan-combined-v1i. Array views/padding/CPU edits are
covered. The prior v1h fixture compile failure is preserved separately.

Standalone Vulkan WSI presenter passed visibly on WinSta0/Default,36 presents,
overlay, resize, minimize/restore, bounded retirement; zero validation errors.
Evidence: private/perf-lab/vulkan-present-v1/first-wsi-v1. It is NOT wired to the
game FrameWindowHost yet. No pixel/AA parity or FPS claim.

Game v3: private/workspaces/20260912T015500-8edeaa81, child15715524...,
package private/perf-lab/vulkan-compatibility-v3. First dispatch/EOP completed.
Next input tiling gate failed at0.759167s before any game window/frame. New
cached CS0x83450e2f identifies R8 UNORM Color3D16-cubed, mode19 Thick1DThick;
this is associated evidence, not an exact input-gate descriptor yet.
Root deliberately stopped the positively identified failed child; final fault
status follows that stop. Timmy seed unchanged, Cross2-30, verified desktop.

Mode19/R8 true-volume codec/upload/readback is source-frozen, unbuilt; authored
CPU/GPU volume fixtures cover exact16-cubed and odd padding. Next compile/test
then new visible game run. Detailed input diagnostics are included. Independent
GPU tile encoder source work continues. HTile/packed-format drafts stay private
and unpromoted. Native presenter mailbox/window integration remains root work.

Stable30FPS unmet; last reliable normal FPS about13.3. Normal dev full0b6610b4
hash preserved before v3. Frame/runtime/renderer code is C++; Python only
orchestrates offline builds/tests. Native x86-64/HLE/player stays the foundation;
Remill/AOT remains paused. No active game/build/test at this checkpoint.

All C-only explicitcwd, Uptownfrog/.githooks/push.default=nothing, exact recipient
publication only/no donor push, privacy/Timmy copies/Cross2-30/visible game tests,
translations and tools/liverpool/_recomp restrictions remain. No commit/push.
See latest recipient index/detail for exact receipts and repeat rules.

# Current continuation - 2026-09-12 01:29 UTC

Native GNM/ASC -> Vulkan routing and shader-module lifetime fixes compiled and
passed authored real GPU validation: exact pixels, EOP, fragmented/wrapped ASC,
cross-queue wait release, native unmap/stop; zero validation errors. Frontend and
reader-admitting lifetime CPU fixtures pass. Evidence: recipient
private/perf-lab/vulkan-hle-v1. Original leak failure remains preserved.

First actual Vulkan game: private/workspaces/20260912T011943-bd1867ea, package
private/perf-lab/vulkan-compatibility-v1, child784ba31e... . Verified WinSta0/Default,
Timmy copy and Cross2-30; seed unchanged. Generic output-layout admission failed
at0.768569s BEFORE first window/frame;120s timeout, no FPS result. Depth metadata
diagnostic never fired, so do not assume HTile was reached. Prelaunch Python
import failure is separately retained. Root is adding exact rejection fields.

V2 exact diagnostic (private/workspaces/20260912T013038-71be2f61) identifies the
first rejected image: R32Float, Color1D,1025x1,pitch1032,physical_h8,mode13,3layers;
shader metadata view selects onlylayer0. No metadata/HTile involved at this gate.
Memory agent implementing real array codec/subset publication; resource agent
authors matching GPU test. HTile/Batch3 private draft stays frozen/unbuilt.
Presenter core source work continues; root authored optional bounded Win32
device-extension selection (sourceverified, unbuilt). No active game now.
No accepted performance gain; stable30 unmet. Normaldev full0b6610b4 preserved
(last01:18UTC). Native x86-64/HLE/player foundation; Remill/AOT remains paused.

Gaming hold released; future game runs visible. C-only explicitcwd, Uptownfrog,
.githooks/push.default=nothing, exact recipient publication only, no donor push.
Private game inputs/preferences, Timmy copies, Cross2-30, translations and
tools/liverpool/_recomp ownership preserved. No commit/push.
See latest recipient experiment index/detail for exact evidence and next gate.

# Current continuation - 2026-09-12 01:06 UTC

First authored real Vulkan draw produced256 exact red pixels/padding/EOP, but
validation FAILED on2 leaked shader modules at device destruction. Binaries,
logs and nine manifests preserved recipient private/perf-lab/vulkan-graphics-v1/
first-draw-v1. D32/S8 CPU0.12/0.45s, importedPM40.16s and DMA validation passed.
No game/FPS proof; stable30 unmet. No normaldev overwrite or commit/push.

Module RAII+per-instance validation counters are source-frozen unbuilt. Root
wired native GNM/ASC, publication and memory-retirement source; new HLE GPU
contract unbuilt. Registry lifecycle CPU fixture frozen. Read-only review caught
and fixed pre-admission EOP suppression/cache namespace; reader-admitting
lifetime guard is being authored to avoid writer-preference deadlock.

Actualclinic HTile is the next known compatibility gate. Private bounded Z-only
HTile+atomic3-range publication draft in progress; actual mode/bytes eligibility
unknown. Metadata gates retained. GPU-resident resource updates/presentation
remain architectural performance work after compatibility, as Unleashed audit
recommended. Normal x86-64 bbexec/HLE/frontend preserved; Remill/AOT paused.

Gaming hold released. Future game runs visible, Timmy copies, Cross2-30. All
C-only/Uptownfrog/hooks/pushnothing/privacy/translations/_recomp constraints.
See latest recipient checkpoint index/detail. No game/build/test running now.

# Current continuation - 2026-09-12 00:41 UTC

First real Vulkan GPU service pass: DMA fill/copy, overlapping CPU WRITE_DATA,
EOP bytes/order/padding and unmap/stop PASSED1.13s. Imported PM4 CPU0.15s and
TLS0.16s passed. Exact binaries/logs/source manifests preserved under
recipient private/perf-lab/vulkan-service-v1/validated-dma-v1.
Normaldev full0b6610b4 hash unchanged at00:34UTC. No game/frame/FPS result.

Vulkan validation-request run failed because Khronos layer unavailable.
Source discovery delegated; no global SDK/driver install. Actual game routing
unfinished. Memory agent is landing D32/S8+atomic pair publication; dxvk owns
authored graphics fixture and released new register/hint bounds (unbuilt);
resource handles portable validation layer. Root owns routing/CMake/docs.

Unleashed comparison confirms remaining costs: current fresh snapshots,
unconditional buffer CPU checks, eager publication and CPU texture encoding
remain. Need explicit covered resource updates/lifetimes + GPU surface reuse
and presentation; a Vulkan cache alone is not30FPS proof. Stable30 unmet.
No repeats of parked experiments, no normaldev overwrite or commit/push.

Gaming hold released; future game runs visibly on normal desktop. All C-only/
Uptownfrog/hooks/push.default=nothing/Timmycopies/Cross2-30/privacy/translations/
tools/liverpool/_recomp constraints retained. See latest index/detail.

# Current continuation - 2026-09-12 00:13 UTC

The user released the gaming hold. Isolated C++ builds/tests have resumed.
All six current CPU contracts pass (Liverpool fixture fix retested0.13s).
Nine current GPU overlays emitted together. Adapted configure passed; first
GPU compile failed only on missing DivCeil include and log category. Both fixed;
v2b rebuild passed44.21s: all96 GPU/shader objects compile. No service link/device
execution yet. All failure logs and compiled-adapters-v2b.json retained.

Native bbexec x86-64/HLE/player + GPU-only Vulkan remains locked. No upstream
Core/app/frontend. Service and HLE routing unfinished. Buffer unmap detachment
being implemented; texture stencil/meta/mips compatibility still gated. No
Vulkan device/game/FPS proof, stable30 unmet, normaldev0b6610b4 untouched.
Next: finish link, imported PM4 contract, real device/render checks, visible game
and clean FPS. No repeated parked microbenchmarks. See latest index/detail.

No commit/push. C-only explicitcwd, Uptownfrog/.githooks/push.default=nothing,
private game inputs/preferences, Timmy copies, Cross2-30, visible future game
tests, translations and tools/liverpool/_recomp ownership remain.

# Resource window released

The user has finished Dota and explicitly reopened builds/tests. The gaming hold
below is historical. Root is starting current Vulkan CPU contracts and import
compilation; all future game runs must be visible. Normal dev remains preserved.

# Current continuation — 2026-09-11 23:46 UTC

USER GAMING HOLD REMAINS: source work only; no build/contracts/GPU/game/FPS
until the user releases the resource window. All agents know this.

GPU-only Vulkan under bbexec native x86-64/HLE/player remains locked. Stable30
unmet; normal dev0b6610b4 untouched, last hash22:44. No commit/push.

Root added pinned rasterizer ownership/publication + explicit pipeline config,
source-verified only. Device/shader/program CMake source selection passed23:26:50
(98 files, no configure/compiler). Program optional global-profile fetch dump
removed; actual owned decoding preserved. Current v2 generated tree is STALE
relative to evolving generators; regenerate all manifests together after freezes.

Buffer7102743b freezes prepared-writer/backing retention and reciprocal alias
gates. Memory agent is implementing texture encoder/cache + narrowly reopening
memory for typed texture output. Shader/liverpool/host support source freezes
exist privately, all current contracts unbuilt. Dxvk now owns scheduler bounded
error/drain + runtime.cpp; device generator scheduler ownership transfer pending.
Resource owns explicit PipelineConfig/cache_storage and residual shader settings.
Root owns rasterizer/program/CMake/docs. Separate tools/liverpool/_recomp untouched.

BB_BUILD_VULKAN_GPU_LIBRARY default OFF now prepares optional service archive;
requires nine overlays + real runtime, excludes upstream PageManager and unused
raw shader HLE. Not configured/linked and does not select a game backend.
Need complete texture stencil/meta/mip compatibility, scheduler/service, HLE
routing, then full visible rendering and clean repeated FPS after hold released.
Preserve every failed/inconclusive result. See latest index/detail entry.

C-only explicitcwd/Uptownfrog/.githooks/push.default=nothing/private language/
Timmycopies/Cross2–30/visible future tests/translations all retained.

# Current continuation — 2026-09-11 23:15 UTC

USER IS GAMING: source work only. No game/GPU tests, heavy builds or FPS
measurements until the user releases the resource window. All agents notified.
No new runtime/game/build workload launched after that notice.

Keep the locked GPU-only Vulkan rewrite under bbexec native x86-64/HLE/player.
No shadPS4 CPU/app/frontend integration. Remill/AOT remains paused.
98 GPU/shader objects compiled before hold; memory contract passed0.13s,
CTest0.15s (8b8d6c9f). Neither result is gameplay or FPS improvement.

Root added CMake verified overlay selection and owned shader program/fetch
acquisition, separate guest-base provenance, checked decoder spans. Six program
transforms pass source-only verification in private/perf-lab/vulkan-program-v1.
Existing SRT root-boundary read hardened; regression cases authored, not run.
Runtime.cmake/tests registration now includes Vulkan Liverpool/shader/program.
Do not mistake these unbuilt edits for the earlier passed memory binary.

Agents still own changing sources: resource shader/SRT helper+six overlays;
memory adding atomic Semaphore64 after buffer-overlays freeze; dxvk evolving
Liverpool owned coroutine jobs/tokens/indirect/ASC, not yet frozen.
Device generator frozen; buffer generator frozen. Await all new freezes before
combined generation/build. Root owns program generator, CMake and docs.

Still missing linked service, host scopes/callback wiring, texture cache/guest
layout encoder, BDA/active-command admission. Unsupported work must fail before
GPU issuance; never silent no-op tracker, zero-fill or early completion.
Normal dev0b6610b4 unchanged; last hash verification22:44. No commit/push.
Stable30FPS unmet. See latest index/detail23:15 for exact status.
C-only explicitcwd/Uptownfrog/hooks/privacy/Timmycopies/Cross2–30/visible future
tests/translations/Liverpool ownership all retained.

# Current continuation — 2026-09-11 22:50 UTC

LOCKED user direction: big GPU-only Vulkan rewrite; KEEP bbexec native x86-64
loader/HLE/frontend/game/save/input. Do NOT build a renamed full shadPS4 app.
Full-core plan cancelled before build; authored2files archived privately.
See docs/vulkan-gpu-rewrite.md and latestindex/detail22:50 for exact state.

Active C-only build/vulkan-gpu-v1 GPU+shader OBJECT import compilation, no Core,
app or CPU sources; no linked backend/game run/FPS gain. Root ownsCMake;
resource ownsdevice/platformoverlaygenerator+deviceheader; dxvk ownsGPUservice
header+Liverpooloverlays; memory ownsVulkan memoryadapter+focusedfixture.
Use current agent freezes before editing/building their files. Pending service,
layout conversions and callbacks must preserve existing barriers/CPUvisibility.
No native page protection or no-op PageManager allowed.

D3D12 selectedpass, newdebugger and extra native-resourcehooks STOPPED.
D32S8 authoredGPU tests passed4090/WARP; actualdepthRDCexportv2 failedschema,
no replay. NewnativeDRAW+originalrelays/callbacks compiled,6focusedpass0.78s;
no further live marker-only run. Efficiency audit:4.72ms selecteddepthcannot
bridge41ms gap to30FPS; avoid more prerequisite loops.

Normaldev0b6610b4 verifiedunchanged22:44. No game/GPU test running, no commit/push.
C-onlyexplicitcwd/Uptownfrog/hooks/privacy/Timmycopies/Cross2–30/visibletests/
translations/Liverpoolownership unchanged. Stable30FPS stillunmet.

# Current continuation — 2026-09-11 22:06 UTC

Native hook child71b64b4b passed61/fullvisible twice; normaldev0b6610b4 preserved.
Capture1656ba4a selectedevent25 is actual D32S8, so strict R32/D32 exporter rejected
before texture data. No actualgame-depth D3D12 replay yet. Failure preserved.

ACTIVE sources: memory owns D32S8 enum8/backend/codec/queueenum+validation/GPUfixture
and privateexporter. Root owns private converter, requiring exact native SRV/DSV
creation descriptor because RenderDoc normalizedtuple conflates depth/stencil.
Resource owns native_draw_packet newheader/cpp/fixture+GNMactualDRAW metadata.
Root updatedboot/CMake/privategenerator/harness native_draw_trial496cca89.
No new integratedbuild yet; waitsourcefreezes then nativeDrawBuild storedcommand.

dxvk read-only ownership/prologue-original-hook design. Found exact creation219f130,
CPUacquire2169c30 (submit/wait thenpointerreturn), pixelfree216d1e0. Needlivejoin,
aliasclosure and safe callableoriginalbodyhooks. This is largergraphicsarchitecture,
not staticfaultwork. No barrierremoved/guestGPUenrollment/gameD3D12 yet.

No game/build/test running. Latestindex/detail has failure/progress. C-onlyexplicit
cwd/Uptownfrog/hooks/privacy/Timmycopies/Cross2–30/visibleDefaultdesktop/translations/
Liverpool rules preserved. No commit/push. Stable30FPS remains unmet.

# Current continuation — 2026-09-11 21:52 UTC

Full61 passed22.26s. Frozen native-hook child71b64b4b private/prepared/native-depth-
hook-v1; normaldev0b6610b4 preserved. First visible120s run21832 completed full
clinic/HUD/hardware, all40 foreground/visible,30closed semantic matches and2
pre-arm missing, zero invalidations/duplicates. Diagnostic11.639FPS is notclean.

Second same-child visible capture run54596 /20260911T215016-1f852686 is completing.
RDC saved at private/reports/native-depth-hook-v1-capture/gpu-debug/capture-54596_capture.rdc.
First run arm-token typo fixed in harness738a105b; failure preserved.
Next: after verified child exit, memory agent exports/converts selected depth
RDC and root runs actual D3D12 replay parity. No other GPU workloads meanwhile.

dxvk read-only resource pointer/creation/lifetime investigation; resource agent
actual DRAW boundary memo+live marker analysis. Native setup emits extra draws,
so SetPS does not establish unique DRAW ownership. Shared sources frozen.
No guest enrollment, barrier removal or gameplay renderer switch; stable30
unmet. C-only/Uptownfrog/hooks/privacy/saves/translations/Liverpool preserved.
No commit or push. Latest index/detail records complete limits/results.

# Current continuation — 2026-09-11 21:49 UTC

Actual offscreen depth backend passes RTX4090/WARP with debug layer, including
R32/D32, strip, LESS_EQUAL/write, immutable versions and padding. Source core
eaa5c98e fixed missed legacy-format ceiling; failed attempts preserved.
Evidence private/perf-lab/renderer-depth-gpu-v1/RESULT.md; executable8586b966.

Full native-depth-hook-v1 build/61 contracts currently RUNNING in build/perf-dma.
Root owns boot/CMake/private descriptor (known_image_v2.hpp e87b8ebc).
All agent sources frozen. dxvk now read-only CPU pointer/lifetime boundary;
resource read-only actual DRAW emission boundary; memory prepared private
RenderDoc depth exporter awaiting a selected capture/GPU window.
No game running; upcoming test visible WinSta0/Default, isolated Timmy, Cross2–30.
No barrier removed; no guest GPU ownership or gameplay D3D12 yet. Normaldev
0b6610b4 preserved. C-only/Uptownfrog/hooks/privacy/translations/Liverpool rules
unchanged, no commit/push, stable30FPS unmet.

# Current continuation — 2026-09-11 21:18 UTC

Full59 contracts passed22.27s, including actual D3D12 closed4/256-draw passes
on RTX4090/WARP with exact pixels, immutable versions and padding. Sealed f764
replay stays byte-exact on each adapter. Frozen rendererf3cdc2a2 at
private/prepared/renderer-closed-pass-v2; no game FPS gain claimed.

Visible owner-v3 session20260911T210844-33231ed2 child37780ef6 completed120s,
controlled exit3. Complete clinic/HUD/hardware preview inspected.30 exact
native depth-pass/resource joins; first2 pre-arm emissions explicitly unarmed.
Actual bias1ef32720000, extra returne5b77e/first parentreturne5b30f, vtable53b6860.
Resource agent maps exact SCE relocations/access/lifetimes now. Diagnostic11.966FPS
is not a clean comparison. All40 samples visible/nonminimized, foreground2.5%.

Native wrappere5b2d0 (117B) is the next hook candidate: preserve its getters and
both unmodified e5b350 calls/native state effects, add semantic packet markers.
Queue agent designs checked5-arg callback/whole-image guard. Root owns boot/CMake.
Memory agent owns D3D12 header/codec/backend/GPUfixture plus queue format enum
for R32/D32 depth-only strip family. Do not build until all owned source freezes.

No game/build/test running. Normaldev0b6610b4 unchanged; no production hook or
barrier removal. Small tuning/static-fault work parked. C-only explicit cwd,
Uptownfrog/.githooks/push.default=nothing, isolated Timmy seed17, Cross2–30,
visible Default desktop, language/privacy/hardlinks/translations/Liverpool
ownership preserved. No commit/push. Stable30FPS unmet.

# Current continuation — 2026-09-11 20:53 UTC

Actual D3D12 owned renderer now works for the captured4K f764 pass: byte-exact
versus previous D3D11 on RTX4090 AND separately on WARP. NVIDIA-vs-WARP retains
known1-code differences; no tolerance relaxed. Authored realGPU tests passed
hardware0.48s/WARP0.12s with debug layer. Queue CPU contract passed0.10s.
Frozen sources/executablec9b047e8/logs/reports private/prepared/renderer-queue-gpu-v1.
This is no game FPS result; normalgame staysD3D11, normaldev0b6610b4 untouched.

Agents now implement a CLOSED many-draw pass (one output generation/encoding,
not clone-per-draw). dxvk_probe owns queue header/core/contract; memory_hotpath
owns D3D12 header/codec/backend/GPUcontract. All guest enrollment still rejects.
resource_hotpath owns two-extra-ancestor guarded depth-pass context observer.
Static pass e5b350 and parent e5b2d0 are linked to exact da541/e680 inputs; live
confirmation/CPU ownership pending. Root added post-Commit actual image config
call; do not compile until agent API and all source freezes arrive.

No game/build/test running. Full56 earlier passed21.69s; newqueue andGPU targets
passed focused tests afterwards. Next: build/deeper visible provenance run and
closed-pass GPU parity, then establish actual native resource access boundary.
Latest recipient index/detail entries record outcomes/limits. No production
entry replacement or barrier removal. Small tuning/static-fault work parked.
C-only explicit cwd, Uptownfrog/.githooks/push.default=nothing, Timmy seed17 copies,
Cross2–30, visible Default desktop, language privacy, unrelated translations and
Liverpool ownership preserved. No commit/push. Stable30FPS remains unmet.

# Current continuation — 2026-09-11 20:38 UTC

Larger architecture active. Full56 contracts passed21.69s after fixing the1MiB
GNM reset temporary. Entry helper tested, no production entry enabled. New
neutral queue and actual D3D12 drawing adapter are source-only pending review,
compilation and GPU tests. Guest admission always rejects pending ownership.

Visible session20260911T203050-e3e91288 childd9a0272a has complete clinic/HUD/
hardware panel and32/32 matched depth callers. ActualRVAchain1075405 ->26c031b
->2169730 ->227407c; resource agent maps enforceable resource/pass boundaries.
Diagnostic12.452FPS, not a clean comparison. Normaldev0b6610b4 unchanged.
No game/build/test currently running. Latest index/detail entry has evidence.

Source ownership: resource_hotpath static boundary mapping; dxvk_probe queue
header/core/contract; memory_hotpath temporarily owns orbis_renderer_d3d12.cpp
and tests/contracts/renderer_d3d12.cpp for reflection admission fixes. Root owns
CMake/build/visible runs, recipe/header and docs. Wait for source freezes before
build. BB_ENABLE_D3D12_RENDERER_EXPERIMENT defaultsOFF; all publication stays.

Small tuning/static-fault work remains parked. C-only explicit cwd, Uptownfrog/
.githooks/push.default=nothing, isolated Timmy seed17, Cross2–30, visible Default
desktop, language privacy, translations and Liverpool ownership preserved.
No commit/push. Stable30FPS unmet.

# Current continuation — 2026-09-11 19:56 UTC

USER REDIRECTION: pursue the larger replacement graphics/resource architecture.
Do not continue small transfer/scan tuning or new static-fault tooling.
Read private/reports/renderer-architecture-research-2026-09-11.md.

Interval candidate b628ed4b passed55+5 checks and a complete visible clinic run.
Clean ABBA was cancelled before starting; no FPS conclusion. All evidence is
private and preserved. Selector/fixture/CMake restored to7907/1ec1/3a59 base.
Normaldev0b6610b4 unchanged. No game/build/test currently running.

Primary work: explicit CPU access, resource lifetimes/generations and retained
GPU contents above PM4. Resource agent owns the selected non-null PS caller/
frozen-packet provenance extension in GNM source/header; memory agent maps
native interception; dxvk agent designs a queued-renderer vertical slice.
No agent workload granted. Root owns CMake/build/visible runs. Keep all current
publication until ownership is established; unknown native access stays eager.
Liverpool directory remains separately owned/read-only.

C-only explicit cwd, Uptownfrog/.githooks/push.default=nothing, Timmy seed17
copies, Cross2-30, visible Default desktop, private language preferences,
translations and Liverpool work remain preserved. No commit/push.
Stable30FPS at4K/AA remains the active unmet goal.

# Current continuation — 2026-09-11 19:44 UTC

Native pre-fault stack bracket passed all136 authored cases across four actual
alignments. It is not runtime integration; general writer/relocation coverage
is unproven. Dispatcher-entry test finds red-zone corruption already present
before user dispatcher memory access; park late-handler rescue.
Corrected ELF/EH census distinguishes null FDEs;49.2113% gross metadata coverage
is not instruction/writer coverage. Details and limits at END of both recipient
checkpoint documents; private raw reports preserved.

Current root workload: interval-selection source44304ed5 is building in
build/perf-dma, exec6843, full55 contracts plus five explicit interval modes.
No game/profiler running. No other workload is active; agents have read-only
design/source work. Interval source is default-off and has no FPS result.
New research memo proposes enforceable resource/CPU boundaries above PM4;
actual creator/accessor/destruction functions remain to be mapped.

D3D12 transfer-only experiment has NO FPS gain; keep disabled. Renderer and
presenter remain D3D11, so its label is correct. Simple two-draw worker parked
at~1.43ms optimistic bound. Do not repeat unchanged experiments.

Normaldev SHA0b6610b4 freshly verified19:41. C-only explicit cwd, Uptownfrog,
.githooks/push.default=nothing, visible game runs, fixed Cross2-30, isolated
Timmy seed17, private language preferences, translations and Liverpool work
remain preserved. No commit or push. Stable30FPS remains unmet; goal active.

# Current continuation — 2026-09-11 19:23 UTC

D3D12 image-transfer experiment passed correctness but has NO convincing FPS gain.
Four fully visible/foreground runs: pooled ordinary13.290416 versus D3D12
transfer13.232699FPS (-0.4343%, control drift+0.4592%). Keep disabled/private.
It never replaced the D3D11 renderer/presenter; the visible D3D11 label is correct.
Frozen child94290588 and all sources/reports remain private. Full54 contracts
passed20.65s. Actual clinic and hardware panel were complete.

Refined draw census childaaf1dc5e (source792e8991) passed four focused contracts
after the full54 baseline. Visible session20260911T191759-199ff2c5 complete,
hardware panel ON, D3D12 OFF. Approximately25.9% of clinic draws occur in its
relaxed runs, maximum10; optimistic neighboring-duration bound only~1.43ms/frame.
This does not prove safe overlap. Park the simple two-draw worker hypothesis.
The original singleton-only result was a classifier limitation, not proof.
See newest detailed entries at END of recipient checkpoint index and detail.

Native first-chance probe observed intact red zone before/after context query,
then upper-YMM damage before VEH in the SAME child. Exact old-mask comparison
was inconclusive and retained. New boundary result is narrower, not a repair.
All probe processes exited. Memory agent is authoring a private dispatcher-entry
hardware-breakpoint discriminator; no compilation/run grant yet, no game attach
or Windows disk patches. Broad runtime protection arming remains unproven.

No root game, build or profiler is running at this checkpoint. Subtasks:
memory_hotpath: private debugger gate source;
dxvk_probe: bounded read-only ELF/EH coverage of the imported module;
resource_hotpath: bounded ordered publication-selection optimization source,
if its disjointness/order/completion proof holds. Coordinate builds/probes/games.
Its measured scan ceiling is only1.699ms, not the whole resource cost.
Liverpool delivered its tool and has no running or queued workloads; preserve
its directory and note strict WARP pixel differences in its own handoff.

C-only explicit cwd, Uptownfrog/.githooks/push.default=nothing, fixed Cross2-30,
isolated Timmy seed17, visible Default desktop, normaldev0b6610b4, language
privacy and unrelated translations are preserved. No commit or push. Stable
minimum30FPS at4K/AA remains unmet; continue substantive direct-runtime work.

# Current continuation — 2026-09-11 19:01 UTC

The complete finite-wait off/on/on/off repeat found no convincing FPS change:
13.381064 control versus 13.356655 enabled (-0.1824%, control drift 1.3804%).
Its large socket CPU benefit remains separately measured. Four games finished;
reports private/reports/net-finite-wait-v1-balanced-r2. Do not repeat this fix
as an FPS hypothesis. All windows were visible/nonminimized; focus varied.

D3D12 owned readback now builds and passes all 54 contracts (20.65 s), including
strict real D3D12 publication with zero fallbacks/CUDA counters. Independent
source review found no blocker. Frozen private/prepared/d3d12-owned-runtime-v1
child 942905884a6a8aea690a61fa765834d47447d0cfc94173aa06d0af09e56c45ac.
All CPU visibility/lifetime/padding/version barriers remain. Default-off build
and runtime gates; this is not a full D3D12 renderer or product portability proof.

No root game/build/profiler is running at this checkpoint. Liverpool has the
explicit 40-second GPU then 60-second CPU window granted at 18:59 UTC, and must
release before root tests. A bounded first-chance standalone debugger probe
awaits the next 25-second CPU window. It is a new boundary discriminator after
the failed red-zone gate; no runtime protection-guard integration is allowed.

Next: visible D3D12 clinic diagnostic with CPU/GPU/RAM panel ON and synchronous
draw census ON, then clean comparisons if complete. Census changes no ordering
and reports pending-publication safety UNKNOWN. See the newest entries at the
end of both recipient checkpoint documents for exact evidence.

User asked whether the right bottleneck is targeted: render thread ~90% of one
core, ~75 ms/frame, serial resource preparation/memory validation/readback.
We need ~33 ms for 30 FPS. Socket CPU repair did not move clean FPS. Keep
diagnostic wall costs separate from measured recoverable savings.

C-only explicit working directories, Uptownfrog protections, fixed Cross2-30,
isolated Timmy seed17, visible Default desktop, normaldev0b6610b4, language
privacy, translations and Liverpool's directory remain preserved. No push or
commit. Stable 30 FPS remains unmet; continue substantive work.

# Current continuation — 2026-09-11 18:26 UTC

Opt-in positive net wait passed53contracts20.41s; frozenchildc13b3260bb334b7b9e963b826f703bc80c1db0aad93cbd983f145931de1fce1c
in private/prepared/net-finite-wait-v1. Defaultoff; zero/negativelegacy unchanged,
steady positive deadline and reset-retired identity verified. Visibleclinic
session20260911T181526-3a107a45 complete; socketCPU94.55%->0.02604% ofonecore,
render89.84%, game1.793cores/7.47%of24. Capture14.198FPS isdiagnostic,notA/B.
Detailed evidence at END of recipient experimentindex andlinkedcheckpoint.

Firstcleanpair13.264/13.764FPS stopped on earlyforegroundassertion, incomplete.
The userconfirmedwindowsvisiblelastlook. Actualforeground+activeDefaultdesktop
was independentlyconfirmedlater in the visual run; raising cancomplete afterearly
check. Revisedharnessrecords visibility/focus during50-90s, nofocusmutations there.

CURRENT ROOT WORKLOAD: four100s visible clean off/on/on/off repeat started18:25:56,
private/reports/net-finite-wait-v1-balanced-r2,execsession91614. Expectedends~18:33.
Do not start builds/GPUtests/profilers until it finishes. GameCPU/hardwarecapture
profilersended. Allrootgames useescalated Defaultdesktop, C-only explicitcwd,
Timmycopiedseed17 andfixedCross2-30. Minimum30FPS remainsunmet.

Three source-only agent subtasks whilebenchmarkruns: D3D12owned-ticket runtime
adapter (standaloneplain/debugpassed), synchronous two-drawpipelineeligibility
census, andnewauthored first-chance debugger gate tolocate parkedYMMredzone
damagebefore/after user-mode exceptiondispatch. Do not repeatoldfailedguardgate
unchanged orintegrateprotectionguards. Liverpooltaskawaits40sbuild/GPUreplay
retry; itowns tools/liverpool/_recomp andhasreleasedallpriorworkloads.

Normaldev0b6610b4, languageprivacy, seeds/hardlinkedviews,translations, barriers,
Uptownfrog/.githooks/push.default=nothing preserved. No commit/push.

# Current continuation — 2026-09-11 18:05 UTC

The requested CPU/GPU/RAM panel is implemented and tested; F3 toggles it with
FPS. All51initial contracts and4focused corrections passed; four Default-desktop
comparisons show no measurable FPS regression. Normalbuild/dev0b6610b4 remains
unchanged. Source and frozenprivate builds are ready; no commit/push.

Read the newest socket-attribution/capture entry at the END of recipient
docs/checkpoints/gray-screen-experiments.md and linked detail. Two new diagnostic
runs used frozenchild7a4ed899. Latest20260911T175858-8a3bd707 completed210s.
Verified NexusRevolution Socket=TID31152 spins on positive empty epoll waits:
sampled33000us, over10million calls/sec. This concretely links the hot thread
to the ignored finite timeout; actual FPS recovery remains unproved. A default-off
positive-only wait experiment is being authored with reset-retired lifetime and
monotonic deadline; zero and negative current behavior stay unchanged.

Fresh selected f764/59eb draw capture saved: private/reports/current-f764-net-v2/
gpu-debug/capture-38404_capture.rdc,84,744,705bytes,SHA
591e10ded61ed4fb8cddd9ec5093c1cccdf6f3e2990f1e514ee52a40dd73072a.
Current clinic/hardware panel inspected in current-hud.jpg. The run used Default
desktop and the window was raised/nonminimized, but foreground requests were
denied; wrapper asserted only after normal timeout. Do not call it a clean FPS
comparison or claim foreground-granted. Prior170737run neverarmed, noRDC.

Targeted CPU RIP sample stopped safely at5.57s/223samples after1.0702ms single
pause exceeded1ms cap; every acquired suspension resumed. Native attribution
only because guest mapping validation failed. Reportprivate/reports/
net-wait-attribution-v1-rip. No game or profiler remains running.

Liverpool export/import slot ended with validation failure; other task is
inspecting exact blocker, owns tools/liverpool/_recomp. D3D12 owned-ticket helper
private/perf-lab/d3d12-owned-ticket-v1 is source-frozen, under independentreview,
and now has build-only authorization. No GPUgate/runtimeintegration/FPSresult.
Microsoft EXISTING_HEAPS diagnostic limitation is recorded; general product
support not claimed. Root owns source/docs/build coordination.

Keep C-only explicit cwd/Uptownfrog/.githooks/push.default=nothing; preserve seed
saves, hardlinked views, translations,normalplayer and publication barriers.
Timmy copiedseed17 and Cross1/sec seconds2-30 only. Stable30FPS remains unmet.
Continue substantive runtime work; Remill/AOT startup expansion stays paused.

# Current continuation — 2026-09-11 16:59 UTC

The user-requested CPU/GPU/RAM overlay is implemented and tested. Read the new
hardware-panel entry at the end of the recipient's experiment index and
docs/performance-monitor.md. Frozen private/prepared/hardware-overlay-v2 child
2851f20ba474bed0c8e00211e4c0d7306ecf3a36a8710cd047efd5ee593d650d:
51 initial contracts +4 focused after CPU-ID correction; four real visible
Default-desktop off/on/on/off runs12.845/13.322/13.259/13.275FPS show no measurable
regression. No FPS gain claimed: pooled+1.77% with3.34% control drift.
Complete scene/panel inspected in initialv1 visual. Normalbuild/dev0b6610b4 is
unchanged. Current code includes the accepted monitoring feature plus prior
opt-in runtime experiments, and new default-off net-wait attribution source
being authored; do not treat it as a clean fa47b5b tree.

New CPU evidence: NexusRevolution Socket uses94.55% of one logical CPU,
GXRenderThread84.40%, game2.687core equivalents/11.196% of24 capacity. Hardware
monitor uses0.0781% of one CPU. Reports private/reports/hardware-overlay-v1-cpu.
HleNetEpollWait ignores its timeout; a dedicated diagnostic must associate
actual TIDs/arguments before attributing this hot thread or changing waits.
No arbitrary sleeps or negative/zero-timeout changes have been made.

All four root games/profilers/build/tests have ended. LiverpoolRecomp receives
a <=30-second validation slot from receipt, then explicitly releases. Next:
build/check default-off net-wait attribution if ready, then visible current
f764 RenderDoc capture (C-only verified install/header already compiled), and
thread attribution. A helper-owned, bounded D3D12 async-ticket prototype is
being authored privately. Do not retain D3D12 imports of guest allocations:
existing lease lifetime does not authorize pins across callbacks/reset/unmap.

Continue toward stable minimum30FPS at4K/AA; not achieved. All game runs MUST
use escalated exec on WinSta0/Default and be shown; sandbox IsWindowVisible
is insufficient. Preserve C-only explicit cwd, Uptownfrog/.githooks/push.default,
normal player, Timmy seed isolation, fixed Cross2-30seconds, unrelated
translations and Liverpool's owned directory. No commit or push occurred.

# Current handoff — 11 September 2026

This current section supersedes all older stopped, pending-build, source-state
and acceptance statements below; the older chronology is retained as history.
Stable 30 FPS at the existing 3840x2160/AA settings remains unmet. Continue the
direct x86-64 runtime work. Normal build/dev child is still
0b6610b406a46ccdb6dfbb4d29f6abd3c3459066811bb9da9dc9a94186430afe;
recipient Uptownfrog HEAD remains fa47b5b3c99b13b91c12692a2e108bf5a1b60412.

**All future game runs require escalated exec on WinSta0\Default.** Sandbox exec
was discovered to launch on WinSta0\CodexSandboxDesktop..., where
IsWindowVisible=true does not mean the user can see the game. Verify the actual
desktop and set every command's C working directory explicitly. Earlier captures
prove rendered content; earlier controlled FPS are hidden-desktop comparisons.
Reconfirm retained candidates, including the owned permission cache, with matched
clean Default-desktop runs before accepting them for the visible player.

First confirmed visible run in this continuation: 20260911T161159-88b9fae1,
frozen child 0655c89afd5cb7edb9a97bfcda902ef52a1b4b5607b6faa62e30f0762265e04a,
owned permission caching on, CUDA routes off. Foreground access was granted
at 16:12:59 UTC. Captured 50-90 s: 12.58687 FPS, mean 79.44788 ms,
p95 87.031 ms, p99 96.284 ms, 502 samples, 2180 draws/display and no new
renderer errors. Capture and focus changes make this visibility evidence,
not a clean performance acceptance run. See
private/reports/interactive-desktop-confirmation-v1 in the recipient.

RGBA8 multi-owner compaction was rejected. Frozen child
186a86380c04d3275b6c40acb9f3de22b8683265fa845c67313466a470d0e39d rendered the
complete clinic in 20260911T160310-5318ef20. The 195 s clean 0660 session
20260911T160532-c2f1f75e, with owned caching on, measured control/RGBA8/RGBA8/control
12.71084/12.13682/12.29320/12.67212 FPS: pooled 12.691485 versus 12.214831,
-3.7557%, with only -0.3046% endpoint control drift. Approximately 2180 draws and
no new renderer errors remained. At 16:14 UTC all ten RGBA8-only files were
restored byte-exact from private/perf-lab/rgba8-compaction/{base,base-v1};
final-source/restoration.json records the preserved sources and restoration.
That source base is 0655-equivalent; build/perf-dma still contains rejected
186a8638 until rebuilt. Normal build/dev was never replaced.

Contract accounting is 50 unique tests passed across runs, not one clean 50/50:
initial 49/50 failed the new fixture's UNORM 0.5 rounding assumption; only the
fixture changed to exact 0/1, then focused HDR and RGBA8 contracts both passed.
Do not repeat unchanged RGBA8 compaction without a materially new hypothesis.

The native D3D11 shared-texture/fence to D3D12 existing-host-memory bridge passed
standalone tight/padded RGBA8 tests on RTX 4090: debug/plain both exit 0,
12 cycles in 4.330 s, zero debug messages, exact CPU bytes/native dirty-page
visibility and positive completion of both queues. Source 694af1a6 and executable
bb770be4 are fully hashed in
private/perf-lab/host-heap-probe/texture-bridge/{REPORT.md,manifest.json}.
This remains separate authored-input proof with no runtime or FPS integration;
whole-allocation identity/budgets/lifetime and failure/format gates remain.

Protected-page write-watch research failed its first native-recovery gate.
The owned-input i7-13700K/Windows 10.0.26200.0 probe (source 2ade3f79,
executable 8c86a6c6) corrupted 88 red-zone bytes [RSP-128,RSP-40) in every one
of 16 recovered write faults with live YMM state, mask 0xFFE0, already before
handler entry. Values match upper YMM10-15 state; register/flags/TLS checks and
controls passed. A simple PAGE_READONLY/resume-VEH guard must remain out of the
runtime until pre-dispatch red-zone safety is proven. No Gate 2 ledger was
authored. Exact evidence and the unbuilt plan:
private/perf-lab/writewatch-guard-gate1. Probe PID 49544 exited 1 in 0.0372 s;
no process remained. The earlier peek-first probe also remains parked.

Root now owns implementation of the user's hardware panel: CPU utilization per
logical processor, GPU utilization and RAM, using vendor-neutral Windows
counters on a background service sampled at 1 Hz. Build/contracts and visible
game validation are pending; do not claim a finished panel or FPS gain yet.
The owned permission cache's hidden-desktop +3.58% remains a retained candidate
pending visible reconfirmation; async-owned DMA's +3.53% with +8.26% control
drift remains inconclusive. No new accepted normal player exists.

All work remains on C only; never access E. Preserve recipient .githooks and
push.default=nothing and donor Uptownfrog/push.default=nothing; donor has no
custom hooks. Never modify another branch or push the donor. Authorized recipient
publication may target only refs/heads/Uptownfrog with an exact refspec. Keep
private preferences, copied Timmy saves, seed saves and hardlinked game views
protected. Use fixed Cross taps once per second from seconds 2-30; no screen-driven
navigation. Preserve unrelated translations and tools/liverpool/_recomp, owned
by its separate task. Remill/AOT startup stays paused; cleanup integration is done.

Full chronological evidence, exact hashes and revisit rules are in the
[experiment index](external/Bloodborne-Recompiled/docs/checkpoints/gray-screen-experiments.md#desktop-visibility-and-the-rejected-rgba8-experiment-11-september-2026)
and [detailed checkpoint](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-08-gray-screen-provenance-and-loading.md#11-september-desktop-visibility-rgba8-restoration-and-recovery-gate).

# Active minimum-30-FPS work — 2026-09-11

Current live state after resume at 15:54 UTC: portable multi-owner RGBA8
compaction build succeeded. Child SHA256 186a86380c04d3275b6c40acb9f3de22b8683265fa845c67313466a470d0e39d.
Only configure/build ran; all 50 contracts and game validation remain pending.
Source/base files are private/perf-lab/rgba8-compaction/{base,base-v1};
build logs are build/perf-dma/rgba8-compaction-v1-{0,1}.log.
The independent permission-cache comparison on frozen child 0655c89a completed:
off/on/on/off 12.760/13.278/13.251/12.853 FPS, pooled +3.58%, complete rendering.
Retain this opt-in candidate; no normal player replacement yet.
Async-owned DMA's +3.53% with +8.26% control drift remains inconclusive.
The clean write-watch peek probe regressed dirty cases and is parked.
D3D12 imported-host-buffer correctness passed on RTX4090 with native write-watch
and padding preserved; its native11 shared-texture bridge is source work only.
Root awaits explicit Liverpool test-window release, then runs RGBA8 contracts.
Subagents resume bridge authoring and read-only protected-page tracking research.
Normal child is still 0b6610b4, recipient Uptownfrog/fa47b5b and protections intact.
No root game is running. Stable 30 FPS is unmet; continue substantive work.



This section supersedes the finished/stopped state below. The user explicitly
requested sustained work until at least stable 30 FPS at the existing 4K/AA
settings, authorized subagents and research, and allowed changes to graphics
APIs and architecture. Stable 60 FPS remains the broader performance target.
The reliable accepted player is still about 13.4 FPS. No new runtime gain has
been accepted.

C-only and explicit command working directories remain mandatory. Never access
the old drive. Recipient Uptownfrog at fa47b5b and both installed Git protections
remain intact; normal build/dev child remains 0b6610b4. Do not repeat the rejected
final-image/parallel-publication comparison or parked compaction experiments.
Do not edit seed saves, hardlinked views, translations or LiverpoolRecomp's
owned directory.

New opt-in CUDA direct-readback sources and external DMA publication tracking
are under evaluation. The standalone exact 4K transfer probe was faster than
staging plus memcpy, but DMA is invisible to Windows write watch, so explicit
page generations and a tracked-allocation lease are required. Five focused CPU
contracts passed; full rendering contracts and game comparisons are still
pending. Sources in the active tree are experimental and must not replace the
normal player until accepted on repeatable diagnostic-off FPS and complete
rendering.

Initial full build passed all legacy GPU contracts. The helper test exposed
that host pinning, unlike DMA itself, dirties every watched page on each call.
Production notifications remain intact; the test is being corrected to require
conservative version advancement and native-write invalidation. This may add
exact shadow fallback cost. No game performance result exists for DMA yet.

DXVK 3.1 passed 8/11 existing GPU contracts but failed shared-image imports and
exact depth-bit preservation; no game/FPS test was attempted. A private buffer
arena prototype passed authored contracts, with only synthetic CPU submission
savings. Both remain research candidates. Full hypotheses, identities,
observations and revisit conditions are in the
[experiment index](external/Bloodborne-Recompiled/docs/checkpoints/gray-screen-experiments.md#direct-dma-and-architecture-experiments-11-september-2026).
Private artifacts are under private/perf-lab/{direct-dma,dxvk-probe,buffer-arena}.
The separate Build LiverpoolRecomp toolchain task is active and coordinates
short resource-test windows; do not assume it is permanently idle.

# Latest runtime checkpoint — 2026-09-11

This section supersedes the historical stopped/pending states below. The user
resumed the direct x86-64 runtime work; the larger final-image experiment has now
finished and was rejected on clean performance evidence. Remill/AOT startup
research remains paused. The already-merged cleanup integration was not repeated.

Work stays exclusively on C. Never access E, including stale metadata. Set
command working directories explicitly. Recipient:
`C:\Projects\Bloodborne PC port\external\Bloodborne-Recompiled`.
Both checkouts remain on Uptownfrog. Recipient HEAD is
`fa47b5b3c99b13b91c12692a2e108bf5a1b60412`; .githooks and
push.default=nothing remain intact. No commit or push occurred. Authorized
recipient publication can target only refs/heads/Uptownfrog with an exact
refspec; do not push the donor.

Normal build/dev child remains
`0b6610b406a46ccdb6dfbb4d29f6abd3c3459066811bb9da9dc9a94186430afe`.
All experimental native sources/tests were archived and restored byte-for-byte
to their pre-experiment state. Git confirms no content diff in runtime sources,
headers, shaders, tests or preserved runtime tools. README/CONTRIBUTING
translations and tools/liverpool/_recomp remain untouched by this task. Local
language preferences remain private; 3840x2160, AA, cap 240 and GPU page
compaction remain configured. The reliable retained result is about 13.4 FPS.
Stable 60 FPS at 4K remains unmet; arbitrary resolution/FPS support is still the
broader goal. F6 contracts exist; physical-key/combat verification is pending.

The GPU-resident final-image candidate preserved source readback/Flush, CPU
destination copying, videoout CPU capture and all publication/completion
barriers. It validated captured pixels, producer generation and destination
allocation identity before using an immutable GPU image. Padding, overlays and
resource lifetime contracts passed; the complete clinic visual retained all
2180 draws/display. Candidate v2 passed 43 contracts; the separate parallel
target-publication and private balanced variants passed all 44.

Initial separate off/on/on/off launches suggested +2.50% for GPU handoff.
A stronger single-session balanced comparison contradicted that result:
control 12.651 FPS, handoff 11.421 (-9.72%), parallel target publication 12.560
(-0.71%), both 12.024 (-4.95%). Both handoff phases were slower than adjacent
controls. Timing diagnostics and captures were off; all rendering and CPU
visibility paths remained active. Do not adopt or repeat these unchanged
candidates.

The final diagnostic measured added full-frame pixel validation at 1.980 ms per
call on the submission thread. Presenter work fell from roughly 3.1 to 0.74 ms
per call on its separate thread, but the original readback/copy remained.
These inclusive wall times are not additive savings. Revisit only with a
concrete way to remove validation/cross-device costs while preserving exact
captured output and native CPU visibility. Deferring readback requires explicit
proof of publication order and native CPU-read visibility; incomplete traces
cannot justify removing barriers.

Full hypotheses, failures, exact source/binary/run identities, phase windows,
distributions and revisit conditions:
[experiment index](external/Bloodborne-Recompiled/docs/checkpoints/gray-screen-experiments.md#resumed-final-image-handoff-experiment-11-september-2026)
and [detailed checkpoint](external/Bloodborne-Recompiled/docs/checkpoints/2026-09-08-gray-screen-provenance-and-loading.md).

Private archives in the recipient:

- private/perf-lab/final-image-source/{base,v2,parallel-v1,balanced-v1}
  and restoration.json;
- private/prepared/{final-image-v2,target-publication-v1,final-image-balanced-v1};
- private/reports/final-image-balanced-v1/balanced.json and
  private/reports/final-image-timing-v1/costs.json;
- private/tools/final_image_trial.py, balanced_report.py and final_image_costs.py.

All runtime experiment processes have ended. Tests used isolated Timmy seed17
copies and one X/Cross pulse per second at seconds 2–30; there was no screen-driven
navigation. Seeds and hardlinked views remain read-only. Earlier compaction and
copied-image dirty-page experiments remain parked and privately preserved.

The separate Build LiverpoolRecomp toolchain task owns tools/liverpool/_recomp.
Its isolated CPU validation resumed only after the final runtime diagnostic
finished and is now complete, with no workload left running. Its new bounded
capture writer/importer has authored-fixture coverage; it has recorded no real
game trace and has not improved runtime FPS. See its
[owned handoff](external/Bloodborne-Recompiled/tools/liverpool/_recomp/docs/handoff.md).
Its resource_trace v1 cannot represent the cross-device/keyed-mutex final-image
handoff; any such interval must remain an explicit unsupported gap. Preserve
that task's files and coordinate any future test windows.

# Integration direction and absolute branch restriction — 2026-09-07

The user selected lud-berthe/Bloodborne-Recompiled as the product foundation. All current and future work uses only the permanent Uptownfrog branch in both checkouts. The user explicitly authorized publishing only recipient Uptownfrog on 2026-09-08. UNDER NO CIRCUMSTANCES PUSH TO HIS MAIN BRANCH OR MODIFY ANY OF HIS PRE-EXISTING BRANCHES. See AGENTS.md for the complete restrictions. The original AOT research remains preserved; the historical startup continuation below is paused and is not the current integration task.


## STOPPED at user request (2026-09-11)

The final bounded test is complete. Do not resume automatically; the user wants
to continue later and may shut down the PC. All game/build/test sessions owned
by this work have ended. C only, Uptownfrog only, protection hooks unchanged.
No new commit/push after fa47b5b. Normal build/dev remains validated child0b6610b4;
local English/2160p/cap240/AA and page compaction are unchanged.

Exclusive full-render diagnostic20260911T031751-52ee3112, child1328adf5, validates
all per-thread root/self accounting with no dropped scopes over537 flip calls.
The accepted fullscreen image readback/copy costs10.153ms per flip: target
flush7.530 (includingMap2.346) followed by CPU row copy2.617. Around1409 rejected
classifiers together cost0.0648ms. Command preparation0.234 and lock/cap waits
are negligible in this run. CPU color publication7.959, GPU-copy Map5.105,
memory reads5.791 and version queries5.341 remain substantial. These are
diagnostic wall times including waits/profiler overhead; no clean FPS gain.

Next concrete larger candidate: GPU-resident final-image handoff through the
recognized blit/videoout route, preserving CPU visibility, overlays/2D batches,
padding and resource lifetime. It is NOT implemented or authorized to bypass
native CPU visibility. Use bounded real resource events/retain-defer contracts
where needed, then exact renderer contracts and clean paired FPS. Fullscreen
classifier micro-optimization is ruled out by this measurement. The broken
ablation's29.4ms residual is not proven simulation time or a hard lower bound.

All experimental native/tool edits are restored to fa47b5b. Exclusive source
and manifest are in recipient private/perf-lab/exclusive-source; binary in
build/perf-exclusive; report private/reports/exclusive-render-path/exclusive.json.
Copied-page candidate source is in private/perf-lab/copied-page-source, child77b
in build/perf-pages; it is parked because13.151/13.586/13.298/13.363 FPS off/on/on/off
does not establish a reliable gain. Its complete4K visual is retained. Reliable
normal player remains roughly13.4 FPS; stable60 FPS is unmet. Existing F6
predicate/lifecycle checks pass, but physical key/combat verification is pending.

Recipient experiment index and linked checkpoint contain exact successful,
failed and inconclusive runs. These doc changes remain local/unstaged. Preserve
unrelated README/CONTRIBUTING translations and tools/liverpool/_recomp work.
LiverpoolRecomp says70 CPU tests pass,212 families/242 variants package and727
runtime products round-trip byte-identically; two tonemap recipe variants match
existing bytes. This is offline tooling, not a runtime speedup. That task is also
finishing its handoff and stopping for the user. Do not stage/publish its files.

## Active continuation after project settings update (2026-09-11)

Work only on C:/Projects/Bloodborne PC port, recipient Uptownfrog.
No E access of any kind. Saved Codex project points to C; explicitly set command
workdirs because this task still exposes old sandbox metadata. Recipient hooks
.githooks and push.default=nothing remain enabled. Donor stays local-only.

The cleanup merge7872217 includes owner source44edc2c. This continuation adds
scoped graphics bindings/state reuse, exact empty-indirect dispatch handling,
direct memory comparison, immutable index ownership, and exact GPU page
compaction. All 42 CTest contracts pass in11.11 s. Tested child SHA-256:
0b6610b406a46ccdb6dfbb4d29f6abd3c3459066811bb9da9dc9a94186430afe.
A preserved executable set is private/prepared/baseline-page-compaction.
The validated source checkpoint fa47b5b3c99b13b91c12692a2e108bf5a1b60412 was
committed and pushed only to Uptownfrog; the exact remote ref was verified.
No donor publication.

Four same-binary clean 4K/240/AA-on tests, off/on/on/off, give pooled12.323
versus13.394 FPS (+8.69%). Individual pairs vary:11.935->13.573 and
12.711->13.216. All retain about2180 draws/display, no skipped flips and no
new renderer error types. Stable60 FPS is NOT achieved. See recipient
docs/checkpoints/gray-screen-experiments.md for exact sessions, distributions,
failed/inconclusive experiments and privacy-safe implementation evidence.

The compact path uses integer GPU comparisons, native changed-page tracking
and existing CPU workers. One largest >=32 MiB tracked aligned RGBA16F copy is
selected; <=256 MiB workspace is separate from the <=768 MiB copy cache.
Pre-publication write observations, mapping identity, retained CPU/GPU baseline
tokens, padding, full fallback and all completion/publication barriers remain.
The diagnostic transferred15.20 MB instead of66.85 MB for the clinic HDR copy
(77.26% less); 534/534 measured attempts were sparse. GPU comparison/count/data
readback still blocks at publication; next candidates must preserve correctness.

Private developer.json keeps English,2160p,cap240 and now
gpu_page_compaction=true for normal launches. Generic language stays French,
generic compaction defaults off, and benchmark diagnostics explicitly override
the local setting. No local preference or game artifact is tracked.
Visual20260911T014319-3ea9cac2 shows complete clinic, Timmy, intact HUD/lighting,
AA ON and cap240. All bounded game processes ended. F6 no-damage implementation
and native predicate/lifecycle tests already pass; physical-key/combat validation
is still pending.

Retained OM attachments were4.5% slower and removed; do not repeat without new
evidence. Other earlier microchanges did not establish independent FPS gains.
The corrected focused render-thread profile20260910T194406-d878dd16 measured
17.109 CPU seconds in20 seconds with publication/comparison dominant. An earlier
sampler invocation and scissor-fixture mistake are recorded, not hidden.

The user created a separate LiverpoolRecomp task. Its exclusive scope is the
new tools/liverpool/_recomp directory, not runtime/memory/shared build files.
It supplies a conservative resource-event schema, replay/reference and authored
tests; root has not staged or published that task's files. Small CPU tests may
resume after the four clean game benchmarks; no GPU probes/heavy builds were
run concurrently. Do not infer native CPU non-readability from shader metadata.

## Larger private experiments (2026-09-11)

User explicitly authorized larger reversible experiments after marginal gains.
The early-compaction prototype is parked: clean13.290 and13.006 FPS versus
13.092 control did not establish a reliable gain despite lower Map wait. Its
source and childa50b270f are archived privately; normal build/dev is restored
to child0b6610b4. Private settings remain English,4K,cap240,AA and compaction on.

A separate build/perf-lab now has compile-gated unsafe ablations on fa47b5b,
childb29b59ae4554b3a0d548c62aa4b87895bc50fa7809eed759da2eb740d2777951.
The private hooks activate45 seconds after first3D draw and count removed work.
Masks1/2/4/8/16 bypass CPU copy publication, copied-image validation, native
D3D draw submission, whole HostBackend Draw, and target CPU flush respectively;
32 skips only the common ffaf78adafc66d69 vertex family. These are diagnostic
ceilings, never valid full-render FPS claims. Do not publish these unsafe hooks.
First probe20260911T022004-a1a12715 is pending. The private harness initially
failed an import before launch; adding tools/diagnostics to sys.path fixed it.
All exact outcomes belong in recipient docs/checkpoints/gray-screen-experiments.md.

The other task's [LiverpoolRecomp module](external/Bloodborne-Recompiled/tools/liverpool/_recomp/README.md)
and [clinic analysis](external/Bloodborne-Recompiled/tools/liverpool/_recomp/docs/clinic-analysis.md)
remain separate and unstaged. Its42 synthetic tests pass; no native CPU-read
coverage proof exists. The recorder proposal preserves existing barriers and
labels unknown access coverage. Do not publish or modify that task's files.
README.md and CONTRIBUTING.md translation edits also belong to separate work;
preserve them and exclude them from this optimization's publication.

## Whole-path results and current native candidate

Five private ablations used childb29b59ae and4K/240/AA: skipping copy publication
produced17.621 FPS; copies+target flush+native GPU draws21.886; also bypassing
backend CPU draw preparation34.007 with stale rendering. The common tiled VS
skip barely changed13.074 to13.578 and introduced a bright corrupt region.
Target-flush skip alone15.042. These are diagnostic ceilings, never valid
optimized-game results. Exact windows and failures are in the recipient index.

A full-render per-shader CPU census (childfd7fca0a,session20260911T023524-217e8986)
found122 pairs and21.904ms/flip in backend Draw,18.509ms resource preparation.
Two draws of VSe68071273736ecf3/PSda541cce3d2860d1 account for4.720ms,4.688ms in
resources. The common tiled VS totals4.033ms. CPU timings include profiling
and nested work; they are not GPU shader time. All unsafe hooks were archived
privately and removed from active source before the next candidate.

Current candidate build/perf-pages,child77b10c84718760704efc778ac4bf807cb71e8b8cdf43036fb37579b77eb49e24,
adds exact dirty-page validation of retained copied images. A proven CPU/GPU
equality version survives compatible completed copies; later native AND GPU
publication writes remain watched. Changed pages compare under a mapping lease
with allocation identity, including zero-dirty-page queries. All barriers remain.
Normal version hits keep the cheap summary query. The flag
BB_GPU_COPIED_PAGE_VALIDATION defaults OFF; no normal local setting changed.
43 CTest contracts pass in13.92s including native writes, overlapping watchers,
4K GPU-copy consumers and lifetime replacement. The new fractional-color test
initially failed equally in control/candidate (encoded127 versus assumed128);
using exact0/1 endpoints fixes that copy-test fixture without changing rendering.
Diagnostic20260911T025109-d745fdaa reduced the42.4MB depth-copy comparison
from3.10 to0.114ms/flip (3.26% of pages), but clean off/on/on/off measured
13.151/13.586/13.298/13.363 FPS. Only about1.4% pooled and reverse pair negative:
NOT a convincing gain. Visual20260911T030706-1e40128a shows intact4K clinic/HUD.
The candidate is PARKED; six native/test sources archived privately and restored
to fa47b5b. Candidate build/perf-pages remains child77b10c84.

The active diagnostic-only source adds BB_RENDER_TIMING_EXCLUSIVE per native
thread, complete root-tree buckets with self/root accounting checks, and
accepted/rejected fullscreen, row-copy, command-prepare and lock-wait scopes.
build/perf-exclusive child1328adf54f109d651d87afc460b4675806a580210848dc8bc3a8bc687ced6f52
passes all42 contracts in21.37s. The single bounded full-render attribution run
is pending. Use its result to select one concrete runtime change; wall timers
include waits and observer overhead, and are not clean FPS evidence.

Normal build/dev is still restored stable child0b6610b4 with localEnglish,
2160p,cap240,AA and published page-compaction enabled. No new commit/push after
fa47b5b. Keep unrelated README/CONTRIBUTING and LiverpoolRecomp work separate.
The user explicitly authorized status messages to other tasks; the LiverpoolRecomp
task was also verified local with explicit shared-project coordination instructions.
One detailed status message was initially rejected by automatic review for an
unverified destination; a minimal test-window update passed after verification.

## Latest state: C-only clinic optimization (2026-09-10)

Work exclusively in C:/Projects/Bloodborne PC port. The task environment may
still supply an old E working directory: set every command workdir explicitly
to C and do not access E. Active recipient:
external/Bloodborne-Recompiled, branch Uptownfrog, HEAD15b8eb2a097a71360dcc2d6db586b939dad63d09.
It includes merge7872217 of owner cleanup44edc2c and the tested local/debug and
performance contribution. Published and remote-verified on2026-09-10 using ONLY
refs/heads/Uptownfrog:refs/heads/Uptownfrog, hooks enabled, no tag following.
Owner cleanup remains44edc2c; no other ref was pushed. Recipient working tree is
clean. Donor AGENTS/HANDOFF remain local changes; no donor publication.

The C recipient has a fresh build/dev MSVC Release and rebuilt private clinic
shader library (210 programs,242 sidecars). Private developer.json selects
English,3840x2160,cap240 and a copied Timmy seed17. French remains the generic
default. F6 toggles executable-verified player no damage, default off; native
predicate and lifecycle contracts pass, live combat/key validation is pending.

The user replaced screen recognition with repeated X taps for the first30s.
That route is visually verified in the clinic (session20260910T174959-a7f125dd).
All further game tests must stay at4K/cap240. The user aims for stable60FPS;
this is NOT achieved. Matched serial/parallel publication runs measured11.170 /
11.425FPS, all2180 draws per display. A separately validated MSVC IPO build
measured11.541FPS. New exact write-version block summaries pass the36-contract
suite in build/ipo-msvc; session20260910T181527-047cf9f3 records raster/timing
costs for that candidate. It is diagnostic, not a clean FPS benchmark.

C-only build/dev passes36 contracts (final suite9.26s; contribution-final-tests.log).
The retained child SHA-256 is a6f670c581ba3650197d902a2d1f24ff712c9a252ceea82ed785807ce2b1f20d.
All game/benchmark/build workers are stopped. The E verifier was explicitly
cancelled and must never resume. Its clean control6fd2526e measured10.877FPS
in session20260910T183059-27830907 and11.390FPS in184154-97134391, showing run
variance. Shader-identity memoization40a04cf6 passed37 contracts and rendered the
clinic in visual184523-e855f297, but its11.269FPS benchmark183934-f333a18b did
not beat the matched11.390FPS control. That candidate and its extra fixture
were archived privately and removed from active source. The retained runtime
has affinity mapping, exact publication workers and page-version summaries;
no image quality reductions or omitted draws. Stable60FPS is still unmet.

Structural leads from the separate read-only brainstorm: redundant D3D binding
state, packet publication barriers at opcodes0x12/0x16, and CPU round trips in
final presentation. They are hypotheses, not verified gains. Preserve native CPU
read/write visibility and completion ordering; do not remove drains based only
on GetWriteWatch, shader IDs or repeated descriptors. No such change was made.

Read the recipient docs/checkpoints/gray-screen-experiments.md and its linked
checkpoint before further experiments. It records failed menu/capture attempts,
CPU sampling, compiler selection failure, exact binaries and comparison limits.
All captures, private tools, saves, profiles and binaries stay ignored.

The user explicitly prohibited ALL further E: access on 2026-09-10. The old-drive
verification worker was stopped and collected; its script is disabled on C:.
Leave the old copy untouched. Do not resume old migration, hashing, preservation,
cleanup, or junction-creation instructions. All active source, dependencies,
builds, game inputs, copied saves, and output must use C:. Retained private
receipts on C: are historical and incomplete; no E: project deletion occurred.
Every E-related procedure below is superseded and must not be executed.

## Historical: run45 and initial migration request (2026-09-08)

User explicitly requested: after currentrun45 completes, move ENTIRE project and
Bloodborne game files fromE to C:\Projects\Bloodborne PC port (created empty).
Do not start another run/build before handling migration. First inventory exact
sources, hardlinks/reparse points and physical bytes vs C free328GiB. Preserve all
private captures/research; no deletion to make room without explicitauthorization.
ExistingE paths are embedded in CMake/Ninja/CTest/import assetsource manifests,
so a compatibility junction from oldE project path to physicalC copy is advisable.
Verify source and destination before moves; copy/verify before removingoriginals.
RootownsGit/migration/lifecycle. Agentsfrozen exceptreadonlymigrationaudit.

RecipientHEAD4955e1acac763283c97e44bb6d1db74b26b48ed4; runtimeb096e33 diagnostic,
159/159tests25.24s; lastpublished4c96f78. BranchUptownfrogONLY bothcheckouts,
hooks.githooks,push.default=nothing. No ownerbranchmutations or donorpush.
Run44 completed95.260206s: displayMAGENTA (43cyan), all2,073,600HDR9441pixels
R=B=A, G=.14111328125. ActualGPUtonemapbuffers4112bytes identical, CPUformula
matches everyoutputRGBwithin.988bytelevels. TonemapNOTdefective.9630depthshader
correctlyreplicatesscalar withwrite-maskD preservinggreen. Fullcolorpassesbefore/
afterit are rejectedshader_lowering_unavailable: PS943a6b00/VS9bfd3f00 and
PS9bfd0a00/VS9bfd0500. FirstVS alreadycached; bothPS+secondVS needexactcapture.
Run44privateproofs tonemap-cpu-proof-v1.py/json,hdr-transition-analysis.md,
bloom-chain-audit.md. CurrentbloomallNaN isseparateunresolvedlead, notpackingproof.

Run45 NOWLIVE pid62932, launcher49046,stopobserver90389,hardwareobserver99611.
Runtimeb096e33/docs4955e1a/cachev14,compiler-inputunique+programcapture enabled,
sourcewatchselecttonemap image1,constantcommands,executiondiagnostic enabled.
AutomaticContinue23.091460s (release18:57:27UTC). Latestat18:59:58UTCstillloading
frame780; newshadercapturesstillarriving, so not stalledflat. Stopobserverdeadline
300s afterattachment leavesrunningifcompletionnotmet: rootmuststop exactverified
child iftimeoutexpires andcollectallsessions. No extra game/compiler/buildrunning.
Hardwareobserverstoresread-only5secsamplesafterexitinrun45/hardware-samples.json.
Allpreviousgamesstopped. Roottoolsstoredlivevariablespoint45; donotreuse44PID.

Hardwaremeasured i7-13700K16C24T,RTX409024GB,32GBRAM; ~7.4GBavailableidle
before45,~10GBpagefileused,3.7GBcompressedmemory; ESeagateST2000DM008HDD,
CSamsung980PRO1TBNVMe328GiBfree. Current45slowloading sampleEidle/paging0,
so SSDmayhelploading/builds but notestablishedasmainlimit. Userinformed.

Older run43 detail below is historical; latest facts above supersede it.

## Current work after run43: cyan scene, not finished (2026-09-08)

Keep working until rendering fixed or user stops. Run43 now SHOWS Timmy and clinic
furniture instead of flat gray, but severely washed out cyan. This is progress,
NOT completion; no movement tested. Root visually inspected frames975 and earlier
loading transition. Frame975:48draws/502triangles/glyph8/24,pipeline11. Run43 used
runtime3e26084/docsHEAD e8df7df and cachev14. Continue22.544s, timedobserverstopped
at151.019769s. Child51504,launcher91501,observer94455 STOPPED/collected.
Liveobjectreadagain2551programs/correcttonemapPSbinding,same_lifetime=true.
Three unsupported_texture failures(counter38), no deviceerror.

RecipientHEAD e8df7dfbe71703b2fdd14403c31973d65b08c581 (docs only, NOTpublished);
lastpublished4c96f78,mainunchangedaf93612. Runtime3e26084 tested159/159 in28.00s.
Experimentindex updatedrun43 andtwofailedcompilerjobs (dirtydocintentionally).
Allcurrent/futureworkonlyUptownfrog. Verifyrepository/branchbeforeeverymutation.
No game/compiler/build running NOW. RootownsGit/build/input/lifecycle.

Cachev14 FROZEN/ready:226sealed(195base+31new),checker226/0,40compilejobsok/2failed,
9duplicatedjobsfullyequivalent. Nativecache+4bbsa/spvpairs,basev13all1106files
unchanged;v14inventory1238files,SHA1045bd663e29e5f6152290d459886761c8383f98c92ab57cf38c8491a168f4bf.
Provenance build/shaders/clinic-yebis-v1/handoff.json. No recompilationneeded.

TwofailedVS e16741ba449cf84b/8154cc5ca335759e are EXACToldrun08tessellationholdouts
062/064. Bothpatch9,stage45LS/HS,14DS_READ2_B32 actualhullcontrolpointreads.
TheyneedrealLS/HS/DSstagecompilation+runtimepatchpipeline; do NOTremoveassert or
applyoldpixelquadswizzlefix; NOTestablishedcauseofcyan. Recordedtoavoidrepeats.

CurrentMAINquestion: HDRinputalreadycyan vswrongGPUconstants vsfinalLUT.
ShaderagentverifiedexacttonemapGCN/HLSL: gamma1/2.2,exposure.7317073,neutralmatrix,
finiteconstants;1x1auxcolorsinactiveforrun42frozenconstants. No mathdefectfound.
TonemapPSf7640bc68c9d3efa,VS59eb87748bc6fd87. OriginalGCNbufferbyteoffsets2464,
3232,3328,3360,3392 allwithin4096prefix. HDRt2,constantbuffert0.
Oldrun23A7F4/9448HDRsampling32,400pixels haswarmRGBmeans.0914/.0622/.0293;
notcurrent43evidence. NeedSAME-DRAWreadback.

ACTIVEagent mutex_capacity OWNS boundedopt-inactualGPUbufferdiagnostic in
src/execution/orbis_gpu_3d_d3d11.cpp +focusedexistingGPUfixturetests. Authorized
approach: flagBB_GNM_3D_PIPELINE_CAPTURE_PIXEL_BUFFERS=1, existingselected/armed
pipelineindex<2,atmost8pixelSRVbuffers/draw,64KiBeach,256KiBtotal; D3DstagingCopy/
Mapactualuploadedbuffer (includingcachehits),notsecondguestread. Logslot/address/
size/hash/result/path,diagnosticfailuresneverfaildraw. WaitforFREEZE thenrootreview,
singleworkerbuild/fullCTest. Noagentbuild/Git. Sourcechangespendingbyagent.
world_rendering READONLYpriorLUT28validation/nonneutralcolorscheck; shaderagent
finishedreadonlytonemapmathreview. Rootprivatehelperchangescompiledsyntaxonly.

NEXT44 afternewdiagnosticbuild/tests: targeted_probe_run.py launch
 autonomous-clinic-44 --seed autonomous-clinic-17 --cache build/shader-cache-clinic-v14
 --null-ps-callsite --capture-targets --pixel-buffers --capture-commands
 --constant-commands-only --source-chain --auto-arm-gameplay-layout
 --pipeline-pixel 0xf7640bc68c9d3efa.
No fullcompilerinputs. Newautoarmreadonlydiagnostictrigger requiresknown1920HUD
layout,glyph8/24,frame>=980,draw>=40; retainscandidatepixelsandlabelslayoutmatch,
NOTexactimageverification. No newgameplayinput. Rootinspectretainedhud-before-arm.
Sourcewatchclosesafter2selectedtonemapdraws; targetsallcapturesHDRandoutput.
Couplelaunch→exactPIDquery→stop_completed_probe.ps1 -RunName44 -ChildIdEXACT.
ObserverstopsONLYverifiedPID/path/starttimeafterwatchend+CCBcaptured;max300s
leavesgameforrootifcriteriafail. Monitor/collect;do notleaveunattendedatcompaction.
Privatefunctionsstatehas colorLaunchCmd/colorObserverCmd templates RUN_NAME/CHILD_ID.
Keeponegame,nocompiler/build/GPUreplaywhilelive,Unitycontinuesworking.

## Latest progress: run42 / ctype fix (2026-09-08)

Continue until final world renders or user stops. Run42 CONFIRMED ctype fix:
2551 programs, active1866 VS1844/profile1 and PS1871/profile2 match archive5/2025;
real selected PS and native +88 reach low-level binding. Repeated lifetime checks
match. Tested3e260841f912d8857bed00197ceaff62bdf7ddb0,159/159tests28.00s.
Published HEAD4c96f785aa12a5a5bbe5e575715a72aa113aee20 includes live evidence;
main unchangedaf93612fc2e3df328573ccc0b816bc89ed39fa03. Recipient clean.
Never push donor; its AGENTS/HANDOFF changes remain private. Only Uptownfrog.

Run42 child48624/launcher46281/observer60017 STOPPED/completed/collected106.724696s.
Lastframe960 loadingcard74.897s, not grayHUD or worldsuccess. Continue command
23.9775s but release41.7603s, explaining ACKUTC17:57:55. New shaders/world-depth
draws continued104s; no stall proven. 23998 backendattempts executed/no backend
failures. NewlyenabledYebis adds38 lowering/cache misses perframe. Capture work
continued untilstop; nextleanrun omituniquecompilerinputcapture.

Agent shader_compilation soleSERIALcompiler finished42jobs:40success/2failure.
ExacttonemapPS+VS succeeded. No compiler remains active, but AGENT STILL AUDITING
33keys/duplicateequivalence/2failures before copied cachev14assembly. Wait for its
cache-ready message before game. Newprivate output build/shaders/clinic-yebis-v1.
Tonemap draw82: compiler-inputs/indexed-ps-00000000943e6a00-vs-000000009bfd6300.txt,
PSf7640bc68c9d3efa C0185/20 andVS59eb87748bc6fd87 C0046/18. MainHDR descriptor
96480000 is1920x1080RGBA16F/tile14, destinationRGBA8swap1. No formatfault shown;
noactualimagepayload captured, so cannotclaimthisspecificHDRtargetpixels.
Lastlaterworldcapturewasinterruptedmid-resource; do notinventmissingdata.

Next43: targeted_probe_run.py launch autonomous-clinic-43 --seed autonomous-clinic-17
 --cache build/shader-cache-clinic-v14 --null-ps-callsite. OMIT --compiler-inputs.
Couplelaunch→exactPIDquery→boundedobserver immediately. observe_yebis_probe.py
 --pid EXACT --run autonomous-clinic-43 --after-continue-seconds120
 --timeout-seconds210 (actualargumentspacesrequired). Reads exactoldgrayHUDearly
or timedpostContinue, labelswhich. RootwrapperstopsONLYexactPID/path/starttime
withbranchrecheck. Rootcaninspectnewworldearlier andstopafteradequateevidence.
No manualbuild/compiler/GPUreplaywhilegame; Unitystillinuse;1gameonly.

## Active investigation: continue until fixed or user stops it (2026-09-08)

Keep working until gray screen fixed or user stops. Latest steering requires
recording failed/inconclusive experiments. Both AGENTS.md now enforce this; read
recipient docs/checkpoints/gray-screen-experiments.md before repeating a probe.
Detailed chronology is2026-09-08-gray-screen-provenance-and-loading.md.

Both checkouts ONLY Uptownfrog, verify repository/branch before EVERY mutation.
Never push donor/modify owner refs. Recipient publication only exact
refs/heads/Uptownfrog:refs/heads/Uptownfrog. Hooks enabled,push.default=nothing.
Lastpublished446a1ef9fe2bdb0b5a8041325280fe754cd8062a;main remainsread-only
 af93612fc2e3df328573ccc0b816bc89ed39fa03. Currentcdd2773docsHEAD NOTpublished.
Testedruntime446a1ef:159/159tests28.34s. Root owns Git/build/input/lifecycle.
Unity staysinuse:singlegame, no manualbuild/compiler/GPUreplayduringgame;
oneworkerbuild. Gameinputs/shaders/binaries/captures remainprivateignored.

NO LIVE GAME/BUILD. Run41child46768 andlauncher76601 stopped/collected.
Run40navigation failed despite30framepress; noobjectdata. Newauto_menu.py adds
2s settling+oneexactrecognizedwarningretry afterACK/frames/release.23private
fixturespassed10.430s. Run41succeeded warning5.184/Offline19.985/Continue21.685s,
exactgrayHUD960. Boundedreader29reads17,424bytes, repeatedlifetime/selectionchecks
matched. Total278.583s includesorchestrationdelay; NEXTlaunch+observercouple.
Do notmistake deliberateexit3forcrash. HunterTimmyseed17.

BREAKTHROUGH LEAD run41: actualeffect2555techniques but1program. Active1866 and
constant278 bothVS0/PS0. Onlyprogramprofile1(vs_2D),filenameEMPTY singleton
base+5469e10. Source1866 tonemap/exposure/matrix/gamma declaredVS5/PS2025;
constant278 declaredVS0/PS2534. ContextPSobject0,selector43d11c,RTformat8.
Do notinterpretvertexobjectfieldsaspixelvariants; readercorrected. Earlier
vs_2Didentity DID NOTproveConstantColortechniqueselection whenIDsareincorrect.

Agents independently verifiedguestTrimC54050 callsGetpctype(sUP1hBaouOw,
PLT2BBE6C8), stripswhere16bitflags&0x144. CurrentHLEdigit0084 andletters0181/0182
WRONGLY matchtrim. BuildEffectC7F57B/C7F5A1 trimfilename numericfields toempty;
C7E650internsbyfilenameONLY, soallreusefirstVSprogram beforePScreation.
73validatedGetpctypecallsacross43guestfunctions; masks uppercase2/lowercase10/
hex1/alpha212/alnum232/space144/control8/punctuation80 confirmneedfullABI.
world_rendering OWNS src/execution/orbis_hle_ctype.cpp + tests/boot/orbis_ctype_tests.cpp
correctfullABIpatchandregressionsafterpinnedprimaryreferenceverification.
shader_compilation independentlyreviewsABI+othercallers;
mutex_capacity finalcausalchainlayout/SetPassStatevalidation.
Noagentbuild/Git/game. Root review+singleworkerbuild/full159tests thenprobe42.

Existingrealfixes:COND3b0f2e2 andCEf3b4068 validatedbutgrayunchanged. CE43ring
publicationsinterleavecorrectly. NativeHDRcopyworks; final56cLUTreceivesgray.
Run39all15selectedunknownretained,bothDrawIndirect24 BEFOREsuccessfulHDRcopy,
notmissinglatecompositor. No fallbackPS/fakepixels/relaxgates. Clinicgeometry/
textures/lightingvisibleinintermediateHDR(run23montage). No finalworldfixyet.
Run39exactnullPCchain1075405→11f97fc→11fbc76→c72881 viaimmutablecmdsnapshot;
old32armedcallcapexhaustedrun38,inconclusive. Donotrepeatcappedtimingprobe.

Privatehelpersunderrecipient.tmp/integration:
- targeted_probe_run.py launch autonomous-clinic-42 --seed autonomous-clinic-17
  --cache build/shader-cache-clinic-v13 --null-ps-callsite
  (leanobjectrun; omitheavycaptureoptions).Coupleobserverimmediately.
- observe_yebis_probe.py --pid EXACTPID --run autonomous-clinic-42
  --after-continue-seconds 60: max120swait,abortnavfailure; exactoldgray triggers
  earlyread,otherwiseclearlylabeltimedreadafterContinue. CallerPCderivesbase.
- read_yebis_objects.py --pid EXACT --base ACTUALBASE --run ...
  boundedread-onlyknownroot[base+56c5930]→owner+30wrapper→+E0Tiny;
  vtableandmoduleverified,arraysbounded,root/selectionrechecked. Neverheapscan.
- ObserverPowerShellwrapper MUSTstopONLYexactPID/path/StartTimeafterresult,
  branchguardagain. Nootherprocesses. read-onlyobserveritselfdoesNOTstopchild.
- probe_run.py frame RUN convertslatestcapture; rootinspectactualimage.
CaptureframesunderRUN/frames;System.Drawingcanresizeandemitbase64image.
Do notprintbase64astext. NativeUIunavailable. Newhelpercompilesyntaxpassed;
no fullCTest neededuntilruntimepatch.

## Active merged-runtime probe29 (2026-09-08)

LATEST user request (merge owner main into Uptownfrog) is COMPLETE and published:
remoteUptownfrog e049832ba2c3e0803d63323e8d8d4fbef4377d4b, parentse7c2cdd+af93612.
Main verified unchangedaf93612 afterexactUptownfrogpush. Hooksenabled,
push.default=nothing. Never mutate anyownerbranch/ref. Fullmerge157/157 passed.

Recipient currentHEAD601259c7000f23abe1607a75477904520f4c94ca, twoLOCALcommits
aheadpublishede049832. 0411ced addsreviewedgraphicsdebugtools (otherusertask,
thread01a0807d-dd88-7440-a7eb-321782adeb36, nowCOMPLETEandallslotsreturned).
601259c addsboundedpending2D-at-copyinspection;159/159CTestpass26.63s,
logsclinic-pending-2d-{build,ctest}. No trackedworkingchangesaftercommit.

ACTIVE RUN29 .tmp/integration/autonomous-clinic-29, child57724, launchersession59907.
Binary601259c, freshcopyTimmyseed17/cachev13(195), original1080pELF.
No inputs yet atcheckpoint; firstframepending. ROOTownsprocess/input.
NO BUILDS OR COMPILERS whilethischildlive. Otheruserstoolingtaskfinished;
subagentsholdingread-only. Probecommand includes--gpu-capture withselected
finalPS56c499c7c845fa48, compilerinput+compute captures andsourcewatch.
BB_DISPLAY_PROFILE absent, AA/overlay explicitly0. RenderDocloaded,opt-in
validationfalse. BotharmfilesabsentuntilvisuallyverifiedHUD:
run/arm-pipeline.txt andrun/gpu-debug/capture.arm. Usecapturehelperarmwith
same-runimageevidenceafterHUD; RenderDocscopeone3Ddraw, notwholeguestframe.

Private .tmp/integration/probe_run.py nowhas--gpu-capture anduses
settings.update(debug_capture.prepare(...)) becauseitinheritsnoBB_*settings.
Thischeckstheadjacentbb-gpu-debug-smoke capabilities beforelaunch. Installed
RenderDoc1.46 +MicrosoftGraphicsTools areverified. Toolingfull159tests passed;
sixcase selftest/replaymatches256pixelsandpreexistingSRV exactly. Actualrenderer
andVideoOut fixturesalsocaptured/replayed. LiveInfoQueueunderRenderDocisUNKNOWN
becauseRenderDocintercepts it; separatevalidation-only runneededforrealqueue.
No capture success impliesgameplay. Toolscommitted0411ced, privatebinariesignored.

Newpending2D trace source_pending_2d/batch/draw emittedonlyforarmedwatchedcopy,
withsource/destinationoverlapmask, exactaggregates, up4batches×8representatives×
256sampledvertices. bounds_complete explicitlymarks partialbounds. Snapshotdoes
notdrainorretarget; backendquery/queuecopy/trace locksheldseparately. Existing
source_cpu_copy remainslastbeforeSync torestorefollowreadassociation. Itisnot
atomicwithconcurrentpresentation. Existingwatchcap256/truncationremains.
Authoredranges/caps/nonmutation tests pass; worldreviewno blockers.
Privateparser .tmp/integration/inspect_pending_2d.py TRACE printsdecodedJSON.

Whythistrace: earlierzeroqueued meantONLY3Dfallbackqueue. Separate2Dqueue stores
workuntilVideoOutTakeBatchaftercomputecopy. Adjacentrun28framehad50draws, butits
targetduring983-987sunknown. Do notguessqueuebehaviorfixwithoutcurrentevidence.
Current3Dsourcewatchcannotexclude2D orrejectedprepared/snapshotdraws globally
suppressedbydedup. Newrun29 testsmergedmainfirstandcapturependingatcopy.

Run28 is STOPPED deliberately: child 20652, launcher session 63840. The stop was
recorded in autonomous-clinic-28/stopped-by-agent.json after all required evidence
was captured. Its binary is committed 0692bb2, still local. The LUT fix had passed
154/154 tests before this run. Inputs: warning frame75/Cross1, Offline1440/Cross2,
Continue2265/Cross3. Copied Timmy seed17 and private cache-v13 (195 checked entries).
HUD remains warm gray; no movement or visible gameplay has been established.

LIVE LUT FIX VERIFIED: exact e3a561d29fa73f82 dispatch executes 1024 threads and
4096 writes. Source lut-atlas.raw (16 KiB) and exact final-bound final-lut.raw
(64 KiB) match independently at all 4096 voxels / 16384 float components, bit
exact with zero nonfinite or mismatched values. Validator:
.tmp/integration/validate-clinic-lut-atlas.py. This separate rendering defect is
fixed; it does not by itself restore the world image.

Run28 source-watch completed 49 events without truncation. At 983.147564s a full
LinearColorFill writes ff808080 to display 8bfe8000. No accepted draws to either
watched target occur before the full LinearBufferCopy at 987.722529s copies that
display into final source 8dcd0000 (0x7f8000 bytes). Synchronization sees exactly
one overlapping target, dirty1/gen262, so skipping stale GPU readback is correct.
The gray source is a real clear/copy sequence; do not bypass it or GPU authority.
IMPORTANT next diagnostic gap: both agents independently found deferred 2D queue
is outside HostBackend3D source watch. Adjacent frame has50 presentation batch
draws; target inside983-987s not captured. Queue2D returns executed/gpu_queued
without writing guestpixels; only VideoOut TakeBatch consumes it, aftercompute
copy. Need bounded pending2D source/destination snapshot atcopy and accepted
queue/take/retarget outcome trace. Do not change queue behavior speculatively.
Preparation/snapshot rejection diagnostics also globallydedupand can miss a
watched-target rejected draw. Existing watch proves no accepted3D only.

Private conclusions: run28/source-watch-analysis.md/.json. Rejected fullscreen
CS92803800 is only an IMAGE_STORE constant fill to HDR94420000, not a compositor.
Only the 3D fallback queue was zero; deferred 2D ordering is NOT ruled out. Next: finish validated upstream merge, then probe its renderer
before extending unsupported compute operations speculatively.

Run27 is STOPPED deliberately at974.717s, child32208/launcher77128. Runtime
ca82f81 is tested (154/154 pass24.01s) LOCAL ONLY; published37aaeab remains unchanged.
CopiedTimmyseed17/cachev13. Inputs verified: warning75/Cross1, Offline1530/Cross2,
Continue4125/Cross3. BlackHUD5280/hashade2c6c5428102f0, armedafterHUD.
FinalPS loaded649.69s; truefinalcapture828.222s and sourcewatchend831.799s.
Finalsource8dcd0000grayff808080; output8bfe8000black; LUT65536byteszero.

PROVEN LUT BUG: exacte3a561d29fa73f82 atlas-to-volume compute dispatch33030 is
unsupported_program/zero writes, rsrcC00C2/A18, local4,16,1, groups1,1,16.
Sourceinlineu4..11 is11f06020016x256RGBA8/UNORM/FAC/tile13/pitch16, mips/arrays0,
word3=94d00fac. Outputdescriptor8words atpointeru2/3 names11062970016^3RGBA32F,
FLOAT/FAC/tile13/pitch16, word3a2d00fac,word51e000(lastarray15; 3Ddepth notlayers).
This run's exact finalconsumer matchesoutputaddress, withlastarray0.
Read-only source16KiB lut-atlas.raw has4096uniqueRGBA entries; RGBminmax0..255,
0..255,0..243, alpha255. Final-lut.raw remainszero. Expectedlookupofgray128 is
RGBapproximately139,135,123 afteractualLUTcopy; this alone won'trestoreworldvariation.

PROVEN GRAY COPY: sourcewatch17events,no truncation. GPU26c5 writes8dcd twice,
then831.737064s CS10eef0000 fullLinearBufferCopy copies8bfe8000→8dcd0000,
0x7f8000bytes, matchingcounts0x1fe000dwords, nozero tail. FullcoverPrepare,
Invalidate dirty0→1/gen128, Refreshgray nextfinal. Independentcomputecapture
proves source8bfe fullLinearColorFill0.5,0.5,0.5,1 producesff808080.87laterfull
copiesallgray. InterveningGPUdraws/sourceSyncstillunresolved. Do notskiprealclear/copy.


Recipient current HEAD e48e963 on Uptownfrog; this newest commit is LOCAL ONLY.
The published baseline remains37aaeab. All154tests pass24.65s after the exact
RGBA8 component_swap1 regression failed against the old GPU-image guard.
Captured26c5 producer shaders already export physicalBGR, so host R8 format
remains unchanged; only the matching swap1 RGBA8 eligibility is admitted.
An optional stable PS filter and appended BGRA-conversion eligibility diagnostic
were added. All private shader caches remain unchanged (v13,195entries).

Run26 is STOPPED deliberately at1296.366s (owned child6252). Final-pass filter
PS56c499c7c845fa48 worked: warning75/Cross1, Offline1830/Cross2,
Continue4875/Cross3, black HUD6615/hashade2c6c5428102f0. Armed after HUD;
599.283s capture proves full-screen final pass (2,073,600 PS invocations).
Exact source8dcd0000 has CPU authority (dirty1/gen443) and uniformRGBA128,128,128,255;
output8bfe8000 is all0,0,0,255. All16 final bindings repeat dirty and generation+3.
Exact bound16^3 RGBA32F LUT110629700 read65536bytes, allzero, via validated
read-only process helper. Its shader mathematically predicts captured black.
Private final-lut-analysis.md/json documents CPU-read limitation and hashes.
Source-gray provenance and empty-LUT producer still unproven; do not fake a LUT.

Preparing run27 one-frame source provenance diagnostic plus exact compute
execution results. IMPORTANT: PROGRAM_CAPTURE_DIR does NOT enable dispatch
capture; launcher now explicitly sets BB_GCN_COMPUTE_DISPATCH_CAPTURE_DIR.
Root edits header, CPU copy/fill/color/DMA callers and capture outcome; agent
world_rendering edits only backend source-watch logic. No builds until agent
finishes; no live child currently. ThreeDimensionalByte generic upload recognizes
captured10eef0b00 but only admits R8/tile19; LUTRGBA32F/tile13 incompatible.
Need actual dispatch state before extending semantics. Indirect dispatch currently
counts only; a missing direct LUT match cannot exclude an indirect producer.

Run25 deliberately stopped599.016s: grayHUDframe4935/hash7631755cbc3c589b.
34targets captured491.15s afterHUD butmidframe ontextureimport; notfinalpass.
Geometry/HDR scene variation exists. Near-empty temporarytargets contain37pixels
and are not proof of the final source version. Exact swap1 candidate was verified
against pinned compiler export and capturedsidecars; no establishedLUTdefect.

## Current publication checkpoint - 2026-09-08

Permanent branch: **Uptownfrog**, explicitly designated by the user. Recipient:
`external/Bloodborne-Recompiled`; donor remains local and is not authorized for
push. Owner main and all pre-existing branches must never be modified. Active
AGENTS.md files and recipient hooks now enforce the new rule.

Run24 is STOPPED by the agent (child32304, recorded manual stop). Last verified
live state: Timmy's saved-world HUD over a gray screen. Run23 captures show the
clinic in intermediate MRT/HDR targets, but final post-processing is unresolved.
Run24's pipeline capture used stale target addresses from another run; it never
armed. The old LUT descriptor storage was reused, so no payload was captured
from its stale address. Private probe helper now defaults to all target addresses
and requires a verified HUD before creating its arm file.

A new authored RGBA8 GPU producer -> BGRA F2E consumer regression failed against
c722cf1 because the consumer used stale CPU bytes. The recipient working tree
fixes it with a bounded GPU readback/conversion/upload, per-target generation
caching, and retained image-view lifetimes. Final Release build passed; all 154/154 CTest tests passed in 24.21 seconds.
The recipient checkpoint is docs/checkpoints/2026-09-08-uptownfrog-clinic.md.
Publication COMPLETE: recipient commit 37aaeab18c89766fa225c4b6135e7b9aa210d224
is pushed to origin/Uptownfrog and the recipient working tree is clean. The user
explicitly approved the AGENTS.md/hook replacement after automatic review had
blocked the obsolete branch policy; that blocker is resolved. Only Uptownfrog
was created remotely. Owner main (5904129cc7446fd8cfaefd41d3011ce91eca68b8)
and codex/g2a-checkpoint (f8a0554dc10d29632974b7bd56423d68bc19391b)
were verified identical immediately before and after publication. No owner ref
was updated. This donor policy/handoff commit remains local; do not push donor.
No claim that this fixes the live gray-world output; it needs a new probe.

Unity and its other project remain untouched. Build with one worker and do not
build while a live game test is running. All game data/caches/captures remain
private and ignored. Always name test hunters Timmy and copy seed saves.

The notes below are historical; they do not authorize the old branch or imply
a live process remains running.

## Autonomous continuation - saved-character world load (2026-09-07)


LATEST 2026-09-08 (supersedes older active-run notes below): recipient HEAD
640df89. Full154/154tests pass24.94s (clinic-rg8-ctest.log). Completecachev13:
195checked,0rejected, all186v12entriespreserved+9newkeys. No pushes/ownerbranch
changes. Work onlycodex/integration-validation; Unity remainsuntouched.

ACTIVE run24 .tmp/integration/autonomous-clinic-24, child32304, launcher71369.
Runtime source/recipient HEADc722cf1 (ARM_FILE+liveimagebindingdiagnostics),
full154/154tests pass25.85s in clinic-active-capture-ctest.log, completev13 unchanged.
Seed17copied. Warningframe75/Cross1, Offline1275/Cross2, Continue2295/Cross3 all
visuallyverified. Nowloading. ARM_FILE path run24/arm-pipeline.txt ABSENT: root
must visually verify actualHUD first, THEN createfile toarm. Main draw+flushfilter
8bfe8000, alltargets. Gate logs capture_armed; first16 selecteddraws log full
pixel_image_binding live descriptors+SRVslot+nativeGPUtargetcompatibility/gen/dirty.
No build/compiler duringrun. World_rendering read-onlydiagnostics; mutex_capacity
owns tests/boot/orbis_precompiled_shader_tests.cpp to author (NOT runyet) RGBA8
GPUtarget→BGRA F2E staleCPUfallbackregression. Rootownsrenderer/input/builds.

Private read-onlymemoryhelper .tmp/integration/read_guest_lut.py ready/reviewed:
--pid PID --address 0xADDR --byte-count65536 --run-dir ABS_RUN --output ABS_RUN/lut.raw
(pathinsideexistingrun, overwriteforbidden, exactchildpathverified, read-onlyrights,
1MiBcap, UTC/SHA/creationtime/regions). AfteractualLUTbindinglogged, read its64KiB
16³RGBA32F payload whilechildalive, thenanalyzewithshader_compilation (currentlyidle).
Previouslycaptured LUTaddress110629700, but verifycurrentbindingbeforeuse.

Run23 child29448 deliberately stopped445.076s aftercapture.27targets358.46s in
pipeline-targets and preview pipeline-analysis/clinic-mrt-montage.png show actual
clinicroom/material/lighting in sixMRTs andHDRa7f40000/94480000. HDR94410000constant
RGB0.14111328125/A1, displaygray128; BUT capturepredateslatePS382–391s, so94410000
is NOT provenactivefinalsource. NonfiniteHDR only8paddedrows, notvisible1080.
Exactfirst94410000 producerPS1206bfbf5896827a@10f0d4000 copiesHDRa7f40000 with
validUV andallnativeCanCopyTargetImagegatespass. LatePS10f0cb300(ec30e1d0cbf7a50e)
edgefilters8dcd0000;10f0d4c00(97d23b13486f59a4)13tapblur8da90000/gain2.2;
10f0ca500(56c499c7c845fa48) samples8dcd0000 then16³LUT110629700, exportsBGR.
Captured8dcd:1920x1080/pitch1920 RGBA8BGRAF2E/tile14;8da9:960x540/pitch1024.
Neither inearly27targets; descriptors dedupedbyPS/VSaddresses maybestale.
F2Eoutside nativeGPUtargetmappingcompatibility; fallbackCPUread hasnoGPUreadback.
Needactualarmedsource pairingbeforeclaimingcause. AllinspectedDXBCmatchesv13.

Separatealiasbughypothesis: overlapping9441/9448targets retainedindependently,
SynchronizeMemory publishesaddressorder notlastGPUwrite, andreadstartinglaterbase
mayrejectearlieroverlap. Noevidenceyetcausesgray; don'tfoldspeculativefixintoactivework.
Nativeviewportauditfoundnosupportedclinicrange/clipdefect. Ownermainbranches
remainreadonly/unchanged; no pushes. Unityuntouched. Visibleworld+hunter+movement
stillrequired; onlyintermediateroomrenderingverified.

Run22 properly reached clinic HUD frame2430 but still uniform gray. All13 formerly
native-IR-blocked pairs now match exact captures and have both DXBC modules.
Private compiled-sidecar-ir-gate-verification.json/md records each event/hash.
Former4096² absent-stencil shadow pass now also captured without rejection;
PS789f868cb53636dd and VS04deb1c2ee13d02b modules created. Backend at381.214s:
98194 prepared/ready/attempted/executed, all failure counters zero. Root stopped
verified child80220 intentionally at392.674s; stop record, faultnull/FFFFFFFF.
Visible world/hunter and movement remain required, not verified.

Run21 naturally crashed in intro at193.899s, guest0263B8E7/read4/R14=4, same
metadata allocator pool as20. No clinic conclusion, no manual stop. Ignored
.tmp/integration/clinic-heap-fault-audit.md contains exact84-slot/stride0x30/
payload0xFC0 and locked DLLightMutex caller evidence; no concrete HLE lock defect.
Diagnostic remains design-only. Owner branches unchanged; no pushes.

49f8ecealreadycommitted+tested154/15425.11s: matchingcompiledVS/PSsidecarscan
runwhen nativeIRcannotdecodeDSwordd8d48000; knownIRinterfaceguardsretained,
backendVSpositionfloat4verifiedindependently. AuthoredunsupportedGCN+sealedDXBC
GPUgreenreadback andmissing/corrupt/state/stage/positionnegativecasespass.
13exactrun19pairsacross5PSfamiliesareloggedinprivatecompiled-sidecar-ir-gate-audit.
Explicitstencilformat0 nowclearsstaleSTENCIL_ENABLE in effectivesnapshotcontrol;
rawcapturesremainintact, missingformatanddeclaredS8badbasestillreject. Depth-only
Z32withoutstenciladdressusesD32_FLOAT4bytes (4096²64MiB); packeddepth/stencil8byte
pathretained. Bothstride/readback/padding/stencilretentionGPUtestspass.
640df89addsRG8_UNORMdfmt3/nfmt0texture nativeXY01/FAC; paddedrow,linearsampling,
cache-refreshandunsupportedmapping/formatGPUtestspass. Nootheruncommittedcode.

Run20(49f8ece)neverloadedclinic. EarlyCrossseq2/3wereconsumedduringstartup,
notOffline/Continue; Optionsseq4skippedintro. Video exhaustedhard96capturelimit
(despiteoldenv192). RG8videotexturefailureidentified/fixed640df89. Runendednaturally
399.413s onguest0263B8E7 read4 (movrcx,[r14],R14=4fromallocatorfreelist). Exactfault
isdocumentedupstreamruns245/262; lowerworkerframesmatchrun09heapfailure. Existing
intermittentheap-pathrecurrence, noestablishedHLEcause. NOintentionalstoprecord.

Run19(cbecbe6)reloadedclinicHUDframe5715butgray. PriorPS88c00fecc8e481fc/
VSa584323a4d14aa21t9nullandinitialstencilpassresolved:77175/77175backendattempts
successfulthrough475.826s, allbackendfailurecounters0. Remaining13compiledpairs
blockedbyIRgateand4096²absentstencilformatcasesledto49f8ece. Deliberatelystopped
verifiedchild66816at577.550s; stopped-by-agentrecordretained. Visibleworld/hunter
andactualmovementremainunverified and required. Onlyseed17copiesfornewtests.

cbecbe6 permits real no-RT depth/stencil draws, scalarSV_Depth and sealed exact-pi
outputless contracts with strictactualattachment guards. Color activity is per
MRT nonzerotargetnibble AND nonzeroshadernibble, notcomponentbitintersection
(missingcomponentshaveRGB0/A1defaults). GenuineSVDepthda54 hasCBtargetffffffff,
CBshader0, DB700736 andDBshader11, correctlycolorless. Outputlesscontractsremain
strictrawCBtarget0. Reflecteddeadt-register rawbuffersbindnullwithoutslotshifts;
activebadbuffersstillfail. ResizedDSVs preservepackeddepth/stencil+outsidecrop
inboundedCPUcanonicalrows; explicitscissorcanreusecroppedDSV. CPUreadbacktracks
validrowwidthsandpreservesuntouchedguestpadding, includingL-shapedcoverage.
GPUtestscoverdepth/stencilequality, INCR/discard, maskedSVTargetnoRT, extents,
wrongscalarcolorpassrejection, legacyoutputlessrejection, paddingandslots.

Run18 stopped deliberately at863seconds after successful reload of run17 clinic
save. OnlyverifiedBloodbornechild85348stopped; stopped-by-agentrecordretained.
HUD/menuopen-closepassedprior_Locksyslocktrap;world/huntergray,movementunverified.
NoD3Ddevicefailures; deadflatbuf t9address0 andstencil-onlysnapshotsidentified.
Lateframes3435to3900progressed~1.15fps; saves/fencescontinued,noimport/asserttrap.
Its resultentry_fault/FFFFFFFFisrecordedmanualstop, notnewcrash. Three of five
late17shaderIDs haveexactrun18inputs;2f410a236c531263and506b6502f0a23f6dremainmissing.
Visibleworld/hunter and actualmovement remain required milestones.

Run17:c3f0fe5+v11passedmodff, normalOptionsseq3skippedopeningcutsceneat234.689s.
Frame3090showsgameplayHUD; Optionsseq4openedmenuandIosefkaClinicbanner(frame3210).
World/hunterstillgrayinvisible, movementunverified. Savedataunmountedafternew
userdata0000/0010writes~269.85s; Timmyoffset37352and4246, save-change-auditretains
hashes. It endednaturally402.015s on _Locksyslock exactNIDkALvdgEv5ME (nowfixed).
Seed17worldresumeawaitsrun18verification; seed04and17remainimmutablecopies.
Newcachev12adds6run17missingshadersfromexactrun16state/snapshots; threeare
screen-sizedfour-indexpasses. Five later run17 missesneednewstatecaptures.

Resourceconstraint: another Unityproject is activeandcannotbestopped. Leave
Unityandunrelatedappsuntouched; onebuild/compilerworker; avoidbuild/testoverlap
withlivegame. Slowwalltimealoneisnotproofhang. NativeUIhelperunavailable;
authoredPad/IMEdiagnosticsaretestroute, no physicallivekeyboardclaim. Continue
untilactualvisibleworldandplayercontrol, notjustHUD/menu. No pushes or owner
branchchanges; allworkonlycodex/integration-validation, ownerrefsread-only.


CURRENT UPDATE (supersedes every older active-run note below): recipient34c4369
adds vsprintf with SysV va_list handling;146/146 tests pass9.81s. Run09 ended
in title-demo heap assertion0x208591b at267.960s, no inputs and no EOS seen.
Run10 followed Offline/Continue, passed acosf/EOS, trapped on vsprintf132.914s.
Live EOS fix verified: bounded samples each316 waits, run08 73.006396seconds,
run10 0microseconds/no unresolved waits. This is setup timing, not FPS proof.
Private eos-live-comparison.json and docs/runtime-probe-input.md record evidence.
Run10 cache batch80jobs78success; two shared-memory vertex failures remain.
clinic-v4 adds7pixel shaders without conflicts;73 entries checked,rejected0.
ACTIVE run11: .tmp/integration/autonomous-clinic-11, session19112, copied run04
Timmy seed, clinic-v4, vsprintf binary. Offline/Continue sequence sent by helper.
Actual world visibility/control still unverified. No pushes, all owner refs read-only.


LATEST UPDATE (supersedes older active-run details below): recipient HEAD
`b0328e6`, donor latest prior3500c4f. Added `20c078f` export/geometry setup,
`6082333` acosf, `b0328e6` EVENT_WRITE_EOS SignalFence support. Full146/146 tests
pass after all changes: `.tmp/integration/autonomous-eos-acos-ctest.log`.
Run07 stopped on ES, run08 passed ES/GS and stopped on acosf232.959s. Run08's
zero-valued flags waiting for1 and ignored PM4 opcode0x48 led to EOS support.
Authored EOS->WAIT sequence now has no unresolved wait; actual speed improvement
NOT yet verified. EOS GDS stores remain unsupported (no fabricated fence).
EOS completion packets also use existing growing-buffer replay suppression.

ACTIVE run is now `.tmp/integration/autonomous-clinic-09`, exec session39212;
no inputs sent yet. New EOS+acosf binary, copied run04 Timmy seed, cache
`build/shader-cache-clinic-v3`. Inspect Offline selection then known sequence
Cross(wait60frames)->Cross(Continue). New probes capture every15frames,max192;
GNM performance/cost and new gnm-wait traces are enabled. Current tests saved in
ignored `.tmp/integration` as always. Wait/category files report bounded EOS
signals and unresolved labels; compare addresses/values before changing waits.

Latest cache clinic-v3 checked66/rejected0. Run08 jobs66,64success,2unsupported
vertex captures (062-1126d3a00 and064-1126d3e00) assert on shared memory outside
compute; VGT stage-enable0x45 indicates tessellation setup. Do not fake stage or
shared-memory data. Batch `build/shaders/clinic-post-stages-v1` and audit
selection-audit.json.2new eligible shader keys;8existing entries upgraded only
after verifying new HLSL EXACTLY equals current SM5 lowering of old sealed HLSL,
with identical binding/state metadata. Private assemble_probe_cache.py performs
that explicit check. Cache clinic-v2 is INCOMPLETE: initial audit rejected hash
changes, subsequent AOT command populated only a partial directory; marked
ASSEMBLY-INCOMPLETE.txt, never use it. clinic-v3 is the validated replacement.
Native AOT report `.tmp/integration/clinic-aot-import-v3.json`.

Still NO playable world frame or input-responsive hunter verified. Continue/save
works; current task remains autonomous progress to actual gameplay. Other notes
below describe earlier runs and implementation details.


Active request: continue through keyboard, character creation and into actual
controllable gameplay. Do not stop at the first two milestones. Only work in
recipient `external/Bloodborne-Recompiled` on `codex/integration-validation`.
No owner branch mutations or pushes, ever. Hunter Timmy, copied isolated saves.

Recipient now at `dbae990` (HS setup), preceded by `17349ca` (shader compiler
fixes), `02fff91` (LS setup), `26663fd` (asinf), `35219df` (manual launcher uses
character cache and30min limit), `4affa76` (diagnostic IME). Current full146/146
CTest passes: `.tmp/integration/autonomous-hs-ctest.log`. Native shader-toolchain
contract passes including new authored GCN depth export.9 linkage/FXC tests
pass without skips (fixed test lookup for Ninja compiler location).

Actual game progress: offline menus -> opening movie -> rendered hunter preview,
Timmy accepted -> Finish/Yes -> save. Test input uses explicit diagnostic Pad/IME
files because required Windows desktop automation helper failed setup twice.
The real guest IME GetStatus/GetResult/Term path consumes the name; no guest
memory patches/native UI bypass. This is not physical live keyboard typing.
Native keyboard editing has separate authored control tests. GPU file captures
show actual game rendering. Keep this evidence boundary explicit.

IMPORTANT SAVE: `.tmp/integration/autonomous-clinic-04/savedata/1000` is now a
validated menu Continue seed. It wrote Timmy in userdata0000(offset33732) AND
global userdata0010(offset4246). Run05 confirmed Continue at frame1560 and read
the character successfully. Run03's older save did NOT expose Continue. Preserve
all seeds read-only and COPY to each new run. Never modify original game files.
Game progress after Continue still unverified: no world frame/controllable player.

Runtime progression:
- run04 stopped at969.192s on libc GZWjF-YIFFk (asinf) after finishing creation.
  Implemented std::asin(float), math boundary cases and actual guest XMM0 test.
- run05 Continue -> graphics submitted ->237.158s trap on vckdzbQ46SI(SetLsShader).
  Implemented validated23-word LS program/resource/NOP packets and decode tests.
- run06 passed LS ->158.038s trap on VJNjFtqiF5w(SetHsShader).
  Implemented validated30-word HS program/resource/tessellation context/NOP
  packets and decode tests. These set registers, not hull/domain execution.

ACTIVE `.tmp/integration/autonomous-clinic-07`: launcher exec session70583;
new HS binary, cache `build/shader-cache-clinic-v1`, copied run04 saves,
1800sec runtime/1830sec recorder. No input sent yet at this handoff update.
Inspect current frame/events, then select already highlighted Offline, Cross,
wait menu (Continue selected), Cross. `.tmp/integration/probe_sequence.py <run>
'[[16384,60],[16384,15]]'` replays this observed route using accepted/presented
frame counts. Do not compete with running sequence helper. It stops on result.

Private `.tmp/integration/probe_run.py` launch/frame/input records all env,
seed/cache/source/binary/ELF hashes. `frame <run>` converts latest GPU raw to BMP.
`input <run> --buttons 0x4000` pulses Cross3flips. Up0x10,Down0x40,Left0x80,
Circle0x2000; `--ly 0 --frames30` forward later. Sequence commands decimal.
Current GPU capture every60,max96distinct; performance every15; GNM bounded
cost/performance diagnostics enabled. Program and schema3 indexed snapshots
captured, heavy raw frontier disabled. New cache requires restart (miss memoized).

Local shader cache clinic-v1:64 validated sealed D3D11 entries (55 character +9
new, no conflicts),127 native AOT entries. Compiled entirely from local game
captures; no owner's private bundle. Shader jobs `build/shaders/clinic-local-v2`
(60jobs,59success) plus `build/shaders/clinic-carry-alias-v1` fixes lastjob; all60
now compile.5depth-only jobs correctly excluded from legacy color cache. Audit
`clinic-local-v2/selection-audit.json`:40uniqueeligible,31identicalexisting,9new.
Cache assembly manifest + `.tmp/integration/clinic-aot-import-v1.json` provenance.
Earliercharacter cache55+118 rendershunter with lighting/stat-icon artifacts.

Compiler fixes: copy captured z-export format0x1c4 and DB_SHADER_CONTROL0x203
mask into shadPS4 runtime; scalar/vector uint-add-carry SM5 helper; coalesce
identical readonly ByteAddressBuffer aliases at same t-register. Captured shader
formerly aborted/missing uaddCarry/overlapping t0 now compiles. Depth-only export
is not inserted under color-only legacy key. Pinned native toolchain rebuilt
with `tools/dev.py python external/Bloodborne-Recompiled/tools/build_shader_toolchain.py
--offline --generator Ninja --jobs2` (add spaces to --jobs argument).

All source changes committed locally; never push. The user closed Dota for RAM
and said they would close unused apps. Do NOT close unrelated Unity sessions.
Paging was observed; resident game memory1-2GB vs private6GB, slow rendering.
Computer-use skill26.901.51231 applied but node_repl/sky setup failed; do not
bypass native control restrictions with Win32 UI scripts. Inspect GPU frame files
by .NET conversion to JPEG base64 and functions.image (file conversion only).

Next: run07 past HS -> fix exact next trap/shader frontier -> actual starting
area, input-responsive movement and reload. Keep final claims narrower than
actual evidence, but persist with authorized project work. Update manual launcher
cache or add a copied-Timmy resume launcher when a meaningful world test is ready.

## PC name-entry update - 2026-09-07

Manual testing is now ready: in the recipient root, double-click
`Test Keyboard.cmd` for an interactive text-field test (type Timmy; Enter
confirms, Escape cancels), or `Launch Game Test.cmd` for a fresh isolated
five-minute game test with logs in `.tmp/manual-tests/`. In game menus Space
confirms and arrow keys navigate; Enter confirms only inside the name field.
Both launchers passed file preflight; the rebuilt keyboard tests pass.

The user requested ordinary PC keyboard typing inside the game window, and
specified **Timmy** as the hunter name for game tests. Implemented on the
recipient's `codex/integration-validation` branch: five Orbis IME imports,
focused native child text field, Unicode/caret/selection/Backspace/clipboard,
Enter confirm, Escape cancel, guest-thread text filtering, lifecycle/error
checks, input capture, and focus restoration. No separate OS keyboard grid.
No automatic name injection is enabled in normal game runs.

[Implementation and evidence](external/Bloodborne-Recompiled/docs/pc-name-entry.md).
Release and **144/144 CTest** tests pass, including imported-ABI and native-control
checks confirming Timmy. A bounded 30-second native startup smoke had no CPU
fault or trapped import. Actual name entry in the recipient's character-creation
scene remains unverified: our local scripted route previously stopped at a
connection dialog and the full 3D cache has not been reproduced. Do not claim a
hunter was created here; the native control fixture is distinct from a game run.
Next game-level check should navigate offline creation, type Timmy, finish the
character and observe the next frontier using a copied save. Use the existing
local shader toolchain/captures if more variants are required.

Nothing was pushed; owner main and checkpoint refs remain unchanged. All
absolute branch restrictions persist. No task test or build is running.

## Integration completed locally - 2026-09-07

Recipient checkout: `E:/bloodborne PC port/external/Bloodborne-Recompiled`, branch
`codex/integration-validation`, commit `2e5a653`, based on owner main `9383a61`.
Nothing was pushed. Owner main and checkpoint refs remain `9383a61` and
`f8a0554` after a read-only check. Recipient origin push URL is disabled;
`push.default=nothing` and branch guards are active. AGENTS.md restrictions apply.

[Integration assessment and reproduction](external/Bloodborne-Recompiled/docs/integration-validation-2026-09-07.md)
records the comparison and selective ports: concurrent guest save-file opens
(with actual failing-before/passing-after regression), exported mutex/rwlock
checks, donor-manifest verification and source/run recording. Also enabled
Ninja/clang-cl for the pinned shader compiler. Unchanged Release: 142/142 tests;
integrated Release: 143/143. Shader compiler contract passed. All 28,840 input
files in effective-v2 matched the donor manifest; the hardlinked view stays read-only.

The owner-specific shader cache is not required to bootstrap. We generated a
75-entry intro/menu cache from our own captures and observed rendered intro,
title and dialog frames. Later runs had zero unsupported 2D draws but remained
at a connection error with the scripted route; no local 3D reproduction yet.
A locally captured vertex/pixel pair also compiled through the general compiler
to DXBC, and D3D11 accepted both. Full character-creation cache, visual parity
and playable native gameplay remain unproven here.

The user reports the owner is blocked at player-name entry because the PS4
system keyboard is missing. Recipient source has no libSceImeDialog HLE.
Our `patches/shadps4-research-ime.patch` and `reports/baseline.md` supply useful
name-entry fixture and clinic/quit/reload evidence, but depend on shadPS4's IME
implementation. Next focused feature: reproduce the recipient name-entry import,
implement its actual IME lifecycle and PC text entry, adapt the opt-in fixture
while preserving guest filtering/UTF-16/cancellation, then validate continuation.
This feature has not been implemented yet.

The original Remill/AOT research below remains preserved and paused. No game
test or compiler build from this integration task remains running.

# Bloodborne recompilation continuation

## Development-speed handoff update — 2026-09-07

Documentation only; the project remains paused and the native checkpoint below is unchanged. The user asked for ways to shorten development and to add them to tomorrow's prompt. Read RESUME_PROMPT.md and reports/development-acceleration.md. Finish the pending two-body check first, then prioritize a bounded driver connecting existing leaf/CFG recovery, targeted dependency discovery, and measured runtime build reuse. Preserve independent checks and cold repeats; no speedup or new native milestone is claimed.

## Paused shutdown checkpoint — 2026-09-07 03:48 UTC

Paused at the user's explicit request for shutdown; do not resume until asked. Read reports/native-startup-checkpoint.md and its evidence JSON. **Native startup completes constructors 0–1080 and enters ordinal 1081, out of 18,444 ordered initial constructors. P4 is open; no native boot or playable port exists.**

Current startup-v61-cohort-chain-v1-1-repeat matches v60: 61,981,184 bytes, SHA256 35ae968d1a05f67b8eae42472d8d6e8b745b0d87980c677e097d91089cd3140d. Twenty-two supplements give 408 game objects / 21,847 roots. Use tools/extend_native_startup.py from_run 20260907-p4-cohort-chain-v1-1-startup-repeat to preserve every argument. The 24-instruction indirect wrapper passes repeat checks and three actual mutex/call/tail-return spans; the following 256-entry cohort has 36 observed returns and 220 unobserved entries. The next cohort selection failed correctly because its target is outside the leaf census; continuation.json preserves the completed prefix.

Next actual target 0x1020b7660, RSP 0x700000fff88, 146,063 operations; 4,971 events repeat. Recovery local/cfg/native-frontier-20b7660-v1 finished: two entries (0x1020b7660, 0x1020bcdd0), 302 instructions, no decode issues, seven unknown indirect calls and retained callback/nonreturn/nonlocal obligations. It is NOT yet independently repeated, Ghidra-checked, compiled or added to startup. Next do those checks in fresh directories, then extend v61 into v62/v63 only after gates pass. No project experiment should remain running at shutdown.

Canonical recovery, compiler v12 / semantics v35, base registry-v7, current services/TLS and thirty guards remain; source bytes stay NX. All unknown target, boundary, embedded-data, mutable-table, startup/FP/TLS and exception/nonlocal uncertainty remains. P1 route/profiling/audio is unchanged. All no-cost work/reads remain approved; no PS4 access and no restart request. Approved require_escalated shell calls work around the broken normal sandbox helper. This is native port development, not cybersecurity work. On resumption, continue until user action is needed or the user asks to stop, maintaining evidence and source commits.

## Previous checkpoint — 2026-09-07 03:38 UTC

Continue autonomously; user action: none. Read reports/native-leaf-cohorts.md and its evidence JSON. **Native startup completes constructors 0–213 and enters ordinal 214. P4 is open; no native boot or playable port exists.**

Current startup-v57-pointer-cohort-v1-repeat exactly repeats v56: 61,946,880 bytes, SHA256 36665eb50016d52839f550ae3a0ed4a5cb558f5d0a2be8b76ec4312c29c7f8f1. Twenty supplements give 406 game objects / 21,590 roots. Use tools/extend_native_startup.py from_run 20260907-p4-pointer-cohort-v1-startup-repeat to retain all arguments. The byte accessor and five small batches are complete. A census of exact simple initial-pointer forms identified 9,760 conditional candidates; a 256-entry cohort passes Ghidra and repeated 786,432-case/512-negative native fixtures. Of those 256, 144 subsequently return and 112 remain unobserved. Pointer candidates and compilation do not establish execution closure.

Next actual target 0x10207ce10, RSP 0x700000ffed8, 81,916 operations; 2,508 events repeat. New native-frontier-207ce10-v1 has 24 instructions, one unknown indirect call and one unknown tail jump. Repeated recovery v2-repeat and Ghidra/native CFG compilation are running; inspect their records before continuing. Larger candidate groups use the same exact grammar, source checks and conditional provenance. Canonical recovery is unchanged.

Compiler v12 / semantics v35, base registry-v7, current service/TLS contracts and thirty guards remain; source bytes stay NX. Full startup/FP/TLS/control, unknown targets, mutable tables and previous uncertainty remain open. Independent P1 route/profiling/audio is unchanged. Continue after commits.

## Previous checkpoint — 2026-09-07 03:21 UTC

Continue autonomously; user action: none. Read reports/native-cfg-frontier.md and its evidence JSON. **Native startup executes the newly recovered branching body 0x1020b6e20, with constructors 0–96 complete and ordinal 97 still in progress. P4 is open; no native boot or playable port exists.**

Current startup-v43-cfg-frontier-repeat exactly repeats v42: 61,908,992 bytes, SHA256 bd7892af07a94a1398b49a06ec85c194006e2a31a0e2e344c8ed8d4bd8c3368f. Thirteen supplements produce 399 game objects / 21,303 roots. Use tools/extend_native_startup.py from_run 20260907-p4-startup-cfg-frontier-v2-repeat to preserve all arguments. The additive CFG delta and repeat recover two bodies / 618 instructions, retain eleven unknown calls and existing nonreturn/nonlocal obligations, and reproduce exactly. Ghidra agrees except one independently explained NOP following an exact nonreturn call. Static CFG checks remain distinct from synthetic AOT fixtures and actual execution. The second helper 0x1020bccd0 is unobserved.

Next actual target 0x10263a960, RSP 0x700000ffef8, 3,429 operations; 474 events repeat. Fresh pointer-leaves-v3 is recovered. A recorded sequence is running Ghidra, batch3 compilation/repeat/manifest and startup-v44/v45-pointer-leaves-batch3(-repeat); inspect statuses before continuing. Linear recovery and the first CFG compilation checker failures are preserved and explained in the report. All subsequent gates passed with original compiled bytes retained.

Canonical startup-recovery-v31, compiler v12 / semantics v35, base registry-v7, current service/TLS contracts and thirty guards remain. Source bytes stay NX. Discovery, callbacks, mutable tables, complete startup/FP/TLS and prior uncertainties remain open. P1 route/profiling/audio is unchanged. Continue after commits.

## Previous checkpoint — 2026-09-07 03:04 UTC

Continue autonomously; user action: none. Read reports/native-pointer-leaves.md and its evidence JSON. **Native startup completes constructors 0–96 and enters ordinal 97. P4 remains open; no native boot or playable port exists.**

Current startup-v39-pointer-leaves-repeat exactly repeats v38: 61,861,888 bytes, SHA256 a578469e2f2a847a7fcae9dd98e06e2c431bd7aed0f0b2e5a353e37c8f0051fe. Eleven supplements give 397 game objects / 21,295 roots. Use tools/extend_native_startup.py with from_run 20260907-p4-startup-pointer-leaves-v2-repeat to retain every service/TLS/supplement argument. The accessor-chain-v2 is complete. Three additional conditional pointer-sequence leaves pass independent Ghidra and repeated 9,216-case AOT checks; all three subsequently return in actual startup. Conditional provenance remains distinct from those later observations.

Next target 0x10236f6f0, RSP 0x700000ffea8, 2,726 completed memory operations; 415 events repeat. Fresh local/cfg/pointer-leaves-v2 and ghidra-pointer-leaves-v2 record six supported candidates, one observed and five conditional. Compilation directories local/compiler-spike/pointer-leaves-batch2-compile-v1 and -v2-repeat are in progress; inspect recorder status before publishing their manifest and continuing. Unsupported nearby bodies remain explicit and require separate recovery if reached.

Compiler v12 / semantics v35, base registry-v7 and thirty guards remain current; source bytes remain NX. Complete startup, FP, dynamic TLS/TCB, unknown targets, mutable tables and prior uncertainty remain. Independent P1 route/profiling/audio is unchanged. Continue after commits.

## Previous checkpoint — 2026-09-07 02:47 UTC

Continue autonomously; user action: none. Read reports/native-address-leaves.md and its evidence JSON. **Native startup completes constructors 0–92 and enters ordinal 93. P4 is open; no native boot or playable port exists.**

Current complete checkpoint startup-v31-address-chain-v1-3-repeat has 61,860,864 bytes, SHA256 799263ac542c2d31d3cf2e708d941536558b48adc59a696226618d1a652e4eb9. Seven supplements produce 393 game objects / 21,289 roots. Exact continuation_argv in local/runtime/address-chain-v1/summary.json retains every supplement, --tls main-tls-contract-v1, --services rwlock-contract-v1, loader-plan-v9-runtime-word and the seed. Four RIP-address accessors now pass independent Ghidra/LLVM checks, repeated 3,072-case AOT fixtures and actual native returns. Their addresses are distinct and individually verified. The preserved v1 evidence-checker equality assumption was corrected in v2-individual without changing compiled artifacts.

Next actual request 0x102370950, RSP 0x700000ffea8, 2,325 operations; 387 events repeat. A bounded follow-on workflow local/runtime/accessor-chain-v2 is running (record 20260907-p4-accessor-chain-v2), starting indices 32/33 and limited to three observed targets. Inspect its current status before resuming or launching another run. It stops on any unsupported body or failed gate. Source inspection of 0x102370950 shows MOV RAX,[RDI+0x40]; RET, but only recorded checks can accept it.

Compiler v12 / semantics v35 and base registry-v7 remain current. Source bytes remain NX. Thirty guards, dynamic TLS/DTV/TCB, guest threads, initialization/FP/control closure and prior uncertainty remain. P1 route/profiling/audio is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 02:35 UTC

Continue autonomously; user action: none. Read reports/native-qword-leaves.md and its evidence JSON. **Native startup executes both recovered 64-bit accessors inside constructor 89; constructors 0–88 remain complete. P4 is open; no native boot or playable port exists.**

Current startup-v23-qword48-leaf-repeat matches v22-qword48-leaf: 61,860,864 bytes, SHA256 6634396dd8d0c2fc39781f54df6416d85ee528191185358edb64c41a3c482096. Use all three --supplement directories local/compiler-spike/native-leaf-manifest-v1, native-qword-leaf-manifest-v1 and native-qword48-leaf-manifest-v1; retain --tls local/runtime/main-tls-contract-v1, --services local/runtime/rwlock-contract-v1, loader-plan-v9-runtime-word and the recorded seed. Combined 389 game objects / 21,285 roots. The two five-byte MOV/RET bodies have independent Ghidra/LLVM checks and repeated 3,072-case AOT tests; generalized byte-form regression matches earlier compiler artifacts.

Next stop unknown target 0x102375b10, RSP 0x700000ffea8, 2,035 memory operations; 359 diagnostic events repeat. Fresh local/cfg/native-target-2375b10-v1 records a bounded RIP-relative LEA/RET body, pending Ghidra and native semantic validation. Extend the strict leaf tool for this form, record manifests and continue. Neighboring function candidates remain unaccepted until independently checked.

Compiler v12 / semantics v35 and base registry-v7 remain current. Source bytes stay NX. Twenty-nine previous guards and one TCB-field guard remain; dynamic TLS/DTV/TCB, guest threads, initialization/FP/control closure and prior uncertainty stay open. P1 route/profiling/audio is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 02:26 UTC

Continue autonomously; user action: none. Read reports/native-main-tls.md and its evidence JSON. **Native startup passes its first FS-based TLS access and remains inside constructor 89, with constructors 0–88 complete. P4 is open; no native boot or playable port exists.**

Current startup-v19-main-tls-repeat matches v18-main-tls: 61,860,352 bytes, SHA256 a515938691532404e0363d863af62e914df7f243b1450d5b9cec09144ca4d40b. Add --tls local/runtime/main-tls-contract-v1 to the current --services rwlock-contract-v1 / --supplement native-leaf-manifest-v1 command, retaining loader-plan-v9-runtime-word and the recorded seed. Native main TLS initializes 1,872 bytes below logical TCB 0x74000010000 and its eight-byte self pointer, setting explicit State FS only. Other TCB fields are guarded: 29 prior guards plus one new 56-byte guard. All 328 recovered FS loads use ten checked initial offsets; eight-thread/3,752-call AOT tests repeat.

Next stop unknown compiled target 0x102375af0, RSP 0x700000ffea8, 1,748 completed memory operations; 315 events repeat. Fresh recovery local/cfg/native-target-2375af0-v1 records five bytes MOV RAX,[RDI+0x40]; RET, still pending Ghidra and compiled validation. Extend the leaf compilation tooling and additive manifest, then continue. Initial neighboring bodies are not automatically accepted targets.

Compiler v12 / semantics v35 and base registry-v7 with one supplement remain current (387 game objects / 21,283 roots). Source bytes stay NX. Dynamic TLS/DTV/TCB fields, guest thread creation, complete initialization/FP/control closure and all prior uncertainties remain open. P1 route/profiling/audio is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 02:15 UTC

Continue autonomously; user action: none. Read reports/native-rwlock.md and its evidence JSON. **Native startup completes constructors 0–88 and initializes a reader/writer lock inside ordinal 89. P4 remains open; no native boot or playable port exists.**

Current probe startup-v17-rwlock-repeat matches v16-rwlock: SHA256 b148b8aaca10373843bcf753fc87f931b1b3a649b7f9f14a43ef5b9d02a4ef02, 61,859,840 bytes. Use --services local/runtime/rwlock-contract-v1 and --supplement local/compiler-spike/native-leaf-manifest-v1 with the existing loader-plan-v9-runtime-word and recorded seed. Native reader/writer ownership passes repeated 68,630-call AOT tests; 41 exact bindings now cover fifteen services. Only rwlock initialization is observed in the game trace.

Next actual stop: source 0x10207bf94, instruction FS:[0] eight-byte read, address zero, RSP 0x700000fff00. Explicit probe FS base is zero. Investigate native TLS/self-pointer and supplied offset at RVA 0x53e44a8 (used by following instruction); validate against PT_TLS and independent Ghidra/implementation references. Do not guess complete TCB fields or unresolved TLS module references. The last dispatch event has 1,590 memory operations, not the exact later fault count; 298 events repeat.

All source mappings remain NX. Compiler v12 / semantics v35, base registry-v7 and one native leaf supplement remain current (387 game objects / 21,283 roots). Twenty-nine unresolved data/TLS slots and other initialization/FP/control uncertainties remain. P1 route/profiling/audio work is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 02:04 UTC

Continue autonomously; user action: none. Read reports/native-startup-leaf.md and its evidence JSON. **Native startup completes constructors 0–88; the recovered missing leaf executes and returns inside constructor 89. P4 remains open; no native boot or playable port exists.**

Current probe local/runtime/startup-v15-native-leaf-repeat repeats v14-native-leaf: SHA256 b18c60e343551cbe490d23636bfe7a242aaeeb9641354a1cabf9a55e161dcf6d, 61,848,064 bytes. Add --supplement local/compiler-spike/native-leaf-manifest-v1 to the existing startup command. This adds the independently checked four-byte body at 0x10207f3b0; 387 game objects / 21,283 roots. Two AOT builds and 3,072 synthetic cases repeat exactly. The base registry and loader identities remain preserved; the complete additive compilation manifests enter the new probe identity.

Next stop scePthreadRwlockInit, NID 6ULAa0fq4jA, gateway 0x102bc0cd8, RDI=0x1056a2090, RSI=0, RSP=0x700000ffed8, 1,208 memory operations. The leaf returns to 0x10207f2bf. Investigate the supplied caller around RVA 0x207f280 and native reader/writer ownership; 253 diagnostic events repeat.

Current loader-plan-v9-runtime-word, replay seed startup-v4-runtime-word/canary-seed.bin, direct-memory-contract-v1, compiler v12-memory-sources / semantics v35-divide remain current. All source bytes remain NX; 29 unresolved data/TLS guards and prior runtime/discovery uncertainties remain. P1 route/profiling/audio is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 01:48 UTC

Continue autonomously; user action: none. Read reports/native-direct-memory.md and its evidence JSON. **Native startup completes constructors 0–88 and enters ordinal 89. P4 remains open; no native boot or playable port exists.**

Current probe local/runtime/startup-v13-direct-memory-repeat/startup.exe repeats v12-direct-memory, SHA256 c5e3aada762bdb1c1f6f06653c1148b87e84cb6b0c951253d63c22f26afb6d25, 61,847,552 bytes. Direct-memory-contract-v1 binds eleven native services through 31 exact identities. Native memory uses an explicit 4.5 GiB reserved pool, committing individual allocations; this is not a measured PS4 capacity. First 116 MiB allocation and RW mapping succeed. Authored allocation/mapping checks and the 49,256-case RAM regression pass.

Next stop: unknown compiled target 0x10207f3b0, RSP 0x700000ffed8, 1,205 completed memory operations; 251 diagnostic events repeat. Constructor 89 target 0x1023756e0 entered but did not return. Recover the missing body and cross-check it with Ghidra, then compile and manifest it before continuing startup. Initial byte inspection suggests a four-byte MOV/RET leaf; this is not yet accepted recovery evidence.

Current loader plan v9-runtime-word, replay seed startup-v4-runtime-word/canary-seed.bin, native-memory-manifest-v1, registry-v7-memory-repeat, compiler v12 and semantics v35 remain current. Source bytes remain NX and 29 data/TLS guards remain. Unsupported memory modes/GPU/unmapping, private object layouts, FP/TLS, initialization order, unknown targets, exceptions/nonlocal flow and helper costs remain explicit. Independent P1 route/profiling/audio work is unchanged. Continue after commits.


## Previous checkpoint — 2026-09-07 01:30 UTC

Continue autonomously; user action: none. Read reports/native-mutex.md and its evidence JSON. **Native startup completes constructor ordinal 0 and enters ordinal 1. P4 remains open; no native boot or playable port exists.**

Current probe local/runtime/startup-v11-mutex-repeat/startup.exe repeats v10-mutex, SHA256 a48228830459668f837a30557c45a662c681fbc16a87d83f3c26ec802e98ae5c, 61,830,144 bytes. Service contract local/runtime/mutex-contract-v1/contract.json contains 23 exact bindings for seven stateful attribute/mutex operations. Authored tests repeat 53,267 AOT calls, blocked recursive-waiter behavior, three-thread/1,536-increment exclusion and seven negative boundaries. Native private object layouts, static/named/timed/robust/protocol cases remain explicit unsupported interfaces; trylock is authored-tested but unbound.

Game trace: constructor 0 at 0x1020edf90 returns to 0x100000084, constructor 1 at 0x101fc22c0 enters, two mutexes are created and one lock returns zero. The next stop is sceKernelGetDirectMemorySize, NID pO96TwzOm5E, gateway 0x102bbeaa8, RSP=0x700000fff18, after 418 registered memory operations. Forty-six diagnostic events repeat. Next inspect allocator callers (main RVAs 0x20819f0 / call 0x2081a80 and 0x2081d40 / call 0x2081ea4), establish native memory budget/allocation/mapping contracts, and continue.

Current loader plan v9-runtime-word, replay seed startup-v4-runtime-word/canary-seed.bin, native-memory-manifest-v1, registry-v7-memory-repeat, compiler v12 and semantics v35 remain current. All original bytes stay NX; 29 data/TLS slots remain guarded. Complete initialization order, FP/TLS, unknown targets, exceptions/nonlocal flow, private object layouts, helper costs and P1 baseline route/profiling/audio remain open. Continue after commits.

## Previous checkpoint — 2026-09-07 01:16 UTC

Continue autonomously; user action: none. Read reports/native-mutex-attributes.md and its evidence JSON. **Native attribute initialization/type selection now pass inside the first constructor. P4 remains open; no native boot or playable port exists.**

Current probe local/runtime/startup-v9-mutexattr-repeat/startup.exe matches v8-mutexattr exactly, SHA256 e43bce2608fb9fbe9c420d60e26845c565359277a2a533c58742303f64e2fc81, 61,822,976 bytes. Contract local/runtime/mutexattr-contract-v1/contract.json binds three stateful attribute services through nine exact canonical/PLT identities. Repeated authored tests pass 45,059 AOT service calls and four negative stops. Attributes use native process state and opaque logical handles; direct guest private-layout dereferences remain explicit stops. First constructor ordinal 0 still has not returned.

Next actual stop: scePthreadMutexInit (NID cmo1RIYva9o), gateway 0x102bbfec8. At 154 registered memory operations: RDI=0x1056a5728, RSI=0x700000fff48, RDX=0, RSP=0x700000fff38. Prior init/settype returned zero and requested type 2. Seventeen diagnostic call events repeat. Implement/test native mutex creation and ownership/synchronization, then continue through concrete stops.

Current plan loader-plan-v9-runtime-word; replay seed startup-v4-runtime-word/canary-seed.bin; object manifest native-memory-manifest-v1 / registry-v7-memory-repeat / compiler v12-memory-sources / semantics v35-divide unchanged. All original bytes remain NX. Twelve strong-data and seventeen TLS slots remain guarded. Complete initialization order, FP/TLS, private object layouts, callbacks, guest exceptions/nonlocal flow, helper costs and P1 baseline route/profiling/audio remain open. Continue after commits; native port development is the task.

## Previous checkpoint — 2026-09-07 01:03 UTC

Continue autonomously; user action: none. Read reports/native-runtime-word.md and its evidence JSON. **Native startup now completes both atexit registrations and enters the first constructor. P4 remains open; no native boot or playable port exists. Source bytes remain NX.**

The shared eight-byte libc runtime word is initialized before entry. Exactly eight data relocations bind; 29 other slots remain guarded (12 strong data / 17 TLS). Current plan local/runtime/loader-plan-v9-runtime-word; current probe local/runtime/startup-v7-runtime-word-trace-repeat/startup.exe repeats v6-trace, SHA256 e63d0d3044433d633cc1ad3156b44c980f31939d7e7382c6391234a89352529f, 61,816,320 bytes. Replay seed local/runtime/startup-v4-runtime-word/canary-seed.bin, SHA256 fd3936a99e3629eda04843c671e3776e23e7ef82b08dc698c0a05326e489d9e7. Evidence local/runtime/canary-evidence-v1/checked.json. Compiler v12-memory-sources, semantics v35-divide, native-memory-manifest-v1 and registry-v7-memory-repeat remain current.

Actual constructor ordinal 0 at 0x1020edf90 has entered but not returned. Its mutex helper reaches scePthreadMutexattrInit, NID F8bUHwAG284, gateway 0x102bbfea8, after 148 registered memory operations. RDI=0x700000fff48 / RSP=0x700000fff38. Both atexit calls returned zero. Thirteen optional dispatch/import events repeat exactly; this log does not enumerate every compiled direct call. Ghidra independently checks 59 constructor/helper/PLT instructions. Authored runtime-word tests (4,096 positive, 64 mismatches, two bounds stops) and 20,480 control regression cases pass.

Next implement the validated mutex attribute/service dependency using native state and registered logical pointers, then continue through concrete startup stops. No success placeholders, guessed strong-data/TLS values or original-code fallback. Native startup ABI/order, FP/TLS, exceptions/nonlocal flow, helper costs and P1 baseline route/profiling/audio remain open. This is native port development; keep reporting focused on that deliverable. Continue after commits.

## Previous checkpoint — 2026-09-07 00:15 UTC

Continue autonomously; user action: none. Read reports/native-startup.md and reports/native-startup-evidence.json, then reports/native-load.md. **The first bounded native AOT entry now executes and reproduces its predicted stop. P4 remains open; no native game boot or playable port exists. Original game bytes never execute.**

Main entry 0x1000000a0 calls compiled libc _init_env (RET), then compiled atexit. It stops at source/PC 0x80002f119 reading unresolved __stack_chk_guard slot 0x8000b84e0. Exact RSP decrement 104 and eleven completed memory operations match independent Ghidra/Capstone evidence. Callback registration, constructors and main are not reached. Inputs are an explicitly chosen private stack/argument context, not a completed platform startup ABI; no FP/TLS profile is selected.

Current portable probe local/runtime/startup-v3-repeat/startup.exe matches v2-portable byte-for-byte: 61,802,496 bytes, SHA256 001058c6fb85e8f65ac3524d19cf7c45396e86702aac71658d9daaf679e4b5f6. Bundle SHA256 50c451119975da769a92b5c9bf97f294e60dd2c001ed47d9424f35e16e1df05c; trace identity 5b4745457db251e65336dd81f426289c8d54f67a3cf9ffccada1fb14d75129ba. Evidence local/runtime/startup-evidence-v1/checked.json; contract local/runtime/startup-entry-contract-v1/contract.json. All 18 private data regions are NX; 37 unresolved slots remain guarded. Current compiler/object manifest remains native-memory-manifest-v1 / compiler v12-memory-sources / semantics v35-divide; registry-v7-memory-repeat and loader-plan-v8-memory unchanged.

Next independently establish the native __stack_chk_guard object binding (exact namespace/version, pointer width, initialization, mutability and failure behavior), then remove only those justified guards and investigate the next native stop. Never replace unknown slots with guessed values or bypass the guards. Complete initialization order, native services, target FP/TLS state, fourteen x87 selector sites, guest exceptions/nonlocal flow and helper performance remain open. Native slot 9 stays reserved. P1 route/profiling/audio tasks remain open. Continue after commits.

## Previous checkpoint — 2026-09-06 23:55 UTC

Continue autonomously; user action: none. Read reports/native-load.md and reports/native-load-evidence.json, then reports/native-memory-sources.md. **P4 remains open. Native private data loading now passes; no game-derived CPU function has executed, no native boot exists and there is no playable port.**

Native loader local/runtime/load-v3-repeat repeats v2-sha-width: sixteen private NX regions / 97,517,568 bytes; 238,572 resolved relocations applied; 37 unresolved slots (296 bytes) guarded. All 97,517,272 unguarded bytes match an independent Python relocation/BSS digest. Every unresolved-slot probe stops before reading; eleven malformed/identity cases reject. Bundle SHA256 f2f0ce06c0b96892e3d1634c25e3542a3931189ceec4730352d4bbf3fcc0207a. Evidence: local/runtime/load-evidence-v1/checked.json. Supplied module hashes are unchanged. The loader validator contains no game AOT roots and calls no initializer/entry.

Current full object manifest remains local/compiler-spike/native-memory-manifest-v1/active-objects.json; compiler v12-memory-sources, semantics v35-divide. Registry-v7-memory-repeat / link-v9-memory-repeat / loader-plan-v8-memory remain current. The complete linked validator still rejects entry mode. Next independently verify entry arguments and initialization order, add logical stack/TLS/native service contracts, then investigate the first bounded native startup stop. Keep strong data/TLS unknowns guarded; native slot 9 reserved; mutable constructors, FP profile, fourteen x87 selector sites, guest exceptions/nonlocal transfer and unknown targets explicit. Helper runtime cost is unmeasured. P1 route/profiling/audio remains open. Continue after commits.

## Previous checkpoint — 2026-09-06 23:42 UTC

Continue autonomously; user action: none. Read reports/native-memory-sources.md and its evidence JSON, then reports/runtime-guards.md. **P4 remains open; P3 compilation/explicit handling passed. No game-derived CPU function has executed, no native boot exists and there is no playable port.**

All 386 startup objects now use precise native memory-source bridges and repeat exactly. Active manifest local/compiler-spike/native-memory-manifest-v1/active-objects.json, SHA256 5b573c9ac36fb389c69a9830e9ec299ab5da35781904f078bc99bb6a85ff34e6. Compiler v12-memory-sources / semantics v35-divide; 21,181 entries, 21,282 roots, 18,444 constructors, 874,279 exact bytestrings and all 4,305 nonreturn sites retained. LLVM inspector build/control-audit-v8-memory-fp/control-audit.exe validates 505,682 bridged sites with exact State/source arguments; control counts and all 551 dispatch pairs match prior evidence. Object bytes are 74,174,245; helper runtime cost is unmeasured.

Current registry local/runtime/registry-v7-memory-repeat (identity e2b4ebb39d380c389b53da374442030e43e79f2109d61a252f893b0ecbe6f07e) and complete host validator local/runtime/link-v9-memory-repeat/registry.exe repeat exactly. PE: 61,058,048 bytes, SHA256 38605b045293f8d87b57fe55852f092b3a66a849c4acd23171457e083b7e53c4. All 708 unimplemented import gateways and unknown-target probes stop. Current loader plan local/runtime/loader-plan-v8-memory is bound to that registry; payloads match prior plan and 37 unresolved references remain. Evidence: local/runtime/native-memory-evidence-v1/checked.json. Older object/registry/link generations are preserved, not current.

Next implement and validate private NX module loading with runtime guards over all unresolved slots, then independently verify actual entry setup and native services in dependency order. No guessed strong data/TLS values, automatic constructor-table iteration or CPU fallback. Source guards/calls pass authored checks; target FP profile, fourteen x87 selector sites, conditional export/control assumptions and guest exceptions/nonlocal transfer remain explicit. Native slot 9 stays reserved. P1 route/profiling/audio tasks are unchanged. Continue after commits.

## Previous checkpoint — 2026-09-06 23:26 UTC

Continue autonomously; user action: none. Read reports/runtime-guards.md and its evidence JSON. **P4 remains open; P3 compilation/explicit handling passed. No game-derived CPU function has executed, no native boot exists and there is no playable port.**

Unresolved-slot guards pass repeated authored checks (2,568 AOT, 648 spans, 202 negative boundaries, four setup rejections). The first NOP/load check exposed stale trace-entry PC diagnostics; compiler build/sparse-lift-v12-memory-sources/bb-sparse-lift.exe plus native/runtime/sourced.cpp fix this with explicit State and invocation-local instruction addresses. Successful calls preserve State; fault scopes never span dispatch. Control, FP and memory regressions pass. Evidence: local/runtime/guards-evidence-v2-status/checked.json. Preserved v1 failure is evidence, not erased.

Current active game manifest remains source-exit-manifest-v2-regression/active-objects.json and therefore still uses v11. Next enable native_memory_provenance in all 386 copied game inputs, recompile/repeat and independently inspect source/State arguments plus existing control boundaries before regenerating registry/linkage. Only then proceed to private NX loading with the 37 unresolved relocation guards. Current registry-v5-service-identities, link-v7-repeat and loader-plan-v7-repeat remain the last complete host-only artifacts; they do not incorporate this compiler ABI. Native service slot 9 remains reserved. P1 route/profiling/audio tasks are unchanged. Continue after commits.

## Previous checkpoint â€” 2026-09-06 23:02 UTC

Continue autonomously; user action: none. Read reports/native-services.md and reports/native-services-evidence.json, then reports/native-loader.md. **P4 is open; P3 compilation/explicit handling passed. No game-derived CPU function has executed, no native boot exists and there is no playable port.**

593 canonical external-function identities now cover all 831 function relocation uses, including 143 cross-module identities. Native logical range [0x900000000,0xa00000000) is reserved; future modules must skip it. Current registry is local/runtime/registry-v5-service-identities (identity c6682220b81ce1f78abce9da0daaaee45efaa954027d8fab7e8c1264301efa3b), with 21,282 game roots and 775 import entries. All 708 unimplemented gateways and an unknown target stop correctly. Current complete host-only validator local/runtime/link-v7-repeat/registry.exe is 54,722,048 bytes, SHA256 98bc1df33f8b15d5b42d8807459897f2686bd4b6829cf0d130914a9733f19b99, identical to v6-services. No game entry or guest mapping is created by it.

Loader-plan-v7-repeat reproduces v6-services and leaves 37 unresolved relocations: twenty data imports and seventeen TLS module references. Zero code relocations; all 238,609 destinations and 18,444 constructor pointers remain checked. Next add runtime access guards for unresolved relocation slots, then validate private NX module loading and actual entry setup without exposing guessed values. Resolve/test strong-data/TLS contracts and implement native services in dependency order. All previous unknown targets, mutable tables, conditional exports, absent FP profile and fourteen unresolved x87 selector sites remain visible. Continue after commits; P1 route/profiling/audio work remains open.

## Previous checkpoint â€” 2026-09-06 22:51 UTC

Continue autonomously; user action: none. Read reports/native-loader.md and reports/native-loader-evidence.json, then reports/native-link.md. **P3 compilation/explicit-handling passed; P4 is open. No game-derived CPU function has executed, no native boot exists and there is no playable port.**

Loader plan local/runtime/loader-plan-v5-repeat matches v4-weak exactly: eight modules, sixteen segments, 97,517,568 mapped bytes, 238,609 relocations, zero code relocations and all 18,444 constructor slots checked. These are fresh copied segment bytes and a plan; native private loading is not implemented yet. Library and module versions are checked for supplied symbol bindings. Twelve weak module callbacks resolve to zero only under independently checked ELF/Ghidra evidence (loader-weak-v3-source-identity). Strong imports remain explicit.

752 unresolved relocation references remain: 715 functions, twenty data objects and seventeen TLS module references. Next generate canonical native external-function identities across modules (preserving pointer equality and explicit unimplemented stops), then resolve/test the strong-data/TLS contracts and implement private NX loading plus actual entry setup. Keep constructor mutation, unvisited targets, FP profile selection, guest exceptions/nonlocal transfer and real services visible. The 54,663,680-byte complete registry validator remains local/runtime/link-v5-repeat/registry.exe; it executes no game entries. Active game manifest/registry/compiler/semantics and all P1 work remain as recorded in the preceding checkpoint. Continue after commits.

## Previous checkpoint â€” 2026-09-06 22:37 UTC

Continue autonomously; user action: none. Read reports/native-link.md and reports/native-link-evidence.json, then reports/runtime-fp.md, reports/runtime-boundaries.md and reports/source-exits.md. **P3 startup compilation and explicit-exit-handling gate passes; proceed to P4. No game-derived CPU function has been executed, no native game boot exists and there is no playable port.**

All 386 current objects link with 21,282 compiled roots and 182 import gateways. The complete host-only validator repeats byte-for-byte: local/runtime/link-v5-repeat/registry.exe, SHA256 307f10134ca4236b89ead17006b72b80c14af2617a3c5321a9df1ed4bae8190b, 54,663,680 bytes. It validates tables without calling game entries; all 115 external native gateways and an unknown target stop correctly. The 67 exact bundled-export bindings are conditional on loader/initialization/interposition contracts. No universal success stubs or CPU fallback exists.

Registry local/runtime/registry-v3-repeat matches v2-ghidra; identity SHA256 e73b23f8b12cad14b6352ef944f3b190a1649de1d0ab07a231ea9564e311d7c4. It has 551 source/request pairs and 335 x87 metadata sites. Fourteen additional R12/R13-based x87 sites have Ghidra-checked boundaries but unresolved default selector metadata; they remain explicit stops. No target FP profile is selected. Gate passage establishes compilation and explicit handling, not game startup or service completeness. Current unknown indirect/callback/control counts and canonical recovery v31-conditional-repeat remain unchanged.

Active game object manifest remains source-exit-manifest-v2-regression/active-objects.json, SHA256 e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6. Compiler v11-source-exits and semantics v35-divide remain pinned. Next P4: private NX module data loading, exact relocations/BSS, initialization order and logical stack/TLS, then actual native entry with precise service stops. Guest exceptions/nonlocal recovery, real services and profile selection remain open. P1 route/profiling/audio work is unchanged. Preserve all runs and immutable game files. Continue after commits.

## Previous checkpoint â€” 2026-09-06 22:23 UTC

Continue autonomously; user action: none. Read reports/runtime-fp.md and reports/runtime-fp-evidence.json, then reports/runtime-boundaries.md. **P3 remains open. No game-derived object has been linked or executed; no native boot/playable port exists.**

Explicit FP profile/metadata and fault bindings pass 32,768 authored AOT cases and twelve precise negative boundaries; three setup rejections pass. FP-v3-repeat matches v2-payloads exactly. Memory-v4-fp-regression (49,256 cases) and control-v6-fp-regression (20,480 cases) pass unchanged outcomes. Evidence is local/runtime/fp-evidence-v1/checked.json. No PS4 FP profile is inferred or selected by default. Runtime faults remain noexcept process stops; guest exception/nonlocal recovery and real service bindings remain unimplemented.

Current complete startup manifest remains source-exit-manifest-v2-regression/active-objects.json, SHA256 e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6 (386 objects / 21,181 entries / 21,282 roots). Compiler v11-source-exits, semantics v35-divide, recovery v31-conditional-repeat and all unknowns remain unchanged. Next generate immutable target/import/source-pair and x87 metadata tables with input identities, then link the full object set into a host-only registry validator. Do not invoke game entries during linkage validation. P1 route/profiling/audio-crash work remains open. Continue after commits.

## Previous checkpoint â€” 2026-09-06 22:13 UTC

Continue autonomously; user action: none. Native runtime memory/control prototypes now pass repeated authored checks. Read reports/runtime-boundaries.md and reports/runtime-boundaries-evidence.json, then the preceding source-exit checkpoint. **P3 remains open. No game-derived object has been linked or executed; no native boot/playable port exists.**

Memory-v3-repeat passes 49,256 cases, eleven precise negative exits and two setup rejections; control-v5-repeat passes 20,480 authored AOT cases, nine negative exits and one setup rejection. Nineteen selected artifacts match their preceding deterministic runs exactly; recorder/source ZIP checks pass in local/runtime/boundaries-evidence-v1. Private code/data mappings are NX; code writes stop explicitly. Native target/import dispatch and source/request checks have no CPU fallback. The actual fault handlers use noexcept process termination, not guest exception recovery. Native arithmetic and compiled-export imports are authored fixture bindings, not validated game services.

Current active game objects remain local/compiler-spike/source-exit-manifest-v2-regression/active-objects.json (SHA256 e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6): 386 objects / 21,181 entries / 21,282 compiled roots. Compiler v11-source-exits and semantics v35-divide remain pinned. Canonical recovery v31-conditional-repeat and all unknowns remain unchanged. Next implement remaining FP/numeric bindings with explicit profile/segment provenance, generate static tables from the checked dispatch registry, then validate complete linkage. No target FP profile is selected by default. P1 Hunter's Dream, profiling and opening audio mutex investigation remain open. Continue after commits without a new user confirmation.

## Previous checkpoint â€” 2026-09-06 21:35 UTC

Continue autonomously; user action: none. Read reports/source-exits.md and reports/source-exits-evidence.json, then reports/control-exits.md, reports/linkage.md and reports/call-return.md. **P3 remains open. No native game boot or playable port exists.** No game-derived object has been linked or executed.

Current complete object manifest: `local/compiler-spike/source-exit-manifest-v2-regression/active-objects.json`, SHA256 `e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6`. All 386 objects replace the preceding set; do not re-add old or diagnostic objects. Source-exit-compile-v3-repeat matches v2-all for every input, root/unit list, audit, bitcode and object. Total: 21,181 entries / 21,282 unique roots / 18,444 constructors / 874,279 exact checked instruction byte strings / 67,835,213 object bytes.

Use compiler `build/sparse-lift-v11-source-exits/bb-sparse-lift.exe`, SHA256 `20fd7b06fafc7ae97c6cecccfb64ed0f5fd605d537e0c9125b0cbc10e469bbcf`; semantics remain `build/extended-semantics-v35-divide/amd64_avx.bc`, SHA256 `9fb5e55e7d5dde0482182afda9e3160f3d33298f3b724c1d21111df26446a8fa`. SoftFloat remains build/softfloat-v2-repeat/softfloat.lib. All 4,305 exact nonreturn annotations now retain source, owner and conditional evidence in inputs. Ordinary call returns are checked before restoring the continuation. Sourced block-transfer hooks carry actual/requested target and executed source; unexpected hypercall returns use a distinct fault reason. Unclassified compiler endings reject.

Source-exit authored tests pass 28,672 cases and repeat, including 24,576 hardware comparisons and 2,048 mocked hypercall faults. Ordinary-call regression remains 14,336 cases with identical native object/outcome; input and sparse regressions pass. Pinned saved bitcode has semantic inlining, before clang O2. The new LLVM audit separates structural CFG reachability from total sites: 61,370/61,536 sourced faults, 552/4,813 block transfers. All 4,305 unique nonreturn sites have structurally reachable guards. Neither count is guest execution coverage or final machine-path count.

The dispatch registry `local/compiler-spike/source-exit-dispatch-v2-tail-imports` validates 551 distinct direct-branch source/request pairs: 524 compiled-root pairs and 27 verified import-stub pairs. Native dispatch is still unvalidated. Runtime imports number 182 stubs, including five tail-only stubs absent from the 177 COFF unresolved PLT symbols. Ghidra independently verifies all five new stub boundaries. COFF additionally needs 63 support/library bindings. Thirty-five duplicated constants / 90 definitions / 12 objects remain independently compatible. Current repeated audits: control-exit-inventory-v10-source-repeat and whole-program-linkage-v11-source-repeat. Latest full evidence check: source-exit-evidence-v2-instruction-bytes.

Canonical recovery is unchanged at `local/cfg/startup-recovery-v31-conditional-repeat`, DB SHA256 `f33d86bb063c338e4bebaf603ae6f32f53e9bbf49f9bf7dd70c8506edc7959ef`, manifest SHA256 `3f729683862cf6c3aa7ebbcfbaef625cff078d27e33d10b30d7f04c0a16b5f99`. Keep 9,044 unknown indirect calls, 430 indirect jumps, 143 callback arguments, five conditional ending obligations and three native service-control obligations visible. P0/P1/P2 evidence is unchanged; baseline observations are not native execution.

Next implement and validate native control/fault handlers, source/target dispatch checks and native/bundled import binding compatible with nounwind, then link the complete set before deciding P3. No success placeholders, interpreter/JIT/reassembly or original CPU fallback. P1 Hunter's Dream route, profiler overhead / CPU-GPU-queue costs and audio mutex crash remain open. Approved elevated shells and installed tools work; no restart or read approval is needed. Preserve all runs and immutable game views. Continue after commits until the user stops work or an actual user action is necessary.

## Previous checkpoint â€” 2026-09-06 20:58 UTC

Execution continues autonomously; user action: none. Read reports/call-return.md and reports/call-return-evidence.json, then reports/divide-semantics.md, reports/control-exits.md and reports/linkage.md. **P3 remains open.** All 21,181 current entries compile into 386 objects with 21,282 unique compiled roots and every initial constructor exactly once. Native boundary handling and whole-set linkage remain unvalidated. No native game boot or playable port exists.

The compiler continuation validates source-aware ordinary call-return guards: legacy AOT follows the wrong continuation in 4,096 authored cases and ignores 4,096 declared nonreturn assertions. Pinned check_call_return applies only to asynchronous hypercalls. New build/sparse-lift-v10-exact-read passes 14,336 authored cases (8,192 explicit faults), fourteen input checks and a byte-identical repeat. Exact instruction read limits fix a CALL/POP fusion conflict; Ghidra independently confirms all three instruction boundaries. This compiler has not yet replaced any active game object. Next add source/reason to missing exits, migrate all 4,305 exact recovery annotations into input return_contracts, then rebuild and audit the complete set. No native game execution or production unwind is inferred.

Current active object manifest: `local/compiler-spike/divide-integration-manifest-v1/active-objects.json`, SHA256 `36683365f7bf8b4ec59043f05587a8d418aa38a9827e829f99b8c53fe1b084c0`. It replaces thirteen previous complete objects with divide-replacement-compile-v2-repeat: 632 entries / 695 compiled roots / 38,394 instructions, with the same 204 missing starts. All thirteen objects repeat byte-for-byte; their total is 3,533,901 bytes. The other 373 objects retain their identities. Old files remain preserved; do not re-add superseded or diagnostic objects.

Canonical recovery remains `local/cfg/startup-recovery-v31-conditional-repeat`: 21,181 entries / 874,279 instruction addresses / eight modules, byte-identical to v30. Database SHA256 `f33d86bb063c338e4bebaf603ae6f32f53e9bbf49f9bf7dd70c8506edc7959ef`; manifest SHA256 `3f729683862cf6c3aa7ebbcfbaef625cff078d27e33d10b30d7f04c0a16b5f99`. All 18,444 initial constructors, including 16,069 outside unwind entries, are decoded and compiled. There are zero rejections/quarantines under recorded conditions, while 9,044 unknown indirect calls, 430 indirect jumps, 143 unknown callback arguments, five conditional continuations and three service-control obligations remain visible. Neither recovered bodies nor object compilation establishes execution coverage.

The new COMI/UCOMI extension fixes concrete NaN/denormal, guest MXCSR, fault and host-state defects: the old module differs in 245,718 of 851,968 authored cases; the replacement and fresh repeat have zero differences, including 121,600 matching unmasked faults. All 49 recovered sites (32 VUCOMISS / 17 VUCOMISD) select the authored binding. No original game instruction was executed. Use build/extended-semantics-v35-divide for new compilation, SHA256 `9fb5e55e7d5dde0482182afda9e3160f3d33298f3b724c1d21111df26446a8fa`, with build/sparse-lift-v8-selector-audit and the unchanged build/softfloat-v2-repeat/softfloat.lib.

DIV/IDIV correction now passes 327,680 Python-oracle/hardware/AOT cases, including 218,424 precise native faults, with zero differences and a fresh exact repeat. Legacy division had the wrong PC for every fault, plus two host-overflow cases in IDIV32 with a double-width signed minimum divided by -1. All twenty selector names are replaced with unsigned-magnitude arithmetic and explicit reason/width fault hooks. The 28 recovered division sites all select these bindings. Original instructions/game data remain untouched. The COMI regression remains byte-identical and passes all 851,968 cases.

Current LLVM census: `local/compiler-spike/control-exit-inventory-v8-divide-repeat`, byte-identical to v7-divide. All 386 modules verify and match all roots. There are 4,818 missing-block calls, 9,134 function-call intrinsics, 20,149 returns, 442 jumps, zero generic error calls, 56 explicit divide-fault calls, 58 SIMD fault calls and 5 asynchronous / 4 synchronous hypercalls. Zero indirect LLVM calls. Missing-block PC arguments are loads; ordinary Remill control calls carry nounwind. Preserve source instruction and exit reason; target availability does not authorize dispatch. Main 0x210b730 is both a compiled entry and the excluded continuation after the conditional call at 0x210b72b.

Current COFF audit: `local/compiler-spike/whole-program-linkage-v9-divide-repeat` reproduces v8-divide for all structured artifacts and 386 raw nm logs. Of 239 unresolved names, 177 are verified import stubs (67 supplied compiled-export candidates, 110 external) and 62 support/library bindings. No unclassified direct targets. Raw COFF and LLVM readobj check 35 duplicated constants / 90 definitions / 12 objects in coff-constants-v3-divide. The separate 4,366 compiler missing-start records retain their source classifications: 4,178 after control contracts, 165 compiled-root transfers, 23 verified import tails. They are not the emitted-IR call-site count.

Next extend the validated ordinary call-return checks with source instruction and exit reason for the remaining missing-block/hypercall exits, then migrate and rebuild the complete set. A known compiled destination is insufficient to authorize dispatch. Validate compatible nounwind handling, native service/support contracts, compiled export binding and linkage before deciding P3. No successful-return placeholders, interpreter, JIT or original CPU fallback may replace native behavior.

Reproduce recovery from the original startup-db-v1 seed with all documented jump/control/callback/object/service/symbol/Lua evidence and `--conditional-control-evidence local/cfg/conditional-control-checked-v1/checked.json`; use reports/conditional-control.md for the full command. Never seed from an extended database. All runs use tools/run_record.py and fresh outputs; always use UTF-8. Preserve divide-characterize-v1, which terminated on host overflow. V2 captured failures in the authored subprocess; V3 records both exact failing inputs. Current semantic/test/replacement repeats pass.

P1 Hunter's Dream route, profiler overhead / CPU-GPU-queue costs and the opening audio mutex crash remain unchanged. Existing LLVM/Remill/Ghidra/JDK/Tracy installations and approved require_escalated shells work. No restart, read approval, paid component, PS4 or user action is needed. Continue until the user asks to stop or a concrete user action becomes necessary.

Updated 2026-09-06 02:12 UTC. Execute the authorized PLAN.md autonomously. Read reports/STATUS.md, reports/startup-closure.md, reports/control-flow-evidence.json, reports/baseline.md, reports/compiler-spike.md and reports/decisions/0002-promoted-state-and-control-boundaries.md first. No PS4 access exists. No playable native port exists.

## Current result and next work

P0 passed with optional trophy/DLC limits. P1 reaches clinic movement, normal game quit and reload of the moved position in a separately instrumented shadPS4 build. A Windows guest save-file sharing bug was reproduced independently, identified as error 32 in the runtime, and fixed separately. The opening audio-thread mutex crash remains unresolved.

P2's bounded feasibility gate now supports proceeding to P3: eleven real roots / 13,584 full-state cases; real relative jump table/RIP data; callback/nonlocal transfer; TLS/locked XADD/MFENCE fixtures. State promotion reduces representative longer-kernel ratios below 2x; tiny list length 1 remains 2.22x. The 1000-object scale survey still has 842 unresolved execution boundaries and is not execution coverage.

Next: use local/cfg/startup-recovery-v22-cache-repeat/analysis.sqlite, specifically its recovery_* tables, plus compilation-manifest.jsonl/frontier.jsonl/constructor-order.json. These four artifacts reproduce byte-for-byte from v21-cache. All 18,444 initial constructor bodies remain decoded, including 16,069 outside all unwind ranges. There are now 21,178 entries / 874,266 instructions across eight modules. Twenty-nine Ghidra-checked conditional control summaries reduce fence findings from 146 to 8. Exact callback argument roles expose 65 new entries and further indirect work. P3 remains open: 9,044 indirect-call records, 430 indirect-jump records, 143 unknown callback-argument records and native import/callback/exception/control contracts. Read reports/startup-closure.md and reports/startup-closure-evidence.json for exact remaining addresses and reproduction commands. No P4 game execution is established by these incomplete gates.

Priority continuation: the sparse compiler adapter is now implemented and all 12 formerly rejected entries build reproducible objects; read reports/sparse-compiler.md. The full compilation survey now exposes 48 rejected entries (including two constructors) and eight quarantined boundary cases. Investigate exact rejected instruction semantics with independent checks, then extend callback provenance and indirect tables/vtables. Read reports/startup-v9.md and reports/startup-batch.md. The current checked derived summaries are local/cfg/bad-alloc-control-checked-v1/contracts.json; the earlier 28 are identical inside the new 29-entry set. Recovery regenerates from the default startup-db-v1 seed with --jump-evidence local/cfg/startup-table-bytes-v1/tables.json --control-evidence local/cfg/bad-alloc-control-checked-v1/contracts.json. Never pass an extended database as the seed. The derivation tool's current experiment is intentionally pinned to v4 and its base contracts; extending it to a source with existing derived summaries must explicitly carry their transitive evidence.

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

The current permission profile is managed workspace-write with automatic review. The normal sandbox helper again fails setup; authorized require_escalated shell calls work. Use that working route. No restart or read approval is needed. Earlier desktop Node initialization failures were not retested; do not assume shell recovery proves that UI helper works. Root Git may need per-command safe.directory; do not modify global configuration.

Maintain durable status and investigate failed gates. No PS4, proprietary SDK purchase, emulator endpoint or direct-execution substitution is authorized as a replacement for native recompilation.

P3 checkpoint: the prior 128 constructor objects remain preserved. The new 65-entry dependency batch builds 52 Windows objects; 12 sparse and one disputed entry are explicitly excluded. Forty-two new objects retain CPU boundary declarations; none were executed. Twenty-eight focused checks pass. Ghidra checks all 28 derived helper summaries (254 instructions) and all 65 new entries plus remaining issues (73 windows, 3,234 shared instructions with LSDA roots supplied). Sixteen remaining reachability differences follow annotated nonreturn calls; raw evidence is retained. Run audits in order: tools.summarize_startup_closure, tools.summarize_startup_recovery, tools.summarize_cfg. Earlier v1 overexpansion/export failures, v4/v5 repetition, constructor compilation and table evidence remain intact. This continuation started from clean d05363e, following e47c900 and 3f83339.

User preference: all cost-free actions in the plan are approved. Continue in this chat; do not repeatedly ask for read confirmation. No paid component or user action is pending. P1 remains separate: Hunter's Dream route, profiler overhead and CPU/GPU/queue costs, and intermittent opening audio mutex crash. No new P1 run occurred during this P3 continuation.

Sparse compiler checkpoint: native/sparse_lift uses an isolated audited copy of the pinned Remill TraceLifter with exact instruction maps, no filler and no input-code execution. build/sparse-lift-v3/bb-sparse-lift.exe leaves the old lifter/libraries unchanged. local/compiler-spike/sparse-manifest-v4 and sparse-manifest-v5-repeat build 12 byte-identical objects: 1,517 instructions, 46 roots, 159,654 object bytes; 27 explicit missing paths retain control/transfer obligations. Ten input checks and 8,192 authored AOT cases pass in sparse-checks-v4. One disputed dependency entry and the nine graph fence findings remain. Previous failed builds/checks and timestamp-only repeat mismatch are retained. Use -mno-incremental-linker-compatible for deterministic COFF object emission. reports/sparse-compiler-evidence.json is integrated in the recovery/control-flow audits. Continue working after committing; the user explicitly asked to proceed until an actual user action is necessary or they say stop.

Latest continuation: startup-v9-evidence.json checks byte-identical recovery, 33 focused tests, all 29 helper summaries / 265 instructions, and fifteen nullable __cxa_throw destructor arguments. Ghidra checks all ten changed windows (1,131 shared instructions); 52 extra instructions follow ordinary fallthrough after documented nonreturn calls. One libc backward jump disappears after the new _Xbad_alloc terminal; no other instruction set changes. Full startup-batch-all-v1 survey attempts all 21,152 issue-free manifests: 21,104 entries including 18,442 constructors compile into 372 objects / 63,178,585 bytes; 48 reject, eight manifests stay quarantined. All objects are static evidence and none were linked or executed. First reported failures include BLSR/BLSI, several missing AVX semantic families, FNSTENV/FXSAVE and eight decoder-error categories still requiring exact diagnostics. Old semantics and sparse driver v3 remain unchanged.

The added RIP-relative RVA-zero negative check passes; local/cfg/startup-recovery-v10-zero-guard reproduces the v8/v9 database, manifest, frontier and constructor order byte-for-byte. Keep v9 as the current analysis path; v10 is the unchanged guarded-code repeat.

Rejected-instruction inventory: build/sparse-inspector-v1/inspect.exe (native/sparse_lift/inspect.cpp) confirms all 14,595 instructions in the 48 rejected entries decode with matching boundaries. local/compiler-spike/startup-rejection-inspection-v1 lists 889 problem sites: missing selectors and 16 UD2 explicit traps, no invalid decode. Ghidra all-48 comparison is local/cfg/ghidra-compiler-rejections-v1. Implement missing semantics in an isolated module and give traps an explicit native boundary; do not classify UD2 as unreadable bytes. The original sparse driver/semantics still remain unchanged.

The all-48 Ghidra check and tools.check_compiler_rejections pass: all 14,595 instruction identities agree; 202 extra instructions in fourteen windows are explained by ordinary fallthrough after exact nonreturn annotations. No unresolved instruction-byte disagreement remains for the rejected batch. Native BMI/SIMD/state semantics and explicit UD2 boundary handling are the next compiler work.

Current compiler continuation: build/sparse-lift-v5/bb-sparse-lift.exe supports an explicit semantics directory and manifest-declared UD2. Use build/extended-semantics-v1/amd64_avx.bc for the authored BMI extension. Old driver/semantics remain unchanged. BMI forms pass 34,816 full-State/defined-flags/memory cases against bit-scan and authored hardware references; trap_fixture verifies the exact fault address and terminal handler, with no hardware UD2/game execution. Sparse 8,192-case regression still passes. startup-bmi-trap-recompile-v1 and v2-repeat produce seven byte-identical objects for fourteen formerly rejected entries, including sixteen explicit native UD2 sites. Combined compiled entries: 21,118; 34 compiler rejections plus eight quarantined manifests remain. reports/bmi-trap-evidence.json audits identities and distinct roots.

Current vector checkpoint: all 18,444 initial ordered constructor entries now compile. Use build/extended-semantics-v3-blend-rsqrt/amd64_avx.bc, including BMI/SHUFFLE/BLEND/RSQRT. Fresh startup-vector-recompile-v1 and v2-repeat compile seventeen of the original forty-eight rejected entries into eight byte-identical objects / 538,686 bytes. They supersede the previous fourteen-entry BMI/trap batch; combined with original startup-batch-all-v1 successes, the total is 21,121 entries. Thirty-one compiler rejections and eight quarantined manifests remain. reports/vector-semantics.md/evidence and tools/summarize_vector_semantics audit actual symbols, constructor coverage, source identities and checks. Authored cases: shuffle 32,768; blend 122,880; rsqrt 399,360; BMI regression 34,816. No game execution. RSQRT is a native LLVM intrinsic with host estimate results; AMD Jaguar bit-exactness is unverified. The constructor 0x10326c0 exposed RSQRT and BLEND after SHUFPS was fixed; all three now compile with tested selectors.

Current packed/transfer checkpoint: reports/packed-semantics.md/evidence audits local/compiler-spike/startup-transfer-recompile-v1 and v2-repeat. Forty-one of the original forty-eight rejected entries compile into eleven byte-identical objects / 1,022,023 bytes, superseding earlier extension batches. Combined with startup-batch-all-v1 successes: 21,145 entries; all 18,444 initial constructors; seven rejections and eight quarantined boundaries. Use build/extended-semantics-v6-transfer/amd64_avx.bc with BMI, SHUFFLE, BLEND, RSQRT, PACKED and TRANSFER in that order. New authored packed/select/transfer cases: 262,144 / 376,832 / 593,408; all earlier BMI/shuffle/blend/rsqrt contracts also pass against v6. Original sources/modules remain unchanged. Failed v4 duplicate-selector build and transfer-v1 missing fixture reader are preserved and diagnosed.

Current precise floating checkpoint: reports/fp-semantics.md/evidence audits startup-fp-recompile-v1 and v2-repeat. Forty-six of the original forty-eight rejected entries compile into eight byte-identical objects / 1,134,668 bytes, superseding earlier extension batches. Combined census 21,150; all 18,444 initial constructors. Use build/extended-semantics-v9-sqrt/amd64_avx.bc, built from BMI, SHUFFLE, BLEND, RSQRT, PACKED, TRANSFER, MINMAX, ROUND, SQRT in that order. New min/max / round / sqrt authored cases: 1,572,864 / 4,194,304 / 3,145,728, with 397,448 / 618,933 / 1,875,621 precise native fault cases. local/compiler-spike/semantic-suite-v9 passes all ten families. Host MXCSR is unchanged by the new integer semantics. __bb_native_simd_fault is an explicit nonreturning runtime dependency, not PS4 exception delivery.

Retained floating fixture failures: CRT longjmp v1 hit STATUS_BAD_FUNCTION_TABLE; builtin Windows escape v2-v5 corrupted restoration because its saved frame base disagreed with biased RBP. Disassembly evidence is recorded. v6 uses the P2-style System V escape frame and restores host nonvolatile registers. The shared authored helper is native/semantics/fp_fixture.h. No general Windows unwind compatibility is implied. All game objects remain unlinked/unexecuted.

Immediate next compiler task: libc 0x30430 (FNSTENV/FLDENV) and 0x53cd0 (FXSAVE). Complete missing-selector inventory is in reports/fp-semantics-evidence.json. Inspect x87 state coherence first: push/pop does not maintain tags; FNINIT writes FSAVE view while other code uses FXSAVE; status is split between cached SW and state.sw. FNINIT is absent from current recovered startup instructions; do not relabel its source issue as an observed startup path. The recovered x87 census has fld/fstp/fldz/fxch plus comparisons and a few arithmetic/conversion forms. Add authored hardware/AOT tag/environment checks and a coherent state contract before accepting serialization. P3 runtime/control closure, eight disputed boundaries, indirect/callback/native service/exception work remain open. Continue after commits; no user action is needed.

X87 investigation: reports/x87-state.md/evidence records 11,520 authored cases, with 10,176 selected-field counterexamples. The 355 recovered x87 sites belong to twelve entries; FNINIT is absent. Stack tags/overflow, forced single precision, overlapping initialization and host-control isolation remain unresolved. Do not accept FNSTENV/FLDENV/FXSAVE merely to compile the final two bodies. Original Remill sources/modules remain unchanged. Continue independent callback/indirect provenance recovery; current inspection exposes callee-saved constants lost across calls and callback loads from mutable relocated slots. User action: none.

Latest callback checkpoint: read reports/callback-relocations.md/evidence. Current recovery v13 repeats v12 byte-for-byte and requires both --sysv-callee-saved-candidates and --initial-callback-relocation-candidates plus the existing jump/control evidence. Keep original startup-db-v1 seed. Eleven additional constant callback arguments and 142 initial mutable function-slot bindings expose eleven new libc bodies / 407 instructions. All prior instruction sets are unchanged. 94 Ghidra windows agree on 4,030 shared instructions; five extras follow existing nonreturn calls. One new object repeats (34,421 bytes), combined with original 372 plus final FP eight: 21,161 compiled entries in 381 objects, no duplicate logical roots. Two x87 rejections/eight quarantines persist. All 144 unknown callback records remain semantically unknown; 142 now have initial candidates. Forty-two focused checks pass. Next inspect the libc branch-merged destructor argument and entry-point incoming finalizer, then indirect/vtable provenance. Continue after commits; no user action is pending.

Latest callback slice: reports/callback-slices.md/evidence. Current v15 repeats v14 and requires --callback-slice-evidence local/cfg/callback-slices-checked-v1/checked.json in addition to both v13 candidate flags and existing jump/control evidence. Main entry RSI remains an unbound native-finalizer callback; libc 0x631c0 has the independently checked destructor target 0x5f390. Two new wrappers / two instructions produce a repeated 572-byte object. Combined 21,168 entries / 382 objects; all initial constructors; two x87 rejects/eight quarantines. Fifty-one focused checks pass. Next inspect shared constructor factory 0x2ba2b10 -> 0x207fa50 -> 0x20819f0 and its table assignments. User action: none; continue after commits.

Latest object dispatch checkpoint: reports/object-dispatch.md/evidence. Canonical v17-dispatch-repeat reproduces v16; use --object-dispatch-evidence local/cfg/object-dispatch-checked-v1/checked.json plus all existing flags. Three initial table-slot candidates add two bodies / 39 instructions and one repeated 4,162-byte object. Combined 21,165 entries / 383 objects; two x87 rejects/eight quarantines remain. Ghidra checks source operands, raw relocation bytes and the new closure. The independently checked 2,165-constructor cohort / 25,980 instructions is ready for candidate expansion; 2,630 other shapes remain separate. Fifty-eight focused checks pass. Next expand the checked cohort and the nested lock slot at 0x207f07c, retaining unknown calls and mutation/initialization assumptions. User action: none; continue after commits.

Latest constructor cohort checkpoint: reports/constructor-cohorts.md/evidence. Canonical v20-subobject-repeat reproduces v19; use --object-dispatch-evidence local/cfg/object-dispatch-expanded-v3-subobject/checked.json plus all existing flags. 4,767 initial candidate records retain all unresolved calls; 4,761 of 4,795 constructor [RAX+0x20] sites have independently checked initial provenance. Three new bodies / 237 instructions build one repeated 21,448-byte object. Combined 21,168 entries / 384 objects; two x87 rejects/eight quarantines remain. Sixty-four focused checks pass. Next independently slice earlier cache-register definitions at the remaining 34 sites and follow lock receivers in 0x207cd90. User action: none; continue after commits.

Latest cache-slice checkpoint: reports/constructor-cache-slices.md/evidence. Canonical v22-cache-repeat reproduces v21; use --object-dispatch-evidence local/cfg/object-dispatch-expanded-v4-cache/checked.json plus existing flags. All 4,795 constructor [RAX+0x20] records have independently checked conditional initial candidates; every unknown runtime record remains unchanged. No new body/object: 21,168 compiled entries / 384 objects, two x87 rejects/eight quarantines. The bounded worklist fixes repeated branch enumeration and recursion depth; both failures are retained. Sixty-nine focused tests and exact old callback-slice regression pass. Next investigate canonical x87 state/tag/serialization contracts with authored hardware tests, and continue lock/other indirect closure. User action: none; continue after commits.
