# Static x87 integration and object ownership

2026-09-06 16:44 UTC. The static compilation census is now **21,170 entries / 380 objects**, including all **18,444 initial constructors**. Both remaining compiler rejections, libc **0x30430** and **0x53cd0**, compile. **Eight control-boundary quarantines remain. P3 has not passed. No game-derived object was linked or executed.**

## Exact selector and integration evidence

Compiler v8 adds observational audit rows containing each decoded selector and its selected LLVM implementation. Its exact-byte/MMX/trap checks retain their behavior; the authored scale fixture's bitcode, function/helper objects and results are byte-identical to compiler v7. No original Remill library, executable or semantic source was modified.

An isolated static catalog checks all **355 recovered x87 instructions and five MXCSR instructions**, covering **31 selectors in 12 libc owners**. Every selector resolves to its checked authored implementation. The catalog preserves the original instruction bytes at separate logical PCs and adds an authored RET; it proves selection, not original function execution. The subsequent complete-body builds check the original manifest PCs and bytes. Neither the catalog nor the new complete object contains legacy `__remill_fpu_` helpers or `x86_fp80` IR.

All 12 affected bodies compile independently into 12 reproducible diagnostic objects: **1,820 instructions / 752,278 object bytes**. Their six missing paths are fallthrough addresses after the existing stack-protector failure import. These diagnostic objects are not included in the active object set.

## Whole-object replacement

The prior 384-object set contains 21,168 unique entries. Every compiled instruction-set hash matches the canonical current manifest, with no stale sets or duplicate compiled logical roots. Five prior objects contain ten of the affected bodies, together with other entries that must be retained:

| Prior startup-batch-all-v1 object | Entries |
|---|---:|
| batch-0004-b-a | 22 |
| batch-0004-b-b-b | 12 |
| batch-0005-b-b | 7 |
| batch-0006-a | 21 |
| batch-0006-b-a-b-a-b-a | 1 |

The replacement group therefore contains all **63 prior entries plus two formerly rejected entries**. It produces one **981,385-byte object from 4,766 instructions and 65 roots**, using compiler **v8-selector-audit** and semantics **v31-scale**. Two fresh builds reproduce input, root/unit manifests, selector audit, bitcode and object bytes exactly. Old files remain untouched. Retained objects keep their own recorded compiler and semantic identities; they are not relabeled as v31.

Use **`local/compiler-spike/x87-integration-evidence-audit-v2-path/active-objects.json`** as the current complete static object manifest. SHA256: **495bb7a294e038b4888afa1955913951c11e89fe245070f1ce1564c606ed4577**. It contains 379 retained objects and the one replacement object. Do not append the replacement to the old full set, or include the 12 diagnostic objects. The combined audit checks that every issue-free current manifest has exactly one entry owner and every compiled logical root has exactly one object owner.

## Remaining boundaries and limits

The replacement object retains **17 missing-path records**: 16 unexpected returns after `__stack_chk_fail`, and the existing libc import endpoint at **0x300**, NID **VADc3MNQ3cM**, whose name/contract is unresolved here. It also declares 89 native runtime or compiled-target dependencies. These are explicit integration obligations. No universal-success stub, original-byte execution or interpreter/JIT fallback was introduced.

The eight quarantined entries remain libc **0x1f560, 0x5ff10, 0x60510, 0x60560, 0x606f0** and main **0x207f990, 0x210b0e0, 0x210b940**. Their fallthrough-at-fence evidence must be resolved with control/cleanup/termination contracts or further justified recovery, not by dropping the findings. Unknown indirect/callback targets, mutable constructor tables and native exception/service boundaries remain unchanged. The canonical database still has 21,178 entries / 874,266 instruction addresses across eight modules; its database/manifest identities are unchanged.

The x87 numeric, metadata, image and comparison policy limits remain those in the arithmetic/scale/load/store/image reports. Intel-host agreement is not AMD Jaguar execution evidence. MMX remains absent from the recovered graph and compiler v8 retains the explicit rejection. General Windows unwind, PS4 fault delivery and native startup services are still incomplete. Object compilation does not establish native game boot, gameplay, performance or execution coverage. P1 route/profiling/audio work is unchanged.

## Checks and reproduction

The compiler checks pass ten sparse-input cases and 8,192 authored AOT cases; twelve MMX rejections and three positive controls; 112 exact opcode/prefix checks; and six native-trap input checks with normal/fault execution. The v8 scale regression passes 2,809,856 authored AOT/scope checks with the same outputs as v7. The evidence audit verifies every run's source archive, exact selector mapping, complete-object repeats, old/new ownership, all current instruction-set hashes and the remaining quarantine list.

Audit v1 completed its checks but failed while constructing a report reference from a relative output path. Audit v2 resolves that path first and passes. The failed run and its partial outputs are retained. Full result: `reports/x87-integration-evidence.json`.

Wrap commands in `tools/run_record.py --id UNIQUE --` and use fresh output directories:

- `-m tools.x87_selector_inventory OUT build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe build/extended-semantics-v31-scale`.
- `-m tools.x87_replacement_plan OUT` recreates this historical replacement plan from its pinned prior object set.
- `-m tools.startup_batch_compile local/cfg/startup-recovery-v22-cache-repeat OUT build/sparse-lift-v8-selector-audit/bb-sparse-lift.exe --entries local/compiler-spike/x87-replacement-plan-v1/entries.json --semantics build/extended-semantics-v31-scale --explicit-ud2`.
- `-m tools.summarize_x87_integration OUT` audits this checkpoint; later changes must retain its source snapshot or explicitly update its inputs.

Next inspect the eight remaining control-boundary quarantines and their independent Ghidra/native-contract evidence. Continue from the active object manifest above, preserving uncertainty and all existing runs. No user action is required.
