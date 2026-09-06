# Decision 0003: canonical x87 State and explicit image profiles

2026-09-06 13:16 UTC. P3 semantic integration decision; no native game boot or complete x87 implementation is approved by these tests.

Keep raw 80-bit payloads in `State.st` in logical ST order. Keep physical nonempty occupancy, TOP and control in the existing FXSAVE-shaped cache; synchronize split condition/exception flags. Reconstruct full two-bit tags from occupancy and payload classification when storing an environment. Rotate logical payloads on TOP imports while preserving their physical registers. Keep guest arithmetic and pointers in canonical State rather than relying on the host floating environment.

`native/semantics/x87_environment.h` implements pure 28-byte environment and 512-byte FXSAVE image operations. Pointer segments and image profile are explicit inputs. A profile states whether legacy selectors are zeroed, whether FXSAVE pointers are written only when ES is set, and which MXCSR mask is serialized. The Intel calibration profile is a hardware test configuration. The AMD conditional-pointer profile follows the primary manual but has no AMD hardware observation. Neither profile is selected from host CPUID implicitly.

Preserve the software-owned image tail at offsets 416 through 511. Guest last-pointer segment metadata must be carried explicitly when instruction selectors are integrated; do not substitute current host selectors. Treat host pointer upper-half loss as a limitation of the hardware oracle, with counted and precisely bounded observations. The native image retains canonical 64-bit pointers independently of that host loss.

The next selector layer must handle waiting exceptions before memory effects where required, validate the supported memory span/alignment, and distinguish unsupported mapping cases from architecturally established faults. Pure packing functions do not implement those boundaries. All relevant x87 memory conversions/arithmetic and MMX alias behavior must use the same canonical representation before the experimental module is accepted for startup.

Evidence: reports/x87-faults.md, reports/x87-fault-evidence.json, reports/x87-serializers.md and reports/x87-serializer-evidence.json. The accepted startup module remains v9-sqrt; v15 is the experimental stack/control module. P3's two rejected bodies and eight quarantines remain visible.
