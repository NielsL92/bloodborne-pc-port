# Initial object dispatch recovery

Updated 2026-09-06 01:36 UTC. P3 remains open. No game-derived CPU code was executed.

Three independently checked initial table-slot candidates add two bodies and 39 instruction addresses. Recovery v16-dispatch and v17-dispatch-repeat produce byte-identical databases, manifests, frontier records and constructor order: 21,175 entries / 874,029 instruction addresses. All previous instruction sets are unchanged. All 18,444 initial constructors remain present; these are initial table contents, not immutable runtime order.

| Observed initial table | Slot | Candidate RVA | Result |
| --- | --- | --- | --- |
| Singleton table 0x53b3060 | +0x20 | 0x2082ee0 | Three-instruction output-value method; newly recovered |
| Factory lock table 0x52b6230 | +0x18 | 0x207ee90 | Previously recovered |
| Factory lock table 0x52b6230 | +0x28 | 0x207f070 | Newly recovered; another indirect call at 0x207f07c |

The constructor factory thunk 0x2ba2b10 jumps to 0x207fa50. Its null-singleton path constructs aligned storage based at 0x56a20c8 through 0x20819f0; that constructor writes the singleton table. Other paths read mutable singleton/cache state. The factory also writes the lock table on its initialization path. Native allocation, guard, lock, initialization failure and interposition behavior remain unresolved. A conditional initial-object candidate does not establish a unique runtime target.

Ghidra checks six source windows / 379 shared instructions. A separate Java reader parses the complete raw ELF64 Rela table and initial slot bytes independently; only three specified slots are inspected. No expected target addends are supplied to that reader. Adjacent pointer-like or zero words are not promoted or treated as table extents. The recovery checks current module/witness bytes and exact relocation identities before using a candidate; every original unresolved indirect call remains.

The two new bodies and eight remaining boundary disputes receive a second independent check: ten windows / 614 shared instructions, no byte/boundary disagreements. One extra instruction follows an existing nonreturn annotation and remains explicitly explained. The eight fence findings stay quarantined.

Both new entries compile into one byte-identical 4,162-byte native object across fresh runs. The audit verifies exact manifest instruction sets, decoded address ownership and actual COFF symbols. Combined retained compilation census: 21,165 entries / 383 objects, including all 18,444 initial constructors. Two x87 entries still reject. Objects remain unlinked and unexecuted; successful compilation is not execution coverage.

## Repeated constructor sequence

Of 4,795 constructor indirect-call sites with operand [RAX+0x20], 2,165 match the exact contiguous cache/factory/call sequence. They all read cache slot 0x5540670 and call the same factory on its null path. Ghidra independently decodes all 2,165 windows / 25,980 instructions and checks the absolute cache operand, register dataflow, conditional branch destination, factory call and virtual offset. The 2,630 other shapes remain separately inventoried. Fifty-eight focused checks pass, including wrong branch/factory, partial/indexed/segmented load, wrong object, instruction gap and wrong slot negatives.

This checked cohort is not yet expanded into v17's manifest; only the first representative currently carries the singleton target candidate. Next expand those conditional records and inspect the nested lock slot at 0x207f07c. Retain mutable-state uncertainty and the original unknown calls.

## Reproduce and continue

Use `local/cfg/startup-recovery-v17-dispatch-repeat`, `local/cfg/object-dispatch-checked-v1/checked.json`, `local/cfg/dispatch-cohort-checked-v1/checked.json` and `reports/object-dispatch-evidence.json`. Each experiment has an immutable `local/runs/20260906-p3-*` source archive and logs. The evidence report lists every run.

Fresh recovery command, wrapped with `tools/run_record.py --id UNIQUE --`:

```
.venv/Scripts/python.exe -m tools.cfg_recover_startup FRESH_OUTPUT --jump-evidence local/cfg/startup-table-bytes-v1/tables.json --control-evidence local/cfg/bad-alloc-control-checked-v1/contracts.json --sysv-callee-saved-candidates --initial-callback-relocation-candidates --callback-slice-evidence local/cfg/callback-slices-checked-v1/checked.json --object-dispatch-evidence local/cfg/object-dispatch-checked-v1/checked.json
```

Recovery retains 9,042 indirect-call records, 430 indirect jumps, 143 unknown callback arguments, eight disputed boundaries and all native service/callback/exception obligations. The x87 state counterexamples remain unresolved. Baseline observations and native execution remain distinct. User action required: none.
