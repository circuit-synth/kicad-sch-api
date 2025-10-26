# KiCAD Schematic API Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring strategy for the kicad-sch-api project to address critical architectural issues, improve maintainability, and establish a solid foundation for future development.

## Current State Analysis

### Large File Issues
- **parser.py** (2,317 LOC): Single class with 55+ methods, massive responsibility scope
- **schematic.py** (1,754 LOC): God class with 80+ methods across 15 different concerns
- **cache.py** (867 LOC): Monolithic symbol caching with circular parsing logic
- **components.py** (731 LOC): Index fragmentation across multiple collections
- **formatter.py** (561 LOC): Underutilized rules engine with growth potential

### Critical Architectural Problems

1. **God Classes & Single Responsibility Violations**
   - `SExpressionParser`: 50+ private parsing methods in one class
   - `Schematic`: Handles parsing, validation, I/O, collections, manipulation
   - `SymbolLibraryCache`: Caching, parsing, inheritance resolution, file I/O

2. **Tight Coupling & Circular Dependencies**
   - Parser → Schematic → Components → Cache → Parser cycle
   - Missing abstractions for core concepts
   - Direct implementation dependencies instead of interfaces

3. **Code Duplication**
   - Symbol inheritance logic implemented differently in cache vs schematic
   - Parsing patterns repeated 50+ times with identical structure
   - Collection indexing duplicated across 3 collection classes

4. **Testing Gaps**
   - Individual parser methods untested
   - Symbol resolution logic untested
   - No round-trip integration tests
   - Performance testing missing

## Refactoring Strategy

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Establish clean interfaces and break core dependencies

#### 1.1 Extract Core Interfaces
```python
# New: kicad_sch_api/interfaces/
class IElementParser(Protocol):
    def can_parse(self, element: List[Any]) -> bool: ...
    def parse(self, element: List[Any]) -> Dict[str, Any]: ...

class ISchematicRepository(Protocol):
    def load(self, path: Path) -> Dict[str, Any]: ...
    def save(self, data: Dict[str, Any], path: Path) -> None: ...

class ISymbolResolver(Protocol):
    def resolve_symbol(self, lib_id: str) -> Optional[Dict[str, Any]]: ...
```

#### 1.2 Break Parser Monolith
```python
# Split parser.py into specialized parsers
parsers/
├── __init__.py
├── base.py          # Base parser interface
├── symbol_parser.py # Symbol-specific parsing
├── wire_parser.py   # Wire and connection parsing
├── label_parser.py  # Label and text parsing
├── sheet_parser.py  # Hierarchical sheet parsing
└── registry.py      # Parser registration and dispatch
```

**Benefits**:
- 50+ methods → 5-10 focused classes
- Testable individual parsers
- Extensible for new KiCAD elements

#### 1.3 Extract Parser Registry Pattern
```python
class ElementParserRegistry:
    """Central registry for all S-expression element parsers."""

    def __init__(self):
        self._parsers: Dict[str, IElementParser] = {}

    def register(self, element_type: str, parser: IElementParser):
        self._parsers[element_type] = parser

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        element_type = element[0] if element else None
        parser = self._parsers.get(element_type)
        return parser.parse(element) if parser else None
```

### Phase 2: Collection Architecture (Weeks 3-4)
**Goal**: Eliminate duplicate collection patterns and improve performance

#### 2.1 Abstract Collection Base
```python
# New: kicad_sch_api/collections/base.py
class IndexedCollection(Generic[T]):
    """Base class for all schematic element collections with automatic indexing."""

    def __init__(self):
        self._items: List[T] = []
        self._uuid_index: Dict[str, T] = {}
        self._reference_index: Dict[str, T] = {}  # For components
        self._dirty_indexes = False

    def add(self, item: T) -> T:
        self._items.append(item)
        self._invalidate_indexes()
        return item

    def remove(self, identifier: str) -> bool:
        # Unified removal by UUID or reference
        pass

    def _rebuild_indexes(self):
        """Rebuild all indexes from current items."""
        pass
```

#### 2.2 Specialized Collections
```python
collections/
├── __init__.py
├── base.py           # IndexedCollection base class
├── components.py     # ComponentCollection (extends base)
├── wires.py         # WireCollection (extends base)
├── labels.py        # LabelCollection (extends base)
└── junctions.py     # JunctionCollection (extends base)
```

**Benefits**:
- Eliminates code duplication across collections
- Consistent API for all collection types
- Automatic index management
- Better performance with lazy indexing

### Phase 3: Symbol Resolution (Weeks 5-6)
**Goal**: Single authoritative symbol inheritance and caching

#### 3.1 Extract Symbol Resolver
```python
# New: kicad_sch_api/symbols/resolver.py
class SymbolResolver:
    """Authoritative symbol inheritance and resolution."""

    def __init__(self, cache: ISymbolCache):
        self._cache = cache
        self._inheritance_cache: Dict[str, Dict[str, Any]] = {}

    def resolve_symbol(self, lib_id: str) -> Optional[Dict[str, Any]]:
        """Resolve symbol with full inheritance chain."""
        if lib_id in self._inheritance_cache:
            return self._inheritance_cache[lib_id]

        symbol = self._resolve_with_inheritance(lib_id)
        self._inheritance_cache[lib_id] = symbol
        return symbol

    def _resolve_with_inheritance(self, lib_id: str) -> Dict[str, Any]:
        """Private implementation of inheritance resolution."""
        pass
```

#### 3.2 Refactor Cache Architecture
```python
symbols/
├── __init__.py
├── cache.py         # ISymbolCache implementation
├── resolver.py      # SymbolResolver
├── inheritance.py   # Symbol inheritance logic
└── validators.py    # Symbol validation
```

### Phase 4: Schematic Separation (Weeks 7-8)
**Goal**: Break down the 1,754-line Schematic god class

#### 4.1 Extract Schematic Responsibilities
```python
# Split schematic.py responsibilities:

core/
├── schematic.py          # Core schematic (< 300 LOC)
├── io_manager.py        # File I/O operations
├── validator_manager.py # Validation coordination
└── manipulation/        # Element manipulation
    ├── __init__.py
    ├── wire_operations.py
    ├── component_operations.py
    ├── label_operations.py
    └── sheet_operations.py
```

#### 4.2 Composition Over Inheritance
```python
class Schematic:
    """Streamlined schematic interface."""

    def __init__(self, data: Dict[str, Any]):
        # Composed managers
        self._io = IOManager()
        self._validator = ValidationManager()
        self._wire_ops = WireOperations(self)
        self._component_ops = ComponentOperations(self)

        # Collections
        self.components = ComponentCollection()
        self.wires = WireCollection()
        self.labels = LabelCollection()

    # Delegate to specialized managers
    def save(self, path: Path) -> None:
        self._io.save(self, path)

    def validate(self) -> List[ValidationIssue]:
        return self._validator.validate(self)
```

### Phase 5: Testing Strategy (Weeks 9-10)
**Goal**: Comprehensive test coverage and quality assurance

#### 5.1 Unit Testing Strategy
```python
tests/
├── unit/
│   ├── parsers/          # Individual parser tests
│   ├── collections/      # Collection behavior tests
│   ├── symbols/          # Symbol resolution tests
│   └── validation/       # Validation logic tests
├── integration/
│   ├── round_trip/       # Parse → modify → save → parse
│   ├── file_format/      # Format preservation tests
│   └── performance/      # Large schematic tests
└── fixtures/
    ├── minimal/          # Minimal test cases
    ├── complex/          # Real-world schematics
    └── edge_cases/       # Error conditions
```

#### 5.2 Testing Priorities
1. **Parser Components**: Each parser class individually tested
2. **Symbol Resolution**: Complete inheritance chain testing
3. **Round-trip Validation**: Parse → modify → format → parse consistency
4. **Performance**: Large schematic benchmarks (1000+ components)
5. **Error Handling**: Malformed input graceful handling

### Phase 6: Performance & Polish (Weeks 11-12)
**Goal**: Optimize performance and finalize architecture

#### 6.1 Performance Optimizations
- Lazy loading for symbol cache
- Indexed lookups for collections
- Streaming parser for large files
- Memory optimization for large schematics

#### 6.2 API Polish
- Consistent naming conventions
- Comprehensive documentation
- Type hints throughout
- Error message improvements

## Implementation Guidelines

### Code Quality Standards
- **Maximum class size**: 300 LOC
- **Maximum method complexity**: 7 (cyclomatic)
- **Test coverage**: 80%+ for new code
- **Type hints**: 100% coverage
- **Documentation**: All public APIs

### Dependency Injection Pattern
```python
# Use dependency injection for testability
class SchematicLoader:
    def __init__(
        self,
        parser: IParser,
        validator: IValidator,
        symbol_resolver: ISymbolResolver
    ):
        self._parser = parser
        self._validator = validator
        self._symbol_resolver = symbol_resolver
```

### Error Handling Strategy
```python
# Consistent error handling with context
class SchematicError(Exception):
    """Base exception for schematic operations."""
    def __init__(self, message: str, context: Optional[Dict] = None):
        super().__init__(message)
        self.context = context or {}

class ParseError(SchematicError):
    """Specific parsing errors with line numbers."""
    pass
```

## Migration Strategy

### Backwards Compatibility
- Maintain public API compatibility during refactoring
- Use deprecation warnings for removed features
- Provide migration guide for breaking changes

### Incremental Rollout
1. **Week 1-2**: Internal interfaces and parser registry
2. **Week 3-4**: Collections (maintains external API)
3. **Week 5-6**: Symbol resolver (internal change)
4. **Week 7-8**: Schematic class (careful API preservation)
5. **Week 9-10**: Testing and validation
6. **Week 11-12**: Performance and polish

### Risk Mitigation
- Extensive test suite before any changes
- Feature flags for new implementations
- Parallel implementation during transition
- Comprehensive CI/CD validation

## Success Metrics

### Code Quality Improvements
- **Average class size**: 500+ LOC → <300 LOC
- **Cyclomatic complexity**: 10-15 → 5-7 per method
- **Code duplication**: ~10% → <2%
- **Test coverage**: <30% → 80%+

### Performance Targets
- **Large schematic parsing**: <2s for 1000+ components
- **Memory usage**: 50% reduction for large files
- **Symbol resolution**: <100ms for complex inheritance

### Maintainability Goals
- **New element types**: <1 day to implement
- **Bug isolation**: Clear ownership by module
- **API evolution**: Non-breaking changes supported

## Conclusion

This refactoring plan addresses the core architectural issues while maintaining backwards compatibility and improving testing. The phased approach allows for incremental validation and reduces risk while building a solid foundation for future development.

**Key Benefits**:
- **Maintainability**: Clear separation of concerns and reduced coupling
- **Testability**: Comprehensive test coverage and isolated components
- **Extensibility**: Easy to add new KiCAD elements and features
- **Performance**: Optimized for large schematics and complex operations
- **Quality**: Professional code standards and error handling

**Estimated Timeline**: 12 weeks with 1-2 developers
**Risk Level**: Medium (mitigated by incremental approach and testing)
**Impact**: High (resolves major architectural debt and enables future growth)