# P3 scoped native x87 loads and opcode correction

Updated 2026-09-06 14:40 UTC. Experimental semantics v24-loads and compiler v6-x87-opcode pass 1,613,884 checks: 1,351,740 authored AOT/hardware instruction cases plus 262,144 concurrent helper-scope checks. P3 remains open. Accepted startup compilation remains 21,168 entries using v5 / v9-sqrt, with two rejections and eight quarantines. No native game boot or playable port exists.

## Instruction and numerical boundary

`X87_LOAD.cpp.inc` replaces FLD m32/m64 and FILD m16/m32/m64. A waiting pending exception precedes the bounded source-memory check. Stack overflow takes priority over conversion. Masked overflow pushes the indefinite value; unmasked overflow suppresses the push. Signaling NaN conversion raises invalid, and an unmasked invalid also suppresses the push. Source denormals raise DE but still push their exact widened value when DE is unmasked. The instruction updates explicit pointer/opcode metadata after determining the new exception. The Intel FLD description specifies that denormal loads still push. [Intel instruction reference](https://cdrdv2-public.intel.com/812383/253666-sdm-vol-2a.pdf).

Three ordinary native C++ entrypoints call the pinned SoftFloat library for exact widening. They accept raw integers and return significand, sign/exponent and flags through an explicitly checked 16-byte ABI. A per-call scope saves/restores library rounding, tininess, precision and exception flags. Four concurrent threads check restoration and independently fixed exact outputs for single/double signaling NaNs, minimum subnormals and signed 64-bit limits. Loads ignore precision control because widening is exact. This does not generalize the current scope to arithmetic with reduced precision or unmasked wrapped results.

The instruction fixture tests all TOP values and occupancy patterns, masks/stickies, special payloads, integer limits, 4,096 deterministic random payloads per form/profile, two explicit metadata policies, waiting suffixes and compound load/raw80-store sequences. Complete native State, defined flags/status, raw stack payloads, memory bytes, return/fault PC, service counts and host FP isolation are checked. Undefined C0/C2/C3 are excluded. There are 238,606 matched hardware faults, 30 separate unsupported-memory cases and 30 extra pending-before-unsupported cases. Canonical full logical pointers remain checked; the earlier host low-32 pointer comparison limit remains explicit.

## Concrete decoder defect

Both initial runs stop at FLD m64's metadata guard after load32 passed 90,116 cases. Observed guest FOP was `0x107`, expected `0x507` from exact `DD 07` bytes. Pinned `external/remill/lib/Arch/X86/Arch.cpp` documents an eleven-bit opcode but implements `bytes[0] & 3`, dropping bit 10.

The separately compiled v6 sparse adapter validates the trailing implicit PC/FOP operand pair and exact prefixed escape/ModRM bytes before semantic lifting. It corrects the immediate using all three escape bits and records original/corrected values in the audit. Unexpected decoder values reject. Original Remill source, libraries and v5 executable remain unchanged. Independent Capstone checks cover 112 authored forms across all eight escape bytes and seven prefix combinations; 56 require correction. These are static checks, not execution coverage. Existing startup objects have not been regenerated or relabeled as corrected.

Raw regression passes 688,144 cases, stack regression 1,499,136 and deferred-fault regression 720,896. Sparse input checks pass ten cases and 8,192 authored executions; six explicit trap checks also pass.

## Reproducibility and continuation

All outputs and failures are preserved. The v3/v4 repeat matched lifted bitcode, function object and raw results. The helper object differed only in the COFF timestamp. Applying the existing deterministic emission flag to that C++ object yields byte-identical v5/v6 function bitcode, function object, native helper object and results without normalization. The library is unchanged from `build/softfloat-v2-repeat/softfloat.lib`.

Use fresh paths and `tools/run_record.py`. Current commands are `tools.x87_load_experiment OUT build/sparse-lift-v6-x87-opcode/bb-sparse-lift.exe build/extended-semantics-v24-loads build/softfloat-v2-repeat/softfloat.lib`, `tools.x87_opcode_checks OUT DRIVER SEMANTICS`, and `tools.summarize_x87_loads OUT`. Exact argv, source archives, identities and results are in `reports/x87-loads-evidence.json` and retained run manifests.

Next integrate the same metadata policy across older x87 producers and FNINIT segment reset, then numeric stores/arithmetic and MMX coherence. Native control/import/callback/exception closure remains required. No new P1 baseline run occurred; Hunter's Dream, profiler overhead/costs and the intermittent opening audio mutex crash remain independent work.
