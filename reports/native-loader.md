# P4 module loading plan

Private loading update (2026-09-06 23:55 UTC): reports/native-load.md records repeated native NX allocation, resolved relocation application and independent full unguarded-byte validation. Thirty-seven unresolved slots remain guarded. No game-derived CPU execution has occurred.


Current generation (2026-09-06 23:42 UTC): see reports/native-memory-sources.md. Active objects are native-memory-manifest-v1; current registry is registry-v7-memory-repeat, link is link-v9-memory-repeat and loader plan is loader-plan-v8-memory. Complete authored/source/LLVM/link checks pass; native game loading/execution has not occurred.


2026-09-06 22:51 UTC. P3's compilation/explicit-handling gate passed at commit 40f9a28. P4 is open. No game-derived CPU function has executed and there is no native boot or playable port.

The loader plan independently rechecks the eight supplied module hashes and copies their sixteen loadable segment byte streams into fresh local outputs. It plans 97,517,568 logical mapped bytes: 92,463,404 initial bytes and 5,054,164 zero bytes including BSS/alignment padding. Code is classified read-only/NX; writable data stays writable. The 238,609 relocation destinations fit declared data spans, with no duplicate destination and no code-segment relocation. Actual native allocation/loading has not been implemented yet. The plan never changes an original or hardlinked file.

All 18,444 ordered initial constructor slots match their relative relocations exactly, and the table is writable. Actual compiled startup must read that table; the initial snapshot is not a replacement initialization loop. All eight TLS headers are retained with explicit registry-order module IDs; three have nonempty images (main 1,872 bytes, Fios2 64 bytes, libc 1,184 bytes including 544 initialized bytes). Per-thread placement and seventeen symbol-bearing DTPMOD64 references remain unresolved.

Current plan local/runtime/loader-plan-v5-repeat reproduces v4-weak byte-for-byte for 25 artifacts, including all segment files and the complete relocation ledger. It classifies 233,350 relative relocations, 4,379 conditional static symbol bindings, 116 existing native gateway references and twelve checked absent weak callbacks. Static symbol resolution checks matching library and module versions; there are no version disputes for the resolved supplied bindings. This retains the fixed module-set/interposition assumption.

The initial v1/v2 plan exposed 764 unresolved relocations. V3 additionally checked module versions without changing output. The twelve absent weak module_start/module_stop bindings now use the ELF weak-zero rule, after exact raw symbol/relocation checks and independent Ghidra decoding of all twelve six-byte PLT stubs. [ELF symbol-binding specification](https://gabi.xinuos.com/elf/05-symtab.html). This applies only to those checked weak bindings in the supplied module set. No strong import is zeroed and no service returns universal success. Evidence: loader-weak-v3-source-identity and local/cfg/ghidra-loader-weak-v1.

Remaining: 752 unresolved relocations, comprising 715 function-binding references, twenty strong data references and seventeen TLS module references. No unresolved value is guessed. Aerolib/reference-source identities for the strong data imports are __stack_chk_guard, __progname, Need_sceLibcInternal, _Stdout, _Stderr, _FInf and _FNan. These names are leads, not complete data-layout or behavior contracts. In particular, the shadPS4 dummy guard value and host FILE pointers are not native guest-layout implementations.

The next work assigns canonical native function identities across repeated imports, retaining explicit unimplemented-service stops. Using a module-local PLT address for every imported function pointer can give the same external function different pointer values across modules, so the complete loader must normalize these bindings. Then resolve and test strong-data/TLS contracts, validate native private loading, and construct the actual entry stack/arguments. Module initialization, callbacks, real services, FP profile selection and guest exception/nonlocal recovery remain P4 obligations. P1 baseline work is unchanged.

Reproduce with tools/run_record.py and fresh outputs:

- tools.check_loader_weak local/runtime/registry-v3-repeat OUT --ghidra local/cfg/ghidra-loader-weak-v1
- tools.native_loader_plan local/runtime/registry-v3-repeat local/cfg/startup-v1/roots.json OUT --weak-bindings local/runtime/loader-weak-v3-source-identity
- tools.summarize_loader_plan OUT (pins this checkpoint's repeated runs)
