"""Task model — represents a unit of work submitted to the engine."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any

from gemm.types import TaskResult, TaskStatus


@dataclass
class Task:
    """A unit of work submitted to an adapter.

    Instances are created by the engine on `submit()`. Callers hold a
    reference and use `await task.wait()` to block until completion.
    """

    adapter_name: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: TaskStatus = TaskStatus.PENDING
    result: TaskResult | None = None
    _done: asyncio.Event = field(default_factory=asyncio.Event, repr=False, compare=False)

    async def wait(self) -> TaskResult:
        """Block until the task completes and return its result."""
        await self._done.wait()
        assert self.result is not None, "task marked done without a result"
        return self.result

    def _complete(self, result: TaskResult) -> None:
        """Internal: record the final result and signal any waiters."""
        self.result = result
        self.status = result.status
        self._done.set()
