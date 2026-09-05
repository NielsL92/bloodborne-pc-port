# Complete startup compilation survey

Updated 2026-09-05 22:34 UTC. The full v9 startup manifest set was submitted to the isolated sparse Remill driver. This is static native compilation evidence; no game object was linked or executed.

`tools/startup_batch_compile.py` groups entries by exact module hash and RVA into batches bounded by 128 entries or 5,000 supplied instructions. A larger single entry stays intact. Only exact instruction bytes are supplied. Failed batches are recursively split so every rejected entry is identified. Eight manifests with unresolved fence findings are explicitly quarantined. No size or instruction-shape exclusions hide failures.

The experiment assigns distinct logical module bases, preserving main base 0x100000000 and reserving separate 4-GiB slots for bundled modules. The recorded mapping is a compilation identity; it does not implement relocation or loading. Entry, LSDA and independently recovered transfer roots are compiled. Missing code, native services, callbacks and indirect/exception targets remain explicit runtime dependencies.

| Full survey result | Count |
| --- | ---: |
| Total manifests | 21,160 |
| Quarantined boundary manifests | 8 |
| Attempted entries | 21,152 |
| Successfully compiled entries | 21,104 |
| Compiled initial constructors | 18,442 of 18,444 |
| Rejected entries | 48 |
| Successful objects | 372 |
| Object bytes | 63,178,585 |
| Compiled instruction addresses / roots | 858,411 / 21,186 |
| Duplicate compiled logical roots | 0 |
| Explicit missing-path records | 4,326 |

The full survey intentionally returns failure while any entry rejects. Its first eight-batch pilot compiled 802 of 805 selected entries; three failures exposed missing BLSR semantics. The complete run exposed further missing BMI/SIMD and floating-point state semantics, plus eight entries initially rejected at decoder error categories. Rejection occurs on unsuccessful semantic lifting; these instructions are not silently counted as compiled or replaced with execution fallback.

Current retained output: `local/compiler-spike/startup-batch-all-v1`; source database `local/cfg/startup-recovery-v9-repeat`; driver `build/sparse-lift-v3/bb-sparse-lift.exe`. The audit verifies object hashes, actual native symbols, exact instruction maps, distinct root definitions, every requested entry and every failed input. Full local details are in the per-batch manifests/logs, with checked summaries in `reports/startup-batch-evidence.json`.

Reproduce using `tools/run_record.py --id UNIQUE -- .venv/Scripts/python.exe -m tools.startup_batch_compile local/cfg/startup-recovery-v9-repeat local/compiler-spike/NEW build/sparse-lift-v3/bb-sparse-lift.exe`. Add `--sample-batches 8` for the bounded pilot. Use `-m tools.summarize_startup_batch` to audit the retained full run.

The read-only inspector checks all 14,595 instructions in the 48 rejected entries. Every instruction decodes with matching bytes/boundaries; zero invalid categories or decode failures occur. It identifies 889 problem sites: missing semantic selectors and sixteen deliberate UD2 traps. The complete selector list is local/compiler-spike/startup-rejection-inspection-v1/summary.json. Treat explicit traps separately from missing instruction semantics. Next independently cross-check rejected entries, implement missing semantics with authored correctness checks, then resubmit the rejected manifests. Preserve the existing driver/semantics and successful objects as historical evidence. Native linking, startup dispatch, indirect/callback/exception closure and service contracts still need implementation; full object construction alone cannot pass P3/P4. P1 Hunter's Dream, profiling and audio-crash work remains separate.

Ghidra independently checks all 48 rejected entries and agrees on all 14,595 instruction identities, including every one of the 889 problem sites. Its 202 extra instructions in fourteen windows all follow ordinary fallthrough after explicit nonreturn calls; no extra path remains unexplained by that bounded comparison. Raw paths and exact comparisons remain in reports/compiler-rejections-evidence.json. This does not validate the missing instruction semantics or implement those runtime contracts.
