"""Core runtime: engine and adapter registry."""

from gemm.core.engine import Engine
from gemm.core.registry import AdapterRegistry

__all__ = ["AdapterRegistry", "Engine"]
