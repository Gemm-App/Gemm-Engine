# `src/` - source layout

This folder contains the installable Python package for Gemm.

## What to edit here

- Edit framework runtime code in `src/gemm/`.
- Keep package exports explicit in `src/gemm/__init__.py`.
- Keep shared value and error types in `src/gemm/types.py` and
  `src/gemm/errors.py`.

## Change workflow

1. Make the code change in the smallest relevant module.
2. If the public API changes, update `src/gemm/__init__.py` exports.
3. Add or update tests under `tests/unit/` and `tests/integration/`.
4. Update documentation in `docs/` for behavior changes.

## Validation checklist

Run from repository root:

```bash
pytest
ruff check .
black --check .
mypy
```

If your change is internal only, still run unit tests for touched modules.
