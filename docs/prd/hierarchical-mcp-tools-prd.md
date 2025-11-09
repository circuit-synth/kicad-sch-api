# PRD: Add Hierarchical Schematic Tools to MCP Server

## Overview

Add missing MCP tools for hierarchical schematic creation, specifically sheet pins and hierarchical labels. The core library already has full hierarchical support, but these capabilities are not exposed as MCP tools, blocking Test 11 and real-world circuit design workflows.

**What exists:**
- `manage_sheets` tool with "add" and "set_context" actions (provides add_hierarchical_sheet and set_hierarchy_context)
- Core library: `schematic.sheets.add_sheet()`, `schematic.set_hierarchy_context()`, `schematic.add_sheet_pin()`, `schematic.add_hierarchical_label()`

**What's missing:**
- MCP tool for adding sheet pins
- MCP tool for adding hierarchical labels
- MCP tool for removing hierarchical labels

**Approach:** Add standalone tools following the pattern of `add_wire`, `add_label`, `add_junction`.

## Success Criteria

- [ ] `add_sheet_pin` MCP tool implemented and working
- [ ] `add_hierarchical_label` MCP tool implemented and working
- [ ] `remove_hierarchical_label` MCP tool implemented and working
- [ ] Test 11 (hierarchical schematics) can execute successfully
- [ ] Example hierarchical schematic workflow documented
- [ ] All MCP tests pass

## Functional Requirements

### REQ-1: Add Sheet Pin Tool

**Tool signature:**
```python
@mcp.tool()
async def add_sheet_pin(
    sheet_uuid: str,
    name: str,
    pin_type: str,
    edge: str,
    position_along_edge: float
) -> dict
```

**Parameters:**
- `sheet_uuid`: UUID of sheet to add pin to (from add_hierarchical_sheet response)
- `name`: Pin name (e.g., "VCC", "SDA", "CLK")
- `pin_type`: Electrical type - one of: "input", "output", "bidirectional", "tri_state", "passive"
- `edge`: Which edge to place pin on - one of: "left", "right", "top", "bottom"
- `position_along_edge`: Distance along edge from reference corner (mm)

**Returns:**
```python
{
    "success": True,
    "pin_uuid": "...",
    "sheet_uuid": "...",
    "name": "VCC",
    "pin_type": "output",
    "edge": "right",
    "position": {"x": 150.0, "y": 60.0},  # Calculated absolute position
    "message": "Added sheet pin: VCC"
}
```

**Error cases:**
- Sheet not found: `{"success": False, "error": "SHEET_NOT_FOUND"}`
- Invalid pin_type: `{"success": False, "error": "INVALID_PIN_TYPE"}`
- Invalid edge: `{"success": False, "error": "INVALID_EDGE"}`
- No schematic loaded: `{"success": False, "error": "NO_SCHEMATIC_LOADED"}`

**Delegates to:** `schematic.sheets.add_sheet_pin(sheet_uuid, name, pin_type, edge, position_along_edge)`

### REQ-2: Add Hierarchical Label Tool

**Tool signature:**
```python
@mcp.tool()
async def add_hierarchical_label(
    text: str,
    position: Tuple[float, float],
    shape: str = "input",
    rotation: float = 0.0,
    size: float = 1.27
) -> dict
```

**Parameters:**
- `text`: Label text (must match a sheet pin name in parent)
- `position`: Label position (x, y) in mm
- `shape`: Label shape/type - one of: "input", "output", "bidirectional", "tri_state", "passive" (default: "input")
- `rotation`: Label rotation in degrees (default: 0)
- `size`: Text size in mm (default: 1.27)

**Returns:**
```python
{
    "success": True,
    "label_uuid": "...",
    "text": "VCC",
    "position": {"x": 150.0, "y": 100.0},
    "shape": "output",
    "rotation": 0.0,
    "message": "Added hierarchical label: VCC"
}
```

**Error cases:**
- Invalid shape: `{"success": False, "error": "INVALID_SHAPE"}`
- No schematic loaded: `{"success": False, "error": "NO_SCHEMATIC_LOADED"}`

**Delegates to:** `schematic.add_hierarchical_label(text, position, shape, rotation, size)`

### REQ-3: Remove Hierarchical Label Tool

**Tool signature:**
```python
@mcp.tool()
async def remove_hierarchical_label(
    label_uuid: str
) -> dict
```

**Parameters:**
- `label_uuid`: UUID of hierarchical label to remove

**Returns:**
```python
{
    "success": True,
    "label_uuid": "...",
    "message": "Removed hierarchical label"
}
```

**Error cases:**
- Label not found: `{"success": False, "error": "LABEL_NOT_FOUND"}`
- No schematic loaded: `{"success": False, "error": "NO_SCHEMATIC_LOADED"}`

**Delegates to:** `schematic.remove_hierarchical_label(label_uuid)` (or similar removal method)

### REQ-4: Integration with Existing Tools

These new tools work alongside existing hierarchical tools:

**Creating hierarchical schematics workflow:**

1. **Create parent and add sheet** (existing tool):
   ```python
   # Uses manage_sheets with action="add"
   manage_sheets(
       action="add",
       name="Power Supply",
       filename="power.kicad_sch",
       position=(50, 50),
       size=(100, 100),
       project_name="MyProject"
   )
   # Returns: {"sheet_uuid": "...", ...}
   ```

2. **Add sheet pins** (NEW tool):
   ```python
   add_sheet_pin(
       sheet_uuid="...",
       name="VCC",
       pin_type="output",
       edge="right",
       position_along_edge=10.0
   )
   ```

3. **Create child schematic and set context** (existing tool):
   ```python
   # Uses manage_schematic
   manage_schematic(action="create", name="MyProject")

   # Uses manage_sheets with action="set_context"
   manage_sheets(
       action="set_context",
       parent_uuid="...",
       sheet_uuid="..."
   )
   ```

4. **Add components to child** (existing tool):
   ```python
   add_component(lib_id="Device:R", value="10k", ...)
   ```

5. **Add hierarchical labels in child** (NEW tool):
   ```python
   add_hierarchical_label(
       text="VCC",
       position=(150, 100),
       shape="output"
   )
   ```

## KiCAD Format Specifications

### Sheet Pin S-Expression Format

```lisp
(pin "VCC" output
  (at 150.0 60.0 0)
  (effects
    (font (size 1.27 1.27))
    (justify right)
  )
  (uuid "...")
)
```

**Required fields:**
- Pin name (string)
- Pin type: input | output | bidirectional | tri_state | passive
- Position (at x y rotation)
- Effects with font size
- Justification based on edge
- UUID

**Edge-based positioning (from sheet.py):**
- "right": rotation=0°, justify="right", position from top edge
- "bottom": rotation=270°, justify="left", position from left edge
- "left": rotation=180°, justify="left", position from bottom edge
- "top": rotation=90°, justify="right", position from left edge

### Hierarchical Label S-Expression Format

```lisp
(hierarchical_label "VCC"
  (shape output)
  (at 150.0 100.0 0)
  (effects
    (font (size 1.27 1.27))
  )
  (uuid "...")
)
```

**Required fields:**
- Label text (string)
- Shape: input | output | bidirectional | tri_state | passive
- Position (at x y rotation)
- Effects with font size
- UUID

**Version compatibility:** KiCAD 7.0 and 8.0

## Technical Constraints

### Backward Compatibility

- Must not break existing MCP tools
- Must work with existing `manage_sheets` tool
- Must maintain schematic state through `get_current_schematic()`

### Format Preservation

- Sheet pins must match exact KiCAD S-expression format
- Hierarchical labels must match exact KiCAD S-expression format
- UUIDs must be preserved/generated correctly
- Grid alignment not strictly required for labels (can be off-grid)

### Error Handling

- Validate all enum parameters (pin_type, shape, edge)
- Check schematic exists before operations
- Provide clear error messages for LLM debugging
- Log all operations for troubleshooting

## Reference Schematic Requirements

**NOT NEEDED** - This is an MCP server wrapper issue, not a format preservation issue. The core library already handles hierarchical schematics correctly. We just need to expose existing functions as MCP tools.

**Testing approach:**
- Use existing hierarchical reference schematics in `tests/reference_kicad_projects/`
- Verify MCP tools can recreate these schematics
- Test against Test 11 scenarios

## Edge Cases

### EC-1: Invalid Pin Types

**Input:** `pin_type="foo"`
**Expected:** Return error with valid pin types list
**Handling:** Validate against `["input", "output", "bidirectional", "tri_state", "passive"]`

### EC-2: Invalid Edge Values

**Input:** `edge="middle"`
**Expected:** Return error with valid edges list
**Handling:** Validate against `["left", "right", "top", "bottom"]`

### EC-3: Sheet Not Found

**Input:** `sheet_uuid="nonexistent"`
**Expected:** Return error indicating sheet not found
**Handling:** Check sheet exists before attempting to add pin

### EC-4: No Schematic Loaded

**Input:** Tools called without schematic loaded
**Expected:** Return error indicating no schematic
**Handling:** Check `get_current_schematic()` returns non-None

### EC-5: Hierarchical Label Name Mismatch

**Input:** Hierarchical label "VDD" in child, but sheet pin is "VCC"
**Expected:** Tool succeeds (validation is separate concern)
**Handling:** Tool adds label regardless, validation happens later (possibly in test suite or ERC)

### EC-6: Duplicate Sheet Pin Names

**Input:** Adding "VCC" pin twice to same sheet
**Expected:** Tool succeeds (KiCAD allows this, though ERC may warn)
**Handling:** No duplicate checking in MCP tool layer

## Impact Analysis

### Files to Modify

**New file:** `mcp_server/tools/hierarchy_tools.py`
- Contains: `add_sheet_pin()`, `add_hierarchical_label()`, `remove_hierarchical_label()`
- Pattern: Similar to `connectivity_tools.py`

**Modified file:** `mcp_server/server.py`
- Import new tools
- Register with `@mcp.tool()` decorators
- Add to tool registry

### Existing Tool Integration

**No changes required to:**
- `manage_sheets` - already provides add and set_context
- `manage_schematic` - used for create/load/save
- `add_component` - works with hierarchical context
- `add_wire`, `add_label` - work in child schematics

**Complements:**
- `manage_sheets` provides sheet creation and context
- New tools provide pin and label management
- Together enable full hierarchical workflow

### Testing Impact

**New MCP tests needed:**
- Test sheet pin creation on all edges
- Test hierarchical label creation with all shapes
- Test hierarchical workflow end-to-end
- Test error cases for validation

**Existing tests:**
- Core library tests already validate hierarchical functionality
- MCP server tests need new scenarios for these tools

## Out of Scope

- Sheet pin validation (matching with hierarchical labels) - handled by core library or ERC
- Multi-level hierarchy traversal tools - exists in HierarchyManager
- Hierarchy visualization tools - exists in HierarchyManager
- Netlist generation from hierarchical designs - separate concern (Issue #106)
- Automatic sheet pin positioning - user must specify edge and position
- Sheet pin reordering/modification - use remove + add pattern
- Hierarchical label connection validation - separate validation concern

## Acceptance Criteria

Implementation complete when:

- [ ] `add_sheet_pin` tool implemented in `mcp_server/tools/hierarchy_tools.py`
- [ ] `add_hierarchical_label` tool implemented in `mcp_server/tools/hierarchy_tools.py`
- [ ] `remove_hierarchical_label` tool implemented in `mcp_server/tools/hierarchy_tools.py`
- [ ] All three tools registered in `mcp_server/server.py`
- [ ] All tools handle error cases (no schematic, invalid params)
- [ ] All tools return standardized response format
- [ ] Tools successfully delegate to core library functions
- [ ] MCP integration tests added for hierarchical workflow
- [ ] Test 11 scenarios execute successfully
- [ ] Documentation updated (README, examples)
- [ ] Issue #110 updated to reflect existing vs new tools
- [ ] All existing MCP tests still pass
- [ ] Format preservation validated (output matches KiCAD)

---

**Implementation estimate:** 4-6 hours (simple MCP wrapper, no format preservation work needed)
**Priority:** P0 - Blocking Test 11 and real-world hierarchical design
**Complexity:** Low - wrapping existing, tested library functions
