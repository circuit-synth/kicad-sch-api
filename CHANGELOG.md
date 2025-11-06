# Changelog

All notable changes to kicad-sch-api will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[0.4.1]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.3.0...v0.3.2
[0.3.0]: https://github.com/circuit-synth/kicad-sch-api/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/circuit-synth/kicad-sch-api/releases/tag/v0.2.0
