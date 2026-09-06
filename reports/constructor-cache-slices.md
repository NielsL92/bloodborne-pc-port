# Earlier constructor cache addresses

Updated 2026-09-06 02:12 UTC. P3 remains open; no native game execution.

All 34 remaining constructor [RAX+0x20] sites have independently checked earlier cache-address provenance. Twenty-eight sites in 0x20b8c80 use the +0x458 subobject cache 0x5540668. Six sites across 0x1c00350 and 0x1fb89c0 use the whole-object cache 0x5540670. These are addresses of mutable caches, not validated runtime cache contents.

Capstone-based slices and an independent SLEIGH implementation follow recovered normal predecessors, register write sets and constants. Exact dispatch-tail checks include the receiver register, factory, adjustment, conditional branch and slot. All three source windows / 1,608 shared instructions agree. Two extra instructions in the larger constructor follow existing nonreturn annotations and remain explained. The slices retain conditional SysV saved-register preservation, metadata entry roots, cycles, unknown writes and budget limits; none of those assumptions implements native dispatch.

Two retained failures improved the analysis tool. The first recursive traversal repeatedly enumerated reconverging branches; its exact child was stopped after 164 seconds. Memoization then hit Python recursion depth on long slices. A bounded worklist now visits each (instruction, register) state once, unions terminal constants, and detects back edges with an explicit DFS stack. The complete 34-site inventory runs in 1.22 seconds. Sixty-nine focused tests pass, including 28 reconverging branches and a 1,600-instruction deep slice. The original two callback-slice artifacts reproduce byte for byte with both the memoized intermediate and final worklist implementations.

Current `local/cfg/startup-recovery-v22-cache-repeat` reproduces v21-cache byte for byte. It has 4,801 initial table-target records; all 4,795 constructor [RAX+0x20] call records have a checked initial candidate. Every prior unresolved record is unchanged. This does not close runtime indirect calls, establish table/cache immutability or prove execution coverage.

No new bodies were added. All 21,178 entry instruction sets / 874,266 instruction addresses are unchanged from v20. The audit verifies every retained object hash and per-entry instruction identity before carrying forward 21,168 compiled entries / 384 objects. All 18,444 initial constructors remain compiled; two x87 rejects and eight quarantines remain. No game object was linked or executed.

## Continue

Use v22 and the existing jump/control/SysV/callback flags, with:

```
--object-dispatch-evidence local/cfg/object-dispatch-expanded-v4-cache/checked.json
```

`reports/constructor-cache-evidence.json` records exact hashes, all retained failures, source ZIP identities, independent checks and reused objects. Keep all earlier runs. The frontier still contains 9,044 indirect calls, 430 indirect jumps, 143 unknown callback arguments, eight uncertain boundaries and unimplemented native service/exception/control contracts.

Next resolve the x87 canonical register/tag/control/status model against authored hardware checks, then its environment serialization and remaining arithmetic contracts. Continue indirect lock receiver closure at 0x207cd90 and other vtable/callback paths. Research into native software arithmetic is preliminary; no new semantic module or runtime correction is claimed. P1 remains a separate instrumented baseline. User action required: none.
