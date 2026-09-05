# P0 input validation and missing-data account

Recorded 2026-09-05. P0 passes for the corrected main-game development inputs; use effective-v2. DLC availability remains unverified and is outside the current demonstrated content scope.

The original packages were read only. Their SHA-256 values were computed once and recorded in reports/input-manifest.json. The effective executable is CUSA03173 update 01.09, SHA-256 d65f0b4f01d59166aed16f8604196d8b7dd805abbf0758b356e8f1354c9429f9. Both package SFOs identify EP9000-CUSA03173_00-BLOODBORNE0000EU; base APP_VER is 01.00 and update APP_VER is 01.09. This identifies the supplied build; it does not prove correctness of its extraction or DLC entitlement by itself.

Full base extraction produced 28,808 files. All 405 files from an independent update extraction match the reused update extraction by path, length and SHA-256. The previous selectively extracted base code also matches the full extraction. The effective base/update view contains 28,810 files, 31,428,130,448 bytes, and 405 update replacements. The union adds update-only sce_discmap_patch.plt and the effective public sce_sys/param.sfo metadata. See the full per-file provenance and hashes in local/game/view-manifest.json, local/game/base-hashes.jsonl and local/game/update-hashes.jsonl. This view uses hardlinks; editing an effective asset in place would also change its source extraction, so consumers must treat it as read only.

Reproducible extraction runs:

- 20260905-p0-extract-base-shared

- 20260905-p0-extract-update-repeat-netsha

- 20260905-p0-game-view

The earlier leaf proof was reproduced once in 20260905-p0-proof: 26 Python tests, 19 real leaf functions / 205,048 comparisons and 28 authored fixtures / 302,176 comparisons. It remains limited CPU evidence. It does not establish game boot, complete architectural equivalence, or a playable port.

Seven readable bundled libraries and their transitive imports are inventoried in reports/module-audit.json and private local/analysis/transitive-modules.json. The file sce_sys/about/right.sprx (16,025 bytes) has unsupported SELF header attributes for the existing parser; no needed-module reference to it was found in the main executable or seven parsed libraries. This is a documented unreadable input, not a demonstrated startup dependency.

The static import matcher leaves three main-executable names without candidates: sceNpNotifyPlusFeature, sceKernelTruncate and sceKernelReleaseFlexibleMemory. Bundled modules have additional unmatched textual names. Textual matching can miss runtime registration and does not establish semantic or ABI correctness. The pinned shadPS4 linker registers its libc-internal HLE fallback when firmware libraries are absent (src/core/linker.cpp, lines 80–90). The unmodified baseline progressed into game asset loading and graphics/audio initialization with only supplied game files; no missing proprietary firmware has been demonstrated as a startup blocker. Unresolved module_start/module_stop lookup messages and stubbed network/trophy calls remain recorded runtime issues, not universal success implementations in our AOT harness.

The supplied files include map/event/sound assets with m34, m35 and m36 identifiers and DLC title-menu assets. Both SFOs have USER_DEFINED_PARAM_1=13, while their additional-content service-ID fields are empty. No separate add-on package or verified local add-on entitlement has been supplied. The executable imports AppContent initialization, parameter and additional-content enumeration interfaces. The pinned baseline's AppContent implementation obtains application parameters from the SFO and enumerates additional-content SFOs under the user addcont directory. Asset presence and the European title ID therefore do not establish a local entitlement or prove access to The Old Hunters. Actual offline DLC access remains to be tested after startup and gameplay are established; no entitlement is fabricated.

Fresh separate portable profiles were created for normal and research runs. Empty-save backup manifests are in local/saves/backups. Existing global user saves were not touched. The first baseline run stopped at a migration prompt caused by missing home/1000, even on a new profile; subsequent profiles precreate empty home directories 1000–1003 using the source-confirmed initialization contract.

Hardware/tool inventory is reports/environment.md; official archive digests are reports/toolchain-downloads.json; current source and submodule pins are reports/dependency-lock.json. No PS4 comparison is available or required from the user. Remaining observations must use the plan's independent instruction, contract, data and runtime checks.

## Correction discovered during P1

The first view described above contained the full PFS tree and public param.sfo, but omitted other named system metadata outside PFS. That omission caused the baseline to report missing npbind.dat and a missing trophy communication ID. This was an extraction/view defect, not absent user data.

tools/package_metadata.py uses the already available PkgTool API to extract the named system metadata from both supplied packages twice, including encrypted npbind/nptitle through its existing entry-decryption implementation. All repeat results match. It checks the npbind header/entry count and gives update data precedence.

The corrected, separately created local/game/effective-v2 contains 28,840 files / 31,438,428,662 bytes, including 31 effective system-metadata files. The original executable hash is unchanged. Provenance is in local/game/view-v2-manifest.json and local/game/system-metadata/manifest.json; the public summary is reports/input-view-v2.json. The old view/captures remain unchanged for comparison.

With v2, the baseline finds the trophy communication ID and reaches offline character creation. It still reports that its configured 16-byte ReleaseTrophyKey is absent, so trophy archive extraction is unverified. That key is an optional trophy-data dependency for the observed route, not a missing compiler tool or a demonstrated startup blocker. Package-install license/key-table internals were not placed in the game view. DLC entitlement remains unverified.

P0 is accepted with these explicit data limitations. Do not use the superseded view for new baseline work.
