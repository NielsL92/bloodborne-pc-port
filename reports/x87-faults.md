# x87 waiting and exception evidence

Latest 2026-09-06 13:16 UTC: canonical state-image helper evidence is in `reports/x87-serializers.md`. The helper audit passes with a separately measured host pointer limitation; no startup selector or game execution was added.

Updated 2026-09-06 12:53 UTC. The authored stack/control family now passes its masked and deferred-fault comparisons. It remains experimental; P3 is open and no native game boot exists.

`build/extended-semantics-v15-x87-flags` passes 1,499,136 masked cases in `local/compiler-spike/x87-stack-probe-v3` and 720,896 pending/new-exception cases in `local/compiler-spike/x87-fault-probe-v7-memory`. All 285,424 hardware faults match the explicit native callback in occurrence, fault instruction address, pending mask and compared architectural effects. The checks include all six exception masks and all combinations of sticky exception bits for seven control/wait sequences. They compare defined status, nonempty 80-bit payloads, comparison flags, unaffected State bytes, host floating state, memory values and access counts. The fixture checks the imported initial state before each hardware sequence.

The corrections preserve denormal status, recompute exception-summary and busy bits after FLDCW, and write comparison-result flags for newly raised exceptions while suppressing the stack pop when the exception is unmasked. Pending exceptions transfer before a waiting instruction performs its own effects. The callback is `__bb_native_x87_fault(Memory*, State*, pending_mask)` and transfers through the authored bounded System V nonlocal frame. General Windows unwind, PS4 fault delivery and native game runtime integration are not implemented by this fixture.

A wider initial-flags matrix exposed an Intel documentation conflict. The instruction reference says unordered result flags are withheld for an unmasked invalid operation, while an older Intel specification correction A16 says they are written. The independent 65,536-case probe uses FNINIT, memory FLD80 and FLDCW initialization, followed immediately by PUSHFQ; it has no AOT or SEH dependency in the comparison path. All 24,960 unmasked-invalid cases write unordered flags, including 21,840 where those flags change. LLVM disassembly confirms the authored instruction bytes. The experimental implementation follows these two host observations and the correction; AMD Jaguar equivalence remains open. [Intel instruction reference](https://cdrdv2-public.intel.com/812383/253666-sdm-vol-2a.pdf), [Intel Pentium II specification update, A16, printed page 61](https://www.citi.umich.edu/projects/citi-netscape/pdf/24333721.pdf). The latter text was retrieved from the search index; direct PDF retrieval returned 502.

Retained diagnostic results make each change reviewable:

- Fault probe v1: 77,952 differing cases; inconsistent imported exception-summary bits obscure semantic issues.
- v2/v3: 11,616 differing cases after checking normalized initial state. v3 fixes the fixture's instruction-address mapping for hardware/native ABI encoding lengths.
- v4: 744 differences remain with fixed initial comparison flags; unmasked denormal comparisons still need result-flag writes.
- v5: 14,064 differences after varying initial flags exposes unmasked invalid result writes as well.
- v6/v7-memory: zero differences across 720,896 cases. v7 additionally checks that pending faults suppress memory reads.

The audit `tools.summarize_x87_faults` recomputes counts, checks raw observations, object/fixture/semantic identities, all archived source snapshots and unchanged original Remill sources. It also verifies that the accepted v9-sqrt module remains unchanged. Evidence is in `reports/x87-fault-evidence.json`; the recorded audit is `local/compiler-spike/x87-fault-evidence-audit-v1`.

Next, extend the canonical state model into independently checked FNSTENV/FLDENV/FXSAVE serializers, then cover memory conversion and arithmetic families before promoting a coherent module. Guest last-IP/DP/FOP, reserved bytes, undefined condition flags, empty payloads and AMD-specific behavior need explicit treatment. Sixteen corrected selector bindings do not establish correctness for other original x87 operations. The startup census remains 21,168 compiled entries, two rejected serializer bodies (libc 0x30430 and 0x53cd0) and eight quarantined manifests. No new game-derived object was linked or executed.

Reproduce with fresh output directories and run IDs through `tools/run_record.py`: `tools.x87_stack_probe`, `tools.x87_fault_probe` with the sparse lifter v5 and experimental semantics v15; `tools.x87_compare_probe` for the separate hardware probe; `tools.summarize_x87_faults` for the pinned evidence audit.
