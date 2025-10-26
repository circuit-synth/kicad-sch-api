# Managers Module

Specialized manager classes implementing Phase 4 architecture.

## Overview

The manager system is the core of Phase 4 architecture. Each manager has a single responsibility and is coordinated by the main `Schematic` class. This pattern provides excellent separation of concerns and testability.

## Managers

### FileIOManager (`file_io.py`)
- **Purpose**: Handle file I/O operations
- **Responsibilities**:
  - Load schematic files
  - Save with exact format preservation
  - Parse and format coordination
- **Key Methods**:
  - `load_file(path)` - Load .kicad_sch file
  - `save_file(path)` - Save to file
  - `_parse_content()` - Coordinate with parser

### ValidationManager (`validation.py`)
- **Purpose**: Comprehensive validation and error detection
- **Responsibilities**:
  - Check for invalid references
  - Validate electrical connectivity
  - Detect missing components
  - Collect all errors without stopping
- **Key Methods**:
  - `validate()` - Run all validation checks
  - `add_error()` - Add validation issue
  - `get_issues()` - Get all found issues
- **Error Types**:
  - MissingReference
  - InvalidConnection
  - DuplicateComponents
  - etc.

### ComponentManager (`components.py`)
- **Purpose**: Component CRUD operations and filtering
- **Responsibilities**:
  - Add/remove components
  - Update properties
  - Filter and search
  - Bulk operations
- **Key Methods**:
  - `add_component()` - Add new component
  - `remove_component()` - Remove by reference
  - `filter_by_lib_id()` - Find by library ID
  - `bulk_update()` - Update multiple components
- **Features**:
  - Symbol library integration
  - Property management
  - Footprint assignment

### WireManager (`wire.py`)
- **Purpose**: Wire routing and connectivity
- **Responsibilities**:
  - Add/remove wires
  - Route connections
  - Calculate net connectivity
- **Key Methods**:
  - `add_wire()` - Add connection
  - `remove_wire()` - Remove by UUID
  - `route_wire()` - Calculate path with routing algorithm
- **Routing Algorithms**:
  - Simple Manhattan (L-shaped)
  - A* pathfinding (complex paths)

### TextElementManager (`text_elements.py`)
- **Purpose**: Text labels and annotations
- **Responsibilities**:
  - Add/remove labels
  - Position text elements
  - Update text content
- **Key Methods**:
  - `add_label()` - Add text label
  - `remove_label()` - Remove by UUID
  - `update_text()` - Change label content
- **Label Types**:
  - Global labels (net connection)
  - Local labels
  - Hierarchical labels

### GraphicsManager (`graphics.py`)
- **Purpose**: Graphical elements (shapes, etc.)
- **Responsibilities**:
  - Add/remove shapes
  - Manage rectangles, circles, lines
  - Handle polylines
- **Key Methods**:
  - `add_rectangle()` - Add rect shape
  - `add_circle()` - Add circle shape
  - `remove_graphic()` - Remove by UUID

### MetadataManager (`metadata.py`)
- **Purpose**: Sheet and document metadata
- **Responsibilities**:
  - Manage sheet properties
  - Handle document information
  - Store custom properties
- **Key Methods**:
  - `set_title()` - Set sheet title
  - `set_property()` - Store custom property
  - `get_metadata()` - Get all metadata

### FormatSyncManager (`format_sync.py`)
- **Purpose**: Coordinate format preservation
- **Responsibilities**:
  - Track original formatting
  - Ensure exact output match
  - Manage formatting state
- **Key Methods**:
  - `mark_modified()` - Mark element as changed
  - `preserve_format()` - Preserve original formatting
  - `get_format_directives()` - Get formatting info

## Manager Coordination

```
Schematic class coordinates all managers:

schematic = Schematic.load('file.kicad_sch')
  ↓ delegates to
FileIOManager → loads file
  ↓ delegates to
Parser → parses content
  ↓ creates managers
ComponentManager, WireManager, etc.
  ↓ on save() call
FormatSyncManager → coordinates format
  ↓ delegates to
Formatter → outputs KiCAD format
  ↓ delegates to
FileIOManager → saves to file
```

## Manager Dependencies

- All managers are **owned** by Schematic class
- Managers have **minimal cross-dependencies**
- Each manager is **independently testable**
- Format preservation is **coordinated** by FormatSyncManager

## Testing

Each manager should have:
- Unit tests for individual operations
- Integration tests with other managers
- Format preservation tests (critical)
- Error handling tests

Test location: `../../tests/unit/managers/`

## Adding New Managers

When adding new functionality:

1. **Create new manager class** in `managers/` directory
2. **Implement** required interface/base class
3. **Add to Schematic class** in `__init__()` method
4. **Register** in `__all__` export
5. **Add comprehensive tests** in test directory
6. **Update documentation** (this README)

## Phase 4 Architecture Benefits

✅ **Separation of Concerns** - Each manager has one job
✅ **Testability** - Managers can be tested independently
✅ **Maintainability** - Clear, organized code structure
✅ **Extensibility** - Easy to add new managers
✅ **Coordination** - Schematic class handles orchestration

## Known Issues

- See parent `README.md` for core module issues
- Manager interaction edge cases may need testing
- Error propagation from managers needs documentation

## References

- Architecture decision: See `../.memory_bank/decisionLog.md`
- Design patterns: See `CLAUDE.md` in project root
- Related code: `../schematic.py` for integration
