# Changelog

All notable changes to kicad-sch-api will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Pin-Aligned Component Placement** (#137) - Revolutionary new API for placing components by pin position
  - `add_with_pin_at()`: Add components positioned by specific pin location instead of component center
    - Eliminates manual pin offset calculations
    - Perfect for horizontal signal flows (filters, amplifiers, signal chains)
    - Works with all rotations (0°, 90°, 180°, 270°)
    - Automatic grid snapping to 1.27mm KiCAD grid
    - Example: `sch.components.add_with_pin_at('Device:R', '2', (150, 100), value='10k')`

  - `align_pin()`: Move existing components to align specific pins
    - Maintains component rotation
    - Useful for cleaning up existing schematics
    - Example: `component.align_pin('2', (200, 100))`

  - `calculate_position_for_pin()`: Low-level helper for custom placement logic
    - Inverse operation of `get_pin_position()`
    - Handles all rotation transformations
    - Grid snapping support

  - **Testing**: 18 comprehensive tests (100% passing)
    - Unit tests for all rotation angles
    - Integration tests for voltage dividers, RC filters
    - Real-world circuit validation

  - **Documentation**:
    - Comprehensive example file: `examples/pin_aligned_placement.py` (6 examples)
    - Updated `/user:generate-circuit` slash command to use new API
    - Full API documentation in docstrings

  - **Impact**:
    - 66% code reduction for horizontal signal flows
    - Eliminates 51 lines of complex verification code from slash commands
    - Perfect alignment guaranteed (<0.001mm error)
    - Makes autonomous circuit generation significantly easier

- **MCP Server Integration** - Complete Model Context Protocol server for AI agents
  - FastMCP 2.0 framework with STDIO transport
  - Entry point: `kicad-sch-mcp` command for Claude Desktop integration
  - Global schematic state management for MCP tools

- **Pin Discovery MCP Tools** (`mcp_server/tools/pin_discovery.py`)
  - `get_component_pins`: Get all pins with positions, types, and metadata
  - `find_pins_by_name`: Semantic lookup with wildcard support (*, CLK*, *IN*)
  - `find_pins_by_type`: Filter by electrical type (passive, input, output, power_in, etc.)
  - Progress reporting via MCP Context
  - Comprehensive error handling (NO_SCHEMATIC_LOADED, COMPONENT_NOT_FOUND, VALIDATION_ERROR)

- **Schematic Management MCP Tools** (`mcp_server/server.py`)
  - `create_schematic`: Create new blank KiCAD schematics
  - `load_schematic`: Load existing .kicad_sch files with validation
  - `save_schematic`: Save schematics to disk with optional path
  - `get_schematic_info`: Query metadata about loaded schematic

- **Component Management MCP Tools** (`mcp_server/tools/component_tools.py`)
  - `add_component`: Add components to schematics with comprehensive options
    - Auto-reference generation if not specified
    - Auto-positioning if position not provided
    - Rotation support (0, 90, 180, 270 degrees)
    - Footprint specification
    - Full validation and error handling
  - `list_components`: List all components with complete metadata
  - `update_component`: Update component properties (value, position, rotation, footprint)
  - `remove_component`: Remove components from schematic
  - `filter_components`: Advanced filtering by lib_id, value, footprint
    - Exact match and pattern matching support
    - AND logic for multiple criteria

- **Connectivity MCP Tools** (`mcp_server/tools/connectivity_tools.py`)
  - `add_wire`: Add wire connections between points
    - Horizontal and vertical wire support
    - UUID tracking for wire management
  - `add_label`: Add net labels to establish logical connections
    - Rotation support (0, 90, 180, 270)
    - Custom text size
    - Net naming for non-physical connections
  - `add_junction`: Add wire junctions for T-connections
    - Custom diameter support
    - Required for proper wire branching

- **Pydantic Models** (`mcp_server/models.py`)
  - Type-safe data models for all MCP responses
  - `PointModel`, `PinInfoOutput`, `ComponentPinsOutput`, `ComponentInfoOutput`, `ErrorOutput`
  - Updated to Pydantic v2 standards (ConfigDict)
  - Comprehensive field validation and examples

- **MCP Server Testing**
  - 49 comprehensive integration tests (all passing)
  - Component management: 20 tests
  - Connectivity: 10 tests
  - Pin discovery: 11 tests
  - Schematic management: 4 tests
  - Workflow & performance: 4 tests
  - End-to-end workflow tests
  - Performance validation (<50ms response times)
  - Error handling coverage for all failure modes

- **MCP Documentation** - Comprehensive documentation for MCP server
  - Enhanced `MCP_SETUP_GUIDE.md` with detailed tool reference
  - Created `docs/MCP_EXAMPLES.md` with complete usage examples
    - Basic component operations
    - Complete circuit examples (voltage divider, LED circuit, RC filter)
    - Advanced pin discovery patterns
    - Batch operations and common patterns
    - Troubleshooting guide
  - Updated `README.md` with verified working examples
  - Common library IDs reference
  - KiCAD coordinate system explanation
  - Grid alignment best practices

### Changed
- **Dependencies**
  - Added `mcp>=1.10.0` (Model Context Protocol SDK)
  - Added `fastmcp>=0.2.0` (FastMCP server framework)
  - Added `pytest-asyncio>=0.21.0` (async test support)

- **Package Configuration**
  - Added `mcp_server*` to setuptools packages
  - Added `kicad-sch-mcp` entry point script
  - MCP server now properly packaged with library

### Performance
- Pin discovery operations: 4.32ms average (10x faster than 50ms requirement)
- All MCP operations complete in <50ms
- Efficient symbol caching and indexed lookups
- Component iteration and filtering optimized
- Wire and label creation near-instant

### Circuit Building Capabilities
The MCP server now enables complete programmatic circuit construction:
- **Component Management**: Add, list, update, remove, and filter components
- **Connectivity**: Create wire connections, net labels, and junctions
- **Pin Discovery**: Find pins by name, type, or get complete pin information
- **Schematic Management**: Create, load, save, and query schematics

This represents a complete P0 (priority 0) implementation for AI-powered
circuit design via Model Context Protocol.

## [0.5.0] - 2025-11-06

### Added
- **Enhanced Collection Architecture** - Complete rewrite of element collection system
  - `BaseCollection[T]`: Abstract base class for all collections
  - `IndexRegistry`: Centralized lazy index management with declarative specs
  - `PropertyDict`: Auto-tracking dictionary for modification detection
  - `ValidationLevel`: Enum for configurable validation strictness (NONE → PARANOID)
  - **Batch Mode**: Context manager for deferred index rebuilding (100x speedup)
  - Full generic type support with `Generic[T]` for type safety

- **ComponentCollection Enhancements**
  - Dual index strategy: UUID/reference via IndexRegistry, lib_id/value manual indexes
  - `filter(**criteria)`: Flexible filtering with multiple criteria
  - `bulk_update()`: Batch update operations with automatic index maintenance
  - Component wrapper class with validated property setters
  - Grid snapping and rotation validation

- **New Collection Implementations**
  - `LabelCollection`: Text and position indexing with `LabelElement` wrapper
  - `WireCollection`: Endpoint indexing and geometry queries (horizontal/vertical)
  - `JunctionCollection`: Position-based queries with tolerance matching

- **Performance Optimizations**
  - O(1) lookups via IndexRegistry for UUID and reference
  - Lazy index rebuilding: mark dirty → rebuild on access
  - Batch mode prevents redundant index rebuilds
  - Single rebuild after bulk operations

### Changed
- **API Consistency Improvements**
  - `sch.components.get_by_reference("R1")` → `sch.components.get("R1")`
  - `sch.components.get_by_lib_id("Device:R")` → `sch.components.filter(lib_id="Device:R")`
  - `sch.components.get_by_value("10k")` → `sch.components.filter(value="10k")`
  - `LabelCollection.add()` now returns `LabelElement` wrapper (was UUID string)
  - `ComponentCollection.add()` returns `Component` wrapper for direct property access

- **Schematic Integration**
  - Updated `Schematic` class to use new collection architecture
  - Consistent `.modified` property across all collections
  - Unified `.mark_saved()` method for all collections

### Documentation
- Added comprehensive `docs/COLLECTIONS.md` with architecture details
- Migration guide for API changes
- Performance characteristics and benchmarks
- Best practices for batch operations
- Complete examples for all collection types

### Testing
- 83/83 collection tests passing (100%)
- 435/437 unit tests passing (99.5%)
- BaseCollection infrastructure: 49 tests
- ComponentCollection: 34 tests
- Full integration with existing test suite

### Internal
- Migrated from dual collection architecture to unified BaseCollection system
- Preserved backward compatibility where possible
- Legacy collections in `core/` preserved but deprecated

## [0.4.1] - 2025-01-26

### Added
- **KiCad CLI Wrappers with Docker Fallback** - Comprehensive wrapper module for kicad-cli commands
  - Netlist export supporting 8 formats (kicadsexpr, kicadxml, spice, spicemodel, cadstar, orcadpcb2, pads, allegro)
  - Bill of Materials (BOM) export with extensive customization options
  - Electrical Rule Check (ERC) validation with structured violation reporting
  - PDF/SVG/DXF documentation exports
  - Automatic detection and fallback: local kicad-cli → Docker container
  - Environment variable configuration (KICAD_CLI_MODE, KICAD_DOCKER_IMAGE)
- **Schematic Export Methods** - Six new convenience methods on Schematic class:
  - `run_erc()` - Electrical Rule Check validation
  - `export_netlist()` - Netlist export
  - `export_bom()` - Bill of Materials export
  - `export_pdf()` - PDF documentation
  - `export_svg()` - SVG graphics
  - `export_dxf()` - DXF for CAD integration
- **Comprehensive Test Suite** - 58 new tests for CLI functionality
  - 48 unit tests with mocks for fast execution
  - 10 integration tests with real schematics
  - Automatic skip if KiCad unavailable

### Documentation
- Added comprehensive CLI module README with usage examples
- Added example script demonstrating all export capabilities
- Updated API documentation with export method signatures

### Fixed
- CLI integration test variable reference bug

### Closes
- Issue #33: Netlist generation
- Issue #34: BOM generation

## [0.4.0] - 2025-01-24

### Added
- Enhanced `/publish-pypi` command with mandatory version parameter
- Automatic git tagging on release
- GitHub release creation
- Version validation and confirmation prompts

### Changed
- Improved release process consistency
- Better error handling in PyPI publishing

### Closes
- Issue #3: Establish consistent release process
- Issue #4: Enhance /publish-pypi command

## [0.3.2] - 2025-01-20

### Added
- Electrical Rules Check (ERC) validation module
- Comprehensive ERC test suite
- ERC documentation and user guide

### Documentation
- Added ERC User Guide
- Integrated ERC documentation into ReadTheDocs
- Added ReadTheDocs badge to README

## [0.3.0] - 2025-01-15

### Added
- Component removal functionality
- Element removal (wires, labels, hierarchical sheets)
- Enhanced collection classes with removal methods
- Comprehensive removal test suite

### Changed
- Improved validation and error reporting

## [0.2.0] - 2025-01-10

### Added
- Initial release with core schematic manipulation
- S-expression parsing and formatting
- Component management with collections
- Wire operations and connectivity
- Symbol library caching
- Format preservation guarantees
- Comprehensive test suite with reference projects

### Documentation
- Initial documentation and examples
- API reference
- Quick start guide

[0.5.0]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.3.0...v0.3.2
[0.3.0]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/circuit-synth/kicad-sch-api/releases/tag/v0.2.0
