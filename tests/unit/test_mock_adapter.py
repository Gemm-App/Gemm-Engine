import pytest

from gemm import AdapterConnectionError, Pose, SensorNotAvailable, TaskStatus
from gemm.adapters import Adapter, MockAdapter
from gemm.types import BatteryState, IMUData, RobotOdometry


@pytest.fixture
def adapter() -> MockAdapter:
    return MockAdapter(name="gemm/mock")


def test_mock_adapter_satisfies_protocol(adapter: MockAdapter):
    assert isinstance(adapter, Adapter)


@pytest.mark.asyncio
async def test_connect_then_disconnect(adapter: MockAdapter):
    await adapter.connect()
    await adapter.disconnect()


@pytest.mark.asyncio
async def test_operations_before_connect_raise(adapter: MockAdapter):
    with pytest.raises(AdapterConnectionError):
        await adapter.get_state()
    with pytest.raises(AdapterConnectionError):
        await adapter.execute("noop", {})


@pytest.mark.asyncio
async def test_initial_state(adapter: MockAdapter):
    await adapter.connect()
    state = await adapter.get_state()
    assert state.pose == Pose(x=0.0, y=0.0)
    assert state.battery == pytest.approx(1.0)
    assert state.metadata == {}


@pytest.mark.asyncio
async def test_move_to_updates_pose(adapter: MockAdapter):
    await adapter.connect()
    result = await adapter.execute("move_to", {"x": 3.0, "y": 4.0, "yaw": 1.5})
    assert result.ok
    assert result.status is TaskStatus.COMPLETED

    state = await adapter.get_state()
    assert state.pose == Pose(x=3.0, y=4.0, yaw=1.5)


@pytest.mark.asyncio
async def test_noop_action_succeeds(adapter: MockAdapter):
    await adapter.connect()
    result = await adapter.execute("noop", {})
    assert result.ok


@pytest.mark.asyncio
async def test_unknown_action_returns_failure(adapter: MockAdapter):
    await adapter.connect()
    result = await adapter.execute("fly_to_the_moon", {})
    assert not result.ok
    assert result.status is TaskStatus.FAILED
    assert result.error is not None
    assert "fly_to_the_moon" in result.error


@pytest.mark.asyncio
async def test_disconnect_blocks_further_ops(adapter: MockAdapter):
    await adapter.connect()
    await adapter.disconnect()
    with pytest.raises(AdapterConnectionError):
        await adapter.execute("noop", {})


@pytest.mark.asyncio
async def test_execution_delay_awaits():
    slow = MockAdapter(name="slow", execution_delay=0.01)
    await slow.connect()
    result = await slow.execute("noop", {})
    assert result.ok


# ------------------------------------------------------------------ #
# Sensor tests                                                        #
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_get_sensor_battery_returns_battery_state(adapter: MockAdapter):
    await adapter.connect()
    reading = await adapter.get_sensor("battery")
    assert isinstance(reading, BatteryState)
    assert 0.0 <= reading.soc <= 1.0
    assert reading.voltage > 0


@pytest.mark.asyncio
async def test_get_sensor_imu_returns_imu_data(adapter: MockAdapter):
    await adapter.connect()
    reading = await adapter.get_sensor("imu")
    assert isinstance(reading, IMUData)
    assert len(reading.quaternion) == 4
    assert len(reading.rpy) == 3


@pytest.mark.asyncio
async def test_get_sensor_odometry_returns_robot_odometry(adapter: MockAdapter):
    await adapter.connect()
    reading = await adapter.get_sensor("odometry")
    assert isinstance(reading, RobotOdometry)
    assert len(reading.position) == 3
    assert len(reading.orientation) == 4


@pytest.mark.asyncio
async def test_get_sensor_unknown_raises(adapter: MockAdapter):
    await adapter.connect()
    with pytest.raises(SensorNotAvailable):
        await adapter.get_sensor("lidar")


@pytest.mark.asyncio
async def test_get_sensor_before_connect_raises(adapter: MockAdapter):
    with pytest.raises(AdapterConnectionError):
        await adapter.get_sensor("battery")


@pytest.mark.asyncio
async def test_subscribe_returns_callable(adapter: MockAdapter):
    await adapter.connect()
    unsubscribe = adapter.subscribe("battery", lambda _: None)
    assert callable(unsubscribe)
    unsubscribe()


@pytest.mark.asyncio
async def test_subscribe_callback_fired_by_fire_sensor(adapter: MockAdapter):
    await adapter.connect()
    received = []
    adapter.subscribe("battery", received.append)
    reading = BatteryState(soc=0.8, voltage=24.0, current=-2.0)
    adapter._fire_sensor("battery", reading)
    assert received == [reading]


@pytest.mark.asyncio
async def test_unsubscribe_stops_callbacks(adapter: MockAdapter):
    await adapter.connect()
    received = []
    unsubscribe = adapter.subscribe("battery", received.append)
    unsubscribe()
    adapter._fire_sensor("battery", BatteryState(soc=0.5, voltage=24.0, current=-1.0))
    assert received == []


@pytest.mark.asyncio
async def test_subscribe_unknown_sensor_raises(adapter: MockAdapter):
    await adapter.connect()
    with pytest.raises(SensorNotAvailable):
        adapter.subscribe("lidar", lambda _: None)


@pytest.mark.asyncio
async def test_disconnect_clears_subscriptions(adapter: MockAdapter):
    await adapter.connect()
    received = []
    adapter.subscribe("battery", received.append)
    await adapter.disconnect()
    # After reconnect, old subscription is gone
    await adapter.connect()
    adapter._fire_sensor("battery", BatteryState(soc=1.0, voltage=25.0, current=0.0))
    assert received == []
