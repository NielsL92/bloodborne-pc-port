# Experimental x87 stack and control recovery

Updated 2026-09-06 02:34 UTC. Paused at the user's request for PC shutdown. P3 remains open and the accepted startup semantics remain `build/extended-semantics-v9-sqrt`. No native game boot or gameplay exists.

The isolated integer implementation in `native/semantics/X87_STATE.cpp.inc` replaces sixteen selector bindings for FLD1/FLDZ, FNINIT, FLDCW/FNSTCW/FNSTSW, register FXCH/FSTP, FUCOMI/FUCOMIP and FWAIT. It preserves raw 80-bit payloads, models physical occupancy and logical TOP, synchronizes split status flags and avoids changing host floating controls. This is a partial experimental family: memory loads/stores, arithmetic, serializers and complete native faults remain unresolved. It must not be used for startup compilation yet.

`local/compiler-spike/x87-state-probe-v3` using the v11 experimental module matches all 11,520 cases of the original masked diagnostic. The original v2 result of 10,176 differing cases remains preserved. These are selected-field diagnostic comparisons, not execution coverage.

`local/compiler-spike/x87-stack-probe-v1` expands to 1,499,136 authored AOT/hardware cases across nineteen forms, every TOP and occupancy, all supported precision/rounding settings, status/flag presets, sixteen special 80-bit representations and all selected comparison operand pairs. It checks defined status, comparison flags, nonempty payloads, memory/return contracts, unaffected State bytes and host floating state. It finds 35,888 differences, all missing denormal-operand status in four FUCOMI/FUCOMIP forms (8,972 each). The other compared fields agree. The wrapper records successful characterization even when comparisons differ; inspect `differing_cases`, never infer semantic success from process exit alone.

The source now adds denormal status when an ordered comparison sees a nonzero exponent-zero operand. `build/extended-semantics-v12-x87-denormal` builds successfully but **has not been run through the expanded probe**. That is the exact next action. Preserve v11 and the failing expanded probe. Earlier v10 failed because the selector parser omitted lowercase characters in three selector names; the parser correction and all failure logs are retained.

The separate authored hardware experiment `local/compiler-spike/x87-environment-probe-v1` covers 2,097,152 full-tag imports (65,536 tag words, eight TOP values, four payload rotations). Every case agrees with importing occupancy and reconstructing nonempty tag classification from payloads; only 8,192 agree with preserving the literal full tag word. Occupancy, control, TOP and nonempty payload mapping agree in every case. This checks Intel host behavior, not AMD Jaguar or PS4 equivalence. Intel documents this empty/nonempty interpretation for FLDENV/FRSTOR/FXRSTOR and classification when storing tags. [Intel architecture manual, section 22.18.4](https://www.intel.la/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.pdf).

Remaining semantic work includes pending versus newly raised exceptions, unmasked fault transfer, all relevant arithmetic precision/rounding, memory conversion and environment serialization. Guest IP/DP/FOP behavior, reserved fields, undefined flags and empty payloads are excluded from current hardware comparisons. Check AMD-specific flags and special-value behavior against primary manuals before selecting the guest contract. The Intel comparison reference distinguishes quiet from signaling NaNs and unsupported encodings. [Intel instruction reference, volume 2A](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf).

Resume with a fresh run ID and output directory:

```text
.venv/Scripts/python.exe tools/run_record.py --id UNIQUE -- .venv/Scripts/python.exe -m tools.x87_stack_probe local/compiler-spike/NEW build/sparse-lift-v5/bb-sparse-lift.exe build/extended-semantics-v12-x87-denormal
```

All artifacts and source snapshots remain in the six runs listed under `latest_experimental_checkpoint` in `reports/x87-state-evidence.json`. The canonical recovery remains v22-cache-repeat: 21,178 entries / 874,266 instructions; 21,168 compiled entries, two x87 compiler rejections and eight quarantined manifests. All 18,444 initial constructors compile. No native link or game execution occurred. P1's independent route, profiler and audio crash investigations remain unchanged.
