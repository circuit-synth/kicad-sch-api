# MCP Server Setup Guide for Claude Code

## ⚠️ CRITICAL: Run Claude Code WITHOUT Permissions Flag

**DO NOT use `--dangerously-skip-permissions` flag when running Claude Code!**

```bash
# ❌ WRONG - This prevents MCP servers from loading:
claude --dangerously-skip-permissions

# ✅ CORRECT - Run normally to allow MCP approval prompts:
claude
```

The `--dangerously-skip-permissions` flag bypasses the MCP server approval flow, preventing the `.mcp.json` file from being processed. You MUST run Claude Code normally to see the approval prompt and load MCP servers.

---

## Quick Setup (5 minutes)

### Step 1: Install the package

```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
uv pip install -e .
```

### Step 2: Verify .mcp.json exists

The `.mcp.json` file should already exist in the project root:

```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "kicad-sch-mcp"]
    }
  }
}
```

This file tells Claude Code to load the MCP server automatically when you open this project.

### Step 3: Start Claude Code (WITHOUT skip-permissions flag!)

```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
claude  # ← Run normally, NOT with --dangerously-skip-permissions
```

### Step 4: Approve the MCP Server

When Claude Code starts, you should see a prompt asking to approve the `kicad-sch-api` MCP server. Click **"Approve"**.

### Step 5: Verify it's working

Once approved, ask Claude:

> "What MCP tools do you have available?"

You should see 15 tools:

**Schematic Management (4 tools):**
- `create_schematic` - Create new blank schematics
- `load_schematic` - Load existing .kicad_sch files
- `save_schematic` - Save schematics to disk
- `get_schematic_info` - Query schematic metadata

**Component Management (5 tools):**
- `add_component` - Add components to the schematic
- `list_components` - List all components with metadata
- `update_component` - Update component properties
- `remove_component` - Remove components
- `filter_components` - Filter components by criteria

**Connectivity (3 tools):**
- `add_wire` - Create wire connections
- `add_label` - Add net labels
- `add_junction` - Add wire junctions

**Pin Discovery (3 tools):**
- `get_component_pins` - Get comprehensive pin information
- `find_pins_by_name` - Find pins by name pattern (wildcards supported)
- `find_pins_by_type` - Find pins by electrical type

## Example Usage

Once configured, you can ask Claude to:

### Example 1: Create circuit with components

```
Create a new schematic called "TestCircuit" and add a 10k resistor at position (100, 100), then get its pin information.
```

Claude will use the MCP tools to:
1. Call `create_schematic("TestCircuit")`
2. Call `add_component(lib_id="Device:R", value="10k", reference="R1", position=(100, 100))`
3. Call `get_component_pins("R1")` to retrieve pin data

### Example 2: Build a complete voltage divider circuit

```
Create a voltage divider circuit with R1=10k and R2=1k, fully connected with VCC and GND labels.
```

Claude will:
1. Create a schematic
2. Add R1 and R2 using `add_component`
3. Connect them with `add_wire`
4. Add "VCC" and "GND" labels using `add_label`
5. Add junctions where wires meet using `add_junction`
6. Save the schematic

This demonstrates the full circuit-building workflow!

## Troubleshooting

### ⚠️ #1 Most Common Issue: Using --dangerously-skip-permissions Flag

**If tools aren't appearing, check if you're running Claude Code with the skip-permissions flag:**

```bash
# ❌ This PREVENTS MCP servers from loading:
claude --dangerously-skip-permissions

# ✅ Run normally instead:
claude
```

The permissions system is what triggers the MCP approval flow. Without it, the `.mcp.json` file is never processed!

### Tools still not appearing?
- Make sure you approved the MCP server when prompted
- Restart Claude Code completely
- Check that `.mcp.json` exists in the project root
- Verify the package is installed: `uv pip list | grep kicad-sch-api`

### Server not starting?
```bash
# Test the server manually
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
uv run kicad-sch-mcp
```

Press Ctrl+C to stop. If this works, the server is fine - check your config.

### Check Claude Desktop logs
**macOS**: `~/Library/Logs/Claude/mcp*.log`

Look for errors related to kicad-sch-api startup.

## What You Can Do

Once set up, you can ask Claude to:

### Component Management
- **Add components**: "Add a 10k resistor at position (100, 100) with reference R1"
- **List components**: "Show me all components in the schematic"
- **Update components**: "Change R1's value to 20k and rotate it 90 degrees"
- **Filter components**: "Find all resistors with value 10k"
- **Remove components**: "Remove capacitor C3"
- **Add with footprint**: "Add a 100nF capacitor with footprint C_0603_1608Metric"

### Circuit Building & Connectivity
- **Wire connections**: "Connect pin 1 of R1 to pin 1 of R2 with a wire"
- **Net labels**: "Add a VCC label at position (100, 50)"
- **Junctions**: "Add a junction where three wires meet at (125, 100)"
- **Complete circuits**: "Create a voltage divider with R1=10k and R2=1k, fully wired with VCC and GND"
- **Build filters**: "Create an RC low-pass filter with R=10k and C=100nF, connected with wires"

### Analysis & Discovery
- **Analyze schematics**: "Load my schematic and list all components"
- **Find pins**: "Find all the power input pins in component U1"
- **Discover pins by pattern**: "Find all pins with CLK in the name on IC1"

### File Operations
- **Save work**: "Save this schematic to ~/Desktop/my_circuit.kicad_sch"
- **Load circuits**: "Load the schematic at ~/Desktop/existing.kicad_sch"

## Complete Circuit Creation Examples

You can now build complete, functional circuits entirely through MCP:

### Example 1: LED Circuit with Current Limiting Resistor

**Natural Language Request**:
```
Create a complete LED circuit with a 220Ω current limiting resistor:
1. Add an LED
2. Add a 220Ω resistor
3. Wire the LED anode to one resistor pin
4. Add a VCC label at the other resistor pin
5. Add a GND label at the LED cathode
6. Save as led_circuit.kicad_sch
```

**What MCP Tools Get Called**:
1. `create_schematic(name="LED Circuit")`
2. `add_component(lib_id="Device:LED", reference="D1", value="LED", position=(127.0, 76.2))`
3. `add_component(lib_id="Device:R", reference="R1", value="220", position=(127.0, 95.25))`
4. `get_component_pins("D1")` - Get LED pin positions
5. `get_component_pins("R1")` - Get resistor pin positions
6. `add_wire(start=(127.0, 72.39), end=(127.0, 66.04))` - VCC to R1
7. `add_wire(start=(127.0, 80.01), end=(127.0, 91.44))` - R1 to D1
8. `add_wire(start=(127.0, 99.06), end=(127.0, 105.41))` - D1 to GND
9. `add_label(text="VCC", position=(129.54, 66.04))`
10. `add_label(text="GND", position=(129.54, 105.41))`
11. `save_schematic(file_path="led_circuit.kicad_sch")`

**Result**: Fully functional KiCAD schematic ready to open in KiCAD!

### Example 2: RC Low-Pass Filter

**Natural Language Request**:
```
Create an RC low-pass filter with R=10k, C=100nF, cutoff frequency ~159Hz
```

**What Happens**:
1. Creates schematic
2. Adds resistor R1 (10k) and capacitor C1 (100nF)
3. Gets pin positions for both components
4. Wires input → R1 → C1 → output
5. Adds GND connection to capacitor
6. Labels: INPUT, OUTPUT, GND
7. Adds junction at output node
8. Saves schematic

### Example 3: Voltage Divider (Verified Working)

**Natural Language Request**:
```
Create a voltage divider with R1=10k and R2=20k, fully connected with VCC and GND
```

**Exact Tool Calls** (this was tested and verified):
```python
# 1. Create schematic
create_schematic(name="Voltage Divider")

# 2. Add components
add_component(lib_id="Device:R", reference="R1", value="10k",
              position=(127.0, 76.2), rotation=0)
add_component(lib_id="Device:R", reference="R2", value="20k",
              position=(127.0, 95.25), rotation=0)

# 3. Get pin positions
get_component_pins("R1")  # Returns pin 1 at (127.0, 72.39), pin 2 at (127.0, 80.01)
get_component_pins("R2")  # Returns pin 1 at (127.0, 91.44), pin 2 at (127.0, 99.06)

# 4. Add wires
add_wire(start=(127.0, 72.39), end=(127.0, 66.04))   # VCC to R1 pin 1
add_wire(start=(127.0, 80.01), end=(127.0, 91.44))   # R1 pin 2 to R2 pin 1
add_wire(start=(127.0, 99.06), end=(127.0, 105.41))  # R2 pin 2 to GND

# 5. Add labels
add_label(text="VCC", position=(129.54, 66.04), rotation=0.0)
add_label(text="VOUT", position=(129.54, 85.725), rotation=0.0)
add_label(text="GND", position=(129.54, 105.41), rotation=0.0)

# 6. Add junction at tap point
add_junction(position=(127.0, 85.725), diameter=0.0)

# 7. Save
save_schematic(file_path="voltage_divider.kicad_sch")
```

**Result**: ✅ Verified working - opens perfectly in KiCAD with proper connections

## Detailed Tool Reference

### Schematic Management Tools

#### `create_schematic(name: str)`
Create a new blank KiCAD schematic.

**Parameters**:
- `name`: Project name for the schematic

**Returns**: Success message with schematic info

**Example**:
```
"Create a new schematic called MyProject"
```

#### `load_schematic(file_path: str)`
Load an existing .kicad_sch file.

**Parameters**:
- `file_path`: Absolute path to .kicad_sch file

**Example**:
```
"Load the schematic at /Users/me/Desktop/test.kicad_sch"
```

#### `save_schematic(file_path: str = None)`
Save the current schematic to disk.

**Parameters**:
- `file_path`: Optional path to save to. If not provided, saves to original location.

**Example**:
```
"Save this schematic to ~/Desktop/my_circuit.kicad_sch"
```

#### `get_schematic_info()`
Get information about the currently loaded schematic.

**Returns**: Metadata including project name, component count, etc.

**Example**:
```
"What components are in the current schematic?"
```

### Component Management Tools

#### `add_component(lib_id: str, value: str, reference: str = None, position: tuple = None, rotation: float = 0, footprint: str = None)`
Add a component to the schematic.

**Parameters**:
- `lib_id`: Library identifier (e.g., "Device:R", "Device:C", "Device:LED")
- `value`: Component value (e.g., "10k", "100nF", "LED")
- `reference`: Component reference (e.g., "R1", "C1") - auto-generated if not provided
- `position`: (x, y) tuple in mm - auto-placed if not provided
- `rotation`: Rotation in degrees (0, 90, 180, 270)
- `footprint`: PCB footprint (e.g., "Resistor_SMD:R_0603_1608Metric")

**Examples**:
```
"Add a 10k resistor at position (100, 100) with reference R1"
"Add a 100nF capacitor with footprint C_0603_1608Metric"
"Add an LED at (150, 150) rotated 90 degrees"
```

#### `list_components()`
List all components in the current schematic.

**Returns**: List of all components with complete metadata

**Example**:
```
"Show me all components in the schematic"
```

#### `update_component(reference: str, value: str = None, position: tuple = None, rotation: float = None, footprint: str = None)`
Update component properties.

**Parameters**:
- `reference`: Component reference to update (e.g., "R1")
- `value`: New value (optional)
- `position`: New position (optional)
- `rotation`: New rotation (optional)
- `footprint`: New footprint (optional)

**Examples**:
```
"Change R1's value to 20k"
"Rotate C1 by 90 degrees"
"Move U1 to position (200, 200)"
"Update R1 value to 47k and footprint to R_0805_2012Metric"
```

#### `remove_component(reference: str)`
Remove a component from the schematic.

**Parameters**:
- `reference`: Component reference to remove (e.g., "R1")

**Example**:
```
"Remove capacitor C3"
```

#### `filter_components(lib_id: str = None, value: str = None, footprint: str = None)`
Filter components by criteria (uses AND logic).

**Parameters**:
- `lib_id`: Filter by library ID pattern (optional)
- `value`: Filter by value pattern (optional)
- `footprint`: Filter by footprint pattern (optional)

**Examples**:
```
"Find all resistors" → filter_components(lib_id="Device:R")
"Find all 10k resistors" → filter_components(lib_id="Device:R", value="10k")
"Find all 0603 components" → filter_components(footprint="*0603*")
```

### Connectivity Tools

#### `add_wire(start: tuple, end: tuple)`
Add a wire connection between two points.

**Parameters**:
- `start`: (x, y) starting point in mm
- `end`: (x, y) ending point in mm

**Returns**: Wire UUID for tracking

**Example**:
```
"Connect point (100, 100) to point (150, 100) with a wire"
```

**Note**: KiCAD wires should be horizontal or vertical for proper connectivity.
The library supports both but horizontal/vertical is recommended.

#### `add_label(text: str, position: tuple, rotation: float = 0.0, size: float = 1.27)`
Add a net label to the schematic.

**Parameters**:
- `text`: Label text (e.g., "VCC", "GND", "DATA")
- `position`: (x, y) position in mm
- `rotation`: Rotation in degrees (0, 90, 180, 270) - default 0
- `size`: Text size in mm - default 1.27

**Returns**: Label UUID

**Examples**:
```
"Add a VCC label at position (100, 50)"
"Add a DATA label rotated 90 degrees at (150, 100)"
```

**Note**: Labels create logical connections between nets with the same name.
For example, all wires labeled "VCC" are electrically connected.

#### `add_junction(position: tuple, diameter: float = 0.0)`
Add a wire junction (visual indicator for T-connections).

**Parameters**:
- `position`: (x, y) position in mm
- `diameter`: Junction diameter in mm (0 = use KiCAD default)

**Returns**: Junction UUID

**Example**:
```
"Add a junction where three wires meet at (125, 100)"
```

**Note**: Junctions are required where 3+ wires meet to indicate proper electrical connection.

### Pin Discovery Tools

#### `get_component_pins(reference: str)`
Get comprehensive pin information for a component.

**Parameters**:
- `reference`: Component reference (e.g., "R1", "U1")

**Returns**: All pins with positions, types, names, and numbers

**Example**:
```
"Get all pin information for U1"
"What are the pin positions for R1?"
```

**Output includes**:
- Pin number (e.g., "1", "2")
- Pin name (e.g., "VCC", "GND", "CLK")
- Electrical type (e.g., "passive", "input", "output", "power_in")
- Position in schematic coordinates (x, y)

#### `find_pins_by_name(reference: str, name_pattern: str, case_sensitive: bool = False)`
Find pins matching a name pattern (supports wildcards).

**Parameters**:
- `reference`: Component reference
- `name_pattern`: Pattern to match (e.g., "VCC", "CLK*", "*IN*")
- `case_sensitive`: Case-sensitive matching (default: False)

**Examples**:
```
"Find all clock pins on U1" → find_pins_by_name("U1", "CLK*")
"Find all input pins on IC1" → find_pins_by_name("IC1", "*IN*")
"Find the VCC pin on U2" → find_pins_by_name("U2", "vcc")
```

#### `find_pins_by_type(reference: str, pin_type: str)`
Find pins by electrical type.

**Parameters**:
- `reference`: Component reference
- `pin_type`: Type filter - one of:
  - `"input"` - Input pins
  - `"output"` - Output pins
  - `"bidirectional"` - Bidirectional pins
  - `"passive"` - Passive pins (resistors, capacitors)
  - `"power_in"` - Power input pins
  - `"power_out"` - Power output pins
  - `"open_collector"` - Open collector
  - `"open_emitter"` - Open emitter
  - `"tri_state"` - Tri-state
  - `"unspecified"` - Unspecified type
  - `"no_connect"` - No connect

**Examples**:
```
"Find all input pins on U1" → find_pins_by_type("U1", "input")
"Find all power pins on IC1" → find_pins_by_type("IC1", "power_in")
```

## Common Library IDs

Here are common component library IDs for quick reference:

### Passive Components
- `Device:R` - Resistor
- `Device:C` - Capacitor
- `Device:L` - Inductor
- `Device:CP` - Polarized capacitor
- `Device:R_POT` - Potentiometer

### Semiconductors
- `Device:LED` - LED
- `Device:D` - Diode
- `Device:D_Zener` - Zener diode
- `Device:Q_NPN_BCE` - NPN transistor
- `Device:Q_PNP_BCE` - PNP transistor

### Integrated Circuits
- `Amplifier_Operational:TL072` - Dual op-amp
- `Amplifier_Operational:LM358` - Dual op-amp
- `Regulator_Linear:AMS1117-3.3` - 3.3V linear regulator
- `MCU_ST_STM32F4:STM32F407VGTx` - STM32 microcontroller

### Connectors
- `Connector:Conn_01x02` - 2-pin connector
- `Connector:Conn_01x04` - 4-pin connector
- `Connector_Generic:Conn_01x08` - 8-pin connector

## Understanding KiCAD Coordinates

**CRITICAL**: KiCAD uses millimeters and a specific coordinate system:

### Grid Alignment
- **Default grid**: 1.27mm (50 mil)
- **ALL positions must be grid-aligned**: Components, wires, labels, junctions
- **Common grid values**: 0.00, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, ...

**Good coordinates** (on grid):
```python
position=(127.0, 76.2)   # 100 × 1.27, 60 × 1.27
position=(101.6, 88.9)   # 80 × 1.27, 70 × 1.27
```

**Bad coordinates** (off grid):
```python
position=(100.5, 75.3)   # Not grid-aligned - will cause connectivity issues!
```

### Coordinate System
- **X-axis**: Normal (increases to the right)
- **Y-axis**: INVERTED (+Y is DOWN, like computer graphics)
  - Lower Y values = visually HIGHER on screen (top)
  - Higher Y values = visually LOWER on screen (bottom)

### Component Rotation
- `0°` - Default orientation (vertical for resistors/capacitors)
- `90°` - Rotated 90° clockwise
- `180°` - Upside down
- `270°` - Rotated 90° counter-clockwise

**Example for resistor**:
- `rotation=0` - Vertical, pins at top and bottom
- `rotation=90` - Horizontal, pins on left and right

## Additional Resources

For comprehensive usage examples and patterns, see:

**📖 [MCP Examples Guide](docs/MCP_EXAMPLES.md)** - Complete examples including:
- Basic component operations
- Building complete circuits (voltage dividers, LED circuits, filters)
- Advanced pin discovery
- Batch component updates
- Common patterns and best practices
- Troubleshooting guide

**📖 [API Reference](docs/API_REFERENCE.md)** - Complete Python API documentation

**📖 [README](README.md)** - Main project documentation

---

**Questions or Issues?**

Report problems at: https://github.com/circuit-synth/kicad-sch-api/issues
