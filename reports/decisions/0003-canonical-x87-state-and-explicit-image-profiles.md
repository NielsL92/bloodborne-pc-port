# Decision 0003: canonical x87 State and explicit image profiles

2026-09-06 13:16 UTC. P3 semantic integration decision; no native game boot or complete x87 implementation is approved by these tests.

Keep raw 80-bit payloads in `State.st` in logical ST order. Keep physical nonempty occupancy, TOP and control in the existing FXSAVE-shaped cache; synchronize split condition/exception flags. Reconstruct full two-bit tags from occupancy and payload classification when storing an environment. Rotate logical payloads on TOP imports while preserving their physical registers. Keep guest arithmetic and pointers in canonical State rather than relying on the host floating environment.

`native/semantics/x87_environment.h` implements pure 28-byte environment and 512-byte FXSAVE image operations. Pointer segments and image profile are explicit inputs. A profile states whether legacy selectors are zeroed, whether FXSAVE pointers are written only when ES is set, and which MXCSR mask is serialized. The Intel calibration profile is a hardware test configuration. The AMD conditional-pointer profile follows the primary manual but has no AMD hardware observation. Neither profile is selected from host CPUID implicitly.

Preserve the software-owned image tail at offsets 416 through 511. Guest last-pointer segment metadata must be carried explicitly when instruction selectors are integrated; do not substitute current host selectors. Treat host pointer upper-half loss as a limitation of the hardware oracle, with counted and precisely bounded observations. The native image retains canonical 64-bit pointers independently of that host loss.

The next selector layer must handle waiting exceptions before memory effects where required, validate the supported memory span/alignment, and distinguish unsupported mapping cases from architecturally established faults. Pure packing functions do not implement those boundaries. All relevant x87 memory conversions/arithmetic and MMX alias behavior must use the same canonical representation before the experimental module is accepted for startup.

Evidence: reports/x87-faults.md, reports/x87-fault-evidence.json, reports/x87-serializers.md and reports/x87-serializer-evidence.json. The accepted startup module remains v9-sqrt; v15 is the experimental stack/control module. P3's two rejected bodies and eight quarantines remain visible.

## Experimental profile extension — 2026-09-06

The same explicit policy service now covers producer metadata and comparison behavior. Bits 2/3 select FDP/FOP updates only on newly raised unmasked exceptions. Bit 4 preserves comparison C1 except stack underflow; clear selects unconditional C1 clearing. Bit 5 preserves OF/SF/AF; clear selects zeroing them. Existing image bits 0/1 and upper-32 MXCSR mask remain unchanged. FNINIT resets the external saved-selector metadata as well as canonical pointers/opcode.

These are explicit choices, not host-CPUID defaults. Reports/x87-metadata.md records Intel documentation versus two independent local C1 observations and AMD's documented auxiliary-flag preservation. Selected-policy deviations remain counted. No AMD Jaguar hardware equivalence or complete comparison exception profile is claimed. The extensions remain experimental and do not promote the startup module.

## Arithmetic control boundary — 2026-09-06

Experimental register add/subtract/multiply use ordinary native scoped numeric helpers and canonical stack state. Valid PC values 0/2/3 select 24/53/64-bit significands. PC=1 terminates through a distinct unsupported service before instruction effects, with existing pending exceptions taking priority. Local PC=1/3 agreement does not implicitly adopt a guest policy. Arithmetic unmasked overflow/underflow/precision result completion differs from memory stores; preserve the separately tested rules. MMX is absent from the current recovered graph and explicitly rejected by compiler v7 until shared-state behavior is validated. FSCALE and complete startup/runtime integration remain open; see reports/x87-arithmetic.md.

## Static integration — 2026-09-06 16:44 UTC

The exact 355-site x87 / five-site MXCSR catalog and complete-body checks support using v31-scale with compiler v8-selector-audit for a new static replacement object. It replaces five whole prior objects and adds the two formerly rejected entries; the current active manifest is in reports/x87-integration.md. Retained objects keep their own build identities. This updates static compilation acceptance only. Native floating-state profile selection, general runtime exception/control integration and AMD Jaguar execution equivalence remain unproved; P3 is still open because eight control boundaries are quarantined.
