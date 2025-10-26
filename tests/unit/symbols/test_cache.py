"""
Unit tests for symbol cache interface and implementation.

Tests the symbol caching functionality while maintaining separation
from inheritance resolution concerns.
"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from kicad_sch_api.core.types import Point
from kicad_sch_api.library.cache import SymbolDefinition
from kicad_sch_api.symbols.cache import ISymbolCache, SymbolCache


class MockSymbolCache(ISymbolCache):
    """Mock implementation for testing interfaces."""

    def __init__(self):
        self.symbols = {}
        self.libraries = set()

    def get_symbol(self, lib_id: str):
        return self.symbols.get(lib_id)

    def has_symbol(self, lib_id: str) -> bool:
        return lib_id in self.symbols

    def add_library_path(self, library_path) -> bool:
        self.libraries.add(str(library_path))
        return True

    def get_library_symbols(self, library_name: str):
        return [lid for lid in self.symbols.keys() if lid.startswith(f"{library_name}:")]

    def clear_cache(self) -> None:
        self.symbols.clear()

    def get_cache_statistics(self):
        return {"symbols_cached": len(self.symbols)}


class TestISymbolCache:
    """Test cases for ISymbolCache interface."""

    def test_interface_compliance(self):
        """Test that mock implementation satisfies interface."""
        cache = MockSymbolCache()
        assert isinstance(cache, ISymbolCache)

        # Test all interface methods exist
        assert hasattr(cache, "get_symbol")
        assert hasattr(cache, "has_symbol")
        assert hasattr(cache, "add_library_path")
        assert hasattr(cache, "get_library_symbols")
        assert hasattr(cache, "clear_cache")
        assert hasattr(cache, "get_cache_statistics")

    def test_mock_cache_basic_operations(self):
        """Test basic operations on mock cache."""
        cache = MockSymbolCache()

        # Initially empty
        assert not cache.has_symbol("Device:R")
        assert cache.get_symbol("Device:R") is None

        # Add symbol
        symbol = SymbolDefinition(
            lib_id="Device:R", name="R", library="Device", reference_prefix="R"
        )
        cache.symbols["Device:R"] = symbol

        # Now should find it
        assert cache.has_symbol("Device:R")
        assert cache.get_symbol("Device:R") is symbol

        # Clear cache
        cache.clear_cache()
        assert not cache.has_symbol("Device:R")


class TestSymbolCache:
    """Test cases for SymbolCache implementation."""

    def test_cache_initialization(self):
        """Test cache initializes correctly."""
        cache = SymbolCache(enable_persistence=False)

        assert len(cache._symbols) == 0
        assert len(cache._library_paths) == 0
        assert cache._cache_hits == 0
        assert cache._cache_misses == 0

    def test_cache_initialization_with_persistence(self, tmp_path):
        """Test cache initialization with persistence enabled."""
        cache_dir = tmp_path / "cache"
        cache = SymbolCache(cache_dir=cache_dir, enable_persistence=True)

        assert cache._cache_dir == cache_dir
        assert cache_dir.exists()

    def test_add_library_path_valid(self, tmp_path):
        """Test adding valid library path."""
        cache = SymbolCache(enable_persistence=False)

        # Create mock library file
        lib_file = tmp_path / "test.kicad_sym"
        lib_file.write_text("(kicad_symbol_lib)")

        result = cache.add_library_path(lib_file)

        assert result is True
        assert lib_file in cache._library_paths
        assert "test" in cache._library_index

    def test_add_library_path_nonexistent(self):
        """Test adding non-existent library path."""
        cache = SymbolCache(enable_persistence=False)

        result = cache.add_library_path("/nonexistent/path.kicad_sym")

        assert result is False
        assert len(cache._library_paths) == 0

    def test_add_library_path_wrong_extension(self, tmp_path):
        """Test adding file with wrong extension."""
        cache = SymbolCache(enable_persistence=False)

        # Create file with wrong extension
        wrong_file = tmp_path / "test.txt"
        wrong_file.write_text("content")

        result = cache.add_library_path(wrong_file)

        assert result is False
        assert len(cache._library_paths) == 0

    def test_add_library_path_duplicate(self, tmp_path):
        """Test adding duplicate library path."""
        cache = SymbolCache(enable_persistence=False)

        lib_file = tmp_path / "test.kicad_sym"
        lib_file.write_text("(kicad_symbol_lib)")

        # Add twice
        result1 = cache.add_library_path(lib_file)
        result2 = cache.add_library_path(lib_file)

        assert result1 is True
        assert result2 is True  # Should still return True
        assert len(cache._library_paths) == 1

    def test_get_symbol_not_found(self):
        """Test getting non-existent symbol."""
        cache = SymbolCache(enable_persistence=False)

        symbol = cache.get_symbol("Device:R")

        assert symbol is None
        assert cache._cache_misses == 1
        assert cache._cache_hits == 0

    def test_has_symbol_not_found(self):
        """Test checking for non-existent symbol."""
        cache = SymbolCache(enable_persistence=False)

        result = cache.has_symbol("Device:R")

        assert result is False

    def test_clear_cache(self):
        """Test clearing cache."""
        cache = SymbolCache(enable_persistence=False)

        # Add some data
        cache._symbols["Device:R"] = Mock()
        cache._cache_hits = 5
        cache._cache_misses = 2

        cache.clear_cache()

        assert len(cache._symbols) == 0
        assert cache._cache_hits == 0
        assert cache._cache_misses == 0

    def test_get_cache_statistics(self):
        """Test getting cache statistics."""
        cache = SymbolCache(enable_persistence=False)

        # Add some data
        cache._symbols["Device:R"] = Mock()
        cache._cache_hits = 10
        cache._cache_misses = 3

        stats = cache.get_cache_statistics()

        assert stats["symbols_cached"] == 1
        assert stats["cache_hits"] == 10
        assert stats["cache_misses"] == 3
        assert stats["hit_rate_percent"] == 10 / 13 * 100

    def test_get_library_symbols_empty(self):
        """Test getting symbols from non-existent library."""
        cache = SymbolCache(enable_persistence=False)

        symbols = cache.get_library_symbols("NonExistent")

        assert symbols == []

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
        (kicad_symbol_lib
          (symbol "R" (pin_numbers hide)
            (property "Reference" "R" (id 0))
            (property "Value" "R" (id 1))
          )
          (symbol "C" (pin_numbers hide)
            (property "Reference" "C" (id 0))
            (property "Value" "C" (id 1))
          )
        )
    """,
    )
    def test_get_library_symbols_with_content(self, mock_file, tmp_path):
        """Test getting symbols from library with content."""
        cache = SymbolCache(enable_persistence=False)

        lib_file = tmp_path / "Device.kicad_sym"
        lib_file.write_text("content")  # Content doesn't matter, we mock the read

        cache.add_library_path(lib_file)
        symbols = cache.get_library_symbols("Device")

        assert "Device:R" in symbols
        assert "Device:C" in symbols
        assert len(symbols) == 2

    def test_load_symbol_invalid_lib_id(self):
        """Test loading symbol with invalid lib_id."""
        cache = SymbolCache(enable_persistence=False)

        symbol = cache._load_symbol_from_library("invalid_format")

        assert symbol is None

    def test_check_extends_directive_none(self):
        """Test checking extends directive on symbol without extends."""
        cache = SymbolCache(enable_persistence=False)

        # Symbol data without extends
        symbol_data = ["symbol", "R", ["property", "Reference", "R"]]

        extends = cache._check_extends_directive(symbol_data)

        assert extends is None

    def test_check_extends_directive_found(self):
        """Test checking extends directive on symbol with extends."""
        cache = SymbolCache(enable_persistence=False)

        import sexpdata

        # Symbol data with extends
        symbol_data = ["symbol", "R_Special", ["extends", "R"], ["property", "Reference", "R"]]

        extends = cache._check_extends_directive(symbol_data)

        assert extends == "R"

    def test_can_load_symbol_valid(self, tmp_path):
        """Test checking if symbol can be loaded."""
        cache = SymbolCache(enable_persistence=False)

        lib_file = tmp_path / "Device.kicad_sym"
        lib_file.write_text("(kicad_symbol_lib)")
        cache.add_library_path(lib_file)

        result = cache._can_load_symbol("Device:R")

        assert result is True

    def test_can_load_symbol_invalid_lib_id(self):
        """Test checking if symbol with invalid lib_id can be loaded."""
        cache = SymbolCache(enable_persistence=False)

        result = cache._can_load_symbol("invalid_format")

        assert result is False

    def test_can_load_symbol_unknown_library(self):
        """Test checking if symbol from unknown library can be loaded."""
        cache = SymbolCache(enable_persistence=False)

        result = cache._can_load_symbol("Unknown:R")

        assert result is False

    def test_extract_symbol_properties_basic(self):
        """Test extracting basic symbol properties."""
        cache = SymbolCache(enable_persistence=False)

        symbol_data = [
            "symbol",
            "R",
            ["property", "Reference", "R?"],
            ["property", "ki_description", "Resistor"],
            ["property", "ki_keywords", "passive"],
        ]

        properties = cache._extract_symbol_properties(symbol_data)

        assert properties["reference_prefix"] == "R"
        assert properties["description"] == "Resistor"
        assert properties["keywords"] == "passive"

    def test_extract_symbol_properties_empty(self):
        """Test extracting properties from symbol with no properties."""
        cache = SymbolCache(enable_persistence=False)

        symbol_data = ["symbol", "R"]

        properties = cache._extract_symbol_properties(symbol_data)

        assert properties["reference_prefix"] == "U"  # Default
        assert properties["description"] == ""
        assert properties["keywords"] == ""

    def test_find_symbol_in_parsed_data_found(self):
        """Test finding symbol in parsed library data."""
        cache = SymbolCache(enable_persistence=False)

        import sexpdata

        parsed_data = [
            sexpdata.Symbol("kicad_symbol_lib"),
            ["symbol", "R", ["property", "Reference", "R"]],
            ["symbol", "C", ["property", "Reference", "C"]],
        ]

        symbol_data = cache._find_symbol_in_parsed_data(parsed_data, "R")

        assert symbol_data is not None
        assert symbol_data[1] == "R"

    def test_find_symbol_in_parsed_data_not_found(self):
        """Test finding non-existent symbol in parsed library data."""
        cache = SymbolCache(enable_persistence=False)

        import sexpdata

        parsed_data = [
            sexpdata.Symbol("kicad_symbol_lib"),
            ["symbol", "R", ["property", "Reference", "R"]],
        ]

        symbol_data = cache._find_symbol_in_parsed_data(parsed_data, "NotFound")

        assert symbol_data is None
