# Gemm

**Open-source framework for multi-brand robot fleet integration.**

Gemm defines a neutral abstraction layer between application code and the
hardware-specific software that controls robots. You register an adapter
for each robot brand, submit tasks by name, and the framework handles the
rest — the same code runs against real hardware and simulators.

## Why Gemm

Every robot vendor ships its own SDK, protocols, and proprietary tooling.
Building a fleet across multiple brands means re-implementing the same
plumbing — connection management, task execution, error handling — once
per vendor, and locking the application into a single hardware supplier.

Gemm provides a single, stable contract that any adapter implements. Your
application depends on Gemm, not on any specific robot SDK.

## Quick example

```python
import asyncio
from gemm import Engine
from gemm.adapters import MockAdapter


async def main() -> None:
    async with Engine() as engine:
        await engine.register(MockAdapter(name="r1"))

        task = await engine.submit("r1", "move_to", {"x": 1.0, "y": 2.0})
        result = await task.wait()

        print(result.status)  # TaskStatus.COMPLETED


asyncio.run(main())
```

## Where to go next

- [Getting started](getting-started.md) — install and run your first task.
- [Adapters](concepts/adapters.md) — the core contract every robot implements.
- [Tasks](concepts/tasks.md) — submit work, wait for results, handle failures.
- [Building an adapter](guides/building-an-adapter.md) — integrate a new robot
  brand in under an hour.
