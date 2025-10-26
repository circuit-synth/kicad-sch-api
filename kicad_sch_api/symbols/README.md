# Symbols Module

Symbol caching, validation, and inheritance resolution.

## Overview

This module provides symbol-related functionality including symbol caching, inheritance resolution, and symbol validation. This is distinct from the library cache (`library/cache.py`) which handles library-level caching.

## Module Files

### Symbol Cache (`cache.py`)
- **Lines**: ~500
- **Purpose**: Symbol definition caching and storage
- **Key Classes**:
  - Symbol caching classes
  - Symbol definition management

### Symbol Resolver (`resolver.py`)
- **Lines**: ~400
- **Purpose**: Resolve symbol inheritance chains
- **Key Classes**:
  - `SymbolResolver` - Handles symbol inheritance
  - Inheritance chain resolution
- **Features**:
  - Base symbol resolution
  - Derived symbol extension
  - Multi-level inheritance
  - Property inheritance

### Symbol Validators (`validators.py`)
- **Lines**: ~600
- **Purpose**: Validate symbol definitions and structure
- **Key Classes**:
  - Symbol validation functions
  - Pin validation
  - Property validation
- **Validation Types**:
  - Pin definition validation
  - Symbol structure validation
  - Property validation
  - Electrical rule checking

## Symbol Inheritance

KiCAD supports symbol inheritance where derived symbols extend base symbols:

```
Base Symbol (e.g., Device:R_Base)
    ↓ inherits
Derived Symbol (e.g., Device:R)
    ↓ adds
Additional properties, pin definitions
```

The resolver (`resolver.py`) handles this inheritance chain.

## Pin Utilities & Component Bounds

**Note**: Pin utilities and component bounds are located in `core/`, not here:
- `core/pin_utils.py` - Pin parsing and position calculation
- `core/component_bounds.py` - Bounding box calculation

## Integration with Library Cache

This module works alongside `library/cache.py`:

- `library/cache.py` - Library-level caching (symbol library files)
- `symbols/cache.py` - Symbol-level caching (individual symbols)
- `symbols/resolver.py` - Inheritance resolution
- `symbols/validators.py` - Symbol validation

## Data Flow

```
KiCAD Symbol Library File (.kicad_sym)
    ↓ loaded by
library/cache.py (SymbolLibraryCache)
    ↓ extracts
Individual Symbol Definition
    ↓ cached by
symbols/cache.py
    ↓ resolved by
symbols/resolver.py (if has inheritance)
    ↓ validated by
symbols/validators.py
    ↓
Used in schematic
```

## Symbol Validation

The validators module checks:
- Pin electrical types match connections
- Pin numbers are unique
- Symbol structure is valid KiCAD format
- Properties are correctly defined
- Inheritance chains are valid

### Example Usage
```python
from kicad_sch_api.symbols import validators, resolver

# Validate symbol
issues = validators.validate_symbol(symbol_def)
if issues:
    print(f"Found {len(issues)} validation issues")

# Resolve inheritance
resolved_symbol = resolver.resolve_inheritance(derived_symbol, base_symbol)
```

## Known Issues

1. **Symbol Inheritance** - Complex multi-level inheritance may have edge cases
2. **Validation Coverage** - Not all KiCAD symbol features validated
3. **Performance** - Large symbols with many pins may be slow to validate

## Testing

Tests located in `../../tests/`:
- `test_symbol_cache.py` - Symbol caching tests
- `test_symbol_resolver.py` - Inheritance resolution tests
- `test_symbol_validators.py` - Validation tests
- Integration tests with real KiCAD symbols

## Related Modules

- `library/cache.py` - Library-level caching
- `core/pin_utils.py` - Pin position calculation
- `core/component_bounds.py` - Bounding box calculation
- `core/types.py` - Type definitions

## Future Improvements

- [ ] Improve validation coverage
- [ ] Optimize inheritance resolution
- [ ] Add symbol transformation support
- [ ] Cache validation results
- [ ] Support custom symbol properties

## References

- KiCAD Symbol Format: https://github.com/KiCad/kicad-symbols
- Symbol inheritance: KiCAD documentation
- Library caching: See `library/README.md`
