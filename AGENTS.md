# Repository collaboration restrictions

UNDER NO CIRCUMSTANCES MAY ANYTHING BE PUSHED TO lud-berthe/Bloodborne-Recompiled's main BRANCH. NEVER.

The owner has authorized work only on our fresh branch: codex/integration-validation.
All work in that repository must remain on that branch. Every pre-existing owner branch, including main and codex/g2a-checkpoint, is read-only. Never commit, merge, rebase, reset, delete, force-update, or push to those branches. Never modify them through GitHub APIs, PR merges, or another checkout. Reading upstream refs/source for comparison is permitted.

Before every mutation, confirm the repository and current branch. Stop if the branch is not codex/integration-validation. Do not reuse another contributor's branch or bypass installed hooks. Keep push.default=nothing and the upstream push URL disabled until the user explicitly requests publishing our contribution branch. Such publication must target only refs/heads/codex/integration-validation and must never update any other ref.

Implementation direction confirmed by the user: use the other project's direct x86-64 runtime as the product foundation; selectively port our save-file-sharing correction, input verification, run recording, and missing regression tests. Preserve this project's Remill/AOT research and private artifacts. Do not resume its paused startup expansion as part of the integration task.

Game inputs, generated code/shaders, captures, saves, binaries, and dependency checkouts remain private and untracked. Treat local/game/effective-v2 as read-only because it contains hardlinks. Never edit original game views or seed saves in place.

Use `Timmy` as the hunter name in game tests, as requested by the user.
