# Development acceleration recommendations

2026-09-07. Requested during the shutdown pause. This is a documentation-only review of the existing code, saved runs and approved plan. No new experiment or native progress was made. Native checkpoint f4ad5e5 remains startup-v61: 1,081 completed constructors, P4 open, no native boot or gameplay. RESUME_PROMPT.md carries the prioritized instructions.

The strongest near-term opportunity is reducing repeated manual handoffs and discovering relevant dependencies earlier. This is an engineering hypothesis grounded in the current workflow, not a measured project-wide speedup. Complete the already recovered two-body frontier before substantial tooling changes.

## Observed costs and limitations

| Saved evidence | Finding | Implication |
| --- | --- | --- |
| local/runs/20260907-p4-cohort-chain-v1/manifest.json | 74.175 s, parent status failed after the second selection rejected an out-of-census target | The successful prefix is valid, but the automatic workflow ends at a recovery-method boundary. |
| Same run prefix, child 1-ghidra | 12.291 s | Independent decoding has a measurable cost; retain it. |
| Children 1-compile / 1-compile-repeat | 13.447 / 12.622 s | Both actual compilations together cost 26.069 s. |
| Children 1-startup / 1-startup-repeat | 16.701 / 14.990 s | Together 31.691 s, including preparation/build/check/run work, not just game execution. |
| local/runs/20260907-p4-native-frontier-20b7660-v1/manifest.json | 50.30 s for two entries / 302 instructions | Profile recovery setup, metadata and hashing before assuming instruction decoding dominates. |
| tools/native_startup_experiment.py | Fifteen runtime/registry translation units plus x87_numeric.cpp are compiled each time | Unchanged runtime object reuse is a concrete candidate; the existing 386 base game objects are already reused. |
| tools/ghidra_byte_windows.py | New Ghidra project and executable-segment copies per selected module; request construction retains only start/end | Batching can amortize setup. Nonempty additional_roots currently do not reach the Java checker. |
| reports/baseline.md | 63,886,259 zones and memory-limited capture; overhead unmeasured | Use targeted discovery logging, not blanket instruction or tiny-operation tracing. |
| native/runtime/control.cpp | Unknown dispatch records source zero; finite 65,536-event trace limit | Caller attribution is missing. A trace-budget stop must not be confused with a missing function or gameplay failure. |

These are one cohort and one frontier, not a representative throughput sample. tools/run_record.py starts its elapsed timer after creating its own source archive, so the values are command time, not all wall-clock or agent investigation time. No hardware bottleneck or cache speedup has been established.

## Recommended order

1. **Finish the pending native step.** Repeat native-frontier-20b7660-v1, check with Ghidra, compile twice, publish and run the next startup pair. Keep the current checkpoint usable. This exposes whether the next dependency needs discovery, a service, compiler behavior or runtime state.

2. **Connect existing recovery workflows.** Refactor the small existing scripts into a bounded driver with explicit stop classification, per-stage run records, distinct output directories, acceptance checks and an atomic continuation record. Supported leaves use select_pointer_leaf_cohort / compile_leaf_batch; other recoverable bodies use recover_native_frontier / compile_native_frontier. A true mismatch exits with evidence and the last accepted checkpoint; it does not prompt a guessed annotation or service response. Do not rewrite historical failed records.

   Current CFG compilation accepts 1–64 entries in one module, despite a larger optional recovery budget. New imports/source pairs, mixed-module deltas, overlap uncertainty and unsupported control behavior need explicit handling. Audit ownership against the canonical database and accepted supplements before broadening automation. Keep independent decoding independent: provide bytes and justified roots, not the desired instruction listing.

   A bounded regression for this driver is justified because it publishes executable manifests: cover a saved successful leaf case, a successful CFG case, a real rejection, and resumption after an interrupted stage. The payoff test is fewer manual command handoffs with the same acceptance evidence. Time-box the initial change to roughly one or two hours; checkpoint partial improvements and return to the actual native blocker if it grows into a framework project.

3. **Discover likely dependencies ahead of time.** Maintain a queue keyed by module hash/RVA, observation provenance and blocking reason. Prioritize actual native stops, dependencies visible in the associated supplied data, then targeted baseline observations. Use the existing exact-form census in bounded batches; proximity alone is not reachability. Do not make all 9,760 original census candidates a prerequisite for startup. The latest 256-entry cohort had 36 observed returns and 220 unobserved entries, illustrating the need to measure useful work separately from emitted roots.

   The separate shadPS4 research build can collect relevant call/callback/service/module observations and targeted table writes without changing the native execution model. First identify practical instrumentation seams and estimate their cost; baseline boundary hooks will not automatically capture every internal indirect call. Start with startup or an existing clinic route, use bounded records/deduplication and preserve enough ordering/context to interpret them. Independently recover and compile candidates before native use. Absence from a trace, initial relocations and observed table values do not prove static closure or immutability.

4. **Reuse runtime work at two levels.** At build time, profile the sixteen rebuilt native units and consider content-keyed object reuse for unchanged units. Keys must cover compiler/tool versions, transitive headers, flags/ABI, generated configuration and relevant dependencies; startup-config.h changes as manifests change, so not every unit can be reused. Materialize verified artifacts in fresh run directories and identify their producing runs. Keep cache-hit evidence distinct from actual recompilation. Required independent/cold repeats stay in place; copying one object twice cannot establish reproducibility. A small dependency/invalidation check is essential before relying on a cache.

   At implementation time, retain PLAN.md's strategy of adapting selected pinned shadPS4 services and graphics components. Inventory their dependencies and implement coherent families with shared confirmed contracts. Generate repetitive binding metadata only after validating signatures and semantics. Audit State, memory ownership, logical pointers, TLS, callbacks, synchronization, errors and shutdown behavior. Existing emulator loader/CPU entry code is not the native application's entry path. No universal-success stubs, wholesale libc substitution or guessed private structures.

5. **Improve evidence handling where it repeatedly costs time.** Generate a compact checkpoint summary and exact next command from accepted run records. Keep large evidence JSON and immutable source archives as references rather than copying their contents into every prompt. Classify faults as unknown target, service, guarded state, decode dispute, compiler issue or diagnostic budget. Preserve failed artifacts and do not promote a skipped check into a pass.

   The Ghidra wrapper currently drops additional_roots even though BBCheckRecovery.java supports them. Audit/fix this with a relevant independent landing-pad fixture before relying on exception-bearing deltas; it is not evidence that the current two-body pending recovery is wrong. Sourced indirect-call diagnostics may later remove caller ambiguity, but require compiler/invocation-context validation. Do not migrate every object solely for nicer logs before showing that source-zero ambiguity is blocking recovery. Keep existing source-zero records explicitly unknown.

6. **Overlap only independent work and keep the playable route first.** Bound parallel compilation/check jobs by actual memory and CPU behavior. Separate output ownership; no competing writes to a shared analysis DB, build tree or baseline save. Performance measurements run without competing workloads. While compilation runs, useful independent work includes service dependency inspection or preparation of the P1 route/profiling/audio investigation, subject to the session's active delegation rules.

   The next product milestones are real native graphics submission and the first playable opening. Preserve the full-game target, but defer new renderers, speculative recompiler replacements, broad symbol naming, 60-fps optimization and full-game sweeps until the relevant gates. A bigger function count is not a substitute for resolving the next actual blocker.

## How to decide whether this helped

Record total wall time as well as existing stage time, recovery-method handoffs, newly resolved blocker categories, useful observed entries versus compiled-only candidates, cache cold/hit results and the latest native milestone. Track blocked investigation time separately where practical. Compare several representative leaf and branching-function advances before assigning a throughput improvement. The previous month ranges remain speculative planning allowances; do not extrapolate delivery dates from constructor counts.

Keep improvements local and cost-free. Do not require a new PC, external service, another restart or PS4 access. No proposed shortcut changes the native AOT/no-fallback requirement, source-file protection, failed-run preservation, independent checks, or plan gates.
