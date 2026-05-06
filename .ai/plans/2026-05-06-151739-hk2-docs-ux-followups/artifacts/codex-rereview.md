**Blocking Issues**
- [README.md](/Users/alex.furrier/git_repositories/harness-toolkit/README.md:132): The command index lists `hk start` as a common command, but current CLI behavior requires a slug. `scripts/hk-dev start` fails with `parameter "--slug" requires an argument`. This should be `hk start <slug> --plan "..."`, or split “start work” from “inspect active work.”

- [docs/harness-kit-2-design.md](/Users/alex.furrier/git_repositories/harness-toolkit/docs/harness-kit-2-design.md:102): The backlog says “add review prompt/backfill helpers,” but `hk review prompt` already exists and is promoted in the README. This reads like `review prompt` is future work. Wording should narrow this to “review backfill helpers” or “review prompt dispatch/backfill helpers.”

**Non-Blocking**
- [README.md](/Users/alex.furrier/git_repositories/harness-toolkit/README.md:138): `hk review add ...` is technically incomplete because the command requires `--backend`, `--reviewer`, `--rubric`, and `--summary`. The ellipsis makes it less severe, but for an agent-facing command index, a concrete minimal shape would reduce failed attempts.

I did not modify files. I verified the relevant command behavior with `scripts/hk-dev --help` and focused command help.