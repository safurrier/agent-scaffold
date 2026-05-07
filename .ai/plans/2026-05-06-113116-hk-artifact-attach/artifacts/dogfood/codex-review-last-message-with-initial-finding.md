The repository quality gate fails because existing e2e tests still reject any `attach` text in root help. The implementation may be otherwise sound, but the current changes do not pass the required check suite.

Review comment:

- [P1] Keep the root help legacy check green — <REPO_ROOT>/src/harness_toolkit/kit/cli.py:61-61
  With this help text, `hk --help` now contains the word `attach`, so `mise run check` fails in the existing e2e tests that assert the removed legacy top-level `hk attach` surface is absent (`tests/e2e/test_hk2_cli_parity.py` and `tests/e2e/test_harness_kit_rollout.py`). Please either adjust the remaining legacy-surface assertions to check for the command specifically, as the unit test does, or avoid this wording in root help.