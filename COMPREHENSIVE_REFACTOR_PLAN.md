# Comprehensive Refactoring Plan - Build it Right

**Goal:** Make kicad-sch-api simpler, more testable, robust, maintainable, documented, and efficient
**Freedom:** Full control - no backward compatibility constraints
**Timeline:** 3-4 days of focused work
**Outcome:** Production-ready architecture for public launch

---

## 🎯 Core Principles

### 1. **Simplicity**
- One obvious way to do things
- Consistent patterns everywhere
- No redundant methods
- Clear naming

### 2. **Testability**
- Pure functions where possible
- Dependency injection
- Easy to mock
- Comprehensive test coverage

### 3. **Robustness**
- Strong validation
- Immutable data where appropriate
- Clear error messages
- No silent failures

### 4. **Maintainability**
- Well-organized code
- Clear separation of concerns
- Documented design decisions
- Easy to extend

### 5. **Documentation**
- Every public method documented
- Architecture guides
- Usage examples
- Decision rationale

### 6. **Efficiency**
- Lazy evaluation
- Efficient indexes
- Minimal allocations
- Performance benchmarks

---

## 📊 Phase 0: Current State Analysis (2 hours)

### 0.1 Circuit-Synth Usage Analysis (1 hour)

Let me analyze how circuit-synth uses this library:

```bash
# Find circuit-synth
cd /Users/shanemattner/Desktop/circuit_synth_repos/
ls -la

# Analyze usage patterns
grep -r "from kicad_sch_api" circuit-synth/ --include="*.py" | sort | uniq
grep -r "\.components\." circuit-synth/ --include="*.py" | head -20
grep -r "\.wires\." circuit-synth/ --include="*.py" | head -20
grep -r "\.add_" circuit-synth/ --include="*.py" | head -20

# Find pain points
grep -r "TODO\|FIXME\|HACK\|WORKAROUND" circuit-synth/ --include="*.py" | grep kicad
```

**Questions to answer:**
- What API patterns does circuit-synth use most?
- Are there any workarounds or hacks?
- What features are unused?
- What's missing that would help?

### 0.2 Current Architecture Analysis (30 min)

**Current pain points identified:**

1. **Dual collection architecture** - 2 implementations, confusion
2. **Inconsistent API** - `sch.add_wire()` vs `sch.wires.add()`
3. **Manual index management** - Each collection manages its own
4. **No modification tracking** - Properties can change without detection
5. **Incomplete modern collections** - Missing 30+ methods
6. **No batch operations** - Slow for bulk changes
7. **No validation levels** - All-or-nothing
8. **Poor test organization** - Tests scattered
9. **Documentation drift** - Docs don't match code

### 0.3 Define Success Metrics (30 min)

**Measurable goals:**

| Metric | Current | Target | Measure |
|--------|---------|--------|---------|
| Lines of code | ~15,000 | ~10,000 | 33% reduction |
| Test coverage | ~60% | >90% | pytest-cov |
| Test count | ~60 | ~150 | Comprehensive |
| Avg method complexity | High | Low | Cyclomatic complexity |
| API consistency | 60% | 100% | Pattern analysis |
| Documentation | 70% | 100% | Every public method |
| Performance (1000 adds) | ~2s | <1s | Benchmark |

---

## 🏗️ Phase 1: Optimal Architecture Design (4 hours)

### 1.1 Collection Architecture

**Decision: Single, clean hierarchy**

```
BaseCollection (Abstract)
├── Properties: _items, _modified, _indexes
├── Methods: add(), remove(), get(), find(), filter()
└── Abstract: _get_uuid(), _register_indexes()

ComponentCollection(BaseCollection)
├── Indexes: uuid, reference, lib_id, value
├── Methods: add_ic(), spatial queries, bulk ops
└── Wrapper: Component class

WireCollection(BaseCollection)
├── Indexes: uuid, endpoint, type
└── Methods: routing queries

LabelCollection(BaseCollection)
├── Indexes: uuid, text, position, type
└── Methods: net queries

JunctionCollection(BaseCollection)
├── Indexes: uuid, position
└── Methods: spatial queries

TextCollection(BaseCollection)
├── Indexes: uuid, content
└── Methods: search

NoConnectCollection(BaseCollection)
├── Indexes: uuid, position
└── Methods: spatial queries

NetCollection(BaseCollection)
├── Indexes: uuid (=name), components
└── Methods: connection management
```

**Key improvements:**
- ONE base class (no core/modern split)
- Consistent interface
- Centralized index management
- Clear hierarchy

### 1.2 API Design

**Decision: Collection-First with Smart Schematic Layer**

```python
# PRIMARY API: Collections (80% of use cases)
sch.components.add("Device:R", "R1", "10k", (100, 100))
sch.wires.add(start=(100, 110), end=(150, 110))
sch.labels.add("VCC", (125, 110))
sch.components.remove("R1")

# SECONDARY API: Schematic (complex operations)
sch.add_wire_between_pins("R1", "2", "R2", "1")  # Needs component lookup
sch.auto_route_pins("R1", "2", "R2", "1")         # Complex routing
sch.are_pins_connected("R1", "2", "R2", "1")     # Connectivity analysis
sch.get_net_for_pin("R1", "2")                   # Net analysis

# REMOVED: Redundant Schematic methods
# sch.add_wire() ❌ - use sch.wires.add()
# sch.add_label() ❌ - use sch.labels.add()
# sch.remove_wire() ❌ - use sch.wires.remove()
```

**Benefits:**
- One obvious way to do things
- Schematic layer only for complex operations
- Consistent, predictable API

### 1.3 Data Model

**Decision: Immutable core, mutable wrapper**

```python
@dataclass(frozen=True)
class Point:
    """Immutable point - prevents accidental modification"""
    x: float
    y: float

@dataclass(frozen=True)
class SchematicPin:
    """Immutable pin data"""
    number: str
    name: str
    type: PinType
    position: Point
    orientation: PinOrientation

@dataclass
class SchematicSymbol:
    """Mutable symbol data (internal)"""
    uuid: str
    lib_id: str
    reference: str
    value: str
    position: Point
    rotation: float
    # ... mutable for internal use

class Component:
    """
    Public wrapper with smart properties.
    - Immutable views where appropriate
    - Modification tracking
    - Validation on changes
    """
    def __init__(self, data: SchematicSymbol, collection):
        self._data = data
        self._collection = collection
        self._properties = PropertyDict(data.properties,
                                       on_modify=collection._mark_modified)
```

**Benefits:**
- Prevents bugs from accidental mutation
- Clear intent (what can/can't change)
- Better for threading/async future use

### 1.4 Index Management

**Decision: Centralized IndexRegistry**

```python
class IndexSpec:
    """Specification for an index"""
    def __init__(self,
                 name: str,
                 key_func: Callable[[T], Any],
                 multi: bool = False,
                 case_sensitive: bool = True):
        self.name = name
        self.key_func = key_func
        self.multi = multi
        self.case_sensitive = case_sensitive

class IndexRegistry:
    """Manages all indexes for a collection"""
    def __init__(self):
        self._specs: Dict[str, IndexSpec] = {}
        self._indexes: Dict[str, Dict[Any, Any]] = {}
        self._dirty = False

    def register(self, spec: IndexSpec):
        """Register an index specification"""

    def rebuild(self, items: List[T]):
        """Rebuild all indexes from items"""

    def get(self, index_name: str, key: Any) -> Optional[Union[T, List[T]]]:
        """Get item(s) from named index"""

# Usage in ComponentCollection
def _register_indexes(self):
    self._indexes.register(IndexSpec('uuid', lambda c: c.uuid))
    self._indexes.register(IndexSpec('reference', lambda c: c.reference))
    self._indexes.register(IndexSpec('lib_id', lambda c: c.lib_id, multi=True))
    self._indexes.register(IndexSpec('value', lambda c: c.value, multi=True))
```

**Benefits:**
- Consistent index management
- Easy to add new indexes
- Performance monitoring
- Clear intent

### 1.5 Modification Tracking

**Decision: PropertyDict with auto-tracking**

```python
class PropertyDict(MutableMapping[str, str]):
    """
    Dictionary that tracks modifications.

    Automatically calls on_modify when properties change.
    Provides dict-like interface.
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

    # ... implement full MutableMapping

# Usage
component.properties['Tolerance'] = '1%'  # Automatically tracked!
del component.properties['OldKey']        # Automatically tracked!
```

**Benefits:**
- No manual tracking needed
- Pythonic interface
- Hard to forget

### 1.6 Validation

**Decision: Configurable validation levels**

```python
class ValidationLevel(IntEnum):
    NONE = 0      # No validation (fast, dangerous)
    BASIC = 1     # Format only (reference, lib_id syntax)
    NORMAL = 2    # Check duplicates, UUIDs (default)
    STRICT = 3    # Check library symbols exist
    PARANOID = 4  # Check everything including pins, connections

# Global default
kicad_sch_api.config.validation_level = ValidationLevel.NORMAL

# Per-operation override
sch.components.add(..., validation=ValidationLevel.STRICT)

# Batch mode
with sch.components.batch_mode(validation=ValidationLevel.BASIC):
    # Fast bulk import
    for row in csv_data:
        sch.components.add(...)
```

**Benefits:**
- Performance when needed
- Safety by default
- Explicit tradeoffs

---

## 🔨 Phase 2: Implementation Plan (16 hours)

### 2.1 Core Infrastructure (4 hours)

**File: `kicad_sch_api/collections/base.py`**

Implement:
- ✅ `IndexSpec` class
- ✅ `IndexRegistry` class
- ✅ `PropertyDict` class
- ✅ `BaseCollection` abstract class
- ✅ `ValidationLevel` enum
- ✅ Full documentation
- ✅ Unit tests for each

### 2.2 Component System (4 hours)

**File: `kicad_sch_api/collections/components.py`**

Implement:
- ✅ `Component` wrapper (all 72 methods, organized)
- ✅ `ComponentCollection` (complete API)
- ✅ Multi-unit IC support (`add_ic`)
- ✅ Spatial queries (`in_area`, `near_point`)
- ✅ Bulk operations
- ✅ Statistics
- ✅ Comprehensive tests

### 2.3 Other Collections (4 hours)

**Files:** `wires.py`, `labels.py`, `junctions.py`, `texts.py`, `no_connects.py`, `nets.py`

Implement each with:
- ✅ Full CRUD operations
- ✅ Specialized indexes
- ✅ Query methods
- ✅ Statistics
- ✅ Tests

### 2.4 Schematic Integration (2 hours)

**File: `kicad_sch_api/core/schematic.py`**

Update to:
- ✅ Use new collections
- ✅ Remove redundant methods
- ✅ Keep only complex operations
- ✅ Update managers
- ✅ Update hierarchy support

### 2.5 Testing (2 hours)

Create comprehensive test suite:
- ✅ Unit tests for each collection
- ✅ Integration tests
- ✅ Format preservation tests
- ✅ Performance benchmarks
- ✅ Edge case tests

---

## 🧪 Phase 3: Testing Strategy (4 hours)

### 3.1 Test Organization

```
tests/
├── unit/
│   ├── collections/
│   │   ├── test_base.py              # BaseCollection tests
│   │   ├── test_components.py        # Component tests
│   │   ├── test_wires.py
│   │   ├── test_labels.py
│   │   └── ...
│   ├── core/
│   │   ├── test_schematic.py
│   │   ├── test_geometry.py
│   │   └── ...
│   └── utils/
├── integration/
│   ├── test_create_schematic.py      # End-to-end workflows
│   ├── test_hierarchical.py
│   └── test_connectivity.py
├── performance/
│   ├── test_bulk_operations.py       # Performance benchmarks
│   └── test_index_performance.py
├── reference/
│   ├── test_format_preservation.py   # Existing reference tests
│   └── ...
└── conftest.py                       # Shared fixtures
```

### 3.2 Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| collections/base.py | 100% |
| collections/components.py | 95% |
| collections/*.py | 90% |
| core/schematic.py | 85% |
| Overall | 90%+ |

### 3.3 Performance Benchmarks

```python
def test_bulk_add_performance():
    """Adding 1000 components should be <1s"""
    sch = create_schematic("Benchmark")

    start = time.time()
    for i in range(1000):
        sch.components.add("Device:R", f"R{i}", "10k")
    duration = time.time() - start

    assert duration < 1.0, f"Too slow: {duration:.2f}s"

def test_query_performance():
    """Querying by reference should be O(1)"""
    sch = create_schematic("Benchmark")
    for i in range(10000):
        sch.components.add("Device:R", f"R{i}", "10k")

    start = time.time()
    for i in range(1000):
        comp = sch.components.get(f"R{random.randint(0, 9999)}")
    duration = time.time() - start

    assert duration < 0.1, f"Queries too slow: {duration:.2f}s"
```

---

## 📚 Phase 4: Documentation Overhaul (4 hours)

### 4.1 API Documentation

**File: `docs/API_REFERENCE_V2.md`**

For every public method:
```python
def add(
    self,
    lib_id: str,
    reference: Optional[str] = None,
    value: str = "",
    position: Optional[Union[Point, Tuple[float, float]]] = None,
    **kwargs
) -> Component:
    """
    Add component to schematic.

    Args:
        lib_id: Library identifier in format "Library:Symbol"
                Examples: "Device:R", "Connector_Generic:Conn_01x02"
        reference: Component reference (e.g., "R1", "U1")
                  Auto-generated if None (e.g., "R1", "R2", ...)
        value: Component value (e.g., "10k", "100nF", "STM32F103")
        position: Position in mm as (x, y) tuple or Point
                 Auto-placed if None
        **kwargs: Additional properties (Tolerance, Power, MPN, etc.)

    Returns:
        Component: Newly created component instance

    Raises:
        ValidationError: If lib_id invalid or reference already exists
        LibraryError: If symbol not found in KiCAD libraries

    Examples:
        >>> # Basic resistor
        >>> r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))

        >>> # With properties
        >>> r2 = sch.components.add(
        ...     "Device:R", "R2", "10k", (110, 100),
        ...     footprint="Resistor_SMD:R_0805",
        ...     Tolerance="1%",
        ...     Power="0.125W"
        ... )

        >>> # Auto-generated reference
        >>> r3 = sch.components.add("Device:R", value="10k")
        >>> print(r3.reference)  # "R3"

    Notes:
        - Position is automatically snapped to KiCAD grid (1.27mm)
        - Reference must be unique within schematic
        - Rotation must be 0, 90, 180, or 270 degrees

    See Also:
        - add_ic() for multi-unit components
        - Component class for available properties
        - remove() for removing components
    """
```

### 4.2 Architecture Guide

**File: `docs/ARCHITECTURE_V2.md`**

Document:
- Collection hierarchy
- Index management
- Modification tracking
- Validation strategy
- Performance characteristics
- Extension points

### 4.3 Migration Guide

**File: `docs/MIGRATION_V04_TO_V05.md`**

```markdown
# Migration Guide: v0.4.x → v0.5.0

## Breaking Changes

### Removed Methods

These Schematic methods were redundant - use collections instead:

| Removed | Use Instead |
|---------|-------------|
| `sch.add_wire()` | `sch.wires.add()` |
| `sch.add_label()` | `sch.labels.add()` |
| `sch.remove_wire()` | `sch.wires.remove()` |

### API Changes

**ComponentCollection.remove()** now accepts multiple types:
```python
# Old (still works)
sch.components.remove_by_uuid(uuid)
sch.components.remove_component(comp)

# New (unified)
sch.components.remove("R1")          # By reference
sch.components.remove(uuid)          # By UUID
sch.components.remove(comp_object)   # By object
```

## New Features

- PropertyDict for automatic modification tracking
- Configurable validation levels
- Batch mode for performance
- Better error messages
- Comprehensive documentation

## Performance Improvements

- 2-3x faster bulk operations
- O(1) lookups by reference/UUID
- Lazy index rebuilding
```

### 4.4 Examples

**File: `docs/EXAMPLES.md`**

Real-world examples:
- Creating common circuits
- Hierarchical designs
- Wire routing patterns
- Bulk operations
- Performance optimization

---

## 🔧 Phase 5: Circuit-Synth Update (2 hours)

### 5.1 Update Imports
### 5.2 Use Collection-First API
### 5.3 Remove Workarounds
### 5.4 Test Integration

---

## 📈 Success Metrics (Final Validation)

After refactoring, verify:

✅ **Simplicity**
- [ ] One way to do each operation
- [ ] Consistent patterns throughout
- [ ] Clear, obvious API

✅ **Testability**
- [ ] >90% test coverage
- [ ] >150 tests
- [ ] All edge cases covered

✅ **Robustness**
- [ ] Comprehensive validation
- [ ] Clear error messages
- [ ] No silent failures

✅ **Maintainability**
- [ ] Well-organized code (10K lines, down from 15K)
- [ ] Clear architecture
- [ ] Documented decisions

✅ **Documentation**
- [ ] Every public method documented
- [ ] Architecture guide complete
- [ ] Migration guide clear
- [ ] Examples comprehensive

✅ **Efficiency**
- [ ] <1s to add 1000 components
- [ ] O(1) lookups
- [ ] Performance benchmarks pass

---

## 🚀 Execution Plan

**Ready to start?** I'll begin with:

1. **Phase 0** (2h) - Analyze circuit-synth usage patterns
2. **Phase 1** (4h) - Design complete architecture
3. **Phase 2** (16h) - Implement everything
4. **Phase 3** (4h) - Comprehensive testing
5. **Phase 4** (4h) - Documentation overhaul
6. **Phase 5** (2h) - Circuit-synth update

**Total: 32 hours = 4 days**

**Shall I start with Phase 0 - analyzing circuit-synth?**
