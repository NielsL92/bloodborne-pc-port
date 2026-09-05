# Packed integer and vector transfer compilation

Updated 2026-09-05 23:46 UTC. The combined startup census now compiles **21,145 entries**, including all **18,444 initial constructors**. Seven dependency entries reject and eight uncertain boundary manifests remain quarantined. No game-derived object was linked or executed; P3 remains open.

`build/extended-semantics-v6-transfer/amd64_avx.bc` adds authored packed shifts, unpacking, signed minimum/maximum, products, byte shuffles, immediate lane selection/blends, extract/insert operations, GPR sign masks and exact unaligned-load selectors. It reuses the two existing wide register multiply selectors and existing unaligned-load helper. Original Remill sources, old semantic modules and lifters remain unchanged.

The original 372 successful objects combine with eleven new objects containing forty-one of the original forty-eight rejected entries. These eleven supersede the earlier eight vector objects; they are not additive to that batch. New object bytes total 1,022,023. Fresh repeat output is byte-identical, actual COFF symbols agree with audited roots, and no duplicate logical roots exist across the combined objects. Sixteen explicit UD2 sites and fifteen missing-path records remain visible in the new batch.

## Checks

All checks execute authored AOT and authored hardware instructions, with independent portable references and guarded memory. Every check below also passes with the final combined semantic module:

| Contract | Authored cases |
| --- | ---: |
| Eight packed arithmetic/unpack/byte-shuffle operations; 64 forms | 262,144 |
| Seven immediate-controlled shift/alignment/shuffle/blend operations; all 256 controls across 46 forms | 376,832 |
| Seven extract/insert/mask/load/unpack operations; 2,318 instruction roots | 593,408 |
| Prior shuffle / variable blend / reciprocal-square-root / BMI contracts | 32,768 / 122,880 / 399,360 / 34,816 |

Tests check complete State, preserved flags/vectors, VEX upper clearing, register aliases, signed boundaries/product overflow, large shift counts, independent 128-bit lanes, distinct memory contents, scalar insertion read size and unaligned vector reads. Mask tests cover every sign combination and clear the GPR's upper 32 bits. These are bounded instruction contracts, not whole-game execution coverage or general memory-fault support. Reciprocal-square-root Jaguar bit-exactness remains unverified.

The v4 semantic build rejected duplicate existing YMM multiply definitions; v5 adds only missing selectors. Transfer fixture v1 failed linking because its reused 128-bit unpack helper needed a guarded floating-bit reader; v2 supplies that reader and passes. Both failed runs remain intact.

## Remaining evidence

`reports/packed-semantics-evidence.json` checks every instruction selector in the seven rejected bodies against the final bitcode's actual selector symbols. Missing forms are FNSTENV, FLDENV, FXSAVE, VROUNDSD, VMINPS, VMAXPS and VSQRTPS (eight exact selectors). The exact module/entry/site records are retained; first-failure diagnostics alone would miss FLDENV and VSQRTPS. Instruction identities still agree with the earlier all-forty-eight Ghidra comparison.

Primary instruction definitions are in [Intel's instruction manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf), including shift saturation, signed ordering and per-lane alignment. The next investigation must establish guest/host MXCSR, unmasked exceptions and x87 environment layout behavior before accepting those state-sensitive forms. Eight uncertain control boundaries, callback provenance, indirect targets and native runtime closure also remain open.

Reproduction: use fresh paths and `tools/run_record.py`. Build the semantic module with BMI, SHUFFLE, BLEND, RSQRT, PACKED and TRANSFER extensions in that order. `tools.vector_semantics_checks` accepts packed/select/transfer families. `tools.startup_batch_compile` uses v9 recovery, the original rejected-entry selection, driver v5, the explicit semantics path and `--explicit-ud2`. Recorded runs are `startup-transfer-recompile-v1` and `v2-repeat`; their failed exit status reflects the seven retained rejections. Run `tools.summarize_packed_semantics NEW`, then `tools.summarize_startup_recovery` and `tools.summarize_cfg` for integrated audits.
