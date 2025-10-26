# Collections Module

Enhanced collection classes with filtering, searching, and bulk operations.

## Overview

This module provides specialized collection classes that extend Python's built-in list functionality with domain-specific features for managing schematic elements.

## Collection Classes

### Base Collection Pattern
All collections follow this pattern:
```python
class ElementCollection:
    def __init__(self, elements: List[Element]):
        self._elements = elements

    def add(self, element: Element) -> Element:
        """Add element and return it"""

    def remove(self, identifier) -> bool:
        """Remove element by identifier"""

    def filter(self, **criteria) -> List[Element]:
        """Filter by criteria"""

    def bulk_update(self, criteria, updates) -> int:
        """Update multiple elements"""
```

## Available Collections

### ComponentCollection
- **Location**: `core/components.py`
- **Elements**: Component objects
- **Key Methods**:
  - `add()` - Add component with symbol lookup
  - `remove()` - Remove by reference
  - `filter_by_lib_id()` - Find by library ID
  - `filter_by_value()` - Find by component value
  - `filter_by_footprint()` - Find by footprint
  - `bulk_update()` - Update multiple components
  - `get_by_reference()` - Get specific component

### WireCollection
- **Location**: `core/wires.py`
- **Elements**: Wire objects
- **Key Methods**:
  - `add()` - Add wire connection
  - `remove()` - Remove by UUID
  - `find_connected()` - Find wires at point
  - `find_net()` - Get all wires in net

### LabelCollection
- **Location**: `core/labels.py` and `core/texts.py`
- **Elements**: Label and text objects
- **Key Methods**:
  - `add()` - Add label
  - `remove()` - Remove by UUID
  - `find_by_text()` - Find by content
  - `find_at_position()` - Find at coordinate

### JunctionCollection
- **Location**: `core/junctions.py`
- **Elements**: Junction points
- **Key Methods**:
  - `add()` - Add junction
  - `remove()` - Remove by UUID
  - `find_at_position()` - Find at coordinate

### NetCollection
- **Location**: `core/nets.py`
- **Elements**: Net definitions
- **Key Methods**:
  - `add()` - Add net
  - `find_by_name()` - Get net by name
  - `get_wires()` - Get wires in net

## Common Operations

### Adding Elements
```python
# Add component with symbol lookup
resistor = sch.components.add(
    lib_id='Device:R',
    reference='R1',
    value='10k',
    position=(100, 100)
)

# Add wire
wire = sch.wires.add(
    start=(100, 100),
    end=(150, 100)
)

# Add label
label = sch.labels.add(
    text='VCC',
    position=(100, 100),
    label_type='global'
)
```

### Filtering
```python
# Find all resistors
resistors = sch.components.filter_by_lib_id('Device:R')

# Find by value
resistors_10k = sch.components.filter_by_value('10k')

# Find by footprint
smd_resistors = sch.components.filter_by_footprint('*SMD*')

# Custom filter
large_components = [c for c in sch.components if c.value > 100]
```

### Bulk Operations
```python
# Update multiple components
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Bulk change footprint
sch.components.bulk_update(
    criteria={'value': '10k'},
    updates={'footprint': 'Resistor_SMD:R_0603_1608Metric'}
)
```

### Iteration
```python
# Iterate over all components
for component in sch.components:
    print(f"{component.reference}: {component.value}")

# Iterate over filtered subset
for wire in sch.wires.find_net('GND'):
    print(f"Wire in GND net: {wire}")
```

## Collection Features

### Filtering Capabilities
- **By ID/Reference** - Find by identifier
- **By Type** - Filter by element type
- **By Property** - Filter by custom properties
- **By Position** - Find at coordinate or region
- **By Regex** - Pattern matching
- **Custom Functions** - User-defined filters

### Bulk Operations
- **Update Multiple** - Change many elements
- **Delete Multiple** - Remove selection
- **Copy Selection** - Clone elements
- **Export Selection** - Get as dictionary

### Search & Query
- **Fast lookup** - Indexed lookups
- **Spatial search** - Find by position
- **Pattern matching** - Regex support
- **Aggregation** - Count, sum, statistics

## Performance Characteristics

| Operation | Complexity | Time |
|-----------|-----------|------|
| Add element | O(1) | ~1µs |
| Remove by ID | O(n) | ~10µs |
| Filter by property | O(n) | ~100µs |
| Bulk update | O(n) | ~1ms |
| Find at position | O(n) | ~100µs |

Where n = number of elements in collection.

## Extending Collections

To create a custom collection:

```python
from collections import UserList

class CustomCollection(UserList):
    def __init__(self, elements=None):
        super().__init__(elements or [])

    def find_by_custom_criteria(self, criteria):
        """Custom finder method"""
        return [e for e in self.data if meets_criteria(e, criteria)]
```

## Integration Points

### Used By
- `Schematic` class - Owns all collections
- Managers - Access via schematic instance
- User code - Direct collection manipulation

### Related Modules
- `core/types.py` - Element type definitions
- `core/schematic.py` - Collection ownership
- `core/managers/*` - Manager implementations

## Testing

Tests located in `../../tests/`:
- `test_collections.py` - Collection functionality
- `test_component_collection.py` - Component-specific tests
- `test_wire_collection.py` - Wire-specific tests
- Integration tests with real schematics

## Known Issues

1. **Performance Indexing** - Large collections may need optimization
2. **Bulk Update Errors** - No rollback on partial failures
3. **UUID Handling** - Some operations may not properly use UUIDs
4. **Memory Usage** - Large schematics may consume significant memory

## Future Improvements

- [ ] Lazy collection evaluation
- [ ] Indexed lookups for O(1) queries
- [ ] Bulk operation transactions/rollback
- [ ] Event listeners on collection changes
- [ ] Collection change history
- [ ] Parallel operations for large collections

## References

- Python Collections: https://docs.python.org/3/library/collections.html
- Design patterns: See `CODEBASE_ANALYSIS.md`
- Type system: See `core/types.py`
