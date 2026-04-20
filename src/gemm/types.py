"""Shared value types used across the framework and adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Pose:
    x: float
    y: float
    z: float = 0.0
    yaw: float = 0.0


@dataclass(frozen=True, slots=True)
class RobotState:
    pose: Pose
    battery: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TaskResult:
    status: TaskStatus
    error: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    @classmethod
    def success(cls, **data: Any) -> TaskResult:
        return cls(status=TaskStatus.COMPLETED, data=data)

    @classmethod
    def failure(cls, error: str) -> TaskResult:
        return cls(status=TaskStatus.FAILED, error=error)
