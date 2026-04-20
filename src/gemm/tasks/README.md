# `gemm/tasks/` — work units

Everything about a unit of work: the data model (`Task`) and the thing
that actually runs it (`TaskExecutor`).

## Files

| File          | Purpose |
| ---           | --- |
| `task.py`     | `Task` dataclass — the handle users `await`. Carries adapter name, action, params, id, status, result, and an internal `asyncio.Event` for signaling. |
| `executor.py` | `TaskExecutor` — resolves an adapter from the registry and runs one task. Its `run()` method **never raises**; every exception becomes a `TaskResult.failure(...)`. |

## Why the split

`Task` is a plain data model — no logic, trivially serializable if we ever
need to persist or log it. `TaskExecutor` holds the only mutation logic
and keeps `Task` dumb. Keep them separate.

## The "never raises" rule

`TaskExecutor.run()` must return normally on every path. This is what lets
callers write:

```python
result = await task.wait()
if result.ok: ...
```

instead of wrapping in `try/except`. Breaking this is a silent correctness
bug — callers will hang on `task.wait()` forever because `_done` never
fires.

If you change `executor.py`:

1. Every branch must end with `task._complete(result)`.
2. No `raise` statements. Log and convert.
3. If you need to propagate a fatal error (e.g. the process is shutting
   down), revisit the design instead — `close()` semantics are in
   `core/engine.py`.

## `Task._complete` is private

The leading underscore is load-bearing. External code — including adapters
— must **not** call `_complete()`. It exists for `TaskExecutor` alone.
Keeping the write path single-threaded is how `await task.wait()` stays
correct without extra locking.

## Fields you can touch vs. not

| Field         | Mutable by whom |
| ---           | --- |
| `status`      | `TaskExecutor` only. |
| `result`      | `TaskExecutor` only (via `_complete`). |
| `_done`       | `TaskExecutor` only (via `_complete`). |
| `id`          | Generated once at construction, then frozen in practice. |
| Everything else | Set at construction, treat as frozen. |

Do not add `frozen=True` to the dataclass yet — the executor mutates
`status` and `result` in place. If you want frozen, switch to a
`Task` / `TaskState` split first.

## Concurrency model

- Each `submit()` creates exactly one `asyncio.Task` that runs the
  executor. Those handles are tracked in `Engine._in_flight`.
- Tasks on different adapters run concurrently (they await different SDKs).
- Tasks on the **same** adapter are serialized only because `execute()`
  is a single async method — there's no queue. If you need a priority
  queue, build it on top, not inside.

## Cancellation

Not implemented. `TaskStatus.CANCELLED` is reserved in the enum but never
set. When we add it:

- Add `Task.cancel()` that flips status to `CANCELLED` **only if** still
  `PENDING`.
- Decide (and document) whether `RUNNING` tasks can be cancelled — this
  depends on whether adapters can stop an in-flight hardware command.
- Update `AdapterContractTests` to test whichever semantics we land on.
