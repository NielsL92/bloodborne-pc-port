# Experimental x87 image instruction bindings

2026-09-06 13:36 UTC. Four image selectors now run as authored AOT code in experimental v18: FNSTENV (28 bytes), FLDENV (28 bytes), FXSAVE and FXSAVE64. They pass 557,864 cases against hardware images and explicit image-profile rules. Accepted startup semantics remain v9-sqrt; the two rejected libc entries are not promoted, and P3 remains open.

The selectors use the canonical raw stack/image helpers from decision 0003. FLDENV checks pending x87 exceptions before any memory or profile service. FNSTENV and FXSAVE are non-waiting. A runtime span check validates the fixture's fully mapped RAM and FXSAVE alignment; profile and last-pointer segments are explicit services. FXSAVE emits only written bytes, leaving its software tail and AMD's conditionally omitted pointer fields untouched without reading the destination. FLDCW also normalizes every reserved control-word bit.

The fixture compares the entire State outside independently observed architectural changes, all 640 surrounding memory bytes, logical return/fault PC, flags, host floating state, pending masks, and exact memory/profile/metadata service counts. It covers all TOPs, varied occupancy and payload classes, every exception-mask/sticky-state combination, all 65,536 raw tag words, every FLDENV/FLDCW control word, unaligned 28-byte environments and every nonzero alignment offset within 16 bytes for FXSAVE. Hardware and native paths agree on 161,640 faults. Four additional native-only cases verify that a pending exception precedes an intentionally unsupported mapping; 24 cases diagnose an unsupported partial span. These do not claim PS4 page-fault semantics or general Windows guest unwinding.

Intel hardware supplies the ordinary image and State oracle. The AMD profile's conditional pointer writes and explicit selectors follow the primary manual and are checked as specified byte differences, with no AMD execution claim. The binding matrix uses 32-bit last-pointer values to avoid the separately isolated host upper-pointer preservation limit. The pure helper regression still checks full-width pointers: 5,242,880 checks pass in v4-inline, with zero host truncations in that run. Previous truncations and their independent delayed reproduction remain retained in reports/x87-serializers.md.

Existing masked-stack and deferred-fault regressions also pass against v18: 1,499,136 and 720,896 cases. New experiments are not timing measurements; the three independent regressions ran concurrently. The IR retains explicit runtime services and no host floating-environment helper calls in these authored image roots.

Two failures are preserved. The v16 semantic build could not include cstring under the pinned freestanding recipe; compiler memory builtins fixed that header dependency. The v17 prepare run decoded all eight authored sequences but produced an invalid internal full_tags declaration when only compiled roots moved into the output module. Mandatory inlining keeps the pure helper in the compiled roots; the unchanged sparse driver verifies v18 successfully. No invalid IR was accepted.

Reproduce with tools/run_record.py and fresh output directories:

- Build tools.build_extended_semantics with BMI, SHUFFLE, BLEND, RSQRT, PACKED, TRANSFER, MINMAX, ROUND, SQRT, X87_STATE and X87_ENV, in that order.
- Run tools.x87_image_experiment OUT build/sparse-lift-v5/bb-sparse-lift.exe build/extended-semantics-v18-x87-images.
- Run tools.x87_stack_probe, tools.x87_fault_probe and tools.x87_serializer_probe as recorded in their run manifests.
- Run tools.summarize_x87_images OUT to audit source snapshots, binary identities, exact counters, preserved failures and the accepted module.

Evidence is reports/x87-image-evidence.json. Current closure remains 21,178 entries / 874,266 instructions; 21,168 compiled entries / 384 objects; two x87 rejections and eight quarantines. All 18,444 initial constructor entries compile, without an execution-coverage claim. No game bytes ran here.

Next: fix guest LDMXCSR/STMXCSR isolation and reserved-bit faults, integrate x87 memory conversions/arithmetic and MMX aliasing with canonical State, and continue native control/service closure. Other x87 producers still need to update pointer metadata. Image operations assume stable fully mapped RAM; unsupported mappings and architectural partial writes need separate contracts. P1 route, profiler overhead and opening audio crash work remain distinct and unchanged.
