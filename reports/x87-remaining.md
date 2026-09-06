# P3 remaining x87 sites and MMX boundary

Current 2026-09-06 16:48 UTC: inventory v3-integrated preserves all 355 instruction records and reports zero remaining arithmetic encodings and zero MMX sites. Recognition of the new arithmetic families is restricted to their checked register/FSCALE byte patterns. Exact 360-site x87/MXCSR selector validation and complete-object replacement are recorded in `reports/x87-integration.md`. P3 remains open with eight control-boundary quarantines; the earlier nine-site inventory below is retained as historical evidence.

Updated 2026-09-06 15:23 UTC. The canonical startup graph contains 355 x87-related instructions and no MMX register operands, EMMS or FEMMS. Nine arithmetic/scale sites still need experimental semantic work; they belong to five libc entries. This is a static inventory, not execution coverage or an absence claim about unknown targets and later gameplay.

| Site | Exact bytes | Operation | Owner |
| --- | --- | --- | --- |
| 0x1b91c | DE E9 | FSUBP ST(1) | 0x1b6f0 |
| 0x2c2df | DE E1 | FSUBRP ST(1) | 0x2c230 |
| 0x2c577 | DE C2 | FADDP ST(2) | 0x2c300 |
| 0x2c63a | DE E1 | FSUBRP ST(1) | 0x2c300 |
| 0x2c714 | D8 E1 | FSUB ST(1) | 0x2c300 |
| 0x2c7fa | D8 C9 | FMUL ST(1) | 0x2c7c0 |
| 0x2c8f0 | D8 CA | FMUL ST(2) | 0x2c7c0 |
| 0x2c996 | DE E9 | FSUBP ST(1) | 0x2c7c0 |
| 0x413f2 | D9 FD | FSCALE | 0x413e0 |

All sites use supplied libc SHA256 `4378b47f46f1d856824a6f971db1a0c3f41833b77f49d2fba9538f667a139166`. The initial classification omitted Capstone's `fucompi` spelling and listed 20 remaining sites. All eleven alias sites have exact DF E8..EF bytes and map to the already characterized FUCOMIP selector. The corrected inventory preserves identical instruction fields and database/manifest hashes and reports nine. Audit v1 compared the entire annotated JSON and failed because only selected rows carry ownership annotations; audit v2 compares instruction fields independently of those annotations. The failed audit is retained.

Experimental compiler v7 rejects decoded MM0..MM7 register operands and EMMS/FEMMS before lifting. Remill's separate MMX storage is not coherent with canonical raw x87 storage yet. This explicit rejection allows work to focus on present arithmetic sites while ensuring a later discovered MMX path cannot silently use unvalidated shared-state semantics. There is no opt-in bypass.

Twelve authored MMX cases reject with that exact reason, including register/memory transfers, arithmetic, SSE/MMX conversion and state-clear instructions. Three ordinary SSE/x87/image controls compile. Ten sparse-input checks and 8,192 authored execution cases pass; all 112 exact x87 opcode/prefix checks pass. No game code was executed or newly accepted.

Current inventory is `local/compiler-spike/x87-remaining-inventory-v2-alias`; exact inputs, ownership, hashes and checks are in `reports/x87-remaining-evidence.json`. Use `tools.x87_remaining_inventory OUT`, `tools.sparse_mmx_checks OUT DRIVER SEMANTICS` and `tools.summarize_x87_remaining OUT` through `tools/run_record.py` with fresh outputs.

Next investigate native arithmetic precision, denormal/noncanonical handling, NaN propagation, C1 and unmasked wrapped results, then FSCALE. Native import/callback/exception/control gates remain open. Accepted startup stays compiler v5 / semantics v9-sqrt, with 21,168 compiled entries, two rejections and eight quarantines. No native game boot or playable port exists.
