# Repository collaboration restrictions

UNDER NO CIRCUMSTANCES MAY ANYTHING BE PUSHED TO lud-berthe/Bloodborne-Recompiled's main BRANCH. NEVER.

The user explicitly designated `Uptownfrog` as the only permanent branch for all current and future work on 2026-09-08, replacing the old contribution branch rule.
All work in that repository must remain on that branch. Every pre-existing owner branch, including main and codex/g2a-checkpoint, is read-only. Never commit, merge, rebase, reset, delete, force-update, or push to those branches. Never modify them through GitHub APIs, PR merges, or another checkout. Reading upstream refs/source for comparison is permitted.

Before every mutation, confirm the repository and current branch. Stop if the branch is not Uptownfrog. Do not reuse another contributor's branch or bypass installed hooks. Keep push.default=nothing and the installed branch-protection hooks enabled. The user explicitly authorized publication to lud-berthe/Bloodborne-Recompiled on 2026-09-08. Publication must use an exact refspec targeting only refs/heads/Uptownfrog and must never update any other ref. Do not push this donor repository without a separate explicit request.

Implementation direction confirmed by the user: use the other project's direct x86-64 runtime as the product foundation; selectively port our save-file-sharing correction, input verification, run recording, and missing regression tests. Preserve this project's Remill/AOT research and private artifacts. Do not resume its paused startup expansion as part of the integration task.

Game inputs, generated code/shaders, captures, saves, binaries, and dependency checkouts remain private and untracked. Treat local/game/effective-v2 as read-only because it contains hardlinks. Never edit original game views or seed saves in place.

Use `Timmy` as the hunter name in game tests, as requested by the user.


## Experiment memory

Record unsuccessful and inconclusive experiments as well as fixes. Before repeating
a gray-screen experiment, read the recipient's
`docs/checkpoints/gray-screen-experiments.md` and its linked detailed checkpoint.
Record the hypothesis, exact tested revision/run, observation, conclusion and the
new evidence required to revisit it. A capture that missed the relevant interval
is inconclusive, not evidence that the suspected operation is absent. Keep private
run artifacts ignored. Update the index and handoff after each meaningful result.

## This repository (NielsL92/bloodborne-pc-port)

User decision on 2026-10-06: this donor repository keeps all work on `master`. It has no `Uptownfrog` branch. The `Uptownfrog` rule above applies only to lud-berthe/Bloodborne-Recompiled. Commit with the GitHub noreply address that is already set in this repository's local git config, never a private email address. Push only on an explicit user request.
