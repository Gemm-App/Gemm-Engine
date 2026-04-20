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

## Publish to PyPI (Trusted Publishing)

This repository includes an automated publish workflow:

- `.github/workflows/publish.yml`

It supports:

- Automatic publish to PyPI on push to `main` when the version is new.
- Automatic GitHub Release creation after successful PyPI publish.
- Manual publish to TestPyPI or PyPI via `workflow_dispatch`.

### One-time setup

Configure a Trusted Publisher in both PyPI and TestPyPI:

1. Project: `gemm-engine`
2. Repository: `Gemm-App/Gemm-Engine`
3. Workflow: `publish.yml`
4. Environment: leave empty.

### Automatic release on push to `main`

1. Bump versions in `pyproject.toml` (`[project].version`) and
   `src/gemm/__init__.py` (`__version__`).
2. Commit and push to `main`.
3. The workflow builds the package, publishes to PyPI, and creates a
   GitHub Release using tag `v<version>`.

If that version tag already exists on origin, the publish step is skipped
to avoid duplicate uploads.

### Manual publish to TestPyPI

Run the `Publish` workflow from GitHub Actions and choose `repository=testpypi`.

### Manual publish to PyPI

Run the `Publish` workflow from GitHub Actions and choose:

1. `repository=pypi`
2. `create_release=true` (or `false` if you only want package publication)
