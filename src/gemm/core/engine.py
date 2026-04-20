"""Engine — central runtime that owns the registry, executor, and lifecycle."""

from __future__ import annotations

import asyncio
import logging
from types import TracebackType
from typing import Any

from gemm.adapters.base import Adapter
from gemm.core.registry import AdapterRegistry
from gemm.errors import AdapterNotRegistered, EngineClosed
from gemm.tasks.executor import TaskExecutor
from gemm.tasks.task import Task

logger = logging.getLogger(__name__)


class Engine:
    """Central runtime: registers adapters, submits tasks, manages lifecycle.

    Intended to be used as an async context manager:

        async with Engine() as engine:
            await engine.register(SomeAdapter(name="r1"))
            task = await engine.submit("r1", "move_to", {"x": 1.0, "y": 2.0})
            result = await task.wait()
    """

    def __init__(self) -> None:
        self._registry = AdapterRegistry()
        self._executor = TaskExecutor(self._registry)
        self._in_flight: set[asyncio.Task[None]] = set()
        self._closed = False

    async def __aenter__(self) -> Engine:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def register(self, adapter: Adapter) -> None:
        self._require_open()
        self._registry.register(adapter)
        try:
            await adapter.connect()
        except Exception:
            self._registry.unregister(adapter.name)
            raise

    async def unregister(self, name: str) -> None:
        self._require_open()
        adapter = self._registry.unregister(name)
        await adapter.disconnect()

    def adapter_names(self) -> list[str]:
        return self._registry.names()

    async def submit(
        self,
        adapter_name: str,
        action: str,
        params: dict[str, Any] | None = None,
    ) -> Task:
        self._require_open()
        if adapter_name not in self._registry:
            raise AdapterNotRegistered(f"adapter {adapter_name!r} is not registered")

        task = Task(adapter_name=adapter_name, action=action, params=params or {})
        handle = asyncio.create_task(self._executor.run(task))
        self._in_flight.add(handle)
        handle.add_done_callback(self._in_flight.discard)
        return task

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        if self._in_flight:
            await asyncio.gather(*self._in_flight, return_exceptions=True)

        for name in self._registry.names():
            adapter = self._registry.get(name)
            try:
                await adapter.disconnect()
            except Exception:
                logger.exception("error disconnecting adapter %r", name)

    def _require_open(self) -> None:
        if self._closed:
            raise EngineClosed("engine has been closed")
