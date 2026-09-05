# P3 sparse manifest compiler

Updated 2026-09-05 22:14 UTC. All twelve dependency bodies rejected by the earlier contiguous consumer now produce reproducible Windows objects. P3 remains open; no game-derived object was executed, no native game boot or playable port exists.

## Exact input and compiler boundary

`native/sparse_lift/main.cpp` consumes explicit instruction-address/byte rows and ordered logical entry roots. Only supplied bytes are readable; gaps stay absent. It rejects overlaps, duplicates, interior control targets, incorrect instruction boundaries, unsupported semantics and unvisited manifest instructions. An explicit missing target remains a recorded runtime boundary. The audit counts successful pre-optimization semantic lifts, not execution coverage or complete function boundaries.

`tools/build_sparse_lift.py` compiles a minimally audited copy of the hash-pinned Remill TraceLifter into a separate executable. Hooks check instruction starts, exact decoded bytes and successful semantic lifting. Existing Remill libraries and `remill-lift-21.exe` remain unchanged. Build identities include original/audited source, tool and linked-library hashes. Output uses LLVM Windows AOT bitcode and native COFF objects; the tool performs no input-code execution.

The adapter uses manifest entry, LSDA landing pads, independently recovered table targets and in-map direct-call targets as roots. Ordinary direct jumps stay inside their trace. Removing unnecessary direct-jump roots reduced 225 roots / 1,437,824 object bytes to 46 roots / 159,654 bytes while preserving all 1,517 instruction identities. This does not implement exception entry or indirect dispatch.

## Evidence

| Check | Result |
| --- | --- |
| Previously rejected sparse entries | 12 / 12 objects built |
| Supplied instructions / bytes | 1,517 / 5,369 |
| Compilation roots / object bytes | 46 / 159,654 |
| Missing paths | 27, all linked to explicit annotated control or external transfers |
| Objects retaining CPU/runtime boundaries | 12 |
| Authored input cases | 10 passed, including absent targets and invalid maps |
| Authored AOT execution | 8,192 cases passed |
| Fresh repeat | All twelve objects byte-identical; COFF timestamps zero |

The authored branch and separate-entry fixture checks low-32-bit branch inputs, result registers, preserved registers, logical return/RSP and guarded stack bytes. It executes only authored compiled host code. It does not establish game runtime, callback, exception or service correctness. All game objects retain explicit native boundary declarations and were not linked or executed.

Current outputs: `local/compiler-spike/sparse-manifest-v5-repeat`, repeated from `sparse-manifest-v4`; authored checks `sparse-checks-v4`; compiler `build/sparse-lift-v3/bb-sparse-lift.exe`. The machine-readable audit is `reports/sparse-compiler-evidence.json`, integrated in the recovery/control-flow reports.

## Investigated failures

The first isolated build lacked Remill's private header include directory; the second built. The first authored check run passed all ten input cases but failed a combined clang-cl source/object command; separate compile/link fixed that invocation. A third driver build added rejection of unsuccessful semantic lifts; all cases passed with it.

The first minimal-root repeat failed raw object equality. All twelve differences were confined to the four COFF timestamp bytes at offsets 4..7. The final compiler command adds `-mno-incremental-linker-compatible`; two new emissions now match without normalization. Earlier artifacts remain untouched. This flag suppresses the timestamp associated with incremental-linker compatibility. [LLVM change and rationale](https://reviews.llvm.org/D51635), [Clang users manual](https://clang.llvm.org/docs/UsersManual.html).

## Reproduce and continue

Wrap every command with `.venv/Scripts/python.exe tools/run_record.py --id UNIQUE --` and use fresh destinations:

1. `.venv/Scripts/python.exe -m tools.build_sparse_lift build/NEW`
2. `.venv/Scripts/python.exe -m tools.sparse_lift_checks local/compiler-spike/NEW build/NEW/bb-sparse-lift.exe`
3. `.venv/Scripts/python.exe -m tools.sparse_manifest_compile local/cfg/startup-recovery-v7-repeat local/compiler-spike/NEW build/NEW/bb-sparse-lift.exe`
4. Audit retained outputs with `-m tools.summarize_sparse_compiler`, then `-m tools.summarize_startup_recovery`, then `-m tools.summarize_cfg`.

Next investigate the nine fence findings and the one excluded disputed dependency entry, then continue indirect/callback/exception and native service closure. Sparse input acceptance is resolved for this batch only. The 9,029 indirect-call records, 430 indirect-jump records, 170 unknown callback arguments, mutable constructor tables and unknown targets remain explicit. Static compilation does not pass the startup execution gate. No new P1 baseline run occurred; Hunter's Dream, profiler overhead/cost separation and the intermittent audio mutex crash remain independent work.
