# Lua panic-field startup recovery

2026-09-06 18:34 UTC. **P3 remains open; no native game boot or playable port exists.**

The current complete manifest is `local/compiler-spike/lua-panic-evidence-audit-v1/active-objects.json` (SHA256 `d6dfcad6be850c130aed3c9d0fa91512fa7051426c0c95bddebd340a42f0fbc3`): 21,176 entries / 384 objects, including every initial constructor exactly once. Five boundary quarantines remain. No game-derived object was linked or executed.

## Evidence and object roles

The publisher's Lua 5.0.2 archive is 190,442 bytes with SHA256 `a6c85d85f912e1c321723084389d63dee7660b81b8292452b190ea7190dd73bc`. The supplied binary contains a Lua 5.0.2 version marker at file offset 76,970,868. The public `luaD_throw` branches between a saved error context and a panic callback followed by exit. Main 0x210ad70 has the same inspected structure. Public source and checksum: https://www.lua.org/ftp/ . Local unmodified regular source files: `local/references/lua-5.0.2-v2-source/lua-5.0.2`, with per-file identity and MIT copyright retained.

Freestanding compilation of the unmodified headers, without linking or execution, gives:

| Layout | LP64 reference | Windows LLP64 reference | Supplied access |
| --- | ---: | ---: | ---: |
| `lua_State.l_G` | 0x20 | 0x20 | 0x20 |
| `lua_State.errorJmp` | 0x90 | 0x90 | 0x90 |
| `global_State.panic` | 0x50 | 0x40 | 0x50 |
| `sizeof(lua_State)` | 160 | 160 | allocator requests 192 |
| `sizeof(global_State)` | 288 | 272 | allocator requests 288 |

The supplied state has extensions at/beyond +0xa0, including allocator/context +0xa8. This rules out silently replacing its layout with the default public Windows structure. The comparison identifies an inspected prefix/source family; it does not establish complete type, configuration or library identity. No host jmp_buf definition was used or inferred.

At 0x210ad80 the throw helper loads `[RDI+0x20]`; at 0x210ad84 it calls `[RAX+0x50]`. Two actual constant stores to that global-state field identify possible callbacks:

| Assignment owner / store | Conditional role | Target / decoded body |
| --- | --- | --- |
| 0x2115080 / 0x21150fe | default global initialization | 0x21155e0, XOR EAX,EAX; RET |
| 0x20fbc50 / 0x20fbccf | game wrapper override after state creation | 0x2100e00, eight instructions; conditional call to already recovered 0x20e2550, then zero return |

The state creator stores its allocator at +0xa8 and passes initializer 0x2115080 in RSI to protected helper 0x210adb0. That helper preserves RSI in R14 and invokes it at 0x210ae13. These are concrete role witnesses under normal SysV behavior. The same runtime global object, initialization ordering and subsequent callback writes remain conditions, not proven alias or mutation closure. Other +0x50 stores belong to the Lua state base_ci field or wrapper fields and were not classified as panic assignments.

Ghidra independently decodes five owners and two target windows: 813 shared instructions, no byte/boundary disagreement, and one extra NOP after an existing stack-protector nonreturn annotation. No expected instruction list, callback target or no-return hint was supplied to SLEIGH. Metadata landing pads are additional roots for the five owner windows; the two new target windows remain bounded analysis regions, not standalone function-extent proofs.

## Reproducible recovery and compilation

`local/cfg/startup-recovery-v28-lua-panic` and `local/cfg/startup-recovery-v29-lua-panic-repeat` reproduce database, manifest, frontier and constructor order byte-for-byte. Database SHA256 `8e0b6733e75c69995e586d83d7a9d7bd3032cf6d9c587e76422864beac1a78f7`; manifest SHA256 `73a4d6eb9985b4cbd657dfd31669fb4860863e7536916b58bf5209159164bf89`. Exact streaming delta: 21,178 old entries unchanged, only main 0x210ad70 gains four candidate/binding edges, and two bodies / ten instructions are added. All original edges remain. Unknown indirect calls 9,044; indirect jumps 430; callback arguments 143; service obligations three; quarantines five.

Fresh lua-panic-compile-v1 and v2-repeat reproduce input, roots, units, audit, LLVM bitcode and Windows object. The new two-root object is 2,002 bytes, SHA256 `ee0e4f9c3effbd987c0146245720f805f01ef67817ee0832612aedebc9d3b6c0`. It has no sparse missing paths but still declares native memory/flags/return dispatch and a compiled dependency on main 0x20e2550. Successful compilation is static evidence only.

`tools/summarize_lua_panic.py` verifies every retained object's identity, every current instruction-set hash, unique compiled-root ownership, all constructor entries, the full frontier, run source snapshots and all repeated artifacts. Seventy-six focused checks include changed field roles, store registers, source/target bytes, target arithmetic, owner scope, retained unknown calls and retained ordinary fallthrough. Generic control derivation is unchanged.

Every experiment is recorded in local/runs with prefix `20260906-p3-`. Preserve the failed lua50-reference-v1 run: it rejected two convenience symlinks before source extraction. The corrected tool skips only those exact unneeded executable links and records their omission. Preserve lua-panic-checks-v1: a nonexistent test-module name caused a runner error after all 69 loaded checks passed. The corrected module list runs all 76 successfully.

## Continuation

Investigate the five remaining exception/nonlocal fence cases and callback-dependent control summaries without dropping target or runtime uncertainty. The source-supported panic callback is allowed to return; it is followed by exit. An unknown callback is still an execution obligation, even where a separate conditional no-ordinary-return summary may become supportable. Never substitute public Lua interpretation, emulator execution or original-game CPU execution for native recompilation. P1 observations remain separate and unchanged.
