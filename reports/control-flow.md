# P3 control-flow and dependency recovery

2026-09-05. Started after the bounded P2 feasibility gate. P3's recovery/closure gate is not passed.

The initial SQLite database (local/cfg/seed-v1/analysis.sqlite) records exact module hashes and RVAs for the executable and all seven supplied bundled libraries. Schema and builder: tools/cfg_seed.py. All module hashes were checked against the earlier transitive inventory; original PKGs were not rehashed.

| Fact type | Count |
| --- | ---: |
| Modules | 8 |
| Program segments | 67 |
| Indexed unwind ranges | 169,640 |
| Dynamic symbols | 3,486 |
| Relocations | 238,609 |
| Metadata entry seeds | 171,430 |
| Relocated executable-address pointer candidates | 204,539 |
| Validated relative jump edges | 5 |

All eight modules' supported unwind encodings parsed without errors; the indexed ranges had no detected overlaps. This does not establish source-level function boundaries. Pointer candidates may identify interior addresses or data and are not confirmed targets. Dependencies are recorded as names/candidates, not assumed HLE implementations.

Portable tools were installed under external/toolchains after archive size/SHA256 verification: Ghidra 12.1.3 and Temurin JDK 21.0.12.1+1. Identities/official download URLs are in reports/p3-tool-downloads.json. Ghidra's official instructions require JDK21; the pinned launcher properties and Java entry are used by tools/ghidra_headless.py, with settings/cache/temp directories kept inside local/tool-profiles/ghidra. [Official Ghidra release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.3_build).

The no-argument smoke invocation exited 1 with the expected usage text; it was not a Java/installation failure. The actual headless fixture check passed: Ghidra independently recovered the same five switch targets at RVA 0x4023a and agreed with Capstone on 113 instruction boundaries. No targets were supplied to Ghidra by the script. Embedded table data was not treated as instructions.

Evidence: local/cfg/ghidra-bitreader-v1, tools/ghidra_scripts/BBCheckBitReader.java, tools/ghidra_fixture_check.py. The Ghidra decompiler output is an analysis artifact, not automatically trusted source for the port. This is one independently checked function, not a whole-executable analysis.

Next: recursive decode across a structurally varied bounded sample, preserving unresolved indirect edges and code/data/boundary disagreements. Cross-check disputed cases with Ghidra, then extend toward startup/service/module closure. Do not count a metadata import or 1,000 compiled objects as a recovered executable.
