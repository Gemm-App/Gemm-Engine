# `tests/unit/` - isolated module tests

Unit tests validate behavior of individual modules with minimal dependencies.

## Current suite map

- `test_registry.py` -> `src/gemm/core/registry.py`
- `test_task.py` -> `src/gemm/tasks/task.py`
- `test_types.py` -> `src/gemm/types.py`
- `test_mock_adapter.py` -> `src/gemm/adapters/mock.py`
- `test_contract_harness.py` -> `src/gemm/testing/contract.py`

## Add tests here when

- The change is local to one module or value type.
- You are fixing a pure logic bug.
- You want very fast regression coverage.

## Unit test rules

1. Keep tests focused and deterministic.
2. Avoid overlap with integration scenarios unless it catches a subtle edge.
3. Prefer expressive test names that describe expected behavior.
4. For async APIs, use `@pytest.mark.asyncio` and keep awaited paths explicit.
