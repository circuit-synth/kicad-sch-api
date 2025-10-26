"""
Unit tests for ElementParserRegistry.

Tests the parser registry functionality including registration,
dispatching, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from kicad_sch_api.parsers.registry import ElementParserRegistry
from kicad_sch_api.parsers.base import BaseElementParser
from kicad_sch_api.interfaces.parser import IElementParser


_UNSET = object()  # Sentinel value


class MockElementParser(BaseElementParser):
    """Mock parser for testing."""

    def __init__(self, element_type: str, return_value=_UNSET, accept_all=False):
        super().__init__(element_type)
        if return_value is _UNSET:
            self.return_value = {"type": element_type, "test": True}
        else:
            self.return_value = return_value
        self.accept_all = accept_all

    def can_parse(self, element):
        if self.accept_all:
            return True
        return super().can_parse(element)

    def parse_element(self, element):
        return self.return_value


class TestElementParserRegistry:
    """Test cases for ElementParserRegistry."""

    def test_registry_initialization(self):
        """Test registry initializes correctly."""
        registry = ElementParserRegistry()
        assert registry.get_registered_types() == []
        assert not registry.has_parser("test")

    def test_register_parser(self):
        """Test registering a parser."""
        registry = ElementParserRegistry()
        parser = MockElementParser("test")

        registry.register("test", parser)

        assert registry.has_parser("test")
        assert "test" in registry.get_registered_types()

    def test_register_duplicate_parser_warning(self, caplog):
        """Test registering duplicate parser shows warning."""
        registry = ElementParserRegistry()
        parser1 = MockElementParser("test")
        parser2 = MockElementParser("test")

        registry.register("test", parser1)
        registry.register("test", parser2)  # Should warn

        assert "Overriding existing parser" in caplog.text

    def test_unregister_parser(self):
        """Test unregistering a parser."""
        registry = ElementParserRegistry()
        parser = MockElementParser("test")

        registry.register("test", parser)
        assert registry.has_parser("test")

        result = registry.unregister("test")
        assert result is True
        assert not registry.has_parser("test")

    def test_unregister_nonexistent_parser(self):
        """Test unregistering non-existent parser."""
        registry = ElementParserRegistry()

        result = registry.unregister("nonexistent")
        assert result is False

    def test_parse_element_with_registered_parser(self):
        """Test parsing element with registered parser."""
        registry = ElementParserRegistry()
        expected_result = {"type": "test", "value": "success"}
        parser = MockElementParser("test", expected_result)

        registry.register("test", parser)

        element = ["test", "data"]
        result = registry.parse_element(element)

        assert result == expected_result

    def test_parse_element_with_fallback_parser(self):
        """Test parsing unknown element with fallback parser."""
        registry = ElementParserRegistry()
        fallback_result = {"type": "unknown", "fallback": True}
        fallback_parser = MockElementParser("unknown", fallback_result, accept_all=True)

        registry.set_fallback_parser(fallback_parser)

        element = ["unknown_type", "data"]
        result = registry.parse_element(element)

        assert result == fallback_result

    def test_parse_element_no_parser_available(self, caplog):
        """Test parsing element with no available parser."""
        registry = ElementParserRegistry()

        element = ["unknown_type", "data"]
        result = registry.parse_element(element)

        assert result is None
        assert "No parser available" in caplog.text

    def test_parse_invalid_element(self, caplog):
        """Test parsing invalid element."""
        registry = ElementParserRegistry()

        # Test with None
        result = registry.parse_element(None)
        assert result is None

        # Test with empty list
        result = registry.parse_element([])
        assert result is None

        # Test with non-list
        result = registry.parse_element("not a list")
        assert result is None

    def test_parse_elements_multiple(self):
        """Test parsing multiple elements."""
        registry = ElementParserRegistry()
        parser1 = MockElementParser("type1", {"result": 1})
        parser2 = MockElementParser("type2", {"result": 2})

        registry.register("type1", parser1)
        registry.register("type2", parser2)

        elements = [
            ["type1", "data1"],
            ["type2", "data2"],
            ["unknown", "data3"]  # This should be skipped
        ]

        results = registry.parse_elements(elements)

        assert len(results) == 2
        assert {"result": 1} in results
        assert {"result": 2} in results

    def test_clear_registry(self):
        """Test clearing all parsers."""
        registry = ElementParserRegistry()
        parser = MockElementParser("test")

        registry.register("test", parser)
        registry.set_fallback_parser(parser)

        assert registry.has_parser("test")

        registry.clear()

        assert not registry.has_parser("test")
        assert registry.get_registered_types() == []

    def test_get_registered_types(self):
        """Test getting list of registered types."""
        registry = ElementParserRegistry()

        registry.register("type1", MockElementParser("type1"))
        registry.register("type2", MockElementParser("type2"))

        types = registry.get_registered_types()
        assert set(types) == {"type1", "type2"}

    def test_parse_element_parser_failure(self):
        """Test handling parser failure."""
        registry = ElementParserRegistry()

        # Create a parser that explicitly returns None (failure)
        failing_parser = MockElementParser("test", return_value=None)
        registry.register("test", failing_parser)

        element = ["test", "data"]
        result = registry.parse_element(element)

        assert result is None