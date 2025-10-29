# Changelog - v0.4.3

## Fixed

### Critical Symbol Comparison Bug Fix

**Issue:** `sexpdata.Symbol` objects were being compared directly with strings, causing boolean properties to be parsed incorrectly.

**Impact:** 
- `(in_bom yes)` and `(on_board yes)` were parsed as `False`
- Components excluded from BOM and board during export
- Broke bidirectional KiCad ↔ Python workflows

**Root Cause:**
```python
# Before (BUGGY)
symbol_data["in_bom"] = sub_item[1] == "yes"  # sub_item[1] is Symbol('yes')
# Symbol('yes') == "yes" returns False ❌
```

**Solution:**
Created `kicad_sch_api/core/parsing_utils.py` with type-safe `parse_bool_property()` helper:
```python
def parse_bool_property(value, default=True):
    if isinstance(value, sexpdata.Symbol):
        value = str(value)  # Convert Symbol to string
    return value.lower() == "yes" if isinstance(value, str) else default
```

Updated `symbol_parser.py` to use the helper function for `in_bom` and `on_board` properties.

**Verification:**
- 13 comprehensive unit tests added
- Components now correctly preserve `in_bom=True` and `on_board=True`
- File round-trips maintain correct property values

## Files Changed

- `kicad_sch_api/core/parsing_utils.py` (new): Type-safe boolean property parser
- `kicad_sch_api/parsers/elements/symbol_parser.py`: Use parse_bool_property helper
- `tests/unit/test_parse_bool_property.py` (new): 13 unit tests including regression test

## Related

- PR #67: Symbol comparison bug fix
- Fixes critical bug affecting circuit-synth bidirectional workflows

