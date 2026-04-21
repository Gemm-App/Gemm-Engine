"""Gemm — open-source framework for multi-brand robot fleet integration."""

from gemm.adapters.base import Adapter
from gemm.core.engine import Engine
from gemm.errors import (
    AdapterAlreadyRegistered,
    AdapterConnectionError,
    AdapterError,
    AdapterNotRegistered,
    EngineClosed,
    GemmError,
    InvalidAction,
    TaskFailed,
)
from gemm.tasks.task import Task
from gemm.types import Pose, RobotState, TaskResult, TaskStatus

__version__ = "0.1.1"

__all__ = [
    "Adapter",
    "AdapterAlreadyRegistered",
    "AdapterConnectionError",
    "AdapterError",
    "AdapterNotRegistered",
    "Engine",
    "EngineClosed",
    "GemmError",
    "InvalidAction",
    "Pose",
    "RobotState",
    "Task",
    "TaskFailed",
    "TaskResult",
    "TaskStatus",
    "__version__",
]
