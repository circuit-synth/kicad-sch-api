# KiCAD Bus System Research

**Date:** 2025-11-05
**Issue:** #31 - Complete Bus Support
**Purpose:** Understand KiCAD bus system for implementation

---

## 🔍 Bus System Overview

KiCAD supports two types of buses:

### 1. **Vector Buses** (Array/Range Buses)
- **Syntax:** `BusName[M..N]` where M and N are integers
- **Example:** `DATA[0..7]` expands to 8 signals: DATA0, DATA1, ..., DATA7
- **Use Case:** Multi-bit data buses, address buses, control signals
- **Net Names:** Produces nets like `DATA0`, `DATA1`, etc.

### 2. **Group Buses** (Named Signal Groups)
- **Syntax:** `BusName{Signal1 Signal2 Signal3}`
- **Example:** `CPU{CLK RST INT NMI}` groups 4 distinct signals
- **Mixed Example:** `MEMORY{A[7..0] D[7..0] OE WE}` combines vector buses and signals
- **Use Case:** Grouping related but non-sequential signals
- **Net Names:** Produces nets like `MEMORY.CLK`, `MEMORY.A7`, etc.

---

## 📐 Bus Entries (Wire-to-Bus Connectors)

### Purpose
- **Visual connectors** at 45° angles between individual wires and buses
- **Graphical only** - not required for logical connections
- **Professional appearance** - makes schematics cleaner and more readable

### File Format
```
(bus_entry
  (at X Y)              ; Position
  (size X_offset Y_offset)  ; Endpoint relative to start
  (stroke ...)          ; Visual appearance
  (uuid "...")          ; Unique identifier
)
```

### Typical Usage
- Connect individual component pins to bus lines
- Standard size: 2.54mm at 45° angle
- Usually placed where wires meet buses

---

## 📄 File Format Details

### Wire vs Bus in S-Expression
Both use identical structure, differing only in element name:

**Wire:**
```lisp
(wire (pts (xy X1 Y1) (xy X2 Y2))
  (stroke (width 0) (type default))
  (uuid "...")
)
```

**Bus:**
```lisp
(bus (pts (xy X1 Y1) (xy X2 Y2))
  (stroke (width 0) (type default))
  (uuid "...")
)
```

### Key Differences
1. **Element name:** `wire` vs `bus`
2. **Visual width:** Buses typically thicker (shown in schematic editor)
3. **Label interpretation:** Labels on buses use vector/group syntax

---

## 🏷️ Bus Labels

### Vector Bus Label
```
DATA[0..7]
```
- Must be attached to a **bus** (not wire)
- Automatically expands to 8 individual nets
- Each net can be accessed via bus entry + wire + label

### Group Bus Label
```
MEMORY{A[7..0] D[7..0] OE WE}
```
- Combines multiple signals and vector buses
- Produces hierarchical net names: `MEMORY.A7`, `MEMORY.OE`
- More flexible than vector buses

### Label Connection Rules
1. **Direct connection:** Label placed on bus/wire directly
2. **Bus entry connection:** Wire → Bus Entry → Bus → Label
3. **Hierarchical:** Can connect across sheets via hierarchical labels

---

## 🎯 Implementation Requirements

### Core Types Needed
1. **BusEntry dataclass** (NEW)
   - Position (Point)
   - Size (Point/offset)
   - Stroke definition
   - UUID

2. **Wire dataclass** (EXISTS - needs enhancement)
   - Currently has `wire_type: WireType` enum (WIRE, BUS)
   - Already supports bus type!
   - May need bus label parsing

3. **BusLabel dataclass** (NEW or extend Label)
   - Bus name
   - Type (vector vs group)
   - Range/signals
   - Parsing logic for `[M..N]` and `{signals}`

### Collections Needed
1. **BusEntryCollection** (NEW)
   - Add/remove bus entries
   - Query by position
   - Validation

2. **BusCollection** (NEW or extend WireCollection)
   - Specialized bus operations
   - Vector bus expansion utilities
   - Group bus parsing
   - Label validation

### Parser Support
1. **Bus entry parser** - Parse `(bus_entry ...)` S-expressions
2. **Bus label parser** - Parse vector `[M..N]` and group `{...}` syntax
3. **Wire parser** - Already handles buses (wire_type=BUS)

### API Features
1. **Bus creation:**
   ```python
   bus_uuid = sch.buses.add(start=(100, 100), end=(200, 100))
   ```

2. **Bus entry creation:**
   ```python
   entry_uuid = sch.bus_entries.add(position=(100, 110), size=(2.54, -2.54))
   ```

3. **Vector bus label:**
   ```python
   label = sch.add_bus_label("DATA[0..7]", position=(150, 100))
   ```

4. **Group bus label:**
   ```python
   label = sch.add_bus_label("CPU{CLK RST INT}", position=(150, 100))
   ```

5. **Bus expansion utilities:**
   ```python
   nets = sch.expand_bus_label("DATA[0..7]")
   # Returns: ["DATA0", "DATA1", ..., "DATA7"]
   ```

---

## 🧪 Testing Strategy

### Reference Schematics Needed
Create manual KiCAD schematics to understand exact format:

1. **Simple Vector Bus** - Single DATA[0..7] bus
2. **Multiple Vector Buses** - Address + Data buses
3. **Group Bus** - CPU control signals
4. **Mixed Bus** - Vector + individual signals in group
5. **Bus with Entries** - Proper 45° connectors
6. **Bus Hierarchical** - Bus across hierarchical sheets
7. **Complex Bus Circuit** - Realistic microprocessor interface

### Unit Tests Needed
- Bus entry creation and positioning
- Vector bus label parsing
- Group bus label parsing
- Bus expansion to individual nets
- Bus entry angle/size validation
- Integration with existing wire system

---

## 📚 References

- **KiCAD Documentation:** https://docs.kicad.org/8.0/en/eeschema/
- **File Format Spec:** https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
- **Forum Discussion:** https://forum.kicad.info/t/kicad-group-buses/49535
- **Stack Exchange:** https://electronics.stackexchange.com/questions/732026/kicad-8-0-bus-management

---

## 🎓 Key Learnings

1. **Bus entries are optional** - Purely graphical, not required for connections
2. **Buses use same structure as wires** - Just different element name in S-expression
3. **Label syntax is critical** - Parser must handle `[M..N]` and `{signals}` correctly
4. **Hierarchical names** - Group buses create dotted net names like `MEMORY.A7`
5. **KiCAD 6/7/8 compatibility** - Vector and group buses supported since KiCAD 6.0

---

## ✅ Next Steps

1. Create reference schematics manually in KiCAD
2. Analyze S-expression format from real files
3. Implement BusEntry and enhanced bus support
4. Create BusCollection with expansion utilities
5. Add comprehensive tests
6. Update documentation

---

**Status:** Research complete, ready for reference schematic creation
