# `gemm/adapters/` — the contract + bundled adapters

The **most important file in the repository** is `base.py`. It defines the
`Adapter` protocol — the single point where the framework meets every
robot brand. Changing it is a cross-ecosystem breaking change.

## Files

| File      | Purpose |
| ---       | --- |
| `base.py` | The `Adapter` Protocol. Four async methods + a `name` attribute. `@runtime_checkable` so `isinstance(x, Adapter)` works in the registry. |
| `mock.py` | `MockAdapter` — in-memory reference implementation. Used by tests and examples. Doubles as a canonical example for adapter authors. |

## Changing `base.py`

Every third-party adapter in the ecosystem implements this protocol. Any
change here ripples out. Before editing:

1. Write down the motivation. "Nice to have" is not enough — we must be
   willing to tell `gemm-unitree`, `gemm-yourbrand`, etc. that they need
   to update.
2. Prefer additive changes. A new optional method is far safer than
   changing the signature of an existing one.
3. Update `AdapterContractTests` in `gemm/testing/contract.py` to cover
   the new behavior. If the test harness doesn't enforce it, the contract
   is just a docstring.
4. Update the guide at `docs/guides/building-an-adapter.md`.

If you find yourself wanting to change the protocol to make one specific
adapter easier, that is a red flag — the adapter should bend, not the
protocol.

## `MockAdapter` rules

`MockAdapter` is the reference. Adapter authors read it to learn the
contract. Keep it:

- **Short.** Under ~60 lines. Whenever possible, leave trickier error
  paths to real adapters.
- **Honest.** Every branch that matters (raise before connect, fail on
  unknown action, return `TaskResult.success` on success) must be present
  and easy to find.
- **Dependency-free.** Standard library only.

Adding a new mock action:

1. Extend the `if action == "..."` chain in `execute()`.
2. Add a row to the action table in `docs/concepts/adapters.md` if the
   action is expected to exist across real adapters too.
3. Unit-test it in `tests/unit/test_mock_adapter.py`.

## Adding a **new shipped** adapter

Don't. Ecosystem adapters live in their own repositories
(`gemm-unitree`, `gemm-<brand>`, ...). The engine repo ships `MockAdapter`
and nothing else on purpose — zero hardware dependencies, zero vendor
coupling.

The one exception would be a second "reference" adapter that's still
hardware-free and exists to demonstrate the contract from a different
angle (e.g. an async-stream-based mock). Discuss first.

## Naming

- The PyPI distribution prefix is `gemm-<brand>` (dash).
- The import name is `gemm_<brand>` (underscore — Python rule).
- The class name is `<Brand>Adapter`.

These conventions are not enforced by code; they are enforced by review.
