"""Minimal end-to-end example against the built-in MockAdapter.

Run with:

    python examples/hello_mock.py

No hardware required. The same code runs against a real robot by swapping
``MockAdapter`` for an ecosystem adapter (for example, ``gemm-unitree``) —
the rest of the program does not change.
"""

from __future__ import annotations

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


if __name__ == "__main__":
    asyncio.run(main())
