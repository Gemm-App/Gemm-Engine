# Building an adapter

This guide walks through integrating a new robot brand into Gemm. The target
is a working adapter in **under an hour**, validated automatically by the
shared contract tests.

## Scope

An adapter is a small Python package that:

- Implements the `Adapter` protocol (four async methods and a `name`).
- Lives in its own repository (recommended) or module.
- Publishes to PyPI so other teams can `pip install gemm-mybrand`.

You do **not** need to modify the Gemm engine repository.

## 1. Scaffold the package

```
gemm-mybrand/
├── pyproject.toml
├── src/
│   └── gemm_mybrand/
│       ├── __init__.py
│       ├── py.typed
│       └── adapter.py
└── tests/
    └── test_contract.py
```

`pyproject.toml`:

```toml
[project]
name = "gemm-mybrand"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "gemm-engine>=0.1.0",
    # your robot SDK here
]

[project.optional-dependencies]
testing = ["gemm-engine[testing]"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Include an empty `py.typed` file so downstream mypy users can see your types.

## 2. Implement the adapter

`src/gemm_mybrand/adapter.py`:

```python
from typing import Any

from gemm.errors import AdapterConnectionError
from gemm.types import Pose, RobotState, TaskResult

import mybrand_sdk  # whatever your hardware uses


class MyBrandAdapter:
    def __init__(self, name: str, host: str, port: int) -> None:
        self.name = name
        self._host = host
        self._port = port
        self._sdk: mybrand_sdk.Client | None = None

    async def connect(self) -> None:
        self._sdk = await mybrand_sdk.connect(self._host, self._port)

    async def disconnect(self) -> None:
        if self._sdk is not None:
            await self._sdk.close()
            self._sdk = None

    async def get_state(self) -> RobotState:
        sdk = self._require_sdk()
        telemetry = await sdk.telemetry()
        return RobotState(
            pose=Pose(x=telemetry.x, y=telemetry.y, yaw=telemetry.yaw),
            battery=telemetry.battery,
        )

    async def execute(self, action: str, params: dict[str, Any]) -> TaskResult:
        sdk = self._require_sdk()
        if action == "move_to":
            await sdk.navigate(params["x"], params["y"])
            return TaskResult.success()
        return TaskResult.failure(f"unsupported action: {action!r}")

    def _require_sdk(self) -> mybrand_sdk.Client:
        if self._sdk is None:
            raise AdapterConnectionError(f"{self.name!r} is not connected")
        return self._sdk
```

Three rules to internalise:

- **No inheritance.** `MyBrandAdapter` does not extend any Gemm base class.
  Structural typing via the `Adapter` protocol is enough.
- **Raise `AdapterConnectionError`** if `get_state`/`execute` are called
  before `connect()`. The contract tests verify this explicitly.
- **Return a failure, do not raise**, for expected failures in `execute()`.
  Raising is handled by the engine, but returning keeps debugging predictable
  and forces you to think about the user-visible error message.

## 3. (Optional) Implement the sensor interface

If your robot exposes hardware sensors, add `get_sensor()` and `subscribe()`:

```python
from collections.abc import Callable
from gemm.errors import AdapterConnectionError, SensorNotAvailable
from gemm.types import BatteryState, IMUData, SensorReading

_SUPPORTED = frozenset({"battery", "imu"})

class MyBrandAdapter:
    # ... existing methods ...

    async def get_sensor(self, sensor: str) -> SensorReading:
        self._require_connected()
        if sensor == "battery":
            raw = await self._sdk.battery()
            return BatteryState(soc=raw.percent / 100, voltage=raw.volts,
                                current=raw.amps, temperature=raw.temp)
        if sensor == "imu":
            raw = await self._sdk.imu()
            return IMUData(quaternion=raw.quat, angular_velocity=raw.gyro,
                           linear_acceleration=raw.accel, rpy=raw.rpy)
        raise SensorNotAvailable(f"sensor {sensor!r} not available")

    def subscribe(
        self,
        sensor: str,
        callback: Callable[[SensorReading], None],
    ) -> Callable[[], None]:
        self._require_connected()
        if sensor not in _SUPPORTED:
            raise SensorNotAvailable(f"sensor {sensor!r} not available")
        listeners = self._subscriptions.setdefault(sensor, [])
        listeners.append(callback)
        def unsubscribe() -> None:
            try:
                listeners.remove(callback)
            except ValueError:
                pass
        return unsubscribe
```

Rules: raise `AdapterConnectionError` before `connect()`, raise
`SensorNotAvailable` for unknown names, return a no-arg unsubscribe callable,
and never block inside a callback. See [Sensors](../concepts/sensors.md) for the
full type reference.

## 4. Wire up the contract tests

`tests/test_contract.py`:

```python
import pytest
from gemm.testing import AdapterContractTests
from gemm_mybrand import MyBrandAdapter


class TestMyBrandContract(AdapterContractTests):
    @pytest.fixture
    def adapter(self):
        return MyBrandAdapter(name="t", host="localhost", port=9000)
```

Running `pytest` now executes **11 inherited tests** that probe the uniform
contract:

- Protocol compliance.
- Non-empty name.
- Raises on use before `connect()`.
- Connect/disconnect lifecycle is clean.
- `get_state()` after connect returns a `RobotState`.
- `execute()` returns a `TaskResult`.
- Unsupported actions return a failure rather than raising.
- `get_sensor()` raises before `connect()`.
- `get_sensor()` raises `SensorNotAvailable` for unknown sensors.
- `subscribe()` returns a callable unsubscribe.

When these pass, your adapter is Gemm-compliant. Anything specific to your
robot's action vocabulary belongs in separate tests you write yourself.

## 4. (Optional) Expose via entry points

If you want Gemm to discover your adapter from an installed package by name,
declare an entry point in `pyproject.toml`:

```toml
[project.entry-points."gemm.adapters"]
mybrand = "gemm_mybrand:MyBrandAdapter"
```

This is opt-in and reserved for a future Gemm release.

## Checklist

- [ ] Package scaffolded with `src/` layout.
- [ ] Adapter implements the four-method contract (`connect`, `disconnect`, `get_state`, `execute`).
- [ ] Adapter implements `get_sensor` and `subscribe` if the robot has sensors.
- [ ] `AdapterContractTests` subclassed and all 11 tests passing.
- [ ] Adapter-specific tests for the actions and sensors your robot supports.
- [ ] `py.typed` marker included.
- [ ] Published to PyPI (or an internal index).
