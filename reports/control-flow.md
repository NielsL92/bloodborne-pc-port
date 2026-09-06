# P3 control-flow and dependency recovery

Updated 2026-09-05 20:59 UTC. **P3 startup compilation/exit closure has not passed. No native game boot exists.**

## Current database and startup gate

The current extension is `local/cfg/startup-recovery-v7-repeat/analysis.sqlite`, using its `recovery_*` tables. It includes all 18,444 ordered initial constructor entries, 21,160 total entries across eight modules and 873,582 distinct decoded instruction addresses. The database, compilation manifest, frontier and constructor order reproduce byte-for-byte from v6. All constructor roots are preserved in invocation order; 16,069 are outside every indexed unwind range.

There are no current overlap or undecodable-instruction findings. Twenty-eight independently checked conditional control summaries reduce fallthrough findings from 146 to 9. Callback recovery adds 65 entries; the frontier now retains 9,029 indirect-call records, 430 indirect-jump records, 20,842 unvalidated import records, 170 unknown callback-argument records and runtime/exception obligations. The larger indirect frontier is newly exposed work. A drained explicit-target queue is not complete static discovery. No pointer candidate or object build is execution coverage.

The earlier sample builds 128 constructor objects. The new 65-entry batch builds 52 Windows objects, with 12 sparse and one disputed entry excluded. No P3 object was executed. Ghidra checks every new entry and remaining boundary entry; all 3,234 shared instructions agree after separately supplying LSDA roots. Earlier two-table checks remain preserved. Read `reports/startup-closure.md` for current commands, limits and exact remaining boundary cases; `reports/startup-recovery.md` preserves the initial checkpoint. Focused continuation evidence is in `reports/startup-closure-evidence.json`, integrated through the recovery evidence into `reports/control-flow-evidence.json`.

The earlier startup-db-v1, with its 18,437 undecoded frontier, remains immutable historical evidence. Existing survey tables inside the new database retain their original meanings. Initial constructor tables remain mutable runtime data; unexpected targets require strict failure diagnostics.

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

## Sparse compilation continuation (2026-09-05 22:14 UTC)

The isolated manifest lifter now compiles all twelve previously sparse-rejected dependency bodies: 1,517 instructions / 46 roots / 159,654 object bytes. Two fresh deterministic emissions are byte-identical; no filler is inserted, and every supplied instruction must match Remill boundaries and lift successfully. Ten input checks and 8,192 authored AOT cases pass. These are additional authored checks, separate from earlier real-function comparisons. The game-derived objects were not linked or executed and retain 27 explicit missing paths plus native runtime dependencies. The recovery graph remains v7 with nine fence findings and unresolved indirect/callback/exception/service contracts. See reports/sparse-compiler.md and reports/sparse-compiler-evidence.json.

## Full startup survey and v9 recovery (2026-09-05 22:34 UTC)

The repeated v9 recovery has 21,160 entries / 873,581 instruction addresses, eight fence findings and 155 unknown callback arguments. Twenty-nine control summaries / 265 instructions and all fifteen new null exception-destructor values are independently checked. The complete compilation survey attempts all 21,152 issue-free manifests and builds 21,104 entries, including 18,442 constructors, into 372 native objects. Its exact census is 858,411 compiled instruction addresses and 21,186 defined logical roots. Forty-eight semantic/decoder rejections and eight disputed manifests remain; see reports/startup-v9.md, reports/startup-batch.md and their machine-readable evidence. No game objects were linked or executed.

## BMI and explicit trap continuation (2026-09-05 23:04 UTC)

Tested isolated BLSR/BLSI semantics and explicit native UD2 boundaries compile fourteen more startup entries. Combined census: 21,118 entries; 34 semantic rejections and eight quarantined boundaries remain. Thirty-four thousand eight hundred sixteen authored BMI cases pass, alongside six trap declaration/control checks and the prior 8,192 authored sparse cases. Game-derived objects remain unlinked/unexecuted; all native fault delivery, services and dispatch contracts stay explicit. See reports/bmi-trap.md and reports/bmi-trap-evidence.json.

## Vector semantics and constructor compilation (2026-09-05 23:29 UTC)

All 18,444 initial constructor entries compile with the isolated, independently tested vector semantic extensions. Combined census: 21,121 entries; 31 compiler rejections and eight quarantined boundaries remain. Eight new objects reproduce byte-for-byte and supersede the seven BMI/trap objects for combined ownership. Authored checks pass 32,768 shuffle, 122,880 blend, 399,360 RSQRT and 34,816 BMI cases. RSQRT uses a native LLVM intrinsic; AMD Jaguar bit-exact estimates remain unverified. No game-derived object was linked or executed, and this does not pass startup runtime/control closure. See reports/vector-semantics.md and reports/vector-semantics-evidence.json.

## Packed integer and transfer continuation (2026-09-05 23:46 UTC)

Combined compiler census: 21,145 entries, all 18,444 initial constructors. Seven dependency entries reject and eight uncertain boundaries remain quarantined. Eleven extension objects repeat byte-for-byte, superseding earlier extension batches. Packed/select/transfer checks pass 262,144 / 376,832 / 593,408 authored cases; prior BMI/vector checks also pass in the final module. The remaining complete selector inventory covers floating-point min/max/sqrt/round and x87 environment/save operations. Guest/host MXCSR and native exception/state contracts require independent evidence. No game object was linked or executed. See reports/packed-semantics.md and reports/packed-semantics-evidence.json.

## Precise floating continuation (2026-09-06 00:18 UTC)

Combined census: 21,150 entries, all 18,444 initial constructors. Two x87 environment/save entries reject; eight uncertain boundaries remain quarantined. Integer min/max, scalar-round and sqrt semantics pass 1,572,864 / 4,194,304 / 3,145,728 authored cases, including precise guest faults and host MXCSR isolation. The complete earlier suite passes in the combined module. Eight extension objects repeat byte-for-byte, superseding earlier batches. Native Windows unwind and PS4 exception delivery are unimplemented; the authored nonlocal fixture uses an explicitly bounded System V frame. Existing x87 tag/layout/state inconsistencies require investigation before accepting FNSTENV/FLDENV/FXSAVE. See reports/fp-semantics.md/evidence. No game-derived object was linked or executed.

2026-09-06 x87 gate investigation: reports/x87-state.md/evidence preserves authored hardware/AOT counterexamples for tags, precision, split status and initialization. Twelve recovered entries own 355 x87 sites. Compiler census remains 21,150 with two rejections/eight quarantine cases; no game execution. State serialization requires a coherent native state contract. Independent callback/indirect closure work continues.

2026-09-06 callback relocation checkpoint: reports/callback-relocations.md/evidence establishes repeated v12/v13 recovery with 21,171 entries / 873,988 instruction addresses. Eleven new bodies compile into one repeated 34,421-byte object; combined 21,161 entries / 381 objects. Ghidra checks 94 windows / 4,030 shared identities plus 142 absolute slot operands. Existing instruction sets are unchanged. 9,041 indirect calls, 430 indirect jumps, 144 unknown callback arguments, two x87 compiler rejects and eight disputed manifests remain. No game execution.

2026-09-06 branch-sensitive callback checkpoint: reports/callback-slices.md/evidence checks v14/v15 recovery and one repeated 572-byte object for two destructor wrappers. Combined 21,163 compiled entries / 382 objects; 143 unknown callback arguments remain (142 initial mutable candidates plus the entry-provided finalizer). Ghidra independently checks both source slices and the new-body/boundary windows. No native game execution; x87 and runtime/control gates remain open.

2026-09-06 initial object dispatch checkpoint: reports/object-dispatch.md/evidence audits repeated v16/v17 recovery (21,175 entries / 874,029 instruction addresses) and a repeated 4,162-byte object for two new entries. Combined 21,165 compiled entries / 383 objects; all initial constructors. Three conditional initial table-slot records retain every unknown call. Independent Ghidra checks source/table bytes and ten closure windows / 614 instructions; 2,165 further matching constructor windows / 25,980 instructions are checked for the next candidate expansion. 9,042 indirect calls, 430 indirect jumps, 143 unknown callback arguments, two x87 rejects, eight quarantines and runtime contracts remain. No native game execution.

2026-09-06 constructor cohort checkpoint: reports/constructor-cohorts.md/evidence audits repeated v19/v20 recovery, 4,767 conditional initial target records and a repeated 21,448-byte object for three new bodies. Combined 21,168 compiled entries / 384 objects; all initial constructors. Independent SLEIGH checks 4,761 exact constructor windows / 59,897 instructions and eleven closure windows / 812 instructions. Every prior unknown record is retained. 9,044 indirect calls, 430 indirect jumps, 143 unknown callback arguments, two x87 rejects/eight quarantines and native runtime contracts remain. No game execution.
