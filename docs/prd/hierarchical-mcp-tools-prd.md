# PRD: Add Hierarchical Schematic Support to MCP Server

## Overview

Add missing MCP functionality for hierarchical schematic creation. The core library already has full hierarchical support, but sheet pins and hierarchical labels are not exposed through MCP consolidated tools.

**What exists:**
- `manage_sheets` with "add" and "set_context" actions
- `manage_labels` for local/net labels  
- `manage_global_labels` for global labels
- Core library: Full hierarchical support

**What's missing:**
- Sheet pin actions in `manage_sheets`
- `manage_hierarchical_labels` consolidated tool

**Approach:**
- Create `manage_hierarchical_labels` (9th consolidated tool)
- Extend `manage_sheets` with "add_pin" and "remove_pin" actions

## Success Criteria

- [ ] `manage_hierarchical_labels` tool implemented
- [ ] `manage_sheets` extended with pin actions
- [ ] Test 11 scenarios pass
- [ ] All existing MCP tests pass

## Functional Requirements

### REQ-1: Extend manage_sheets with Sheet Pin Actions

Extend `manage_sheets` with "add_pin" and "remove_pin" actions.

**Action: "add_pin"**

Required params:
- sheet_uuid, pin_name, pin_type, edge, position_along_edge

Returns: `{"success": True, "pin_uuid": "...", "position": {...}}`

Delegates to: `schematic.sheets.add_sheet_pin()`

**Action: "remove_pin"**

Required params:
- sheet_uuid, pin_uuid

Returns: `{"success": True, "pin_uuid": "..."}`

Delegates to: `schematic.sheets.remove_sheet_pin()`

### REQ-2: Create manage_hierarchical_labels Tool

New consolidated tool following `manage_global_labels` pattern.

**Action: "add"**

Required params:
- text, position

Optional params:
- shape (default: "input"), rotation (default: 0), size (default: 1.27)

Returns: `{"success": True, "label_uuid": "...", "text": "VCC"}`

Delegates to: `schematic.add_hierarchical_label()`

**Action: "remove"**

Required params:
- label_uuid

Returns: `{"success": True, "label_uuid": "..."}`

Delegates to: `schematic.remove_hierarchical_label()`

### REQ-3: Complete Workflow Example

```python
# Create parent + sheet
manage_sheets(action="add", name="Power", filename="power.kicad_sch", ...)

# Add sheet pins (NEW)
manage_sheets(action="add_pin", sheet_uuid="...", pin_name="VCC", 
              pin_type="output", edge="right", position_along_edge=10.0)

# Create child + set context
manage_schematic(action="create", name="MyProject")
manage_sheets(action="set_context", parent_uuid="...", sheet_uuid="...")

# Add hierarchical labels in child (NEW)
manage_hierarchical_labels(action="add", text="VCC", position=(150, 100), 
                          shape="output")
```

## Technical Constraints

- Backward compatible with existing tools
- Maintains consolidated tool pattern (8 → 9 tools)
- Format preservation handled by core library
- Standardized error responses

## Edge Cases

- Invalid pin_type/shape/edge → return error with valid values
- Sheet/label not found → return NOT_FOUND error
- No schematic loaded → return NO_SCHEMATIC_LOADED error
- Missing required params → return INVALID_PARAMS error

## Impact Analysis

**Files to modify:**
- `mcp_server/tools/consolidated_tools.py` - extend manage_sheets, add manage_hierarchical_labels
- `mcp_server/server.py` - register manage_hierarchical_labels

**Pattern:**
- Follows existing consolidated tool architecture
- 8 consolidated tools → 9 consolidated tools

## Out of Scope

- Pin/label validation (core library/ERC handles this)
- Hierarchy visualization (HierarchyManager handles this)
- Netlist generation (Issue #106)
- Automatic pin positioning

## Acceptance Criteria

- [ ] manage_sheets extended with add_pin, remove_pin actions
- [ ] manage_hierarchical_labels created with add, remove actions
- [ ] All actions validate enum parameters
- [ ] All actions handle error cases
- [ ] Standardized response format
- [ ] MCP integration tests added
- [ ] Test 11 passes
- [ ] All existing tests pass
- [ ] Documentation updated

**Estimate:** 4-6 hours  
**Priority:** P0  
**Complexity:** Low (MCP wrapper only)
