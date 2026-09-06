# Experimental native FSCALE

2026-09-06 16:20 UTC. Experimental semantics **v31-scale** / compiler **v7-mmx-guard** pass FSCALE numeric, AOT and independent hardware checks. The recovered site is libc **0x413f2**, owned by **0x413e0**. This completes bounded family checks for the nine arithmetic sites in the current recovered graph. Exact selector/module integration remains next; accepted startup stays v5 / v9-sqrt. No game-derived object was linked, executed or newly accepted. P3 remains open.

## Numeric behavior

`__bb_x87_scale` operates on raw significands/exponents using integer exponent adjustment and rounding. It uses scoped SoftFloat only for NaN propagation, restores all four library controls and leaves host floating-point state unchanged. All four PC encodings are supported because FSCALE does not use precision control. The scale is truncated toward zero. Finite scale magnitudes at least 131,072 can be bounded to that magnitude because all finite input exponents remain beyond the adjusted result range; sign and exception outcomes are retained.

Unsupported raw encodings take invalid-operation priority; NaNs, pseudodenormals, denormal operands, zero and infinity are explicit cases. Normal results retain the full 64-bit significand. Masked subnormal results round according to RC. Unmasked overflow/underflow adjusts the exponent by 24,576. If that still leaves an exponent outside the normal range, the result becomes signed infinity/zero with precision set, even when the ordinary directed-rounding saturation result would differ. Unmasked invalid/denormal exceptions suppress the register write; other arithmetic exceptions complete it and remain pending until a waiting instruction.

The instruction reference defines truncation, operand-class results and C1 rounding behavior. The general x87 exception description separately covers massive FSCALE overflow/underflow after exponent adjustment. [Intel FSCALE reference](https://cdrdv2-public.intel.com/812383/253666-sdm-vol-2a.pdf), [Intel exception description, sections 8.5.4–8.5.6](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366521.pdf)

## Retained findings

Numeric v1 had **256 differences**: an exactly zero scale preserves a denormal destination without raising a new underflow exception. A nonzero fractional scale which truncates to zero still enters exponent/underflow handling and can produce a wrapped result when UE is unmasked. The corrected path handles exact zero separately, after operand classification and denormal-operand priority. Both independent setup paths reproduce this distinction; no AMD Jaguar equivalence is claimed.

The second hardware probe initializes operands through FNINIT / FLD80 / FLDENV, starting at TOP=6 with physical tags 0xc0. The first uses FXRSTOR, starting TOP=0 with tags 3. All **761,856** logical operand and defined status observations agree after explicitly accounting for initial TOP; both paths retain their initial physical occupancy. The inherited v2 summary incorrectly labeled any nonzero TOP as a pop. The raw evidence is intact, the separate comparison checks the actual TOP values, and v3 corrects that metric to `top_changed` while reproducing every raw output row. This reporting correction is preserved alongside the earlier output.

## Validation

| Experiment | Checks | Differences |
|---|---:|---:|
| Independent FXRSTOR setup | 761,856 | Characterization only |
| Independent FLD80/FLDENV setup | 761,856 | 0 against normalized first setup |
| PC independence pairs | 571,392 | 0 |
| Numeric v1 | 761,856 | 256 |
| Numeric v2, exact-zero correction | 761,856 | 0 |
| Numeric v3, dense integer-scale boundaries and raw/finite inputs | 2,021,632 | 0 |
| AOT v1 and fresh v2 repeat, each | 2,809,856 | 0 |
| Arithmetic regression v4 | 8,052,736 | 0 |

The final FSCALE AOT count comprises **1,761,280 hardware comparisons** and **1,048,576 concurrent load/store/arithmetic/scale scope checks**. All **349,046** pending hardware faults match; FSCALE has no reserved-PC rejection. Cases cover occupancy/TOP, raw classes, integer and fractional scale boundaries, all controls/masks, sticky flags, metadata and five sequences: scale alone, waiting suffix, sign change, exchange/rescale, and register store/pop. Undefined C0/C2/C3 are excluded. Full raw stack/GPR state, unchanged memory, defined flags, fault PC/mask, runtime record counts and host isolation are checked. Pointer/opcode profiles remain explicit; hardware pointer comparison retains the established low-32-bit limit while native logical pointers are fully checked.

Final `function.bc`, `function.obj`, `numeric.obj` and `execute.stdout` repeat byte-for-byte. `tools/summarize_x87_scale.py` verifies source archives, numeric/module identities, retained failures, independent setup/PC comparisons and reproducibility. Run **20260906-p3-x87-scale-evidence-audit-v1** passes. Full evidence: `reports/x87-scale-evidence.json`.

## Reproduction and next work

Wrap each command with `tools/run_record.py --id UNIQUE --` and use a fresh output directory:

- `.venv/Scripts/python.exe -m tools.x87_scale_probe local/compiler-spike/NEW` (add `--load-input` for the second setup).
- `.venv/Scripts/python.exe -m tools.x87_scale_numeric_probe local/compiler-spike/NEW build/softfloat-v2-repeat/softfloat.lib`.
- `.venv/Scripts/python.exe -m tools.x87_scale_experiment local/compiler-spike/NEW build/sparse-lift-v7-mmx-guard/bb-sparse-lift.exe build/extended-semantics-v31-scale build/softfloat-v2-repeat/softfloat.lib`.
- `.venv/Scripts/python.exe -m tools.summarize_x87_scale local/compiler-spike/NEW`.

The audit pins this source state; use preserved source snapshots after later changes. Next audit exact recovered selectors and fresh static compilation for the remaining libc 0x30430 / 0x53cd0 bodies, keeping experimental artifacts separate. Native import/callback/exception/control closure, general Windows unwind and PS4 fault delivery remain open. MMX is absent from the present graph and compiler v7 rejects it. No interpreter/JIT/original-game CPU fallback was introduced. P1 route/profiling/audio work remains unchanged; no user action is required.
