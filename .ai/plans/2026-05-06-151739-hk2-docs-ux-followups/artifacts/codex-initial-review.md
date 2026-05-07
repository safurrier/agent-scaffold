**Blocking Issues**

- [README.md:132](<REPO_ROOT>/README.md:132) lists `hk work` as an inspect command, but `hk work` is only a command group. The actual inspection command is `hk work status`, and the promoted path is already `hk status`. An agent copying the table gets help text, not work state. Code: [cli.py:628](<REPO_ROOT>/src/harness_toolkit/kit/cli.py:628), [cli.py:651](<REPO_ROOT>/src/harness_toolkit/kit/cli.py:651).

- [README.md:142](<REPO_ROOT>/README.md:142) documents dangerous skips as `review|sync`, but HK2 also supports and readiness honors `validation`. That under-documents a real readiness escape hatch and contradicts the implemented check set. Code: [cli.py:1151](<REPO_ROOT>/src/harness_toolkit/kit/cli.py:1151), [policy.py:119](<REPO_ROOT>/src/harness_toolkit/kit/readiness/policy.py:119).

**Non-Blocking Suggestions**

- [README.md:126](<REPO_ROOT>/README.md:126) says the table is “the rest of the surface,” but it is not exhaustive (`hk instructions`, `hk init`, and subcommands are omitted). Consider wording it as “the common surface” or “the promoted/advanced surface” to avoid implying full command coverage.

- [docs/harness-kit-lifecycle-design.md:102](<REPO_ROOT>/docs/harness-kit-lifecycle-design.md:102) says “add review backend adapters.” That could be read as HK eventually running or dispatching reviews itself. Given the current HK2 model is shell-first and records externally run review evidence, I’d clarify this as “tool-callable review dispatch helpers” or “review prompt/backfill adapters,” preserving that HK records results rather than owning reviewer execution.

- [README.md:86](<REPO_ROOT>/README.md:86) still uses the heading “Workflow Modes,” but the new section is really about the agent-facing lifecycle mental model. A heading like “Harness Kit Agent Workflow” would fit the new framing better.

No file modifications made. I verified the command-surface concerns against `scripts/hk-dev --help`, `scripts/hk-dev work --help`, and `scripts/hk-dev dangerously-skip --help`.