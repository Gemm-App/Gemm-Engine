import pytest

from gemm import Task, TaskResult, TaskStatus


def test_task_initial_state():
    task = Task(adapter_name="r1", action="noop")
    assert task.adapter_name == "r1"
    assert task.action == "noop"
    assert task.params == {}
    assert task.status is TaskStatus.PENDING
    assert task.result is None
    assert task.id


def test_task_ids_are_unique():
    a = Task(adapter_name="r1", action="noop")
    b = Task(adapter_name="r1", action="noop")
    assert a.id != b.id


@pytest.mark.asyncio
async def test_task_wait_returns_result_once_completed():
    task = Task(adapter_name="r1", action="noop")
    task._complete(TaskResult.success(detail="done"))

    result = await task.wait()
    assert result.ok
    assert task.status is TaskStatus.COMPLETED
    assert result.data == {"detail": "done"}


@pytest.mark.asyncio
async def test_task_wait_reflects_failure():
    task = Task(adapter_name="r1", action="noop")
    task._complete(TaskResult.failure("boom"))

    result = await task.wait()
    assert not result.ok
    assert task.status is TaskStatus.FAILED
    assert result.error == "boom"
