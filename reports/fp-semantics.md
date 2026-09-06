# Precise floating-point instruction contracts

Updated 2026-09-06 00:18 UTC. The combined compiler census is **21,150 entries**, including all **18,444 initial constructor entries**. Two dependency entries still reject; eight uncertain boundary manifests remain quarantined. P3 remains open. No game-derived object was linked or executed.

`build/extended-semantics-v9-sqrt/amd64_avx.bc` adds integer implementations of VMINPS/VMAXPS, VROUNDSD and VSQRTPS. They update guest MXCSR explicitly and leave host floating-point state unchanged. Square root uses a restoring integer root/remainder and explicit binary32 rounding; scalar rounding operates on binary64 fields. Reciprocal-square-root remains the earlier host estimate intrinsic, with AMD Jaguar bit-exactness unverified.

The original 372 successful objects combine with eight new objects containing forty-six of the original forty-eight rejected entries. These supersede earlier extension batches. New bytes total 1,134,668; raw object bytes and instruction audits repeat identically. Actual COFF symbols match manifest roots with no duplicates across combined objects. Seventeen missing-path records, sixteen explicit UD2 sites and new native SIMD-fault declarations remain visible. Native linking, runtime services and control closure are not established.

## Independent evidence

An authored hardware probe records 77,824 result/status/fault observations. The integer min/max model matches all 8,192 relevant records; a naive denormal model mismatches 384 because a NaN suppresses a denormal exception in the same operand pair. The independent integer square-root model matches all 4,096 relevant records and captures precomputation exception priority.

The complete combined suite passes all earlier BMI/vector contracts plus:

| New AOT contract | Cases | Precise native fault cases |
| --- | ---: | ---: |
| Min/max, sixteen register/memory/alias forms and 128 MXCSR settings | 1,572,864 | 397,448 |
| Scalar round, four forms, all 256 immediate values and 64 MXCSR settings | 4,194,304 | 618,933 |
| Square root, six forms and 128 MXCSR settings | 3,145,728 | 1,875,621 |

Tests compare full guest State, status/control bits, logical PC, stack/return behavior, vector aliases/upper clearing and guarded memory. Inputs include special values, all finite exponent bins for square root, subnormals, sampled mantissas and mixed exception lanes. Portable references are separate from the integer semantic algorithms; authored hardware independently checks results and fault/status behavior. Reference hardware faults expose preserved XMM registers in Windows exception contexts; AOT fault checks compare the entire guest State including upper vectors. Numerical checks are bounded and are not a whole-game performance result.

Min/max preserves second-operand NaN/zero selection. Round obeys immediate/guest rounding selection and precision suppression. Square root suppresses newly raised precision when a vector precomputation fault is unmasked. These behaviors follow [Intel's instruction manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf) and are independently checked by the local probe. Windows exception codes are retained as host observations; they are not used as guest exception identities.

## Fault boundary and retained failures

`__bb_native_simd_fault(memory, state, raised, unmasked)` is explicitly nonreturning. Before it is called, guest sticky flags are updated while destination, guest stack and faulting PC retain pre-instruction values. The authored handler uses a bounded nonlocal escape. It does not implement PS4 exception delivery.

Min/max fixture v1 used CRT longjmp and exited with `STATUS_BAD_FUNCTION_TABLE` across generated code. Native Windows unwind support remains unimplemented. Fixture v2 used a builtin escape and exposed register corruption; v3/v4 recorded exact State/memory differences. Adding a complete nonvolatile clobber list in v5 did not fix it. Disassembly showed that the Windows builtin setjmp saved an unbiased frame base while the return path used a biased RBP. The v6 System V escape frame, consistent with the existing P2 fixture, restores the caller correctly and passes the complete matrix. All failed runs and disassembly are preserved. This fixture workaround is not a claim of general Windows unwind compatibility.

## Remaining x87 gate

Only libc entries 0x30430 and 0x53cd0 reject. Actual final semantic-symbol inspection finds FNSTENV_MEMmem28, FLDENV_MEMmem28 and FXSAVE_MEMmfpxenv missing. Adding serializers alone would be insufficient: pinned x87 push/pop updates values and TOP without updating tags; FNINIT writes the FSAVE union view while normal x87 code uses FXSAVE. FNINIT is not currently present in the recovered startup instruction census, so its source defect is not itself an observed startup path. Status also exists in both the saved environment and `state.sw` fields and needs a coherent contract.

The next bounded investigation is authored x87 environment/tag/state characterization, followed by a coherent implementation for the recovered forms. Keep these two entries rejected until their effects are independently checked. Indirect calls, callbacks, eight disputed control boundaries and native runtime/exception closure remain open. No user action is needed.

Evidence: `reports/fp-semantics-evidence.json`, `local/compiler-spike/fp-characterization-v1`, `minmax-model-v1`, `sqrt-model-v1`, `semantic-suite-v9`, and `startup-fp-recompile-v1` / `v2-repeat`. Reproduce with fresh output directories and `tools/run_record.py`: build BMI/SHUFFLE/BLEND/RSQRT/PACKED/TRANSFER/MINMAX/ROUND/SQRT in order; run `tools.run_semantic_suite`; recompile the original rejected selection using driver v5 and `--explicit-ud2`; audit with `tools.summarize_fp_semantics NEW`, `tools.summarize_startup_recovery`, then `tools.summarize_cfg`.
