"""Adapter contract — the core abstraction of the framework."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from gemm.types import RobotState, SensorReading, TaskResult


@runtime_checkable
class Adapter(Protocol):
    """Contract every robot adapter must fulfill.

    Adapters bridge Gemm's engine and a specific robot implementation.
    They do not need to inherit from this Protocol — structural typing
    is sufficient. Any object exposing the required attributes and
    methods with compatible signatures satisfies the contract.

    Sensor interface
    ----------------
    ``get_sensor(sensor)`` performs a one-shot read of the named sensor and
    returns the current value as the appropriate ``SensorReading`` subtype.

    ``subscribe(sensor, callback)`` registers a callback that is invoked
    every time a new reading arrives (e.g. from a hardware stream). It
    returns an *unsubscribe* callable — calling it removes the callback.

    Sensors that an adapter does not support should raise
    ``gemm.errors.SensorNotAvailable``.
    """

    name: str

    async def connect(self) -> None:
        """Open the connection to the underlying robot."""
        ...

    async def disconnect(self) -> None:
        """Release the connection and any associated resources."""
        ...

    async def get_state(self) -> RobotState:
        """Return a snapshot of the robot's current state."""
        ...

    async def execute(self, action: str, params: dict[str, Any]) -> TaskResult:
        """Execute a named action with the given parameters."""
        ...

    async def get_sensor(self, sensor: str) -> SensorReading:
        """Return the current reading for the named sensor.

        Args:
            sensor: Sensor identifier string. Well-known values:
                ``"imu"``, ``"battery"``, ``"odometry"``, ``"lidar"``,
                ``"motors"``, ``"sport_state"``, ``"video"``.

        Returns:
            A :data:`~gemm.types.SensorReading` instance whose concrete type
            matches the sensor (e.g. :class:`~gemm.types.IMUData` for
            ``"imu"``).

        Raises:
            :exc:`~gemm.errors.SensorNotAvailable`: sensor not supported.
            :exc:`~gemm.errors.AdapterConnectionError`: called before
                ``connect()``.
        """
        ...

    def subscribe(
        self,
        sensor: str,
        callback: Callable[[SensorReading], None],
    ) -> Callable[[], None]:
        """Register a callback invoked on every new reading for *sensor*.

        Args:
            sensor: Same identifiers as :meth:`get_sensor`.
            callback: Called with the new :data:`~gemm.types.SensorReading`
                each time fresh data arrives. Must not block.

        Returns:
            An *unsubscribe* callable. Call it (no arguments) to stop
            receiving callbacks for this registration.

        Raises:
            :exc:`~gemm.errors.SensorNotAvailable`: sensor not supported.
            :exc:`~gemm.errors.AdapterConnectionError`: called before
                ``connect()``.
        """
        ...
