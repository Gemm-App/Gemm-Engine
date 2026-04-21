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
    SensorError,
    SensorNotAvailable,
    TaskFailed,
)
from gemm.tasks.task import Task
from gemm.types import (
    BatteryState,
    IMUData,
    LiDARScan,
    MotorState,
    Pose,
    RobotOdometry,
    RobotState,
    SensorReading,
    TaskResult,
    TaskStatus,
    VideoFrame,
)

__version__ = "0.1.1"

__all__ = [
    "Adapter",
    "AdapterAlreadyRegistered",
    "AdapterConnectionError",
    "AdapterError",
    "AdapterNotRegistered",
    "BatteryState",
    "Engine",
    "EngineClosed",
    "GemmError",
    "IMUData",
    "InvalidAction",
    "LiDARScan",
    "MotorState",
    "Pose",
    "RobotOdometry",
    "RobotState",
    "SensorError",
    "SensorNotAvailable",
    "SensorReading",
    "Task",
    "TaskFailed",
    "TaskResult",
    "TaskStatus",
    "VideoFrame",
    "__version__",
]
