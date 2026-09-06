# P3 numeric x87 stores and completion boundaries

Updated 2026-09-06 15:14 UTC. Experimental v29-store-priority / compiler v6 passes 6,858,428 checks: 6,334,140 authored instruction cases plus 524,288 concurrent numeric-scope checks. There are 1,030,916 matched hardware faults, 30 extra native pending-before-unsupported cases and 30 separate unsupported mappings. P3 remains open. No native game boot or playable port exists; accepted compilation remains 21,168 entries with two rejections and eight quarantines.

## Native conversion and instruction effects

Seven selectors now have experimental checked semantics: FST/FSTP single/double stores and FISTTP signed 16/32/64-bit truncating stores. Five ordinary native numerical entrypoints return destination bits, IEEE flags, magnitude-rounding direction and an extra tiny-result fact. Each call saves/restores all four SoftFloat thread-local controls. The 16-byte result ABI and its field offsets are checked independently.

Unsupported extended encodings are detected before entering the library. Pseudodenormals are normalized explicitly. Integer overflow produces the format's indefinite value and invalid flag; it does not retain a precision flag from an intermediate wider conversion. Floating-store C1 reflects magnitude rounding, including negative values; integer truncation clears C1. Guest precision control does not change these destination-format conversions.

Instruction semantics first check a pending x87 exception and the exact writable span. Stack underflow takes priority over numerical conversion. Newly raised unmasked invalid, overflow or underflow suppress the write and optional pop. Unmasked overflow/underflow also suppress newly generated precision flags. Unmasked precision still completes the store and optional pop, with a later waiting instruction observing the pending exception. This behavior is checked independently before a subsequent wait. AMD's FST description explicitly says unmasked overflow prevents the store. [AMD instruction reference](https://docs.amd.com/api/khub/documents/w13cmcpL4f9MCT4WPN6eDg/content).

## Failed gates and boundary recovery

The first 5,316,668-case matrix passed, but dense rounding boundaries exposed 1,120 differences. An unrounded source-exponent threshold treated some values as underflow even when hardware completed their store near the normal/subnormal boundary. Changing the extra tiny fact to describe the rounded destination reduced differences to 288. Those remaining cases required unmasked library-reported underflow to suppress precision flags too. The final instruction combines the numeric UE flag with the extra nonzero-source/rounded-tiny fact; an exponent threshold alone was disproved.

The independent hardware probe has preserved 64,512 initial observations and 78,848 after adding exact boundary inputs. It uses authored store instructions with FXRSTOR input setup, followed by a nonwaiting state save. It uses no Remill, SoftFloat, AOT or SEH in the comparison path. Exact subnormal destinations can raise unmasked underflow without inexactness, while values rounding into the normal range require the more precise decision above. These remain observations on this Intel CPU, not proof of AMD Jaguar behavior.

An intermediate build invocation accidentally listed SQRT twice and omitted the x87 extension tail. Duplicate definitions rejected compilation. The fresh v29 build uses the complete extension list. Every failed directory and exact command remains retained.

## Final checks and continuation

The final matrix covers all TOP/occupancy patterns, exception masks/stickies, two explicit pointer/opcode profiles, raw special/unsupported values, integer limits, random encodings, dense single/double rounding boundaries, targeted finite random inputs, waiting suffixes and a two-store sequence. Full native State, raw stack payloads, memory, defined flags/status, service calls, logical pointers and fault/return behavior are checked. Undefined C0/C2/C3 are excluded. Hardware pointer comparisons retain the previously documented low-32 isolation limit.

Fresh v5/v6 outputs reproduce the function bitcode/object, native numeric helper object and raw results byte-for-byte without normalization. The expanded load regression also passes 1,876,028 cases. No performance conclusion is drawn from these correctness runs.

Use fresh paths and `tools/run_record.py`: `tools.x87_store_experiment OUT build/sparse-lift-v6-x87-opcode/bb-sparse-lift.exe build/extended-semantics-v29-store-priority build/softfloat-v2-repeat/softfloat.lib`, `tools.x87_store_probe OUT`, and `tools.summarize_x87_stores OUT`. Reports/x87-stores-evidence.json preserves exact identities, source archives, results and retained failures.

Next: arithmetic, FSCALE and MMX coherence, then native import/callback/exception/control closure. The accepted startup compiler/semantics stay v5 / v9-sqrt; experiments have not been silently promoted. No new P1 baseline run occurred; route, profiling and audio work remain independent.
