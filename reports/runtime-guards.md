# Unresolved-slot guards and precise memory fault sources

Later execution checkpoint (2026-09-07 00:15 UTC): reports/native-startup.md records the first bounded supplied-entry AOT trace and its repeated canary-slot stop. Earlier no-game-execution statements below describe their dated experiments. No native boot or playable port exists.


Current generation (2026-09-06 23:42 UTC): see reports/native-memory-sources.md. Active objects are native-memory-manifest-v1; current registry is registry-v7-memory-repeat, link is link-v9-memory-repeat and loader plan is loader-plan-v8-memory. Complete authored/source/LLVM/link checks pass; native game loading/execution has not occurred.


2026-09-06 23:26 UTC. P4 remains open; P3 compilation/explicit handling passed under its recorded narrow scope. No game-derived CPU function has executed. Native module loading, boot and gameplay remain absent.

Registered RAM can now carry immutable named access guards over unresolved relocation slots. Full-span read, write, CAS and atomic accesses reject overlap before copying bytes or counting a completed operation. A guard may cross two adjacent logical regions with separate private NX backing. Setup rejects overlapping, unmapped, zero-sized or post-seal guards. These guards preserve unresolved values; they do not resolve the twenty strong data imports or seventeen TLS relocations.

The first authored NOP/load check exposed a compiler diagnostic defect: the guarded load at 0x1000e0001 reported the trace entry 0x1000e0000. The guard already stopped before any completed memory operation. The failed run local/runtime/guards-v1 and its exact source snapshot remain preserved. Relying on State.RIP alone cannot identify every memory instruction in a promoted trace.

Compiler v12-memory-sources optionally adapts scalar memory, CAS, atomics, barriers and native FP hooks after semantic inlining. Each bridge receives the explicit State argument and a load from the existing per-invocation BB_SOURCE_PC slot. The native bridge scopes those values around the helper and restores the prior scope on success. Only terminating faults update State.RIP to the executed instruction. Scopes never span control dispatch, and successful helpers preserve their existing architectural effects. The original helper ABI remains available for older authored fixtures with custom Memory layouts; every active game input must explicitly enable native_memory_provenance before startup.

Repeated guards-v3-flow / guards-v4-repeat pass 2,568 authored AOT cases, 648 unguarded span checks, 202 negative child-process boundaries and four setup rejections. Branch alternatives, loop exit, inner callee, caller continuation and an FXSAVE span all report the exact executed source. Nested-call probes allow only the expected prior stack/helper operations; no guarded access completes. 13 selected inputs, bitcode, native objects and outputs repeat exactly. Control (20,480 authored AOT), FP (32,768 authored AOT) and memory (49,256 unit cases) retain their previous outcomes.

Evidence: reports/runtime-guards-evidence.json and local/runtime/guards-evidence-v2-status/checked.json verify source ZIPs, the preserved counterexample, exact-repeat artifacts and regressions. The first summary attempt used the wrong recorder failure-status spelling; it is preserved as guards-evidence-v1 and corrected without changing test results.

The current game object manifest still uses compiler v11-source-exits. The authored fix is not yet applied to those objects. Next prepare and recompile all 386 objects, independently inspect source arguments and control contracts using LLVM, repeat, then regenerate registry/linkage before private native loading. Unknown targets, conditional export/control contracts, target FP profile and fourteen disputed x87 selector sites remain explicit. Guest exception/nonlocal recovery is not implemented. Baseline P1 evidence and its outstanding route, profiling and audio work remain separate.
