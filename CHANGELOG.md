# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-10-12

### Added
- **Comprehensive Component Removal**: Full component removal functionality with lib_symbols cleanup
  - `ComponentCollection.remove()` method for removing components by reference
  - Automatic lib_symbols synchronization to remove unused symbol definitions
  - Complete test suite with 4 dedicated removal tests

- **Element Removal Operations**: Removal support for all schematic elements
  - Wire removal via `Schematic.remove_wire()` and `WireCollection.remove()`
  - Label removal via `Schematic.remove_label()`
  - Hierarchical label removal via `Schematic.remove_hierarchical_label()`
  - Junction removal via `JunctionCollection.remove()`
  - 5 comprehensive element removal tests

- **Professional Configuration System**: Centralized configuration management
  - `KiCADConfig` class with structured configuration categories
  - Property positioning, grid settings, sheet settings, and tolerance configuration
  - Configurable via public `ksa.config` API for user customization
  - Eliminates hardcoded test coordinates and magic numbers from production code

- **Enhanced UUID Support**: UUID parameters for exact format matching
  - `add_label()`, `add_sheet()`, and `add_sheet_pin()` now accept optional `uuid` parameter
  - Deterministic UUID management for test reproducibility
  - Support for both auto-generated and user-specified UUIDs

### Fixed
- **Pin Electrical Type Formatting**: Added missing pin electrical types to prevent incorrect quoting
  - Added support for `no_connect`, `open_collector`, `open_emitter`, and `free` pin types
  - Prevents these types from being incorrectly quoted in S-expression output
  - Fixes KiCAD schematic opening error: "Expecting 'input, output, ... no_connect'"
  - All pin types now correctly formatted as unquoted symbols per KiCAD specification

- **Format Preservation**: Achieved byte-for-byte compatibility with KiCAD reference files
  - Custom S-expression formatters for wire `pts` elements
  - Proper float formatting matching KiCAD precision (0.0000 vs 0.0)
  - Fixed coordinate and color formatting inconsistencies
  - All 29 tests now pass with exact format preservation

- **Hierarchical Annotation and Paper Format**: Fixed KiCad component annotation for hierarchical schematics
  - Corrected component instance paths for hierarchical designs
  - Fixed paper format specification for multi-sheet projects
  - Improved schematic synchronization for hierarchical structures

### Enhanced
- **Rectangle Support**: Added graphical rectangle support to kicad-sch-api
  - Full support for graphical rectangles in schematics
  - Enables bounding box visualization and design documentation

### Changed
- **Version Bump**: Updated from 0.2.1 to 0.3.0 for major feature additions
- **Test Coverage**: Expanded from 17 to 29 tests with comprehensive removal validation
- **Code Quality**: Achieved enterprise-grade configuration management and extensibility

### Documentation
- Updated `CLAUDE.md` with comprehensive removal API documentation
- Enhanced README.md with new features and professional configuration examples
- Documented all new removal methods and configuration options

### Technical Notes
- All changes maintain 100% backward compatibility
- No breaking API changes - existing code continues to work unchanged
- Performance optimizations through centralized configuration
- Enhanced extensibility for future component types and workflows

## [0.2.1] - 2025-01-20

### Added
- **Professional PyPI Release**: First official release to Python Package Index
- **Enhanced Bounding Box Visualization**: 
  - Colored rectangle support with all KiCAD stroke types
  - Support for solid, dash, dot, dash_dot, dash_dot_dot line styles
  - Component bounding box visualization with color customization
- **Improved Manhattan Routing**:
  - Enhanced obstacle avoidance algorithms
  - Perfect KiCAD grid alignment (1.27mm grid)
  - Multiple routing strategies and clearance options
- **Code Quality Improvements**:
  - Formatted with black for consistent style
  - Import sorting with isort
  - Enhanced type checking coverage
- **Comprehensive Testing**:
  - 71 passing tests with 6 intentionally skipped
  - Enhanced test coverage for new features
  - Format preservation validation

### Enhanced
- **Exact Format Preservation**: Improved KiCAD format compatibility
- **Parser & Formatter**: Enhanced S-expression handling
- **Performance**: Optimized for professional use cases

### Technical
- **Dependencies**: Updated build system and packaging
- **Documentation**: Enhanced API documentation
- **CI/CD**: Professional package validation and testing

## [0.2.0] - 2025-01-19

### Added
- Initial public release
- Basic schematic manipulation functionality
- Component management with ComponentCollection
- Wire and label creation
- Symbol library integration
- Format preservation foundation

## [0.1.0] - 2025-01-18

### Added
- Initial development version
- Core S-expression parsing
- Basic schematic loading and saving