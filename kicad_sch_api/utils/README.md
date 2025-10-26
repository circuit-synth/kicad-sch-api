# Utils Module

Validation and utility functions.

## Overview

This module provides validation, error handling, and utility functions used throughout the library.

## Validation System (`validation.py`)

### Core Classes

#### ValidationError
- **Purpose**: Exception raised during validation
- **Inherits from**: `Exception`
- **Use Case**: Validation failures that can be caught and handled

#### ValidationIssue
- **Purpose**: Represents a single validation issue
- **Attributes**:
  - `issue_type` - Type of problem (error, warning, info)
  - `message` - Human-readable description
  - `element_type` - What element has the issue (component, wire, etc.)
  - `element_id` - Specific element identifier
  - `line_number` - Location in file (if applicable)
  - `severity` - HIGH, MEDIUM, LOW
- **Methods**:
  - `__str__()` - Format for display
  - `to_dict()` - Convert to dictionary

#### ValidationReport
- **Purpose**: Aggregate validation results
- **Attributes**:
  - `issues` - List of ValidationIssue objects
  - `passed` - Boolean indicating if validation passed
  - `error_count` - Number of errors
  - `warning_count` - Number of warnings
  - `info_count` - Number of info messages
- **Methods**:
  - `add_issue()` - Add validation issue
  - `get_errors()` - Filter for errors only
  - `get_warnings()` - Filter for warnings only
  - `print_summary()` - Display results

### Validation Checks

The ValidationManager in `core/managers/validation.py` performs:

| Check | Type | Purpose |
|-------|------|---------|
| Reference uniqueness | Error | No duplicate reference designators |
| Missing reference | Warning | Components without reference |
| Invalid footprint | Warning | Missing or invalid footprint |
| Unconnected pins | Warning | Pins not connected to nets |
| Electrical validation | Info | Net connectivity checks |
| Format validation | Error | Ensure KiCAD format compliance |
| Library validation | Warning | Referenced symbols must exist |

### Using Validation

```python
import kicad_sch_api as ksa

# Load schematic
sch = ksa.load_schematic('my_circuit.kicad_sch')

# Run validation
report = sch.validate()

# Check results
if report.passed:
    print("Validation passed!")
else:
    print(f"Found {report.error_count} errors")
    for issue in report.get_errors():
        print(f"  - {issue}")

# Filter by severity
high_severity = [i for i in report.issues if i.severity == 'HIGH']
```

## Error Types

### Validation Error Types
- `MissingReference` - Component has no reference
- `DuplicateReference` - Same reference used twice
- `InvalidFootprint` - Missing or malformed footprint
- `MissingLibrary` - Referenced library not found
- `MissingSymbol` - Referenced symbol not found
- `UnconnectedPin` - Pin has no connection
- `InvalidConnection` - Connection violates rules
- `MalformedElement` - Element doesn't follow format

### Exception Types
- `ValidationError` - General validation error
- `ParseError` (from core) - File parsing failed
- `ConfigError` - Configuration invalid

## Common Utility Functions

While most utilities are in their respective modules, common ones include:

- **String utilities**:
  - `normalize_reference()` - Standardize component references
  - `parse_value_string()` - Extract component value

- **File utilities**:
  - `get_file_size()` - File size in bytes
  - `get_file_mtime()` - File modification time

- **Type utilities**:
  - `is_valid_coordinate()` - Check if valid point
  - `is_valid_reference()` - Check if valid reference

## Configuration (`core/config.py`)

Not in utils but related:
- **KiCADConfig** - Global configuration singleton
- **Usage**: `from kicad_sch_api.core.config import config`

## Logging

The library uses Python standard `logging`:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Use in code
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.warning("Warning message")
logger.error("Error message")
```

## Testing

Tests located in `../../tests/`:
- `test_validation.py` - Validation system tests
- `test_error_handling.py` - Error handling
- Integration tests validate error messages

## Known Issues

1. **Validation Coverage** - Some edge cases may not be validated
2. **Error Messages** - Could be more specific for debugging
3. **Recovery Mechanism** - Validators don't suggest fixes
4. **Performance** - Full validation may be slow on large schematics

## Future Improvements

- [ ] Add validation rules customization
- [ ] Include suggested fixes in validation issues
- [ ] Add performance warnings for large schematics
- [ ] Implement async validation for large files
- [ ] Add validation rule profiles (strict, lenient, etc.)

## Integration Points

### Used By
- `Schematic.validate()` - Main validation entry point
- `ValidationManager` - Implements validation logic
- File I/O - Validates during save
- Component addition - Validates new components

### Related Modules
- `core/parser.py` - Parsing errors
- `core/formatter.py` - Format validation
- `core/managers/validation.py` - Manager implementation

## References

- Validation pattern: See `CODEBASE_ANALYSIS.md`
- Error handling: See `CLAUDE.md`
- Configuration: See `core/config.py`
