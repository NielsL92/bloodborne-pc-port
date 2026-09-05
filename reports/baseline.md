# P1 baseline investigation

Updated 2026-09-05. The separate shadPS4 research build now creates a named character, reaches the clinic, responds to camera/movement input, quits through the game menu, and reloads the moved position. This uses original game CPU execution. It is not native recompilation or a playable native port.

The unmodified Release baseline and unmodified symbols/Tracy build are preserved. Earlier startup failures and character-creation evidence are in reports/archive/baseline-pre-restart.md. All launches use new private profiles; seeded saves are copied, backed up and hashed before launch. Original packages and hardlinked asset views remain read only.

## Reproducible route and builds

Pinned shadPS4: 22fb56d51c72cdf00b5e21a96e9eb1f5f3eb47db. Current research patch order:
1. shadps4-research-capture.patch: renderer readback and frame-indexed buttons.
2. shadps4-research-ime.patch: opt-in one-shot ASCII name fixture, retaining existing text filtering and UTF-16 commit.
3. shadps4-research-diagnostics.patch: frame-indexed axes and Windows open-error diagnostics.
4. shadps4-guest-file-sharing.patch: guest HostFile opens permit concurrent readers/writers.

Preserved research binaries/PDBs: build/shadps4-profile-capture-v1, shadps4-profile-ime-v1, shadps4-profile-diagnostics-v1. Current build/shadps4-profile includes all four patches. Unmodified builds remain at shadps4-baseline and shadps4-profile-unmodified. Exact hashes are in the dependency lock and capture launch records.

| Capture | Observation |
| --- | --- |
| research-clinic | TestHunter finalized; opening cinematic; standing player and HUD in clinic; save files created |
| research-clinic-reload-continue | Copied initial clinic save reloads; diagnostic Tracy trace captured |
| research-clinic-movement | Camera rotates; character moves; Options menu opens; pre-fix sharing violation diagnosed |
| research-clinic-sharing-fixed | Same copied seed and movement route; System menu; no sharing violations |
| research-clinic-exit-confirm | Exit Game confirmation observed; No selected by default |
| research-clinic-proper-exit | Selects Yes; game returns to title before bounded process termination |
| research-clinic-clean-reload | Copy of properly exited profile reloads the moved character position |

Button/axis fixtures live in tools/fixtures/baseline-*.tsv. First creation uses baseline-clinic.tsv and --ime-text TestHunter for 330 seconds. Movement uses baseline-clinic-move.tsv plus baseline-clinic-axes.tsv for 240 seconds. Proper exit uses baseline-exit.tsv plus the axes fixture for 220 seconds. Clean reload uses baseline-resume-continue.tsv for 180 seconds, seeded from research-clinic-proper-exit.

The pre-fix reload schedule initially stopped at title because an improper-shutdown warning shifted the input sequence; warning images explain those failures. A too-early Options input also did not open the menu. Later schedules preserve the corrected checkpoints; no failed route was relabeled as successful.

## Save-sharing failure and correction

Pre-fix research-clinic-movement logs Windows error 32 on userdata0000/0010 opens (SLSession, write mode, ShareReadOnly). The independent native/file_share_probe.cpp reproduces errno EACCES / DOS error 32 on a new writable file when the second writer opens under _SH_DENYWR; _SH_DENYNO permits both opens. This distinguishes sharing policy from read-only attributes/ACLs.

HostFsBackend previously constructed IOFile with its default ShareReadOnly, which maps to _SH_DENYWR. The separate guest-file patch requests ShareReadWrite for guest regular files; existing mount write checks remain active. Before testing the patch, the target was recorded: eliminate these repeated failed save opens on the copied-seed route and verify normal game quit/reload. Completed fixed captures meet that bounded target. This is not a claim of comprehensive save reliability or quantified game speedup.

The game saves under user/home/1000/savedata/CUSA00207/SPRJ0005 despite application ID CUSA03173; this behavior comes from the supplied game and was preserved. All seeds/backups stay under local test directories.

## Profiling evidence and open issues

Matching Tracy v0.11.1/protocol 69 tools were built locally. Server/tool pin: 5d542dc09f3d9378d005092a4ad446bd405f819a; shad client pin: 143a53d1985b8e52a7590a0daca30a0a7c653b42. Tools: build/tracy-capture/tracy-capture.exe, tracy-csvexport.exe, bb-tracy-frames.exe.

research-clinic-reload-continue produced 63,886,259 zones, a 179 MB compressed trace, and about 130.4 seconds of data. The 10-percent-RAM capture limit stopped it before the requested 160 seconds. Full-trace CPU self time includes Rasterizer::Draw 14.50 s, DispatchDirect 3.66 s and WaitGpuIdle 3.00 s. Millions of tiny memory-tracker zones dominate event volume.

Base FrameMark intervals over trace time 90â€“130 s: 1199 frames, median 33.30 ms, p95 34.67 ms, p99 50.69 ms, 19 intervals over 50 ms. These are diagnostic internal frame intervals in a heavily instrumented run, not a normal-build benchmark or a CPU/GPU cost separation. Profiler/screenshot/log overhead is unmeasured; do not select an optimization target or claim speed from these numbers alone.

| Open issue | Evidence / confidence | Next distinguishing experiment |
| --- | --- | --- |
| Opening audio-thread crash | research-finish: Mv_AudioPlayThread reports Dantelion2 PthreadMutex.cpp(130), invalid mutex EINVAL, then 0xc0000005 at 0xd8d56d2. Before IME entry; subsequent captures pass. Cause unconfirmed. | Bounded repeat with targeted mutex identity/lifetime logging and a dump; correlate create/destroy/use. |
| Excessive trace volume | 63.9 million zones and memory cap termination; directly measured. | Reduce tiny-zone tracing or delayed targeted capture; compare overhead against preserved normal/profile builds. |
| CPU versus GPU bottleneck | Draw/dispatch/wait totals are CPU zones only; no independent GPU/queue/presentation distribution yet. | Targeted GPU timestamps/PresentMon plus at least three matched cold/warm scene runs. |
| Route coverage | Clinic only, no Hunter's Dream or Central Yharnam route. | Extend scripted route on backed-up saves; preserve audio and progression observations. |
| Missing optional files/trophies | Known asset probes and trophy-key absence; no observed clinic startup blocker. | Distinguish optional probes from required paths when a concrete failure occurs. |

No additional installation or user action is currently required. Codex's desktop helper remains broken after restart; domain-level renderer capture and scripted runtime input supplied these observations.

Verified clean reload preview: [clinic-clean-reload-shadps4.jpg](<E:/bloodborne PC port/local/captures/summary/clinic-clean-reload-shadps4.jpg>).
