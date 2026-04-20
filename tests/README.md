# `tests/` - test strategy and placement

This folder validates framework behavior across three levels:

- `unit/`: fast tests for isolated modules and value types.
- `integration/`: end-to-end engine workflows.
- shared config: `conftest.py`.

## Where to add tests

- Editing `src/gemm/core/*`: add integration tests first, then targeted unit
  tests if needed.
- Editing `src/gemm/adapters/*`: add/update `unit/test_mock_adapter.py` and
  contract harness tests.
- Editing `src/gemm/tasks/*`: update `unit/test_task.py` and related flow tests.
- Editing protocol semantics: update `src/gemm/testing/contract.py` and dogfood
  tests in `unit/test_contract_harness.py`.

## Run tests

```bash
pytest
pytest tests/unit
pytest tests/integration
```

Prefer adding regression tests in the same change that fixes a bug.
