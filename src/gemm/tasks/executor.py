"""TaskExecutor — resolves an adapter and runs a single task against it."""

from __future__ import annotations

import logging

from gemm.core.registry import AdapterRegistry
from gemm.tasks.task import Task
from gemm.types import TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(self, registry: AdapterRegistry) -> None:
        self._registry = registry

    async def run(self, task: Task) -> None:
        """Execute a task. Never raises — all errors become TaskResult.failure."""
        try:
            adapter = self._registry.get(task.adapter_name)
            task.status = TaskStatus.RUNNING
            result = await adapter.execute(task.action, task.params)
        except Exception as exc:
            logger.exception("error running task %s", task.id)
            result = TaskResult.failure(f"{type(exc).__name__}: {exc}")
        task._complete(result)
