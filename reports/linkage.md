# Complete native linkage inventory

2026-09-06 21:35 UTC. P3 remains open. Current object set: `local/compiler-spike/source-exit-manifest-v2-regression/active-objects.json`, SHA256 e5c5516e4703ac055f97128799b45bed91c3b90d235a67f6446973c3a698a8a6. All 386 objects repeat and contain 21,282 unique actual COFF function definitions for 21,181 recovered entries. No game-derived object has been linked or executed.

`whole-program-linkage-v11-source-repeat` reproduces v10-source-exits, including every raw llvm-nm log. There are 240 unresolved COFF names: 177 verified PLT stubs and 63 native support/library bindings. The new sourced-control-fault and block-transfer symbols replace the generic missing-block symbol. No unclassified direct logical symbol remains.

COFF symbols alone omit five tail-only import stubs reached through the block-transfer interface. The combined registry in source-exit-dispatch-v2-tail-imports/native-import-stubs.json contains 182 stubs: 67 with supplied compiled-export candidates and 115 external stubs. Raw type-7 relocations identify the five additions; Ghidra independently confirms their six-byte boundaries. Their identity does not establish native ABI/service behavior or binding.

All 551 structurally reachable source/request pairs independently decode as direct branches: 524 compiled-root pairs and 27 import-stub pairs. The runtime must check actual target equals requested target, source/target and module identities, and a validated compiled/native binding. Unknown targets fail with context. The older 4,366 missing-start records retain 4,178 after-contract, 165 compiled-target and 23 import-tail classifications; they are a separate measurement from emitted saved-IR sites and pairs.

Raw COFF and LLVM readobj in coff-constants-v4-source-exits agree on 35 duplicated constants / 90 definitions / 12 objects: matching read-only, relocation-free COMDAT selection-Any payloads. This resolves duplicate metadata compatibility, not the complete native link.

Next implement and validate the 63 support/library bindings, native fault/control behavior, bundled/native import binding and full linkage. Keep nounwind contracts explicit. Full source-exit evidence and remaining scope are in reports/source-exits.md and reports/source-exits-evidence.json. No native game boot or playable port exists.
