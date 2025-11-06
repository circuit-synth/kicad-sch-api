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

You should see 7 tools:
- `get_component_pins`
- `find_pins_by_name`
- `find_pins_by_type`
- `create_schematic`
- `load_schematic`
- `save_schematic`
- `get_schematic_info`

## Example Usage

Once configured, you can ask Claude to:

```
Create a new schematic called "TestCircuit" and add a 10k resistor at position (100, 100), then get its pin information.
```

Claude will use the MCP tools to:
1. Call `create_schematic("TestCircuit")`
2. Add the component via the library API
3. Call `get_component_pins("R1")` to retrieve pin data

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

- **Create circuits**: "Create a voltage divider with two 10k resistors"
- **Analyze schematics**: "Load my schematic and tell me about the components"
- **Find pins**: "Find all the power input pins in component U1"
- **Discover pins by pattern**: "Find all pins with CLK in the name"
- **Save work**: "Save this schematic to ~/Desktop/my_circuit.kicad_sch"

The MCP server gives Claude full access to create and manipulate KiCAD schematics!
