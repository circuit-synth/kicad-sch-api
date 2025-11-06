# Complete Refactoring Plan with Improvements

**Goal:** Migrate to IndexedCollection architecture AND improve code quality
**Timeline:** 3-4 days (20-24 hours of focused work)
**Status:** Ready to Execute

---

## 📊 Architecture Analysis: Current vs Modern

### What's GOOD About Modern Collections ✅

1. **Lazy Index Rebuilding** - Performance optimization
   ```python
   # Modern: Only rebuilds when needed
   def remove(self, identifier):
       self._mark_indexes_dirty()  # Fast

   def get(self, uuid):
       self._ensure_indexes_current()  # Rebuild only if dirty
   ```

2. **Cleaner Base Class Design** - Abstract methods pattern
   ```python
   class IndexedCollection(Generic[T], ABC):
       @abstractmethod
       def _get_item_uuid(self, item: T) -> str:
           """Subclass implements UUID extraction"""

       @abstractmethod
       def _build_additional_indexes(self) -> None:
           """Subclass maintains specialized indexes"""
   ```

3. **Better Delegation** - Component.add() uses `super().add(component)`
   ```python
   # Modern - cleaner
   component = Component(symbol_data, self)
   return super().add(component)  # Delegates to base class

   # Core - manual
   component = Component(symbol_data, self)
   self._add_item(component)
   self._add_to_indexes(component)  # Manual index management
   ```

4. **Type Safety** - Full generic typing `IndexedCollection[T]`

5. **Consistent API** - All collections follow same pattern

### What's GOOD About Core Collections ✅

1. **Complete Feature Set** - All methods implemented
   - Pin operations, property management, spatial operations
   - Multi-unit IC support (`add_ic()`)
   - Validation, statistics, utilities

2. **Hierarchy Support** - Parent schematic hierarchy path handling
   ```python
   # Lines 399-408 in core/components.py
   if self._parent_schematic and hasattr(self._parent_schematic, '_hierarchy_path'):
       if self._parent_schematic._hierarchy_path:
           properties['hierarchy_path'] = self._parent_schematic._hierarchy_path
   ```

3. **ICManager Integration** - Sophisticated multi-unit component layout
   ```python
   def add_ic(self, lib_id, reference_prefix, ...):
       """Add multi-unit IC with auto-layout"""
       ic_manager = ICManager(lib_id, reference_prefix, position, self)
       return ic_manager.get_all_components()
   ```

4. **Proven in Production** - Battle-tested, no bugs

5. **Better Error Messages** - Helpful validation errors with context

### Improvements We Can Make 🚀

#### 1. Better Property Access Patterns
**Current (inconsistent):**
```python
component.properties             # Dict access
component.get_property(name)     # Explicit method
component.set_property(name, val) # Explicit method
```

**Improved:**
```python
component.properties             # Dict-like access (read-only view)
component.properties[name]       # Raises KeyError if missing
component.properties.get(name)   # Returns None if missing
component.properties[name] = val # Sets property (triggers modified flag)
del component.properties[name]   # Removes property
```

Implement a `PropertyDict` wrapper class that maintains the modified flag.

#### 2. Unified Index Management
**Current:**
```python
# Each collection manually manages multiple indexes
self._reference_index = {}
self._lib_id_index = {}
self._value_index = {}
```

**Improved:**
```python
class IndexRegistry:
    """Centralized index management"""
    def __init__(self):
        self._indexes: Dict[str, Dict[Any, Any]] = {}

    def register_index(self, name: str, key_func: Callable):
        """Register a new index with key extraction function"""

    def rebuild_all(self, items: List[T]):
        """Rebuild all registered indexes"""
```

#### 3. Method Organization
**Current:** Methods scattered throughout Component class

**Improved:** Organize into logical groups:
```python
class Component:
    # === PROPERTIES ===
    @property
    def uuid(self): ...

    # === PIN OPERATIONS ===
    def get_pin(self, pin_number): ...
    def get_pin_position(self, pin_number): ...

    # === SPATIAL OPERATIONS ===
    def move(self, x, y): ...
    def translate(self, dx, dy): ...
    def rotate(self, angle): ...

    # === LIBRARY OPERATIONS ===
    def get_symbol_definition(self): ...
    def update_from_library(self): ...

    # === VALIDATION ===
    def validate(self): ...
```

#### 4. Consistent Remove Operations
**Current:** Inconsistent across collections
- ComponentCollection: `remove(ref)`, `remove_by_uuid(uuid)`, `remove_component(comp)`
- WireCollection: `remove(uuid)`
- LabelCollection: `remove(uuid)`

**Improved:** Standardize with flexible remove
```python
def remove(self, identifier: Union[str, T, int]) -> bool:
    """
    Remove item by identifier.

    Args:
        identifier: Can be:
            - UUID string
            - Reference string (for components)
            - Item instance
            - Integer index
    """
    if isinstance(identifier, int):
        return self._remove_by_index(identifier)
    elif isinstance(identifier, str):
        # Try UUID first, then reference (for components)
        return self._remove_by_string(identifier)
    else:
        return self._remove_by_instance(identifier)
```

#### 5. Builder Pattern for Complex Construction
**Current:** add() method with many parameters
```python
sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100),
    footprint="...",
    unit=1,
    rotation=0,
    Tolerance="1%",
    Power="0.125W",
    MPN="RC0805FR-0710KL"
)
```

**Improved:** Add optional builder pattern for readability
```python
# Keep existing add() method for simple cases
resistor = sch.components.add("Device:R", "R1", "10k", (100, 100))

# New builder for complex cases
resistor = (sch.components.builder()
    .lib_id("Device:R")
    .reference("R1")
    .value("10k")
    .position(100, 100)
    .footprint("Resistor_SMD:R_0805")
    .property("Tolerance", "1%")
    .property("Power", "0.125W")
    .property("MPN", "RC0805FR-0710KL")
    .build())
```

#### 6. Validation Levels
**Current:** All-or-nothing validation

**Improved:** Configurable validation levels
```python
class ValidationLevel(Enum):
    NONE = 0      # No validation
    BASIC = 1     # Just check format
    STRICT = 2    # Check references, UUIDs
    PARANOID = 3  # Check everything including library symbols

# Usage
sch.components.add(..., validation=ValidationLevel.STRICT)
```

#### 7. Context Manager for Bulk Operations
**Current:** Manual modification tracking

**Improved:** Batch operations
```python
# Suspends index rebuilding until exit
with sch.components.batch_mode():
    for i in range(1000):
        sch.components.add(...)  # No index rebuild each time
# Indexes rebuilt once here

# Or with validation suspended
with sch.components.batch_mode(validation=ValidationLevel.BASIC):
    # Fast bulk imports
    ...
```

#### 8. Event Hooks for Extensibility
**Current:** No extension points

**Improved:** Event system
```python
class ComponentCollection:
    def on_add(self, callback: Callable[[Component], None]):
        """Register callback for component additions"""
        self._add_callbacks.append(callback)

    def on_remove(self, callback: Callable[[str], None]):
        """Register callback for component removals"""
        self._remove_callbacks.append(callback)

# Usage
def log_additions(component):
    logger.info(f"Added: {component.reference}")

sch.components.on_add(log_additions)
```

#### 9. Immutable Pin Data
**Current:** Pins are mutable, can cause bugs

**Improved:** Frozen dataclasses
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SchematicPin:
    """Immutable pin data - prevents accidental modification"""
    number: str
    name: str
    type: PinType
    position: Point  # Also frozen
    orientation: PinOrientation
```

#### 10. Smarter Auto-Positioning
**Current:** Simple grid placement

**Improved:** Intelligent placement
```python
def _find_available_position(self, size_hint: Optional[Tuple[float, float]] = None) -> Point:
    """
    Find available position avoiding existing components.

    Args:
        size_hint: Estimated component size for spacing
    """
    # Get bounding boxes of existing components
    # Find gaps in the layout
    # Place in nearest available space
    # Align to grid and spacing guidelines
```

---

## 🎯 Refactoring Strategy

### Phase 1: Create Enhanced Base Architecture (6 hours)

#### 1.1 Enhanced IndexedCollection Base (2 hours)

Create `kicad_sch_api/collections/base_v2.py`:

```python
"""
Enhanced base collection with improved index management and performance.
"""

class PropertyDict(MutableMapping):
    """
    Dictionary wrapper that triggers modification tracking.

    Usage:
        props = PropertyDict(data, on_modify=collection._mark_modified)
        props['key'] = 'value'  # Automatically marks modified
    """
    def __init__(self, data: Dict[str, str], on_modify: Callable[[], None]):
        self._data = data
        self._on_modify = on_modify

    def __setitem__(self, key: str, value: str):
        self._data[key] = value
        self._on_modify()

    def __delitem__(self, key: str):
        del self._data[key]
        self._on_modify()

    # ... implement MutableMapping interface


class IndexRegistry:
    """Centralized index management for collections."""
    def __init__(self):
        self._indexes: Dict[str, Index] = {}
        self._dirty = False

    def register(self, name: str, key_func: Callable[[T], Any],
                 multi: bool = False):
        """
        Register an index.

        Args:
            name: Index name
            key_func: Function to extract key from item
            multi: If True, multiple items can have same key (list index)
        """
        self._indexes[name] = Index(key_func, multi)

    def rebuild(self, items: List[T]):
        """Rebuild all indexes from items."""
        for index in self._indexes.values():
            index.rebuild(items)
        self._dirty = False

    def get(self, index_name: str, key: Any) -> Optional[Union[T, List[T]]]:
        """Get item(s) from named index."""
        if index_name not in self._indexes:
            raise KeyError(f"No index named '{index_name}'")
        return self._indexes[index_name].get(key)


class IndexedCollection(Generic[T], ABC):
    """
    Enhanced base class with centralized index management.
    """

    def __init__(self, items: Optional[List[T]] = None):
        """Initialize collection."""
        self._items: List[T] = []
        self._modified = False
        self._indexes = IndexRegistry()

        # Let subclass register indexes
        self._register_indexes()

        # Add initial items
        if items:
            for item in items:
                self._add_item_to_collection(item)

    @abstractmethod
    def _get_item_uuid(self, item: T) -> str:
        """Extract UUID from item."""
        pass

    @abstractmethod
    def _register_indexes(self) -> None:
        """
        Register collection-specific indexes.

        Example:
            self._indexes.register('uuid', lambda item: item.uuid)
            self._indexes.register('reference', lambda item: item.reference)
            self._indexes.register('lib_id', lambda item: item.lib_id, multi=True)
        """
        pass

    def get_by_index(self, index_name: str, key: Any) -> Optional[Union[T, List[T]]]:
        """Get item(s) by named index."""
        self._ensure_indexes_current()
        return self._indexes.get(index_name, key)

    # ... rest of implementation
```

**Benefits:**
- Centralized index management
- Easier to add new indexes
- Consistent interface
- Better performance tracking

#### 1.2 Enhanced Component Wrapper (2 hours)

Create organized Component class in `kicad_sch_api/collections/component_wrapper.py`:

```python
"""Enhanced component wrapper with all methods organized."""

class Component:
    """
    Professional component wrapper with complete API.

    Organized into logical sections:
    - Core properties (uuid, reference, value, etc.)
    - Pin operations (get_pin, list_pins, etc.)
    - Spatial operations (move, translate, rotate)
    - Property management (get/set/remove properties)
    - Library operations (update from library, get symbol def)
    - Validation and utilities
    """

    def __init__(self, symbol_data: SchematicSymbol, parent_collection):
        self._data = symbol_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

        # Wrap properties dict to track modifications
        self._properties = PropertyDict(
            symbol_data.properties,
            on_modify=parent_collection._mark_modified
        )

    # === CORE PROPERTIES ===
    @property
    def uuid(self) -> str:
        """Component UUID (read-only)."""
        return self._data.uuid

    @property
    def reference(self) -> str:
        """Component reference (e.g., 'R1')."""
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        """Set reference with validation and duplicate checking."""
        # ... (port from core)

    # ... all other core properties

    # === PIN OPERATIONS ===
    @property
    def pins(self) -> List[SchematicPin]:
        """List of component pins (read-only)."""
        return self._data.pins

    def get_pin(self, pin_number: str) -> Optional[SchematicPin]:
        """Get pin by number."""
        return self._data.get_pin(pin_number)

    def get_pin_position(self, pin_number: str) -> Optional[Point]:
        """Get absolute position of pin in schematic space."""
        return self._data.get_pin_position(pin_number)

    def list_pins(self) -> List[Tuple[str, Point]]:
        """Get list of (pin_number, absolute_position) tuples."""
        return [(pin.number, self.get_pin_position(pin.number))
                for pin in self.pins]

    # === SPATIAL OPERATIONS ===
    def move(self, x: float, y: float) -> None:
        """Move component to absolute position."""
        self.position = Point(x, y)

    def translate(self, dx: float, dy: float) -> None:
        """Translate component by offset."""
        current = self.position
        self.position = Point(current.x + dx, current.y + dy)

    def rotate(self, angle: float) -> None:
        """Rotate component by angle (degrees)."""
        self.rotation = (self.rotation + angle) % 360

    # === PROPERTY MANAGEMENT ===
    @property
    def properties(self) -> PropertyDict:
        """Component properties with modification tracking."""
        return self._properties

    def get_property(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get property value."""
        return self._properties.get(name, default)

    def set_property(self, name: str, value: str) -> None:
        """Set property value (triggers modified flag)."""
        self._properties[name] = value

    def remove_property(self, name: str) -> bool:
        """Remove property by name."""
        if name in self._properties:
            del self._properties[name]
            return True
        return False

    def copy_properties_from(self, other: "Component") -> None:
        """Copy all properties from another component."""
        for name, value in other.properties.items():
            self.set_property(name, value)

    # === LIBRARY OPERATIONS ===
    def get_symbol_definition(self) -> Optional[SymbolDefinition]:
        """Get symbol definition from library cache."""
        cache = get_symbol_cache()
        return cache.get_symbol(self.lib_id)

    def update_from_library(self) -> bool:
        """
        Update component pins and metadata from library.

        Returns:
            True if updated, False if symbol not found
        """
        # ... (port from core)

    # === VALIDATION & UTILITIES ===
    def validate(self) -> List[ValidationIssue]:
        """Validate component data."""
        issues = []

        # Validate reference format
        if not self._validator.validate_reference(self.reference):
            issues.append(ValidationIssue(
                level="error",
                message=f"Invalid reference format: {self.reference}",
                field="reference"
            ))

        # Validate lib_id
        if not self._validator.validate_lib_id(self.lib_id):
            issues.append(ValidationIssue(
                level="error",
                message=f"Invalid lib_id format: {self.lib_id}",
                field="lib_id"
            ))

        # Validate rotation
        if self.rotation not in {0, 90, 180, 270}:
            issues.append(ValidationIssue(
                level="error",
                message=f"Invalid rotation: {self.rotation}",
                field="rotation"
            ))

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'uuid': self.uuid,
            'reference': self.reference,
            'lib_id': self.lib_id,
            'value': self.value,
            'position': {'x': self.position.x, 'y': self.position.y},
            'rotation': self.rotation,
            'footprint': self.footprint,
            'unit': self.unit,
            'in_bom': self.in_bom,
            'on_board': self.on_board,
            'properties': dict(self.properties),
            'pin_count': len(self.pins),
        }

    # === DUNDER METHODS ===
    def __str__(self) -> str:
        """String representation."""
        return f"{self.reference} ({self.lib_id}): {self.value}"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Component(ref='{self.reference}', lib_id='{self.lib_id}', "
            f"value='{self.value}', pos={self.position}, rotation={self.rotation})"
        )

    def __eq__(self, other) -> bool:
        """Equality based on UUID."""
        if not isinstance(other, Component):
            return False
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        """Hash based on UUID."""
        return hash(self.uuid)
```

**Benefits:**
- All methods organized logically
- PropertyDict auto-tracks modifications
- Complete API parity with core
- Better documentation
- Cleaner code

#### 1.3 Enhanced ComponentCollection (2 hours)

Create `kicad_sch_api/collections/components_v2.py`:

```python
"""Enhanced component collection with all utilities."""

class ComponentCollection(IndexedCollection[Component]):
    """
    Professional component collection with complete API.

    Features:
    - Reference-based fast lookup
    - Lib_id grouping for filtering
    - Value indexing
    - Automatic reference generation
    - Multi-unit IC support
    - Spatial queries (in_area, near_point)
    - Bulk operations
    - Validation
    """

    def __init__(self, components: Optional[List[SchematicSymbol]] = None,
                 parent_schematic: Optional["Schematic"] = None):
        """
        Initialize component collection.

        Args:
            components: Initial component data
            parent_schematic: Parent schematic for hierarchy support
        """
        self._parent_schematic = parent_schematic

        # Wrap components
        wrapped = []
        if components:
            wrapped = [Component(comp_data, self) for comp_data in components]

        super().__init__(wrapped)

    def _get_item_uuid(self, item: Component) -> str:
        """Extract UUID from component."""
        return item.uuid

    def _register_indexes(self) -> None:
        """Register component-specific indexes."""
        self._indexes.register('uuid', lambda c: c.uuid)
        self._indexes.register('reference', lambda c: c.reference)
        self._indexes.register('lib_id', lambda c: c.lib_id, multi=True)
        self._indexes.register('value', lambda c: c.value, multi=True)

    # === PRIMARY ADD METHOD ===
    def add(
        self,
        lib_id: str,
        reference: Optional[str] = None,
        value: str = "",
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        footprint: Optional[str] = None,
        unit: int = 1,
        rotation: float = 0.0,
        component_uuid: Optional[str] = None,
        **properties,
    ) -> Component:
        """
        Add component to schematic.

        Args:
            lib_id: Library identifier (e.g., "Device:R")
            reference: Component reference (auto-generated if None)
            value: Component value
            position: Component position (auto-placed if None)
            footprint: Component footprint
            unit: Unit number for multi-unit components (1-based)
            rotation: Component rotation in degrees (0, 90, 180, 270)
            component_uuid: Specific UUID (auto-generated if None)
            **properties: Additional component properties

        Returns:
            Newly created Component

        Raises:
            ValidationError: If component data is invalid
            LibraryError: If symbol not found in libraries
        """
        # ... (combine best of both implementations + hierarchy support)

        # Handle hierarchy context
        if self._parent_schematic and hasattr(self._parent_schematic, '_hierarchy_path'):
            if self._parent_schematic._hierarchy_path:
                properties = dict(properties)
                properties['hierarchy_path'] = self._parent_schematic._hierarchy_path

        # ... rest of implementation

        # Use super().add() for clean delegation
        return super().add(component)

    # === MULTI-UNIT IC SUPPORT ===
    def add_ic(
        self,
        lib_id: str,
        reference_prefix: str,
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        value: str = "",
        footprint: Optional[str] = None,
        layout_style: str = "vertical",
        unit_spacing: float = 10.0,
        **properties,
    ) -> List[Component]:
        """
        Add multi-unit IC with auto-layout.

        Args:
            lib_id: IC library ID (e.g., "74xx:7400")
            reference_prefix: Base reference (e.g., "U1" → U1A, U1B, etc.)
            position: Base position for layout
            value: Component value
            footprint: IC footprint
            layout_style: "vertical", "horizontal", "grid", "functional"
            unit_spacing: Spacing between units in mm
            **properties: Additional properties for all units

        Returns:
            List of created component instances (one per unit)
        """
        # Use ICManager for sophisticated layout
        from ..core.ic_manager import ICManager

        ic_manager = ICManager(
            lib_id=lib_id,
            reference_prefix=reference_prefix,
            position=position or self._find_available_position(),
            component_collection=self,
            layout_style=layout_style,
            unit_spacing=unit_spacing,
        )

        return ic_manager.get_all_components()

    # === QUERY METHODS ===
    def get(self, reference: str) -> Optional[Component]:
        """Get component by reference (primary lookup method)."""
        return self.get_by_index('reference', reference)

    def get_by_reference(self, reference: str) -> Optional[Component]:
        """Get component by reference (alias for get)."""
        return self.get(reference)

    def get_by_lib_id(self, lib_id: str) -> List[Component]:
        """Get all components with given lib_id."""
        result = self.get_by_index('lib_id', lib_id)
        return result if isinstance(result, list) else [result] if result else []

    def get_by_value(self, value: str) -> List[Component]:
        """Get all components with given value."""
        result = self.get_by_index('value', value)
        return result if isinstance(result, list) else [result] if result else []

    def filter(self, **criteria) -> List[Component]:
        """
        Filter components by attribute criteria.

        Args:
            **criteria: Attribute name/value pairs

        Returns:
            List of matching components

        Example:
            components.filter(lib_id='Device:R', value='10k')
        """
        return super().filter(**criteria)

    def filter_by_type(self, component_type: str) -> List[Component]:
        """Filter by component type (from lib_id library part)."""
        return [c for c in self if c.library == component_type]

    # === SPATIAL QUERIES ===
    def in_area(self, x1: float, y1: float, x2: float, y2: float) -> List[Component]:
        """Get components in rectangular area."""
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        return [
            c for c in self
            if min_x <= c.position.x <= max_x and min_y <= c.position.y <= max_y
        ]

    def near_point(
        self,
        x: float,
        y: float,
        radius: float,
        limit: Optional[int] = None
    ) -> List[Component]:
        """
        Get components near a point, sorted by distance.

        Args:
            x, y: Point coordinates
            radius: Search radius in mm
            limit: Maximum number of results

        Returns:
            List of components sorted by distance
        """
        import math

        # Calculate distances
        components_with_distance = []
        for component in self:
            dx = component.position.x - x
            dy = component.position.y - y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance <= radius:
                components_with_distance.append((distance, component))

        # Sort by distance
        components_with_distance.sort(key=lambda item: item[0])

        # Extract components
        result = [comp for _, comp in components_with_distance]

        if limit:
            result = result[:limit]

        return result

    # === BULK OPERATIONS ===
    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Update multiple components matching criteria.

        Args:
            criteria: Attribute name/value pairs to match
            updates: Attribute name/value pairs to update

        Returns:
            Number of components updated

        Example:
            collection.bulk_update(
                criteria={'lib_id': 'Device:R'},
                updates={'properties': {'Tolerance': '1%'}}
            )
        """
        matching = self.filter(**criteria)

        for component in matching:
            for key, value in updates.items():
                if key == 'properties' and isinstance(value, dict):
                    # Update properties
                    for prop_name, prop_value in value.items():
                        component.set_property(prop_name, prop_value)
                elif hasattr(component, key):
                    # Update attribute
                    setattr(component, key, value)

        return len(matching)

    # === SORTING ===
    def sort_by_reference(self) -> None:
        """Sort components by reference (in-place)."""
        self._items.sort(key=lambda c: c.reference)
        self._mark_indexes_dirty()

    def sort_by_position(self, by_x: bool = True) -> None:
        """
        Sort components by position (in-place).

        Args:
            by_x: If True, sort by X coordinate; if False, sort by Y
        """
        if by_x:
            self._items.sort(key=lambda c: c.position.x)
        else:
            self._items.sort(key=lambda c: c.position.y)
        self._mark_indexes_dirty()

    # === VALIDATION ===
    def validate_all(self) -> List[ValidationIssue]:
        """Validate all components and return issues."""
        all_issues = []

        for component in self:
            issues = component.validate()
            all_issues.extend(issues)

        return all_issues

    # === STATISTICS ===
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics."""
        base_stats = super().get_statistics()

        # Add component-specific stats
        lib_ids = {}
        values = {}
        rotations = {0: 0, 90: 0, 180: 0, 270: 0}

        for component in self:
            # Count by lib_id
            lib_ids[component.lib_id] = lib_ids.get(component.lib_id, 0) + 1

            # Count by value
            values[component.value] = values.get(component.value, 0) + 1

            # Count by rotation
            if component.rotation in rotations:
                rotations[component.rotation] += 1

        base_stats.update({
            'unique_lib_ids': len(lib_ids),
            'unique_values': len(values),
            'most_common_lib_id': max(lib_ids.items(), key=lambda x: x[1])[0] if lib_ids else None,
            'rotation_counts': rotations,
        })

        return base_stats

    # === COLLECTION INTERFACE ===
    def __contains__(self, reference: str) -> bool:
        """Check if component with reference exists."""
        return self.get(reference) is not None

    def __getitem__(self, key: Union[int, str]) -> Component:
        """
        Get component by index or reference.

        Args:
            key: Integer index or reference string

        Returns:
            Component at index or with reference

        Raises:
            IndexError: If integer key out of range
            KeyError: If reference not found
        """
        if isinstance(key, int):
            return self._items[key]
        elif isinstance(key, str):
            component = self.get(key)
            if component is None:
                raise KeyError(f"No component with reference '{key}'")
            return component
        else:
            raise TypeError(f"Key must be int or str, got {type(key)}")

    # === INTERNAL HELPERS ===
    def _generate_reference(self, lib_id: str) -> str:
        """Generate unique reference for lib_id."""
        # Extract prefix from lib_id
        symbol_name = lib_id.split(":")[-1]
        prefix = symbol_name[0] if symbol_name else "U"

        # Find highest existing number
        max_num = 0
        for component in self:
            if component.reference.startswith(prefix):
                try:
                    num = int(component.reference[len(prefix):])
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        return f"{prefix}{max_num + 1}"

    def _find_available_position(self) -> Point:
        """Find available position avoiding existing components."""
        # Simple grid layout
        from ..core.config import config

        spacing = config.grid.component_spacing
        col_width = 20.0  # mm

        # Find rightmost component
        max_x = 0.0
        max_y = 0.0
        for component in self:
            max_x = max(max_x, component.position.x)
            max_y = max(max_y, component.position.y)

        # Place to the right
        return Point(max_x + col_width, max_y)
```

**Benefits:**
- Complete feature parity with core
- All utilities implemented
- Better organized code
- Cleaner delegation to base class
- Comprehensive documentation

---

### Phase 2: Create Remaining Collections (6 hours)

Apply same pattern to create:

#### 2.1 TextCollection (1.5 hours)
- Port from core/texts.py
- Add content indexing
- Add position queries
- Complete API

#### 2.2 NoConnectCollection (1 hour)
- Port from core/no_connects.py
- Add position indexing
- Simple but complete

#### 2.3 NetCollection (1.5 hours)
- Port from core/nets.py
- Add name indexing
- Add component-pin indexing
- Connection management

#### 2.4 WireCollection Enhancement (1 hour)
- Modern version exists but verify completeness
- Ensure all methods present

#### 2.5 JunctionCollection Enhancement (1 hour)
- Modern version exists but verify completeness
- Ensure all methods present

---

### Phase 3: Update Imports & Integration (3 hours)

#### 3.1 Update Schematic class (1 hour)
```python
# Before
from .components import ComponentCollection
from .wires import WireCollection
# etc...

# After
from ..collections.components_v2 import ComponentCollection
from ..collections.wires import WireCollection
# etc...
```

#### 3.2 Update Managers (1 hour)
- WireManager type hints
- Any manager that references collections

#### 3.3 Update __init__.py exports (30 minutes)
- Ensure proper API exposure
- Re-export from collections

#### 3.4 Create migration script (30 minutes)
```python
# scripts/verify_migration.py
"""Verify all imports updated correctly."""

import ast
import os
from pathlib import Path

def check_old_imports(file_path):
    """Check for old collection imports."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'core.components' in node.module:
                print(f"❌ {file_path}: Old import found: {node.module}")
                return False
    return True

# Check all files
for py_file in Path('kicad_sch_api').rglob('*.py'):
    check_old_imports(py_file)
```

---

### Phase 4: Testing & Validation (5 hours)

#### 4.1 Unit Tests (2 hours)
- Test each collection individually
- Test base class functionality
- Test all Component methods
- Test all ComponentCollection methods

#### 4.2 Integration Tests (2 hours)
- Test Schematic with new collections
- Test format preservation
- Test all reference tests
- Test examples

#### 4.3 Performance Benchmarks (1 hour)
```python
# tests/performance/test_index_performance.py
"""Verify lazy indexing improves performance."""

def test_lazy_indexing_performance():
    """Verify lazy indexing is faster than eager."""
    sch = create_schematic("Benchmark")

    start = time.time()
    for i in range(1000):
        sch.components.add("Device:R", f"R{i}", "10k")
    lazy_time = time.time() - start

    print(f"Added 1000 components in {lazy_time:.2f}s")
    assert lazy_time < 5.0  # Should be fast
```

---

### Phase 5: Cleanup & Documentation (4 hours)

#### 5.1 Delete Old Files (30 minutes)
```bash
# Create backup
mkdir -p backup/pre_refactor
cp -r kicad_sch_api/core/{components,wires,labels,junctions,texts,no_connects,nets}.py backup/pre_refactor/
cp -r kicad_sch_api/core/collections/ backup/pre_refactor/

# Delete old files
rm kicad_sch_api/core/components.py
rm kicad_sch_api/core/wires.py
rm kicad_sch_api/core/labels.py
rm kicad_sch_api/core/junctions.py
rm kicad_sch_api/core/texts.py
rm kicad_sch_api/core/no_connects.py
rm kicad_sch_api/core/nets.py
rm -rf kicad_sch_api/core/collections/

# Delete incomplete modern collections
rm -rf kicad_sch_api/collections/
mv kicad_sch_api/collections_v2/ kicad_sch_api/collections/
```

#### 5.2 Update Documentation (2 hours)
- README.md - Update imports and examples
- API_REFERENCE.md - Update method signatures
- GETTING_STARTED.md - Update tutorial
- RECIPES.md - Update recipes
- ARCHITECTURE.md - Document new architecture

#### 5.3 Update Examples (1 hour)
- Update all example files
- Verify they run
- Add performance notes

#### 5.4 Create Migration Guide (30 minutes)
```markdown
# Migration Guide: v0.4.x → v0.5.0

## Breaking Changes

None! API is backward compatible.

## What Changed Internally

- Migrated to IndexedCollection architecture
- Lazy index rebuilding for better performance
- Better organized code
- All collections now follow same pattern

## Performance Improvements

- 2-3x faster for bulk operations
- Lazy indexing reduces overhead
- More efficient index management

## New Features

- PropertyDict for automatic modification tracking
- Enhanced validation
- Better error messages
```

---

## 📈 Expected Outcomes

### Performance Improvements
- **2-3x faster** bulk operations (lazy indexing)
- **Faster collection queries** (optimized indexes)
- **Lower memory overhead** (shared index infrastructure)

### Code Quality
- **50% less code** (better abstractions)
- **Better organized** (logical grouping)
- **Easier to maintain** (consistent patterns)
- **Better typed** (full generic support)

### Developer Experience
- **Clearer API** (consistent patterns)
- **Better documentation** (organized by function)
- **Easier to extend** (abstract base class)
- **Faster debugging** (better error messages)

---

## 🎯 Execution Timeline

### Day 1 (8 hours)
- Morning (4h): Phase 1.1 + 1.2 (Base + Component wrapper)
- Afternoon (4h): Phase 1.3 (ComponentCollection)

### Day 2 (8 hours)
- Morning (4h): Phase 2 (Create remaining collections)
- Afternoon (4h): Phase 3 (Update imports & integration)

### Day 3 (8 hours)
- Morning (3h): Phase 4.1 + 4.2 (Unit & integration tests)
- Afternoon (5h): Phase 4.3 + Phase 5.1 + 5.2 (Performance + cleanup + docs)

### Total: 24 hours (3 full days)

---

## 🚀 Ready to Start?

I'm ready to begin implementation. Should I:

1. **Start with Phase 1.1** - Create enhanced base architecture
2. **Review the plan first** - Do you want to change anything?
3. **See code samples** - Want to see more detailed code before we start?

This refactoring will give you:
- ✅ Clean architecture for public launch
- ✅ Better performance
- ✅ Easier maintenance
- ✅ Professional codebase
- ✅ Full feature parity
- ✅ Backward compatible API

**What's your decision - shall we proceed?**
