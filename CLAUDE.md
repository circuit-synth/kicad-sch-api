# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

kicad-sch-api is a Python library for reading and writing KiCAD schematic files. The core focus is **exact format preservation** and **simple API design**.

**Key Principle**: "Simple is my north star" - prioritize simplicity over features.

## CRITICAL: KiCAD Coordinate System ⚠️

### 🔴 THE MOST IMPORTANT CONCEPT IN THIS LIBRARY

**KiCAD uses TWO DIFFERENT coordinate systems**, and understanding this is CRITICAL for ALL pin position calculations, connectivity analysis, and component placement.

### The Two Coordinate Systems

#### 1. Symbol Space (Library Definitions)
**Uses NORMAL Y-axis (+Y is UP)** like standard mathematics:
- All KiCAD symbol libraries define pins in this coordinate system
- Pin 1 at `(0, 3.81)` means 3.81mm UPWARD from origin
- Pin 2 at `(0, -3.81)` means 3.81mm DOWNWARD from origin

#### 2. Schematic Space (Placed Components)
**Uses INVERTED Y-axis (+Y is DOWN)** like most computer graphics:
- **Lower Y values** = visually HIGHER on screen (top)
- **Higher Y values** = visually LOWER on screen (bottom)
- **X-axis is normal** (increases to the right)

### The Critical Transformation

**When placing a symbol on a schematic, Y coordinates MUST be negated:**

```python
# Symbol library defines (NORMAL Y-axis, +Y up):
Pin 1: (0, +3.81)   # 3.81mm UPWARD in symbol space
Pin 2: (0, -3.81)   # 3.81mm DOWNWARD in symbol space

# Component placed at (100, 100) in schematic (INVERTED Y-axis, +Y down):
# Y must be NEGATED during transformation:
Pin 1: (100, 100 + (-3.81)) = (100, 96.52)   # VISUALLY AT TOP (lower Y)
Pin 2: (100, 100 + (+3.81)) = (100, 103.81)  # VISUALLY AT BOTTOM (higher Y)
```

### Implementation Location

**File:** `kicad_sch_api/core/geometry.py:apply_transformation()`

```python
def apply_transformation(point, origin, rotation, mirror):
    x, y = point

    # CRITICAL: Negate Y to convert from symbol space (normal Y) to schematic space (inverted Y)
    # This MUST happen BEFORE rotation/mirroring
    y = -y
    logger.debug(f"After Y-axis inversion (symbol→schematic): ({x}, {y})")

    # Then apply mirroring and rotation...
```

**This single line (`y = -y`) is CRITICAL** - without it, all pin positions are swapped and connectivity analysis breaks.

### Why This Matters - Real Impact

**Without this transformation, the library had a catastrophic bug:**
- ❌ All pin numbers were swapped (pin 1 calculated at bottom, pin 2 at top)
- ❌ All connectivity analysis was broken
- ❌ Wire routing connected to wrong pins
- ❌ Hierarchical connections failed
- ❌ Netlist generation was incorrect

**With this transformation:**
- ✅ Pin positions match KiCAD exactly
- ✅ Connectivity analysis works correctly
- ✅ Wire routing connects to correct pins
- ✅ Hierarchical connections work
- ✅ Netlist matches `kicad-cli` output

### Discovery Timeline

This was discovered during hierarchical connectivity implementation:
1. Initial implementation had pins swapped
2. User pointed out: "pin 2 is a higher number than pin 1, but pin 1 is at top"
3. Root cause: Symbol libraries use normal Y-axis, schematics use inverted Y-axis
4. Fix: Add Y negation BEFORE rotation/mirroring
5. Result: All 11 hierarchical connectivity tests pass + all pin rotation tests pass

### Testing Coverage

**Tested by:**
- `tests/unit/test_pin_rotation.py` - 11 tests for pin positions at all rotations
- `tests/reference_tests/test_pin_rotation_*.py` - 8 reference tests against real KiCAD schematics
- `tests/unit/test_connectivity_ps2_hierarchical.py` - 11 tests for hierarchical connections
- All tests verify pin positions match `kicad-cli` netlist output

### When Working with Pin Positions

**ALWAYS remember:**
- Pin positions from `list_component_pins()` are in SCHEMATIC space (inverted Y)
- Lower Y = visually HIGHER on screen (top of component)
- Higher Y = visually LOWER on screen (bottom of component)

**Example with resistor at position (100, 100) with rotation=0:**
```python
# Pin positions returned by list_component_pins():
Pin 1: (100, 96.52)   # Lower Y = VISUALLY AT TOP ⬆️
Pin 2: (100, 103.81)  # Higher Y = VISUALLY AT BOTTOM ⬇️
```

### Grid Alignment

**ALL positions in KiCAD schematics MUST be grid-aligned:**

- **Default grid:** 1.27mm (50 mil) - the standard KiCAD schematic grid
- **Component positions** must be on grid
- **Wire endpoints** must be on grid
- **Pin positions** must be on grid
- **Label positions** should be on grid
- **Sheet boundaries** should be on grid-aligned rectangles
- **Junction positions** must be on grid

**Common grid-aligned values (in mm):**
```
0.00, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, 8.89, 10.16, ...
```

**When creating components programmatically:**
- Always use grid-aligned coordinates
- Round positions to nearest 1.27mm increment
- Verify pin positions align to grid after transformations

**Example - Grid-aligned component placement:**
```python
# Good - on grid
sch.components.add('Device:R', 'R1', '10k', position=(100.33, 101.60))

# Bad - off grid
sch.components.add('Device:R', 'R2', '10k', position=(100.5, 101.3))
```

**Why grid alignment matters:**
- Ensures proper electrical connectivity
- Maintains clean schematic appearance
- Prevents connectivity issues from floating-point errors
- Matches KiCAD's internal connection detection
- Required for proper ERC (Electrical Rule Check)

This is critical for:
- Wire routing and connectivity
- Component placement
- Pin position calculations
- Visual layout understanding
- Electrical connectivity detection

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

## Library Configuration

### Symbol Library Path Discovery

The library automatically discovers KiCAD symbol libraries (`.kicad_sym` files) using environment variables and system paths.

**Common Issue**: Users report "Library not found" or "Symbol not found" errors when creating components.

**Root Cause**: Library cannot find KiCAD symbol library files.

**Solution**: Configure environment variables to point to KiCAD symbol directories.

### Environment Variables (Recommended)

The library checks these environment variables in order:
- `KICAD_SYMBOL_DIR` - Generic, works for any version
- `KICAD9_SYMBOL_DIR` - KiCAD 9 specific
- `KICAD8_SYMBOL_DIR` - KiCAD 8 specific
- `KICAD7_SYMBOL_DIR` - KiCAD 7 specific

**macOS:**
```bash
export KICAD8_SYMBOL_DIR=/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols/
```

**Linux:**
```bash
export KICAD8_SYMBOL_DIR=/usr/share/kicad/8.0/symbols/
```

**Windows:**
```powershell
$env:KICAD8_SYMBOL_DIR="C:\Program Files\KiCad\8.0\share\kicad\symbols"
```

### Programmatic Configuration

Alternatively, add library paths in code:

```python
import kicad_sch_api as ksa

cache = ksa.SymbolLibraryCache()
cache.add_library_path("/custom/path/to/symbols")
cache.discover_libraries()

# Now create schematics
sch = ksa.create_schematic("MyCircuit")
```

### Verification

Test library discovery:

```python
import kicad_sch_api as ksa

cache = ksa.SymbolLibraryCache(enable_persistence=False)
lib_count = cache.discover_libraries()

print(f"Discovered {lib_count} libraries")

# Test loading a symbol
symbol = cache.get_symbol("Device:R")
if symbol:
    print("✓ Symbol library working")
else:
    print("✗ Check environment variables")
```

### Troubleshooting

If users report library errors:
1. Check environment variables are set correctly
2. Verify paths contain `.kicad_sym` files
3. Test with simple script (see above)
4. See `docs/LIBRARY_CONFIGURATION.md` for complete guide
5. Use `/troubleshoot-library` command for interactive help

### When to Help Users with Library Setup

- User reports "library not found" errors
- Component creation fails with symbol errors
- User has non-standard KiCAD installation
- User needs custom library paths
- First-time setup on new machine

## Creating Hierarchical Schematics (Issue #100)

**CRITICAL**: For hierarchical designs, child schematics MUST have proper hierarchy context set using `set_hierarchy_context()` or component references will show as "?" in KiCad.

### Quick Example

```python
import kicad_sch_api as ksa

# 1. Create parent schematic
main = ksa.create_schematic("MyProject")
parent_uuid = main.uuid

# 2. Add hierarchical sheet
power_sheet_uuid = main.sheets.add_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(50, 50),
    size=(100, 100),
    project_name="MyProject"  # MUST match parent project name!
)

# 3. Create child schematic with hierarchy context
power = ksa.create_schematic("MyProject")  # SAME project name!
power.set_hierarchy_context(parent_uuid, power_sheet_uuid)  # CRITICAL!

# 4. Now components get correct hierarchical paths automatically
vreg = power.components.add('Regulator_Linear:AMS1117-3.3', 'U1', 'AMS1117-3.3')
# Component path will be: /parent_uuid/power_sheet_uuid (CORRECT!)

# 5. Save both schematics
main.save("main.kicad_sch")
power.save("power.kicad_sch")
```

### Critical Requirements for Hierarchical Schematics

1. **Same Project Name**: All schematics (parent + children) MUST use identical project names
2. **Call `set_hierarchy_context()` BEFORE adding components**
3. **Pass `project_name` parameter to `add_sheet()`**
4. **Save parent UUID early** for use when creating children

### Without vs With Hierarchy Context

**❌ Without `set_hierarchy_context()`:**
- Component instance path: `/child_uuid` (WRONG)
- KiCad displays: "C?", "R?", "U?" instead of proper references
- Components cannot be annotated

**✅ With `set_hierarchy_context()`:**
- Component instance path: `/parent_uuid/sheet_uuid` (CORRECT)
- KiCad displays: "C1", "C2", "R1", "U1" (proper references)
- Components annotate correctly

### Complete Example

See **`docs/HIERARCHY_FEATURES.md`** for comprehensive hierarchical schematic documentation and **`examples/parametric_circuit_demo.py`** for a complete working example.

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

### Interactive Reference Testing Strategy ⭐
**This is the PROVEN strategy from pin rotation (PR #91) - USE THIS!**

This collaborative approach ensures our API generates exact KiCad-compatible output:

#### Step 1: Claude Creates Blank Schematic
```python
# Claude creates blank reference schematic
import kicad_sch_api as ksa
sch = ksa.create_schematic("Reference Test")
sch.save("tests/reference_kicad_projects/feature_name/test.kicad_sch")
```
```bash
# Claude opens it for user
open tests/reference_kicad_projects/feature_name/test.kicad_sch
```

#### Step 2: User Manually Adds Elements in KiCad
- User adds the element(s) being tested (label, junction, etc.)
- User positions elements, sets properties
- User saves schematic (Ctrl+S)
- User tells Claude: "done" or "saved"

#### Step 3: Claude Analyzes KiCad Format
```python
# Claude reads the manually created reference
sch = ksa.Schematic.load("tests/reference_kicad_projects/feature_name/test.kicad_sch")

# Extract exact positions, properties, format
for element in sch.labels:  # or junctions, etc.
    print(f"Position: {element.position}")
    print(f"Properties: {element.properties}")
    # Understand exact KiCad S-expression format
```

#### Step 4: Claude Creates Unit Tests
```python
class TestFeature:
    def test_feature_creation(self, schematic):
        """Test creating feature programmatically."""
        element = schematic.add_feature(...)
        assert element.property == expected_value

    def test_feature_matches_kicad_reference(self):
        """Verify against manually created KiCad reference."""
        sch = ksa.Schematic.load("tests/reference_kicad_projects/feature_name/test.kicad_sch")
        element = get_element(sch)

        # Verify exact positions match KiCad
        assert element.position.x == expected_x
        assert element.position.y == expected_y
```

#### Step 5: Verify Exact Format Match
- Run tests: `uv run pytest tests/unit/test_feature.py -v`
- Run reference tests: `uv run pytest tests/reference_tests/test_feature_reference.py -v`
- Verify outputs match KiCad exactly

#### Success Example: Pin Rotation (PR #91)
This strategy was used to implement pin position rotation transformation:
- 4 reference schematics created (0°, 90°, 180°, 270°)
- 19 tests created (11 unit + 8 reference)
- All tests verified against real KiCad wire endpoints
- 100% format compatibility achieved

**Key Benefits:**
- ✅ Ensures exact KiCad compatibility (not guessing format)
- ✅ Reference schematics serve as regression tests
- ✅ User validation confirms correctness
- ✅ Fast iteration cycle (create → test → verify)
- ✅ Documents expected behavior with real examples

### Debugging Pattern
**Standard workflow for implementing new features:**

1. **Manual Reference Creation**: Create simple KiCAD project manually to establish expected output
2. **Logic Development**: Write Python logic to generate the same output
3. **Extensive Debug Prints**: Add lots of debug prints to understand parsing/formatting
4. **Exact Diff Validation**: Use file diff tests to ensure byte-perfect output matching

## Key Principles

1. **Exact Format Preservation**: Core differentiator for KiCAD compatibility
2. **Performance First**: Symbol caching, indexed lookups, bulk operations
3. **Simple API Design**: "Simple is my north star" - prioritize simplicity
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
- **Comprehensive Validation**: Error collection and reporting

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

## Architecture Decision Records (ADR)

Architectural decisions and technical rationale are documented in `docs/ADR.md`. This file contains:

- **ADR-001**: S-expression Foundation with Enhanced API
- **ADR-002**: Component-Centric API Design
- **ADR-003**: Format Preservation Strategy
- **ADR-004**: Testing Strategy with Reference Schematics
- **ADR-005**: Performance Optimization Approach
- **Technology Choices**: Python, sexpdata, pytest decisions
- **Integration Patterns**: MCP Server architecture, error handling

See `docs/ADR.md` for the complete decision history and architectural guidance.

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

## Commit Message Guidelines

### Format Requirements

**Always use conventional commit format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code changes that neither fix bugs nor add features
- `perf:` Performance improvements
- `chore:` Build process, dependencies, tooling

**Examples of GOOD commit messages:**
```
feat(components): Add component removal by reference

Implement ComponentCollection.remove() method to remove components
by reference designator. Updates all associated connectivity data.

Closes #42
```

```
fix(geometry): Correct Y-axis transformation in pin positions

Pin positions were inverted due to missing Y-axis negation when
converting from symbol space to schematic space. Added y = -y
transformation before rotation/mirroring.

Fixes #91
```

```
docs: Update README with simpler API examples

Remove marketing language and replace with technical descriptions.
Focus on "simple is my north star" principle.
```

**Examples of BAD commit messages:**
```
❌ "update stuff"
❌ "fix bug"
❌ "wip"
❌ "changes"
❌ "🚀 Add awesome new feature!!!"
```

### Subject Line Rules

- Use imperative mood ("Add feature" not "Added feature" or "Adds feature")
- No period at the end
- Keep under 72 characters
- Be specific and descriptive
- NO emojis in commit messages
- NO marketing language ("professional", "seamless", etc.)

### Body Guidelines

- Explain WHAT changed and WHY (not HOW - code shows that)
- Reference issues/PRs when relevant
- Use bullet points for multiple changes
- Keep lines under 72 characters

## Related Projects

- **circuit-synth**: Original project that this library was extracted from
- **mcp-kicad-sch-api**: MCP server implementation using this library

---

*This project provides simple, tested KiCAD schematic manipulation with exact format preservation.*
