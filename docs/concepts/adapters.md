# Adapters

An **adapter** is the bridge between Gemm's engine and a specific robot
implementation. The adapter owns the connection, translates Gemm's generic
`execute(action, params)` calls into robot-specific commands, and reports
state back as a structured `RobotState`.

## The contract

Every adapter must satisfy the `Adapter` protocol:

```python
from typing import Any, Protocol, runtime_checkable
from gemm.types import RobotState, TaskResult


@runtime_checkable
class Adapter(Protocol):
    name: str

    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def get_state(self) -> RobotState: ...
    async def execute(self, action: str, params: dict[str, Any]) -> TaskResult: ...
```

## Structural typing, not inheritance

`Adapter` is a `Protocol`. Your class does **not** need to inherit from it —
structural typing is enough. Any class that exposes the four methods with
compatible signatures and a `name` attribute satisfies the contract.

This keeps adapters decoupled: they do not import a Gemm base class, can be
tested in isolation, and can live in completely separate packages — including
separate GitHub repositories maintained by third parties.

## Registration

Adapters are registered with the engine by name:

```python
await engine.register(MyAdapter(name="r1"))
```

The engine:

1. Verifies the instance satisfies the `Adapter` protocol at runtime.
2. Rejects duplicate names with `AdapterAlreadyRegistered`.
3. Calls `adapter.connect()`.
4. Rolls back the registration if `connect()` raises — the adapter is not
   left in the registry in a half-connected state.

From that point forward, adapters are referenced by name. Tasks carry the
adapter name rather than the instance, which makes them easy to serialize,
log, or persist.

## Lifecycle

| Phase    | Call                       | Notes |
| ---      | ---                        | --- |
| Setup    | `connect()`                | Open the connection, handshake with the SDK. |
| Runtime  | `get_state()`, `execute()` | Must raise `AdapterConnectionError` if called before `connect()`. |
| Teardown | `disconnect()`             | Release resources. Called automatically on `engine.close()`. |

## Error handling conventions

`execute()` is expected to **return** `TaskResult.failure(...)` for expected
failures — unsupported actions, invalid parameters, soft errors reported by
the robot. If the adapter raises instead, the engine catches the exception
and converts it to a failure result; nothing escapes to the caller.

This means application code always inspects `result.ok` / `result.error`
rather than wrapping `task.wait()` in a `try/except`.

## Ecosystem adapters

Third-party adapters live in their own packages (for example,
`gemm-unitree`, `gemm-yourbrand`). The Gemm engine imposes no coupling: any
package that publishes an object satisfying the `Adapter` protocol can be
registered.
