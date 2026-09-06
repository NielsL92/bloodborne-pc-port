# x87 state blockers

Updated 2026-09-06 00:36 UTC. P3 remains open; no native game boot exists.

The two remaining compiler rejections are libc 0x30430 (FNSTENV/FLDENV) and 0x53cd0 (FXSAVE). Adding their serializers to the current State would conceal existing state errors. The authored probe in `local/compiler-spike/x87-state-probe-v2` compares ten short sequences over all eight TOP values, four occupancy patterns, three precision modes, four rounding modes and three status presets. Of 11,520 cases, 10,176 differ in at least one selected defined field. These are deliberately diagnostic inputs, not an estimate of game failure frequency.

Concrete counterexamples:

- FLD1 from an empty stack with TOP zero changes hardware TOP to seven and the abridged tag to 0x80. AOT changes TOP but leaves the tag zero. Popping likewise fails to clear the physical tag.
- A full stack followed by FLD1 produces hardware masked stack-overflow status and an indefinite result. The pinned implementation pushes a normal one without the matching exception state.
- FLDCW with double or extended precision stores single precision in State. FNSTCW also overwrites State precision and reads rounding from a linked host helper instead of faithfully storing the guest control word.
- FNINIT uses the overlapping FSAVE representation while other semantics use FXSAVE. The authored regression shows stale logical status and a cleared guest MXCSR. FNINIT is absent from the recovered startup instruction census; this is a source regression, not an observed startup path.
- The probe's linked rounding helper changes host floating controls when called by the existing semantics. This is an explicit runtime isolation obligation; host-control counts depend on that authored helper.

The original Remill sources and all semantic modules remain unchanged. The first probe failed to link because the fixture lacked `__remill_fpu_exception_test`; v2 adds the exact host-status reader. Both runs and source ZIPs are preserved. A successful probe wrapper means the counterexample experiment completed, not that x87 semantics passed.

`reports/x87-state-evidence.json` and `local/compiler-spike/x87-gap-inventory-v1/sites.json` tie the evidence to 355 recovered x87 instruction sites owned by twelve entries. This inventory is static ownership, not execution coverage or a claim that all 355 sites are individually incorrect. The two rejected bodies already have the all-48 independent Ghidra instruction comparison; no instruction boundaries changed here.

The selected comparisons cover tag occupancy, control, defined status bits, memory words, guest MXCSR and nonempty 80-bit register payloads. All exceptions are masked. Undefined condition flags, reserved bytes, host instruction/data pointers and complete State are excluded. Exact unmasked guest faults, arbitrary full-tag imports, arithmetic rounding/precision, and AMD-specific pointer behavior need separate checks.

The architecture requires one canonical x87 register/tag/status/control representation, synchronized split flags, correct stack exceptions, and native waiting/fault transfer before accepting environment serialization. Runtime work must preserve guest precision without leaking host state. The unchanged compiler census is 21,150 compiled entries, two rejected entries and eight quarantined manifests. Indirect/callback closure is independent work that can continue while this semantic gate stays open.

Reproduce through `tools/run_record.py` with fresh outputs:

- `-m tools.x87_state_probe local/compiler-spike/NEW build/sparse-lift-v5/bb-sparse-lift.exe build/extended-semantics-v9-sqrt`
- `-m tools.x87_gap_inventory local/compiler-spike/NEW`

The probe design is checked against the Intel manual's FLD/FLDCW, FNINIT, FNSTCW, FNSTENV, FXSAVE and stack exception descriptions. [Intel instruction reference, volume 2A](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf).
