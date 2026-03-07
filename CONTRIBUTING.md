# Contributing to Besshouka

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

```bash
git clone https://github.com/akhi/besshouka.git
cd besshouka
python -m venv env_besshouka
source env_besshouka/bin/activate
pip install -e ".[dev]"
```

Requires **Python >=3.11, <3.14**. Python 3.13 is recommended.

## Running Tests

```bash
# Fast tests (excludes GiNZA model loading)
pytest tests/ -m "not slow"

# Full suite (requires GiNZA + ja_ginza model)
pytest tests/ -v

# With coverage
pytest tests/ --cov=besshouka --cov-report=term-missing
```

## Linting

```bash
pip install ruff bandit
ruff check besshouka/
ruff format --check besshouka/
bandit -r besshouka/ -c pyproject.toml
```

## Making Changes

1. Fork the repository and create a branch from `main`
2. Write tests for any new functionality
3. Ensure all tests pass and linting is clean
4. Submit a pull request

## What You Can Contribute

- **New recognizers** — add regex patterns via YAML or implement a new recognizer class under `besshouka/analyzer/recognizers/`
- **New operators** — add a new operator under `besshouka/anonymizer/operators/`
- **Bug fixes** — if you find a bug, open an issue first, then submit a fix
- **Documentation** — improve READMEs, add examples, fix typos
- **Test coverage** — add tests for edge cases

## Project Structure

```
besshouka/
├── analyzer/          # PII detection (regex + GiNZA NER)
├── anonymizer/        # PII transformation (operators)
├── orchestrator/      # Pipeline wiring
├── models/            # Data classes
├── config/            # YAML loader
├── defaults/          # Built-in recognizer/operator YAML
└── cli.py             # Typer CLI
```

Each module has its own README with extension guides.

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Include tests for new functionality
- Follow existing code style (enforced by ruff)
- Update relevant READMEs if you change public-facing behavior
