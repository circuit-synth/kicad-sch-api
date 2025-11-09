"""Unit tests for WireWrapper class."""

import pytest

from kicad_sch_api.core.types import Point, Wire, WireType
from kicad_sch_api.wrappers.wire import WireWrapper


class MockWireCollection:
    """Mock wire collection for testing."""

    def __init__(self):
        self.modified = False
        self._dirty_indexes = False

    def _mark_modified(self):
        self.modified = True


class TestWireWrapper:
    """Test WireWrapper functionality."""

    def test_init_with_wire_and_collection(self):
        """Test wrapper initialization."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()

        wrapper = WireWrapper(wire, collection)

        assert wrapper._data == wire
        assert wrapper._collection == collection

    def test_uuid_property(self):
        """Test UUID property returns wire UUID."""
        wire = Wire(uuid="wire-uuid-123", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.uuid == "wire-uuid-123"

    def test_points_getter(self):
        """Test points property returns wire points."""
        points = [Point(0, 0), Point(10, 10), Point(20, 10)]
        wire = Wire(uuid="wire-1", points=points)
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.points == points
        assert len(wrapper.points) == 3

    def test_points_setter_valid(self):
        """Test points setter with valid points."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        new_points = [Point(5, 5), Point(15, 15), Point(25, 25)]
        wrapper.points = new_points

        assert wrapper.points == new_points
        assert collection.modified

    def test_points_setter_validates_minimum_points(self):
        """Test points setter validates at least 2 points."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        with pytest.raises(ValueError) as exc_info:
            wrapper.points = [Point(0, 0)]

        assert "at least 2 points" in str(exc_info.value)

    def test_points_setter_with_empty_list(self):
        """Test points setter rejects empty list."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        with pytest.raises(ValueError):
            wrapper.points = []

    def test_start_property(self):
        """Test start property returns first point."""
        wire = Wire(uuid="wire-1", points=[Point(5, 10), Point(15, 20), Point(25, 30)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.start == Point(5, 10)

    def test_end_property(self):
        """Test end property returns last point."""
        wire = Wire(uuid="wire-1", points=[Point(5, 10), Point(15, 20), Point(25, 30)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.end == Point(25, 30)

    def test_wire_type_property(self):
        """Test wire_type property returns wire type."""
        wire = Wire(
            uuid="wire-1",
            points=[Point(0, 0), Point(10, 10)],
            wire_type=WireType.BUS,
        )
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.wire_type == WireType.BUS

    def test_wire_type_setter(self):
        """Test wire_type setter updates type and marks modified."""
        wire = Wire(
            uuid="wire-1",
            points=[Point(0, 0), Point(10, 10)],
            wire_type=WireType.WIRE,
        )
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        wrapper.wire_type = WireType.BUS

        assert wrapper.wire_type == WireType.BUS
        assert collection.modified

    def test_stroke_width_property(self):
        """Test stroke_width property."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)], stroke_width=0.5)
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.stroke_width == 0.5

    def test_stroke_width_setter(self):
        """Test stroke_width setter."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)], stroke_width=0.5)
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        wrapper.stroke_width = 1.0

        assert wrapper.stroke_width == 1.0
        assert collection.modified

    def test_length_property(self):
        """Test length property delegates to wire."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(3, 0), Point(3, 4)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        # 3 + 4 = 7
        assert wrapper.length == pytest.approx(7.0)

    def test_is_simple_property(self):
        """Test is_simple property delegates to wire."""
        wire_simple = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        wire_complex = Wire(uuid="wire-2", points=[Point(0, 0), Point(10, 10), Point(20, 20)])
        collection = MockWireCollection()

        wrapper_simple = WireWrapper(wire_simple, collection)
        wrapper_complex = WireWrapper(wire_complex, collection)

        assert wrapper_simple.is_simple()
        assert not wrapper_complex.is_simple()

    def test_mark_modified_with_none_collection(self):
        """Test modification tracking with None collection."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        wrapper = WireWrapper(wire, None)

        # Should not raise
        wrapper.points = [Point(5, 5), Point(15, 15)]

    def test_data_property(self):
        """Test data property returns underlying wire."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        assert wrapper.data == wire
        assert isinstance(wrapper.data, Wire)

    def test_equality_by_uuid(self):
        """Test wrappers are equal if UUIDs match."""
        wire1 = Wire(uuid="same-uuid", points=[Point(0, 0), Point(10, 10)])
        wire2 = Wire(uuid="same-uuid", points=[Point(5, 5), Point(15, 15)])
        wire3 = Wire(uuid="different-uuid", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()

        wrapper1 = WireWrapper(wire1, collection)
        wrapper2 = WireWrapper(wire2, collection)
        wrapper3 = WireWrapper(wire3, collection)

        assert wrapper1 == wrapper2
        assert wrapper1 != wrapper3

    def test_hash_by_uuid(self):
        """Test wrappers hash by UUID."""
        wire1 = Wire(uuid="same-uuid", points=[Point(0, 0), Point(10, 10)])
        wire2 = Wire(uuid="same-uuid", points=[Point(5, 5), Point(15, 15)])
        wire3 = Wire(uuid="different-uuid", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()

        wrapper1 = WireWrapper(wire1, collection)
        wrapper2 = WireWrapper(wire2, collection)
        wrapper3 = WireWrapper(wire3, collection)

        assert hash(wrapper1) == hash(wrapper2)
        assert hash(wrapper1) != hash(wrapper3)

    def test_repr(self):
        """Test string representation."""
        wire = Wire(uuid="wire-1", points=[Point(0, 0), Point(10, 10)])
        collection = MockWireCollection()
        wrapper = WireWrapper(wire, collection)

        repr_str = repr(wrapper)
        assert "WireWrapper" in repr_str
        assert "Wire" in repr_str
