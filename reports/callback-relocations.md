# Callback relocation closure

Updated 2026-09-06 00:52 UTC. P3 remains open; no native game boot or playable port exists.

Use `local/cfg/startup-recovery-v13-repeat`. Its database, compilation manifest, frontier and constructor order reproduce v12 byte-for-byte. The original v9 instruction sets are unchanged. The graph now has 21,171 entries and 873,988 instruction addresses across eight modules, with all 18,444 initially ordered constructors retained.

An explicit optional mode preserves constant values held in RBX, RBP and R12-R15 across a normal SysV call return. Every use remains conditional on the ABI, with 9,354 register-preservation frontier records in the expanded graph. This exposes eleven additional constant destructor arguments, all targeting previously recovered bodies. Branches, landing-pad roots, volatile registers and partial writes remain unknown. [SysV AMD64 ABI source](https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex).

A separate mode follows full-width RIP-relative loads at exact callback ABI sites to initial relocation bindings. It rejects segment-relative loads, truncated pointers, adjusted symbol addends, non-function symbols and ambiguous providers. It retains every unknown runtime callback argument alongside the initial binding candidate; prior writes or later registry/table mutation are not excluded.

The 142 initial candidates refer to two libc function exports: NID `kxXCvcat1cM` at libc 0x59ce0 and `Uw3OTZFPNt4` at 0x5c430, loaded from main-module slots 0x53e4330 and 0x53e4338. Exact relocation type, symbol, NID/library/provider and unique supplied export are audited. Their dependencies add eleven bodies and 407 distinct instruction addresses, including ten additional exception regions and twelve indirect-call records. [Destructor registration ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#dso-dtor).

Ghidra independently checks all eleven new bodies, all affected callback source windows and the remaining disputed boundaries: 94 windows, 4,030 shared instructions, no boundary or recovery-only disagreement. Its decoded absolute memory operands independently agree on all 142 callback slots. Five extra instructions in four windows follow ordinary fallthrough after existing conditional nonreturn annotations. These are retained and reconciled, not discarded.

The new bodies compile into one 34,421-byte Windows object, repeated byte-for-byte against the repeated recovery. It contains no duplicate logical roots relative to the original 372 successful objects and final eight-object floating extension batch. The combined compilation census is 21,161 entries in 381 objects, including all initial constructors. Two x87 entries reject and eight boundary entries remain quarantined. The new object has ten missing-path records and was not linked or executed. Successful compilation is not semantic or execution coverage; `reports/x87-state.md` still records concrete state failures.

Forty-two focused recovery/control/exception checks pass. The callback frontier still contains 144 unknown argument records: 142 now have initial mutable binding candidates; two lack such a candidate. The full graph retains 9,041 indirect-call records, 430 indirect-jump records, eight boundary findings, exception/nonlocal transfers and native import/callback/service contracts.

Reproduce with `tools/run_record.py` and fresh directories:

1. `-m tools.cfg_recover_startup local/cfg/NEW --jump-evidence local/cfg/startup-table-bytes-v1/tables.json --control-evidence local/cfg/bad-alloc-control-checked-v1/contracts.json --sysv-callee-saved-candidates --initial-callback-relocation-candidates`. Keep the default original `startup-db-v1` seed.
2. `-m tools.cfg_callback_candidate_delta local/cfg/startup-recovery-v9-repeat local/cfg/NEW local/cfg/DELTA`.
3. `-m tools.ghidra_recovery_check local/cfg/NEW local/cfg/GHIDRA --selection local/cfg/DELTA/selection.json --exception-roots`.
4. The checked current comparison is `local/cfg/callback-candidates-checked-v1/checked.json`; `tools/check_callback_candidates.py` pins that experiment's inputs.
5. `-m tools.startup_batch_compile local/cfg/NEW local/compiler-spike/NEW build/sparse-lift-v5/bb-sparse-lift.exe --entries local/cfg/DELTA/new-entries.json --semantics build/extended-semantics-v9-sqrt --explicit-ud2`.
6. Current evidence audit: `-m tools.summarize_callback_relocations local/cfg/NEW`, then `-m tools.summarize_startup_recovery`, then `-m tools.summarize_cfg`.

Next: independently slice the remaining libc exception-destructor argument across its branch merge; identify the entry-point finalizer ABI; extend indirect/vtable provenance without treating executable pointers as proven entries. Native x87 state, callback registry, cleanup/exception dispatch and service contracts remain separate gates. No user action is needed.
