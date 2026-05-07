# Worker Report

## Changed

- Added `src/adoption_trial/text.py` with `normalize_whitespace(value: str) -> str`.
- Added `src/adoption_trial/__init__.py` to export the utility from the package.
- Added `tests/test_text.py` with parametrized pytest coverage for repeated spaces, leading/trailing whitespace, newlines, tabs, empty strings, and whitespace-only strings.
- Updated `pyproject.toml` so pytest includes `src` on the import path.

## Validation

- PASS: `uv run --with pytest pytest tests`
- PASS: `uv run --with ruff ruff check .`
- PASS: `uv run --with ruff ruff format --check .`
- FAIL, then corrected: `uv run --with ty ty check` failed because `pytest` was not installed in that temporary tool environment.
- PASS: `uv run --with ty --with pytest ty check`

## Review Notes

- Loaded the anti-pattern review checklist and found no blocking issues.
- Did not commit changes.
