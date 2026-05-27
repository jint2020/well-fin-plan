# Repository Guidelines

## Project Structure & Module Organization

This repository is a small Python project for financial planning utilities and related documents.

- `main.py` is the current application entry point.
- `pyproject.toml` defines package metadata and the Python version requirement.
- `docs/` stores project artifacts, including `个人资金管理模板_浮动收入版.xlsx`.
- `README.md` is currently available for user-facing overview and setup notes.

Keep source changes close to their purpose. If the codebase grows, prefer moving reusable Python code into a package directory such as `well_fin_plan/` and tests into `tests/`.

## Build, Test, and Development Commands

- `python main.py` runs the current entry point.
- `python -m compileall .` performs a quick syntax check across Python files.
- `python -m venv .venv` creates a local virtual environment if one is not already present.
- `source .venv/bin/activate` activates the local environment on macOS/Linux.

The project currently declares Python `>=3.13` and has no runtime dependencies in `pyproject.toml`.

## Coding Style & Naming Conventions

Use standard Python style: 4-space indentation, clear function names, and lowercase snake_case for modules, functions, and variables. Use PascalCase for classes and UPPER_SNAKE_CASE for constants.

Keep functions small and explicit. Avoid adding broad abstractions until repeated behavior appears in at least two places. Prefer type hints for new public functions, especially once modules are split out from `main.py`.

## Testing Guidelines

No test framework is configured yet. When adding behavior, add `pytest` tests under `tests/` with filenames like `test_budget_rules.py` and test functions named `test_<expected_behavior>`.

Until a test command is added to project tooling, run focused checks with:

```bash
python -m compileall .
```

If `pytest` is introduced, document the install and run commands in `README.md`.

## Commit & Pull Request Guidelines

This repository has no commits yet, so no historical commit convention can be inferred. Use short, imperative commit messages such as `Add budget template parser` or `Document development workflow`.

Pull requests should include a concise summary, the commands used to verify changes, and screenshots or sample outputs when modifying generated documents or user-facing artifacts. Link related issues when available.

## Security & Configuration Tips

Do not commit private financial data, credentials, or personal account details. Keep example spreadsheets anonymized, and store local-only files in ignored paths.
