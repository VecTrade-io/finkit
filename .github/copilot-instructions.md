# FinKit — Copilot Instructions

## Workflow

All agents follow the standard workflow defined in `instructions/agent-workflow.instructions.md`:
**Implement → Verify → Changelog → Commit**

## Agents

| Agent | When to Use |
|-------|------------|
| `@vt-finkit-dev` | Implementing financial calculations |
| `@vt-finkit-tester` | Writing/fixing tests |

## Conventions

- Python 3.9+
- Pure computation only (no API/network calls)
- NumPy vectorized operations (no loops over data)
- Full type hints including numpy dtypes
- Google-style docstrings with LaTeX formulas
- Standard finance terminology for names

## Build & Test

```bash
pip install -e ".[dev]"    # Install with dev deps
pytest                     # Run tests
pytest --cov               # With coverage
ruff check .               # Lint
mypy src/                  # Type check
```
