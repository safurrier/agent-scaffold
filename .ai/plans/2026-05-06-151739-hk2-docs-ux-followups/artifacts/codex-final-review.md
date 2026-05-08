No blocking findings.

I reviewed the uncommitted docs changes in:

[README.md](<REPO_ROOT>/README.md:88)  
[AGENTS.md](<REPO_ROOT>/AGENTS.md:85)  
[docs/harness-kit-lifecycle-design.md](<REPO_ROOT>/docs/harness-kit-lifecycle-design.md:88)  
[docs/portable-workflow.md](<REPO_ROOT>/docs/portable-workflow.md:190)

I also spot-checked the documented commands against `scripts/hk-dev --help`, including `artifact attach`, `export`, `dangerously-skip`, `decide`, `plan`, and `profile`. The new agent-facing framing is consistent with the repo guidance, and I did not find command examples that would block the docs.

No files were modified.