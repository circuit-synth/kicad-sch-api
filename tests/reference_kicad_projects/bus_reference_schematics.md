# Bus System Reference Schematics

**Purpose:** Create manual KiCAD schematics to understand exact bus format for implementation
**Issue:** #31 - Complete Bus Support
**Date:** 2025-11-05

Following the proven pattern from hierarchy implementation (PR #91, #95, #96), we'll create reference schematics manually in KiCAD, then analyze the exact S-expression format to ensure our Python API generates identical output.

---

## 📋 Reference Schematics to Create

### ✅ **Priority 1: Foundation (Create First)**

#### 1. **`01_simple_vector_bus/`** - Basic Vector Bus
**Purpose:** Understand fundamental vector bus format

**What to create:**
- Single 8-bit data bus: `DATA[0..7]`
- Bus line (thick) from (100, 100) to (200, 100)
- Bus label "DATA[0..7]" on the bus
- No components, no bus entries - just the bus itself

**Expected learning:**
- Bus S-expression format vs wire format
- Bus label format for vector syntax `[M..N]`
- Stroke properties for buses

**File:** `01_simple_vector_bus/simple_vector_bus.kicad_sch`

---

#### 2. **`02_bus_with_entry/`** - Bus Entry Connector
**Purpose:** Understand bus entry format and positioning

**What to create:**
- Single 8-bit bus: `DATA[0..7]`
- Bus line from (100, 100) to (200, 100)
- **One bus entry** at (120, 100) connecting to bus
  - 45° angle, standard size (2.54mm)
  - Wire from bus entry to (120, 115)
  - Label "DATA0" on the wire

**Expected learning:**
- Bus entry S-expression: `(bus_entry (at X Y) (size dx dy) ...)`
- Positioning relative to bus
- Connection between wire-entry-bus-label

**File:** `02_bus_with_entry/bus_with_entry.kicad_sch`

---

#### 3. **`03_vector_bus_with_component/`** - Bus to Component Connection
**Purpose:** Complete bus-to-pin connection

**What to create:**
- 8-bit data bus: `DATA[0..7]`
- 8-input component (e.g., 74HC373 latch or resistor network)
- **8 bus entries** connecting bus to component pins
- Proper labels on each wire: DATA0, DATA1, ..., DATA7

**Expected learning:**
- Multiple bus entries from same bus
- Spacing and positioning conventions
- Real-world bus connection pattern

**File:** `03_vector_bus_with_component/vector_bus_component.kicad_sch`

---

### ✅ **Priority 2: Advanced Features**

#### 4. **`04_group_bus/`** - Group Bus (Named Signals)
**Purpose:** Understand group bus syntax

**What to create:**
- Group bus: `CPU{CLK RST INT NMI}`
- Bus line from (100, 100) to (200, 100)
- Bus label "CPU{CLK RST INT NMI}" on bus
- 4 bus entries with labels: CLK, RST, INT, NMI

**Expected learning:**
- Group bus syntax `{signal1 signal2 signal3}`
- How KiCAD parses non-sequential signal names
- Net name generation (CPU.CLK, CPU.RST, etc.)

**File:** `04_group_bus/group_bus.kicad_sch`

---

#### 5. **`05_mixed_bus/`** - Mixed Vector + Group Bus
**Purpose:** Complex bus with both types

**What to create:**
- Mixed bus: `MEMORY{A[7..0] D[7..0] OE WE}`
- Bus line across schematic
- Bus entries for:
  - 8 address lines (A0-A7)
  - 8 data lines (D0-D7)
  - 2 control signals (OE, WE)

**Expected learning:**
- Mixed syntax parsing
- Hierarchical net names (MEMORY.A7, MEMORY.OE)
- Complex bus label format

**File:** `05_mixed_bus/mixed_bus.kicad_sch`

---

#### 6. **`06_multiple_buses/`** - Multiple Independent Buses
**Purpose:** Multiple buses in one schematic

**What to create:**
- Address bus: `ADDR[15..0]` (16-bit)
- Data bus: `DATA[7..0]` (8-bit)
- Control bus: `CTRL{RD WR CS OE}`
- All three buses parallel on schematic
- Some connections to show differentiation

**Expected learning:**
- Multiple bus management
- Bus label positioning
- No crosstalk between buses

**File:** `06_multiple_buses/multiple_buses.kicad_sch`

---

### ✅ **Priority 3: Real-World Patterns**

#### 7. **`07_microprocessor_interface/`** - Realistic MCU Bus
**Purpose:** Professional bus usage pattern

**What to create:**
- Microcontroller (e.g., ATmega328P or similar)
- Address bus: `ADDR[15..0]`
- Data bus: `DATA[7..0]`
- Control bus: `CTRL{RD WR MREQ IORQ M1}`
- Memory chip connected via buses
- Proper bus entries to all connections

**Expected learning:**
- Real-world bus complexity
- Professional schematic appearance
- Bus routing best practices

**File:** `07_microprocessor_interface/mcu_bus.kicad_sch`

---

#### 8. **`08_bus_hierarchical/`** - Bus Across Sheets
**Purpose:** Hierarchical bus connections

**What to create:**
- **Root schematic:**
  - Hierarchical sheet symbol
  - Sheet pins for DATA[7..0] bus
  - Bus label on root

- **Child schematic:**
  - Hierarchical label DATA[7..0]
  - Component connections via bus

**Expected learning:**
- Bus through hierarchical boundaries
- Sheet pin bus syntax
- Hierarchical bus label matching

**Files:**
- `08_bus_hierarchical/root.kicad_sch`
- `08_bus_hierarchical/child.kicad_sch`

---

### ✅ **Priority 4: Edge Cases**

#### 9. **`09_bus_angles/`** - Non-Horizontal Buses
**Purpose:** Bus routing at various angles

**What to create:**
- Horizontal bus
- Vertical bus
- Diagonal bus (if supported)
- Bus entries at different angles

**Expected learning:**
- Bus entry angle calculation
- Non-standard bus orientations
- Entry positioning rules

**File:** `09_bus_angles/bus_angles.kicad_sch`

---

#### 10. **`10_bus_no_entries/`** - Direct Bus Connections
**Purpose:** Buses without graphical entries

**What to create:**
- Bus line with label DATA[0..7]
- Wires with labels DATA0, DATA1, etc. directly touching bus
- No bus entries (test if optional)

**Expected learning:**
- Whether bus entries are truly optional
- Direct wire-to-bus connections
- Alternate connection patterns

**File:** `10_bus_no_entries/bus_no_entries.kicad_sch`

---

## 🎯 Creation Priority Order

### **Start with these 3** (Core Understanding):
1. ✅ `01_simple_vector_bus` - Understand basic bus format
2. ✅ `02_bus_with_entry` - Understand bus entry format
3. ✅ `03_vector_bus_with_component` - Complete connection pattern

### **Then add these 3** (Advanced Features):
4. ✅ `04_group_bus` - Group bus syntax
5. ✅ `05_mixed_bus` - Complex combined syntax
6. ✅ `06_multiple_buses` - Multiple bus management

### **Finally these 2** (Real-World):
7. ✅ `07_microprocessor_interface` - Professional pattern
8. ✅ `08_bus_hierarchical` - Hierarchical integration

### **Optional** (Edge Cases):
9. ⚠️ `09_bus_angles` - If time permits
10. ⚠️ `10_bus_no_entries` - If time permits

---

## 📐 Creation Guidelines

### Grid Alignment
- Use 1.27mm (50 mil) grid for all elements
- Bus positions: multiples of 2.54mm preferred
- Bus entry standard size: 2.54mm at 45°

### Bus Styling
- **Width:** KiCAD default for buses (thicker than wires)
- **Color:** Default bus color (usually blue/green)
- **Stroke:** Default stroke type

### Naming Conventions
- Vector buses: `NAME[M..N]` - capitalize, use descriptive names
- Group buses: `NAME{SIG1 SIG2}` - capitalize consistently
- Net labels: Match bus syntax exactly (DATA0, not data0)

### Component Selection
- Use simple components: resistor networks, buffers, latches
- Avoid complex multi-unit symbols (keep focus on buses)
- DIP packages preferred for clarity

### Documentation
- Each schematic should have title block
- Include project name matching folder name
- Add comments explaining bus structure

---

## 🧪 Testing Checklist

After creating each schematic, verify:
- [ ] Schematic loads without errors in KiCAD
- [ ] Bus labels display correctly
- [ ] Electrical Rule Check (ERC) passes
- [ ] Netlist generation includes expanded bus nets
- [ ] File saved in KiCAD 8.0 format
- [ ] No unnecessary library dependencies

---

## 📊 Expected Analysis Points

For each schematic, we'll analyze:

1. **S-Expression Structure:**
   - `(bus ...)` format
   - `(bus_entry ...)` format
   - `(label ... (on_bus yes))` or similar

2. **Coordinate System:**
   - Bus entry positioning math
   - 45° angle calculation
   - Size parameter interpretation

3. **Label Parsing:**
   - Vector syntax `[M..N]` detection
   - Group syntax `{signals}` parsing
   - Nested syntax `{A[7..0] B}`

4. **Net Expansion:**
   - How DATA[0..7] expands to 8 nets
   - Hierarchical naming (MEMORY.A7)
   - Net name uniqueness

---

## 🚀 Next Steps After Creation

1. **User creates schematics** in KiCAD manually
2. **Claude analyzes** S-expression format from files
3. **Implement** Bus, BusEntry, BusCollection classes
4. **Write tests** verifying Python output matches reference
5. **Verify** byte-perfect format preservation

---

## 📝 Notes

- **Follow proven pattern:** This is the same approach used successfully for:
  - Pin rotation (PR #91) - 19 tests, all passing
  - Hierarchy management (PR #96) - 19 tests, all passing

- **Iterative approach:** Create → Analyze → Implement → Test → Verify

- **User involvement:** Your manual creation in KiCAD ensures we match real-world usage

---

**Ready to start!** Which schematic would you like to create first?

I recommend starting with `01_simple_vector_bus` to understand the basic format.
