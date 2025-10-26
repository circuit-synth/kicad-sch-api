# kicad_sch_api - Core Package

Professional KiCAD schematic manipulation library with exact format preservation.

## Overview

This is the main package directory containing all core functionality for programmatic manipulation of KiCAD schematic files. The library provides a modern, Pythonic API while maintaining exact format compatibility with KiCAD's native output.

## Directory Structure

### Core Modules

- **`core/`** - Core schematic manipulation and manager architecture
  - `schematic.py` - Main Schematic class and entry point (1,584 lines)
  - `parser.py` - S-expression parser for KiCAD format (2,351 lines)
  - `formatter.py` - Format preservation and output generation
  - `types.py` - Core data types (Point, Component, Wire, etc.)
  - `components.py` - Component collection management
  - `config.py` - Configuration system for KiCAD behavior

### Manager System (Phase 4 Architecture)

Located in `core/managers/`, these specialized managers handle distinct responsibilities:

- `file_io.py` - File loading/saving operations
- `validation.py` - Validation and error collection
- `components.py` - Component manipulation
- `wire.py` - Wire connection management
- `text_elements.py` - Text labels and annotations
- `graphics.py` - Graphical elements (rectangles, circles, etc.)
- `metadata.py` - Sheet and document metadata
- `format_sync.py` - Format preservation coordination

### Utility Modules

- **`geometry/`** - Geometric calculations and routing
  - `geometry.py` - Point, segment, and shape utilities
  - `simple_manhattan.py` - L-shaped wire routing (simple)
  - `manhattan_routing.py` - A* pathfinding routing (430 lines)
  - `wire_routing.py` - Wire utilities

- **`symbols/`** - Symbol library and pin management
  - `pin_utils.py` - Pin parsing and analysis
  - `component_bounds.py` - Bounding box calculations

- **`library/`** - Symbol library management
  - `cache.py` - Multi-layer symbol caching (RAM, disk, KiCAD)

- **`parsers/`** - Component-specific parsers
  - `base.py` - Base parser class
  - `symbol_parser.py` - Component symbol parsing
  - `wire_parser.py` - Wire parsing
  - `label_parser.py` - Text label parsing
  - `registry.py` - Parser registration system

- **`collections/`** - Enhanced collection classes
  - ComponentCollection, WireCollection, etc. with filtering and bulk operations

- **`utils/`** - Validation and utility functions
  - `validation.py` - Comprehensive validation system

- **`discovery/`** - Component search and indexing
  - `search_index.py` - SQLite-based component search

- **`interfaces/`** - Type definitions and protocols
  - Interface definitions for extensibility

### Specialized Modules

- **`ic_manager.py`** - Multi-unit IC handling (193 lines, experimental/unclear status)
- **`placement/`** - Component placement algorithms (currently unused)

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/schematic.py` | 1,584 | Main API, manager coordination |
| `core/parser.py` | 2,351 | S-expression parsing (CRITICAL) |
| `core/formatter.py` | 563 | Format preservation logic |
| `core/components.py` | 736 | Component collection |
| `core/config.py` | 285 | Configuration system |
| `core/types.py` | 420 | Type definitions |
| `library/cache.py` | 450+ | Symbol caching system |

## Architecture Patterns

### Manager-Based Design
The Schematic class coordinates 8 specialized managers, each with a single responsibility:
- Separation of concerns
- Easier testing and maintenance
- Clear dependencies

### Exact Format Preservation
Every S-expression maintains original formatting to ensure output matches KiCAD byte-perfectly:
- Parser preserves structure
- Formatter reconstructs exactly
- Critical for version control

### Type System
Strong typing throughout with strict mypy configuration:
- Frozen dataclasses for immutability
- Comprehensive type hints
- Protocol-based interfaces

## Code Quality

- **Type Checking**: Strict mypy enabled
- **Formatting**: Black/isort compliance
- **Testing**: 39 comprehensive test files
- **Documentation**: Module and class docstrings throughout

## Version Info

- **Current Version**: 0.4.0 ✅ CONSISTENT
- **Package Version**: 0.4.0 (in __init__.py)
- **Project Version**: 0.4.0 (in pyproject.toml)

## Known Issues

1. **Version Mismatch** - ✅ FIXED (both now 0.4.0)
2. **IC Manager Status** - Unclear if experimental or dead code
3. **Routing Consolidation** - Multiple routing implementations (simple vs complex)
4. **Unresolved TODOs** - 4 TODO comments in code
5. **Empty placement/ Directory** - Only contains __pycache__, no actual code

## Related Documentation

- See `CLAUDE.md` for development guide
- See `CODEBASE_ANALYSIS.md` for detailed architecture analysis
- See root `README.md` for user-facing documentation
