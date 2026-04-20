# Gemm-Engine

Open-source framework for multi-brand robot fleet integration.

## Requirements

- Python 3.11+

## Install

For package consumers:

```bash
pip install gemm-engine
```

For local development (from repository root):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Run Example Code

Run the built-in mock example:

```bash
python examples/hello_mock.py
```

## Run Tests

Run all tests:

```bash
pytest
```

Run only unit or integration tests:

```bash
pytest tests/unit
pytest tests/integration
```

## Run Quality Checks

These match CI checks:

```bash
ruff check .
black --check .
mypy
```

## Build and Serve Docs

Serve docs locally:

```bash
mkdocs serve
```

Build docs in strict mode:

```bash
mkdocs build --strict
```