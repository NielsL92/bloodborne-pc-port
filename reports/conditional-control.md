# Conditional exception-control endings

2026-09-06. **All 21,181 current manifest entries compile; P3 remains open.** The complete set is `local/compiler-spike/conditional-control-evidence-audit-v2-exits/active-objects.json`, SHA256 `d23a3d2c94477ba3463b421929b678d48ce7e054a8cf943e179daa24526c2b74`: 386 objects, all 18,444 initial constructors once, zero compiler rejections and zero fence quarantines under recorded conditions. Native linkage/exit handling has not passed. No game-derived object was linked or executed, and no native game boot or playable port exists.

## Why the prior proof was inconclusive

The generic control derivation rejects unresolved indirect calls, even when their ordinary return paths subsequently reach a known terminal. That policy remains unchanged. The reviewed source-family evidence identifies a Lua panic callback and two libc exception-reporting calls, but does not establish their complete runtime target sets. Resolving initial candidate pointers is insufficient to claim those callbacks are closed.

A separate bounded proof makes the ordinary-call assumption explicit at exactly three CALL instructions:

| Helper | Call site | Independent instruction | Remaining uncertainty |
| --- | --- | --- | --- |
| main 0x210ad70 | 0x210ad84 | CALL [RAX+0x50] | mutable Lua global panic callback and state/global identity |
| libc 0x60750 | 0x60811 | CALL [RCX+0x10] | RTTI dispatch; initial symbol-relocation candidate only |
| libc 0x60750 | 0x6081f | CALL [RCX+0x10] | returned exception object's callback; target remains unknown |

Each listed call must either return to its explicit next instruction under the ordinary SysV call/return contract, or leave through an explicit native nonlocal/termination boundary. This is a condition, not a runtime implementation or an exhaustive transfer proof. Callback corruption of code/control state, asynchronous effects and unvalidated exception destinations remain outside the demonstrated contract. An indirect jump or arbitrary computed transfer does not receive this assumption.

Under that condition, main 0x210ad70 reaches the existing exit or longjmp contract. Libc 0x60750 reaches std::terminate. Libc 0x60560 calls the latter helper after the unwind-raise attempt. The proof constructs a finite acyclic path graph, checks every root including metadata landing pads, rejects missing successors and return paths, and verifies all terminal dependencies against the original base contract registry or the newly checked helper. No old derived summary is silently imported. The three callbacks remain unresolved in the database.

## Exactly five scoped annotations

| Owner | Final call | Checked helper |
| --- | --- | --- |
| libc 0x60510 | 0x60541 | 0x60560 |
| libc 0x60560 | 0x605d9 | 0x60750 |
| libc 0x606f0 | 0x60742 | 0x60750 |
| main 0x210b0e0 | 0x210b72b | 0x210ad70 |
| main 0x210b940 | 0x210b9e0 | 0x210ad70 |

The recovery loader matches full module hash, owner, call site and target; verifies source bytes, base identity, independent evidence and transitive helper dependencies; and adds an unresolved conditional-control continuation at each of these five sites. It does not install a global helper/import no-return summary. All other call sites and the generic derivation remain unchanged.

Ghidra independently decodes seven relevant owners and agrees on 650 recovered instructions. Its graph is reconstructed from SLEIGH flow and targets, not the Capstone successor list. Only the three named computed CALL instructions have a conditional ordinary successor; each terminal must independently be a direct call/jump to the recorded target. The three helper proofs cover their full recovered instruction sets. Raw extra Ghidra instructions remain preserved. No expected instruction list or no-return hint was supplied to Ghidra. Analysis/unwind fences still do not prove whole-function boundaries by themselves.

Eighty-eight focused tests pass. Authored negative cases reject unapproved callbacks, computed jumps, changed callback bytes, return paths, cycles, missing successors, additional unknown roots, callback-as-terminal claims, unused assumptions and altered call-site targets. Recovery tests verify the explicit runtime obligation and exact scope.

## Reproduction and compilation

Recovery v30-conditional-control and `local/cfg/startup-recovery-v31-conditional-repeat` reproduce database, compilation manifest, frontier and constructor order byte-for-byte. Database SHA256 `f33d86bb063c338e4bebaf603ae6f32f53e9bbf49f9bf7dd70c8506edc7959ef`; manifest SHA256 `3f729683862cf6c3aa7ebbcfbaef625cff078d27e33d10b30d7f04c0a16b5f99`. The streaming delta changes exactly five entries: no decoded instruction or original manifest edge is removed; each gains the annotation and runtime obligation, and its fence issue disappears. The database drops only the five conditional ordinary-fallthrough edges. All prior unknown-target counts remain: 9,044 indirect calls, 430 indirect jumps, 143 callback arguments, and three service obligations.

Fresh conditional-control-compile-v1 and v2-repeat build two byte-identical Windows objects, with identical inputs, root maps, audit and bitcode:

| Object | Entries / instructions | Bytes | SHA256 |
| --- | --- | ---: | --- |
| libc batch-0000 | 3 / 61 | 4,900 | b2ad536a548109bfaed44e5943bd417ac3db870f6b6a32bc70fa305c9a2bc426 |
| main batch-0001 | 2 / 479 | 41,148 | 4f8b567f6b6f2b422224026324d3d556223079634d59cf75ae6f246e8c2b81d4 |

The complete audit retains all previous 384 objects, checks every object hash and current instruction-set identity, and verifies unique compiled-root ownership. No entry remains excluded from the current 21,181-entry manifest. This is compilation evidence, not execution coverage.

All seven new explicit missing-block exits are classified. Libc 0x60546/0x605de/0x60747 and main 0x210b730/0x210b9e5 represent unexpected ordinary returns from the five new conditional endings. Main 0x210b722 follows an existing stack-protector terminal. Main 0x210d390 is a cross-unit tail transfer from 0x210b940 to an already compiled entry in startup-batch-all-v1/batch-0188. These paths need native diagnostics/dispatch; a missing-block intrinsic does not alone imply missing code.

All experiments use tools/run_record.py with fresh outputs. Preserve the failed conditional-control-inventory-v1: compilation manifests omit ordinary fallthrough, so its assumption about that input format was rejected. V2 reads indexed database edges and verifies their nonfallthrough subset equals the compilation manifest before proving paths. The source inspection also verifies both libc calls use RCX. Audits v1 and v2-exits are preserved; v2 adds the complete seven-exit classification and has an identical active object manifest.

## Next gate investigation

Audit actual defined/undefined symbols across the 386 objects and map all external transfers to compiled targets, imported services or explicit unresolved diagnostics. Validate native missing-block, direct/indirect call, return, callback, exception and nonlocal boundaries before declaring P3 passed or starting a game execution attempt. Unknown/unvisited coverage and mutable tables remain visible. No original-game CPU, emulator, interpreter, JIT or reassembly substitute has been introduced. P1 route/performance/audio investigations remain unchanged.
