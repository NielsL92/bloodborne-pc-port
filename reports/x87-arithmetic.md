# Experimental native x87 register arithmetic

2026-09-06 16:02 UTC. The five recovered register-arithmetic families pass authored numeric and AOT checks in experimental semantics **v30-arithmetic**, with compiler **v7-mmx-guard**. P3 remains open. No game-derived object was linked, executed or newly accepted; accepted startup remains compiler v5 / semantics v9-sqrt.

## Result and scope

`X87_ARITHMETIC.cpp.inc` supplies FADDP, FSUBP, FSUBRP, FSUB ST0/ST(i), and FMUL ST0/ST(i). These families account for eight recovered sites in four libc entries. The remaining ninth arithmetic site is FSCALE at libc **0x413f2**, owned by **0x413e0**. The exact prior inventory stays preserved in `local/compiler-spike/x87-remaining-inventory-v2-alias/remaining-arithmetic.json`; the new evidence carries the eight checked sites and separate FSCALE remainder. MMX remains absent from the current graph and compiler v7 rejects MMX/EMMS/FEMMS explicitly if new recovery encounters it.

The ordinary native helpers in `x87_numeric.cpp` operate on raw significand/exponent pairs and return result bits, exception flags and C1 rounding direction. They scope all four SoftFloat thread-local controls. Valid precision controls select 24, 53 or 64 significant bits, with all four rounding modes. Unsupported encodings, pseudodenormals, denormal operands, NaN payloads and invalid-operation priority are handled explicitly. The existing SoftFloat source/library is unmodified; there is no guest instruction fetch/decode or CPU fallback in these helpers.

Reserved precision-control value 1 returns an explicit unsupported status. The instruction checks pending exceptions first and reaches `__bb_native_x87_unsupported` before changing arithmetic state. Independent local hardware produced the same result for PC=1 and PC=3 in 122,880 paired observations, but that does not establish an AMD Jaguar contract. The numeric helper also retains internal unsupported results if a supposedly representable wrapped exponent or the recentered computation violates its checked bounds; none occur in the passing valid-control matrices.

## Exception completion and the retained failure

Unmasked invalid or denormal-operand exceptions suppress result writes and popping. Unmasked arithmetic overflow, underflow and precision complete the result and optional pop, then remain pending until a waiting instruction. Overflow and underflow can coexist with precision. This differs from the independently checked memory-store completion rules. Empty-stack handling, TOP/physical occupancy, deferred faults and metadata all use canonical guest State.

The Intel architecture manual describes adjusting unmasked stack-result exponents by 24,576 and rounding according to the applicable precision and rounding controls. Its FSCALE discussion separately calls out results that remain outside the range after this adjustment. These descriptions inform the experiments; local Intel observations do not establish AMD equivalence. [Intel SDM, sections 8.5.4–8.5.6](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366521.pdf)

Numeric v1 had **576 differences**. Scaling both add/sub operands directly by -24,576 made a much smaller operand unrepresentable. The replacement normalizes the finite significands and recenters the operation in the middle exponent range before rounding, then restores the wrapped result exponent. For addition/subtraction, a nonzero operand more than 256 bits below the larger operand retains its sign and a sticky tail: such a gap cannot cancel two leading bits and precision is at most 64 bits. Multiplication recenters both normalized operands and restores the sum of their exponent shifts. The failed run remains intact, including its source snapshot and diagnostics.

## Evidence

| Experiment | Checks | Differences |
|---|---:|---:|
| Independent hardware arithmetic probe | 491,520 | Characterization only |
| Numeric v1 | 491,520 | 576 |
| Numeric v2, corrected exponent path | 491,520 | 0 |
| Numeric v3, arbitrary raw and finite pairs | 5,529,600 | 0 |
| Numeric v4, extra NaNs and dense rounding edges | 8,271,360 | 0 |
| AOT bindings v2 and fresh v3 repeat, each | 7,790,592 | 0 |
| Store regression v7 | 7,120,572 | 0 |
| Load regression v9 | 2,138,172 | 0 |

The final numeric count comprises **8,117,760 hardware comparisons** and **153,600 reserved-control rejections**. The AOT count comprises **5,603,328 hardware comparisons**, **583,680 pending-before-reserved checks**, **817,152 reserved-control rejections**, and **786,432 concurrent load/store/arithmetic scope checks**. These categories must not all be presented as hardware execution comparisons. There are **845,672 matched hardware pending faults**. The extra native pending faults belong to the explicit reserved-control boundary tests.

The AOT matrix covers all eight register indices for each family, 15 waiting suffixes and two mixed arithmetic sequences; all TOP/occupancy patterns; masks and sticky flags; raw/special inputs; targeted finite operands and precision/rounding settings. It compares full State and untouched memory, integer flags, defined x87 status, runtime record/return counts, fault class/PC/mask and host floating-point isolation. Undefined C0/C2/C3 are excluded. Both pointer/opcode profiles remain explicit; hardware pointer comparison is limited to the low 32 bits while native logical pointers and metadata are checked in full.

`function.bc`, `function.obj`, `numeric.obj`, and `execute.stdout` are byte-identical between the two final AOT runs. `tools/summarize_x87_arithmetic.py` verifies results, module/header/source identities, all run source archives, the independent pop/exception observations, reserved-control hardware pairs, reproducibility and exact remaining FSCALE site. Run **20260906-p3-x87-arithmetic-evidence-audit-v1** passes. Machine-readable detail: `reports/x87-arithmetic-evidence.json`.

## Reproduction and continuation

Use fresh output directories and wrap every command with `tools/run_record.py --id UNIQUE --`:

- `.venv/Scripts/python.exe -m tools.x87_arithmetic_probe local/compiler-spike/NEW`
- `.venv/Scripts/python.exe -m tools.x87_arithmetic_numeric_probe local/compiler-spike/NEW build/softfloat-v2-repeat/softfloat.lib`
- `.venv/Scripts/python.exe -m tools.x87_arithmetic_experiment local/compiler-spike/NEW build/sparse-lift-v7-mmx-guard/bb-sparse-lift.exe build/extended-semantics-v30-arithmetic build/softfloat-v2-repeat/softfloat.lib`
- `.venv/Scripts/python.exe -m tools.summarize_x87_arithmetic local/compiler-spike/NEW`

The audit pins this source state; historical source ZIPs remain the authority after subsequent edits. Next investigate FSCALE's scale truncation, noncanonical/denormal/NaN behavior, precision-control independence, C1, and masked/unmasked extreme exponent results. Then assess coherent module integration and the two x87-rejected bodies without confusing compilation with execution. Native import/callback/exception/control closure remains open. P1 Hunter's Dream route, overhead/cost profiling and intermittent audio mutex crash work are unchanged. No user action is required.
