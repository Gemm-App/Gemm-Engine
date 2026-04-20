"""Reference adapter that simulates a robot in memory.

Used for testing the framework and validating the contract without real
hardware. Also serves as a reference implementation for adapter authors.
"""

from __future__ import annotations

import asyncio
from typing import Any

from gemm.errors import AdapterConnectionError
from gemm.types import Pose, RobotState, TaskResult


class MockAdapter:
    def __init__(self, name: str, *, execution_delay: float = 0.0) -> None:
        self.name = name
        self._execution_delay = execution_delay
        self._connected = False
        self._pose = Pose(x=0.0, y=0.0)
        self._battery = 1.0

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def get_state(self) -> RobotState:
        self._require_connected()
        return RobotState(pose=self._pose, battery=self._battery)

    async def execute(self, action: str, params: dict[str, Any]) -> TaskResult:
        self._require_connected()

        if self._execution_delay > 0:
            await asyncio.sleep(self._execution_delay)

        if action == "move_to":
            self._pose = Pose(
                x=float(params["x"]),
                y=float(params["y"]),
                z=float(params.get("z", 0.0)),
                yaw=float(params.get("yaw", 0.0)),
            )
            return TaskResult.success(pose=self._pose)

        if action == "noop":
            return TaskResult.success()

        return TaskResult.failure(f"unsupported action: {action!r}")

    def _require_connected(self) -> None:
        if not self._connected:
            raise AdapterConnectionError(f"adapter {self.name!r} is not connected")
