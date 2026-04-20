import pytest

from gemm import AdapterConnectionError, Pose, TaskStatus
from gemm.adapters import Adapter, MockAdapter


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
