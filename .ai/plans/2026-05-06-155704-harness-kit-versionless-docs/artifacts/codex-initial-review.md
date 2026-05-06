**Blocking Issues**

- [docs/harness-kit-lifecycle-design.md](/Users/alex.furrier/git_repositories/harness-toolkit/docs/harness-kit-lifecycle-design.md:490) still has a public “Migration strategy” section, plus “staged migration” frontmatter and a “Phase plan.” This keeps the page framed as a rollout/migration document instead of one current Harness Kit lifecycle. Related public ADR wording remains in [0008](/Users/alex.furrier/git_repositories/harness-toolkit/docs/decisions/0008-harness-kit-ledger-first-local-assistant.md:132) and [0009](/Users/alex.furrier/git_repositories/harness-toolkit/docs/decisions/0009-harness-kit-lifecycle-first-cli.md:141). That conflicts with the goal to avoid implying a migration guide.

- [src/harness_toolkit/kit/cli.py](/Users/alex.furrier/git_repositories/harness-toolkit/src/harness_toolkit/kit/cli.py:54) still exposes “Harness Kit 2” / “HK2” in user-facing CLI help. This is outside the docs-only diff, but it means the public surface still has version framing if users follow docs and explore `hk --help`.

**Non-Blocking**

- Command removal wording is accurate: `scripts/hk-dev attach`, `scripts/hk-dev legacy plan x`, and `scripts/hk-dev legacy sync-check` all fail as unknown commands. The docs’ “removed portable plan-artifact commands” wording is better than HK1/HK2 migration wording.

- Renamed docs/nav links look consistent. `uv run mkdocs build --strict` passed, with only the existing ignored `site/` output and an info note that `docs/AGENTS.md` is not in nav.

- `git diff --check` passed.

I did not modify source/docs files. The MkDocs build wrote ignored `site/` output; tracked/untracked status for the reviewed files remained unchanged.