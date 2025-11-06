# Pin Connection Architecture - Dependency Diagrams and Flow

## 1. Dependency Graph

### 1.1 Module Dependency Tree (Bottom-Up)

```
EXTERNAL DEPENDENCIES
  │
  ├─ sexpdata (for parsing)
  └─ typing (Python stdlib)

FOUNDATION LAYER
  │
  ├─ core/types.py (Point, Wire, Junction, etc.)
  │   └─ No internal dependencies (only stdlib)
  │
  ├─ core/exceptions.py
  │   └─ core/types.py
  │
  └─ core/geometry.py
      └─ core/types.py

LIBRARY LAYER
  │
  ├─ library/cache.py (SymbolDefinition, symbol_cache)
  │   ├─ core/types.py
  │   └─ utils/validation.py
  │
  └─ core/pin_utils.py (list_component_pins, get_component_pin_position)
      ├─ core/types.py
      ├─ core/geometry.py
      └─ library/cache.py

COLLECTION LAYER
  │
  ├─ collections/base.py
  ├─ collections/components.py
  ├─ collections/wires.py
  └─ collections/junctions.py

PIN DISCOVERY LAYER (Track A)
  │
  ├─ pins/errors.py
  │   └─ core/exceptions.py
  │
  ├─ pins/models.py
  │   └─ core/types.py (Point, SchematicPin)
  │
  └─ pins/discovery.py ⭐ PRIMARY SERVICE
      ├─ pins/models.py
      ├─ pins/errors.py
      ├─ library/cache.py
      ├─ core/pin_utils.py
      ├─ core/geometry.py
      └─ core/types.py

ROUTING LAYER (Track B)
  │
  ├─ routing/errors.py
  │   └─ core/exceptions.py
  │
  ├─ routing/models.py
  │   ├─ core/types.py
  │   └─ enum (Python stdlib)
  │
  ├─ routing/grid.py
  │   └─ core/types.py
  │
  ├─ routing/junction_detector.py
  │   ├─ core/types.py
  │   ├─ core/geometry.py
  │   ├─ routing/models.py
  │   └─ logging (stdlib)
  │
  └─ routing/router.py ⭐ PRIMARY SERVICE
      ├─ routing/models.py
      ├─ routing/errors.py
      ├─ routing/grid.py
      ├─ routing/junction_detector.py
      ├─ pins/discovery.py
      ├─ core/types.py
      └─ logging (stdlib)

SCHEMATIC INTEGRATION LAYER
  │
  ├─ core/schematic.py (Schematic class)
  │   ├─ collections/ (all)
  │   ├─ core/types.py
  │   ├─ core/exceptions.py
  │   ├─ library/cache.py
  │   ├─ core/parser.py
  │   ├─ core/formatter.py
  │   │
  │   ├─ pins/discovery.py (lazy import)
  │   ├─ routing/router.py (lazy import)
  │   └─ routing/models.py (lazy import)

TEST INFRASTRUCTURE LAYER (Track C)
  │
  ├─ tests/conftest.py
  │   ├─ pytest (external)
  │   ├─ kicad_sch_api (all public API)
  │   └─ tempfile (stdlib)
  │
  ├─ tests/helpers.py
  │   ├─ kicad_sch_api (public API)
  │   └─ core/types.py
  │
  └─ tests/unit/ and tests/reference_tests/
      ├─ pytest
      ├─ conftest (fixtures)
      ├─ helpers (utilities)
      └─ kicad_sch_api (classes under test)
```

### 1.2 Critical Dependency Points

**No Circular Dependencies:**
```
pins/discovery.py  ╔════════╗
                   ║ Does   ║
routing/router.py  ║  NOT   ║  pins/models.py
                   ║ Have   ║
core/schematic.py  ╚════════╝  routing/models.py

All dependencies flow downward only
```

**Lazy Loading Points (avoid circular imports):**
```python
# In core/schematic.py:
def __init__(self, ...):
    self._pin_discovery = None  # Not initialized yet
    self._wire_router = None    # Not initialized yet

@property
def pin_discovery(self):
    if self._pin_discovery is None:
        from ..pins import PinDiscovery  # Import here, not at module level
        self._pin_discovery = PinDiscovery(self)
    return self._pin_discovery

@property
def wire_router(self):
    if self._wire_router is None:
        from ..routing import WireRouter  # Import here, not at module level
        self._wire_router = WireRouter(self, self.pin_discovery)
    return self._wire_router
```

---

## 2. Data Flow Diagrams

### 2.1 Pin Discovery Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CODE / APPLICATION                       │
│                                                                   │
│  sch = ksa.load_schematic("circuit.kicad_sch")                  │
│  pins = sch.get_component_pins("U1")  # or                       │
│  pins = sch.pin_discovery.get_pins_info("U1")                   │
└──────────────────────────────────────────┬──────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│          PinDiscovery.get_pins_info(component_ref)              │
│                                                                   │
│  1. Check cache: component_ref in _component_pins_cache?        │
│     YES → return cached ComponentPins ──────────────────┐       │
│     NO  → continue                                      │       │
│                                                         │       │
│  2. Get component from schematic                        │       │
│     component = schematic.components.get(ref)          │       │
│                                                         │       │
│  3. Get pin positions from component                    │       │
│     pin_positions = list_component_pins(component)     │       │
│     ↓                                                   │       │
│     ┌──────────────────────────────────────┐           │       │
│     │ core/pin_utils.py                    │           │       │
│     │ Returns: [(pin_number, Point), ...]  │           │       │
│     │ Applies: rotation, mirroring,        │           │       │
│     │          component position          │           │       │
│     └──────────────────────────────────────┘           │       │
│                                                         │       │
│  4. Get symbol definition                              │       │
│     symbol_def = symbol_cache.get_symbol(lib_id)      │       │
│     ↓                                                   │       │
│     ┌──────────────────────────────────────┐           │       │
│     │ library/cache.py                     │           │       │
│     │ Returns: SymbolDefinition            │           │       │
│     │ Contains: pins[], pin types, names   │           │       │
│     └──────────────────────────────────────┘           │       │
│                                                         │       │
│  5. Enhance pin info with symbol data                  │       │
│     FOR each pin_number, position:                     │       │
│       - Find matching symbol pin definition            │       │
│       - Extract pin type, shape, name                  │       │
│       - Find connected wires                           │       │
│       - Create PinInfo instance                        │       │
│       - Index by number and name                       │       │
│                                                         │       │
│  6. Create ComponentPins result                        │       │
│     result = ComponentPins(                            │       │
│         pins_by_number={...},                          │       │
│         pins_by_name={...}                             │       │
│     )                                                   │       │
│                                                         │       │
│  7. Cache result                                       │       │
│     _component_pins_cache[component_ref] = result      │       │
└──────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────┐
                        │ RETURN ComponentPins         │
                        │ ├─ pins_by_number           │
                        │ ├─ pins_by_name             │
                        │ └─ get_pin() method         │
                        └─────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER CODE (continued)                         │
│                                                                   │
│  pin_1 = pins.get_pin("1")                                       │
│  # PinInfo: reference, pin_number, position, pin_type, etc.    │
│                                                                   │
│  pin_by_name = pins.get_pin("GND")                              │
│  # Also works for named pins                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Wire Routing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER CODE / APPLICATION                       │
│                                                                   │
│  sch.connect_pins("R1", "2", "R2", "1")  # or                  │
│  result = sch.wire_router.connect_pins(                         │
│      from_component="R1",                                       │
│      from_pin="2",                                              │
│      to_component="R2",                                         │
│      to_pin="1"                                                 │
│  )                                                              │
└──────────────────────────────────────────┬──────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│          WireRouter.connect_pins() PRIMARY METHOD               │
│                                                                   │
│  STEP 1: Resolve source pin                                     │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ from_pin_result = pin_discovery.match_pin(          │       │
│  │     "R1", "2"                                       │       │
│  │ )                                                   │       │
│  │ Returns: PinMatchResult(found, pin_info, ...)      │       │
│  │ ↓                                                   │       │
│  │ if not from_pin_result.found:                       │       │
│  │   return ConnectionResult(success=False, ...)      │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                   │
│  STEP 2: Resolve destination pin                                │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ to_pin_result = pin_discovery.match_pin(           │       │
│  │     "R2", "1"                                       │       │
│  │ )                                                   │       │
│  │ (same validation as step 1)                         │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                   │
│  STEP 3: Calculate routing path                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ path = _calculate_path(                              │      │
│  │     from_pin_info.position,                          │      │
│  │     to_pin_info.position,                            │      │
│  │     options                                          │      │
│  │ )                                                    │      │
│  │                                                      │      │
│  │ _calculate_path():                                   │      │
│  │  - Snap to grid (GridSnapping)                      │      │
│  │  - Select algorithm (Manhattan, Direct, etc)        │      │
│  │  - Return RoutingPath(start, end, waypoints)        │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
│  STEP 4: Create wire in schematic                               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ wire_uuid = schematic.wires.add(                     │      │
│  │     points=path.all_points(),                        │      │
│  │     wire_type=WireType.WIRE                          │      │
│  │ )                                                    │      │
│  │                                                      │      │
│  │ WireCollection.add():                               │      │
│  │  - Create Wire object                               │      │
│  │  - Validate points                                  │      │
│  │  - Add to collection                                │      │
│  │  - Return UUID                                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
│  STEP 5: Detect and create junctions                            │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ if options.auto_create_junctions:                   │      │
│  │                                                      │      │
│  │   junctions = junction_detector.                    │      │
│  │       detect_required_junctions(path)               │      │
│  │                                                      │      │
│  │   JunctionDetector.detect_required_junctions():     │      │
│  │    - For each existing wire:                        │      │
│  │      • Find crossing points with new wire           │      │
│  │      • Exclude endpoints                            │      │
│  │      • Check if junction already exists             │      │
│  │    - Return list of Point objects                   │      │
│  │                                                      │      │
│  │   FOR each junction_point:                          │      │
│  │     junc_uuid = schematic.junctions.add(            │      │
│  │         position=junction_point                     │      │
│  │     )                                                │      │
│  │     junction_uuids.append(junc_uuid)                │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                   │
│  STEP 6: Return result                                          │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ return ConnectionResult(                             │      │
│  │     success=True,                                    │      │
│  │     wire_uuid=wire_uuid,                             │      │
│  │     junctions_created=junction_uuids,                │      │
│  │     path=path,                                       │      │
│  │     ...                                              │      │
│  │ )                                                    │      │
│  └──────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER CODE (continued)                         │
│                                                                   │
│  if result.success:                                              │
│    print(f"Connected {result.wire_uuid}")                        │
│    for junc in result.junctions_created:                         │
│      print(f"  Junction: {junc}")                                │
│  else:                                                            │
│    print(f"Failed: {result.error_message}")                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Junction Detection Detailed Flow

```
┌────────────────────────────────────────────────────────────────┐
│  JunctionDetector.detect_required_junctions(path)              │
│                                                                 │
│  INPUT: RoutingPath with start, end, waypoints               │
│                                                                 │
│  ALGORITHM:                                                     │
│  1. Get all path segments (points connected by lines)          │
│     all_points = [start] + waypoints + [end]                  │
│     segments = [(p[i], p[i+1]) for i in range(n-1)]           │
│                                                                 │
│  2. FOR each existing wire in schematic.wires:                │
│     ├─ FOR each segment of new path:                           │
│     │  ├─ Find intersections with existing wire               │
│     │  │  └─ _find_segment_intersections(new_seg, wire)       │
│     │  │     ├─ FOR each segment of existing wire:            │
│     │  │     │  └─ Calculate intersection point               │
│     │  │     │     └─ _line_segment_intersection()            │
│     │  │     │        Uses parametric line equations          │
│     │  │     └─ Return list of intersection Points            │
│     │  │                                                        │
│     │  └─ Filter out endpoints:                                │
│     │     ├─ is_new_endpoint? (< tolerance from segment end)  │
│     │     ├─ is_existing_endpoint? (< tolerance from wire end)│
│     │     └─ If either: skip (don't create junction)          │
│     │                                                          │
│     └─ Add valid crossings to result list                      │
│                                                                 │
│  3. Remove duplicates (within tolerance)                       │
│                                                                 │
│  OUTPUT: List[Point] where junctions should be created        │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Service Interaction Matrix

```
                    │ Requires    │ Provides   │ Used By
────────────────────┼─────────────┼────────────┼──────────────────
PinDiscovery        │ symbol_cache│ PinInfo    │ WireRouter
                    │ pin_utils   │ ComponentP │ Schematic
                    │ geometry    │ PinMatchRe │ Tests
────────────────────┼─────────────┼────────────┼──────────────────
WireRouter          │ PinDiscovery│ Connection │ Schematic
                    │ JunctionDet │ Result     │ User code
                    │ GridSnapping│            │ Tests
────────────────────┼─────────────┼────────────┼──────────────────
JunctionDetector    │ geometry    │ List[Point]│ WireRouter
                    │ core/types  │ (junction  │
                    │             │ positions) │
────────────────────┼─────────────┼────────────┼──────────────────
GridSnapping        │ core/types  │ Point      │ WireRouter
                    │             │ (snapped)  │ Tests
────────────────────┼─────────────┼────────────┼──────────────────
Schematic           │ All above   │ Properties │ User code
                    │ (lazy init) │ & methods  │
────────────────────┼─────────────┼────────────┼──────────────────
Tests               │ All services│ Test       │ CI/CD
                    │ fixtures    │ results    │
```

---

## 4. Call Stack Examples

### 4.1 Complete Pin Discovery Call Stack

```
main()
├─ sch = ksa.load_schematic("circuit.kicad_sch")
│  └─ Schematic.load() → parsed + populated ✓
│
├─ pins = sch.get_component_pins("U1")
│  └─ Schematic.get_component_pins(ref)
│     └─ PinDiscovery.get_pins_info(ref)
│        ├─ Check cache
│        ├─ Get component: ComponentCollection.get(ref)
│        ├─ list_component_pins(component)
│        │  ├─ For each pin in component.pins:
│        │  │  └─ apply_transformation(pin.pos, component)
│        │  │     └─ core/geometry.apply_transformation()
│        │  │        └─ negate Y, apply rotation/mirror
│        │  └─ Return [(pin_num, Point), ...]
│        ├─ Get symbol: SymbolCache.get_symbol(lib_id)
│        │  └─ library/cache.py: load/parse library file
│        ├─ For each pin:
│        │  ├─ Find symbol pin definition
│        │  ├─ Parse pin type/shape
│        │  ├─ Find connected wires
│        │  └─ Create PinInfo
│        ├─ Create ComponentPins with indices
│        ├─ Cache result
│        └─ Return ComponentPins ✓
│
└─ pin_1 = pins.get_pin("1")
   └─ ComponentPins.get_pin(identifier)
      └─ Return PinInfo (from pins_by_number or pins_by_name) ✓
```

### 4.2 Complete Wire Routing Call Stack

```
main()
├─ result = sch.connect_pins("R1", "2", "R2", "1")
│  └─ Schematic.connect_pins()
│     └─ WireRouter.connect_pins(from_comp, from_pin, to_comp, to_pin)
│        ├─ PinDiscovery.match_pin("R1", "2")
│        │  └─ PinDiscovery.get_pins_info("R1")
│        │     [call stack as in section 4.1]
│        │  └─ Return PinMatchResult(found=True, pin_info=...) ✓
│        │
│        ├─ PinDiscovery.match_pin("R2", "1")
│        │  └─ [same as above] ✓
│        │
│        ├─ _calculate_path(start_pos, end_pos, options)
│        │  ├─ GridSnapping.snap(start_pos)
│        │  │  └─ Round to grid_size
│        │  ├─ GridSnapping.snap(end_pos)
│        │  │  └─ Round to grid_size
│        │  ├─ Select routing algorithm
│        │  └─ _route_manhattan(start, end)
│        │     └─ Create waypoint for L-shape
│        │        └─ Return RoutingPath ✓
│        │
│        ├─ SchematicWires.add(points=[...])
│        │  ├─ Create Wire object
│        │  ├─ Validate points
│        │  ├─ Add to _items and _uuid_index
│        │  └─ Return wire_uuid ✓
│        │
│        ├─ JunctionDetector.detect_required_junctions(path)
│        │  ├─ Get path segments
│        │  ├─ For each existing wire:
│        │  │  ├─ _find_segment_intersections()
│        │  │  │  └─ For each existing segment:
│        │  │  │     └─ _line_segment_intersection()
│        │  │  │        └─ Solve parametric equations
│        │  │  │           └─ Return Point or None
│        │  │  └─ Filter out endpoints
│        │  └─ Return [Point, ...] (junction positions) ✓
│        │
│        ├─ For each junction point:
│        │  └─ SchematicJunctions.add(position)
│        │     ├─ Create Junction object
│        │     ├─ Add to collection
│        │     └─ Return junc_uuid ✓
│        │
│        └─ Return ConnectionResult(
│             success=True,
│             wire_uuid=...,
│             junctions_created=[...],
│             path=...
│           ) ✓
│
└─ if result.success:
   └─ print(f"Wire {result.wire_uuid}, Junctions {result.junctions_created}") ✓
```

---

## 5. Memory and Performance Characteristics

### 5.1 Caching Strategy

```
┌──────────────────────────────────────────────────────────────┐
│ Cache Layer 1: Symbol Library Cache (library/cache.py)      │
│                                                              │
│ Key: lib_id (e.g., "Device:R")                              │
│ Value: SymbolDefinition                                      │
│ Lifetime: Application lifetime (shared across schematics)   │
│ Strategy: LRU with access_count tracking                     │
│ Hit Rate Expected: 90%+ (components reuse same symbols)     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Cache Layer 2: Component Pins Cache (pins/discovery.py)     │
│                                                              │
│ Key: component_reference (e.g., "R1", "U1")                 │
│ Value: ComponentPins (pins indexed by number and name)       │
│ Lifetime: Per schematic (reset on load)                      │
│ Strategy: Lazy initialization, cleared on schematic reset    │
│ Hit Rate Expected: 70%+ (repeated pin queries)              │
└──────────────────────────────────────────────────────────────┘

Cache Invalidation:
─────────────────
- Component added/removed → invalidate affected entries
- Component repositioned → ✓ (positions still correct)
- Component rotated → ✓ (positions still correct)
- Wire added/removed → invalidate connected_wires field
- Label added/removed → invalidate connected_label field
```

### 5.2 Performance Metrics

```
TYPICAL OPERATION TIMES (rough estimates)

Operation                          Time        Notes
────────────────────────────────────────────────────────────
Load symbol library (once)        100-500ms   Cached by library module
Get pins for component (cached)   <1ms        Hash lookup
Get pins for component (uncached) 10-50ms     Symbol lookup + processing
Find pin by position              5-20ms      O(n*m) where n=components, m=pins
Route wire (Manhattan)            2-10ms      Simple geometry
Detect junctions (no crossings)   5-20ms      O(n) where n=existing wires
Detect junctions (many crossings) 50-200ms    O(n*m) for each crossing calc

MEMORY USAGE (rough estimates)

Structure                 Size per item    Notes
────────────────────────────────────────────────────────────
PinInfo                  ~500 bytes       Includes position, type, name
ComponentPins            ~2KB             For 20-pin IC
SymbolDefinition         ~10KB            Includes graphics + pins
Routing cache            ~1KB             Per active routing operation
```

---

## 6. Error Flow Diagrams

### 6.1 Pin Discovery Error Handling

```
get_pins_info(component_ref)
│
├─ Component not found
│  └─ PinNotFoundError
│     → Caller handles: suggest checking reference spelling
│
├─ Symbol library not found
│  └─ SymbolLibraryError
│     → Caller handles: check library installation
│
├─ Symbol parsing error
│  └─ SymbolLibraryError
│     → Caller handles: check library file integrity
│
└─ SUCCESS
   └─ Return ComponentPins
      ├─ All pins found
      ├─ Positions calculated correctly
      └─ Types and names populated
```

### 6.2 Wire Routing Error Handling

```
connect_pins(from_comp, from_pin, to_comp, to_pin)
│
├─ Source pin not found
│  └─ ConnectionResult(success=False)
│     error_message: "Cannot find source pin: ..."
│     from_pin_result.candidates: [alternative pins]
│
├─ Destination pin not found
│  └─ ConnectionResult(success=False)
│     error_message: "Cannot find destination pin: ..."
│     to_pin_result.candidates: [alternative pins]
│
├─ Wire creation fails
│  └─ ConnectionResult(success=False)
│     error_message: "Failed to create wire: ..."
│
├─ Junction creation warnings (non-fatal)
│  └─ ConnectionResult(success=True)
│     warnings: ["Failed to create junctions: ..."]
│
└─ SUCCESS
   └─ ConnectionResult(
        success=True,
        wire_uuid: "...",
        junctions_created: [...],
        algorithm_used: MANHATTAN,
        path: RoutingPath(...)
      )
```

---

## 7. Integration Checklist

**Pre-implementation:**
- [ ] Review this design document with team
- [ ] Confirm module locations and naming
- [ ] Identify any additional dependencies
- [ ] Plan testing strategy

**Core Implementation:**
- [ ] Implement pins/models.py
- [ ] Implement routing/models.py
- [ ] Implement pins/discovery.py
- [ ] Implement routing/junction_detector.py
- [ ] Implement routing/grid.py
- [ ] Implement routing/router.py

**Integration:**
- [ ] Update core/schematic.py with lazy-initialized properties
- [ ] Create pins/__init__.py and routing/__init__.py
- [ ] Update main package __init__.py exports

**Testing:**
- [ ] Create tests/conftest.py with fixtures
- [ ] Create tests/helpers.py with utilities
- [ ] Write unit tests for each service
- [ ] Create reference test schematics
- [ ] Write reference tests
- [ ] Write integration tests

**Documentation:**
- [ ] Update CLAUDE.md with pin connection examples
- [ ] Create usage examples in examples/
- [ ] Add docstrings to all public methods

---

## 8. Summary Table

| Aspect | Details |
|--------|---------|
| **Modules** | 8 new modules (pins/, routing/) + tests/ |
| **Services** | 2 primary (PinDiscovery, WireRouter) + 2 support (JunctionDetector, GridSnapping) |
| **Data Classes** | 10+ dataclasses (PinInfo, ComponentPins, ConnectionResult, etc.) |
| **Dependencies** | No circular dependencies, lazy initialization |
| **Caching** | 2-level caching (symbol library, component pins) |
| **Test Fixtures** | 7 main fixtures + parametrized variants |
| **Algorithms** | Manhattan routing, line intersection, grid snapping |
| **Error Handling** | 8+ specific exception types with diagnostics |
| **Performance** | <50ms for typical operations, <1ms for cached lookups |

