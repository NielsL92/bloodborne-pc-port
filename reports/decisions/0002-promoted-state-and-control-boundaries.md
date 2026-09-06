# Decision 0002: promoted State and explicit control boundaries

2026-09-05. Supersedes the stop-expansion decision in 0001 for P3 analysis only.

Continue with Remill/LLVM. State promotion on the existing full-state contracts demonstrates mitigation of repeated register/flag/PC stores; representative longer kernels are below the approximate 2x warning threshold. Preserve the one-element warning and all previous failed results.

The service callback/nonlocal protocol, thread-local State/TLS, serialized locked operation, MFENCE publication fixture, and real five-way jump table now have bounded demonstrations with original code pages non-executable. Proceed to a provenance-aware P3 control-flow/dependency database.

Do not interpret this as authorization to execute unrecovered game targets through original bytes, or as a complete runtime. Unknown targets fail with diagnostics. Memory lowering and promotion retain their explicit contracts; recoverable asynchronous faults, MMIO, arbitrary guest mapping, and complete service coverage must be resolved before supported native gameplay.

The static-reassembly comparison remains separate and is not the endpoint. The shadPS4 file-sharing correction is a measured baseline/runtime bug fix, not native recompilation.

Service-site continuation (2026-09-06 17:41 UTC): three exact module/entry/call-site contracts now remove ordinary fallthrough conditionally while adding unresolved native service-control obligations. The abort rule additionally requires its independently checked constant arguments and entry path. Generic debug-service calls retain their return path. Five exception/nonlocal quarantines and all unknown callback/indirect targets remain. These annotations and 21,173 compiled entries are static evidence; the native runtime and P3 gate remain open. See reports/startup-services.md.

Lua callback continuation (2026-09-06 18:34 UTC): independently checked source/layout and constant-store evidence adds two conditional panic-field target dependencies. The supplied Lua state has a compatible inspected LP64 prefix plus custom extensions; a default Windows public Lua layout cannot replace it. The unknown call, state/global alias, callback mutation and nonlocal destinations remain explicit. No public interpreter or game CPU execution was introduced. See reports/lua-panic.md.

Conditional ending continuation (2026-09-06 18:55 UTC): a separate, independently checked ordinary-call model covers three exact unknown CALL sites and proves conditional paths through three helpers. It is applied only at five disputed ending sites and adds five unresolved native continuation records. Generic unknown-call rejection remains strict. All 21,181 current entries compile, but native callbacks/nonlocal transfer, full linkage and exit handling remain open; P3 has not passed. See reports/conditional-control.md.
