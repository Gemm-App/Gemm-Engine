# `gemm/core/` — runtime

The engine and the registry. This is where adapters are stored and where
tasks are kicked off. Users interact with it through the `Engine` class;
everything else in this folder is an implementation detail.

## Files

| File          | Purpose |
| ---           | --- |
| `engine.py`   | `Engine` — async context manager. Owns the registry, dispatches tasks to the executor, tracks in-flight work, and orchestrates shutdown. |
| `registry.py` | `AdapterRegistry` — in-memory name → adapter map. Validates Protocol compliance on `register()` and raises typed errors on duplicate / missing names. |

## Engine responsibilities (and non-responsibilities)

The engine **does**:

- Validate that an adapter satisfies the `Adapter` protocol at register time.
- Call `adapter.connect()` after registration; roll back (remove from the
  registry) if `connect()` raises.
- Accept task submissions and schedule them via `TaskExecutor`.
- Track every in-flight `asyncio.Task` so `close()` can wait for them.
- Disconnect every adapter on close.

The engine **does not**:

- Retry failed tasks.
- Queue tasks when the adapter is busy — concurrency is the adapter's
  concern (see `tasks/README.md`).
- Cancel in-flight tasks on close. They run to completion.
- Persist state. Everything is in-memory.

If you are tempted to add one of these, discuss first — most of them are
better solved at the adapter layer or in a higher-level scheduler.

## Lifecycle invariants

- `Engine.__aenter__` returns `self`. It does **not** start background
  tasks — nothing is running until someone calls `submit()`.
- `close()` is idempotent. Calling it twice is a no-op.
- After `close()`, every public method except `adapter_names()` must raise
  `EngineClosed`.
- `close()` awaits `_in_flight` with `return_exceptions=True` so one
  misbehaving task cannot block shutdown.

## Editing guide

### Adding a method to `Engine`

1. If it mutates state, call `self._require_open()` first.
2. If it touches the registry, delegate to `AdapterRegistry` — do not
   reach into `self._registry._adapters`.
3. Update the docstring example in the class body if the change affects
   the "hello robot" flow.
4. Add an integration test in `tests/integration/test_engine_e2e.py`.
   Unit-testing `Engine` in isolation is almost always wrong; its value is
   in wiring things together.

### Adding a registry constraint

All lookups and mutations funnel through `AdapterRegistry`. When adding a
new rule (e.g. max adapters, name pattern):

1. Put the check in the registry, not in `Engine`.
2. Raise a specific error from `gemm.errors` — never a bare `ValueError`
   or `RuntimeError`.
3. Unit-test it in `tests/unit/test_registry.py`.

### Do not

- Import `asyncio.TaskGroup` yet — we target 3.11+ but the shape of the
  in-flight set is deliberately simple. Revisit when cancellation lands.
- Log at `INFO` level for per-task events. The engine is a library; stay at
  `DEBUG` unless something is actually wrong.
- Catch `BaseException`. Only `Exception` for adapter errors, and let
  `CancelledError` / `KeyboardInterrupt` propagate.
