# Decision 0001: do not integrate the current lifted state representation broadly

Date: 2026-09-05. Status: P2 gate failed; candidate retained for a bounded redesign.

Windows Remill/LLVM objects and ten real root contracts work under their tested conditions. A CMPSS state mismatch was isolated, corrected and retested. The two optimized kernel families remain approximately 2.0-4.6x slower after a concrete ordinary-memory lowering alternative. This fails the plan's performance warning gate before broad integration.

Static reassembly preserves near-original speed in the bounded comparison but is a different approach and has not been adopted as the deliverable. Its narrower scalar-result contract is not a replacement for the full-state lifted tests.

Continue only with a measured mitigation such as verified state/flag promotion, preserving defined effects and explicit callback/nonlocal boundaries. Do not start P3/P4 broad expansion until P2's performance and critical-runtime requirements pass. P1 baseline investigation can continue independently.

Evidence and limits: ../compiler-spike.md. Baseline: ../baseline.md. Current task continuation: ../../HANDOFF.md.
