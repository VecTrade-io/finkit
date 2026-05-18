# Contributing to FinKit

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

```bash
git clone https://github.com/VecTrade-io/finkit.git
cd finkit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v --tb=short --cov=finkit
```

Coverage must remain at or above **90%**.

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Pull Request Process

1. Fork the repository and create a feature branch from `main`.
2. Add tests for any new functionality.
3. Ensure `pytest` passes with ≥90% coverage.
4. Ensure `ruff check` and `ruff format --check` pass.
5. Update documentation if applicable.
6. Submit a pull request with a clear description.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add moving average convergence`
- `fix: handle NaN in RSI calculation`
- `docs: update README examples`
- `test: add edge cases for bollinger bands`

## Code of Conduct

Be respectful and constructive. We follow the
[Contributor Covenant](https://www.contributor-covenant.org/) v2.1.
