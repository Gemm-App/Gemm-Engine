from gemm import Pose, RobotState, TaskResult, TaskStatus


def test_pose_has_zero_defaults_for_z_and_yaw():
    p = Pose(x=1.0, y=2.0)
    assert p.z == 0.0
    assert p.yaw == 0.0


def test_pose_is_immutable():
    p = Pose(x=1.0, y=2.0)
    try:
        p.x = 5.0  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("Pose should be frozen")


def test_task_result_success_is_ok():
    r = TaskResult.success(pose=Pose(x=1.0, y=2.0))
    assert r.ok
    assert r.status is TaskStatus.COMPLETED
    assert r.error is None
    assert "pose" in r.data


def test_task_result_failure_is_not_ok():
    r = TaskResult.failure("sensor timeout")
    assert not r.ok
    assert r.status is TaskStatus.FAILED
    assert r.error == "sensor timeout"


def test_robot_state_defaults_metadata_to_empty_dict():
    s = RobotState(pose=Pose(x=0.0, y=0.0), battery=0.5)
    assert s.metadata == {}
    assert s.battery == 0.5
