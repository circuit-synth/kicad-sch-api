# KiCAD Schematic MCP Server Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
uv add "mcp[cli]>=1.0.0" "fastmcp>=2.0.0"
```

### 2. Test the Server
```bash
python3 test_mcp.py
```

### 3. Run the MCP Server
```bash
python3 run_mcp_server.py
```

### 4. Configure Claude Desktop (Claude Code)

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "python3",
      "args": [
        "/Users/shanemattner/Desktop/kicad-sch-api/run_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/shanemattner/Desktop/kicad-sch-api"
      }
    }
  }
}
```

**Important**: Update the paths to match your actual directory location.

## Available Tools

### Schematic Management
- `create_schematic(name)` - Create new schematic
- `load_schematic(file_path)` - Load existing schematic  
- `save_schematic(file_path)` - Save current schematic
- `get_schematic_info()` - Get current schematic information

### Component Operations
- `add_component(lib_id, reference, value, position)` - Add component
- `list_components()` - List all components

### Connection Operations  
- `add_wire(start_pos, end_pos)` - Add wire connection

### Resources
- `schematic://current` - Current schematic state

## Example Usage

Ask Claude:

> "Create a new schematic called 'Power Supply', add a voltage regulator at position (100, 100) with reference U1, and add some decoupling capacitors"

The MCP server will:
1. Create the schematic
2. Add the components using your existing kicad-sch-api
3. Maintain state for multiple operations
4. Preserve exact KiCAD formatting

## Features

✅ **Stateful Operations**: Keep schematic in memory for multiple edits  
✅ **Format Preservation**: Uses your existing API with exact KiCAD compatibility  
✅ **Error Handling**: Detailed error messages for AI agents  
✅ **Type Safety**: Full type hints and validation  
✅ **Professional Logging**: Proper stderr logging for MCP STDIO transport  

## Basic Test Results

```
✅ Create schematic: SUCCESS
✅ Add component: SUCCESS  
✅ List components: SUCCESS
✅ Schematic info: SUCCESS
```

Ready for AI-driven schematic creation!