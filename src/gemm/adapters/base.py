"""Adapter contract — the core abstraction of the framework."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from gemm.types import RobotState, TaskResult


@runtime_checkable
class Adapter(Protocol):
    """Contract every robot adapter must fulfill.

    Adapters bridge Gemm's engine and a specific robot implementation.
    They do not need to inherit from this Protocol — structural typing
    is sufficient. Any object exposing the required attributes and
    methods with compatible signatures satisfies the contract.
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
