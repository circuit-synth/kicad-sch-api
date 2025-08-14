# CLAUDE.md - kicad-sch-api

This file provides guidance to Claude Code when working on the kicad-sch-api project.

## Project Overview

kicad-sch-api is a professional KiCAD schematic manipulation library with exact format preservation and AI agent integration via MCP server.

## Architecture

```
kicad-sch-api/
├── python/                          # Core Python library
│   ├── kicad_sch_api/              # Main package
│   │   ├── core/                   # Core schematic functionality
│   │   ├── library/                # Symbol library management
│   │   ├── mcp/                    # MCP server interface
│   │   └── utils/                  # Validation and utilities
│   └── tests/                      # Comprehensive test suite
├── mcp-server/                     # TypeScript MCP server
└── submodules/kicad-skip/          # Foundation library
```

## Key Commands

### Development
```bash
# Install in development mode
uv pip install -e .

# Run tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_component_management.py::TestComponentManagement::test_component_creation_and_access -v

# Format code
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/
```

### MCP Server
```bash
# Build MCP server
cd mcp-server
npm install
npm run build

# Start MCP server
npm start
```

## Core API Usage

```python
import kicad_sch_api as ksa

# Load schematic
sch = ksa.load_schematic('circuit.kicad_sch')

# Add components
resistor = sch.components.add('Device:R', ref='R1', value='10k', pos=(100, 100))

# Update properties
resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
resistor.set_property('MPN', 'RC0603FR-0710KL')

# Bulk operations
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Save with exact format preservation
sch.save()
```

## Testing Strategy

### Reference Schematics
Create test schematics in `tests/reference_kicad_projects/` covering:
- Basic components (R, L, C, D)
- Labels (local, global, hierarchical)
- Hierarchical sheets
- Complex components (ESP32, USB-C, multi-unit ICs)
- Graphics and text elements

### Test Categories
- **Unit tests**: Individual component functionality
- **Integration tests**: File I/O and round-trip validation
- **Format preservation**: Exact output matching KiCAD
- **Performance tests**: Large schematics, bulk operations
- **MCP tests**: AI agent integration

## Key Principles

1. **Exact Format Preservation**: Core differentiator from kicad-skip
2. **Performance First**: Symbol caching, indexed lookups, bulk operations
3. **Professional Quality**: Comprehensive validation, error collection
4. **AI-Ready**: Native MCP integration for agent workflows
5. **Enhanced UX**: Modern object-oriented API vs kicad-skip's verbose interface

## Dependencies

- **sexpdata**: S-expression parsing foundation
- **typing-extensions**: Type hint support for older Python
- **pytest**: Testing framework
- **uv**: Package and environment management

## Memory Bank System

This repository uses a **Code Memory Bank** system to maintain persistent development context and knowledge across sessions.

### Memory Bank Structure

The `.memory_bank/` directory contains:

- **activeContext.md**: Current development session state and focus areas
- **decisionLog.md**: Technical decisions, trade-offs, and architectural choices (ADR format)
- **productContext.md**: Project overview, value proposition, and target users
- **progress.md**: Completed milestones, current tasks, and next priorities
- **features/**: PRDs for planned features (create directory as needed)

### Memory Bank Usage - REQUIRED WORKFLOW

**⚠️ IMPORTANT**: All development work MUST follow the memory bank workflow to maintain project context and decision history.

#### Before Starting Any Work:
1. **Read existing context**: Review `.memory_bank/` files to understand current state
2. **Update active context**: Document what you're working on and why
3. **Check decision log**: Ensure new work aligns with previous architectural decisions

#### For New Features:
1. **Write PRD**: Create Product Requirements Document in `.memory_bank/features/`
2. **Update decision log**: Document architectural choices and trade-offs
3. **Update progress**: Track milestones and implementation status

#### Memory Bank Commands:
```bash
# REQUIRED: Update memory bank after any significant work
/umb

# Query past decisions and context
# Example: "What decisions were made about S-expression parsing?"
```

#### Memory Bank Structure:
- **activeContext.md**: Current session state, focus areas, active files
- **decisionLog.md**: All architectural decisions with rationale (ADR format)
- **productContext.md**: Project overview, value proposition, target users
- **progress.md**: Milestones, current tasks, success metrics
- **features/**: PRDs for planned features (create directory as needed)

#### Required Workflow Pattern:
1. **Before coding**: Read memory bank context, write feature PRD
2. **During development**: Update active context with current work
3. **After completing work**: Update decision log and progress
4. **Use /umb command**: Update memory bank before ending session

This ensures continuity of development decisions and maintains institutional knowledge across all AI development sessions.

## Related Projects

- **circuit-synth**: Parent project and source of transferred logic
- **kicad-skip**: Foundation library for S-expression parsing

---

*This project significantly enhances kicad-skip with professional features and development memory management.*