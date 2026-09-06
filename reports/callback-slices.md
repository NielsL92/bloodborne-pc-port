# Branch-sensitive callback closure

Updated 2026-09-06 01:12 UTC. P3 remains open; no native game boot exists.

Current recovery is `local/cfg/startup-recovery-v15-repeat`, repeating v14-slice byte-for-byte. It adds two entry wrappers / two instruction addresses to the unchanged v13 graph. There are 21,173 entries and 873,990 instruction addresses. All 18,444 initial constructors remain in their original order.

The unresolved libc callback at 0x631c0 receives RDX from RCX. Backward analysis of every recovered normal predecessor reaches one of two LEA instructions at 0x6316c and 0x631b0; both produce libc RVA 0x5f390. The analysis preserves alternative paths and rejects unknown writes, partial values, volatile call results, cycles, exhausted budgets and entry/landing-pad registers without provenance. Ghidra independently reconstructs the predecessor graph, register writes and constant operands, agreeing on both source windows / 97 instructions and the complete destructor slice.

Recovery consumes the independently checked per-site artifact, validates the source bytes, exact callback role and metadata roots, and records a separate native runtime obligation. Libc 0x5f390 and its wrapper destination 0x5f9f0 are newly requested bodies. Ghidra checks both new entries and all eight disputed boundaries: ten windows / 577 shared instructions. Five extra instructions in one existing boundary follow ordinary fallthrough after a conditional nonreturn annotation; they are retained.

Both wrappers compile into one repeated 572-byte object with no duplicate roots relative to earlier successful batches. Combined: 21,163 compiled entries / 382 objects. Two x87 entries still reject and eight boundary entries remain quarantined. The object is unlinked and unexecuted, and retains one missing-path record. Fifty-one focused recovery/control/slice tests pass. The earlier integration edit stopped on a text-match assertion before writing; its v1 test wrapper ran the existing fifty checks. The corrected v2 run includes the integration test.

The program-entry callback at main 0xbc remains an incoming RSI value, carried through RBX across a conditional normal SysV call return. The pinned shadPS4 reference passes its ProgramExitFunc in RSI. This corroborates a loader-provided callback interpretation; it is not a PS4 observation or native execution. The native process-entry layer must bind a logical finalizer callback and dispatch it to native code. Do not invent a game RVA or copy the reference's original-pointer execution route.

There are now 143 unknown callback argument records: 142 retain initial mutable relocation candidates and one is the entry-provided finalizer. The full graph still has 9,041 indirect-call records, 430 indirect-jump records, eight boundary findings, x87 counterexamples and native service/exception/control obligations.

Reproduce through `tools/run_record.py` and fresh outputs:

- Slice: `-m tools.cfg_callback_slices local/cfg/startup-recovery-v13-repeat local/cfg/NEW`.
- Independent source windows: `-m tools.ghidra_recovery_check local/cfg/startup-recovery-v13-repeat local/cfg/NEW --selection local/cfg/callback-slices-v1/selection.json --exception-roots`.
- Current independent slice artifact: `local/cfg/callback-slices-checked-v1/checked.json`, checked by `tools/check_callback_slices.py`.
- Recovery: preserve the v13 command's two candidate flags and jump/control evidence, and add `--callback-slice-evidence local/cfg/callback-slices-checked-v1/checked.json`. Keep the original startup-db-v1 seed.
- New-body list: `local/cfg/callback-slice-delta-v1/new-entries.json`; compile with sparse driver v5 and semantic module v9-sqrt.
- Audit: `-m tools.summarize_callback_slices local/cfg/NEW`, then the recovery and control-flow summaries.

Next bounded target: repeated constructor virtual calls use factory thunk main 0x2ba2b10 -> 0x207fa50 -> object constructor 0x20819f0. Inspect its table assignments and relevant slots with independent checks. Mutable singleton state, allocation failure, object identity, table writes, and service behavior must remain explicit. No user action is pending.
