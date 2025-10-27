"""Test to verify and fix ComponentCollection.remove() bug."""

import kicad_sch_api as ksa
from kicad_sch_api.collections.components import Component, ComponentCollection
from kicad_sch_api.core.types import Point, SchematicSymbol


def test_component_removal_syncs_all_indexes():
    """Test that remove() properly updates all indexes and _items."""
    
    # Create collection with 2 components
    symbol_data = [
        SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
        ),
        SchematicSymbol(
            uuid="uuid2",
            lib_id="Device:R",
            reference="R2",
            value="10k",
            position=Point(200, 100),
        ),
    ]
    collection = ComponentCollection(symbol_data)
    
    print(f"Initial state:")
    print(f"  _items: {len(collection._items)} components")
    for c in collection._items:
        print(f"    - {c.reference}")
    print(f"  _reference_index: {list(collection._reference_index.keys())}")
    print(f"  len(collection): {len(collection)}")
    
    # Remove R2 using base class method
    print(f"\nRemoving R2 by UUID...")
    removed = collection.remove("uuid2")
    print(f"  Removal returned: {removed}")
    
    # Ensure indexes are current
    collection._ensure_indexes_current()
    
    print(f"\nAfter removal:")
    print(f"  _items: {len(collection._items)} components")
    for c in collection._items:
        print(f"    - {c.reference}")
    print(f"  _reference_index: {list(collection._reference_index.keys())}")
    print(f"  len(collection): {len(collection)}")
    
    # Verify expectations
    assert len(collection) == 1, f"Expected 1 component, got {len(collection)}"
    assert "R1" in collection._reference_index, "R1 should be in reference index"
    assert "R2" not in collection._reference_index, "R2 should NOT be in reference index"
    assert len(collection._items) == 1, "Should have 1 item in _items"
    
    # Try to get R2 - should return None
    r2 = collection.get_by_reference("R2")
    assert r2 is None, "R2 should not be found after removal"
    
    print("\n✅ All assertions passed!")


if __name__ == "__main__":
    test_component_removal_syncs_all_indexes()
