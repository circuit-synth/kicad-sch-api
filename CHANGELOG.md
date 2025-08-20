# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-01-20

### Added
- **Pin-to-Pin Wire Drawing**: Intelligent wire routing between component pins
  - `add_wire_between_pins()` method for direct pin-to-pin connections
  - `add_wire_to_pin()` method for connecting arbitrary points to component pins
  - `get_component_pin_position()` method for pin position queries
  - Automatic pin position calculation using existing pin positioning functionality
  - Support for both Point objects and tuple coordinates
  - Comprehensive error handling for invalid components and pins
  - 11 dedicated test cases covering all functionality and edge cases

### Enhanced
- **Wire Management**: Improved wire creation with pin-aware routing
  - Seamless integration with existing WireCollection
  - UUID-based wire tracking for all pin-to-pin connections
  - Maintains exact format preservation for all wire types

### Technical Notes
- Built on existing pin positioning functionality from recent commits
- All wire drawing maintains KiCAD's coordinate system (inverted Y-axis)
- Zero test failures achieved - comprehensive validation of all functionality
- Example files included demonstrating voltage divider and complex circuit creation

## [0.3.0] - 2025-01-20

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

- **Reference-Based Validation**: Advanced removal testing against KiCAD reference files
  - `test_single_resistor_to_blank()` - validates resistor removal matches blank schematic exactly
  - `test_two_resistors_remove_one_matches_single()` - validates selective removal preserves remaining components
  - Byte-for-byte format preservation during removal operations

- **Professional Configuration System**: Centralized configuration management eliminating anti-patterns
  - `KiCADConfig` class with structured configuration categories
  - Property positioning, grid settings, sheet settings, and tolerance configuration
  - Configurable via public `ksa.config` API for user customization
  - Eliminates hardcoded test coordinates and magic numbers from production code

- **Enhanced UUID Support**: UUID parameters for exact format matching
  - `add_label()`, `add_sheet()`, and `add_sheet_pin()` now accept optional `uuid` parameter
  - Deterministic UUID management for test reproducibility
  - Support for both auto-generated and user-specified UUIDs

### Fixed
- **Format Preservation**: Achieved byte-for-byte compatibility with KiCAD reference files
  - Custom S-expression formatters for wire `pts` elements  
  - Proper float formatting matching KiCAD precision (0.0000 vs 0.0)
  - Fixed coordinate and color formatting inconsistencies
  - All 29 tests now pass with exact format preservation

- **Anti-Pattern Elimination**: Removed hardcoded values and test-specific production code
  - Moved test coordinate logic to configurable positioning system
  - Eliminated hardcoded test names in title block generation
  - Centralized magic numbers into structured configuration classes
  - Professional separation of concerns between tests and production code

- **Wire Removal Synchronization**: Fixed inconsistency between collection and data structures
  - `remove_wire()` now updates both WireCollection and underlying schematic data
  - Ensures removal operations maintain data integrity across API layers

### Changed
- **Version Bump**: Updated from 0.2.0 to 0.3.0 for major feature additions
- **Test Coverage**: Expanded from 17 to 29 tests with comprehensive removal validation
- **Code Quality**: Achieved enterprise-grade configuration management and extensibility

### Documentation
- Updated `CLAUDE.md` with comprehensive removal API documentation
- Added `REFACTORING_SUMMARY.md` detailing anti-pattern elimination
- Enhanced README.md with new features and professional configuration examples
- Documented all new removal methods and configuration options

### Technical Notes
- All changes maintain 100% backward compatibility
- No breaking API changes - existing code continues to work unchanged
- Performance optimizations through centralized configuration
- Enhanced extensibility for future component types and workflows

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