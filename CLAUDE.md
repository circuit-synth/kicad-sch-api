# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

kicad-sch-api is a professional KiCAD schematic manipulation library with exact format preservation. The core focus is building robust Python library functionality before implementing MCP server integration.

## Architecture

```
kicad-sch-api/
├── kicad_sch_api/                  # Main package
│   ├── core/                       # Core schematic functionality
│   ├── collections/                # Enhanced collection classes
│   ├── geometry/                   # Geometric calculations
│   ├── library/                    # Symbol library management
│   ├── symbols/                    # Symbol caching and validation
│   ├── parsers/                    # Element parsers
│   ├── interfaces/                 # Type protocols
│   ├── discovery/                  # Component search
│   └── utils/                      # Validation and utilities
├── tests/                          # Comprehensive test suite
└── examples/                       # Usage examples
```

## Key Commands

### Development Environment Setup
```bash
# Install in development mode
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

### Testing Commands
```bash
# Run all tests (29 comprehensive tests)
uv run pytest tests/ -v

# Run format preservation tests (critical for exact KiCAD compatibility)
uv run pytest tests/reference_tests/test_against_references.py -v

# Run component removal tests (comprehensive removal functionality)
uv run pytest tests/test_*_removal.py -v

# Run specific test categories
uv run pytest tests/reference_tests/ -v     # Reference format matching
uv run pytest tests/test_component_removal.py -v  # Component removal
uv run pytest tests/test_element_removal.py -v    # Element removal

# Run tests with markers (if configured)
uv run pytest -m "format" -v          # Format preservation tests
uv run pytest -m "integration" -v     # Integration tests  
uv run pytest -m "unit" -v           # Unit tests
```

### Code Quality (ALWAYS run before commits)
```bash
# Format code
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/

# Type checking
uv run mypy kicad_sch_api/

# Linting
uv run flake8 kicad_sch_api/ tests/

# Run all quality checks
uv run black kicad_sch_api/ tests/ && \
uv run isort kicad_sch_api/ tests/ && \
uv run mypy kicad_sch_api/ && \
uv run flake8 kicad_sch_api/ tests/
```

## Core API Usage

```python
import kicad_sch_api as ksa

# Create new schematic
sch = ksa.create_schematic('My Circuit')

# Add components
resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))

# Update properties
resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
resistor.set_property('MPN', 'RC0603FR-0710KL')

# Add wires and labels
sch.wires.add(start=(100, 110), end=(150, 110))
sch.add_label("VCC", position=(125, 110))

# Bulk operations
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Remove components and elements
sch.components.remove('R1')  # Remove by reference
sch.remove_wire(wire_uuid)   # Remove by UUID
sch.remove_label(label_uuid) # Remove by UUID

# Configuration customization
ksa.config.properties.reference_y = -2.0  # Adjust label positioning
ksa.config.tolerance.position_tolerance = 0.05  # Tighter matching

# Save with exact format preservation
sch.save()
```

## Testing Strategy & Format Preservation

**CRITICAL**: This project's core differentiator is exact format preservation. Always verify output matches KiCAD exactly.

### Format Preservation Testing
```bash
# Run format preservation tests after any changes
uv run pytest tests/test_format_preservation.py -v
uv run pytest tests/test_exact_file_diff.py -v

# Test specific reference projects
uv run pytest tests/reference_tests/test_single_resistor.py -v
```

### Reference Test Schematics
Located in `tests/reference_kicad_projects/`, manually created in KiCAD:
- `single_resistor/` - Basic component test
- `two_resistors/` - Multiple components
- `resistor_divider/` - Connected circuit
- `single_wire/` - Wire routing
- `single_label/` - Text labels
- `single_hierarchical_sheet/` - Hierarchical design
- `blank_schematic/` - Empty schematic baseline

### Test Categories & Markers
```bash
# Specific test types (use pytest markers)
uv run pytest -m "format" -v      # Format preservation (CRITICAL)
uv run pytest -m "integration" -v # File I/O and round-trip validation  
uv run pytest -m "unit" -v        # Individual component functionality
uv run pytest -m "performance" -v # Large schematic performance
uv run pytest -m "validation" -v  # Error handling and validation
```

### New Feature Testing Pattern
**Standard workflow for implementing new features with exact KiCAD compatibility:**

1. **Test Planning**: Identify what needs testing and describe the test case
2. **Manual Reference Creation**: Create blank KiCAD schematic, manually add required elements
3. **Reference Analysis**: Read the manually created schematic to understand exact KiCAD format
4. **Python Implementation**: Write Python logic to generate the same output
5. **Exact Format Validation**: Ensure Python output matches manual KiCAD output byte-perfectly

**Interactive Testing Steps:**
1. Claude creates blank schematic and opens it in KiCAD
2. User manually edits schematic with required test elements
3. Claude analyzes the edited schematic as reference format
4. Claude creates unit test that generates identical output
5. Test validates both functionality and exact KiCAD format compliance

### Debugging Pattern
**Standard workflow for implementing new features:**

1. **Manual Reference Creation**: Create simple KiCAD project manually to establish expected output
2. **Logic Development**: Write Python logic to generate the same output
3. **Extensive Debug Prints**: Add lots of debug prints to understand parsing/formatting
4. **Exact Diff Validation**: Use file diff tests to ensure byte-perfect output matching

## Key Principles

1. **Exact Format Preservation**: Core differentiator for KiCAD compatibility
2. **Performance First**: Symbol caching, indexed lookups, bulk operations
3. **Professional Quality**: Comprehensive validation, error collection
4. **Foundation First**: Stable Python library that serves as foundation for MCP servers
5. **Enhanced UX**: Modern object-oriented API with pythonic interface
6. **MCP Compatibility**: Maintain stable API for external MCP servers to build upon

## Core Architecture Patterns

### S-Expression Processing
- **Parser** (`core/parser.py`): Converts KiCAD files to Python objects
- **Formatter** (`core/formatter.py`): Converts Python objects back to exact KiCAD format
- **Types** (`core/types.py`): Dataclasses for schematic elements (Point, Component, Wire, etc.)

### Component Management  
- **Schematic** (`core/schematic.py`): Main entry point, loads/saves files
- **ComponentCollection** (`core/components.py`): Enhanced collection with filtering, bulk operations
- **SymbolLibraryCache** (`library/cache.py`): Symbol lookup and caching system

### Key Design Patterns
- **Exact Format Preservation**: Every S-expression maintains original formatting
- **Object-Oriented API**: Modern Python interface with clean design  
- **Performance Optimization**: Symbol caching, indexed lookups, bulk operations
- **Professional Validation**: Comprehensive error collection and reporting

## Claude Code Configuration

This project includes a `.claude/settings.json` file that configures Claude Code for optimal development:

- **Default Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Automated Hooks**:
  - Format preservation tests run after code changes
  - Code quality checks on Python file modifications

The configuration enforces the project's core requirements automatically.

## Dependencies

- **sexpdata**: S-expression parsing library
- **typing-extensions**: Type hint support for older Python versions
- **uv**: Primary package and environment manager (NOT pip/venv)

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

**⚠️ CRITICAL**: All development work MUST follow the memory bank workflow to maintain project context and decision history. Claude Code instances have not been following these instructions consistently - this MUST be enforced.

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

## MCP Server Compatibility

This library is designed as a stable foundation for MCP servers. Key compatibility requirements:

### API Stability
- **Public API**: All documented APIs are considered stable and maintained for backward compatibility
- **Version Compatibility**: MCP servers should specify minimum required version (e.g., `kicad-sch-api>=0.2.0`)
- **Error Handling**: Consistent exception handling for MCP servers to wrap and translate errors

### MCP Server Integration Pattern
```python
# Standard pattern for MCP servers
import kicad_sch_api as ksa

@mcp_tool
async def create_schematic(name: str):
    try:
        sch = ksa.create_schematic(name)
        return success_response(f"Created schematic: {name}")
    except Exception as e:
        return error_response(f"Error creating schematic: {e}")
```

### Related MCP Servers
- **[mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)**: Reference implementation using standard MCP SDK

## Version Management & Release Guidelines

### Version Increment Rules
- **DEFAULT**: Always use patch/subminor version increments (0.0.1) unless explicitly instructed otherwise
- **Patch increments (0.2.0 → 0.2.1)**: Bug fixes, small improvements, additional tests
- **Minor increments (0.2.0 → 0.3.0)**: New features, API additions, significant improvements
- **Major increments (0.2.0 → 1.0.0)**: Breaking changes, major API redesigns

### Release Process Rules
- **NEVER commit or push without explicit user instructions**
- **NEVER publish to PyPI without specific user authorization**
- **ALWAYS ask before version increments** - default to patch/subminor (0.0.1)
- **ALWAYS verify version intention** before building packages

### Example Version Decision Process:
```
User: "Add component removal feature"
Claude: "This adds new functionality. Should I increment:
- Patch version (0.2.0 → 0.2.1) for incremental improvement?  
- Minor version (0.2.0 → 0.3.0) for significant new feature?
Default: patch version unless specified otherwise."
```

## Related Projects

- **circuit-synth**: Parent project and source of transferred logic

---

*This project provides professional KiCAD schematic manipulation with development memory management.*