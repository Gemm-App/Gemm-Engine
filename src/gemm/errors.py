"""Exception hierarchy for the Gemm framework."""


class GemmError(Exception):
    """Base exception for every error raised by Gemm."""


class AdapterError(GemmError):
    """Base exception for adapter-related failures."""


class AdapterConnectionError(AdapterError):
    """Adapter failed to connect, lost connection, or was used while disconnected."""


class AdapterNotRegistered(AdapterError):
    """Referenced an adapter by name that is not registered with the engine."""


class AdapterAlreadyRegistered(AdapterError):
    """Attempted to register an adapter whose name is already in use."""


class InvalidAction(AdapterError):
    """Adapter was asked to execute an action it does not support."""


class TaskFailed(GemmError):
    """A task was submitted and reported a failure status."""


class EngineClosed(GemmError):
    """Operation was attempted on an Engine that has already been closed."""


class SensorError(GemmError):
    """Base exception for sensor-related failures."""


class SensorNotAvailable(SensorError):
    """The adapter does not support the requested sensor.

    Raise this from ``get_sensor()`` when the sensor name is unknown or the
    hardware is not present on the connected robot.
    """
