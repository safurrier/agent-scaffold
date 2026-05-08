# Dogfood profile config

```toml
version = 1
default_profile = "generic"

[[targets]]
name = "dread"
path = "/tmp/hk-profile-config-dogfood/dread"
profile = "dread"

[[targets]]
name = "foreman"
path = "/tmp/hk-profile-config-dogfood/foreman"
profile = "foreman"

[profiles.dread]
title = "Dread"
summary = "Python Click CLI for reading <REDACTED_ORG> data."
target_hint = "/tmp/hk-profile-config-dogfood/dread"
instructions = """
Use focused pytest while iterating.
Use ruff on changed Python files before handoff.
For message formatting changes, inspect src/dread/formatting.py and tests/test_formatting.py.
For review, use Codex via `codex review --uncommitted` when available, then record `hk review add --backend codex`.
"""

[[profiles.dread.checks]]
name = "formatting-tests"
purpose = "Run focused message formatting tests."
command_template = "uv run pytest tests/test_formatting.py -q"
run_from = "repo-root"
notes = ["Use for formatting helper changes."]

[[profiles.dread.checks]]
name = "lint-changed"
purpose = "Lint dread source and tests."
command_template = "uv run ruff check src/ tests/"
run_from = "repo-root"

[[profiles.dread.reviews]]
name = "codex-core"
purpose = "Codex review for correctness and test adequacy."
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt_file = "prompts/codex-core-review.md"

[profiles.foreman]
title = "Foreman"
summary = "Rust CLI/TUI project."
target_hint = "/tmp/hk-profile-config-dogfood/foreman"
instructions = """
Use focused cargo tests while iterating.
Use cargo fmt --check before handoff.
For CLI config behavior, inspect tests/cli_config.rs first.
For review, use Codex via `codex review --uncommitted` when available, then record `hk review add --backend codex`.
"""

[[profiles.foreman.checks]]
name = "cli-config-tests"
purpose = "Run Foreman CLI config tests."
command_template = "cargo test --test cli_config"
run_from = "repo-root"
notes = ["Use for CLI/config behavior changes."]

[[profiles.foreman.checks]]
name = "format"
purpose = "Check Rust formatting."
command_template = "cargo fmt --check"
run_from = "repo-root"

[[profiles.foreman.reviews]]
name = "codex-core"
purpose = "Codex review for correctness and test adequacy."
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt_file = "prompts/codex-core-review.md"
```
