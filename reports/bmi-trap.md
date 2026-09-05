# BMI semantics and explicit native UD2 boundaries

Updated 2026-09-05 23:04 UTC. Fourteen of the original 48 compiler-rejected startup entries now compile. P3 remains open: 34 compiler rejections, eight disputed manifests and native control/runtime closure remain. No game-derived object was linked or executed.

`native/semantics/BMI.cpp.inc` adds BLSR/BLSI register and memory forms at 32 and 64 bits. `tools/build_extended_semantics.py` builds a fresh semantic module from the existing pinned recipe and unchanged original sources/bitcode components. The previous semantics remain preserved. The extension follows the operation and flags sections of the instruction specification. The BLSI descriptive paragraph conflicts with its operation/flags text at zero; the implemented carry behavior matches those explicit sections and the authored hardware checks. [Intel BLSI/BLSR specification](https://cdrdv2-public.intel.com/774492/325383-sdm-vol-2abcd.pdf).

All eight forms pass 34,816 authored AOT cases. A separate bit-position scan, compiled with BMI disabled, and authored hardware instructions agree on results and defined CF/OF/SF/ZF flags. Checks include full State preservation, 32-bit zero extension, zero/single-bit/high-bit inputs, guarded memory, exact access counts and logical returns. Undefined AF/PF outputs are excluded. These tests execute no original game code.

The sparse driver accepts an explicit semantic directory. A missing explicitly selected module rejects rather than silently selecting the default. Manifest-declared exact UD2 bytes are routed to a dedicated `__bb_native_ud2` native boundary. The faulting logical address is preserved; the handler is nonreturning. Undeclared traps, unsupported trap kinds, wrong bytes, duplicate declarations and claimed fallthrough reject. The compiler records explicit native traps separately from semantic instruction counts. This is diagnostic fault termination, not an implementation of PS4 signal/exception delivery.

Six input cases plus authored conditional normal-return/fault execution pass. The fault handler checks full State and untouched memory, reports logical PC 0x100020045, and terminates the fixture process with the expected status. No hardware UD2 instruction or game code is executed. The existing ten sparse input cases and 8,192 authored branch/return cases also pass with the new driver.

All 48 prior rejected entries were resubmitted without additional filtering. Fourteen now compile into seven objects totaling 473,648 bytes; all seven objects repeat byte-for-byte. They contain sixteen explicit native UD2 sites and retain their runtime dependencies. The other 34 entries remain rejected with exact logs. Combining these objects with the original complete survey gives 21,118 compiled entries with no duplicate logical roots. The two outstanding constructor entries are 0x10326c0 and 0x28772a0, both blocked by VSHUFPS.

Current artifacts:

- Driver: `build/sparse-lift-v5/bb-sparse-lift.exe`.
- Semantic module: `build/extended-semantics-v1/amd64_avx.bc`.
- Checks: `local/compiler-spike/bmi-semantics-v2`, `sparse-trap-v1`, `sparse-checks-v5`.
- Recompilation: `local/compiler-spike/startup-bmi-trap-recompile-v2-repeat`.
- Audit: `reports/bmi-trap-evidence.json`.

Use fresh outputs and `tools/run_record.py --id UNIQUE --`. Reproduce builds with `-m tools.build_extended_semantics build/NEW` and `-m tools.build_sparse_lift build/NEW`. Checks use `-m tools.bmi_semantics_checks OUT DRIVER SEMANTICS_DIR`, `-m tools.sparse_trap_checks OUT DRIVER` and `-m tools.sparse_lift_checks OUT DRIVER`.

Recompile with `-m tools.startup_batch_compile local/cfg/startup-recovery-v9-repeat OUT DRIVER --entries local/compiler-spike/startup-rejection-inspection-v1/selection.json --semantics SEMANTICS_DIR --explicit-ud2`. The run returns failure while any entry rejects; those failures are retained evidence. Audit with `-m tools.summarize_bmi_trap`, followed by the recovery/control-flow integration audits.

Next address the two constructor VSHUFPS blockers with independent lane, immediate, alias and upper-vector checks. Continue the remaining SIMD/state semantics and native runtime closure afterward. P1 baseline work remains independent.
