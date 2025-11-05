# Connectivity Implementation Plan

## Status: Phase 1 In Progress - 3/80+ scenarios complete ✓

### What We've Accomplished

**✓ W1: Simple Wire Connection (COMPLETE)**
- Created reference schematic with 2 resistors connected by single wire
- Implemented core `ConnectivityAnalyzer` class
- Fixed bug in `pin_utils.py` (SymbolDefinition dataclass access)
- All 14 unit tests passing
- Verified exact KiCAD format compatibility

**✓ J1: T-Junction (COMPLETE)**
- Created reference schematic with 3 resistors meeting at T-junction
- Fixed bug in `connectivity.py` (unhashable Net type in junction merging)
- Junction merging logic verified and working correctly
- All 14 unit tests passing
- Rotated components (90°, 180°) tested successfully

**✓ L1: Label Connections (COMPLETE)**
- Created reference schematic with 2 physically separated wires
- Fixed bug in `connectivity.py` (LabelElement attribute access)
- Label-based net merging working correctly
- All 14 unit tests passing
- Nets correctly named from label text

**Key Insights:**

From W1:
1. Pin position = Component.position + Symbol pin "at" position
2. Pin "length" and "angle" are for visual rendering only
3. Wire endpoints match pin positions exactly (0.000mm distance)
4. Net tracing works by matching wire endpoints to pin positions within tolerance

From J1:
1. Junction merging successfully connects multiple nets into one
2. Rotated components (90°, 180°, 270°) work correctly with pin position calculations
3. Junction point must match wire endpoints within tolerance
4. All three wires meeting at junction correctly merged into single net

From L1:
1. Label-based net merging works perfectly for physically separated wires
2. Matching label names (case-sensitive) connect nets across schematic
3. Net naming prioritizes explicit label text over auto-generated names
4. Labels must be positioned at wire points (within tolerance) to connect
5. LOCAL labels only connect within same schematic sheet

### Implementation Architecture

**New File: `kicad_sch_api/core/connectivity.py`**

Classes:
- `PinConnection`: Represents a component pin with position
- `Net`: Electrical net containing pins, wires, junctions, labels
- `ConnectivityAnalyzer`: Main analysis engine

Key Methods:
- `analyze(schematic)`: Build connectivity graph and return nets
- `are_connected(ref1, pin1, ref2, pin2)`: Check pin connectivity
- `get_net_for_pin(ref, pin)`: Get net for a pin
- `get_connected_pins(ref, pin)`: Get all pins on same net

**Current Capabilities:**
- ✓ Wire-to-pin connections
- ✓ Junction merging (multiple wires at a point)
- ✓ Local label net naming
- ✓ Auto-generated net names
- ⚠️ Global labels (stub implemented, needs testing)
- ✗ Hierarchical labels (not yet implemented)
- ✗ Power symbols (not yet implemented)
- ✗ Bus connections (not yet implemented)

---

## Remaining Test Scenarios

### Phase 1: Wire & Junction Tests (Priority: HIGH)

**Wire Variations:**
- [x] W1: Simple wire between two pins (DONE)
- [ ] W2: Multi-segment wire (3+ points, Manhattan routing)
- [ ] W3: Wire connecting to rotated components (90°, 180°, 270°)
- [ ] W4: Wire with very close but not touching endpoints (tolerance test)

**Junction Tests:**
- [x] J1: T-junction connecting 3 wires (DONE)
- [ ] J2: 4-way junction connecting 4 wires
- [ ] J3: Junction at component pin position
- [ ] J4: Multiple junctions creating network
- [ ] J5: Missing junction at wire crossing (wires overlap but don't connect)

### Phase 2: Label Connection Tests (Priority: HIGH)

**Local Labels:**
- [x] L1: Two wires with same local label (should connect) (DONE)
- [ ] L2: Label at wire endpoint (partially tested in L1)
- [ ] L3: Multiple labels same name on physically connected net
- [ ] L4: Label naming an existing wire net

**Global Labels:**
- [ ] GL1: Two global labels same name connecting separated nets
- [ ] GL2: Global label + local label same name
- [ ] GL3: Multiple global labels creating network

### Phase 3: Complex Scenarios (Priority: MEDIUM)

**Real Circuits:**
- [ ] E15: Voltage divider (R1-R2-GND with junction)
- [ ] E16: RC filter (R-C-GND with junctions)
- [ ] E17: Power distribution (VCC to multiple decoupling caps)
- [ ] E18: Three resistors in series (R1-R2-R3)

**Component Variations:**
- [ ] CP8-CP11: Components at all 4 rotations (0°, 90°, 180°, 270°)
- [ ] CP12: Mirrored components

### Phase 4: Power Symbols (Priority: MEDIUM)

- [ ] PS1: Single GND symbol creating global net
- [ ] PS2: Multiple GND symbols (implicit connection)
- [ ] PS5-PS6: VCC, +5V, +3.3V power symbols
- [ ] PS7: Power symbol + wire connection
- [ ] PS8: Power symbol + label same name

### Phase 5: Hierarchical & Advanced (Priority: LOW)

**Hierarchical Labels:**
- [ ] HL1-HL3: Parent-child sheet connections
- [ ] HL5-HL8: Directional labels (input/output/bidirectional)
- [ ] SP1-SP2: Sheet pin connections

**Bus Connections:**
- [ ] B1-B3: Bus wires and bus entries
- [ ] B4: Bus labels with vector notation
- [ ] B7: Group bus syntax

### Phase 6: Edge Cases & Error Handling (Priority: LOW)

- [ ] E1-E6: Tolerance and positioning edge cases
- [ ] E7-E11: Malformed/invalid cases
- [ ] E13: Net name conflicts
- [ ] E20: Large nets (50+ connections)

---

## Next Steps

### Immediate Priorities:

1. **W2: Multi-segment wire** - Test Manhattan routing
   - Create schematic with 3+ point wire
   - Verify connectivity through middle segments

2. **J1: T-junction** - Test 3-wire junction
   - Critical for real circuits
   - Tests junction merging logic

3. **W3: Rotated components** - Test rotation transformations
   - Verify pin position calculations for all 4 rotations
   - Critical for real-world use

4. **L1: Label connections** - Test label-based net merging
   - Two separate wire segments with same label
   - Should create single net

### Workflow for Each Test:

Using the proven PR #91 workflow:

1. **Claude creates blank/partially populated schematic**
2. **User adds required elements in KiCAD and saves**
3. **Claude analyzes reference format**
4. **Claude creates/updates connectivity logic**
5. **Claude writes unit test**
6. **Iterate until tests pass**

### Test Organization:

```
tests/
├── unit/
│   ├── test_connectivity_w1_simple_wire.py (✓ DONE)
│   ├── test_connectivity_w2_multi_segment.py
│   ├── test_connectivity_w3_rotated.py
│   ├── test_connectivity_j1_t_junction.py
│   ├── test_connectivity_l1_label_connection.py
│   └── ...
├── reference_kicad_projects/
│   └── connectivity/
│       ├── w1_simple_wire/ (✓ DONE)
│       ├── w2_multi_segment/
│       ├── w3_rotated/
│       └── ...
```

---

## API Integration Plan

### Integration Points:

1. **Schematic class**: Add `analyze_connectivity()` method
   ```python
   sch.analyze_connectivity() -> ConnectivityAnalyzer
   ```

2. **WireManager**: Update `are_pins_connected()` to use new analyzer
   ```python
   # Old: Only checks direct wires
   # New: Uses full connectivity tracing
   ```

3. **Validation**: Enable ERC checks
   ```python
   # _build_nets() in PinTypeValidator
   # _count_connections_at_point() in ConnectivityValidator
   ```

4. **NetCollection**: Auto-populate from connectivity
   ```python
   sch.nets  # Auto-populated from connectivity analysis
   ```

### Backward Compatibility:

- Keep old `are_pins_connected()` behavior as `are_pins_directly_connected()`
- New `are_pins_connected()` uses full net tracing
- Document breaking change

---

## Testing Metrics

**Current Coverage:**
- Test Scenarios Implemented: 3 / 80+ (3.75%)
- Unit Tests Passing: 42 / 42 (100%)
- Core Functionality:
  - Wire-to-pin connections ✓
  - Junction merging ✓
  - Rotated components (90°, 180°) ✓
  - Local label connections ✓
  - Net naming from labels ✓

**Target Coverage:**
- Phase 1+2 (Wire/Junction/Labels): ~25 scenarios
- Phase 3 (Complex circuits): ~10 scenarios
- Phase 4 (Power): ~10 scenarios
- Phase 5 (Hierarchical/Bus): ~15 scenarios
- Phase 6 (Edge cases): ~10 scenarios

**Success Criteria:**
- All Phase 1+2 tests passing (essential functionality)
- 90%+ of real-world circuits handled correctly
- Integration with ERC validation
- Performance acceptable for 1000+ component schematics

---

## Performance Considerations

**Current Implementation:**
- O(n*m) where n=wires, m=pins
- Acceptable for <1000 components
- No caching or indexing optimizations yet

**Future Optimizations:**
- Spatial indexing (quadtree) for pin/wire lookup
- Cache connectivity analysis results
- Incremental updates when schematic changes
- Lazy evaluation of nets

---

## Documentation TODO

- [ ] API documentation for ConnectivityAnalyzer
- [ ] User guide with examples
- [ ] Migration guide from old are_pins_connected()
- [ ] Performance best practices
- [ ] Integration examples with ERC

---

## Issues to Address

1. **Pin position calculation bug** - FIXED
   - SymbolDefinition dataclass `.get()` error
   - Fixed in `pin_utils.py`

2. **Net name generation**
   - Currently: `Net-(R1-Pad2)`
   - Consider: More intelligent naming from labels/power symbols

3. **Tolerance handling**
   - Default 0.01mm might be too tight for some schematics
   - Consider making it configurable globally

4. **Performance with large nets**
   - Not yet tested with 50+ connections
   - May need optimization

---

**Last Updated:** 2025-11-04
**Status:** Phase 1 partially complete, ready for next scenarios
