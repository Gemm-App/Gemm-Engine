from gemm import (
    BatteryState,
    IMUData,
    LiDARScan,
    MotorState,
    Pose,
    RobotOdometry,
    RobotState,
    TaskResult,
    TaskStatus,
    VideoFrame,
)


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


# ------------------------------------------------------------------ #
# Sensor type tests                                                   #
# ------------------------------------------------------------------ #


def test_imu_data_fields():
    imu = IMUData(
        quaternion=(1.0, 0.0, 0.0, 0.0),
        angular_velocity=(0.1, 0.0, 0.0),
        linear_acceleration=(0.0, 0.0, 9.81),
        rpy=(0.0, 0.0, 1.57),
        temperature=35.0,
    )
    assert imu.quaternion == (1.0, 0.0, 0.0, 0.0)
    assert imu.rpy[2] == 1.57
    assert imu.temperature == 35.0


def test_imu_data_is_immutable():
    imu = IMUData(
        quaternion=(1.0, 0.0, 0.0, 0.0),
        angular_velocity=(0.0, 0.0, 0.0),
        linear_acceleration=(0.0, 0.0, 9.81),
        rpy=(0.0, 0.0, 0.0),
    )
    try:
        imu.temperature = 99.0  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("IMUData should be frozen")


def test_battery_state_fields():
    b = BatteryState(soc=0.8, voltage=25.2, current=-1.5, temperature=28.0, cycle_count=42)
    assert b.soc == 0.8
    assert b.voltage == 25.2
    assert b.current == -1.5
    assert b.cycle_count == 42


def test_battery_state_temperature_defaults_to_zero():
    b = BatteryState(soc=1.0, voltage=25.0, current=0.0)
    assert b.temperature == 0.0


def test_motor_state_fields():
    m = MotorState(index=3, position=0.5, velocity=0.1, torque=2.5, temperature=45.0)
    assert m.index == 3
    assert m.position == 0.5
    assert m.torque == 2.5


def test_lidar_scan_len():
    pts = [(1.0, 2.0, 0.0), (3.0, 4.0, 0.1)]
    scan = LiDARScan(points=pts, origin=(0.0, 0.0, 0.0), resolution=0.05)
    assert len(scan) == 2
    assert scan.points[0] == (1.0, 2.0, 0.0)


def test_robot_odometry_fields():
    odom = RobotOdometry(
        position=(1.0, 2.0, 0.0),
        orientation=(1.0, 0.0, 0.0, 0.0),
        linear_velocity=(0.5, 0.0, 0.0),
        angular_velocity=(0.0, 0.0, 0.1),
    )
    assert odom.position == (1.0, 2.0, 0.0)
    assert odom.linear_velocity[0] == 0.5


def test_video_frame_fields():
    frame = VideoFrame(data=b"\xff\x00\x00", width=1280, height=720, encoding="bgr24")
    assert frame.width == 1280
    assert frame.encoding == "bgr24"
    assert frame.timestamp == 0.0
