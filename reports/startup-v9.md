# P3 recovery v9

Updated 2026-09-05 22:34 UTC. Continue from `local/cfg/startup-recovery-v9-repeat`. P3 remains open; no native game boot or playable port exists.

A new exact callee selection from the nine earlier fence findings exposed libc `_Xbad_alloc` at 0x5ebd0. Its eleven instructions were already present in the original v4 database. Deriving all summaries again from that original database and unchanged base contracts produced 29 summaries; the previous 28 remain identical. This avoids treating a source's already-derived assumptions as new independent evidence. Ghidra agrees on all 265 instructions and their bounded control paths.

Recognizing full-register `xor reg,reg` and `sub reg,reg` establishes fifteen null `__cxa_throw` destructor arguments. Partial-register writes, different-source operations and non-nullable callbacks remain unresolved. Literal null is not requested as a code entry even where module RVA zero belongs to an executable mapping. General pointer relocation/provenance and values across branches or calls remain unvalidated.

| Evidence | Previous v7 | Current v9 |
| --- | ---: | ---: |
| Entries | 21,160 | 21,160 |
| Distinct instruction addresses | 873,582 | 873,581 |
| Fence findings | 9 | 8 |
| Unknown callback arguments | 170 | 155 |
| Exact constant callback records | 2,300 | 2,300 |
| Indirect call / jump records | 9,029 / 430 | 9,029 / 430 |

The only changed instruction set is libc entry 0x62c20: its backward jump at 0x62d40 becomes unreachable under the independently checked `_Xbad_alloc` control contract. The main entry 0x11e6220 loses its final-call fence finding. No entries were added or removed. All 18,444 ordered constructor records remain unchanged.

Ghidra independently checked all ten changed windows, including LSDA roots. All 1,131 shared instruction identities agree. Its 52 extra instructions follow ordinary fallthrough after the explicit nonreturn calls; every such path is retained and explained in the audit. All fifteen `xor edx,edx` definitions match Ghidra's bytes. This is static ABI provenance and decoding evidence, not callback or exception execution.

Thirty-three focused tests pass. The v8/v9 database, compilation manifest, frontier and constructor order repeat byte-for-byte. `reports/startup-v9-evidence.json` contains hashes, exact changes and run identities. One first audit failed because it used an incorrect literal contract ID; the ID assertion was corrected, and the failed run remains preserved.

Reproduce through `tools/run_record.py --id UNIQUE --` and fresh outputs:

1. `-m tools.cfg_boundary_inventory local/cfg/startup-recovery-v7-repeat local/cfg/NEW`
2. `-m tools.cfg_derive_control local/cfg/startup-recovery-v4 local/cfg/NEW --extra-entries local/cfg/boundary-inventory-v1/selection.json`
3. `-m tools.ghidra_recovery_check local/cfg/startup-recovery-v4 local/cfg/NEW --selection local/cfg/derived-bad-alloc-v1/selection.json`
4. `-m tools.check_derived_control local/cfg/startup-recovery-v4 local/cfg/derived-bad-alloc-v1/candidates.json local/cfg/ghidra-bad-alloc-v1 local/cfg/NEW`
5. `-m tools.cfg_recover_startup local/cfg/NEW --jump-evidence local/cfg/startup-table-bytes-v1/tables.json --control-evidence local/cfg/bad-alloc-control-checked-v1/contracts.json`
6. `-m tools.cfg_callback_zero_delta local/cfg/startup-recovery-v7-repeat local/cfg/startup-recovery-v9-repeat local/cfg/NEW`
7. `-m tools.ghidra_recovery_check local/cfg/startup-recovery-v9-repeat local/cfg/NEW --selection local/cfg/callback-zero-delta-v1/selection.json --exception-roots`
8. `-m tools.summarize_startup_v9`

The remaining eight fence cases are the prior libc abort/exit/throw chain, main thread-exit wrapper and two exit/longjmp wrappers listed in reports/startup-closure.md. Native service, callback, exception and restored-context behavior remains open. No new baseline run occurred.

The added RIP-relative RVA-zero negative check passes; local/cfg/startup-recovery-v10-zero-guard reproduces the v8/v9 database, manifest, frontier and constructor order byte-for-byte. Keep v9 as the current analysis path; v10 is the unchanged guarded-code repeat.
