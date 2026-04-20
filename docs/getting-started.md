# Getting started

## Install

```bash
pip install gemm-engine
```

Requires Python 3.11 or later.

## Hello, robot

Gemm ships with a `MockAdapter` so you can try the framework without hardware.

```python
import asyncio
from gemm import Engine
from gemm.adapters import MockAdapter


async def main() -> None:
    async with Engine() as engine:
        await engine.register(MockAdapter(name="r1"))

        task = await engine.submit("r1", "move_to", {"x": 3.0, "y": 4.0})
        result = await task.wait()

        if result.ok:
            print(f"arrived at {result.data['pose']}")
        else:
            print(f"task failed: {result.error}")


asyncio.run(main())
```

## What just happened

1. `Engine()` constructs the runtime. Entering the `async with` block opens it.
2. `engine.register(...)` stores the adapter by name and calls `adapter.connect()`.
3. `engine.submit(name, action, params)` schedules the task on an adapter and
   returns immediately — it does **not** block on completion.
4. `await task.wait()` suspends until the adapter finishes and a result is set.
5. Leaving the context manager disconnects every registered adapter in turn.

The same code runs against real hardware by swapping `MockAdapter` for a real
adapter such as `gemm-unitree`. The rest of your application never changes.

## Running multiple robots concurrently

```python
async with Engine() as engine:
    await engine.register(MockAdapter(name="a"))
    await engine.register(MockAdapter(name="b"))
    await engine.register(MockAdapter(name="c"))

    tasks = await asyncio.gather(
        engine.submit("a", "move_to", {"x": 1.0, "y": 0.0}),
        engine.submit("b", "move_to", {"x": 2.0, "y": 0.0}),
        engine.submit("c", "move_to", {"x": 3.0, "y": 0.0}),
    )
    results = await asyncio.gather(*(t.wait() for t in tasks))
```

Submitting is non-blocking: each task starts running in the background
immediately. Tasks on different adapters execute concurrently.
