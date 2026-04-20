# `gemm/testing/` - adapter contract harness

This package contains reusable tests that adapter packages inherit to verify
contract compliance.

## Files

| File | Purpose |
| --- | --- |
| `contract.py` | `AdapterContractTests` base class with shared adapter checks. |

## When to edit this folder

Edit this folder when the adapter contract itself changes or when you discover
a missing invariant that all adapters should satisfy.

## Rules for contract changes

1. Keep tests generic across robot brands.
2. Do not add hardware- or vendor-specific expectations.
3. Prefer additive checks over breaking existing adapter semantics.
4. Keep failure messages explicit so adapter authors can diagnose quickly.

## Required follow-up when changing contract tests

- Run `pytest tests/unit/test_contract_harness.py`.
- Run integration tests to ensure the bundled mock still passes.
- Update `docs/guides/building-an-adapter.md` if expectations change.
- Update `src/gemm/adapters/README.md` if the contract guidance changed.
