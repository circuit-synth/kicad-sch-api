"""Unit tests for BaseManager abstract class."""

import pytest

from kicad_sch_api.core.managers.base import BaseManager
from kicad_sch_api.utils.validation import ValidationIssue


class ConcreteManager(BaseManager):
    """Concrete implementation of BaseManager for testing."""

    def __init__(self, schematic_data=None, **kwargs):
        super().__init__(schematic_data, **kwargs)
        self.custom_attr = kwargs.get("custom_attr", "default")


def test_base_manager_initialization_no_data():
    """Test BaseManager can be initialized without data."""
    manager = ConcreteManager()

    assert manager.data is None
    assert manager.schematic is None


def test_base_manager_initialization_with_data():
    """Test BaseManager can be initialized with schematic data."""
    test_data = {"version": "20230121", "uuid": "test-uuid"}
    manager = ConcreteManager(test_data)

    assert manager.data == test_data
    assert manager.schematic is None


def test_base_manager_set_schematic():
    """Test setting schematic reference."""
    manager = ConcreteManager()

    # Mock schematic object
    mock_schematic = type("MockSchematic", (), {})()

    manager.set_schematic(mock_schematic)

    assert manager.schematic == mock_schematic


def test_base_manager_schematic_property():
    """Test schematic property getter."""
    manager = ConcreteManager()
    mock_schematic = type("MockSchematic", (), {})()

    assert manager.schematic is None

    manager.set_schematic(mock_schematic)

    assert manager.schematic == mock_schematic


def test_base_manager_data_property():
    """Test data property getter."""
    test_data = {"test": "value"}
    manager = ConcreteManager(test_data)

    assert manager.data == test_data


def test_base_manager_validate_default():
    """Test default validate() returns empty list."""
    manager = ConcreteManager()

    issues = manager.validate()

    assert isinstance(issues, list)
    assert len(issues) == 0


def test_base_manager_with_kwargs():
    """Test BaseManager passes through additional kwargs."""
    test_data = {"version": "20230121"}
    manager = ConcreteManager(test_data, custom_attr="custom_value")

    assert manager.data == test_data
    assert manager.custom_attr == "custom_value"


def test_base_manager_inheritance():
    """Test that ConcreteManager properly inherits from BaseManager."""
    manager = ConcreteManager()

    assert isinstance(manager, BaseManager)
    assert hasattr(manager, "data")
    assert hasattr(manager, "schematic")
    assert hasattr(manager, "set_schematic")
    assert hasattr(manager, "validate")


def test_base_manager_validate_override():
    """Test that validate() can be overridden."""
    from kicad_sch_api.utils.validation import ValidationLevel

    class CustomManager(BaseManager):
        def validate(self):
            return [
                ValidationIssue(
                    category="test", message="Custom validation", level=ValidationLevel.WARNING
                )
            ]

    manager = CustomManager()
    issues = manager.validate()

    assert len(issues) == 1
    assert issues[0].level == ValidationLevel.WARNING
    assert issues[0].message == "Custom validation"


def test_base_manager_multiple_managers_independent():
    """Test that multiple manager instances are independent."""
    data1 = {"uuid": "uuid-1"}
    data2 = {"uuid": "uuid-2"}

    manager1 = ConcreteManager(data1)
    manager2 = ConcreteManager(data2)

    assert manager1.data == data1
    assert manager2.data == data2
    assert manager1.data is not manager2.data


def test_base_manager_schematic_independence():
    """Test that schematic references are independent across managers."""
    manager1 = ConcreteManager()
    manager2 = ConcreteManager()

    schematic1 = type("Schematic1", (), {})()
    schematic2 = type("Schematic2", (), {})()

    manager1.set_schematic(schematic1)
    manager2.set_schematic(schematic2)

    assert manager1.schematic == schematic1
    assert manager2.schematic == schematic2
    assert manager1.schematic is not manager2.schematic
