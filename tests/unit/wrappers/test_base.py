"""Unit tests for ElementWrapper base class."""

import pytest
from kicad_sch_api.wrappers.base import ElementWrapper


class MockData:
    """Mock data class for testing."""
    def __init__(self, uuid: str, value: str = "test"):
        self.uuid = uuid
        self.value = value


class MockCollection:
    """Mock collection for testing."""
    def __init__(self):
        self.modified = False
        self._dirty_indexes = False

    def _mark_modified(self):
        self.modified = True


class ConcreteWrapper(ElementWrapper[MockData]):
    """Concrete implementation for testing."""
    
    @property
    def uuid(self) -> str:
        return self._data.uuid


class TestElementWrapper:
    """Test ElementWrapper base class functionality."""
    
    def test_init_with_data_and_collection(self):
        """Test wrapper initialization."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        
        wrapper = ConcreteWrapper(data, collection)
        
        assert wrapper._data == data
        assert wrapper._collection == collection
    
    def test_data_property(self):
        """Test data property returns underlying data."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)
        
        assert wrapper.data == data
        assert wrapper.data.uuid == "test-uuid-1"
    
    def test_uuid_property_abstract(self):
        """Test UUID property must be implemented."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)
        
        assert wrapper.uuid == "test-uuid-1"
    
    def test_mark_modified_calls_collection(self):
        """Test _mark_modified calls collection method."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)
        
        assert not collection.modified
        wrapper._mark_modified()
        assert collection.modified
    
    def test_mark_modified_with_none_collection(self):
        """Test _mark_modified handles None collection gracefully."""
        data = MockData("test-uuid-1")
        wrapper = ConcreteWrapper(data, None)
        
        # Should not raise
        wrapper._mark_modified()
    
    def test_invalidate_indexes(self):
        """Test _invalidate_indexes updates collection."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)

        assert not collection._dirty_indexes
        wrapper._invalidate_indexes()
        assert collection._dirty_indexes
    
    def test_invalidate_indexes_with_none_collection(self):
        """Test _invalidate_indexes handles None collection gracefully."""
        data = MockData("test-uuid-1")
        wrapper = ConcreteWrapper(data, None)
        
        # Should not raise
        wrapper._invalidate_indexes()
    
    def test_equality_by_uuid(self):
        """Test wrappers are equal if UUIDs match."""
        data1 = MockData("test-uuid-1")
        data2 = MockData("test-uuid-1")
        data3 = MockData("test-uuid-2")
        collection = MockCollection()
        
        wrapper1 = ConcreteWrapper(data1, collection)
        wrapper2 = ConcreteWrapper(data2, collection)
        wrapper3 = ConcreteWrapper(data3, collection)
        
        assert wrapper1 == wrapper2
        assert wrapper1 != wrapper3
        assert wrapper2 != wrapper3
    
    def test_equality_with_non_wrapper(self):
        """Test equality with non-wrapper returns False."""
        data = MockData("test-uuid-1")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)
        
        assert wrapper != "test-uuid-1"
        assert wrapper != data
        assert wrapper != None
    
    def test_hash_by_uuid(self):
        """Test wrappers hash by UUID."""
        data1 = MockData("test-uuid-1")
        data2 = MockData("test-uuid-1")
        data3 = MockData("test-uuid-2")
        collection = MockCollection()
        
        wrapper1 = ConcreteWrapper(data1, collection)
        wrapper2 = ConcreteWrapper(data2, collection)
        wrapper3 = ConcreteWrapper(data3, collection)
        
        assert hash(wrapper1) == hash(wrapper2)
        assert hash(wrapper1) != hash(wrapper3)
    
    def test_hash_allows_use_in_set(self):
        """Test wrappers can be used in sets."""
        data1 = MockData("test-uuid-1")
        data2 = MockData("test-uuid-1")  # Same UUID
        data3 = MockData("test-uuid-2")
        collection = MockCollection()
        
        wrapper1 = ConcreteWrapper(data1, collection)
        wrapper2 = ConcreteWrapper(data2, collection)
        wrapper3 = ConcreteWrapper(data3, collection)
        
        wrapper_set = {wrapper1, wrapper2, wrapper3}
        assert len(wrapper_set) == 2  # wrapper1 and wrapper2 are same UUID
    
    def test_repr(self):
        """Test string representation."""
        data = MockData("test-uuid-1", "test-value")
        collection = MockCollection()
        wrapper = ConcreteWrapper(data, collection)
        
        repr_str = repr(wrapper)
        assert "ConcreteWrapper" in repr_str
        assert "MockData" in repr_str
