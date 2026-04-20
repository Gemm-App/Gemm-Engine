import pytest

from gemm.adapters import MockAdapter
from gemm.core.registry import AdapterRegistry
from gemm.errors import AdapterAlreadyRegistered, AdapterNotRegistered


def test_register_and_retrieve():
    registry = AdapterRegistry()
    adapter = MockAdapter(name="r1")
    registry.register(adapter)

    assert registry.get("r1") is adapter
    assert "r1" in registry
    assert len(registry) == 1


def test_register_rejects_duplicate_name():
    registry = AdapterRegistry()
    registry.register(MockAdapter(name="r1"))
    with pytest.raises(AdapterAlreadyRegistered):
        registry.register(MockAdapter(name="r1"))


def test_register_rejects_non_adapter():
    registry = AdapterRegistry()
    with pytest.raises(TypeError):
        registry.register("not an adapter")  # type: ignore[arg-type]


def test_get_missing_raises():
    registry = AdapterRegistry()
    with pytest.raises(AdapterNotRegistered):
        registry.get("ghost")


def test_unregister_returns_adapter_and_removes():
    registry = AdapterRegistry()
    adapter = MockAdapter(name="r1")
    registry.register(adapter)

    removed = registry.unregister("r1")
    assert removed is adapter
    assert "r1" not in registry
    assert len(registry) == 0


def test_unregister_missing_raises():
    registry = AdapterRegistry()
    with pytest.raises(AdapterNotRegistered):
        registry.unregister("ghost")


def test_names_returns_registered():
    registry = AdapterRegistry()
    registry.register(MockAdapter(name="a"))
    registry.register(MockAdapter(name="b"))
    assert set(registry.names()) == {"a", "b"}
