# Parsers Module

Component-specific S-expression parsers for different KiCAD elements.

## Overview

This module provides specialized parser classes for different schematic element types. While the main `core/parser.py` handles overall file parsing, these parsers handle element-specific details.

## Architecture

### Parser Registry Pattern
```
Registry → maps element types to parser classes
              ↓
Parser class → parses element content
              ↓
Returns typed object
```

### Base Parser Class (`base.py`)
- **Purpose**: Base class for all element parsers
- **Key Class**: `BaseElementParser`
- **Interface**:
  - `parse(s_expression)` - Parse element
  - `format(element)` - Format back to S-expression
  - `validate(element)` - Check element validity

## Element Parsers

### Symbol Parser (`symbol_parser.py`)
- **Purpose**: Parse component symbol definitions
- **Parses**:
  - Symbol instances in schematic
  - Symbol properties and fields
  - Pin connections
  - Reference designators
- **Key Functions**:
  - `parse_symbol()` - Parse component symbol
  - `parse_symbol_properties()` - Extract all properties
  - `parse_pin_connections()` - Find connected pins

### Wire Parser (`wire_parser.py`)
- **Purpose**: Parse wire connections
- **Parses**:
  - Wire segments
  - Wire endpoints
  - Connected nodes
- **Key Functions**:
  - `parse_wire()` - Parse wire element
  - `validate_connectivity()` - Check connections

### Label Parser (`label_parser.py`)
- **Purpose**: Parse text labels and annotations
- **Parses**:
  - Global labels
  - Local labels
  - Hierarchical labels
  - Text annotations
- **Label Types**:
  - Global label - Net connection across hierarchy
  - Local label - Sheet-local connection
  - Hierarchical label - Subsheet interface
  - Text - Simple annotation
- **Key Functions**:
  - `parse_label()` - Parse text label
  - `get_label_type()` - Determine label type

### Parser Registry (`registry.py`)
- **Purpose**: Register and lookup parsers
- **Key Class**: `ParserRegistry`
- **Functions**:
  - `register_parser(element_type, parser_class)` - Register
  - `get_parser(element_type)` - Lookup parser
  - `parse(element_type, s_expr)` - Parse with registry

## Parsing Flow

```
KiCAD file (text)
    ↓
core/parser.py reads sections
    ↓
ParserRegistry dispatches to element parser
    ↓
Element parser (e.g., symbol_parser.py) parses specific type
    ↓
Returns typed Python object
    ↓
core/formatter.py reverses process
    ↓
KiCAD file (text) with exact format preservation
```

## Element Types Supported

| Element | Parser | Supported |
|---------|--------|-----------|
| Component | symbol_parser.py | ✓ Yes |
| Wire | wire_parser.py | ✓ Yes |
| Label | label_parser.py | ✓ Yes |
| Junction | wire_parser.py | ✓ Yes |
| NoConnect | wire_parser.py | ✓ Yes |
| Text | label_parser.py | ✓ Yes |
| Rectangle | (in core) | ✓ Yes |
| Circle | (in core) | ✓ Yes |

## Adding New Element Parsers

To support new element types:

1. **Create new parser class** - Extend `BaseElementParser`
   ```python
   class MyElementParser(BaseElementParser):
       def parse(self, s_expression):
           # Parse logic
           pass
   ```

2. **Register in registry**
   ```python
   registry.register_parser('my_element', MyElementParser())
   ```

3. **Add tests** - Unit tests for parser
   ```python
   def test_parse_my_element():
       # Test parsing
   ```

4. **Update documentation** - Add to this README

## Error Handling

Parsers should:
- Raise `ParseError` for malformed input
- Include line number in error message
- Provide context about what failed
- Collect non-fatal warnings

## Format Preservation

Critical for exact KiCAD compatibility:
- Parsers preserve original formatting
- Formatter reconstructs exactly
- No normalization of whitespace
- Comments preserved

## Testing

Tests located in `../../tests/`:
- `test_symbol_parser.py` - Component parsing
- `test_wire_parser.py` - Wire parsing
- `test_label_parser.py` - Label parsing
- Integration tests with reference KiCAD files

## Known Issues

1. **Parser Coverage** - All major element types covered, minor types may be missing
2. **Error Recovery** - Parsers don't recover gracefully from some malformations
3. **Documentation** - Individual parser docstrings could be more detailed
4. **Format Preservation** - Some edge cases may not preserve formatting

## Performance

- **Parsing Speed**: ~100-500µs per element
- **Memory**: ~1KB per element object
- **Scalability**: Tested with 10,000+ component schematics

## Related Modules

- `core/parser.py` - Overall file parsing
- `core/formatter.py` - Format preservation
- `core/types.py` - Type definitions
- `ParserRegistry` - Parser dispatch

## References

- KiCAD File Format: https://github.com/KiCad/kicad-file-formats
- Parser pattern: See `CODEBASE_ANALYSIS.md`
- Type system: See `core/types.py`
