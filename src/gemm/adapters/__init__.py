"""Adapter contract and bundled reference adapters."""

from gemm.adapters.base import Adapter
from gemm.adapters.mock import MockAdapter

__all__ = ["Adapter", "MockAdapter"]
