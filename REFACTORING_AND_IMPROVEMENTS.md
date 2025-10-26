# Refactoring and Improvements Analysis

**Date:** 2025-10-26
**Focus:** Code quality improvements, architectural enhancements, and missing KiCAD features
**Target:** Making kicad-sch-api a comprehensive, maintainable, version-resilient API

---

## Part 1: Refactoring Opportunities

### 1.1 DRY Violation: Point Creation from Dict/Tuple

**Issue:** Repeated pattern throughout `schematic.py` for converting position data to Point objects

**Affected Code:** Lines 117-256 in `schematic.py` (and likely elsewhere)

**Current Pattern:**
```python
# Pattern repeated 6+ times
position = junction_dict.get("position", {"x": 0, "y": 0})
if isinstance(position, dict):
    pos = Point(position["x"], position["y"])
elif isinstance(position, (list, tuple)):
    pos = Point(position[0], position[1])
else:
    pos = position
```

**Refactoring Solution:**

Create a helper function in `core/types.py`:
```python
def point_from_dict_or_tuple(data: Union[Dict[str, float], Tuple[float, float], List[float], Point],
                             default: Optional[Point] = None) -> Point:
    """Convert various position formats to Point object.

    Args:
        data: Dict with 'x'/'y' keys, tuple/list of coordinates, or Point
        default: Default point if data is None

    Returns:
        Point object

    Examples:
        point_from_dict_or_tuple({"x": 10, "y": 20})  # -> Point(10, 20)
        point_from_dict_or_tuple((10, 20))  # -> Point(10, 20)
        point_from_dict_or_tuple([10, 20])  # -> Point(10, 20)
        point_from_dict_or_tuple(Point(10, 20))  # -> Point(10, 20)
    """
    if isinstance(data, Point):
        return data
    if isinstance(data, dict):
        return Point(data.get("x", 0), data.get("y", 0))
    if isinstance(data, (list, tuple)) and len(data) >= 2:
        return Point(data[0], data[1])
    if data is None:
        return default or Point(0, 0)
    raise ValueError(f"Cannot convert {type(data)} to Point")
```

**Usage in schematic.py:**
```python
# Before: 12+ lines repeated
pos = Point(position["x"], position["y"]) if isinstance(position, dict) else Point(position[0], position[1])

# After: 1 line
pos = point_from_dict_or_tuple(position)
```

**Impact:**
- ✅ Reduces ~150 lines of code
- ✅ Single source of truth for position conversion
- ✅ Easier to extend with new formats
- ✅ Better error messages

**Priority:** HIGH
**Effort:** 1-2 hours

---

### 1.2 Object Initialization Pattern: Data Conversion in `__init__`

**Issue:** The `Schematic.__init__` method is 450+ lines of repetitive data conversion

**Current Pattern:** Lines 100-290 in `schematic.py`
- Similar code for each collection type (wires, junctions, texts, labels, etc.)
- Type checking and conversion repeated for each element type
- Hard to maintain and prone to bugs

**Refactoring Solution:**

Create an `ElementFactory` class:
```python
class ElementFactory:
    """Factory for creating schematic elements from raw data."""

    @staticmethod
    def create_wire(wire_dict: Dict[str, Any]) -> Wire:
        """Create Wire from dictionary."""
        points = [point_from_dict_or_tuple(p) for p in wire_dict.get("points", [])]
        return Wire(
            uuid=wire_dict.get("uuid", str(uuid.uuid4())),
            points=points,
            wire_type=WireType(wire_dict.get("wire_type", "wire")),
            stroke_width=wire_dict.get("stroke_width", 0.0),
            stroke_type=wire_dict.get("stroke_type", "default"),
        )

    @staticmethod
    def create_junction(junction_dict: Dict[str, Any]) -> Junction:
        """Create Junction from dictionary."""
        return Junction(
            uuid=junction_dict.get("uuid", str(uuid.uuid4())),
            position=point_from_dict_or_tuple(junction_dict.get("position")),
            diameter=junction_dict.get("diameter", 0),
            color=junction_dict.get("color", (0, 0, 0, 0)),
        )

    @staticmethod
    def create_text(text_dict: Dict[str, Any]) -> Text:
        """Create Text from dictionary."""
        return Text(
            uuid=text_dict.get("uuid", str(uuid.uuid4())),
            position=point_from_dict_or_tuple(text_dict.get("position")),
            text=text_dict.get("text", ""),
            rotation=text_dict.get("rotation", 0.0),
            size=text_dict.get("size", 1.27),
            exclude_from_sim=text_dict.get("exclude_from_sim", False),
        )
    # ... similar methods for other types
```

**Usage in Schematic.__init__:**
```python
# Before: 20+ lines of repetitive conversion code
# After:
self._wires = WireCollection([
    ElementFactory.create_wire(w) for w in self._data.get("wires", [])
    if isinstance(w, dict)
])
```

**Impact:**
- ✅ Reduces `Schematic.__init__` from 450 lines to ~100 lines
- ✅ Testable factory methods
- ✅ Easier to add new element types
- ✅ Better error handling

**Priority:** HIGH
**Effort:** 2-3 hours

---

### 1.3 Parser Module Size: Break into Smaller Modules

**Issue:** `parser.py` is 2,351 lines - too large to maintain easily

**Current Structure:**
- Generic parsing logic (~200 lines)
- Element parsers (~1,800 lines): title_block, symbol, wire, junction, label, etc.
- Element serializers (~350 lines)

**Refactoring Solution:**

Create specialized parser modules:
```
kicad_sch_api/core/
├── parser.py (refactored to ~300 lines, main coordinator)
├── parsers/
│   ├── __init__.py
│   ├── base.py (BaseElementParser abstract class)
│   ├── title_block.py (TitleBlockParser)
│   ├── symbol.py (SymbolParser)
│   ├── wire.py (WireParser)
│   ├── junction.py (JunctionParser)
│   ├── label.py (LabelParser)
│   ├── text.py (TextParser)
│   ├── graphic.py (Rectangle, Circle, Arc, Polyline, etc.)
│   ├── image.py (ImageParser)
│   └── sheet.py (SheetParser)
├── formatters/
│   ├── __init__.py
│   ├── base.py (BaseElementFormatter)
│   ├── symbol.py (SymbolFormatter)
│   ├── wire.py (WireFormatter)
│   └── ... (other formatters)
```

**Base class pattern:**
```python
# core/parsers/base.py
class BaseElementParser(ABC):
    """Abstract base for element parsers."""

    @abstractmethod
    def can_parse(self, item: List[Any]) -> bool:
        """Check if this parser handles this element type."""
        pass

    @abstractmethod
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        """Parse element from S-expression."""
        pass

# core/parsers/symbol.py
class SymbolParser(BaseElementParser):
    def can_parse(self, item: List[Any]) -> bool:
        return item and len(item) > 0 and item[0] == "symbol"

    def parse(self, item: List[Any]) -> Dict[str, Any]:
        # Original parser logic from parser.py
        ...
```

**Refactored main parser:**
```python
# core/parser.py
class SExpressionParser:
    def __init__(self, preserve_format: bool = True):
        self._parsers = [
            SymbolParser(),
            WireParser(),
            JunctionParser(),
            LabelParser(),
            TextParser(),
            SheetParser(),
            GraphicParser(),
            ImageParser(),
        ]

    def _parse_element(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Delegate to appropriate parser."""
        for parser in self._parsers:
            if parser.can_parse(item):
                return parser.parse(item)
        return None
```

**Impact:**
- ✅ Each parser file ~150-250 lines (manageable)
- ✅ Easier to understand individual parsers
- ✅ Extensible: easy to add new element types
- ✅ Each parser testable independently
- ✅ Reduced cognitive load on developers

**Priority:** MEDIUM
**Effort:** 4-6 hours

---

### 1.4 Manager Classes: Extract Common Collection Pattern

**Issue:** Collection classes (ComponentCollection, WireCollection, etc.) repeat similar patterns

**Current Pattern:** Each collection has ~200-300 lines with similar methods:
- `add()`, `remove()`, `get()`, `find()`, `filter()`, `bulk_update()`

**Refactoring Solution:**

Create a base collection class:
```python
# core/collections/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Callable, Dict, Any

T = TypeVar('T')

class BaseCollection(ABC, Generic[T]):
    """Base class for schematic element collections."""

    def __init__(self, items: List[T] = None):
        self._items = items or []
        self._index: Dict[str, T] = {}
        self._build_index()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, key: Union[int, str]) -> T:
        if isinstance(key, int):
            return self._items[key]
        return self._index.get(key)

    @abstractmethod
    def _get_key(self, item: T) -> str:
        """Get the unique key for an item (e.g., reference for components)."""
        pass

    @abstractmethod
    def _build_index(self):
        """Build index for fast lookups."""
        for item in self._items:
            key = self._get_key(item)
            if key:
                self._index[key] = item

    def add(self, item: T) -> T:
        """Add item to collection."""
        self._items.append(item)
        key = self._get_key(item)
        if key:
            self._index[key] = item
        return item

    def remove(self, key: str) -> bool:
        """Remove item by key."""
        if key not in self._index:
            return False
        item = self._index.pop(key)
        self._items.remove(item)
        return True

    def get(self, key: str) -> Optional[T]:
        """Get item by key."""
        return self._index.get(key)

    def filter(self, predicate: Callable[[T], bool]) -> List[T]:
        """Filter items by predicate."""
        return [item for item in self._items if predicate(item)]

    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]):
        """Update multiple items matching criteria."""
        for item in self._items:
            if self._matches_criteria(item, criteria):
                self._apply_updates(item, updates)

    @abstractmethod
    def _matches_criteria(self, item: T, criteria: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria."""
        pass

    @abstractmethod
    def _apply_updates(self, item: T, updates: Dict[str, Any]):
        """Apply updates to an item."""
        pass
```

**Usage in ComponentCollection:**
```python
class ComponentCollection(BaseCollection[Component]):
    """Collection of components."""

    def _get_key(self, item: Component) -> str:
        return item.reference

    def _build_index(self):
        for comp in self._items:
            self._index[comp.reference] = comp

    def _matches_criteria(self, item: Component, criteria: Dict[str, Any]) -> bool:
        for key, value in criteria.items():
            if getattr(item, key, None) != value:
                return False
        return True

    def _apply_updates(self, item: Component, updates: Dict[str, Any]):
        for key, value in updates.items():
            setattr(item, key, value)
```

**Impact:**
- ✅ Reduces duplication across 7 collection classes
- ✅ Consistent API across all collections
- ✅ Easier to add new collection types
- ✅ Better type safety with Generic[T]

**Priority:** MEDIUM
**Effort:** 3-4 hours

---

### 1.5 Magic Strings: Configuration Constants

**Issue:** Throughout the codebase: magic strings for element types, wire types, etc.

**Examples:**
- `wire_type = WireType("wire")` - what are valid values?
- `label_type = LabelType("local")` - undocumented
- `shape = HierarchicalLabelShape(...)` - what are options?

**Refactoring Solution:**

Create a configuration module:
```python
# core/config.py - Enhanced
class ElementTypeStrings:
    """Valid string values for element types."""
    WIRE_TYPES = {"wire", "bus"}
    LABEL_TYPES = {"local", "global", "hierarchical"}
    HIERARCHICAL_SHAPES = {"input", "output", "bidirectional", "tristate"}
    STROKE_TYPES = {"solid", "dash", "dot", "dashdot"}
    FILL_TYPES = {"none", "outline", "background"}

class Defaults:
    """Default values for schematic elements."""
    POSITION = {"x": 0, "y": 0}
    STROKE_WIDTH = 0.0
    STROKE_TYPE = "default"
    TEXT_SIZE = 1.27
    JUNCTION_DIAMETER = 0
    PIN_LENGTH = 2.54

class KiCADVersion:
    """Version-specific features."""
    V6 = "6.0"
    V7 = "7.0"
    V8 = "8.0"
    CURRENT = V8

    FEATURE_SUPPORT = {
        "vector_buses": {V6, V7, V8},
        "group_buses": {V7, V8},
        "orthogonal_dragging": {V7, V8},
        "custom_fonts": {V7, V8},
        "properties_panel": {V8},
        "search_panel": {V8},
        "grid_overrides": {V8},
        "power_symbol_net_name": {V8},
        "automatic_label_creation": {V8},
    }

    @classmethod
    def supports(cls, feature: str, version: str = CURRENT) -> bool:
        """Check if feature is supported in version."""
        return version in cls.FEATURE_SUPPORT.get(feature, set())
```

**Usage:**
```python
# Before
if wire_type not in ["wire", "bus"]:
    raise ValueError("Invalid wire type")

# After
if wire_type not in ElementTypeStrings.WIRE_TYPES:
    raise ValueError(f"Invalid wire type. Must be one of: {ElementTypeStrings.WIRE_TYPES}")

# Version checking
if KiCADVersion.supports("properties_panel"):
    # Only in KiCAD 8+
    ...
```

**Impact:**
- ✅ Centralized configuration
- ✅ Better error messages
- ✅ Foundation for version-specific support
- ✅ IDE autocomplete support

**Priority:** MEDIUM
**Effort:** 1-2 hours

---

### 1.6 Type Hints: Inconsistent and Incomplete

**Issue:** Many functions lack type hints or use `Any` too liberally

**Examples:**
```python
# Before: Poor type hints
def parse_symbol(self, item: List[Any]) -> Optional[Dict[str, Any]]:
    ...

def add_component(self, **kwargs):
    ...

# After: Good type hints
def parse_symbol(self, item: List[Any]) -> Optional[SchematicSymbol]:
    ...

def add_component(
    self,
    lib_id: str,
    reference: str,
    value: str,
    position: Union[Point, Tuple[float, float]],
    **kwargs: Any
) -> Component:
    ...
```

**Refactoring Solution:**

1. Enable `mypy` strict mode in `pyproject.toml`:
```toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

2. Create type aliases for clarity:
```python
# core/types.py - Add these
SchematicData = Dict[str, Any]  # Parsed schematic
ElementDict = Dict[str, Any]     # Element from parser
PropertyDict = Dict[str, str]    # Component properties
PositionInput = Union[Point, Tuple[float, float], List[float], Dict[str, float]]
```

3. Update function signatures:
```python
def point_from_dict_or_tuple(data: PositionInput) -> Point:
    """Convert position to Point."""
    ...

def _parse_element(self, item: List[Any]) -> ElementDict:
    """Parse element from S-expression."""
    ...
```

**Impact:**
- ✅ Better IDE support and autocomplete
- ✅ Catches bugs earlier (mypy static analysis)
- ✅ Clearer documentation via type hints
- ✅ Easier for contributors to use the API correctly

**Priority:** MEDIUM
**Effort:** 3-4 hours (spread across multiple files)

---

## Part 2: Missing KiCAD Features

Based on KiCAD 8 documentation and version comparison, here are features not yet fully implemented:

### 2.1 Bus Support (Partial)

**Status:** ⚠️ Limited implementation

**Missing:**
- ✅ Vector buses (e.g., `DATA[0..7]`) - may be partially supported
- ⚠️ Group buses with custom signal grouping - NOT IMPLEMENTED
- ⚠️ Bus entries (45-degree connectors) - NOT IMPLEMENTED

**Implementation Plan:**

```python
# core/types.py - Add
@dataclass
class Bus:
    """Bus element for grouped signals."""
    uuid: str
    name: str  # e.g., "DATA[0..7]" or "BUS_GROUP"
    signals: List[str]  # Individual signal names
    bus_type: Literal["vector", "group"] = "vector"

# core/buses.py - New file
class BusCollection(BaseCollection[Bus]):
    """Collection of buses in schematic."""
    ...

# core/schematic.py - Add property
@property
def buses(self) -> BusCollection:
    return self._buses
```

**Priority:** HIGH (for KiCAD 7/8 compatibility)
**Effort:** 3-4 hours

---

### 2.2 Electrical Rules Check (ERC) Validation

**Status:** ❌ NOT IMPLEMENTED

**Missing:**
- Pin connection validation (e.g., output to output conflict)
- Power supply validation (unpowered chips)
- Dangling wire detection
- Duplicate reference detection
- Undriven signal detection

**Implementation Plan:**

```python
# core/erc.py - New file
class ElectricalRulesChecker:
    """KiCAD Electrical Rules Check equivalent."""

    def check_pin_conflicts(self) -> List[ErcViolation]:
        """Check for conflicting pin connections."""
        violations = []
        # Check each net for pin type conflicts
        # Output to output = error
        # Input to input = warning
        # Open collector chains = ok
        ...
        return violations

    def check_power_supplies(self) -> List[ErcViolation]:
        """Check that all chips have power/ground."""
        ...

    def check_undriven_signals(self) -> List[ErcViolation]:
        """Find signals with no driver."""
        ...

    def check_duplicate_references(self) -> List[ErcViolation]:
        """Find duplicate component references."""
        ...

    def run_all_checks(self) -> List[ErcViolation]:
        """Run all ERC checks."""
        violations = []
        violations.extend(self.check_pin_conflicts())
        violations.extend(self.check_power_supplies())
        violations.extend(self.check_undriven_signals())
        violations.extend(self.check_duplicate_references())
        return violations
```

**Priority:** HIGH (core validation feature)
**Effort:** 6-8 hours

---

### 2.3 Netlist Generation

**Status:** ⚠️ Partial (net extraction exists, full netlist export missing)

**Missing:**
- SPICE netlist generation
- Eagle netlist format
- KiCAD native netlist format
- EDIF format
- Simulation directives support

**Implementation Plan:**

```python
# core/netlist.py - New file
from enum import Enum

class NetlistFormat(Enum):
    KICAD = "kicad"
    SPICE = "spice"
    EAGLE = "eagle"
    EDIF = "edif"

class NetlistGenerator:
    """Generate netlists in various formats."""

    def generate_kicad(self) -> str:
        """Generate KiCAD native netlist format."""
        ...

    def generate_spice(self, include_models: bool = True) -> str:
        """Generate SPICE netlist with component models."""
        ...

    def generate_eagle(self) -> str:
        """Generate Eagle netlist format."""
        ...

    def export(self, format: NetlistFormat) -> str:
        """Export netlist in requested format."""
        if format == NetlistFormat.KICAD:
            return self.generate_kicad()
        elif format == NetlistFormat.SPICE:
            return self.generate_spice()
        ...

# Usage
netlist_gen = NetlistGenerator(schematic)
spice_netlist = netlist_gen.generate_spice()
```

**Priority:** HIGH (common export requirement)
**Effort:** 6-8 hours

---

### 2.4 Bill of Materials (BOM) Generation

**Status:** ⚠️ Partial (component list exists, BOM export missing)

**Missing:**
- CSV/Excel export
- Custom field mapping
- Quantity aggregation
- Pricing integration (optional)
- CSV column customization

**Implementation Plan:**

```python
# core/bom.py - New file
from enum import Enum
from dataclasses import dataclass

@dataclass
class BOMEntry:
    quantity: int
    reference: str
    value: str
    lib_id: str
    footprint: str
    properties: Dict[str, str]

class BOMFormat(Enum):
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    TSV = "tsv"

class BOMGenerator:
    """Generate Bill of Materials."""

    def group_by_value(self) -> Dict[str, List[Component]]:
        """Group components by value."""
        ...

    def generate_entries(self) -> List[BOMEntry]:
        """Generate BOM entries."""
        entries = []
        grouped = self.group_by_value()
        for value, components in grouped.items():
            entry = BOMEntry(
                quantity=len(components),
                reference=", ".join(c.reference for c in components),
                value=value,
                lib_id=components[0].lib_id,
                footprint=components[0].footprint or "",
                properties=components[0].properties,
            )
            entries.append(entry)
        return entries

    def export_csv(self, filepath: str, columns: List[str] = None):
        """Export BOM as CSV."""
        if columns is None:
            columns = ["Quantity", "Reference", "Value", "LibID", "Footprint"]
        ...

    def export_excel(self, filepath: str):
        """Export BOM as Excel file."""
        ...

    def export(self, filepath: str, format: BOMFormat):
        """Export BOM in requested format."""
        ...

# Usage
bom = BOMGenerator(schematic)
bom.export_csv("output.csv")
bom.export_excel("output.xlsx")
```

**Priority:** HIGH (common export requirement)
**Effort:** 4-6 hours

---

### 2.5 Simulation and SPICE Support

**Status:** ⚠️ Minimal (SPICE simulation exists, not fully integrated)

**Missing:**
- Component model management
- Simulation parameter directives (.param, .include)
- Multiple analysis types (DC, AC, transient, parametric)
- Simulation results parsing
- Plot generation

**Implementation Plan:**

```python
# core/simulation.py - New file
from enum import Enum

class AnalysisType(Enum):
    DC = "dc"
    AC = "ac"
    TRANSIENT = "transient"
    PARAMETRIC = "parametric"
    OPERATING_POINT = "op"

@dataclass
class SimulationDirective:
    """SPICE simulation directive."""
    directive: str  # e.g., ".tran 0 1u"
    analysis_type: AnalysisType

class SimulationManager:
    """Manage circuit simulation."""

    def add_directive(self, directive: str, analysis_type: AnalysisType):
        """Add simulation directive."""
        ...

    def set_component_model(self, reference: str, model_name: str, model_file: str):
        """Set SPICE model for component."""
        ...

    def generate_spice_netlist(self) -> str:
        """Generate complete SPICE netlist with directives."""
        ...

    def run_simulation(self, simulator: str = "ngspice") -> SimulationResult:
        """Run simulation with ngspice or other simulator."""
        ...
```

**Priority:** MEDIUM (advanced feature)
**Effort:** 8-10 hours

---

### 2.6 Text Variables and Formatting

**Status:** ⚠️ Partial

**Missing:**
- Text variable substitution (e.g., `${KICAD_PROJECT_NAME}`)
- Markup support
- Dynamic field substitution
- Custom variable definitions

**Implementation Plan:**

```python
# core/text_variables.py - New file
from typing import Dict

class TextVariables:
    """Manage text variables and substitution."""

    # Built-in variables
    BUILTIN = {
        "KICAD_PROJECT_NAME": lambda: project_name,
        "KICAD_FILE": lambda: current_file,
        "KICAD_TIMESTAMP": lambda: datetime.now().isoformat(),
    }

    def __init__(self):
        self.custom_vars: Dict[str, str] = {}

    def define(self, name: str, value: str):
        """Define custom variable."""
        self.custom_vars[name] = value

    def substitute(self, text: str) -> str:
        """Substitute variables in text."""
        result = text
        # Substitute ${VAR_NAME} patterns
        for var_name, var_value in {**self.BUILTIN, **self.custom_vars}.items():
            pattern = f"${{{var_name}}}"
            result = result.replace(pattern, var_value)
        return result

    def apply_to_component(self, component: Component):
        """Apply variable substitution to component."""
        component.value = self.substitute(component.value)
        for key, value in component.properties.items():
            component.properties[key] = self.substitute(value)
```

**Priority:** MEDIUM (formatting feature)
**Effort:** 2-3 hours

---

### 2.7 Hierarchy and Sheet Management

**Status:** ⚠️ Partial (basic sheets supported, advanced hierarchy missing)

**Missing:**
- Complex hierarchies (sheets used multiple times)
- Cross-sheet signal tracking
- Sheet pin validation
- Flat vs. hierarchical mode switching
- Sheet schematic file generation

**Enhancement Plan:**

```python
# core/hierarchy.py - New file
class HierarchyManager:
    """Manage schematic hierarchy."""

    def add_hierarchical_sheet(
        self,
        name: str,
        filename: str,
        position: Point,
        size: Tuple[float, float],
        sheet_pins: List[Sheet Pin],
    ) -> Sheet:
        """Add hierarchical sheet with pins."""
        ...

    def get_sheet_hierarchy(self) -> Dict[str, Any]:
        """Get hierarchy tree structure."""
        ...

    def validate_hierarchy(self) -> List[HierarchyError]:
        """Validate hierarchical connections."""
        ...

    def flatten_hierarchy(self) -> Schematic:
        """Flatten hierarchy into single schematic."""
        ...

    def trace_signal_across_hierarchy(self, signal_name: str) -> List[SignalPath]:
        """Trace signal through hierarchy."""
        ...

class HierarchyError:
    """Hierarchy validation error."""
    error_type: Literal["unconnected_pin", "undefined_signal", "circular_reference"]
    location: str
    message: str
```

**Priority:** MEDIUM
**Effort:** 6-8 hours

---

### 2.8 Advanced Wire Routing

**Status:** ⚠️ Partial (Manhattan routing exists, limited options)

**Missing:**
- 45-degree routing mode (for KiCAD 6 compatibility)
- Avoidance of component bounding boxes
- Custom trace width
- Differential pair routing
- Length matching
- Dynamic obstacle avoidance

**Enhancement Plan:**

```python
# core/routing.py - New file
class RoutingMode(Enum):
    MANHATTAN_90 = "manhattan_90"
    DIAGONAL_45 = "diagonal_45"

class RoutingConstraints:
    """Routing constraints and rules."""
    min_clearance: float = 0.2  # mm
    trace_width: float = 0.25  # mm
    avoid_obstacles: bool = True
    mode: RoutingMode = RoutingMode.MANHATTAN_90

class AdvancedRouter:
    """Advanced wire routing with constraints."""

    def route_with_constraints(
        self,
        start: Point,
        end: Point,
        constraints: RoutingConstraints,
        obstacles: List[Rectangle] = None,
    ) -> List[Point]:
        """Route with custom constraints."""
        ...

    def route_differential_pair(
        self,
        start_p: Point,
        start_n: Point,
        end_p: Point,
        end_n: Point,
        length_match_tolerance: float = 0.1,
    ) -> Tuple[List[Point], List[Point]]:
        """Route differential pair with length matching."""
        ...
```

**Priority:** LOW (advanced feature)
**Effort:** 8-12 hours

---

## Part 3: Version Compatibility Strategy

### 3.1 Version Detection and Feature Flags

**Current:** Assumes single KiCAD version

**Enhancement:**

```python
# core/version.py - Enhanced
class KiCADVersionManager:
    """Manage version-specific functionality."""

    def __init__(self, detected_version: str = "8.0"):
        self.version = detected_version

    def detect_version_from_file(self, filepath: Path) -> str:
        """Detect KiCAD version from file format."""
        content = filepath.read_text()
        # (kicad_sch (version X.Y))
        match = re.search(r'\(version (\d+\.\d+)\)', content)
        if match:
            return match.group(1)
        return "6.0"  # default

    def supports_feature(self, feature: str) -> bool:
        """Check if current version supports feature."""
        return KiCADVersion.supports(feature, self.version)

    def warn_if_unsupported(self, feature: str):
        """Warn if feature not supported in version."""
        if not self.supports_feature(feature):
            warnings.warn(
                f"Feature '{feature}' not supported in KiCAD {self.version}",
                UserWarning
            )
```

**Usage:**
```python
# Auto-detect version
schematic = load_schematic("circuit.kicad_sch")
version_mgr = KiCADVersionManager()
version_mgr.detect_version_from_file(Path("circuit.kicad_sch"))

# Use features safely
if version_mgr.supports_feature("properties_panel"):
    # Only in 8+
    component.set_property("MPN", "ABC123")
else:
    version_mgr.warn_if_unsupported("properties_panel")
```

**Priority:** HIGH
**Effort:** 2-3 hours

---

### 3.2 Format Versioning

**Current:** Exact preservation but assumes single format

**Enhancement:**

```python
# core/formatter.py - Enhanced
class FormatConverter:
    """Convert between KiCAD versions."""

    def convert_v6_to_v7(self, schematic_data: Dict) -> Dict:
        """Convert KiCAD 6 format to 7."""
        # Add new fields, update structures
        ...

    def convert_v7_to_v8(self, schematic_data: Dict) -> Dict:
        """Convert KiCAD 7 format to 8."""
        # Add properties panel, grid overrides, etc.
        ...

    def upgrade(self, schematic_data: Dict, target_version: str) -> Dict:
        """Upgrade schematic to target version."""
        current = self.detect_version(schematic_data)
        while current < target_version:
            if current == "6.0":
                schematic_data = self.convert_v6_to_v7(schematic_data)
            elif current == "7.0":
                schematic_data = self.convert_v7_to_v8(schematic_data)
        return schematic_data
```

**Priority:** MEDIUM
**Effort:** 3-4 hours

---

## Part 4: Implementation Priority Matrix

```
                        Impact
                    HIGH        MEDIUM        LOW
         ┌──────────────────────────────────────┐
    HIGH │ 1.1, 1.2    2.1, 2.2, 2.3, 2.4     │
         │ 3.1         2.5, 2.6, 2.7          │
         │             3.2                     │
     E   ├──────────────────────────────────────┤
     F   │                                      │
     F   │ 1.3, 1.4    1.5, 1.6                │
 MEDIUM  │             2.8                     │
     O   │                                      │
     R   ├──────────────────────────────────────┤
     T   │            -                   -    │
     LOW │                                      │
         └──────────────────────────────────────┘

Legend:
1.x = Refactoring improvements
2.x = Missing features
3.x = Version compatibility
```

---

## Part 5: Implementation Timeline

### Phase 1: Quick Wins (2-3 weeks)
1. ✅ DRY Violation: Point Creation (1.1) - 1-2 hours
2. ✅ Configuration Constants (1.5) - 1-2 hours
3. ✅ Type Hints (1.6) - 2-3 hours
4. ✅ Version Detection (3.1) - 2-3 hours

**Total:** 6-10 hours
**Impact:** Code quality improvements, foundation for version support

### Phase 2: Major Refactoring (3-4 weeks)
5. ✅ Object Initialization (1.2) - 2-3 hours
6. ✅ Parser Modularization (1.3) - 4-6 hours
7. ✅ Base Collection Class (1.4) - 3-4 hours

**Total:** 9-13 hours
**Impact:** Maintainability, extensibility

### Phase 3: Core Features (4-6 weeks)
8. ✅ Bus Support (2.1) - 3-4 hours
9. ✅ ERC Validation (2.2) - 6-8 hours
10. ✅ Netlist Generation (2.3) - 6-8 hours
11. ✅ BOM Generation (2.4) - 4-6 hours

**Total:** 19-26 hours
**Impact:** Comprehensive feature set

### Phase 4: Advanced Features (6-8 weeks)
12. ✅ Simulation Support (2.5) - 8-10 hours
13. ✅ Text Variables (2.6) - 2-3 hours
14. ✅ Hierarchy Management (2.7) - 6-8 hours
15. ✅ Format Versioning (3.2) - 3-4 hours

**Total:** 19-25 hours
**Impact:** Advanced capabilities

### Phase 5: Optional Enhancements (8-12 weeks)
16. ⭐ Advanced Routing (2.8) - 8-12 hours

**Total:** 8-12 hours
**Impact:** Professional wire routing

---

## Part 6: Success Metrics

### Code Quality
- ✅ mypy strict mode passing
- ✅ No repeated code patterns (DRY violations < 3)
- ✅ All modules < 500 lines
- ✅ All functions < 50 lines (mostly)
- ✅ 80%+ test coverage

### Feature Completeness
- ✅ All KiCAD 8 schematic elements supported
- ✅ Version 6, 7, 8 compatibility detection
- ✅ ERC validation working
- ✅ Netlist and BOM export working
- ✅ SPICE simulation integration

### API Design
- ✅ Clear, consistent interface
- ✅ Full type hints
- ✅ Comprehensive documentation
- ✅ Example for each feature
- ✅ Error messages are helpful

### Performance
- ✅ Load 1000+ component schematic < 1 second
- ✅ Add/remove component < 10ms
- ✅ Netlist generation < 100ms
- ✅ ERC check < 500ms

---

## Conclusion

This analysis identifies:
1. **High-impact refactorings** that improve code quality and maintainability
2. **Critical missing features** needed for a comprehensive KiCAD API
3. **Version compatibility strategy** to support multiple KiCAD versions
4. **Realistic implementation timeline** spanning 3-6 months for full implementation

The recommended approach is:
- **Phase 1-2 (Months 1-2):** Refactoring and code quality improvements
- **Phase 3 (Months 2-3):** Core missing features (ERC, netlist, BOM, buses)
- **Phase 4+ (Months 4+):** Advanced features and optimizations

This will transform kicad-sch-api into a professional, feature-complete library for programmatic KiCAD schematic manipulation.
