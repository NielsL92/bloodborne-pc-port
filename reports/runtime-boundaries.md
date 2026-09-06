# Native memory and control boundary checkpoint

2026-09-06 22:13 UTC. P3 remains open. These tests execute private RAM helpers and authored AOT routines only. No game-derived object has been linked or executed and no native boot/playable port exists.

The runtime copies initial bytes into private VirtualAlloc backing and seals the mapping layout. Logical code remains non-executable and read-only; writes to registered code stop as uncovered behavior. No original package or hardlinked view is changed. Logical reads/writes support unaligned and adjacent-region spans, validate the complete access before copying, and reject overflow, missing mappings and permission violations. Native service accesses must use these helpers. A recursive critical section serializes registered RAM accesses, locked sequences and compare/exchange; barriers use the host memory barrier. This is a conservative bootstrap with no performance claim, external-writer/MMIO support or general console memory-model proof.

Static compiled-target, import and source/request tables drive native dispatch. An import binds to an explicit native handler, a compiled export, or an unimplemented-import stop carrying NID/library/module/stub identity. The authored compiled-export path does not pop the logical return twice. A block transfer requires State PC/actual/requested agreement and an approved source/request pair. An available target alone does not authorize that source transfer. Indirect calls and jumps use known compiled entries; unknown targets stop. Caller source is reported as unknown where the current interface does not carry it. No byte decoder, interpreter/JIT or original CPU execution exists in this runtime.

Fault handlers are noexcept and terminate the child process through ExitProcess after a structured diagnostic, preserving actual State PC, RSP, entry, thread, source/target information and compilation identity. They do not throw across nounwind code or use fixture longjmp. This is explicit stopping, not guest exception delivery or nonlocal recovery. Hypercalls and UD2 have distinct stops. Real import services and FP profile/metadata bindings remain unimplemented.

Memory-v2-deterministic and memory-v3-repeat each pass 49,256 positive cases, including 32,768 linearizable tickets from two four-thread protocols, unaligned/cross-region scalars and raw floating-point bits. Eleven child processes verify precise permission, mapping, context, atomic and alignment failures; two setup cases reject overlap and writable code. Four selected objects/results repeat byte-for-byte.

Control-v4-deterministic and control-v5-repeat each pass 20,480 authored AOT cases across direct calls plus sourced branches, native service calls, compiled exports, indirect calls and indirect jumps. Full State and logical stack slots are compared. Nine negative cases verify unregistered source transfers, bad requested targets, unexpected returns/nonreturn violations, unknown targets, unresolved imports, UD2 and both hypercall classes. A setup case rejects duplicate tables. Fifteen selected inputs, audits, bitcode, objects, generated declarations and stable results repeat byte-for-byte. Runtime thread IDs and PE timestamps are deliberately not compared as deterministic artifacts.

Preserved failures: runtime-control-v1 failed before generating its output because of a Python literal-newline error; v2-generator exposed a C++ AddressSpace namespace collision with Remill. Both were fixed, retained and rerun. Runtime-memory-v1 and control-v3-qualified passed before the deterministic COFF option and final diagnostic identity field were added. Evidence checker validates recorder success and source ZIP contents for both current repeats. See runtime-boundaries-evidence.json.

Reproduce in fresh output directories using tools/run_record.py and these module commands:

- tools.runtime_memory_experiment OUT
- tools.runtime_control_experiment OUT build/sparse-lift-v11-source-exits/bb-sparse-lift.exe build/extended-semantics-v35-divide
- tools.summarize_runtime_boundaries OUT (pins this checkpoint's run directories)

The active 386-object startup manifest, recovery database and unknown-target counts remain unchanged. Next bind FP/numeric support with explicit profile provenance, generate and verify static tables from the manifest/dispatch registry, and test complete linkage. P3's exit-handling gate is not inferred from these fixtures. P1 baseline work remains separate and unchanged.
