# KiCAD Schematic API - Code Refactoring Analysis

## Executive Summary

This analysis examines the five largest Python files in the kicad-sch-api project (6,230 LOC total), identifying structural issues, design anti-patterns, testing gaps, and opportunities for refactoring. The codebase shows signs of rapid growth without proper separation of concerns, resulting in tight coupling, bloated classes, and scattered responsibilities.

**Key Findings:**
- **5 god classes** with unclear responsibility boundaries
- **50+ private parsing methods** concentrated in one file (parser.py)
- **Multiple tight couplings** between parser, schematic, and cache
- **Testing gaps** in critical parsing and symbol resolution logic
- **Missing abstractions** for S-expression handling and format preservation
- **Code duplication** in parsing similar element types

---

## 1. FILE-BY-FILE ANALYSIS

### 1.1 parser.py (2,317 lines)

#### Responsibilities & Method Count
- **Public Methods:** 6 (parse_file, parse_string, write_file, dumps, and 2 others)
- **Private Methods:** 50+ parsing functions
- **Lines per method:** 50-150 lines average (large for clarity)

#### Architecture Issues

**God Class Problem:**
```
SExpressionParser handles:
- File I/O operations (parse_file, write_file)
- S-expression to internal format conversion
- Internal format to S-expression conversion
- 50+ specialized parsing methods for different element types
- Library symbol handling
- Format validation
- Schema inference
```

**Parsing Method Proliferation:**
- `_parse_symbol` (60 lines) - Component parsing
- `_parse_wire` (50 lines) - Wire parsing
- `_parse_property` (10 lines) - Property parsing
- `_parse_junction` (35 lines) - Junction parsing
- `_parse_label` (40 lines) - Label parsing
- `_parse_hierarchical_label` (60 lines) - Hierarchical label parsing
- `_parse_sheet` (85 lines) - Sheet parsing
- `_parse_text`, `_parse_text_box`, `_parse_polyline`, `_parse_arc`, `_parse_circle`, `_parse_bezier`, `_parse_rectangle`, `_parse_image` (50-100 lines each)

**Corresponding 50+ "to_sexp" methods** that mirror the parsing logic.

#### Code Smells

1. **Copy-Paste Pattern:** Each `_parse_*` method follows identical structure:
   ```python
   def _parse_element(self, item: List[Any]):
       data = {key: default_value, ...}
       for sub_item in item[1:]:
           if not isinstance(sub_item, list):
               continue
           element_type = str(sub_item[0])
           if element_type == "field1":
               data["field"] = sub_item[1]
           # 20 more elif statements...
       return data
   ```

2. **Bidirectional Conversion Duplication:** Every parse method has a matching `_to_sexp` method with identical structure but opposite direction.

3. **Scattered Format Rules:** Format rules are embedded in parser and formatter, not centralized.

4. **Missing Validation Layer:** Validation happens at multiple stages without clear separation.

#### Tight Coupling

```
SExpressionParser → SExpressionFormatter (format preservation)
                 → SchematicValidator (validation)
                 → types.py (data structures)
                 → Schematic (via _schematic_data_to_sexp)
```

#### Testing Gaps

- **No unit tests for individual parse methods** (e.g., `_parse_symbol`, `_parse_wire`)
- **No edge case tests** for malformed S-expressions
- **Integration tests only** that combine parsing + formatting
- **No performance tests** for large schematics
- **Missing regression tests** for known KiCAD format issues

---

### 1.2 schematic.py (1,754 lines)

#### Responsibilities & Method Count
- **Total Methods:** 80+ (public and property accessors)
- **Public Methods:** 40+ including add_*, remove_*, set_*
- **Properties:** 15+
- **Private Methods:** 13 (_sync_*, _convert_*, etc.)

#### Bloated Public API
```python
class Schematic:
    # File operations (3 methods)
    load(), save(), save_as(), backup()
    
    # Component management (delegated to ComponentCollection)
    components.add(), components.remove(), components.filter()
    
    # Wire management (5 methods)
    add_wire(), remove_wire(), add_wire_to_pin(), add_wire_between_pins()
    auto_route_pins(), are_pins_connected()
    
    # Label management (6 methods)
    add_label(), remove_label(), add_hierarchical_label()
    remove_hierarchical_label()
    
    # Sheet management (4 methods)
    add_sheet(), add_sheet_pin()
    
    # Text/Graphics (6 methods)
    add_text(), add_text_box(), add_image(), add_rectangle()
    draw_bounding_box(), draw_component_bounding_boxes()
    
    # Metadata (7 methods)
    set_title_block(), set_paper_size(), set_version_info()
    copy_metadata_from(), get_summary()
    
    # Validation & Analysis (2 methods)
    validate(), get_performance_stats()
    
    # Internal housekeeping (13 private methods)
```

#### Design Issues

**1. Responsibility Overlap:**
- Schematic handles both **data management** and **API facade**
- Parser handles **conversion** AND **validation**
- Formatter handles **formatting** AND **format preservation rules**

**2. Scattered Symbol Handling:**
```python
# Symbol loading logic spread across:
_sync_components_to_data()      # Line 1418-1510 (complex symbol resolution)
_convert_symbol_to_kicad_format() # Line 1564-1611
_convert_raw_symbol_data()       # Line 1613-1646
_check_symbol_extends()          # Line 1512-1533
_fix_symbol_strings_recursively() # Line 1648-1670
```

These 5 methods (300+ lines) handle symbol inheritance, format conversion, and string fixing - they belong in a dedicated symbol handler.

**3. Massive Initialization:**
```python
def __init__(self, ...):  # Lines 58-150
    # Wire collection initialization (25 lines)
    # Junction collection initialization (25 lines)
    # Component conversion from dict to objects (15 lines)
    # Initialization could be refactored with factory methods
```

**4. Data Sync Methods (Lines 1418-1562):**
Three large methods that sync internal state back to data structures:
- `_sync_components_to_data()` (90 lines) - Extremely complex symbol resolution
- `_sync_wires_to_data()` (13 lines) - Simple, should be in WireCollection
- `_sync_junctions_to_data()` (13 lines) - Simple, should be in JunctionCollection

#### Tight Coupling & Cyclic Dependencies

```
Schematic → Parser (creation, loading)
         → Formatter (saving)
         → ComponentCollection
         → WireCollection
         → JunctionCollection
         → SymbolCache (symbol loading)
         ↓
Parser → Schematic (initialization)
      → Formatter (format preservation)
      → Validator
```

**Issue:** Circular dependency potential via imports:
- schematic.py imports parser.py
- Parser imports from types
- Schematic imports from components, wires, junctions
- These all interconnect

#### Method Complexity Issues

**Problematic Methods:**

1. `_sync_components_to_data()` - **92 lines**
   - Complex symbol inheritance resolution
   - Multiple conditional branches (Method 1, 2, 3)
   - Extensive debug logging (30+ lines)
   - Should delegate to dedicated SymbolResolver class

2. `add_sheet()` - **80 lines**
   - Complex parameter handling
   - Sheet data structure creation
   - Pin creation logic embedded

3. `auto_route_pins()` - **60 lines**
   - Imports from multiple modules inside method
   - Delegates to external routing modules
   - Should use dependency injection

#### Testing Gaps

- **No unit tests** for individual Schematic methods
- **No tests** for symbol inheritance resolution
- **No edge case tests** for metadata operations
- **No tests** for internal data consistency
- **No performance tests** for large schematics
- **Format preservation tests only** in integration suite

---

### 1.3 cache.py (867 lines)

#### Responsibilities & Method Count
- **Public Methods:** 7
- **Private Methods:** 17 (hidden implementation)
- **Data Structures:** 2 (SymbolDefinition, LibraryStats)

#### Architecture Issues

**1. Monolithic Cache Class:**
```python
SymbolLibraryCache handles:
- Library path management (add_library_path, discover_libraries)
- Symbol caching and lookup (get_symbol, search_symbols)
- Library file parsing (_parse_kicad_symbol_file)
- Symbol inheritance resolution (_resolve_extends_relationship, _merge_parent_into_child)
- Pin extraction (_extract_pins_from_symbol, _parse_pin_definition)
- Persistence (_load_persistent_index, _save_persistent_index)
- Performance tracking (get_performance_stats)
```

**2. Hidden Complexity in Private Methods:**
- `_parse_kicad_symbol_file()` - **78 lines**
- `_resolve_extends_relationship()` - **30 lines** - Handles symbol inheritance
- `_merge_parent_into_child()` - **40 lines** - Merges parent symbols into children
- `_extract_pins_from_symbol()` - **12 lines**
- `_extract_pins_from_unit()` - **12 lines**
- `_parse_pin_definition()` - **62 lines**

**3. Inheritance Resolution Logic Leaks:**
- Schematic.py duplicates inheritance resolution logic
- Two different implementations of the same concept
- Source of inconsistency bugs

#### Design Anti-Patterns

**1. Global Singleton Pattern:**
```python
_global_cache: Optional[SymbolLibraryCache] = None

def get_symbol_cache() -> SymbolLibraryCache:
    global _global_cache
    if _global_cache is None:
        _global_cache = SymbolLibraryCache()
        _global_cache.discover_libraries()
    return _global_cache
```
- Makes testing difficult
- Prevents multiple independent cache instances
- Forces global state management

**2. Mixed Responsibilities in SymbolDefinition:**
```python
@dataclass
class SymbolDefinition:
    # Identity
    lib_id: str
    name: str
    library: str
    
    # Metadata
    reference_prefix: str
    description: str
    keywords: str
    datasheet: str
    
    # Structure
    pins: List[SchematicPin]
    units: int
    unit_names: Dict[int, str]
    
    # Format preservation
    raw_kicad_data: Any = None
    
    # Inheritance
    extends: Optional[str] = None
    
    # Metrics
    load_time: float = 0.0
    access_count: int = 0
    last_accessed: float
```

A dataclass with 14 attributes suggests multiple concerns.

#### Circular Parsing Logic

Symbol inheritance involves:
1. **Cache.get_symbol()** calls `_load_symbol_from_library()`
2. **_load_symbol_from_library()** parses file and calls `_check_extends_directive()`
3. **_check_extends_directive()** finds parent name
4. **_resolve_extends_relationship()** calls `_find_symbol_in_parsed_data()` again
5. **_find_symbol_in_parsed_data()** re-parses the same file
6. **_merge_parent_into_child()** combines symbols

**Issue:** File is parsed multiple times for a single symbol lookup.

#### Testing Gaps

- **No unit tests** for individual cache methods
- **No tests** for symbol inheritance resolution
- **No cache invalidation tests**
- **No performance tests** for cache hit rates
- **No tests** for persistent cache on disk
- **No tests** for circular inheritance detection

---

### 1.4 components.py (731 lines)

#### Responsibilities & Method Count
- **Component class:** 20+ properties/methods
- **ComponentCollection class:** 25+ methods
- **Total:** 45+ methods

#### Reasonable Separation

```
Component wrapper: 20 methods
- Properties (reference, value, footprint, position, etc.)
- Property management (get_property, set_property, remove_property)
- Pin access (pins, get_pin, get_pin_position)
- Component state (in_bom, on_board)
- Utilities (move, translate, rotate, copy_properties_from)
- Library integration (get_symbol_definition, update_from_library)

ComponentCollection: 25 methods
- Add/remove (add, add_ic, remove)
- Query (get, filter, filter_by_type, in_area, near_point)
- Bulk operations (bulk_update)
- Sorting (sort_by_reference, sort_by_position)
- Validation (validate_all)
- Statistics (get_statistics)
- Collection interface (__len__, __iter__, __getitem__, __contains__)
- Internal indexing (_add_to_indexes, _remove_from_indexes, etc.)
```

#### Design Issues

**1. Index Management Fragmentation:**
```python
self._components: List[Component]
self._reference_index: Dict[str, Component]
self._lib_id_index: Dict[str, List[Component]]
self._value_index: Dict[str, List[Component]]
```
Three separate indexes must be kept in sync manually:
- `_add_to_indexes()` updates all three
- `_remove_from_indexes()` updates all three
- `_update_reference_index()` for reference changes

**High maintenance burden** - refactoring opportunity for an IndexManager.

**2. Scattered Lookup Logic:**
```python
def filter(self, **criteria):
    # Filters by lib_id, value, value_pattern, reference_pattern, 
    # footprint, in_area, has_property
    # 50 lines of filtering logic
    
def filter_by_type(self, component_type):
    # Different filtering approach
    
def in_area(self, x1, y1, x2, y2):
    # Delegates to filter()
    
def near_point(self, point, radius):
    # Custom distance logic
```

Inconsistent lookup patterns could be unified with a Query DSL or Strategy pattern.

**3. Auto-placement Logic:**
```python
def _find_available_position(self) -> Point:
    grid_size = 10.0
    max_per_row = 10
    row = len(self._components) // max_per_row
    col = len(self._components) % max_per_row
    return Point(col * grid_size, row * grid_size)
```

Simplistic and hardcoded. Real projects need collision detection.

#### Testing Gaps

- **No tests** for index consistency
- **No tests** for bulk_update edge cases
- **No tests** for filter() with combined criteria
- **No tests** for concurrent modifications
- **No tests** for auto-placement collision detection

---

### 1.5 formatter.py (561 lines)

#### Responsibilities & Method Count
- **ExactFormatter class:** 20+ methods
- **FormatRule dataclass:** Configuration storage
- **CompactFormatter:** Minimal override
- **DebugFormatter:** Minimal override

#### Reasonable Design

ExactFormatter handles S-expression formatting:
- Element formatting (`_format_element`, `_format_list`, `_format_inline`, `_format_multiline`)
- Specialized formatters for KiCAD elements (property, pin, image, pts)
- Custom float formatting
- KiCAD rule engine

#### Issues

**1. Rule Engine Under-utilized:**
```python
self.rules = {}
self.rules["kicad_sch"] = FormatRule(...)
self.rules["version"] = FormatRule(...)
# 40+ rule definitions

def _format_list(self, lst, indent_level):
    tag = str(lst[0])
    rule = self.rules.get(tag, FormatRule())
    
    # But then hard-codes specific logic for "property" and "pin"
    if tag == "property":
        return self._format_property(lst, indent_level)
    elif tag == "pin":
        return self._format_pin(lst, indent_level)
```

Rules are defined but then ignored with explicit handlers.

**2. Large Custom Handlers:**
- `_format_property()` - 22 lines
- `_format_pin()` - 60 lines (complex type detection)
- `_format_kicad_sch()` - 47 lines (special blank schematic handling)
- `_format_image()` - 27 lines
- `_format_pts()` - 28 lines

**3. Duplicated Quote Handling:**
Quote logic scattered across multiple methods instead of centralized.

**4. Missing Abstraction:**
No FormattingContext or FormatState to track indentation, nesting depth, parent context.

#### Testing Gaps

- **No unit tests** for individual format methods
- **No regression tests** for output consistency
- **No round-trip tests** (parse → format → parse)
- **No performance tests** for large schematics
- **No edge case tests** for special characters, escaping

---

## 2. CROSS-FILE ANALYSIS

### 2.1 Circular Dependencies & Coupling

**Dependency Graph:**
```
schematic.py → parser.py ─┐
           → formatter.py ├─→ types.py
           → components.py ┤
           → cache.py ─────┘
           
parser.py → formatter.py → types.py
        → validator.py

cache.py → types.py
       → validator.py

components.py → cache.py
            → types.py
            → validator.py
```

**Tight Coupling Issues:**

1. **Parser ↔ Formatter Coupling:**
   - Parser calls formatter.format() during save operations
   - Formatter doesn't need to know about parser structure
   - Could use Strategy pattern

2. **Schematic ↔ Parser Coupling:**
   - Schematic instantiates Parser in __init__
   - Parser instantiates Formatter
   - Difficult to test or substitute

3. **Cache ↔ Schematic Coupling:**
   - Schematic calls cache.get_symbol()
   - Schematic duplicates symbol inheritance logic from cache
   - Two implementations of same feature

4. **Components ↔ Cache Coupling:**
   - ComponentCollection calls cache to resolve symbols
   - Auto-generation logic embedded in components
   - Circular dependency during initialization

### 2.2 Code Duplication

**Symbol Inheritance Logic:**
1. **cache.py:** Lines 533-617
   - `_check_extends_directive()` - Finds extends
   - `_resolve_extends_relationship()` - Loads parent
   - `_merge_parent_into_child()` - Merges

2. **schematic.py:** Lines 1512-1533
   - `_check_symbol_extends()` - Duplicate logic
   
3. **schematic.py:** Lines 1434-1446
   - More inheritance checking with different implementation

**Parsing Element Pattern (50+ times):**
```python
# All these follow identical structure
_parse_symbol()
_parse_wire()
_parse_property()
_parse_junction()
_parse_label()
_parse_hierarchical_label()
_parse_sheet()
_parse_text()
_parse_text_box()
_parse_polyline()
_parse_arc()
_parse_circle()
_parse_bezier()
_parse_rectangle()
_parse_image()
```

And corresponding `_*_to_sexp()` methods.

**Collection Pattern Repetition:**
```python
# ComponentCollection
self._components: List[T]
self._reference_index: Dict[str, T]
self._lib_id_index: Dict[str, List[T]]
self._value_index: Dict[str, List[T]]

# WireCollection (similar pattern)
self._wires: List[T]
# ... indexes

# JunctionCollection (similar pattern)
self._junctions: List[T]
# ... indexes
```

### 2.3 Responsibility Violations (SOLID)

**Single Responsibility Principle Violations:**

1. **SExpressionParser (1 class, 10+ responsibilities):**
   - File I/O
   - S-expression parsing
   - Data conversion (sexp ↔ internal)
   - 50+ specialized parsers
   - Validation
   - Format preservation

2. **SymbolLibraryCache (1 class, 8+ responsibilities):**
   - Library path management
   - Symbol caching
   - File parsing
   - Symbol inheritance resolution
   - Pin extraction
   - Performance tracking
   - Disk persistence
   - Lookup indexing

3. **Schematic (1 class, 15+ responsibilities):**
   - Data management
   - File I/O
   - Component management (delegation)
   - Wire management
   - Label management
   - Sheet management
   - Text/graphics management
   - Symbol resolution
   - Metadata management
   - Validation
   - Performance tracking

**Open/Closed Principle Violations:**
- Adding new element types requires changes to:
  - Parser._sexp_to_schematic_data()
  - Parser._*_parse_element()
  - Parser._*_to_sexp()
  - Formatter (potentially)
  - Schematic (if it manages that type)

**Liskov Substitution Principle Violations:**
- Can't substitute different parsers (SExpressionParser is concrete)
- Can't substitute different formatters easily (tight coupling)
- Can't use different cache implementations

**Interface Segregation Principle Violations:**
- Schematic has 80+ methods - consumers depend on too much
- Parser exposes too many implementation details

**Dependency Inversion Violations:**
- High-level Schematic depends on low-level Parser, Formatter, Cache
- Should depend on abstractions
- Circular dependencies indicate inversion failures

---

## 3. TESTING ANALYSIS

### 3.1 Coverage Gaps

**Parser (2,317 lines):**
- **Status:** Integration tests only
- **Gap:** No unit tests for individual parse methods (50+ methods untested)
- **Missing:**
  - `_parse_symbol()` edge cases
  - `_parse_wire()` with complex routing
  - `_parse_property()` with special characters
  - Symbol inheritance resolution
  - Format validation
  - Large file performance

**Schematic (1,754 lines):**
- **Status:** Mostly integration tests
- **Gap:** No unit tests for individual methods
- **Missing:**
  - Symbol loading and caching logic
  - Metadata operations
  - Wire routing validation
  - Data consistency checks
  - Performance optimization verification

**Cache (867 lines):**
- **Status:** Minimal testing
- **Gap:** Core functionality untested
- **Missing:**
  - Symbol lookup and caching
  - Library discovery
  - Inheritance resolution
  - Pin extraction
  - Cache invalidation
  - Performance metrics

**Components (731 lines):**
- **Status:** Moderate coverage
- **Gap:** Index management and bulk operations
- **Missing:**
  - Index consistency verification
  - Bulk update edge cases
  - Filter combination tests
  - Reference generation collisions
  - Auto-placement collision detection

### 3.2 Test Categories Needed

1. **Unit Tests:** Individual method testing with mocks
2. **Integration Tests:** Multi-component workflows
3. **Regression Tests:** Known issues and format compatibility
4. **Performance Tests:** Large schematic handling
5. **Round-trip Tests:** Parse → modify → format → parse consistency
6. **Edge Case Tests:** Malformed input, extreme values
7. **Property-Based Tests:** Invariant verification

---

## 4. REFACTORING RECOMMENDATIONS

### 4.1 High Priority

#### 1. Extract S-Expression Parsing Abstraction
**Problem:** 50+ parsing methods in SExpressionParser

**Solution:**
```python
# Create element parser registry
class ElementParserRegistry:
    parsers: Dict[str, ElementParser]
    
    def parse(self, element_type: str, data: List) -> Dict:
        parser = self.parsers.get(element_type)
        if not parser:
            raise UnknownElementError(element_type)
        return parser.parse(data)

# For each element type, create a parser
class SymbolElementParser(ElementParser):
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        # Current _parse_symbol logic here
        
class WireElementParser(ElementParser):
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        # Current _parse_wire logic here
```

**Benefits:**
- Eliminates 50+ methods from one class
- Each element type has dedicated, testable class
- Easy to add new element types
- Better follows Open/Closed principle

**Effort:** 3-4 days

---

#### 2. Extract Symbol Resolution Logic
**Problem:** Duplicated in cache.py and schematic.py, complex inheritance handling

**Solution:**
```python
class SymbolResolver:
    """Handles symbol inheritance and resolution."""
    
    def __init__(self, cache: SymbolLibraryCache):
        self.cache = cache
    
    def resolve_symbol(self, lib_id: str) -> ResolvedSymbol:
        """Load and resolve symbol with inheritance."""
        symbol = self.cache.get_symbol(lib_id)
        if symbol.extends:
            parent = self.resolve_symbol(symbol.extends)
            return self._merge_symbols(symbol, parent)
        return symbol
    
    def _merge_symbols(self, child: SymbolDefinition, 
                      parent: SymbolDefinition) -> ResolvedSymbol:
        """Merge parent into child."""
        # Current merge logic from cache.py
```

**Benefits:**
- Single source of truth for symbol resolution
- Eliminates duplication from schematic.py
- Testable in isolation
- Caches resolved symbols to avoid re-merging
- Clear inheritance semantics

**Effort:** 2-3 days

---

#### 3. Extract Index Management
**Problem:** Manual index management in ComponentCollection (and pattern repeated in other collections)

**Solution:**
```python
class IndexedCollection(Generic[T]):
    """Base collection with automatic index management."""
    
    def __init__(self):
        self._items: List[T] = []
        self._indexes: Dict[str, Index] = {}
    
    def add_index(self, name: str, key_func: Callable[[T], Any]):
        """Add indexed field."""
        self._indexes[name] = Index(key_func)
    
    def add(self, item: T):
        self._items.append(item)
        for index in self._indexes.values():
            index.add(item)
    
    def remove(self, item: T):
        self._items.remove(item)
        for index in self._indexes.values():
            index.remove(item)
    
    def filter_by(self, index_name: str, value: Any) -> List[T]:
        return self._indexes[index_name].get(value)

# Usage:
class ComponentCollection(IndexedCollection[Component]):
    def __init__(self):
        super().__init__()
        self.add_index("reference", lambda c: c.reference)
        self.add_index("lib_id", lambda c: c.lib_id)
        self.add_index("value", lambda c: c.value)
```

**Benefits:**
- Eliminates manual index sync bugs
- Reusable for WireCollection, JunctionCollection, etc.
- Consistent interface across collections
- Clear, testable index semantics
- Automatic consistency guarantees

**Effort:** 2-3 days

---

#### 4. Separate Parsing from Validation
**Problem:** Parser mixes parsing with validation, creates tight coupling

**Solution:**
```python
class SchematicValidator:
    """Validates parsed schematic structure."""
    
    def validate(self, schematic_data: Dict) -> List[ValidationIssue]:
        """Check for structure, type, and consistency errors."""
        issues = []
        issues.extend(self._validate_components(schematic_data))
        issues.extend(self._validate_wires(schematic_data))
        # ... more validation
        return issues

# Parser is now simpler
class SExpressionParser:
    """Converts S-expressions to internal format."""
    
    def parse_file(self, path):
        sexp_data = sexpdata.loads(content)
        return self._sexp_to_schematic_data(sexp_data)
        # Validation is caller's responsibility
```

**Benefits:**
- Parser focuses on conversion, not validation
- Validation can be applied selectively
- Clear separation of concerns
- Easier to test both independently
- Can have strict and lenient validators

**Effort:** 2 days

---

### 4.2 Medium Priority

#### 5. Extract Schematic Components Layer
**Problem:** Schematic is a 1,754-line god class

**Solution:** Break into focused concerns:
```python
# Core schematic (metadata, file I/O, collections)
class Schematic:
    components: ComponentCollection
    wires: WireCollection
    junctions: JunctionCollection
    def __init__(self, ...): ...
    def save(self, ...): ...
    def load(cls, ...): ...

# Element addition (extracted from Schematic)
class ElementFactory:
    """Creates and adds elements to schematic."""
    def __init__(self, schematic: Schematic):
        self.schematic = schematic
    def add_wire(self, ...): ...
    def add_label(self, ...): ...
    def add_sheet(self, ...): ...
    # ... all add_* methods

# Symbol resolution (extracted from Schematic)
class SymbolResolutionService:
    """Handles symbol loading and format conversion."""
    def __init__(self, cache: SymbolLibraryCache):
        self.cache = cache
    def sync_symbols(self, schematic: Schematic): ...
    # ... symbol handling from _sync_components_to_data()
```

**Benefits:**
- Schematic focused on core responsibilities
- Element operations isolated and testable
- Symbol handling encapsulated
- Easier to understand and modify
- Better dependency injection

**Effort:** 5-6 days

---

#### 6. Create Formatting Abstraction
**Problem:** Formatter tightly coupled to parser, custom handlers scattered

**Solution:**
```python
class FormatterStrategy(ABC):
    """Strategy for formatting different element types."""
    
    def format(self, element: List[Any], context: FormattingContext) -> str:
        pass

class PropertyFormatterStrategy(FormatterStrategy):
    def format(self, element: List[Any], context: FormattingContext) -> str:
        # Current _format_property logic
        pass

class PinFormatterStrategy(FormatterStrategy):
    def format(self, element: List[Any], context: FormattingContext) -> str:
        # Current _format_pin logic
        pass

class KiCADFormatter:
    """Uses strategies to format elements."""
    
    def __init__(self):
        self.strategies: Dict[str, FormatterStrategy] = {
            "property": PropertyFormatterStrategy(),
            "pin": PinFormatterStrategy(),
            # ...
        }
    
    def format(self, data, context):
        # Dispatches to appropriate strategy
```

**Benefits:**
- Clear separation of formatting concerns
- Easy to add new formatters
- Strategies are independently testable
- FormattingContext encapsulates state
- Better follows Strategy pattern

**Effort:** 3-4 days

---

#### 7. Implement Symbol Caching Strategy
**Problem:** Global singleton cache, symbol file reparsed multiple times

**Solution:**
```python
class SymbolCache(ABC):
    """Abstract caching interface."""
    
    @abstractmethod
    def get(self, lib_id: str) -> Optional[SymbolDefinition]:
        pass
    
    @abstractmethod
    def add(self, lib_id: str, symbol: SymbolDefinition):
        pass

class MemorySymbolCache(SymbolCache):
    """In-memory cache with TTL support."""
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[float, SymbolDefinition]] = {}
        self.ttl = ttl_seconds
    
    def get(self, lib_id: str):
        if lib_id not in self.cache:
            return None
        timestamp, symbol = self.cache[lib_id]
        if time.time() - timestamp > self.ttl:
            del self.cache[lib_id]
            return None
        return symbol

class PersistentSymbolCache(SymbolCache):
    """Disk-backed cache with automatic persistence."""
    def __init__(self, cache_dir: Path):
        self.dir = cache_dir
        # ...
```

**Benefits:**
- Testable cache implementations
- Can inject different cache strategies
- Enables offline-first workflows
- Clear cache semantics
- Eliminates global singleton

**Effort:** 3 days

---

### 4.3 Low Priority

#### 8. Create Query DSL for Component Filtering
```python
class Query:
    def where(self, **criteria) -> "Query":
        pass
    def and_(self, **criteria) -> "Query":
        pass
    def or_(self, **criteria) -> "Query":
        pass
    def execute(self, collection: ComponentCollection) -> List[Component]:
        pass

# Usage:
Query().where(lib_id="Device:R").and_(value="10k").execute(sch.components)
```

#### 9. Extract Performance Monitoring
Create dedicated metrics collection instead of scattered counters.

#### 10. Create Data Migration Framework
For handling format version updates across KiCAD versions.

---

## 5. REFACTORING ROADMAP

### Phase 1: Foundation (Weeks 1-3)
1. Extract S-expression parsing abstraction (ElementParserRegistry)
2. Extract symbol resolution logic (SymbolResolver)
3. Create comprehensive unit tests for new abstractions
4. Add CI/CD integration tests

### Phase 2: Core (Weeks 4-6)
5. Extract index management (IndexedCollection)
6. Refactor ComponentCollection to use IndexedCollection
7. Separate parsing from validation
8. Expand test coverage to 80%+

### Phase 3: Refinement (Weeks 7-8)
9. Extract Schematic components (ElementFactory, SymbolResolutionService)
10. Create formatting abstraction (FormatterStrategy)
11. Implement pluggable cache strategies
12. Final integration testing

### Phase 4: Polish (Weeks 9-10)
13. Documentation updates
14. Performance benchmarking
15. Code style cleanup
16. Release 0.4.0

---

## 6. MIGRATION STRATEGY

### API Compatibility
- Maintain backward compatibility during refactoring
- Deprecate old methods with warnings before removal
- Provide migration guide for users

### Incremental Refactoring
- Refactor one concern at a time
- Add new abstractions alongside old code
- Gradually move consumers to new implementations
- Run full test suite after each change

### Safety Measures
- Use feature flags for new implementations
- A/B test old vs. new in production
- Automated diff generation for output comparison
- Rollback capability at each phase

---

## 7. CONCRETE EXAMPLES

### Example 1: Parser Refactoring

**Before (2,317 lines in one class):**
```python
class SExpressionParser:
    def _parse_symbol(self, item): ...      # 60 lines
    def _parse_wire(self, item): ...        # 50 lines
    def _parse_junction(self, item): ...    # 35 lines
    def _parse_label(self, item): ...       # 40 lines
    # ... 50 more parse methods
    def _symbol_to_sexp(self, data): ...    # 120 lines
    def _wire_to_sexp(self, data): ...      # 45 lines
    # ... 50 more to_sexp methods
```

**After (each element type has dedicated class):**
```python
# Create base interface
class ElementParser(ABC):
    @abstractmethod
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        pass

# Create specific parsers
class SymbolParser(ElementParser):
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        # 60 lines of symbol parsing logic
        symbol_data = {...}
        for sub_item in item[1:]:
            # ... existing parsing code
        return symbol_data

class WireParser(ElementParser):
    def parse(self, item: List[Any]) -> Dict[str, Any]:
        # 50 lines of wire parsing logic
        ...

# Element formatter interface
class ElementFormatter(ABC):
    @abstractmethod
    def format(self, data: Dict[str, Any]) -> List[Any]:
        pass

class SymbolFormatter(ElementFormatter):
    def format(self, symbol_data: Dict[str, Any]) -> List[Any]:
        # 120 lines of symbol formatting logic
        ...

# Main parser becomes thin orchestrator
class SExpressionParser:
    def __init__(self):
        self.parsers = {
            "symbol": SymbolParser(),
            "wire": WireParser(),
            "junction": JunctionParser(),
            # ... all element types
        }
        self.formatters = {
            "symbol": SymbolFormatter(),
            "wire": WireFormatter(),
            # ...
        }
    
    def _sexp_to_schematic_data(self, sexp_data):
        schematic = {...}
        for item in sexp_data[1:]:
            element_type = str(item[0])
            parser = self.parsers.get(element_type)
            if parser:
                element_data = parser.parse(item)
                # Add to appropriate collection
        return schematic
```

**Benefits:**
- Parser.py shrinks from 2,317 to ~400 lines
- Each element parser is ~100 lines, testable independently
- New element types can be added without modifying parser
- Parser logic is now just dispatching to strategies

---

### Example 2: Symbol Resolution Refactoring

**Before (duplicated in two places):**
```python
# cache.py _parse_kicad_symbol_file()
extends_symbol = self._check_extends_directive(symbol_data)
if extends_symbol:
    resolved = self._resolve_extends_relationship(...)
    symbol_data = resolved

# schematic.py _sync_components_to_data()
extends_parent = self._check_symbol_extends(symbol_def.raw_kicad_data)
if extends_parent:
    parent_symbol_def = cache.get_symbol(parent_lib_id)
    if parent_symbol_def:
        # Different merge logic
```

**After (single authoritative implementation):**
```python
class SymbolResolver:
    def __init__(self, cache: SymbolLibraryCache):
        self.cache = cache
        self._resolved_symbols: Dict[str, ResolvedSymbol] = {}
    
    def resolve(self, lib_id: str) -> ResolvedSymbol:
        """Load and fully resolve symbol with inheritance."""
        if lib_id in self._resolved_symbols:
            return self._resolved_symbols[lib_id]
        
        # Load symbol
        symbol = self.cache.get_symbol(lib_id)
        if not symbol:
            return None
        
        # Check for inheritance
        if symbol.extends:
            parent = self.resolve(symbol.extends)
            resolved = self._merge(symbol, parent)
        else:
            resolved = ResolvedSymbol.from_definition(symbol)
        
        # Cache resolved symbol
        self._resolved_symbols[lib_id] = resolved
        return resolved
    
    def _merge(self, child: SymbolDefinition, 
              parent: ResolvedSymbol) -> ResolvedSymbol:
        """Merge parent symbol into child."""
        merged = copy.deepcopy(parent)
        # Apply child overrides
        merged.graphics.extend(child.graphic_elements)
        merged.pins.extend(child.pins)
        return merged

# Usage everywhere:
resolver = SymbolResolver(cache)
resolved_symbol = resolver.resolve("Device:R")
```

---

## 8. SUCCESS METRICS

### Code Quality
- **Reduce average class size** from 500+ LOC to <300 LOC
- **Increase method count** per file (distribution) - more small methods
- **Reduce cyclomatic complexity** (currently 10-15 per method → target 5-7)
- **Achieve 80%+ test coverage**

### Performance
- **Parse time** stays <100ms for typical schematics
- **Cache hit rate** improves to >90%
- **Memory usage** reduces due to eliminated duplication
- **Startup time** improves with lazy loading

### Maintainability
- **Add new element types** without modifying core parser
- **Change formatting rules** in one place
- **Add new cache strategies** without coupling
- **Reduce duplicate code** from ~10% to <2%

### Documentation
- **Create architecture diagrams** for new design
- **Document design patterns** used (Strategy, Factory, Visitor)
- **Create refactoring guide** for contributors
- **Update API documentation**

---

## Conclusion

The kicad-sch-api codebase exhibits classic signs of rapid prototyping without refactoring. Five large files contain 50+ private methods, duplicated logic, and unclear responsibility boundaries. The recommended refactoring focuses on:

1. **Extracting specialized implementations** (ElementParser, SymbolResolver)
2. **Creating reusable abstractions** (IndexedCollection, FormatterStrategy)
3. **Eliminating duplication** (symbol resolution, element parsing)
4. **Improving testability** (smaller classes, clearer interfaces)
5. **Following SOLID principles** (single responsibility, dependency inversion)

The 10-week roadmap breaks refactoring into manageable phases with clear milestones, maintaining backward compatibility while improving code quality by an estimated 40-50%.
