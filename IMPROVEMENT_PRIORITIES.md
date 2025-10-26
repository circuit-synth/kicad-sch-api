# Improvement Priorities Quick Reference

**Last Updated:** 2025-10-26

## TL;DR

kicad-sch-api is **production-ready but needs improvements to be world-class**:

### Top 5 Priorities (Start Here)

1. **🔧 Refactor Point Creation** (1-2 hours)
   - Eliminate ~150 lines of repeated code
   - Create `point_from_dict_or_tuple()` helper

2. **📊 Add ERC Validation** (6-8 hours)
   - Critical missing feature
   - Check pin conflicts, power supplies, dangling wires
   - Expected by users for circuit validation

3. **📋 Complete Bus Support** (3-4 hours)
   - KiCAD 6/7/8 feature
   - Vector buses (DATA[0..7]) and group buses
   - Needed for realistic multi-signal designs

4. **🔗 Netlist & BOM Export** (10-14 hours)
   - Manufacturing-critical features
   - Netlist: KiCAD, SPICE, Eagle, EDIF formats
   - BOM: CSV, Excel with custom columns

5. **🔀 Modularize Parser** (4-6 hours)
   - parser.py is 2,351 lines (unmaintainable)
   - Split into 7-8 focused modules
   - Better maintainability and extensibility

---

## Quick Implementation Guide

### Phase 1: This Month (15-20 hours)

```
Week 1:
  □ Point creation helper (1.1) ............................ 1-2h
  □ Configuration constants (1.5) .......................... 1-2h
  □ Type hints cleanup (1.6) .............................. 2-3h
  □ Version detection (3.1) ............................... 2-3h
  └─ Subtotal: 6-10 hours

Week 2-3:
  □ Object initialization refactor (1.2) .................. 2-3h
  □ Parser modularization (1.3) ........................... 4-6h
  □ Base collection class (1.4) ........................... 3-4h
  └─ Subtotal: 9-13 hours

Total Phase 1: 15-23 hours (1-2 weeks)
Impact: Better code quality, foundation for new features
```

### Phase 2: Next 2 Months (40-50 hours)

```
Priority 1 - Core Features (weeks 4-7):
  □ Bus support (2.1) ..................................... 3-4h
  □ ERC validation (2.2) .................................. 6-8h
  □ Netlist generation (2.3) .............................. 6-8h
  □ BOM generation (2.4) .................................. 4-6h
  └─ Subtotal: 19-26 hours

Priority 2 - Advanced Features (weeks 8-9):
  □ SPICE simulation (2.5) ................................ 8-10h
  □ Text variables (2.6) .................................. 2-3h
  □ Hierarchy management (2.7) ............................ 6-8h
  □ Format versioning (3.2) ............................... 3-4h
  └─ Subtotal: 19-25 hours

Total Phase 2: 38-51 hours (6-8 weeks)
Impact: Feature-complete, professional-grade library
```

---

## Implementation Checklist

### Refactoring (HIGH IMPACT)

```
High Priority (do first):
  ✓ 1.1 Point creation helper
    ├─ Create point_from_dict_or_tuple() in types.py
    ├─ Update schematic.py to use helper
    └─ Remove 12+ repeated patterns

  ✓ 1.2 Element factory for initialization
    ├─ Create ElementFactory class
    ├─ Reduce Schematic.__init__ from 450 → 100 lines
    └─ Testable, maintainable creation logic

  ✓ 1.5 Configuration constants
    ├─ Create ElementTypeStrings (magic string values)
    ├─ Create Defaults (default values)
    ├─ Create KiCADVersion (version features)
    └─ Better error messages, IDE autocomplete

Medium Priority:
  ✓ 1.3 Parser modularization (2,351 lines → 8 modules)
  ✓ 1.4 Base collection class (eliminate duplication)
  ✓ 1.6 Complete type hints (mypy strict)
```

### Missing Features (HIGH VALUE)

```
Critical (feature-complete):
  ✓ 2.1 Bus support
    ├─ Vector buses: DATA[0..7]
    ├─ Group buses with custom signals
    └─ Bus entries (45° connectors)

  ✓ 2.2 Electrical Rules Check (ERC)
    ├─ Pin type conflict detection (output→output)
    ├─ Power supply verification
    ├─ Dangling wire detection
    └─ Duplicate reference detection

  ✓ 2.3 Netlist generation
    ├─ KiCAD native format
    ├─ SPICE netlist with models
    ├─ Eagle format
    └─ EDIF format

  ✓ 2.4 Bill of Materials
    ├─ CSV export with custom columns
    ├─ Excel (.xlsx) export
    ├─ Quantity aggregation
    └─ Property mapping

Advanced (professional features):
  ✓ 2.5 SPICE simulation integration
  ✓ 2.6 Text variables (${KICAD_PROJECT_NAME})
  ✓ 2.7 Advanced hierarchy management
  ✓ 3.2 Format version conversion
```

### Version Compatibility

```
Foundation (needed for multi-version support):
  ✓ 3.1 Version auto-detection
    ├─ Detect from file format
    ├─ Feature support flags
    └─ Warn on unsupported features

  ✓ 3.2 Format conversion
    ├─ Upgrade: v6 → v7 → v8
    ├─ Preserve data during conversion
    └─ Track version in output
```

---

## Code Example: What Gets Better

### Before: Repetitive Point Creation
```python
# Repeated 12+ times in schematic.py (lines 117-256)
position = junction_dict.get("position", {"x": 0, "y": 0})
if isinstance(position, dict):
    pos = Point(position["x"], position["y"])
elif isinstance(position, (list, tuple)):
    pos = Point(position[0], position[1])
else:
    pos = position

junction = Junction(
    uuid=junction_dict.get("uuid", str(uuid.uuid4())),
    position=pos,
    diameter=junction_dict.get("diameter", 0),
    color=junction_dict.get("color", (0, 0, 0, 0)),
)
```

### After: Clean, DRY Code
```python
# 1 line using helper (reusable everywhere)
junction = Junction(
    uuid=junction_dict.get("uuid", str(uuid.uuid4())),
    position=point_from_dict_or_tuple(junction_dict.get("position")),
    diameter=junction_dict.get("diameter", 0),
    color=junction_dict.get("color", (0, 0, 0, 0)),
)
```

### Before: Magic Strings Everywhere
```python
if wire_type not in ["wire", "bus"]:  # What are valid values?
    raise ValueError("Invalid wire type")

wire = Wire(
    uuid=...,
    wire_type=WireType(wire_dict.get("wire_type", "wire")),  # Default unclear
    stroke_type=wire_dict.get("stroke_type", "default"),  # Valid options?
)
```

### After: Clear Configuration
```python
# In config.py - single source of truth
class ElementTypeStrings:
    WIRE_TYPES = {"wire", "bus"}
    STROKE_TYPES = {"solid", "dash", "dot", "dashdot"}

# In code - self-documenting
if wire_type not in ElementTypeStrings.WIRE_TYPES:
    raise ValueError(f"Invalid wire type. Must be: {ElementTypeStrings.WIRE_TYPES}")

wire = Wire(
    uuid=...,
    wire_type=WireType(wire_dict.get("wire_type", Defaults.WIRE_TYPE)),
    stroke_type=wire_dict.get("stroke_type", Defaults.STROKE_TYPE),
)
```

### Before: No ERC (Users Can't Validate)
```python
# No way to check if circuit is valid
schematic = load_schematic("circuit.kicad_sch")
# ... user has no idea if there are problems
```

### After: Professional Validation
```python
schematic = load_schematic("circuit.kicad_sch")

# Get validation issues (ERC equivalent)
erc_violations = schematic.run_erc()

for violation in erc_violations:
    print(f"{violation.severity}: {violation.message}")
    # ERROR: Pin 1 of U1 (output) connected to Pin 2 of U2 (output)
    # WARNING: Chip U3 has no power supply
    # ERROR: Net "DATA_BUS" has no driver
```

### Before: Can't Generate Manufacturing Files
```python
schematic = load_schematic("circuit.kicad_sch")

# Stuck: No way to export for manufacturing
# Have to use KiCAD GUI to generate BOM, netlist
```

### After: Manufacturing-Ready
```python
schematic = load_schematic("circuit.kicad_sch")

# Generate BOM
bom = schematic.generate_bom()
bom.export_csv("components.csv")
bom.export_excel("components.xlsx")
# Output: 100x 10K Resistor, 50x 100nF Capacitor, ...

# Generate netlist
netlist = schematic.generate_netlist()
netlist.export_spice("circuit.cir")  # For simulation
netlist.export_kicad("circuit.net")  # For KiCAD
netlist.export_eagle("circuit.edn")  # For Eagle
```

---

## Success Criteria

### After Phase 1 (Code Quality)
- ✅ No major DRY violations
- ✅ All files < 500 lines
- ✅ Type hints 100% coverage
- ✅ mypy strict mode passing
- ✅ Configuration centralized

### After Phase 2 (Feature-Complete)
- ✅ All KiCAD 8 schematic elements supported
- ✅ ERC validation working
- ✅ Netlist & BOM export working
- ✅ SPICE simulation integration
- ✅ Multi-version support (v6, v7, v8)
- ✅ Test coverage 80%+

### Overall Impact
- 📈 Code maintainability: 5/5 (vs 3/5 currently)
- 📈 Feature completeness: 9/10 (vs 6/10 currently)
- 📈 Developer experience: 9/10 (vs 7/10 currently)
- 📈 Professional grade: 10/10 (vs 7/10 currently)

---

## Files to Read

1. **REFACTORING_AND_IMPROVEMENTS.md** (comprehensive)
   - All details, code examples, architecture diagrams
   - 8,000+ words with implementation guides

2. **This file** (quick reference)
   - Quick prioritization and checklist
   - Example code before/after

3. **repo-review/** directory
   - Current state analysis
   - Test coverage details
   - Feature inventory

---

## Estimated Timeline

| Phase | Duration | Effort | Benefit |
|-------|----------|--------|---------|
| 1: Quick Wins | 1-2 weeks | 15-20h | Foundation |
| 2: Refactoring | 3-4 weeks | 9-13h | Maintainability |
| 3: Core Features | 4-6 weeks | 19-26h | Feature-complete |
| 4: Advanced | 6-8 weeks | 19-25h | Professional |
| 5: Premium | 8-12 weeks | 8-12h | Market-leading |
| **Total** | **3-6 months** | **70-96h** | **World-class** |

---

## Getting Started

### Day 1: Start with Refactoring (Quick Wins)
```bash
# Create helper function (1.1)
# File: kicad_sch_api/core/types.py

def point_from_dict_or_tuple(data: Union[Dict, Tuple, List, Point],
                             default: Optional[Point] = None) -> Point:
    """Convert various position formats to Point."""
    if isinstance(data, Point):
        return data
    if isinstance(data, dict):
        return Point(data.get("x", 0), data.get("y", 0))
    if isinstance(data, (list, tuple)) and len(data) >= 2:
        return Point(data[0], data[1])
    return default or Point(0, 0)

# Test it
from kicad_sch_api.core.types import point_from_dict_or_tuple
assert point_from_dict_or_tuple({"x": 10, "y": 20}).x == 10
assert point_from_dict_or_tuple((10, 20)).y == 20
print("✅ Helper works!")

# Now replace all 12+ uses in schematic.py with this one function
```

### Week 1: Complete Phase 1
- Point helper ✓
- Configuration constants ✓
- Type hints ✓
- Version detection ✓

### Weeks 2-4: Do Phase 2
- Refactor initialization ✓
- Modularize parser ✓
- Base collection class ✓

### Weeks 5-12: Features
- ERC validation (do first - highest value)
- Bus support
- Netlist generation
- BOM generation
- SPICE integration

---

## Need Help?

Refer to **REFACTORING_AND_IMPROVEMENTS.md** for:
- Detailed implementation guides
- Code examples
- Architecture decisions
- Testing strategies
- Performance considerations

---

**Ready to make kicad-sch-api world-class?** Start with Phase 1 this week! 🚀
