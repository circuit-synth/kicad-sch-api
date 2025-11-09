# PRD: Add Hierarchical Schematic Support to MCP Server (Consolidated Tools Approach)

## Overview

Add hierarchical schematic support to the MCP server using the **consolidated tools pattern** introduced in PR #122. The core library already has full hierarchical support, but sheet pins and hierarchical labels are not exposed as MCP tools, blocking Test 11 and real-world circuit design workflows.

**What exists:**
- `manage_sheets` tool with "add" and "set_context" actions
- Core library: `schematic.sheets.add_sheet()`, `schematic.set_hierarchy_context()`, `schematic.sheets.add_sheet_pin()`, `schematic.add_hierarchical_label()`

**What's missing:**
- MCP tool for managing sheet pins (add/remove)
- MCP tool for managing hierarchical labels (add/remove)

**Approach:** Use **consolidated tools pattern** for optimal LLM performance:
- Extend `manage_sheets` with `add_pin` and `remove_pin` actions
- Create new `manage_hierarchical_labels` tool with `add` and `remove` actions
- Follows the pattern of `manage_global_labels` (8th consolidated tool)
- Results in 9th consolidated tool

## Success Criteria

- [x] `manage_sheets` extended with `add_pin` and `remove_pin` actions
- [x] `manage_hierarchical_labels` tool implemented (9th consolidated tool)
- [x] All MCP tools follow consolidated pattern
- [x] Test 11 (hierarchical schematics) can execute successfully
- [x] 22 comprehensive tests created and passing
- [ ] All existing MCP tests still pass
- [ ] Documentation complete

## Functional Requirements

### REQ-1: Extend manage_sheets with Sheet Pin Actions

**Tool signature (extended):**
```python
async def manage_sheets(
    action: str,  # "add", "set_context", "list", "remove", "add_pin", "remove_pin"
    # ... existing parameters ...
    # Pin-related parameters (NEW):
    pin_name: Optional[str] = None,
    pin_type: Optional[str] = None,
    edge: Optional[str] = None,
    position_along_edge: Optional[float] = None,
    pin_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict
```

**New actions:**

#### add_pin Action

**Parameters:**
- `sheet_uuid`: UUID of sheet to add pin to (required)
- `pin_name`: Pin name like "VCC", "SDA", "CLK" (required)
- `pin_type`: Electrical type - one of: "input", "output", "bidirectional", "tri_state", "passive" (required)
- `edge`: Which edge - one of: "left", "right", "top", "bottom" (required)
- `position_along_edge`: Distance along edge from reference corner in mm (required)

**Returns:**
```python
{
    "success": True,
    "pin_uuid": "...",
    "sheet_uuid": "...",
    "pin_name": "VCC",
    "pin_type": "output",
    "edge": "right",
    "position_along_edge": 10.0,
    "absolute_position": {"x": 150.0, "y": 60.0},  # Calculated
    "message": "Added sheet pin: VCC"
}
```

**Validation:**
- Validates `pin_type` against valid types list
- Validates `edge` against valid edges list
- Calculates absolute position based on sheet position, size, and edge

**Error cases:**
- Invalid pin_type → `{"success": False, "error": "INVALID_PIN_TYPE"}`
- Invalid edge → `{"success": False, "error": "INVALID_EDGE"}`
- Missing parameters → `{"success": False, "error": "INVALID_PARAMS"}`

#### remove_pin Action

**Parameters:**
- `sheet_uuid`: UUID of sheet containing the pin (required)
- `pin_uuid`: UUID of pin to remove (required)

**Returns:**
```python
{
    "success": True,
    "sheet_uuid": "...",
    "pin_uuid": "...",
    "message": "Removed sheet pin"
}
```

### REQ-2: Create manage_hierarchical_labels Tool (9th Consolidated Tool)

**Tool signature:**
```python
async def manage_hierarchical_labels(
    action: str,  # "add" or "remove"
    text: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    shape: str = "input",
    rotation: float = 0.0,
    size: float = 1.27,
    label_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict
```

**Pattern:** Follows `manage_global_labels` exactly

**add Action:**

**Parameters:**
- `text`: Label text - must match a sheet pin name in parent (required)
- `position`: Label position (x, y) in mm (required)
- `shape`: Label shape - one of: "input", "output", "bidirectional", "tri_state", "passive" (default: "input")
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
    "size": 1.27,
    "message": "Added hierarchical label: VCC"
}
```

**Validation:**
- Validates `shape` against valid shapes list
- Returns `INVALID_SHAPE` error for invalid shapes

**remove Action:**

**Parameters:**
- `label_uuid`: UUID of hierarchical label to remove (required)

**Returns:**
```python
{
    "success": True,
    "label_uuid": "...",
    "message": "Removed hierarchical label"
}
```

### REQ-3: Complete Hierarchical Workflow

**Creating hierarchical schematics with consolidated tools:**

```python
# 1. Create parent schematic
await manage_schematic(action="create", name="MyProject")
parent_info = await manage_schematic(action="read")
parent_uuid = parent_info["uuid"]

# 2. Add hierarchical sheet to parent
sheet_result = await manage_sheets(
    action="add",
    name="Power Supply",
    filename="power.kicad_sch",
    position=(50.0, 50.0),
    size=(100.0, 100.0),
    project_name="MyProject"
)
sheet_uuid = sheet_result["sheet_uuid"]

# 3. Add sheet pins to parent (NEW)
await manage_sheets(
    action="add_pin",
    sheet_uuid=sheet_uuid,
    pin_name="VCC",
    pin_type="output",
    edge="right",
    position_along_edge=10.0
)

await manage_sheets(
    action="add_pin",
    sheet_uuid=sheet_uuid,
    pin_name="GND",
    pin_type="output",
    edge="right",
    position_along_edge=30.0
)

# 4. Save parent
await manage_schematic(action="save", file_path="main.kicad_sch")

# 5. Create child schematic (SAME project name!)
await manage_schematic(action="create", name="MyProject")

# 6. Set hierarchy context (CRITICAL!)
await manage_sheets(
    action="set_context",
    parent_uuid=parent_uuid,
    sheet_uuid=sheet_uuid
)

# 7. Add components to child
await manage_components(
    action="add",
    lib_id="Regulator_Linear:AMS1117-3.3",
    reference="U1",
    value="AMS1117-3.3"
)

# 8. Add hierarchical labels in child (NEW)
await manage_hierarchical_labels(
    action="add",
    text="VCC",
    position=(150.0, 100.0),
    shape="output"
)

await manage_hierarchical_labels(
    action="add",
    text="GND",
    position=(150.0, 120.0),
    shape="output"
)

# 9. Save child
await manage_schematic(action="save", file_path="power.kicad_sch")
```

## Implementation Details

### Files Modified

**1. `mcp_server/tools/consolidated_tools.py`**
- Extended `manage_sheets` function signature with pin parameters
- Added `add_pin` action (validates pin_type, edge, calculates absolute position)
- Added `remove_pin` action
- Created new `manage_hierarchical_labels` function (130 lines, follows manage_global_labels pattern)

**2. `mcp_server/server.py`**
- Added import for `manage_hierarchical_labels`
- Registered new tool with `@mcp.tool()` decorator
- Updated comment from 8 to 9 consolidated tools
- Updated inline comment for `manage_sheets` to include new actions

### Testing

**Created `tests/mcp/test_hierarchical_tools.py` with 22 comprehensive tests:**

**TestManageSheetsAddPin (7 tests):**
- test_add_pin_right_edge
- test_add_pin_left_edge
- test_add_pin_top_edge
- test_add_pin_bottom_edge
- test_add_pin_all_types
- test_add_pin_invalid_pin_type
- test_add_pin_invalid_edge

**TestManageSheetsRemovePin (3 tests):**
- test_remove_pin_success
- test_remove_pin_missing_params
- test_remove_nonexistent_pin

**TestManageHierarchicalLabels (10 tests):**
- test_add_hierarchical_label_input
- test_add_hierarchical_label_output
- test_add_hierarchical_label_bidirectional
- test_add_hierarchical_label_tri_state
- test_add_hierarchical_label_passive
- test_add_hierarchical_label_with_rotation
- test_add_hierarchical_label_with_custom_size
- test_add_hierarchical_label_invalid_shape
- test_remove_hierarchical_label
- test_remove_hierarchical_label_missing_params

**TestHierarchicalWorkflowEndToEnd (2 tests):**
- test_complete_hierarchical_workflow
- test_multi_level_hierarchy

## Architecture Rationale

### Why Consolidated Tools?

**From PR #122 analysis:**
- Consolidated 43 tools → 8 for "optimal LLM performance"
- Reduces tool count, simplifies LLM decision-making
- Groups operations by entity type with action parameter

**Design decision:**
- New feature with no backward compatibility requirements
- User explicitly chose consolidated approach
- Keeps total tool count at 9 instead of adding 3 more standalone tools
- Aligns with stated architectural direction

### Why Extend manage_sheets vs Separate Tool?

**Sheet pins are sheet properties:**
- Pins belong to sheets (not independent entities)
- Sheet operations already grouped in `manage_sheets`
- Follows single responsibility per entity type
- No need for separate `manage_sheet_pins` tool

### Pattern Consistency

**manage_hierarchical_labels follows manage_global_labels:**
- Identical structure (add/remove actions)
- Similar parameters (text, position, shape)
- Same validation patterns
- Consistent with existing label tools

## Technical Constraints

### Format Preservation

- Sheet pins must match exact KiCAD S-expression format
- Hierarchical labels must match exact KiCAD S-expression format
- Core library already handles format preservation
- MCP tools are thin wrappers with no format logic

### Backward Compatibility

- Must not break existing MCP tools
- Must maintain schematic state through `get_current_schematic()`
- Existing `manage_sheets` actions ("add", "set_context", "list", "remove") unchanged

### Error Handling

- Validate all enum parameters (pin_type, shape, edge)
- Check schematic exists before operations
- Provide clear error messages for LLM debugging
- Log all operations for troubleshooting

## Edge Cases

### EC-1: Invalid Pin Types
**Handled:** Validate against valid_pin_types list, return INVALID_PIN_TYPE error

### EC-2: Invalid Edge Values
**Handled:** Validate against valid_edges list, return INVALID_EDGE error

### EC-3: Invalid Shapes
**Handled:** Validate against valid_shapes list, return INVALID_SHAPE error

### EC-4: No Schematic Loaded
**Handled:** Check `get_current_schematic()` returns non-None

### EC-5: Hierarchical Label Name Mismatch
**Handled:** Tool adds label regardless (validation is separate concern)

### EC-6: Duplicate Sheet Pin Names
**Handled:** No duplicate checking in MCP layer (KiCAD allows, ERC may warn)

## Acceptance Criteria

Implementation complete when:

- [x] `manage_sheets` extended with `add_pin` and `remove_pin` actions
- [x] `manage_hierarchical_labels` tool implemented following `manage_global_labels` pattern
- [x] Both tools registered in `mcp_server/server.py`
- [x] All tools handle error cases (no schematic, invalid params)
- [x] All tools return standardized response format
- [x] Tools successfully delegate to core library functions
- [x] 22 MCP integration tests added for hierarchical workflow
- [ ] All existing MCP tests still pass (verify 71/72 baseline)
- [ ] Test 11 scenarios execute successfully
- [ ] Documentation updated (README, examples)
- [ ] Issue #110 can be closed
- [ ] Format preservation validated (output matches KiCAD)

## Out of Scope

- Sheet pin validation (matching with hierarchical labels) - handled by core library or ERC
- Multi-level hierarchy traversal tools - exists in HierarchyManager
- Hierarchy visualization tools - exists in HierarchyManager
- Netlist generation from hierarchical designs - separate concern (Issue #106)
- Automatic sheet pin positioning - user must specify edge and position
- Sheet pin reordering/modification - use remove + add pattern
- Hierarchical label connection validation - separate validation concern

---

**Implementation estimate:** 4-6 hours (simple MCP wrapper, no format preservation work needed)
**Priority:** P0 - Blocking Test 11 and real-world hierarchical design
**Complexity:** Low - wrapping existing, tested library functions
**Pattern:** Consolidated tools (optimal LLM performance)
