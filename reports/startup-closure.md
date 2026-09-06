# P3 callback and control closure continuation

Updated 2026-09-06 18:55 UTC: all 21,181 current manifest entries compile into 386 objects, including all initial constructors. Canonical `local/cfg/startup-recovery-v31-conditional-repeat` retains 874,279 instruction addresses and every prior unknown target. Zero compiler rejections/quarantines depends on five exact conditional ending annotations, each carrying an unresolved native continuation obligation. Use `local/compiler-spike/conditional-control-evidence-audit-v2-exits/active-objects.json`. P3 remains open pending complete linkage/exit handling; no native game execution. See reports/conditional-control.md and reports/conditional-control-evidence.json. Earlier dated checkpoints below are historical.

Updated 2026-09-06 18:34 UTC: canonical `local/cfg/startup-recovery-v29-lua-panic-repeat` has 21,181 entries / 874,279 instruction addresses. Two Ghidra-checked mutable Lua panic candidates add ten instructions and one reproducible object. The complete active set `local/compiler-spike/lua-panic-evidence-audit-v1/active-objects.json` contains 21,176 entries / 384 objects, zero compiler rejections and five quarantines. Every previous unknown target and all initial constructors remain represented. Public Lua 5.0.2 layout is corroborating evidence only; the supplied state has explicit custom extensions. See reports/lua-panic.md and reports/lua-panic-evidence.json. P3 remains open. Earlier dated checkpoints below are historical.

Updated 2026-09-06 18:01 UTC: current recovery `local/cfg/startup-recovery-v27-rtti-repeat` has 21,179 entries / 874,269 instruction addresses. One Ghidra-checked initial RTTI target adds a four-instruction object; the complete active set `local/compiler-spike/exception-rtti-evidence-audit-v1/active-objects.json` contains 21,174 entries / 383 objects, zero compiler rejections and five quarantines. All 18,444 initial constructors and previous unknown targets remain represented. See reports/exception-rtti.md and reports/exception-rtti-evidence.json. P3 remains open. Earlier dated checkpoints below are historical.

Updated 2026-09-06 17:41 UTC: three independently checked, exact service-call annotations reduce fence quarantines to five. The current complete static census is 21,173 entries / 382 objects; zero compiler rejections and all 18,444 initial constructors are represented. Continue with `local/cfg/startup-recovery-v25-services-memory` and `local/compiler-spike/startup-services-evidence-audit-v1/active-objects.json`. See `reports/startup-services.md` and `reports/startup-services-evidence.json` for the conditional contracts, reproducible objects, retained failures and exact remaining work. P3 remains open; native service/control execution is not established. Earlier dated checkpoints below are historical.

Updated 2026-09-05 20:57 UTC. P3 remains open. No native game boot or playable port exists.

Continue with `local/cfg/startup-recovery-v7-repeat/analysis.sqlite` and its `recovery_*` tables, `compilation-manifest.jsonl`, `frontier.jsonl` and `constructor-order.json`. These four files reproduce byte-for-byte from v6. All earlier runs remain preserved. The 18,444 ordered initial constructor records remain unchanged.

| Static evidence | Previous v4 | Current v7 |
| --- | ---: | ---: |
| Entries across eight modules | 21,095 | 21,160 |
| Distinct instruction addresses | 870,923 | 873,582 |
| Fallthrough fence findings | 146 | 9 |
| Unresolved indirect-call records | 8,980 | 9,029 |
| Unresolved indirect-jump records | 421 | 430 |
| Unvalidated import records | 20,760 | 20,842 |
| Reached exception regions | 22 | 31 |
| Overlap / undecodable findings | 0 | 0 |

The larger indirect frontier is newly exposed work. A drained explicit request queue excludes unknown targets and does not close startup discovery. These are static record counts, sometimes sharing physical sites; they are not execution coverage.

## Investigated control boundaries

The 145 earlier final calls were grouped by exact callee and provider. Most lead to supplied libc length-error, out-of-range and runtime-error helpers, or small game wrappers around them. `tools/cfg_derive_control.py` derives conditional summaries through a least fixed point over documented control contracts. Every analyzed normal branch and metadata landing-pad root must reach a known nonreturning transfer. Missing successors, cycles, returns, unresolved indirect control and service boundaries reject the proof. A final call or unwind end alone supplies no nonreturn evidence.

Twenty-eight of 31 candidate entries passed this bounded derivation in two rounds. Ghidra independently decoded all 28, agreeing on the 254 instruction identities and paths used in the summaries. No expected instruction addresses, no-return annotations or branch targets were supplied to that Ghidra run. The checked artifact retains exact instruction bytes, module hashes, source database and contract hashes, import keys, transitive dependencies and Ghidra evidence. Applying a bundled import summary also requires an unambiguous matching export. Native binding, exception behavior, valid call conventions and code immutability remain assumptions to implement and validate.

The 137 removed fence findings are conditional control-flow corrections. The nine remaining findings are retained with exact addresses and targets in `local/cfg/startup-frontier-delta-v2/delta.json`:

| Component | Findings | Next distinguishing work |
| --- | ---: | --- |
| libc abort, entry 0x1f560 | 1 | The final NOP follows a call to kernel debug-exception with error 0xa002000b and second argument zero. Keep any future annotation contextual; the generic service can reject other arguments and return. |
| libc exit, entry 0x5ff10 | 1 | Its final PLT call resolves to kernel `_exit`, NID 6Z83sYWFlA8. Establish a separate process-termination/service contract. |
| libc throw/rethrow chain, entries 0x60510, 0x60560, 0x606f0 | 3 | Internal 0x60750 has unresolved virtual calls before terminate. The conservative derivation rejects it; callback and exception runtime behavior remain open. |
| Main entry 0x11e6220 | 1 | New dependency ends at `_Xbad_alloc`, NID eT2UsmTewbU, supplied libc 0x5ebd0. Inspect its throw graph and landing pads as a fresh derivation input. |
| Main thread-exit wrapper 0x207f990 | 1 | Exact scePthreadExit NID 3kg7rT0NQIs. Native thread cleanup callbacks and thread termination need an explicit contract. |
| Main entries 0x210b0e0 and 0x210b940 | 2 | Callee 0x210ad70 conditionally invokes an unresolved object virtual call, then exit, or restores context through longjmp. Preserve the indirect callback and restored-context obligations. |

Pinned shadPS4 sources corroborate symbol identities and service behavior, but are not console observations or native runtime implementations. In particular, pthread cleanup routines in that reference still call original guest pointers directly; copying that execution path would violate the native deliverable.

## Callback closure

`tools/cfg_callback_contracts.json` assigns exact argument roles for __cxa_atexit, atexit, __cxa_throw destructors and scePthreadCreate. Roles apply to exact import identities or matching bundled exports, including tail transfers. Constant argument provenance is restricted to one basic block. Unknown registers, memory loads and path merges remain unresolved. An ABI-established callback argument can seed an unindexed entry; arbitrary executable-mapping constants still need independent code-entry evidence.

The current graph records 2,300 constant callback arguments representing 104 unique local target addresses: 2,292 __cxa_atexit records, three atexit records, four throw-destructor records and one thread-start record. It retains 170 unknown callback arguments: 153 destructor registrations, one atexit and 16 throw-destructor arguments. Registration success, registry mutation, object/DSO lifetime, invocation order and runtime target identity are unvalidated. The broad constant-argument frontier remains separate. [Destructor registration ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#dso-dtor), [exception destructor ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html#cxx-throw).

Callback recovery and transitive calls add 65 entries. Ghidra checked every new entry and every remaining boundary entry: 73 windows. An entry-only run missed some separately entered exception pads; a second run also received the recorded LSDA landing-pad roots. All 3,234 shared instruction identities then agreed, with no recovery-only instructions. Sixteen remaining reachability differences were traced through Ghidra's own flow to ordinary fallthrough after annotated nonreturning calls. Both raw runs and explanations remain preserved. This checks bounded decoding, not complete function extents or exception execution.

## Compilation and reproducibility

All 65 new entries were submitted to the manifest compiler in module/RVA order, with no size or gap filtering. Fifty-two produced Windows objects totaling 118,587 bytes. Forty-two objects retain declared CPU boundaries. In that retained first batch, twelve sparse instruction sets required a sparse Remill input adapter and one entry retained a fence issue. Those 13 entries were explicitly excluded, with their manifests and reasons preserved. No filler or embedded data was inserted. No runtime link, execution, correctness or performance result is claimed.

Twenty-eight focused tests pass, including branch alternatives, cycles, missing successors, landing-pad returns, unindexed ABI callback targets, tail registrations, unknown arguments and the prior decode/exception checks. The evidence audit verifies every built object against the current instruction manifest, all requested entries, the independent comparisons, immutable source ZIPs and exact repeated database/manifest/frontier/order hashes. The derivation also repeats identically after hardening its conditional-jump guard.

- Database SHA256: `80472617d1834fb106d75cc03ec65a4589adc1c0b8eae4f5ffc8a6490c843770`
- Manifest SHA256: `0bf25c53dbe20104e1c854fea797a86a7d58291df81ef85009741ee6405a198f`
- Frontier SHA256: `cf4ac27bacaf7958705817b47682132eace863e1579c15fc5323a5c08378f720`
- Focused evidence: `reports/startup-closure-evidence.json`, integrated into `reports/startup-recovery-evidence.json` and `reports/control-flow-evidence.json`.

## Reproduce and continue

Always use `tools/run_record.py --id UNIQUE -- COMMAND` and fresh output directories.

1. Derive: `.venv/Scripts/python.exe -m tools.cfg_derive_control local/cfg/startup-recovery-v4 local/cfg/NEW`.
2. Independently decode: `-m tools.ghidra_recovery_check local/cfg/startup-recovery-v4 local/cfg/NEW --selection local/cfg/derived-control-v2/selection.json`.
3. Verify summaries: `-m tools.check_derived_control local/cfg/startup-recovery-v4 local/cfg/derived-control-v2/candidates.json local/cfg/ghidra-derived-control-v1 local/cfg/NEW`.
4. Recover: `-m tools.cfg_recover_startup local/cfg/NEW --jump-evidence local/cfg/startup-table-bytes-v1/tables.json --control-evidence local/cfg/derived-control-checked-v1/contracts.json`. Keep the default immutable startup-db-v1 seed; do not use an extended database as the seed.
5. Compare: `-m tools.startup_frontier_delta local/cfg/startup-recovery-v4 local/cfg/startup-recovery-v7-repeat local/cfg/NEW`.
6. Independently check new entries and issues: `-m tools.ghidra_recovery_check local/cfg/startup-recovery-v7-repeat local/cfg/NEW --selection local/cfg/startup-frontier-delta-v2/selection.json --exception-roots`.
7. Compile the new batch: `-m tools.startup_manifest_compile local/cfg/startup-recovery-v7-repeat local/compiler-spike/NEW --entries local/cfg/startup-frontier-delta-v2/new-entries.json`.
8. Checks: `-m unittest tests.test_derived_control tests.test_startup_recovery tests.test_exception_metadata -v`. Audits in order: `-m tools.summarize_startup_closure`, `-m tools.summarize_startup_recovery`, `-m tools.summarize_cfg`.

The later sparse adapter resolves all twelve sparse exclusions; see reports/sparse-compiler.md. Next investigate the nine specific boundaries above; extend exact callback provenance and indirect tables/vtables while retaining mutable/unknown targets. Actual startup still needs native import, callback, return, exception and service contracts before the P3/P4 gates pass.

P1 remains independent: Hunter's Dream route, profiler overhead, CPU/GPU/queue costs and the opening audio mutex crash remain pending. No new baseline run occurred in this continuation. The current managed sandbox helper fails setup; approved require_escalated calls work. Use that route without another restart/read approval. No user action or paid component is needed.
