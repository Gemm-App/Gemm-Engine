"""Shared value types used across the framework and adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeAlias


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


# ---------------------------------------------------------------------------
# Sensor reading types
# Each type represents the standard return format for a named sensor.
# Adapters return these from get_sensor() and pass them to subscribe()
# callbacks. The types are frozen and immutable where possible.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class IMUData:
    """Inertial Measurement Unit snapshot.

    All values use SI units: rad, rad/s, m/s².
    """

    quaternion: tuple[float, float, float, float]
    """Orientation quaternion (w, x, y, z), unit quaternion."""

    angular_velocity: tuple[float, float, float]
    """Body-frame angular velocity in rad/s (roll, pitch, yaw rates)."""

    linear_acceleration: tuple[float, float, float]
    """Body-frame linear acceleration in m/s² (x, y, z)."""

    rpy: tuple[float, float, float]
    """Euler angles in radians: (roll, pitch, yaw)."""

    temperature: float = 0.0
    """IMU chip temperature in °C."""


@dataclass(frozen=True, slots=True)
class BatteryState:
    """Battery / BMS snapshot."""

    soc: float
    """State of Charge, normalised to 0.0-1.0 (0 % -> 0.0, 100 % -> 1.0)."""

    voltage: float
    """Bus voltage in volts."""

    current: float
    """Current in amps. Negative means discharging."""

    temperature: float = 0.0
    """Battery temperature in °C."""

    cycle_count: int = 0
    """Number of full charge cycles completed."""


@dataclass(frozen=True, slots=True)
class MotorState:
    """State of a single joint motor."""

    index: int
    """Motor index (hardware-specific; 0-based)."""

    position: float
    """Joint angle in radians."""

    velocity: float
    """Joint angular velocity in rad/s."""

    torque: float
    """Estimated torque in N·m."""

    temperature: float = 0.0
    """Motor temperature in °C."""


@dataclass(frozen=True, slots=True)
class RobotOdometry:
    """Pose + velocity from odometry (wheel/leg/SLAM-based).

    Position is in the SLAM/odom coordinate frame whose origin is the
    robot's position at SLAM initialisation.
    """

    position: tuple[float, float, float]
    """(x, y, z) in metres."""

    orientation: tuple[float, float, float, float]
    """Quaternion (w, x, y, z)."""

    linear_velocity: tuple[float, float, float]
    """Linear velocity in m/s (x, y, z)."""

    angular_velocity: tuple[float, float, float]
    """Angular velocity in rad/s (roll, pitch, yaw rates)."""


@dataclass(slots=True)
class LiDARScan:
    """A single LiDAR point-cloud snapshot.

    Not frozen because the points list may be large and copying it would be
    wasteful. Treat it as read-only after construction.
    """

    points: list[tuple[float, float, float]]
    """3-D points in the SLAM world frame, (x, y, z) in metres."""

    origin: tuple[float, float, float]
    """Origin of the voxel grid in world coordinates."""

    resolution: float
    """Voxel size in metres (e.g. 0.05 = 5 cm)."""

    timestamp: float = 0.0
    """Unix timestamp of the scan (seconds)."""

    def __len__(self) -> int:
        return len(self.points)


@dataclass(slots=True)
class VideoFrame:
    """A single decoded video frame from the robot's camera."""

    data: bytes
    """Raw pixel data in the format described by *encoding*."""

    width: int
    """Frame width in pixels."""

    height: int
    """Frame height in pixels."""

    encoding: str
    """Pixel encoding: ``"bgr24"``, ``"rgb24"``, or ``"jpeg"``."""

    timestamp: float = 0.0
    """Unix timestamp when the frame was captured (seconds)."""


# Union of all sensor reading types.
# get_sensor() returns one of these; subscribe() callbacks receive one.
SensorReading: TypeAlias = (
    IMUData | BatteryState | MotorState | LiDARScan | VideoFrame | RobotOdometry
)
