# Canonical guest MXCSR loads and stores

2026-09-06 13:47 UTC. Experimental v19 replaces LDMXCSR, STMXCSR and their VEX forms. All 812,640 authored cases pass. Loads read guest memory, validate reserved bits against an explicit guest feature mask, and update canonical State only after validation. Stores write the canonical guest CSR. Neither path reads or changes the host floating environment.

A new `__bb_native_mxcsr_fault` boundary distinguishes reserved-bit general protection faults from arithmetic SIMD faults. The fixture proves callback arguments, logical fault/return PC, complete State preservation, surrounding memory, exact read/write/profile calls and host floating-state isolation. Ordinary memory services remain responsible for access validation.

The matrix includes every 16-bit CSR value under both 0xffff and 0xffbf allowed-bit profiles, every upper reserved bit separately, combined upper bits, varied initial guest CSR/x87 pending state/flags and eight operand byte offsets. Intel hardware independently supplies 13,056 reserved-bit fault cases and ordinary load/store images. A further 98,304 cases enforce the explicit DAZ-reserved profile, without a hardware-absence claim. Ninety-six unavailable-memory cases diagnose unsupported fixture mapping and check that no CSR is committed and no profile service runs after a failed read. This is not general guest page-fault or console exception delivery.

The preserved original run has 812,592 cases differing in at least one contract. This number includes expected service calls and host-helper isolation, so it is not a count of unique architectural defects. Raw per-category results separately show guest CSR/memory differences, host control changes, missing reserved-bit faults and changes before an unsupported store. For example, STMXCSR changed guest 0xa581 to 0x8581 using the host rounding mode. The original tool invocation used `--characterize`; its wrapper pass means evidence collection completed, not that the semantics passed.

Primary AMD and Intel instruction descriptions agree that setting reserved CSR bits raises general protection, while merely loading unmasked sticky numeric flags does not immediately raise an arithmetic exception. The explicit feature mask distinguishes DAZ support. The future runtime must normalize a raw zero FXSAVE mask to 0xffbf and keep this choice consistent with image serialization. [AMD instruction reference](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/programmer-references/26568.pdf), [AMD mask definition](https://docs.amd.com/api/khub/documents/sD1_QL~h4Afq2_tvzxqqSQ/content), [Intel instruction reference](https://cdrdv2-public.intel.com/868137/325462-089-sdm-vol-1-2abcd-3abcd-4.pdf). These paragraphs were retrieved from the primary-source search index; direct AMD instruction PDF access returned 404.

The combined v19 module also passes 1,572,864 min/max, 4,194,304 round and 3,145,728 square-root authored checks, including their established precise fault contracts. All 557,864 x87 image cases pass. These are correctness checks; concurrent independent regression runs are not timing measurements.

The canonical recovery database contains five affected sites, all in the supplied libc hash 4378b47f46f1d856824a6f971db1a0c3f41833b77f49d2fba9538f667a139166:

| Entry RVA | Instruction RVAs |
| --- | --- |
| 0x2fcb0 | STMXCSR 0x2fcf5 |
| 0x2fd00 | STMXCSR 0x2fd21; LDMXCSR 0x2fd39 |
| 0x30430 | STMXCSR 0x3045a; LDMXCSR 0x30469 |

These are static sites, not execution coverage. No boundary or code/data interpretation changed, and no new game object is accepted. Startup remains at 21,168 compiled entries, two x87 rejects and eight quarantines. Native game boot and playable port remain absent.

Use fresh outputs and tools/run_record.py. `tools.mxcsr_experiment OUT DRIVER SEMANTICS` runs the authored matrix; `--characterize` retains intentional counterexamples. Build v19 with the existing v18 extension order plus MXCSR. Run `tools.run_semantic_suite OUT DRIVER SEMANTICS --families minmax round sqrt` and `tools.x87_image_experiment OUT DRIVER SEMANTICS` for the scoped regressions. `tools.summarize_mxcsr OUT` checks raw results, source ZIPs, identities, exact database sites and unchanged accepted semantics. Machine-readable evidence is reports/mxcsr-evidence.json.

Next: x87 memory conversions/arithmetic and MMX alias consistency, pointer metadata from all x87 producers, and remaining native control/service closure. Experimental v19 remains separate from accepted v9-sqrt. P1 route/profiling/audio work remains unchanged.
