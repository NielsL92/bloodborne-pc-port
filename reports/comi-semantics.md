# Scalar comparison state and fault correction

2026-09-06 20:00 UTC. COMI/UCOMI semantics now pass 851,968 authored hardware/AOT cases with zero differences, including 121,600 unmasked faults. Fourteen complete replacement objects repeat byte-for-byte. **P3 remains open; no game-derived object was linked or executed.**

The previous retained LLVM census exposed 49 error paths using the COMISS/COMISD implementation. The actual recovered instructions are 32 VUCOMISS and 17 VUCOMISD. Pinned Remill also routes ordered and unordered legacy/VEX forms through those same implementations, checks signaling-NaN status after host floating addition, and does not explicitly apply guest MXCSR masks, sticky flags or DAZ.

The independent test first reproduced 245,718 differing cases out of 851,968 with the prior semantic module. All 121,600 required unmasked faults were missed, flags differed in 131,508 cases, guest MXCSR in 121,567, and host MXCSR changed in 104,537. Counts overlap. The legacy __remill_error hook was never reached in this matrix: its presence in IR did not provide the required instruction-fault behavior.

## Contract and implementation

Intel specifies different invalid-operation rules for COMI and UCOMI, and requires arithmetic flags to remain unchanged when an unmasked exception occurs. Both instruction families can report denormal operands. The hardware checks use the recorded i7-13700K; they do not establish AMD Jaguar execution equivalence or PS4 exception delivery. [Intel Volume 2A, COMISD/COMISS](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf), [Intel Volume 2B, UCOMISD/UCOMISS](https://cdrdv2-public.intel.com/782151/253667-sdm-vol-2b.pdf).

`native/semantics/COMI.cpp.inc` replaces all sixteen scalar register/memory legacy/VEX selectors. It classifies raw NaNs and denormals, applies guest DAZ, orders finite bit patterns with signed-zero equality, updates guest MXCSR sticky state and tests its exception masks. An unmasked fault invokes the explicit native SIMD hook before writing arithmetic flags. Masked completion writes CF/PF/ZF and clears OF/SF/AF. Vector payloads and other State fields remain unchanged. No host floating arithmetic or comparison appears in the authored replacement IR.

`tools/comi_experiment.py` generates authored instructions and separate hardware wrappers. Its fixture checks 24 edge values pairwise plus random inputs, both precisions, all four invalid/denormal mask combinations, DAZ/FTZ, four rounding modes, pre-existing sticky flags, arithmetic-flag patterns and varied host MXCSR. A separate C++ reference uses floating comparison under a known host environment; it is checked against hardware results, flags, MXCSR and fault PCs. AOT checks compare full State, memory reads/preservation, logical return behavior and precise fault state. The escape bridge is an authored-test mechanism, not a general guest unwind implementation.

Both comi-checks-v2-integer and v3-repeat pass all 851,968 cases, with zero flag, MXCSR, host-state, fault, full-State or memory/exit differences. Input, audit, bitcode, object and execution log reproduce byte-for-byte. The prior counterexamples remain in comi-characterize-v1.

## Exact integration and continuation

Current active manifest: `local/compiler-spike/comi-integration-manifest-v1/active-objects.json`, SHA256 `82beba4877f4329768e812fee15a2ca6630283302e07fe06df0de9d5e474730d`. It contains 386 objects / 21,181 entries / 21,282 compiled roots and all 18,444 initial constructors exactly once. Canonical recovery remains startup-recovery-v31-conditional-repeat; no decoded instruction, root or unknown-target obligation changed.

The 49 sites occur in fourteen objects containing 753 entries / 41,047 instructions. Recompilation preserves each complete sparse input, root set and the same 170 missing-start records. The new objects total 3,118,244 bytes and repeat exactly between comi-replacement-compile-v1 and v2-repeat. The fourteen old files remain preserved but are excluded from the new manifest. The other 372 objects retain their recorded compiler/semantic identities.

Replacement compilation uses build/sparse-lift-v8-selector-audit and build/extended-semantics-v34-comi-inline, semantic SHA256 `3db92d94604935e7149bb45d3581b94eddcaf03b56797576d85f34a85f698a12`. Every previous extension has its unchanged source hash; only the comparison extension is added. Original Remill inputs and game files remain untouched.

The refreshed LLVM census in control-exit-inventory-v6-comi-repeat reproduces v5-comi exactly: 4,818 missing-block calls remain; semantic error calls fall from 105 to 56 division sites, and explicit SIMD fault calls rise from 9 to 58. Other inventoried control counts are unchanged. Whole-program-linkage-v7-comi-repeat reproduces v6-comi: 177 verified import stubs, 63 support/library bindings, no unclassified direct targets and the same 4,366 missing-start records. Raw COFF plus LLVM readobj recheck the 35 duplicate constants / 90 definitions / 12 objects in coff-constants-v2-comi.

Every experiment uses tools/run_record.py. The final audit is comi-evidence-audit-v1; reports/comi-semantics-evidence.json verifies source snapshots and the repeated artifacts. Preserve the failed v32 semantic invocation (missing module import context) and v33 compile (attribute placement); v34 fixes the invocation and declaration, with diagnostics retained.

Next investigate the 56 remaining division error sites and precise fault attribution, then preserve source/exit intent at native boundaries and validate native support/import handling and linkage. Unknown targets still fail explicitly; no interpreter, JIT, emulator or original CPU fallback is introduced. P1 observations are unchanged.
