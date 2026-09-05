# P3 control-flow and dependency recovery

Updated 2026-09-05 18:02 UTC. P3 began after the bounded P2 feasibility gate. **P3 startup compilation/exit closure has not passed.** No native game boot exists.

## Current database and startup gate

Use local/cfg/startup-db-v1/analysis.sqlite for continuation. It combines metadata, a bounded recursive survey, independently checked exception records and the executable's initializer roots. The database SHA256 is 4e95fef8253d7c3eb7eecda275c9d72c0574dfed2a9f0f7375190ac8242ed299. Earlier databases and failed runs are retained.

The actual entry at RVA 0xa0 calls the initializer at 0x20, which is absent from the unwind index. Its 113-byte code contract was checked independently with Ghidra: 34 recursively reachable instructions and indirect calls at 0x58 and 0x82 agree. The initial forward constructor array is empty. The reverse list contains **18,444 distinct relocation-backed constructor targets**, of which **16,069 lack an unwind-index start**. The walk ends at an explicit -1 sentinel. Order, slots, relocation addends and initial-state evidence are preserved in local/cfg/startup-v1. Original files were not changed.

This exposes a major coverage gap in an unwind-seeded compiler batch. Constructor pointers are initial-state targets, not immutable runtime guarantees: constructors can modify later entries or register callbacks. Every unexpected runtime target must still fail with diagnostics.

The current query from entry traverses 19 already-decoded ranges and stops at 18,437 missing bodies, five unvalidated import call sites, two unresolved indirect calls, four annotated control contracts requiring runtime handling, and one range-end finding. See local/cfg/startup-db-v1/frontier.json and traversed.json. The query stops at missing bodies, so it does not claim complete startup discovery.

Next: recover the ordered initializer roots, beginning with unindexed entries, and expand direct-call/exception closure into compilation manifests. Preserve code/data ambiguity and unknown targets. Build service contracts for the actual entry imports and all discovered callbacks. Do not proceed to broad P4 execution by treating undecoded entries or registration matches as implemented code.

## Repeated metadata and independent tools

The seed database identifies all code by exact module hash and RVA:

| Fact type | Count |
| --- | ---: |
| Modules | 8 |
| Program segments | 67 |
| Indexed unwind ranges | 169,640 |
| Dynamic symbols | 3,486 |
| Relocations | 238,609 |
| Metadata entry seeds, before exception/initializer additions | 171,430 |
| Relocated executable-address pointer candidates | 204,539 |
| Differentially tested relative jump edges | 5 |

All module hashes match the earlier transitive inventory. Supported unwind encodings parsed without errors, and indexed ranges have no detected overlaps. An indexed range is not necessarily a function. Pointer candidates are not proven call targets.

Fresh seed-v1 and seed-v2 databases reproduced byte-for-byte, SHA256 390dc528c6a562ee10d121cc5689d76a34c17d386f7e4d5668ae6da8ab9da43e. The original PKGs were not rehashed.

Portable Ghidra 12.1.3 and Temurin JDK 21.0.12.1+1 were installed after archive size/SHA256 verification. Official URLs and hashes are in reports/p3-tool-downloads.json. Settings/cache/temp remain under local/tool-profiles/ghidra. [Official Ghidra release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.3_build).

Ghidra independently recovered the real bit-reader's five targets at RVA 0x4023a and agreed on 113 instruction boundaries. The script supplied no jump targets. That check continues to pass against recursive reachability in every survey. Decompiled C is an analysis artifact, not automatically trusted port source.

## Recursive survey and investigated failures

Survey selection starts with the prior 1,000-function stratified compilation sample, P2 roots/callees, entry, and deterministic size-quartile samples of bundled modules. Adding all exception-bearing ranges gives 1,463 ranges.

| Survey | Ranges | Instructions | Overlap findings | Undecodable/range-crossing findings | Range-end findings |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1, no import exit contracts | 1,239 | 391,611 | 3 | 45 | 471 |
| v2, stack-failure contract | 1,239 | 390,527 | 0 | 2 | 75 |
| v3, longjmp contract | 1,239 | 390,523 | 0 | 0 | 51 |
| v4, exception landing pads added | 1,463 | 423,277 | 0 | 4 | 260 |
| v5, unwind/termination and local wrapper contracts | 1,463 | 423,239 | 0 | 0 | 42 |

Zero decode conflicts in this selected set is not a complete-CFG result. Survey v5 retains 6,147 indirect-call edges, 823 indirect jumps, 45 unknown restored-context destinations, 203 unknown exception continuations, and 133 cross-range jumps. No trace or compilation percentage is inferred.

The original three overlaps and most failed decodes came from ordinary fallthrough after __stack_chk_fail into padding or embedded tables. Exact PLT/GOT relocation identity resolved the import; the pinned implementation and independent GCC contract establish its nonreturning behavior. [GCC stack-protection contract](https://gcc.gnu.org/onlinedocs/gccint/Stack-Smashing-Protection.html).

Two remaining cases followed libc longjmp. The supplied libc export at RVA 0x2fd00 restores RSP, saved registers and return PC and RETs through that restored context. The annotation removes only ordinary fallthrough and preserves the unknown restored target. It is static evidence, not execution validation of that libc routine. [Independent C-library contract](https://www.sourceware.org/glibc/manual/2.23/html_node/Non_002dLocal-Details.html).

The four failures exposed by landing-pad seeds followed _Unwind_Resume or an 11-byte begin-catch/terminate helper. Exact supplied-module bytes and import/export identities support typed contracts. Resume remains an unresolved exception continuation. [Exception ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html).

The supplied std::terminate implementation contains a RET after an indirect handler call. The applied contract requires a valid handler that terminates without returning; that handler must be validated during integration. A returning handler is a contract violation, not permission to decode adjacent tables as code. [C++ termination requirements](https://eel.is/c%2B%2Bdraft/exception.terminate).

All contracts, byte hashes, local-entry bounds, provenance and assumptions are explicit in tools/cfg_import_contracts.json. Only exact NID/library/provider PLT matches or exact module/RVA/byte identities apply. No generic “last call must not return” heuristic is used. The 42 remaining range-end findings remain open, including throwing-library helpers and entry's exit call.

## Exception metadata

The reader identifies 225 zPLR ranges: 38 in eboot and 187 in libc. They contain 1,223 call-site records, 692 distinct landing pads and 121 referenced action records, with zero parser issues.

Ghidra independently parsed every selected CIE/FDE/LSDA from supplied mapped bytes. It agrees on all 225 range starts/sizes, LSDA pointers and all 1,223 call-site intervals, landing pads and action indices. Only FDE addresses were supplied; no expected LSDA destinations or call-site results were passed to Ghidra.

Seven focused reader checks pass, including malformed/cyclic action chains, overlapping intervals, invalid landing pads, truncated call-site extents, unsupported encodings and FDE/index disagreement. This does not implement type matching, CFI register restoration, personalities, Windows unwind behavior or runtime exception propagation. LLVM's public personality implementation documents the table layout. [LLVM LSDA layout](https://github.com/llvm/llvm-project/blob/main/libcxxabi/src/cxa_personality.cpp).

The first extractor run failed because the Python merge duplicated an lsda keyword; v2 corrected it. The first Ghidra comparison failed because JSON omitted null landing-pad fields. All 37 differences were checked: numerical values agreed. serializeNulls fixed the exporter, and a fresh v2 comparison passed both modules. Failed outputs are retained.

## Reproduction and durable evidence

Wrap every command with .venv/Scripts/python.exe tools/run_record.py --id UNIQUE -- COMMAND. Each output directory must be new. Commands below use a new destination but intentionally read the pinned prerequisite evidence paths in their source.

- .venv/Scripts/python.exe -m tools.cfg_seed local/cfg/NEW
- .venv/Scripts/python.exe -m tools.cfg_exceptions local/cfg/NEW
- .venv/Scripts/python.exe -m tools.ghidra_exception_check local/cfg/NEW
- .venv/Scripts/python.exe -m tools.cfg_survey local/cfg/NEW --exceptions
- .venv/Scripts/python.exe -m tools.startup_inventory local/cfg/NEW
- .venv/Scripts/python.exe -m tools.ghidra_startup_check local/cfg/NEW
- .venv/Scripts/python.exe -m tools.cfg_startup_database local/cfg/NEW
- .venv/Scripts/python.exe -m unittest tests.test_exception_metadata -v
- .venv/Scripts/python.exe -m tools.summarize_cfg

reports/control-flow-evidence.json is the focused P3 consistency audit, with artifact hashes, survey comparisons and run identities. Run manifests retain exact source snapshots even though results were generated before the source commit. reports/execution-audit.json remains the earlier P0/P1/P2 audit; it is not relabeled as a fresh whole-workspace audit.

P3 is open. P4-P9 remain unstarted. Baseline measurements, Hunter's Dream route, profiler overhead and the intermittent opening audio mutex crash remain separate P1 work. No user installation/action is required for the current tools.
