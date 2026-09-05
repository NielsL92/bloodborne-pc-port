# P1 baseline investigation

Recorded 2026-09-05. A reproducible shadPS4 baseline has been built and the research build reaches **offline character creation**, including a rendered character model. This is original-game CPU execution in shadPS4, not native recompilation. No clinic/gameplay, save/reload route, whole-game improvement or playable native port is demonstrated.

## Builds and profiles

Pinned source: 22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db, with all recursive submodules initialized and recorded in reports/dependency-lock.json.

| Build | Configuration | Identity / evidence |
| --- | --- | --- |
| Normal baseline | Release, clang-cl 21.1.8, release IPO enabled, Tracy disabled, Discord RPC/updater disabled | build/shadps4-baseline/shadps4.exe; SHA256 09b7bdc5561efcdeda4f7211baad10e4c880bc1d9f402fadf03b24410dbace57; 20260905-p1-release-build, 1,373.4s |
| Unmodified profiling build | RelWithDebInfo, Tracy enabled, same pinned runtime source | Preserved exe/PDB in build/shadps4-profile-unmodified; 20260905-p1-profile-build, 1,408.99s; hashes in dependency lock |
| Research capture build | Profiling configuration plus explicit frame capture/controller schedule patch | build/shadps4-profile; patches/shadps4-research-capture.patch; separately hashed |

The external source checkout now contains the research patch. Do not rebuild the normal baseline from that modified checkout and label it unmodified. Existing normal and unmodified profiling binaries are retained.

Every launch uses a new portable user profile and an empty-save backup manifest. No existing global user saves are touched. The bounded capture tool intentionally terminates its own launched process after the requested interval; exit 1 with reason bounded_capture_end is a capture boundary, not evidence of a crash. A run-record status pass means the capture tool completed, not that every game milestone passed.

The research patch uses the renderer's existing game-only and overlay attachment readback, with one checkpoint every 300 submitted game frames. It feeds an explicitly supplied, frame-indexed controller button schedule through GameController::Button for player 1. It is enabled by BB_RESEARCH_CAPTURE; it neither rewrites game CPU behavior nor provides a native recompilation path. The schedule is preserved in tools/fixtures/baseline-character-creation.tsv and each capture profile.

## Reproduction and checkpoints

The latest input view is local/game/effective-v2: 28,840 files, 31,438,428,662 bytes. Its metadata was independently extracted twice, including npbind/nptitle and trophy data. The first view and all earlier captures remain unchanged; see reports/input-validation.md for the correction history.

From the project root, with a new unique run/profile ID:

    .\.venv\Scripts\python.exe tools/run_record.py --id NEW-UNIQUE-RUN -- .\.venv\Scripts\python.exe tools/baseline_capture.py --id NEW-UNIQUE-PROFILE --build shadps4-profile --research-capture --game-view local/game/effective-v2 --input-script tools/fixtures/baseline-character-creation.tsv --seconds 135

The schedule selects Play Offline, New Game, default brightness, and default controls. It does not complete or save a character. The farthest verified image is the Contract character-creation screen, with Enter Name still incomplete.

| Capture | Observation |
| --- | --- |
| baseline-first-boot | Stopped before game load at Save Migration dialog |
| baseline-ready | Normal unmodified baseline logs game initialization, title assets, graphics pipelines and audio initialization |
| research-render-capture | Title menu visibly rendered |
| research-offline-menu | Play Offline reaches New Game menu |
| research-new-game | Brightness setup |
| research-brightness | Controls setup |
| research-controls | Opening cinematic |
| research-metadata-corrected | Corrected view reaches character creation; no npbind/communication-ID lookup failure |

Full stdout/stderr, input schedules, launch argv/cwd/binary hash, process ID, bounded exit and post-run profile copies are under local/captures. Run wrappers are under local/runs/20260905-p1-*.

![shadPS4 baseline title, not native recompilation](../local/captures/summary/title-shadps4.jpg)

![shadPS4 character creation, not native recompilation](../local/captures/summary/character-creation-shadps4.jpg)

## Findings and distinguishing experiments

| Issue | Evidence and layer | Assessment / action |
| --- | --- | --- |
| First-run migration dialog blocks automation | user_manager.cpp CreateDefaultUsers prompts when home/1000 is absent, even in an otherwise empty profile | Resolved for fresh test profiles by creating empty home/1000-1003 directories. No saves were migrated. |
| Missing npbind/trophy communication ID | Earlier PFS-plus-SFO view omitted metadata outside PFS; log reported Failed to load npbind.dat and no npCommId | Extraction/view defect, resolved in effective-v2. The package metadata is supplied, so no console acquisition was needed. |
| Trophy archive cannot be decrypted | Corrected log: Trophy decryption key is not specified; trp.cpp checks a configured 16-byte ReleaseTrophyKey | Specific optional trophy-data dependency remains. A compiler/SDK installation does not supply it. It did not block title/character creation. Do not fabricate trophy success or ask for PS4 access. |
| Missing-file and stub warnings | logo.tpf.dcx and selected part-file lookups fail; network, trophy and other baseline services log stub/dummy paths | Startup continues. These messages alone are not proof of a fatal missing asset, a correct fallback or complete service support. Keep for later route-specific checks. |
| Desktop UI automation unavailable | Codex computer-use Node kernel fails during sandbox/helper initialization; normal view_image also hits sandbox setup errors | Renderer attachment capture supplies visual evidence. Character-name entry and interactive continuation still need working UI automation or an explicitly implemented IME test fixture. The affected component is Codex's Windows sandbox/computer-use helper, not LLVM/Remill. |
| Optimization target not established | Only startup/menu/character-creation observations, no gameplay workload decomposition | No game subsystem has been selected for performance changes. P2 kernel costs are separately reported and are not game frame-rate predictions. |

No missing proprietary firmware was demonstrated as a main startup blocker; the baseline uses its existing libc-internal HLE path. The supplied seven bundled libraries remain native-CPU work for any future strict port and are not silently excluded.

## Measurement limits and next P1 work

Checkpoint intervals in steady title/menu sections are about ten seconds per 300 game frames, consistent with approximately 30 game frames/s at original timing. They are coarse intervals around capture instrumentation, not per-frame percentile statistics. The rendering GPU in the log is the RTX 4090. No claims are made about GPU duration, PresentMon latency, profiler overhead or console visual fidelity.

The symbols/Tracy build exists, but a Tracy session, CPU/GPU/queue/file/allocation breakdown, matched normal-versus-profile overhead test and route-level stability measurements are not complete. PresentMon, RenderDoc and Vulkan validation layers were not installed speculatively. P1's reproducible-baseline requirement has evidence; the broader gameplay/profile matrix remains open.

A continuation should resume at character creation using a fresh or backed-up profile, enter a test name, reach the clinic and measure the first real route. Restarting Codex may be needed to restore its failed Windows computer-use helper for interactive control. No additional tool installation is presently required for the completed compiler experiments. The missing trophy key is a separate optional data issue and is not the cause of P2's failed performance gate.
