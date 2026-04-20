"""AdapterRegistry — stores adapters by name and validates contract compliance."""

from __future__ import annotations

from gemm.adapters.base import Adapter
from gemm.errors import AdapterAlreadyRegistered, AdapterNotRegistered


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, Adapter] = {}

    def register(self, adapter: Adapter) -> None:
        if not isinstance(adapter, Adapter):
            raise TypeError(f"object {adapter!r} does not satisfy the Adapter protocol")
        if adapter.name in self._adapters:
            raise AdapterAlreadyRegistered(f"adapter {adapter.name!r} is already registered")
        self._adapters[adapter.name] = adapter

    def unregister(self, name: str) -> Adapter:
        try:
            return self._adapters.pop(name)
        except KeyError as exc:
            raise AdapterNotRegistered(f"adapter {name!r} is not registered") from exc

    def get(self, name: str) -> Adapter:
        try:
            return self._adapters[name]
        except KeyError as exc:
            raise AdapterNotRegistered(f"adapter {name!r} is not registered") from exc

    def names(self) -> list[str]:
        return list(self._adapters.keys())

    def __contains__(self, name: object) -> bool:
        return name in self._adapters

    def __len__(self) -> int:
        return len(self._adapters)
