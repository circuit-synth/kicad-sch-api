"""
Comprehensive unit tests for base collection infrastructure.

Tests:
- ValidationLevel enum
- IndexSpec dataclass
- IndexRegistry
- PropertyDict
- BaseCollection (via concrete implementation)
- BatchContext
"""

import pytest
from typing import List
from dataclasses import dataclass

from kicad_sch_api.collections.base import (
    ValidationLevel,
    IndexSpec,
    IndexRegistry,
    PropertyDict,
    BaseCollection,
)


# Test fixtures and mock classes
@dataclass
class MockItem:
    """Mock item for testing collections."""
    uuid: str
    reference: str
    value: str


class MockCollection(BaseCollection[MockItem]):
    """Concrete implementation of BaseCollection for testing."""

    def _get_item_uuid(self, item: MockItem) -> str:
        """Extract UUID from mock item."""
        return item.uuid

    def _create_item(self, **kwargs) -> MockItem:
        """Create a mock item."""
        return MockItem(**kwargs)

    def _get_index_specs(self) -> List[IndexSpec]:
        """Get index specifications for mock collection."""
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda item: item.uuid,
                unique=True,
                description="UUID index"
            ),
            IndexSpec(
                name="reference",
                key_func=lambda item: item.reference,
                unique=True,
                description="Reference designator index"
            ),
            IndexSpec(
                name="value",
                key_func=lambda item: item.value,
                unique=False,
                description="Component value index (non-unique)"
            ),
        ]


# ValidationLevel tests
class TestValidationLevel:
    """Test ValidationLevel enum."""

    def test_validation_levels_exist(self):
        """Test all validation levels are defined."""
        assert ValidationLevel.NONE.value == 0
        assert ValidationLevel.BASIC.value == 1
        assert ValidationLevel.NORMAL.value == 2
        assert ValidationLevel.STRICT.value == 3
        assert ValidationLevel.PARANOID.value == 4

    def test_validation_level_comparison(self):
        """Test validation level comparison."""
        assert ValidationLevel.NONE < ValidationLevel.BASIC
        assert ValidationLevel.BASIC < ValidationLevel.NORMAL
        assert ValidationLevel.NORMAL < ValidationLevel.STRICT
        assert ValidationLevel.STRICT < ValidationLevel.PARANOID

    def test_validation_level_equality(self):
        """Test validation level equality."""
        assert ValidationLevel.NORMAL == ValidationLevel.NORMAL
        assert ValidationLevel.NORMAL != ValidationLevel.STRICT


# IndexSpec tests
class TestIndexSpec:
    """Test IndexSpec dataclass."""

    def test_create_valid_index_spec(self):
        """Test creating a valid index specification."""
        spec = IndexSpec(
            name="uuid",
            key_func=lambda x: x.uuid,
            unique=True,
            description="UUID index"
        )
        assert spec.name == "uuid"
        assert callable(spec.key_func)
        assert spec.unique is True
        assert spec.description == "UUID index"

    def test_create_index_spec_with_defaults(self):
        """Test creating index spec with default values."""
        spec = IndexSpec(
            name="ref",
            key_func=lambda x: x.reference
        )
        assert spec.name == "ref"
        assert spec.unique is True  # Default
        assert spec.description == ""  # Default

    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Index name cannot be empty"):
            IndexSpec(name="", key_func=lambda x: x.uuid)

    def test_non_callable_key_func_raises_error(self):
        """Test that non-callable key_func raises ValueError."""
        with pytest.raises(ValueError, match="Index key_func must be callable"):
            IndexSpec(name="test", key_func="not a function")  # type: ignore


# IndexRegistry tests
class TestIndexRegistry:
    """Test IndexRegistry class."""

    @pytest.fixture
    def sample_items(self):
        """Create sample items for testing."""
        return [
            MockItem(uuid="uuid1", reference="R1", value="10k"),
            MockItem(uuid="uuid2", reference="R2", value="10k"),
            MockItem(uuid="uuid3", reference="C1", value="100nF"),
        ]

    @pytest.fixture
    def index_specs(self):
        """Create sample index specifications."""
        return [
            IndexSpec(name="uuid", key_func=lambda x: x.uuid, unique=True),
            IndexSpec(name="reference", key_func=lambda x: x.reference, unique=True),
            IndexSpec(name="value", key_func=lambda x: x.value, unique=False),
        ]

    def test_create_index_registry(self, index_specs):
        """Test creating an index registry."""
        registry = IndexRegistry(index_specs)
        assert len(registry.specs) == 3
        assert "uuid" in registry.specs
        assert "reference" in registry.specs
        assert "value" in registry.specs

    def test_indexes_start_clean(self, index_specs):
        """Test that new registry starts with clean indexes."""
        registry = IndexRegistry(index_specs)
        # Initially, indexes are empty and clean
        assert registry.is_dirty() is False

    def test_mark_dirty(self, index_specs):
        """Test marking indexes as dirty."""
        registry = IndexRegistry(index_specs)
        registry.mark_dirty()
        assert registry.is_dirty() is True

    def test_rebuild_indexes(self, index_specs, sample_items):
        """Test rebuilding all indexes."""
        registry = IndexRegistry(index_specs)
        registry.rebuild(sample_items)

        # Check indexes are built correctly
        assert registry.get("uuid", "uuid1") == 0
        assert registry.get("uuid", "uuid2") == 1
        assert registry.get("uuid", "uuid3") == 2

        assert registry.get("reference", "R1") == 0
        assert registry.get("reference", "R2") == 1
        assert registry.get("reference", "C1") == 2

        # Non-unique index returns list
        assert registry.get("value", "10k") == [0, 1]
        assert registry.get("value", "100nF") == [2]

    def test_rebuild_marks_clean(self, index_specs, sample_items):
        """Test that rebuild marks indexes as clean."""
        registry = IndexRegistry(index_specs)
        registry.mark_dirty()
        assert registry.is_dirty() is True

        registry.rebuild(sample_items)
        assert registry.is_dirty() is False

    def test_unique_index_duplicate_raises_error(self, index_specs):
        """Test that duplicate in unique index raises error."""
        items = [
            MockItem(uuid="uuid1", reference="R1", value="10k"),
            MockItem(uuid="uuid1", reference="R2", value="20k"),  # Duplicate UUID
        ]

        registry = IndexRegistry(index_specs)
        with pytest.raises(ValueError, match="Duplicate key 'uuid1' in unique index 'uuid'"):
            registry.rebuild(items)

    def test_get_from_nonexistent_index_raises_error(self, index_specs):
        """Test getting from non-existent index raises KeyError."""
        registry = IndexRegistry(index_specs)
        with pytest.raises(KeyError, match="Unknown index"):
            registry.get("nonexistent", "key")

    def test_has_key(self, index_specs, sample_items):
        """Test checking if key exists in index."""
        registry = IndexRegistry(index_specs)
        registry.rebuild(sample_items)

        assert registry.has_key("uuid", "uuid1") is True
        assert registry.has_key("uuid", "nonexistent") is False
        assert registry.has_key("reference", "R1") is True
        assert registry.has_key("reference", "R99") is False

    def test_add_spec(self, index_specs):
        """Test adding a new index specification."""
        registry = IndexRegistry(index_specs)

        new_spec = IndexSpec(name="lib_id", key_func=lambda x: "Device:R", unique=False)
        registry.add_spec(new_spec)

        assert "lib_id" in registry.specs
        assert "lib_id" in registry.indexes
        assert registry.is_dirty() is True

    def test_add_duplicate_spec_raises_error(self, index_specs):
        """Test adding duplicate spec raises error."""
        registry = IndexRegistry(index_specs)

        duplicate_spec = IndexSpec(name="uuid", key_func=lambda x: x.uuid)
        with pytest.raises(ValueError, match="Index 'uuid' already exists"):
            registry.add_spec(duplicate_spec)


# PropertyDict tests  
class TestPropertyDict:
    """Test PropertyDict class."""

    def test_create_empty_property_dict(self):
        """Test creating an empty PropertyDict."""
        pd = PropertyDict()
        assert len(pd) == 0
        assert dict(pd) == {}

    def test_create_with_initial_data(self):
        """Test creating PropertyDict with initial data."""
        initial = {"key1": "value1", "key2": "value2"}
        pd = PropertyDict(data=initial)
        assert len(pd) == 2
        assert pd["key1"] == "value1"
        assert pd["key2"] == "value2"

    def test_set_item_calls_callback(self):
        """Test that setting an item calls the modification callback."""
        call_count = []

        def on_modify():
            call_count.append(1)

        pd = PropertyDict(on_modify=on_modify)
        pd["key"] = "value"

        assert len(call_count) == 1
        assert pd["key"] == "value"

    def test_del_item_calls_callback(self):
        """Test that deleting an item calls the modification callback."""
        call_count = []

        def on_modify():
            call_count.append(1)

        pd = PropertyDict(data={"key": "value"}, on_modify=on_modify)
        del pd["key"]

        assert len(call_count) == 1
        assert "key" not in pd

    def test_iteration(self):
        """Test iterating over PropertyDict."""
        pd = PropertyDict(data={"a": 1, "b": 2, "c": 3})
        keys = list(pd)
        assert set(keys) == {"a", "b", "c"}

    def test_len(self):
        """Test len() on PropertyDict."""
        pd = PropertyDict(data={"a": 1, "b": 2})
        assert len(pd) == 2

    def test_repr(self):
        """Test repr() on PropertyDict."""
        pd = PropertyDict(data={"key": "value"})
        assert "PropertyDict" in repr(pd)
        assert "key" in repr(pd)

    def test_set_callback(self):
        """Test setting callback after creation."""
        pd = PropertyDict(data={"key": "value"})

        call_count = []

        def on_modify():
            call_count.append(1)

        pd.set_callback(on_modify)
        pd["new_key"] = "new_value"

        assert len(call_count) == 1


# BaseCollection tests
class TestBaseCollection:
    """Test BaseCollection via MockCollection."""

    @pytest.fixture
    def empty_collection(self):
        """Create an empty mock collection."""
        return MockCollection()

    @pytest.fixture
    def sample_items(self):
        """Create sample items."""
        return [
            MockItem(uuid="uuid1", reference="R1", value="10k"),
            MockItem(uuid="uuid2", reference="R2", value="10k"),
            MockItem(uuid="uuid3", reference="C1", value="100nF"),
        ]

    @pytest.fixture
    def populated_collection(self, sample_items):
        """Create a collection with sample items."""
        return MockCollection(items=sample_items)

    def test_create_empty_collection(self, empty_collection):
        """Test creating an empty collection."""
        assert len(empty_collection) == 0
        assert empty_collection.is_modified is False

    def test_create_with_initial_items(self, populated_collection):
        """Test creating collection with initial items."""
        assert len(populated_collection) == 3
        assert populated_collection.is_modified is True

    def test_add_item(self, empty_collection):
        """Test adding an item to collection."""
        item = MockItem(uuid="uuid1", reference="R1", value="10k")
        result = empty_collection.add(item)

        assert result is item
        assert len(empty_collection) == 1
        assert empty_collection.is_modified is True

    def test_add_duplicate_uuid_raises_error(self, populated_collection):
        """Test adding item with duplicate UUID raises error."""
        duplicate = MockItem(uuid="uuid1", reference="R99", value="1k")

        with pytest.raises(ValueError, match="Item with UUID uuid1 already exists"):
            populated_collection.add(duplicate)

    def test_add_none_item_with_validation_raises_error(self, empty_collection):
        """Test adding None item with validation raises error."""
        with pytest.raises(ValueError, match="Cannot add None item"):
            empty_collection.add(None)  # type: ignore

    def test_remove_by_uuid(self, populated_collection):
        """Test removing item by UUID."""
        result = populated_collection.remove("uuid1")
        assert result is True
        assert len(populated_collection) == 2
        assert populated_collection.get("uuid1") is None

    def test_remove_by_item(self, populated_collection):
        """Test removing item by instance."""
        item = populated_collection.get("uuid2")
        result = populated_collection.remove(item)

        assert result is True
        assert len(populated_collection) == 2
        assert populated_collection.get("uuid2") is None

    def test_remove_nonexistent_returns_false(self, populated_collection):
        """Test removing non-existent item returns False."""
        result = populated_collection.remove("nonexistent-uuid")
        assert result is False
        assert len(populated_collection) == 3

    def test_get_by_uuid(self, populated_collection):
        """Test getting item by UUID."""
        item = populated_collection.get("uuid1")
        assert item is not None
        assert item.uuid == "uuid1"
        assert item.reference == "R1"

    def test_get_nonexistent_returns_none(self, populated_collection):
        """Test getting non-existent item returns None."""
        item = populated_collection.get("nonexistent")
        assert item is None

    def test_find_with_predicate(self, populated_collection):
        """Test finding items with a predicate."""
        results = populated_collection.find(lambda x: x.value == "10k")
        assert len(results) == 2
        assert all(item.value == "10k" for item in results)

    def test_filter_by_criteria(self, populated_collection):
        """Test filtering items by attribute criteria."""
        results = populated_collection.filter(value="10k")
        assert len(results) == 2

        results = populated_collection.filter(reference="R1")
        assert len(results) == 1
        assert results[0].reference == "R1"

    def test_clear(self, populated_collection):
        """Test clearing all items."""
        populated_collection.clear()
        assert len(populated_collection) == 0
        assert populated_collection.is_modified is True

    def test_len(self, populated_collection):
        """Test len() on collection."""
        assert len(populated_collection) == 3

    def test_iter(self, populated_collection):
        """Test iterating over collection."""
        items = list(populated_collection)
        assert len(items) == 3
        assert all(isinstance(item, MockItem) for item in items)

    def test_contains_by_uuid(self, populated_collection):
        """Test __contains__ with UUID."""
        assert "uuid1" in populated_collection
        assert "nonexistent" not in populated_collection

    def test_contains_by_item(self, populated_collection):
        """Test __contains__ with item instance."""
        item = populated_collection.get("uuid1")
        assert item in populated_collection

        new_item = MockItem(uuid="new", reference="R99", value="1k")
        assert new_item not in populated_collection

    def test_getitem(self, populated_collection):
        """Test __getitem__ indexing."""
        item = populated_collection[0]
        assert isinstance(item, MockItem)

    def test_get_statistics(self, populated_collection):
        """Test getting collection statistics."""
        stats = populated_collection.get_statistics()

        assert stats["item_count"] == 3
        assert stats["index_count"] == 3
        assert stats["modified"] is True
        assert stats["indexes_dirty"] is False
        assert stats["collection_type"] == "MockCollection"
        assert stats["validation_level"] == "NORMAL"
        assert stats["batch_mode"] is False

    def test_mark_clean(self, populated_collection):
        """Test marking collection as clean."""
        assert populated_collection.is_modified is True
        populated_collection.mark_clean()
        assert populated_collection.is_modified is False

    def test_validation_level_property(self, empty_collection):
        """Test getting validation level."""
        assert empty_collection.validation_level == ValidationLevel.NORMAL

    def test_set_validation_level(self, empty_collection):
        """Test setting validation level."""
        empty_collection.set_validation_level(ValidationLevel.PARANOID)
        assert empty_collection.validation_level == ValidationLevel.PARANOID

    def test_batch_mode_context(self, empty_collection):
        """Test batch mode context manager."""
        items = [
            MockItem(uuid=f"uuid{i}", reference=f"R{i}", value="10k")
            for i in range(100)
        ]

        with empty_collection.batch_mode():
            for item in items:
                empty_collection._add_item_to_collection(item)
            # Indexes should still be dirty during batch
            assert empty_collection._index_registry.is_dirty() is True

        # After batch, indexes should be rebuilt
        assert empty_collection._index_registry.is_dirty() is False
        assert len(empty_collection) == 100

    def test_lazy_index_rebuilding(self, empty_collection):
        """Test that indexes are rebuilt lazily."""
        item1 = MockItem(uuid="uuid1", reference="R1", value="10k")
        empty_collection._add_item_to_collection(item1)

        # Indexes should be dirty
        assert empty_collection._index_registry.is_dirty() is True

        # Accessing via get() should trigger rebuild
        result = empty_collection.get("uuid1")
        assert result is item1
        assert empty_collection._index_registry.is_dirty() is False
