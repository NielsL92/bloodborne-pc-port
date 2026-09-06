# Constructor dispatch cohorts and subobject closure

Updated 2026-09-06 01:54 UTC. P3 remains open; no native game execution.

The two independently checked constructor sequences now contribute exact initial target candidates to the compilation manifests. The second factory exposes three additional bodies / 237 instruction addresses. Current `local/cfg/startup-recovery-v20-subobject-repeat` reproduces v19-subobject byte for byte: database, manifest, frontier and ordered constructors. It contains 21,178 entries / 874,266 instruction addresses; every prior instruction set is unchanged.

| Constructor sequence | Cache RVA | Factory RVA | Returned-object offset | Checked sites / instructions |
| --- | --- | --- | --- | --- |
| Whole object | 0x5540670 | 0x2ba2b10 | 0 | 2,165 / 25,980 |
| Subobject | 0x5540668 | 0x207bbf0 | +0x458 | 2,596 / 33,917 |

Together they cover 4,761 of the 4,795 constructor call records with operand [RAX+0x20]. Each window is independently decoded and checked with SLEIGH: cache address, register dataflow, branch destination, factory call, object adjustment, cache reload where necessary, and dispatch slot. The 34 remaining sites obtain their cache register earlier in the function and remain separate: 28 subobject sites and six whole-object sites. This grouping is conditional static provenance, not execution coverage or immutable object identity.

Factory 0x207bbf0 writes table 0x53b2e70 at object offset +0x458. Its +0x20 slot initially points to 0x207cb70. The factory's own +0x58 call initially targets 0x207cd90, which calls 0x2085a60 and introduces two further unresolved lock calls. Factory locks use the previously checked initial table; the nested lock +0x10 slot points to the already recovered 0x207ee80. Native construction, initialization races/failure, cache/table mutation, lock semantics and service behavior remain unvalidated.

The extended source check covers ten complete analysis windows / 1,420 shared instructions. Eight specified table/call proposals are independently checked from raw relocation bytes; subobject store displacement is checked explicitly. Repeated cohort expansion yields 4,767 candidate records, including factory/lock calls. Every earlier unresolved record is retained, and the audit checks the exact (module, entry, call, target) set against the proof.

All three new bodies and eight disputed boundaries receive another independent check: eleven windows / 812 shared instructions, no unexplained differences. The ordinary fallthrough instruction after an existing nonreturn annotation remains documented. Boundary windows are not proven function extents.

All three new bodies compile into one 21,448-byte object that repeats byte for byte. The audit checks actual COFF roots and exact decoded/manifest instruction ownership; one missing path stays explicit. Combined retained census: 21,168 entries / 384 objects, including all 18,444 initial constructors. Two x87 rejections and eight quarantines remain. No game-derived object has been linked or executed. Sixty-four focused recovery/provenance tests pass.

## Continue

Use `local/cfg/startup-recovery-v20-subobject-repeat` and its `recovery_*` tables, `compilation-manifest.jsonl`, `frontier.jsonl`, and `constructor-order.json`. Fresh recovery adds this argument to the existing jump, control, SysV, callback-relocation and callback-slice flags:

```
--object-dispatch-evidence local/cfg/object-dispatch-expanded-v3-subobject/checked.json
```

Preserve v18 as the intermediate whole-object cohort expansion. V19/v20 are the current repeated combined evidence. `reports/constructor-cohort-evidence.json` lists all source archives, runs, hashes, independent checks and objects. Existing compilation batches remain retained; the new `subobject-compile-v2-repeat` object adds three entries to the prior 21,165-entry census.

Next independently slice cache-register provenance for the remaining 34 constructor sites and follow the lock receiver paths in 0x207cd90. Continue other indirect/callback/exception closure and coherent x87 state work. The gate still records 9,044 indirect calls, 430 indirect jumps, 143 unknown callback arguments, eight disputed boundaries, two compiler rejects and unimplemented native runtime contracts. Baseline work remains separate. User action required: none.
