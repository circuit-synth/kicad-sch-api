# Architecture Overview

This document explains how kicad-sch-api is structured and how data flows through the system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Code                              │
│  sch = ksa.create_schematic("My Circuit")                   │
│  sch.components.add("Device:R", "R1", "10k", (100, 100))    │
│  sch.save("circuit.kicad_sch")                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Schematic Object                          │
│  - Components Collection                                     │
│  - Wires Collection                                         │
│  - Labels Collection                                        │
│  - Configuration                                            │
│  - Managers (Sheet, Wire, FormatSync)                       │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│              Collections (BaseCollection)                    │
│  - UUID-based indexing (O(1) lookups)                       │
│  - Specialized indexes (reference, lib_id, etc.)            │
│  - Modification tracking                                    │
│  - Validation                                               │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Element Wrappers                            │
│  Component, Wire, Label, Junction, Text, etc.               │
│  - Property access                                          │
│  - Validation                                               │
│  - Type safety                                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Types                                │
│  SchematicSymbol, Wire, Label, Point, etc.                  │
│  - Dataclasses holding raw data                             │
│  - S-expression representation                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│            Parser / Formatter                               │
│  Parser: S-expression → Python objects                      │
│  Formatter: Python objects → S-expression                   │
│  - Exact format preservation                                │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  KiCAD Files                                │
│  .kicad_sch files (S-expression format)                     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Schematic Object (`core/schematic.py`)

The main entry point. Coordinates all operations.

**Responsibilities:**
- Create/load/save schematics
- Manage collections (components, wires, labels, etc.)
- Coordinate managers (sheet, wire, format sync)
- Provide high-level convenience methods

**Example:**
```python
sch = ksa.create_schematic("My Circuit")
# sch.components → ComponentCollection
# sch.wires → WireCollection
# sch.labels → LabelCollection
# etc.
```

### 2. Collections (`core/collections/`)

Collections manage groups of elements with optimized lookups.

**Base Collection (`base.py`):**
- Generic class: `BaseCollection[T]`
- UUID-based indexing for O(1) lookups
- Modification tracking
- Standard collection operations (__len__, __iter__, etc.)

**Specialized Collections:**
- `ComponentCollection`: Reference + lib_id + value indexes
- `WireCollection`: UUID + point-based searches
- `LabelCollection`: UUID + text indexes
- `JunctionCollection`: UUID + position indexes
- `TextCollection`: UUID + content indexes
- `NoConnectCollection`: UUID + position indexes
- `NetCollection`: UUID (name as identifier) + name index

**Why collections?**
- Fast lookups: `sch.components.get("R1")` is O(1)
- Bulk operations: Update 100 components at once
- Type safety: Generic[T] with full type checking
- Consistent API across all element types

**Example:**
```python
# O(1) lookup by reference
resistor = sch.components.get("R1")

# Filter by library
all_resistors = sch.components.filter(lib_id="Device:R")

# Bulk update
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)
```

### 3. Element Wrappers (`core/components.py`, `core/labels.py`, etc.)

Wrapper objects provide intuitive access to element properties.

**Component Example:**
```python
class Component:
    @property
    def reference(self) -> str:
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        # Validation
        if not self._validator.validate_reference(value):
            raise ValidationError(f"Invalid reference: {value}")

        # Update indexes
        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
```

**Benefits:**
- Property validation on set
- Automatic index updates
- Type hints and IDE support
- Clean, Pythonic API

### 4. Data Types (`core/types.py`)

Dataclasses holding the raw schematic data.

```python
@dataclass
class SchematicSymbol:
    """Raw component data."""
    uuid: str
    lib_id: str
    position: Point
    reference: str
    value: str
    footprint: Optional[str]
    unit: int
    properties: Dict[str, str]
    pins: List[SchematicPin]

@dataclass
class Wire:
    """Raw wire data."""
    uuid: str
    points: List[Point]
    wire_type: WireType
    stroke_width: float

@dataclass
class Point:
    """2D coordinate."""
    x: float
    y: float
```

**Why dataclasses?**
- Immutable-ish data storage
- Easy serialization
- Type hints
- Clean separation from logic

### 5. Parser & Formatter (`parsers/`)

Convert between S-expressions and Python objects.

**Parser (`parsers/parser.py`):**
```python
def parse_schematic(filepath: str) -> Dict[str, Any]:
    """Parse .kicad_sch file to Python dict."""
    sexpr = read_sexpr_file(filepath)
    data = {
        'version': extract_version(sexpr),
        'components': parse_components(sexpr),
        'wires': parse_wires(sexpr),
        'labels': parse_labels(sexpr),
        # ...
    }
    return data
```

**Formatter (`core/formatter.py`):**
```python
def format_schematic(data: Dict[str, Any]) -> str:
    """Format Python dict to S-expression string."""
    sexpr = [
        'kicad_sch',
        ['version', data['version']],
        ['uuid', data['uuid']],
        # ... exact KiCAD formatting
    ]
    return format_sexpr(sexpr)
```

**Format Preservation:**
- Exact spacing and indentation
- Proper property ordering
- KiCAD-compatible output
- Tested against reference schematics

### 6. Library Integration (`library/`)

Integration with KiCAD symbol libraries.

**SymbolCache (`library/cache.py`):**
```python
cache = get_symbol_cache()
symbol_def = cache.get_symbol("Device:R")

# Returns:
# - Pin definitions (number, position, angle)
# - Reference prefix ("R" for resistors)
# - Default properties
# - Bounding box dimensions
```

**Discovery (`discovery/`):**
- Search KiCAD library directories
- Index components
- Find symbols by name or category

### 7. Managers (`core/managers/`)

Specialized subsystems for complex operations.

**SheetManager:** Hierarchical sheet management
**WireManager:** Wire routing and connections
**FormatSyncManager:** Track changes for format preservation

### 8. Configuration (`core/config.py`)

Centralized configuration system.

```python
config = ksa.config

# Property positioning
config.properties.reference_y = -2.0
config.properties.value_y = 2.0

# Tolerances
config.tolerance.position_tolerance = 0.01

# Defaults
config.defaults.stroke_width = 0.1
config.defaults.project_name = "My Project"

# Grid
config.grid.unit_spacing = 10.0
```

## Data Flow Examples

### Creating a Component

```
1. User Code:
   sch.components.add("Device:R", "R1", "10k", (100, 100))

2. ComponentCollection.add():
   - Validate lib_id with SymbolCache
   - Generate UUID
   - Create SchematicSymbol dataclass
   - Wrap in Component object
   - Add to collection indexes

3. Collections:
   - Add to _items list
   - Add to _uuid_index
   - Add to _reference_index
   - Add to _lib_id_index
   - Mark as modified

4. Return Component wrapper to user
```

### Saving a Schematic

```
1. User Code:
   sch.save("circuit.kicad_sch")

2. Schematic.save():
   - Collect all data from collections
   - Format as Python dict

3. Formatter.format_schematic():
   - Convert dict → S-expression
   - Apply exact KiCAD formatting
   - Preserve property ordering

4. Write to file:
   - Atomic write (temp file + rename)
   - UTF-8 encoding
   - Preserve line endings
```

### Loading a Schematic

```
1. User Code:
   sch = ksa.load_schematic("circuit.kicad_sch")

2. Parser.parse_schematic():
   - Read S-expression file
   - Extract all elements
   - Return Python dict

3. ElementFactory:
   - Create dataclass objects from parsed data
   - Validate data

4. Schematic initialization:
   - Create collections
   - Populate with elements
   - Set up indexes

5. Return Schematic object to user
```

## Key Design Patterns

### 1. **Collection Pattern**

All element types use consistent collection API:
```python
# Same API for all types
sch.components.get(uuid)
sch.wires.get(uuid)
sch.labels.get(uuid)

# Same bulk operations
sch.components.bulk_update(criteria, updates)
sch.wires.bulk_update(criteria, updates)
```

### 2. **Wrapper Pattern**

Element wrappers provide clean API around raw data:
```python
# Raw data
symbol_data = SchematicSymbol(uuid="...", reference="R1", ...)

# Wrapped for user
component = Component(symbol_data, collection)
print(component.reference)  # Clean property access
component.reference = "R2"  # Validation + index updates
```

### 3. **Factory Pattern**

ElementFactory creates objects from parsed data:
```python
factory = ElementFactory(parsed_data)
components = factory.create_components()
wires = factory.create_wires()
```

### 4. **Manager Pattern**

Complex operations delegated to managers:
```python
sch._sheet_manager.add_sheet(...)
sch._wire_manager.route_between_points(...)
sch._format_sync_manager.mark_dirty(...)
```

### 5. **Configuration Pattern**

Centralized config with dot notation:
```python
config.properties.reference_y = -2.0
config.tolerance.position_tolerance = 0.01
```

## Performance Optimizations

### 1. **O(1) Lookups**
```python
# UUID index: {uuid: index_in_list}
component = sch.components.get("R1")  # O(1), not O(n)
```

### 2. **Lazy Loading**
```python
# Symbol definitions loaded on first access, then cached
symbol_def = cache.get_symbol("Device:R")  # Cached after first call
```

### 3. **Bulk Operations**
```python
# Update 100 components in one operation
sch.components.bulk_update(criteria, updates)  # Much faster than loop
```

### 4. **Indexed Collections**
```python
# Multiple indexes for different access patterns
sch.components._uuid_index       # UUID → component
sch.components._reference_index  # Reference → component
sch.components._lib_id_index     # lib_id → [components]
```

## Extension Points

### Adding New Element Types

1. Create dataclass in `core/types.py`
2. Create element wrapper class
3. Create collection class (inherit from BaseCollection)
4. Add parser in `parsers/elements/`
5. Add formatter logic
6. Add tests

### Adding New Operations

1. Add method to appropriate manager
2. Or add to Schematic class for convenience
3. Update collections if needed
4. Add tests

### Custom Validation

```python
from kicad_sch_api.utils.validation import SchematicValidator

class CustomValidator(SchematicValidator):
    def validate_component(self, component):
        issues = super().validate_component(component)
        # Add custom checks
        if "MPN" not in component.properties:
            issues.append(ValidationIssue("Missing MPN", "warning"))
        return issues
```

## Testing Strategy

### 1. **Format Preservation Tests**
```python
# Load reference schematic created in KiCAD
ref_sch = ksa.load_schematic("tests/reference/single_resistor.kicad_sch")

# Save it
ref_sch.save("output.kicad_sch")

# Compare byte-for-byte
assert files_are_identical("tests/reference/single_resistor.kicad_sch", "output.kicad_sch")
```

### 2. **Unit Tests**
```python
# Test individual components
def test_component_reference_validation():
    with pytest.raises(ValidationError):
        component.reference = "INVALID!"  # Should fail
```

### 3. **Integration Tests**
```python
# Test complete workflows
def test_create_and_save():
    sch = ksa.create_schematic("Test")
    sch.components.add("Device:R", "R1", "10k", (100, 100))
    sch.save("test.kicad_sch")

    # Load and verify
    loaded = ksa.load_schematic("test.kicad_sch")
    assert loaded.components.get("R1").value == "10k"
```

## Common Questions

**Q: Why BaseCollection instead of inheritance?**
A: Generic base class provides type safety and consistent API while allowing specialized behavior in subclasses.

**Q: Why separate wrappers from dataclasses?**
A: Clean separation: dataclasses for data storage, wrappers for API and validation.

**Q: Why managers instead of adding everything to Schematic?**
A: Separation of concerns. Schematic coordinates, managers implement complex operations.

**Q: How is exact format preservation guaranteed?**
A: Formatter uses exact KiCAD spacing/ordering, tested against reference schematics created in KiCAD GUI.

**Q: Can I extend the library?**
A: Yes! Add custom validators, managers, or element types. Modular architecture.

---

**For more details on specific subsystems, see the module docstrings in the code.**
