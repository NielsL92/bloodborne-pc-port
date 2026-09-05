# P3 startup recovery checkpoint

Updated 2026-09-05 20:23 UTC. All 18,444 initial constructor entries now have recovered instruction bodies. **P3 startup compilation/control closure remains open. No native game boot or playable port exists.**

## Current artifacts

Continue from `local/cfg/startup-recovery-v4/analysis.sqlite`, `compilation-manifest.jsonl`, `frontier.jsonl` and `constructor-order.json`. The extension lives in the `recovery_*` tables; the older `decoded_range` / `decode_edge` tables are preserved survey evidence, not the new closure. The ordered roots are byte-for-byte equal to `local/cfg/startup-v1/roots.json`.

The v4 database, manifest and frontier reproduce byte-for-byte in `startup-recovery-v5-repeat`. Database SHA256: `950ac990432cafb7be77f8d5bd221af82fde8cba973195204104e6a1feffad55`. Manifest SHA256: `e617c3c839823e3355c9736b630e89cc5a7c040220f305487bcb05ab0b99b619`. Recorded evidence: `reports/startup-recovery-evidence.json` and the integrated `reports/control-flow-evidence.json`.

| Static recovery result | Count |
| --- | ---: |
| Ordered initial constructor entries | 18,444 |
| Constructor entries outside all indexed unwind ranges | 16,069 |
| Constructor entries with decode issues | 0 |
| Requested entries recovered across eight modules | 21,095 |
| Distinct recovered instruction addresses | 870,923 |
| Queued explicit dependency requests left undecoded | 0 |
| Overlap or undecodable-instruction findings in current recovery | 0 |
| Fallthrough-boundary findings | 146 |
| Unresolved indirect-call edge records | 8,980 |
| Unresolved indirect-jump edge records | 421 |
| Unvalidated import-call records | 20,760 |
| Broad constant-argument candidates in executable mappings | 26,084 |
| Reached exception regions requiring runtime contracts | 22 |

Counts are static records, sometimes sharing physical call sites; they are not execution coverage or percentages of port completion. A drained worklist excludes unresolved/candidate destinations and does not prove complete discovery.

## Recovery policy and investigated failures

`tools/cfg_recover_startup.py` recursively decodes from the recorded constructor entries, actual game entry, bundled DT_INIT entries, direct calls/jumps, matched bundled exports and independently corroborated candidate entries. It also seeds known exception landing pads and records personalities. Unwind ends and following metadata seeds are conservative analysis fences, not proven function ends. Fallthrough across a fence is quarantined. Direct branches cross it through an explicit new entry. Instruction bytes, ownership, edges, issues, references, request provenance and ordered constructor slots are retained.

The first run overexpanded constant call arguments into strings and other data stored in executable mappings. Its database and partial manifests remain under `startup-recovery-v1`; it is rejected as the current graph. Candidates now need separate metadata code-entry evidence before expansion and remain unvalidated even then. No table pointer, metadata start or successful decode is treated as permission to execute. The obsolete first export was stopped after later runs succeeded; its recorded nonzero exit and process identity remain preserved. An ownership-first indexed export removed its query-planner bottleneck.

Both remaining undecodable cases in v2 followed the supplied libc abort wrapper into relative jump-table data. Exact NID/module/RVA/byte identities and independent ABI contracts support the new abort, exit and __cxa_throw annotations. They suppress ordinary return fallthrough while retaining runtime termination, callback and exception obligations. The kernel debug-exception import itself was not given a generic nonreturn annotation. [C library abort behavior](https://sourceware.org/glibc/manual/2.42/html_node/Aborting-a-Program.html), [normal termination and callbacks](https://www.sourceware.org/glibc/manual/2.23/html_node/Normal-Termination.html), [C++ throw ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html#cxx-throw).

Ghidra independently inspected 112 windows: 97 constructor samples plus library disputes. It agreed on all 7,119 shared instruction bytes/lengths. Twenty instruction-set differences were traced through Ghidra's own flow to ordinary fallthrough after documented nonreturn calls. Raw comparisons and the explanation remain separate. Window bounds were supplied as analysis restrictions, not independently proven function extents.

For libc entries 0x61370 and 0x61640, a separate Ghidra decompiler run received supplied mapped bytes and the exact abort ABI contract, with no switch targets supplied. Both 13-case tables agree with a separate Capstone check of CMP/JA bounds, unchanged index, LEA/MOVSXD/ADD/JMP sequence and signed relative table bytes. The 12 distinct edges expose 125 more instructions. All 79 and 81 recovered instruction locations in those two routines agree exactly with Ghidra. These are static checks; exception execution and runtime table mutation remain unvalidated.

The remaining 146 fence findings end with 145 calls and one NOP. Examples and direct/import identities are retained in the evidence report. Do not suppress them based only on being last in an unwind range.

## Compilation and verification

A sample of 128 constructor ordinals, evenly spaced including the first and last, produced 128 Windows COFF objects directly from the manifest. The compiler checks original byte identity and accepts only contiguous recovered instruction sets; sparse sets are explicitly rejected pending a sparse-input adapter. All selected samples were contiguous. Objects total 401,948 bytes; 25 retain declared CPU boundaries. Memory/control helpers remain external. No runtime link, original-game CPU execution, native game execution, or performance result is claimed.

Nine recovery safety checks and seven exception-reader checks pass. They cover embedded data after returns, overlapping decode paths, fence fallthrough, direct cross-fence requests, invalidated register constants, uncertain versus seeded targets, exception-pad seeds, and malformed exception metadata. An initial overlap assertion was too specific about the correct conflict label; the failed run remains retained. Historical source evidence is verified against matching immutable run source ZIPs when the working source has since changed.

## Reproduction and next gate work

Always wrap commands with `.venv/Scripts/python.exe tools/run_record.py --id UNIQUE -- COMMAND`, using a fresh output directory.

- Recovery: `.venv/Scripts/python.exe -m tools.cfg_recover_startup local/cfg/NEW --jump-evidence local/cfg/startup-table-bytes-v1/tables.json`. This deliberately regenerates from the preserved startup-db-v1 source; do not pass an already extended database as --source.
- Independent boundary check: `.venv/Scripts/python.exe -m tools.ghidra_recovery_check local/cfg/startup-recovery-v4 local/cfg/NEW`.
- Independent table recovery: `.venv/Scripts/python.exe -m tools.ghidra_startup_tables local/cfg/NEW` (pinned v3 source and two disputed entries).
- Encoded table check: `.venv/Scripts/python.exe -m tools.check_startup_tables local/cfg/NEW` (pinned independent table evidence).
- Object sample: `.venv/Scripts/python.exe -m tools.startup_manifest_compile local/cfg/startup-recovery-v4 local/compiler-spike/NEW`.
- Checks: `.venv/Scripts/python.exe -m unittest tests.test_startup_recovery tests.test_exception_metadata -v`.
- Audits: `.venv/Scripts/python.exe -m tools.summarize_startup_recovery`, then `-m tools.summarize_cfg`.

Next investigate the 145 final-call identities and their exact local wrapper contracts; recover more of the 421 indirect jumps with the independent table workflow; classify callback registration arguments by exact service ABI rather than treating every executable-mapping constant as a callback. Expand vtable/RTTI and mutable constructor-table cases with provenance. Implement explicit compiler/runtime handling for actual import, callback, exception, restored-context and code-write boundaries before P4 startup. The object sample does not close these gates.

P1 remains separate: extend the saved route toward Hunter's Dream, measure profiler overhead and CPU/GPU/queue costs, and isolate the intermittent opening audio mutex crash. No new baseline run was performed during this P3 checkpoint. No user action or paid component is required.
