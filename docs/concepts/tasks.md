# Tasks

A `Task` is a unit of work submitted to an adapter. It is created by
`engine.submit(...)` and resolved via `await task.wait()`.

## Lifecycle

```
PENDING  →  RUNNING  →  COMPLETED
                     ↘  FAILED
                     ↘  CANCELLED
```

| State       | When it is set |
| ---         | --- |
| `PENDING`   | Just submitted; the executor has not yet picked it up. |
| `RUNNING`   | The adapter's `execute()` is in progress. |
| `COMPLETED` | `execute()` returned `TaskResult.success(...)`. |
| `FAILED`    | `execute()` returned `TaskResult.failure(...)` or raised. |
| `CANCELLED` | Reserved for future cancellation support. |

## Fields

```python
@dataclass
class Task:
    adapter_name: str
    action: str
    params: dict[str, Any]
    id: str                   # auto-generated UUID hex
    status: TaskStatus
    result: TaskResult | None
```

`result` is `None` until the task completes. Use `await task.wait()` to block
until it is set.

## Waiting for results

```python
task = await engine.submit("r1", "move_to", {"x": 1.0, "y": 2.0})
result = await task.wait()

if result.ok:
    print(result.data)
else:
    print(result.error)
```

## Fan-out

Submitting is non-blocking — the task begins running in the background as soon
as `submit()` returns. You can submit many and `asyncio.gather` their waiters:

```python
tasks = await asyncio.gather(
    engine.submit("a", "move_to", {"x": 1.0, "y": 0.0}),
    engine.submit("b", "move_to", {"x": 2.0, "y": 0.0}),
)
results = await asyncio.gather(*(t.wait() for t in tasks))
```

Tasks on different adapters run concurrently. Tasks on the same adapter run
in submission order, because they share a single `execute()` call stack on
the underlying robot.

## Engine close semantics

When an `Engine` context manager exits (or `engine.close()` is called
explicitly), the engine:

1. Stops accepting new submissions — subsequent `submit()` calls raise
   `EngineClosed`.
2. Waits for every in-flight task to finish.
3. Disconnects every registered adapter.

In-flight tasks are never cancelled or dropped. If you need to abort work,
handle it at the adapter level for now (cancellation support is a planned
extension to the task lifecycle).
