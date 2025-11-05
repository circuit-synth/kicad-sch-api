# Implementation Plan: Issue #79 - Comprehensive Unit Tests

## Overview
Add comprehensive unit test coverage for all schematic object types to ensure API correctness, prevent regressions, and document usage patterns.

## Current Status Analysis

### ✅ Existing Tests
- Component creation and properties
- Component rotation (11 unit tests + 8 reference tests)
- Wire creation (basic)
- Geometry and positioning
- Grid snapping
- Pin positioning (with rotation)
- CLI integration (ERC, netlist, BOM)
- Hierarchical instances
- Exception handling
- Text box escaping

### ❌ Missing Tests (from Issue #79)

#### HIGH PRIORITY (Most commonly used)
1. **Labels (local)** - `sch.add_label()`
2. **Global labels** - `sch.add_global_label()`
3. **Hierarchical labels** - `sch.add_hierarchical_label()`
4. **Power symbols** - Component with power flag
5. **Hierarchical sheets** - `sch.add_sheet()`
6. **Sheet pins** - `sch.add_sheet_pin()`

#### MEDIUM PRIORITY (Frequently needed)
7. **NoConnect markers** - `sch.no_connects.add()`
8. **Junctions** - `sch.junctions.add()`
9. **Text elements** - `sch.add_text()`
10. **Text boxes** - `sch.add_text_box()`
11. **Rectangles** - `sch.add_rectangle()`

#### LOW PRIORITY (Less common)
12. **Bus connections** - Not yet implemented in API
13. **Bus entries** - Not yet implemented in API
14. **Multi-unit components** - Use unit parameter
15. **Images** - `sch.add_image()`
16. **Wire to pin** - `sch.add_wire_to_pin()`
17. **Wire between pins** - `sch.add_wire_between_pins()`

## Implementation Strategy

### Phase 1: High Priority Items (Week 1)
Start with most commonly used elements. Use the proven "Interactive Reference Strategy":

1. **Labels (Local)** - `tests/unit/test_label.py` + `test_label_rotation.py`
   - Basic functionality:
     - Create blank schematic
     - User adds label in KiCad
     - Analyze KiCad format
     - Write tests + reference tests
     - Reference: `tests/reference_kicad_projects/label/`
   - Rotation testing (⚠️ CRITICAL):
     - Create 4 blank schematics
     - User adds label at 0°, 90°, 180°, 270° (one per schematic)
     - Analyze S-expression format for each rotation
     - Verify rotation parameter exists and format
     - Write rotation tests
     - References: `label_rotated_0deg/`, `label_rotated_90deg/`, etc.

2. **Junctions** - `tests/unit/test_junction.py`
   - Simple element, quick win
   - NO rotation testing (not rotatable)
   - Reference: `tests/reference_kicad_projects/junction/`

3. **NoConnect** - `tests/unit/test_no_connect.py`
   - Simple element, quick win
   - NO rotation testing (not rotatable)
   - Reference: `tests/reference_kicad_projects/no_connect/`

4. **Global Labels** - `tests/unit/test_global_label.py` + rotation tests
   - Same strategy as local labels (with rotation)
   - Reference: `tests/reference_kicad_projects/global_label/` + rotation refs

5. **Hierarchical Labels** - `tests/unit/test_hierarchical_label.py` + rotation tests
   - Same strategy (with rotation)
   - Reference: `tests/reference_kicad_projects/hierarchical_label/` + rotation refs

### Phase 2: Medium Priority Items (Week 2)
6. **Text** - `tests/unit/test_text.py`
7. **Text Box** - `tests/unit/test_text_box.py`
8. **Hierarchical Sheet** - `tests/unit/test_sheet.py`
9. **Sheet Pin** - `tests/unit/test_sheet_pin.py`
10. **Rectangle** - `tests/unit/test_rectangle.py`

### Phase 3: Advanced Items (Week 3+)
11. **Power Symbols** - Special component type
12. **Multi-unit Components** - Complex components
13. **Wire connections** - Advanced wiring
14. **Images** - Graphics

## Testing Pattern (from Pin Rotation Success)

### For Each Object Type:

#### 1. Reference Schematic Creation
```bash
# Claude creates blank schematic
uv run python /tmp/create_blank.py

# Opens in KiCad for user to edit
open path/to/schematic.kicad_sch
```

#### 2. User Manual Editing
- User adds the element manually in KiCad
- Save schematic
- Notify Claude it's ready

#### 3. Claude Analysis
```python
# Read the KiCad schematic
sch = ksa.Schematic.load("reference.kicad_sch")

# Extract exact format
# - Position
# - Properties
# - S-expression structure
# - All attributes
```

#### 4. Unit Test Creation
```python
class TestLabel:
    def test_label_creation(self, schematic):
        """Test creating a local label."""
        label = schematic.add_label("DATA", position=(100, 100))
        assert label.text == "DATA"
        assert label.position.x == 100

    def test_label_reference_format(self):
        """Test against manually created KiCad reference."""
        sch = ksa.Schematic.load("tests/reference_kicad_projects/label/label.kicad_sch")
        # Verify exact format matches
```

#### 5. Reference Test Creation
```python
class TestLabelReference:
    def test_label_matches_kicad(self):
        """Verify our API generates exact KiCad format."""
        # Load reference
        # Create programmatically
        # Compare outputs
```

## Test Coverage Requirements

For each object type, test:
1. ✅ **Creation** - Object instantiation with valid parameters
2. ✅ **Properties** - Getting/setting all properties
3. ✅ **Validation** - Required field enforcement
4. ✅ **Position** - Correct positioning and grid snapping
5. ✅ **Rotation** - Test all valid rotations (0°, 90°, 180°, 270°) **CRITICAL!**
   - **Don't assume rotation works like components!**
   - Each element type may have different S-expression format for rotation
   - Create manual KiCad references for each rotation angle
   - Verify exact S-expression matches KiCad output
6. ✅ **Format** - S-expression output matches KiCad exactly
7. ✅ **Load/Save** - Round-trip preservation
8. ✅ **Edge Cases** - Empty values, special characters, etc.

### Rotation Testing Strategy ⚠️
**IMPORTANT**: Do NOT assume rotation works the same for all element types!

For each rotatable element (labels, text, text boxes, etc.):
1. Create 4 reference schematics (one per rotation: 0°, 90°, 180°, 270°)
2. Manually rotate element in KiCad for each reference
3. Analyze exact S-expression format for each rotation
4. Implement rotation support if not already present
5. Test that our API generates identical S-expressions

**Which elements can be rotated?**
- Labels (local, global, hierarchical) - YES, can be rotated
- Text - YES, can be rotated
- Text boxes - YES, can be rotated
- Junctions - NO rotation (just a dot)
- NoConnect - NO rotation (just an X marker)
- Sheets - Possibly? Need to verify
- Rectangles - Possibly? Need to verify

## Directory Structure

```
tests/
├── unit/
│   ├── test_label.py                    # NEW - includes rotation tests
│   ├── test_label_rotation.py           # NEW - dedicated rotation tests
│   ├── test_global_label.py             # NEW - includes rotation tests
│   ├── test_global_label_rotation.py    # NEW - dedicated rotation tests
│   ├── test_hierarchical_label.py       # NEW - includes rotation tests
│   ├── test_junction.py                 # NEW - no rotation (not rotatable)
│   ├── test_no_connect.py               # NEW - no rotation (not rotatable)
│   ├── test_text.py                     # NEW - includes rotation tests
│   ├── test_text_rotation.py            # NEW - dedicated rotation tests
│   ├── test_text_box.py                 # NEW - includes rotation tests
│   ├── test_sheet.py                    # NEW - verify rotatability
│   ├── test_sheet_pin.py                # NEW
│   ├── test_rectangle.py                # NEW - verify rotatability
│   └── ...
│
├── reference_tests/
│   ├── test_label_reference.py          # NEW - basic functionality
│   ├── test_label_rotation_reference.py # NEW - rotation verification
│   ├── test_global_label_reference.py   # NEW
│   ├── test_junction_reference.py       # NEW
│   └── ...
│
└── reference_kicad_projects/
    ├── label/                           # NEW - basic label
    │   └── label.kicad_sch
    ├── label_rotated_0deg/              # NEW - rotation references
    │   └── label_rotated_0deg.kicad_sch
    ├── label_rotated_90deg/             # NEW
    │   └── label_rotated_90deg.kicad_sch
    ├── label_rotated_180deg/            # NEW
    │   └── label_rotated_180deg.kicad_sch
    ├── label_rotated_270deg/            # NEW
    │   └── label_rotated_270deg.kicad_sch
    ├── global_label/                    # NEW
    │   └── global_label.kicad_sch
    ├── global_label_rotated_0deg/       # NEW - rotation references
    │   └── global_label_rotated_0deg.kicad_sch
    ├── global_label_rotated_90deg/      # NEW
    │   └── global_label_rotated_90deg.kicad_sch
    ├── hierarchical_label/              # NEW
    │   └── hierarchical_label.kicad_sch
    ├── junction/                        # NEW - no rotation tests needed
    │   └── junction.kicad_sch
    ├── no_connect/                      # NEW - no rotation tests needed
    │   └── no_connect.kicad_sch
    └── ...
```

**Note**: For rotatable elements, we create 4 rotation references (just like we did for components).
This ensures we verify exact S-expression format for each rotation angle.

## Success Metrics

- [ ] 100% API coverage for add_* methods
- [ ] All schematic object types have unit tests
- [ ] All high-priority items have reference tests
- [ ] Each test validates exact KiCad format
- [ ] No regressions in existing functionality
- [ ] Documentation updated with examples

## Immediate Next Steps

1. ✅ Create this plan
2. ⏭️ Update CLAUDE.md with enhanced testing strategy
3. ⏭️ Start with **Labels** (most common, foundational)
4. ⏭️ Create blank label schematic
5. ⏭️ User adds label in KiCad
6. ⏭️ Analyze and implement tests

## Estimated Effort

### With Rotation Testing:
- **Phase 1** (High Priority): 3-4 days (5 object types × 2 test types)
  - Labels (basic + rotation): ~6 hours
  - Junctions (basic only): ~2 hours
  - NoConnect (basic only): ~2 hours
  - Global Labels (basic + rotation): ~4 hours
  - Hierarchical Labels (basic + rotation): ~4 hours

- **Phase 2** (Medium Priority): 3-4 days (5 object types)
  - Text (basic + rotation): ~4 hours
  - Text Box (basic + rotation): ~4 hours
  - Sheets (basic + verify rotation): ~4 hours
  - Sheet Pins: ~3 hours
  - Rectangles (basic + verify rotation): ~3 hours

- **Phase 3** (Advanced): 3-4 days (4+ object types)

**Total**: ~2.5-3 weeks for comprehensive coverage with rotation tests

### Effort Breakdown Per Element:
- **Rotatable elements** (labels, text, text boxes): ~4-6 hours each
  - Basic tests: 1-2 hours
  - 4 rotation references: 2 hours
  - Rotation tests: 1-2 hours
- **Non-rotatable elements** (junction, no-connect): ~2-3 hours each
  - Basic tests: 1-2 hours
  - 1 reference: 1 hour

## Notes

- Use **Interactive Reference Strategy** proven with pin rotation
- Each object type: ~2-4 hours (reference creation + tests)
- Parallelize where possible (multiple object types per day)
- Prioritize quality over speed - exact format matching is critical
