# Sensors

The Gemm sensor interface gives adapters a standard way to expose hardware
sensors — IMU, battery, LiDAR, odometry, motors, video — with consistent
return types, regardless of the underlying robot brand.

## Two access patterns

### One-shot read

```python
from gemm import IMUData

imu: IMUData = await adapter.get_sensor("imu")
print(imu.rpy)          # (roll, pitch, yaw) in radians
print(imu.quaternion)   # (w, x, y, z)
```

`get_sensor()` always returns the **latest cached value**. It is cheap to call
and never blocks on hardware I/O — the adapter maintains an internal cache
updated by the robot's streaming data.

### Real-time subscription

```python
def on_battery(reading):
    print(f"battery: {reading.soc * 100:.1f}%  {reading.voltage:.1f} V")

unsubscribe = adapter.subscribe("battery", on_battery)

# ... later, to stop:
unsubscribe()
```

`subscribe()` returns an **unsubscribe callable**. Call it with no arguments
when you no longer need the data. Callbacks must not block — offload heavy
work to an `asyncio.Task`.

## Well-known sensor names

| Name | Return type | Typical update rate |
| --- | --- | --- |
| `"imu"` | `IMUData` | ~500 Hz |
| `"battery"` | `BatteryState` | ~1 Hz |
| `"odometry"` | `RobotOdometry` | ~50 Hz |
| `"motors"` | `list[MotorState]` | ~50 Hz |
| `"sport_state"` | `RobotState` | ~50 Hz |
| `"lidar"` | `LiDARScan` | ~10 Hz |
| `"video"` | `VideoFrame` | ~30 Hz |

Not every adapter supports every sensor. Call `get_sensor()` and handle
`SensorNotAvailable` if you need to work across robot brands.

## Sensor types

### `IMUData`

```python
@dataclass(frozen=True, slots=True)
class IMUData:
    quaternion: tuple[float, float, float, float]  # w, x, y, z
    angular_velocity: tuple[float, float, float]   # rad/s
    linear_acceleration: tuple[float, float, float] # m/s²
    rpy: tuple[float, float, float]                # roll, pitch, yaw (rad)
    temperature: float                              # °C
```

### `BatteryState`

```python
@dataclass(frozen=True, slots=True)
class BatteryState:
    soc: float         # 0.0–1.0 (0 % → 100 %)
    voltage: float     # volts
    current: float     # amps (negative = discharging)
    temperature: float # °C
    cycle_count: int   # charge cycles
```

### `MotorState`

```python
@dataclass(frozen=True, slots=True)
class MotorState:
    index: int     # hardware motor index
    position: float  # joint angle (rad)
    velocity: float  # joint velocity (rad/s)
    torque: float    # estimated torque (N·m)
    temperature: float # °C
```

### `RobotOdometry`

```python
@dataclass(frozen=True, slots=True)
class RobotOdometry:
    position: tuple[float, float, float]            # x, y, z (m)
    orientation: tuple[float, float, float, float]  # quaternion w, x, y, z
    linear_velocity: tuple[float, float, float]     # m/s
    angular_velocity: tuple[float, float, float]    # rad/s
```

Position is in the SLAM odometry frame. The origin `(0, 0, 0)` is where the
robot initialised its SLAM session.

### `LiDARScan`

```python
@dataclass(slots=True)
class LiDARScan:
    points: list[tuple[float, float, float]]  # (x, y, z) in metres
    origin: tuple[float, float, float]         # voxel grid origin
    resolution: float                           # voxel size (m)
    timestamp: float                            # unix time

    def __len__(self) -> int: ...
```

### `VideoFrame`

```python
@dataclass(slots=True)
class VideoFrame:
    data: bytes    # raw pixel data
    width: int
    height: int
    encoding: str  # "bgr24", "rgb24", "jpeg"
    timestamp: float
```

## Error handling

```python
from gemm import SensorNotAvailable

try:
    lidar = await adapter.get_sensor("lidar")
except SensorNotAvailable:
    print("this robot has no LiDAR")
```

`SensorNotAvailable` is raised when:
- The sensor name is not recognised by the adapter.
- The hardware is not present on the connected robot model.

`AdapterConnectionError` is raised if `get_sensor()` or `subscribe()` is
called before `connect()`.

## Multi-sensor fan-out

```python
import asyncio

imu, battery, odom = await asyncio.gather(
    adapter.get_sensor("imu"),
    adapter.get_sensor("battery"),
    adapter.get_sensor("odometry"),
)
```

## Full example

```python
import asyncio
from gemm import Engine, SensorNotAvailable
from gemm.adapters import MockAdapter

async def main():
    async with Engine() as engine:
        await engine.register(MockAdapter(name="r1"))
        adapter = engine._registry.get("r1")  # direct access for sensor API

        # One-shot
        battery = await adapter.get_sensor("battery")
        print(f"battery: {battery.soc * 100:.0f}%")

        # Real-time subscription
        def on_imu(data):
            print(f"yaw: {data.rpy[2]:.3f} rad")

        unsubscribe = adapter.subscribe("imu", on_imu)
        await asyncio.sleep(5)
        unsubscribe()

asyncio.run(main())
```
