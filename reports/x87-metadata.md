# P3 x87 metadata and explicit comparison policies

Updated 2026-09-06 14:53 UTC. Experimental v26-compare-policy / compiler v6 passes 6,029,312 selected-contract cases and 1,379,648 matched pending faults. These counts do not claim universal hardware equivalence: 232,640 C1-policy deviations and 517,208 auxiliary-flag-policy deviations from this Intel host are separately retained. P3 remains open, with 21,168 accepted compiled entries, two rejections and eight quarantines. No native game boot or playable port exists.

## Unified instruction metadata

The checked helper now serves constants, exchange, register pop, unordered integer-flag comparison, raw transfer/sign/conditional and narrow loads. It obtains an explicit policy, commits logical last-PC/opcode/data-pointer state and reports exact decoded-PC metadata. Newly raised unmasked exceptions are determined before deciding conditional FOP/FDP updates. FNINIT clears pointers/opcode and resets external segment metadata to zero. Compound initialization, push, compare, exchange, pop and waiting sequences exercise service ordering and deferred exceptions.

The metadata fixture checks both pointer/opcode update policies crossed with all four comparison-policy combinations. Defined status/flags, raw stack payloads, memory, return/fault PC, metadata calls, selector resets and host FP isolation are checked. Ordinary stack operations have undefined C0/C2/C3 excluded; comparison preservation and FNINIT reset are checked explicitly. Full canonical pointers remain checked separately from the established low-32 hardware pointer limit.

## Investigated comparison disagreement

The initial v25 run had 116,320 differences, all C1-related in FUCOMI/FUCOMIP cases. Pointer/opcode behavior already agreed. Earlier stack/fault fixtures initialized C1 to zero, so they did not expose this disagreement.

An independent 131,072-case hardware probe uses FNINIT/FLD80 and a local 28-byte environment image to select C1 independently, then reads flags immediately after FCOMI/FCOMIP/FUCOMI/FUCOMIP. There is no Remill, AOT, FXRSTOR-imported guest setup or SEH comparison path. All 65,536 empty-stack cases clear C1; 32,768 occupied-stack cases with input C1=1 preserve it, including masked/unmasked numeric exceptions. The other occupied cases start with C1=0.

Intel's instruction reference specifies C1 clearing, which conflicts with both local hardware experiments. [Intel reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf). AMD's application manual lists only ZF/PF/CF as modified by these comparisons, while this Intel host clears OF/SF/AF too. [AMD application manual, section 6.5](https://docs.amd.com/api/khub/documents/sfvvekC9mDflu6vd3R0NXA/content).

These differences now have explicit policy bits. Bit 4 preserves comparison C1 outside a stack fault; clear selects unconditional C1 clearing. Bit 5 preserves OF/SF/AF; clear selects zeroing them. No host CPUID or documentation assumption silently selects the guest policy. These choices remain separate from the previously documented uncertainty about unmasked-invalid comparison flags on AMD Jaguar. Policy deviations are counted, not ignored or presented as hardware agreement.

## Retained checks and next work

A fixture-local duplicate declaration caused the v2 build failure; no execution occurred. The corrected v3 policy matrix passes, and v4 additionally checks documented C0/C2/C3 preservation and initialization reset. All failed outputs remain intact. The stack, pending-fault, narrower-load and image regressions pass 1,499,136 / 720,896 / 1,613,884 / 557,864 cases respectively. Their original scope remains distinct from the new metadata fixture.

Use fresh outputs with `tools/run_record.py`: `tools.x87_metadata_experiment OUT build/sparse-lift-v6-x87-opcode/bb-sparse-lift.exe build/extended-semantics-v26-compare-policy`, `tools.x87_compare_c1_probe OUT`, then `tools.summarize_x87_metadata OUT`. Run manifests and `reports/x87-metadata-evidence.json` preserve sources, hashes, exact argv and results.

Next implement checked numeric stores/arithmetic/FSCALE and MMX coherence, then complete native import/callback/exception/control closure. Accepted startup artifacts remain v5 / v9-sqrt; the experimental modules are not silently promoted. P1 route/profiling/audio work remains unchanged.
