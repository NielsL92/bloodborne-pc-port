# Integer division fault correction

2026-09-06 20:26 UTC. DIV/IDIV now pass 327,680 authored Python-oracle/hardware/AOT cases with zero differences, including 218,424 fault cases. Thirteen replacement objects repeat byte-for-byte. **P3 remains open; no game-derived object was linked or executed.**

The prior LLVM census contained 56 division error paths from 28 recovered instructions: 18 DIV and 10 IDIV, using 32/64-bit register and memory operands. Pinned BINARY.cpp advanced REG_PC to the next instruction before checking zero/overflow and performed signed double-width division before its quotient-range check.

Independent characterization confirms both problems. All 218,424 fault cases had the wrong logical PC. In addition, IDIV32 with EDX:EAX = 0x80000000:00000000 and divisor 0xffffffff raised host integer-overflow exceptions inside AOT code: forms 24 and 27, trial 159, register and memory variants. Their mathematical quotient does not fit EAX. The host exception comes from the wider signed operation used to calculate that quotient. The remaining 218,422 failures reached generic __remill_error. Successful result registers agreed; aggregate fault decisions agreed, but neither observation established a precise native fault contract.

The first run, divide-characterize-v1, terminated with 0xc0000095. V2 confines unexpected arithmetic exceptions to a handler inside the authored subprocess, and V3 records the two exact input cases. This bridge records a test failure; it is not a guest exception-delivery or production unwind implementation. All failed and diagnostic artifacts remain preserved.

## Implementation and independent checks

Intel specifies divide faults for zero divisors and out-of-range quotients. Signed division truncates toward zero; success arithmetic flags are undefined and are excluded from comparison. [Intel Volume 2A, DIV/IDIV](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf).

`native/semantics/DIVIDE.cpp.inc` replaces all twenty selector names for signed/unsigned 8/16/32/64-bit division. It reads operands before writes, handles signed inputs as unsigned magnitudes, checks the signed or unsigned quotient range, then commits quotient/remainder and the next PC. Zero/overflow invokes __bb_native_divide_fault with an explicit reason and width while preserving the faulting PC and destination state. Unsigned arithmetic avoids signed minimum/-1 overflow; no LLVM sdiv or generic __remill_error remains in the authored replacement IR.

`tools/divide_experiment.py` produces 32 authored forms: signed/unsigned, four widths, memory, independent register and quotient/remainder-register aliases. Python arbitrary-precision arithmetic generates 327,680 expected cases from edge triples, random operands and constructed dividends. Hardware separately verifies results or precise faults before AOT is compared. Tests cover complete State, memory bounds/preservation and return behavior, fault PC/flags, explicit reason/width and unchanged host MXCSR. Undefined success arithmetic flags are excluded. Host observations use the recorded Intel CPU; no AMD Jaguar or PS4 fault-delivery claim is made.

Both divide-checks-v4-unsigned and v5-repeat pass with zero differences, zero generic error calls and zero AOT host exceptions. All 218,424 expected faults reach the explicit native hook with correct State/PC/reason. Oracle files, input, audit, bitcode, object and execution logs reproduce exactly. The independent COMI regression also passes 851,968 cases; its bitcode, object and execution log are unchanged.

The existing LLVM runtime provides the authored fixture's 128-bit arithmetic helpers. Its clang_rt.builtins-x86_64.lib SHA256 is `9cff03d2c5218693b1f91efc0074957c710eeddd932d57a681c8f558b81fbe8e`; no new download or installation was needed. Helper availability in the fixture is not a production runtime link.

## Integration and continuation

Current active manifest: `local/compiler-spike/divide-integration-manifest-v1/active-objects.json`, SHA256 `36683365f7bf8b4ec59043f05587a8d418aa38a9827e829f99b8c53fe1b084c0`. It retains 386 objects / 21,181 entries / 21,282 unique compiled roots and all 18,444 initial constructors. Canonical recovery remains startup-recovery-v31-conditional-repeat with every previous uncertainty and conditional boundary.

Thirteen objects containing 632 entries / 695 roots / 38,394 instructions are replaced as complete objects. Their exact inputs, roots and 204 missing-start records are preserved. New objects total 3,533,901 bytes and reproduce between divide-replacement-compile-v1 and v2-repeat. The previous files remain intact; the other 373 objects retain their identities.

New compilation uses build/sparse-lift-v8-selector-audit and build/extended-semantics-v35-divide, semantic SHA256 `9fb5e55e7d5dde0482182afda9e3160f3d33298f3b724c1d21111df26446a8fa`. Previous extensions, original Remill files and game inputs remain unchanged.

The complete LLVM census control-exit-inventory-v8-divide-repeat reproduces v7-divide: **zero __remill_error calls, 56 explicit divide-fault calls, 58 SIMD fault calls and 4,818 missing-block calls**. Other control counts are unchanged. Whole-program-linkage-v9-divide-repeat reproduces v8-divide: 239 unresolved names, comprising 177 verified import stubs and 62 support/library bindings. __remill_error and __divti3 are removed from the support list; __bb_native_divide_fault is added. The same 35 duplicate constants / 90 definitions / 12 objects pass raw COFF and LLVM readobj checks in coff-constants-v3-divide.

Every experiment uses tools/run_record.py; divide-evidence-audit-v1 verifies source snapshots and all repeated evidence. Next preserve source/exit intent for dynamic return guards and missing blocks, establish compatible native handling and bind/link the full object set before deciding P3. Target availability alone must not authorize dispatch. P1 baseline observations remain unchanged.
