# Lessons Learned - Testing Abstraction Boundaries

## Issue #171: Non-Unique Index Bug

### What Happened
```python
# IndexRegistry returns list for non-unique indexes
result = registry.get("reference", "R1")  # Returns [0] (list)

# ComponentCollection expected int
return self._items[result]  # TypeError: list indices must be int!
```

User's code crashed: `sch.add_wire_between_pins("R1", "2", "C1", "1")`

### The Testing Gap

**What WAS tested**:
- ✅ IndexRegistry returns lists correctly
- ✅ ComponentCollection.get() works with single components

**What WASN'T tested**:
- ❌ ComponentCollection handles list return from IndexRegistry
- ❌ Integration: `add_wire_between_pins()` → `get()` workflow

### The Core Lesson

**"Test the contract, not just the implementation"**

Don't just test that component A produces correct output.
Also test that component B correctly consumes that output.

---

## New Tests Added

### File: `tests/unit/collections/test_non_unique_index_handling.py`

Tests that verify ComponentCollection methods handle non-unique index returns:
- `test_get_with_single_component_returns_component()` - Handles `[0]`
- `test_get_with_multiple_same_reference_returns_first()` - Handles `[0, 1]`
- `test_get_nonexistent_returns_none()` - Handles `None`
- `test_remove_with_single_component_removes_it()` - Remove with `[0]`
- `test_remove_with_multiple_same_reference_removes_first()` - Remove with `[0, 1]`
- Edge cases: empty collections, sequential removals, mixed unique/non-unique

### File: `tests/integration/test_wire_between_pins_non_unique.py`

Integration tests for real user workflows:
- `test_wire_between_pins_basic_workflow()` - Exact failing scenario from Issue #171
- `test_wire_between_multi_unit_components()` - Multi-unit component wiring
- `test_get_pin_position_multi_unit_component()` - Pin lookup with non-unique refs
- `test_connect_multi_unit_to_regular_component()` - Complex routing scenarios

---

## Quick Fix Pattern

When you have Producer → Consumer relationships:

```python
# ✅ Test Producer
def test_producer_returns_list():
    result = producer.get(key)
    assert isinstance(result, list)

# ✅ Test Consumer (THIS WAS MISSING!)
def test_consumer_handles_list():
    result = consumer.use_producer(key)  # Internally calls producer
    assert result is not None  # Must handle list!

# ✅ Test Integration
def test_end_to_end_workflow():
    # Test real user scenario that crosses the boundary
    pass
```

### When to Add Boundary Tests

Add these tests when:
- Component A returns data that Component B consumes
- Return type varies (e.g., `int` vs `List[int]`)
- Multiple implementations exist
- Previous bugs occurred at this boundary

### Common Boundaries in This Project

- IndexRegistry → Collection methods (`get()`, `remove()`)
- Parser → Formatter (S-expression)
- SymbolCache → ComponentCollection
- Component → WireManager (pin positions)

### Testing Checklist

For any feature touching IndexRegistry:
- [ ] Test consumer with single-item list `[0]`
- [ ] Test consumer with multi-item list `[0, 1, 2]`
- [ ] Test consumer with empty list `[]`
- [ ] Test real workflow that exercises the boundary

### Example Test Template

```python
class TestConsumerContract:
    """Verify ComponentCollection handles IndexRegistry return types."""

    def test_get_with_single_match(self):
        """Reference index returns [0], get() should handle it."""
        collection.add("Device:R", reference="R1")
        component = collection.get("R1")
        assert component is not None

    def test_get_with_multiple_matches(self):
        """Multi-unit: reference index returns [0, 1], get() should return first."""
        collection.add("TL072", reference="U1", unit=1)
        collection.add("TL072", reference="U1", unit=2)
        component = collection.get("U1")
        assert component.unit == 1  # First one

    def test_integration_workflow(self):
        """Test real user scenario."""
        sch.components.add("Device:R", reference="R1", ...)
        wire = sch.add_wire_between_pins("R1", "2", "C1", "1")
        assert wire is not None
```

---

## Related Issues

- **Issue #171**: Original bug report
- **PR #171**: Fix with list handling in get() and remove()
- **Commit ab37eb8**: First fix attempt (incomplete - only get())
- **Commit 876d1ae**: Reverted incomplete fix
- **Commit 3bd8ccb**: Complete fix (both get() and remove())

---

**Bottom Line**: If you test that Producer works but don't test that Consumer handles Producer's output, you have a gap.
