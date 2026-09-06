# Initial exception RTTI dispatch

Updated 2026-09-06 18:01 UTC. One independently checked initial target is now recovered and compiled. P3 remains open; no native game boot or playable port exists.

The complete static census is **21,174 entries / 383 objects**, with all 18,444 initial constructors represented once, zero compiler rejections and five quarantines. The current active manifest is `local/compiler-spike/exception-rtti-evidence-audit-v1/active-objects.json` (SHA256 `eccf90da1fbac6bd85c628ffd78df93049e7d267930f9090f857a061a6084540`). It adds one 1,228-byte object to the previous complete 382-object set, preserving every prior compiler/semantic identity.

## Exact evidence

The supplied libc failure-report helper at 0x60750 loads its table pointer from RTTI object slot 0xbe2d0 and calls through table offset 0x10 at 0x60811. Both pointer words are initially zero and require ELF64 type-1 symbol relocations; interpreting the raw words as null targets would be wrong.

| Step | Symbol and addend | Initial result |
| --- | --- | --- |
| Object slot 0xbe2d0 | Defined data symbol 1316, byV+FWlAnB4, value 0xba9c0, addend 16 | Vtable address point 0xba9d0 |
| Method slot 0xba9e0 | Defined function symbol 415, XbEM58kMYFc, value 0x48f00, addend 0 | Method entry 0x48f00 |

Ghidra parses the copied raw symbol, string and relocation tables independently. Its input includes the object slot and method offset, but no expected symbol index, name, target, value or addend. A separate entry-driven SLEIGH decode checks the source load/call operands and the four-instruction target, sharing all 100 instructions across the two windows. The target is XOR EAX,EAX; CMP RDI,RDX; CMOVZ RAX,RSI; RET. Under normal SysV inputs it returns the object argument exactly when the two type-info pointers match, otherwise zero. The pinned symbol map names it __class_type_info::cast_to. Public [libcxxrt dynamic-cast code](https://raw.githubusercontent.com/libcxxrt/libcxxrt/master/src/dynamic_cast.cc) and [exception diagnostics](https://raw.githubusercontent.com/libcxxrt/libcxxrt/master/src/exception.cc) provide context, without proving the supplied library's complete source identity or runtime behavior.

The loader accepts only the checked proposal, unchanged code/table bytes, recorded symbol roles, addends and unique supplied definitions. Tests reject altered bytes, addends, undefined/wrong-role symbols, ambiguous definitions, wrong slots and wrong entry/site ownership. All 65 focused checks pass. The original unresolved indirect call is retained, alongside initial_symbol_dispatch_target_candidate and symbol_dispatch_binding_unvalidated records. Symbol interposition, loader binding, object/table mutation and the second object call at 0x6081f remain unknown. No conditional candidate is promoted into an unconditional return or termination summary.

## Recovery and compilation

`local/cfg/startup-recovery-v27-rtti-repeat` reproduces v26-rtti's database, compilation manifest, frontier and constructor order byte-for-byte. Database SHA256 `86a24fb090bae059aa3bc44b3b0bce64adc3c80ce33d8954172623912c5fa50d`; manifest SHA256 `bc5d2281380375974806d61992622ea6c1a8fdb9a91278639dbbde5c847ef2e9`. The exact delta consists of one new four-instruction entry and two candidate/binding edges in the existing helper. The other 21,177 entries are byte-identical as manifests. All prior unresolved-target counts and all five quarantines remain.

The sparse compiler builds the new entry twice with byte-identical input, roots, units, audit, bitcode and object files. It has no sparse missing path; it still declares native memory, flag and logical-return helpers. Successful object compilation is not native game execution or execution coverage. The complete-object audit verifies every current instruction-set hash, all issue-free manifests, all initial constructors and unique entry/root ownership across 383 objects.

## Reproduce and continue

Use tools/run_record.py with unique run IDs and fresh output directories. Run tools.exception_rtti_inventory, tools.ghidra_symbol_dispatch, tools.ghidra_byte_windows and tools.check_exception_rtti. Regenerate from the original startup-db-v1 seed with all previous evidence flags plus `--symbol-dispatch-evidence local/cfg/exception-rtti-checked-v2-provenance/checked.json`. tools.exception_rtti_delta creates the one-entry compile selection. Compile with tools.startup_batch_compile, v8 sparse lift and v31 semantics, then run tools.summarize_exception_rtti. Exact commands, source ZIPs and artifact hashes are recorded in the evidence JSON.

The libc throw/rethrow quarantines still require the subsequent what() target and exception-runtime work. The remaining main helper has a new source-comparison lead: [Lua 5.0 luaD_throw](https://www.lua.org/source/5.0/ldo.c.html) contains the same error-jump versus panic-callback/exit structure. Verify the supplied structure offsets and assignments before adopting that identification. A memory-indirect call alone does not prove a virtual method. Its mutable callback and restored context remain unresolved.

P1 baseline work is unchanged; no game CPU execution occurred. No user action is needed.
