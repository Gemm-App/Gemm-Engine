"""Reusable pytest base class for validating Adapter contract compliance.

Adapter authors inherit this class and provide an ``adapter`` fixture:

    import pytest
    from gemm.testing import AdapterContractTests
    from my_package import MyAdapter

    class TestMyAdapterContract(AdapterContractTests):
        @pytest.fixture
        def adapter(self):
            return MyAdapter(...)

Every adapter that ships as part of the Gemm ecosystem is expected to pass
these tests. They exercise only the uniform contract — adapter-specific
behavior (action vocabulary, hardware-level checks) must be tested separately.
"""

from __future__ import annotations

import pytest

from gemm.adapters.base import Adapter
from gemm.errors import AdapterConnectionError, SensorNotAvailable
from gemm.types import RobotState, SensorReading, TaskResult

_UNSUPPORTED_ACTION = "__gemm_contract_probe_unknown_action__"
_UNSUPPORTED_SENSOR = "__gemm_contract_probe_unknown_sensor__"


class AdapterContractTests:
    # ------------------------------------------------------------------ #
    # Basic protocol (8 original tests)                                   #
    # ------------------------------------------------------------------ #

    def test_adapter_satisfies_protocol(self, adapter: Adapter) -> None:
        assert isinstance(adapter, Adapter)

    def test_adapter_exposes_non_empty_name(self, adapter: Adapter) -> None:
        assert isinstance(adapter.name, str)
        assert adapter.name

    @pytest.mark.asyncio
    async def test_get_state_before_connect_raises(self, adapter: Adapter) -> None:
        with pytest.raises(AdapterConnectionError):
            await adapter.get_state()

    @pytest.mark.asyncio
    async def test_execute_before_connect_raises(self, adapter: Adapter) -> None:
        with pytest.raises(AdapterConnectionError):
            await adapter.execute(_UNSUPPORTED_ACTION, {})

    @pytest.mark.asyncio
    async def test_connect_then_disconnect(self, adapter: Adapter) -> None:
        await adapter.connect()
        await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_get_state_after_connect_returns_robot_state(self, adapter: Adapter) -> None:
        await adapter.connect()
        try:
            state = await adapter.get_state()
            assert isinstance(state, RobotState)
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_execute_returns_task_result(self, adapter: Adapter) -> None:
        await adapter.connect()
        try:
            result = await adapter.execute(_UNSUPPORTED_ACTION, {})
            assert isinstance(result, TaskResult)
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_unsupported_action_returns_failure_not_raises(self, adapter: Adapter) -> None:
        await adapter.connect()
        try:
            result = await adapter.execute(_UNSUPPORTED_ACTION, {})
            assert not result.ok
        finally:
            await adapter.disconnect()

    # ------------------------------------------------------------------ #
    # Sensor interface (3 additional contract tests)                      #
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    async def test_get_sensor_before_connect_raises(self, adapter: Adapter) -> None:
        """get_sensor() must raise AdapterConnectionError before connect()."""
        with pytest.raises(AdapterConnectionError):
            await adapter.get_sensor(_UNSUPPORTED_SENSOR)

    @pytest.mark.asyncio
    async def test_get_sensor_unknown_raises_sensor_not_available(self, adapter: Adapter) -> None:
        """get_sensor() with an unrecognised name must raise SensorNotAvailable."""
        await adapter.connect()
        try:
            with pytest.raises(SensorNotAvailable):
                await adapter.get_sensor(_UNSUPPORTED_SENSOR)
        finally:
            await adapter.disconnect()

    @pytest.mark.asyncio
    async def test_subscribe_returns_callable_unsubscribe(self, adapter: Adapter) -> None:
        """subscribe() on a supported sensor returns a no-arg unsubscribe callable."""
        await adapter.connect()
        try:
            readings: list[SensorReading] = []
            unsubscribe = None
            for sensor in ("battery", "imu", "odometry", "sport_state", "motors"):
                try:
                    unsubscribe = adapter.subscribe(sensor, readings.append)
                    break
                except SensorNotAvailable:
                    continue
            if unsubscribe is None:
                pytest.skip("adapter exposes no testable sensors")
            assert callable(unsubscribe)
            unsubscribe()  # calling unsubscribe must not raise
        finally:
            await adapter.disconnect()
