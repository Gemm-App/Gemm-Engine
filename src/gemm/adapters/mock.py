"""Reference adapter that simulates a robot in memory.

Used for testing the framework and validating the contract without real
hardware. Also serves as a reference implementation for adapter authors.
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Callable
from typing import Any

from gemm.errors import AdapterConnectionError, SensorNotAvailable
from gemm.types import (
    BatteryState,
    IMUData,
    Pose,
    RobotOdometry,
    RobotState,
    SensorReading,
    TaskResult,
)

# Sensors natively supported by MockAdapter
_SUPPORTED_SENSORS = frozenset({"battery", "imu", "odometry"})


class MockAdapter:
    """In-memory adapter. No hardware required.

    Supports actions: ``move_to``, ``noop``.
    Supports sensors: ``battery``, ``imu``, ``odometry``.

    Use ``_fire_sensor(sensor, data)`` in tests to trigger callbacks.
    """

    def __init__(self, name: str, *, execution_delay: float = 0.0) -> None:
        self.name = name
        self._execution_delay = execution_delay
        self._connected = False
        self._pose = Pose(x=0.0, y=0.0)
        self._battery = 1.0
        # sensor subscription registry: sensor → list of callbacks
        self._subscriptions: dict[str, list[Callable[[SensorReading], None]]] = {}

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        self._subscriptions.clear()

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

    # ------------------------------------------------------------------ #
    # Sensor interface                                                     #
    # ------------------------------------------------------------------ #

    async def get_sensor(self, sensor: str) -> SensorReading:
        """Return a simulated sensor reading.

        Supported: ``"battery"``, ``"imu"``, ``"odometry"``.
        All other values raise :exc:`~gemm.errors.SensorNotAvailable`.
        """
        self._require_connected()

        if sensor == "battery":
            return BatteryState(
                soc=self._battery,
                voltage=25.2,
                current=-1.5,
                temperature=28.0,
                cycle_count=0,
            )

        if sensor == "imu":
            return IMUData(
                quaternion=(1.0, 0.0, 0.0, 0.0),
                angular_velocity=(0.0, 0.0, 0.0),
                linear_acceleration=(0.0, 0.0, 9.81),
                rpy=(0.0, 0.0, self._pose.yaw),
                temperature=35.0,
            )

        if sensor == "odometry":
            return RobotOdometry(
                position=(self._pose.x, self._pose.y, self._pose.z),
                orientation=(1.0, 0.0, 0.0, 0.0),
                linear_velocity=(0.0, 0.0, 0.0),
                angular_velocity=(0.0, 0.0, 0.0),
            )

        raise SensorNotAvailable(
            f"MockAdapter does not support sensor {sensor!r}. "
            f"Supported: {sorted(_SUPPORTED_SENSORS)}"
        )

    def subscribe(
        self,
        sensor: str,
        callback: Callable[[SensorReading], None],
    ) -> Callable[[], None]:
        """Register a callback for *sensor* updates.

        Callbacks are not fired automatically — use :meth:`_fire_sensor`
        in tests to trigger them manually.

        Raises :exc:`~gemm.errors.SensorNotAvailable` for unsupported sensors.
        """
        self._require_connected()
        if sensor not in _SUPPORTED_SENSORS:
            raise SensorNotAvailable(
                f"MockAdapter does not support sensor {sensor!r}. "
                f"Supported: {sorted(_SUPPORTED_SENSORS)}"
            )
        listeners = self._subscriptions.setdefault(sensor, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                listeners.remove(callback)

        return unsubscribe

    def _fire_sensor(self, sensor: str, data: SensorReading) -> None:
        """Test helper: fire all registered callbacks for *sensor*."""
        for cb in list(self._subscriptions.get(sensor, [])):
            cb(data)

    # ------------------------------------------------------------------ #
    # Guards                                                               #
    # ------------------------------------------------------------------ #

    def _require_connected(self) -> None:
        if not self._connected:
            raise AdapterConnectionError(f"adapter {self.name!r} is not connected")
