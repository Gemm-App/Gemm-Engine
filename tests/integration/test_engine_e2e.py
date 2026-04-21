import asyncio
from collections.abc import Callable
from typing import Any

import pytest

from gemm import Engine, EngineClosed, Pose, SensorNotAvailable, TaskStatus
from gemm.adapters import MockAdapter
from gemm.errors import AdapterConnectionError, AdapterNotRegistered
from gemm.types import RobotState, SensorReading, TaskResult


def _stub_get_sensor(sensor: str) -> Any:
    raise SensorNotAvailable(sensor)


def _stub_subscribe(sensor: str, callback: Callable[[SensorReading], None]) -> Callable[[], None]:
    raise SensorNotAvailable(sensor)


@pytest.mark.asyncio
async def test_engine_runs_single_task_end_to_end():
    async with Engine() as engine:
        await engine.register(MockAdapter(name="r1"))

        task = await engine.submit("r1", "move_to", {"x": 3.0, "y": 4.0})
        result = await task.wait()

        assert result.ok
        assert result.status is TaskStatus.COMPLETED
        assert result.data["pose"] == Pose(x=3.0, y=4.0)


@pytest.mark.asyncio
async def test_engine_submit_for_unknown_adapter_raises():
    async with Engine() as engine:
        with pytest.raises(AdapterNotRegistered):
            await engine.submit("ghost", "noop", {})


@pytest.mark.asyncio
async def test_engine_runs_tasks_on_multiple_adapters_concurrently():
    async with Engine() as engine:
        await engine.register(MockAdapter(name="a", execution_delay=0.01))
        await engine.register(MockAdapter(name="b", execution_delay=0.01))
        await engine.register(MockAdapter(name="c", execution_delay=0.01))

        tasks = await asyncio.gather(
            engine.submit("a", "move_to", {"x": 1.0, "y": 0.0}),
            engine.submit("b", "move_to", {"x": 2.0, "y": 0.0}),
            engine.submit("c", "move_to", {"x": 3.0, "y": 0.0}),
        )
        results = await asyncio.gather(*(t.wait() for t in tasks))

        assert all(r.ok for r in results)
        assert engine.adapter_names() == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_engine_close_disconnects_all_adapters():
    adapter = MockAdapter(name="r1")
    engine = Engine()
    await engine.register(adapter)

    await engine.close()

    with pytest.raises(AdapterConnectionError):
        await adapter.get_state()


@pytest.mark.asyncio
async def test_engine_rejects_operations_after_close():
    engine = Engine()
    await engine.close()

    with pytest.raises(EngineClosed):
        await engine.register(MockAdapter(name="r1"))
    with pytest.raises(EngineClosed):
        await engine.submit("r1", "noop", {})


@pytest.mark.asyncio
async def test_engine_close_waits_for_in_flight_tasks():
    engine = Engine()
    await engine.register(MockAdapter(name="slow", execution_delay=0.05))

    task = await engine.submit("slow", "noop", {})
    await engine.close()

    assert task.result is not None
    assert task.result.ok


@pytest.mark.asyncio
async def test_engine_surfaces_adapter_exceptions_as_task_failures():
    class RaisingAdapter:
        name = "boom"

        async def connect(self) -> None:
            pass

        async def disconnect(self) -> None:
            pass

        async def get_state(self) -> RobotState:
            raise NotImplementedError

        async def execute(self, action: str, params: dict[str, Any]) -> TaskResult:
            raise RuntimeError("simulated failure")

        get_sensor = _stub_get_sensor
        subscribe = _stub_subscribe

    async with Engine() as engine:
        await engine.register(RaisingAdapter())

        task = await engine.submit("boom", "any_action", {})
        result = await task.wait()

        assert not result.ok
        assert result.error is not None
        assert "simulated failure" in result.error


@pytest.mark.asyncio
async def test_engine_register_rolls_back_on_connect_failure():
    class FailingConnectAdapter:
        name = "no-conn"

        async def connect(self) -> None:
            raise ConnectionError("cannot reach robot")

        async def disconnect(self) -> None:
            pass

        async def get_state(self) -> RobotState:
            raise NotImplementedError

        async def execute(self, action: str, params: dict[str, Any]) -> TaskResult:
            raise NotImplementedError

        get_sensor = _stub_get_sensor
        subscribe = _stub_subscribe

    async with Engine() as engine:
        with pytest.raises(ConnectionError):
            await engine.register(FailingConnectAdapter())

        assert engine.adapter_names() == []
