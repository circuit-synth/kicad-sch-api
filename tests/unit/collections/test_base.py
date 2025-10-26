"""
Unit tests for base IndexedCollection class.

Tests the core functionality of the unified collection architecture
including indexing, modification tracking, and common operations.
"""

import pytest
from typing import Any, Dict

from kicad_sch_api.collections.base import IndexedCollection


class MockItem:
    """Mock item for testing IndexedCollection."""

    def __init__(self, uuid: str, name: str = "", value: str = ""):
        self.uuid = uuid
        self.name = name
        self.value = value

    def __eq__(self, other):
        return isinstance(other, MockItem) and self.uuid == other.uuid

    def __repr__(self):
        return f"MockItem(uuid='{self.uuid}', name='{self.name}')"


class MockCollection(IndexedCollection[MockItem]):
    """Mock collection for testing base functionality."""

    def _get_item_uuid(self, item: MockItem) -> str:
        return item.uuid

    def _create_item(self, **kwargs) -> MockItem:
        return MockItem(**kwargs)

    def _build_additional_indexes(self) -> None:
        # No additional indexes for mock
        pass


class TestIndexedCollection:
    """Test cases for IndexedCollection base class."""

    def test_collection_initialization_empty(self):
        """Test collection initializes empty correctly."""
        collection = MockCollection()
        assert len(collection) == 0
        assert not collection.is_modified
        assert list(collection) == []

    def test_collection_initialization_with_items(self):
        """Test collection initializes with items correctly."""
        items = [
            MockItem("uuid1", "item1"),
            MockItem("uuid2", "item2")
        ]
        collection = MockCollection(items)

        assert len(collection) == 2
        assert collection.is_modified  # Modified during initialization
        assert list(collection) == items

    def test_add_item(self):
        """Test adding items to collection."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")

        added_item = collection.add(item)

        assert added_item is item
        assert len(collection) == 1
        assert collection.is_modified
        assert item in collection

    def test_add_duplicate_uuid_raises_error(self):
        """Test adding item with duplicate UUID raises error."""
        collection = MockCollection()
        item1 = MockItem("uuid1", "item1")
        item2 = MockItem("uuid1", "item2")

        collection.add(item1)

        with pytest.raises(ValueError, match="Item with UUID uuid1 already exists"):
            collection.add(item2)

    def test_get_by_uuid(self):
        """Test getting items by UUID."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")
        collection.add(item)

        found_item = collection.get("uuid1")
        assert found_item is item

        not_found = collection.get("nonexistent")
        assert not_found is None

    def test_remove_by_uuid(self):
        """Test removing items by UUID."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")
        collection.add(item)

        removed = collection.remove("uuid1")
        assert removed is True
        assert len(collection) == 0
        assert item not in collection

        # Try removing non-existent item
        removed = collection.remove("nonexistent")
        assert removed is False

    def test_remove_by_item(self):
        """Test removing items by item instance."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")
        collection.add(item)

        removed = collection.remove(item)
        assert removed is True
        assert len(collection) == 0
        assert item not in collection

    def test_find_with_predicate(self):
        """Test finding items with predicate function."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "test1", "value1"),
            MockItem("uuid2", "test2", "value2"),
            MockItem("uuid3", "other", "value1")
        ]
        for item in items:
            collection.add(item)

        # Find items with specific value
        found = collection.find(lambda item: item.value == "value1")
        assert len(found) == 2
        assert items[0] in found
        assert items[2] in found

        # Find items with specific name pattern
        found = collection.find(lambda item: item.name.startswith("test"))
        assert len(found) == 2
        assert items[0] in found
        assert items[1] in found

    def test_filter_by_attributes(self):
        """Test filtering items by attribute criteria."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "test1", "value1"),
            MockItem("uuid2", "test2", "value2"),
            MockItem("uuid3", "test1", "value2")
        ]
        for item in items:
            collection.add(item)

        # Filter by single attribute
        found = collection.filter(name="test1")
        assert len(found) == 2
        assert items[0] in found
        assert items[2] in found

        # Filter by multiple attributes
        found = collection.filter(name="test1", value="value2")
        assert len(found) == 1
        assert items[2] in found

        # Filter with no matches
        found = collection.filter(name="nonexistent")
        assert len(found) == 0

    def test_contains_by_uuid(self):
        """Test checking if collection contains UUID."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")
        collection.add(item)

        assert "uuid1" in collection
        assert "nonexistent" not in collection

    def test_contains_by_item(self):
        """Test checking if collection contains item."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")
        other_item = MockItem("uuid2", "other")

        collection.add(item)

        assert item in collection
        assert other_item not in collection

    def test_getitem_by_index(self):
        """Test accessing items by index."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "first"),
            MockItem("uuid2", "second")
        ]
        for item in items:
            collection.add(item)

        assert collection[0] is items[0]
        assert collection[1] is items[1]

    def test_iteration(self):
        """Test iterating over collection."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "first"),
            MockItem("uuid2", "second")
        ]
        for item in items:
            collection.add(item)

        collected_items = list(collection)
        assert collected_items == items

    def test_clear_collection(self):
        """Test clearing all items from collection."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "first"),
            MockItem("uuid2", "second")
        ]
        for item in items:
            collection.add(item)

        collection.clear()

        assert len(collection) == 0
        assert collection.is_modified
        assert list(collection) == []

    def test_modification_tracking(self):
        """Test modification flag tracking."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")

        # Initial state - not modified
        assert not collection.is_modified

        # Adding item marks as modified
        collection.add(item)
        assert collection.is_modified

        # Mark clean
        collection.mark_clean()
        assert not collection.is_modified

        # Removing item marks as modified
        collection.remove(item)
        assert collection.is_modified

    def test_index_rebuilding(self):
        """Test automatic index rebuilding."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "first"),
            MockItem("uuid2", "second")
        ]
        for item in items:
            collection.add(item)

        # Force index rebuild by accessing after marking dirty
        collection._mark_indexes_dirty()
        found_item = collection.get("uuid1")
        assert found_item is items[0]

    def test_get_statistics(self):
        """Test collection statistics."""
        collection = MockCollection()
        items = [
            MockItem("uuid1", "first"),
            MockItem("uuid2", "second")
        ]
        for item in items:
            collection.add(item)

        stats = collection.get_statistics()

        assert stats["item_count"] == 2
        assert stats["uuid_index_size"] == 2
        assert stats["modified"] is True
        assert stats["collection_type"] == "MockCollection"

    def test_lazy_index_rebuilding(self):
        """Test that indexes are only rebuilt when needed."""
        collection = MockCollection()
        item = MockItem("uuid1", "test")

        # Add item
        collection.add(item)

        # Manually mark indexes as clean to test lazy rebuilding
        collection._dirty_indexes = False

        # Access that doesn't require index should not rebuild
        len(collection)
        assert not collection._dirty_indexes

        # Access that requires index should trigger rebuild
        collection.get("uuid1")
        # Index should have been rebuilt, so no longer dirty
        assert not collection._dirty_indexes

    def test_error_handling_in_get_item_uuid(self):
        """Test error handling when _get_item_uuid fails."""
        class BrokenCollection(IndexedCollection):
            def _get_item_uuid(self, item):
                raise ValueError("Broken UUID extraction")

            def _create_item(self, **kwargs):
                return MockItem(**kwargs)

            def _build_additional_indexes(self):
                pass

        collection = BrokenCollection()
        item = MockItem("uuid1", "test")

        # Should raise the error from _get_item_uuid
        with pytest.raises(ValueError, match="Broken UUID extraction"):
            collection.add(item)