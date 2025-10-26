"""
Unit tests for symbol inheritance resolution.

Tests the SymbolResolver functionality for inheritance chain resolution
while maintaining separation from caching concerns.
"""

from unittest.mock import Mock, patch

import pytest

from kicad_sch_api.core.types import Point, SchematicPin
from kicad_sch_api.library.cache import SymbolDefinition
from kicad_sch_api.symbols.cache import ISymbolCache
from kicad_sch_api.symbols.resolver import SymbolResolver


class MockCache(ISymbolCache):
    """Mock cache for testing resolver."""

    def __init__(self):
        self.symbols = {}

    def get_symbol(self, lib_id: str):
        return self.symbols.get(lib_id)

    def has_symbol(self, lib_id: str) -> bool:
        return lib_id in self.symbols

    def add_library_path(self, library_path) -> bool:
        return True

    def get_library_symbols(self, library_name: str):
        return []

    def clear_cache(self) -> None:
        self.symbols.clear()

    def get_cache_statistics(self):
        return {}


class TestSymbolResolver:
    """Test cases for SymbolResolver."""

    def test_resolver_initialization(self):
        """Test resolver initializes correctly."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        assert resolver._cache is cache
        assert len(resolver._inheritance_cache) == 0
        assert len(resolver._resolution_stack) == 0

    def test_resolve_symbol_not_found(self):
        """Test resolving non-existent symbol."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        result = resolver.resolve_symbol("Device:NotFound")

        assert result is None

    def test_resolve_symbol_no_inheritance(self):
        """Test resolving symbol without inheritance."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create symbol without extends
        symbol = SymbolDefinition(
            lib_id="Device:R", name="R", library="Device", reference_prefix="R", extends=None
        )
        cache.symbols["Device:R"] = symbol

        result = resolver.resolve_symbol("Device:R")

        assert result is not None
        assert result.lib_id == "Device:R"
        assert result.extends is None
        assert result is not symbol  # Should be a copy

    def test_resolve_symbol_with_inheritance(self):
        """Test resolving symbol with inheritance."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create parent symbol
        parent = SymbolDefinition(
            lib_id="Device:R_Generic",
            name="R_Generic",
            library="Device",
            reference_prefix="R",
            description="Generic resistor",
            extends=None,
        )
        cache.symbols["Device:R_Generic"] = parent

        # Create child symbol that extends parent
        child = SymbolDefinition(
            lib_id="Device:R_Special",
            name="R_Special",
            library="Device",
            reference_prefix="R",
            extends="R_Generic",
        )
        cache.symbols["Device:R_Special"] = child

        result = resolver.resolve_symbol("Device:R_Special")

        assert result is not None
        assert result.lib_id == "Device:R_Special"
        assert result.extends is None  # Should be cleared after resolution
        assert result.description == "Generic resistor"  # Inherited from parent

    def test_resolve_symbol_inheritance_chain(self):
        """Test resolving symbol with inheritance chain."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create inheritance chain: grandparent -> parent -> child
        grandparent = SymbolDefinition(
            lib_id="Device:R_Base",
            name="R_Base",
            library="Device",
            reference_prefix="R",
            description="Base resistor",
            keywords="passive",
            extends=None,
        )
        cache.symbols["Device:R_Base"] = grandparent

        parent = SymbolDefinition(
            lib_id="Device:R_Generic",
            name="R_Generic",
            library="Device",
            reference_prefix="R",
            datasheet="http://example.com",
            extends="R_Base",
        )
        cache.symbols["Device:R_Generic"] = parent

        child = SymbolDefinition(
            lib_id="Device:R_Special",
            name="R_Special",
            library="Device",
            reference_prefix="R",
            extends="R_Generic",
        )
        cache.symbols["Device:R_Special"] = child

        result = resolver.resolve_symbol("Device:R_Special")

        assert result is not None
        assert result.lib_id == "Device:R_Special"
        assert result.extends is None
        assert result.description == "Base resistor"  # From grandparent
        assert result.keywords == "passive"  # From grandparent
        assert result.datasheet == "http://example.com"  # From parent
        assert hasattr(result, "_inheritance_depth")
        assert result._inheritance_depth == 2

    def test_resolve_symbol_missing_parent(self):
        """Test resolving symbol with missing parent."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create child symbol that extends non-existent parent
        child = SymbolDefinition(
            lib_id="Device:R_Special",
            name="R_Special",
            library="Device",
            reference_prefix="R",
            extends="NonExistent",
        )
        cache.symbols["Device:R_Special"] = child

        result = resolver.resolve_symbol("Device:R_Special")

        assert result is None

    def test_resolve_symbol_circular_inheritance(self):
        """Test resolving symbol with circular inheritance."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create circular inheritance: A -> B -> A
        symbol_a = SymbolDefinition(
            lib_id="Device:A", name="A", library="Device", reference_prefix="U", extends="B"
        )
        cache.symbols["Device:A"] = symbol_a

        symbol_b = SymbolDefinition(
            lib_id="Device:B", name="B", library="Device", reference_prefix="U", extends="A"
        )
        cache.symbols["Device:B"] = symbol_b

        result = resolver.resolve_symbol("Device:A")

        assert result is None

    def test_resolve_symbol_caching(self):
        """Test that resolved symbols are cached."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create symbol
        symbol = SymbolDefinition(
            lib_id="Device:R", name="R", library="Device", reference_prefix="R", extends=None
        )
        cache.symbols["Device:R"] = symbol

        # First resolution
        result1 = resolver.resolve_symbol("Device:R")
        assert result1 is not None

        # Second resolution should return cached result
        result2 = resolver.resolve_symbol("Device:R")
        assert result2 is result1  # Same object from cache

    def test_clear_inheritance_cache(self):
        """Test clearing inheritance cache."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Add something to cache
        symbol = SymbolDefinition(
            lib_id="Device:R", name="R", library="Device", reference_prefix="R", extends=None
        )
        cache.symbols["Device:R"] = symbol
        resolver.resolve_symbol("Device:R")

        assert len(resolver._inheritance_cache) == 1

        resolver.clear_inheritance_cache()

        assert len(resolver._inheritance_cache) == 0

    def test_get_inheritance_statistics(self):
        """Test getting inheritance statistics."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create symbols with inheritance
        parent = SymbolDefinition(
            lib_id="Device:R_Base",
            name="R_Base",
            library="Device",
            reference_prefix="R",
            extends=None,
        )
        cache.symbols["Device:R_Base"] = parent

        child = SymbolDefinition(
            lib_id="Device:R_Special",
            name="R_Special",
            library="Device",
            reference_prefix="R",
            extends="R_Base",
        )
        cache.symbols["Device:R_Special"] = child

        # Resolve symbols
        resolver.resolve_symbol("Device:R_Base")
        resolver.resolve_symbol("Device:R_Special")

        stats = resolver.get_inheritance_statistics()

        assert stats["resolved_symbols"] == 2
        assert "inheritance_chains" in stats
        assert "max_chain_length" in stats

    def test_resolve_parent_lib_id_with_library(self):
        """Test resolving parent lib_id with library prefix."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        parent_lib_id = resolver._resolve_parent_lib_id("OtherLib:Symbol", "Device")

        assert parent_lib_id == "OtherLib:Symbol"

    def test_resolve_parent_lib_id_same_library(self):
        """Test resolving parent lib_id in same library."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        parent_lib_id = resolver._resolve_parent_lib_id("ParentSymbol", "Device")

        assert parent_lib_id == "Device:ParentSymbol"

    def test_merge_symbol_properties(self):
        """Test merging symbol properties."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create parent with properties
        parent = SymbolDefinition(
            lib_id="Device:Parent",
            name="Parent",
            library="Device",
            reference_prefix="U",
            description="Parent description",
            keywords="parent keywords",
            datasheet="parent datasheet",
            pins=[SchematicPin(number="1", name="Pin1", position=Point(0, 0), pin_type="input")],
            units=2,
            unit_names={1: "Unit A", 2: "Unit B"},
        )

        # Create child with some properties
        child = SymbolDefinition(
            lib_id="Device:Child",
            name="Child",
            library="Device",
            reference_prefix="U",
            description="Child description",  # This should take precedence
            pins=[SchematicPin(number="2", name="Pin2", position=Point(1, 1), pin_type="output")],
            units=1,
            unit_names={1: "Main"},
        )

        merged = resolver._merge_symbol_properties(child, parent)

        # Child properties should take precedence
        assert merged.description == "Child description"
        assert merged.keywords == "parent keywords"  # Inherited
        assert merged.datasheet == "parent datasheet"  # Inherited

        # Pins should be merged
        assert len(merged.pins) == 2
        pin_numbers = [pin.number for pin in merged.pins]
        assert "1" in pin_numbers  # From parent
        assert "2" in pin_numbers  # From child

        # Units should be maximum
        assert merged.units == 2  # Parent has more units

        # Unit names should be merged
        assert 1 in merged.unit_names
        assert 2 in merged.unit_names

    def test_validate_inheritance_chain_valid(self):
        """Test validating valid inheritance chain."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create valid chain
        parent = SymbolDefinition(
            lib_id="Device:Parent",
            name="Parent",
            library="Device",
            reference_prefix="U",
            extends=None,
        )
        cache.symbols["Device:Parent"] = parent

        child = SymbolDefinition(
            lib_id="Device:Child",
            name="Child",
            library="Device",
            reference_prefix="U",
            extends="Parent",
        )
        cache.symbols["Device:Child"] = child

        issues = resolver.validate_inheritance_chain("Device:Child")

        assert len(issues) == 0

    def test_validate_inheritance_chain_missing_symbol(self):
        """Test validating chain with missing symbol."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        issues = resolver.validate_inheritance_chain("Device:NonExistent")

        assert len(issues) == 1
        assert "Symbol not found" in issues[0]

    def test_validate_inheritance_chain_circular(self):
        """Test validating circular inheritance chain."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create circular chain
        symbol_a = SymbolDefinition(
            lib_id="Device:A", name="A", library="Device", reference_prefix="U", extends="B"
        )
        cache.symbols["Device:A"] = symbol_a

        symbol_b = SymbolDefinition(
            lib_id="Device:B", name="B", library="Device", reference_prefix="U", extends="A"
        )
        cache.symbols["Device:B"] = symbol_b

        issues = resolver.validate_inheritance_chain("Device:A")

        assert len(issues) == 1
        assert "Circular inheritance" in issues[0]

    def test_get_inheritance_chain(self):
        """Test getting inheritance chain."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create inheritance chain
        grandparent = SymbolDefinition(
            lib_id="Device:GrandParent",
            name="GrandParent",
            library="Device",
            reference_prefix="U",
            extends=None,
        )
        cache.symbols["Device:GrandParent"] = grandparent

        parent = SymbolDefinition(
            lib_id="Device:Parent",
            name="Parent",
            library="Device",
            reference_prefix="U",
            extends="GrandParent",
        )
        cache.symbols["Device:Parent"] = parent

        child = SymbolDefinition(
            lib_id="Device:Child",
            name="Child",
            library="Device",
            reference_prefix="U",
            extends="Parent",
        )
        cache.symbols["Device:Child"] = child

        chain = resolver.get_inheritance_chain("Device:Child")

        assert chain == ["Device:Child", "Device:Parent", "Device:GrandParent"]

    def test_get_inheritance_chain_no_inheritance(self):
        """Test getting inheritance chain for symbol without inheritance."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        symbol = SymbolDefinition(
            lib_id="Device:Simple",
            name="Simple",
            library="Device",
            reference_prefix="U",
            extends=None,
        )
        cache.symbols["Device:Simple"] = symbol

        chain = resolver.get_inheritance_chain("Device:Simple")

        assert chain == ["Device:Simple"]

    def test_get_inheritance_chain_circular(self):
        """Test getting inheritance chain with circular reference."""
        cache = MockCache()
        resolver = SymbolResolver(cache)

        # Create circular chain
        symbol_a = SymbolDefinition(
            lib_id="Device:A", name="A", library="Device", reference_prefix="U", extends="B"
        )
        cache.symbols["Device:A"] = symbol_a

        symbol_b = SymbolDefinition(
            lib_id="Device:B", name="B", library="Device", reference_prefix="U", extends="A"
        )
        cache.symbols["Device:B"] = symbol_b

        chain = resolver.get_inheritance_chain("Device:A")

        # Should stop when circular reference is detected
        assert "Device:A" in chain
        assert "Device:B" in chain
        assert len(chain) == 2
