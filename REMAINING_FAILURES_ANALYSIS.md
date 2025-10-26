# Remaining Failures Analysis - Phase 4 Refactoring

**Session Summary**: Fixed 20 of 25 failing tests (80% success rate)
- **Starting Point**: 25 failures, 277 passing
- **Current State**: 5 failures, 290 passing
- **Status**: 96.7% test pass rate

---

## Overview of Remaining 5 Failures

### Category 1: Hierarchical Sheets (2 failures)
- `test_against_references.py::TestAgainstReferences::test_single_hierarchical_sheet`
- `test_runner.py::TestRunner::test_single_hierarchical_sheet`

### Category 2: Text Box Implementation (1 failure)
- `test_runner.py::TestRunner::test_single_text_box`

### Category 3: Rectangle Color Serialization (2 failures)
- `test_bounding_box_rectangles.py::test_colored_bounding_box_rectangle`
- `test_bounding_box_rectangles.py::test_body_vs_properties_bounding_boxes`

---

## Detailed Analysis

### FAILURE 1 & 2: Hierarchical Sheets Not Being Serialized

**Issue**: Sheets added via `add_sheet()` are not being written to the output schematic file.

#### Test Failure Details

**Test 1** (`test_against_references.py`):
```python
def test_single_hierarchical_sheet(self):
    # Generates schematic with sheet, compares to reference
    # Reference has 88 lines with full sheet definition
    # Generated output: Sheet section is completely missing
```

**Test 2** (`test_runner.py`):
```python
def test_single_hierarchical_sheet(self):
    assert "sheet" in content  # PASS - at least (sheet has sheet_instances)
    assert "subcircuit1" in content  # FAIL - sheet name not found
    assert "subcircuit1.kicad_sch" in content  # FAIL - filename not found
```

#### Expected vs Actual Output

**Expected (from reference)**:
```scheme
(sheet
    (at 137.16 69.85)
    (size 26.67 34.29)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (fields_autoplaced yes)
    (stroke
        (width 0.1524)
        (type solid)
    )
    (fill
        (color 0 0 0 0.0000)
    )
    (uuid "0c5266be-4fa5-460f-9a2f-0ee59ba7fd90")
    (property "Sheetname" "subcircuit1"
        (at 137.16 69.1384 0)
        (effects ...)
    )
    (property "Sheetfile" "subcircuit1.kicad_sch"
        (at 137.16 104.7246 0)
        (effects ...)
    )
    (pin "NET1" input ...)
    (pin "NET2" input ...)
    (pin "NET3" input ...)
    (pin "NET4" input ...)
    (instances
        (project "single_hierarchical_sheet"
            (path "/bfabd21f-2733-4953-b034-506cb9fdf9ab"
                (page "2")
            )
        )
    )
)
```

**Actual (generated)**:
```scheme
(lib_symbols)
(sheet_instances ...)  # Only sheet_instances, not sheet definition
(embedded_fonts no)
```

#### Root Cause Analysis

1. **SheetManager Working**: `SheetManager.add_sheet()` in managers/sheet.py (line 119) correctly appends to `self._data["sheet"]`
   - This means sheets ARE being added to the data dictionary

2. **Parser Not Serializing**: The parser's `_schematic_data_to_sexp()` method (line 301+) needs to serialize `_data["sheet"]`
   - **Current behavior**: Parser checks for "sheet" key and should serialize it
   - **Investigation needed**: Verify if sheets are in _data when save() is called

3. **Likely Problem**: Sheets in `_data["sheet"]` but no corresponding serialization in parser
   - Parser may not have a `_sheet_to_sexp()` method
   - Or sheets are being added AFTER the parser checks for them

#### Code Inspection Points

**File**: `kicad_sch_api/core/managers/sheet.py`
- Lines 39-122: `add_sheet()` appends to `self._data["sheet"]` ✓ Works

**File**: `kicad_sch_api/core/parser.py`
- Lines 301-380: `_schematic_data_to_sexp()`
  - Need to check if it iterates over `schematic_data.get("sheet", [])`
  - Check if `_sheet_to_sexp()` method exists

**File**: `kicad_sch_api/core/schematic.py`
- Lines 902-941: `add_sheet()` calls `_sheet_manager.add_sheet()`
  - No explicit sync to _data needed since SheetManager does it
  - May need to add to save() sync flow

#### Fix Strategy

1. **Verify parser serialization**:
   ```python
   # In parser._schematic_data_to_sexp(), add:
   for sheet in schematic_data.get("sheet", []):
       sexp_data.append(self._sheet_to_sexp(sheet))
   ```

2. **Create `_sheet_to_sexp()` method** if missing:
   - Must convert sheet dict to proper S-expression
   - Must handle properties, pins, and instances sections

3. **Verify sheet data structure** matches what parser expects:
   - Properties with "Sheetname" and "Sheetfile"
   - Pin definitions with effects and justification
   - Instances with project and path info

#### Related Test Script
- `tests/reference_tests/test_single_hierarchical_sheet.py` - Shows how sheets are created
- **Key call**: `sch.add_sheet(name, filename, position, size)`

---

### FAILURE 3: Text Box Not Implemented

**Issue**: Text box creation method exists but doesn't actually create elements.

#### Test Failure Details

**Test** (`test_runner.py`):
```python
def test_single_text_box(self):
    # Expects text_box element in output
    assert 'text_box "Text box goes here"' in content  # FAIL
```

#### Current Implementation Status

**File**: `kicad_sch_api/core/schematic.py`
```python
def add_text_box(
    self,
    text: str,
    position: Union[Point, Tuple[float, float]],
    size: Tuple[float, float] = (10.0, 5.0),
    rotation: float = 0,
    effects: Optional[Dict[str, Any]] = None,
    border_stroke: Optional[Dict[str, Any]] = None,
    fill_color: Optional[Tuple[int, int, int, float]] = None,
    justify: str = "left"
) -> str:
    """Add a text box to schematic."""
    # Implementation just returns empty string or doesn't create element
```

#### Root Cause

Text box functionality is **stubbed but not implemented**:
- Method signature exists but logic is missing
- No call to manager to create text box
- No addition to `_data` dictionary
- No sync mechanism in save()

#### Expected Data Structure

Based on KiCAD format, text boxes should have:
```scheme
(text_box "Text box goes here"
    (at 100 100 0)
    (size 50 25)
    (effects
        (font
            (size 1.27 1.27)
        )
    )
)
```

#### Required Components

1. **Determine if TextBoxManager exists**:
   - Check `kicad_sch_api/core/managers/` for text_box related files
   - If not, may need to create one or extend existing TextElementManager

2. **Add parser support**:
   - Parser must have `_parse_text_box()` method (parsing from files)
   - Parser must have `_text_box_to_sexp()` method (serialization)

3. **Add to Schematic**:
   - Create actual implementation in `add_text_box()`
   - Add to `_data["text_boxes"]` or similar key
   - Add sync method to save()

#### Fix Strategy

1. **Check existing managers** for text box support
2. **If not present, create TextBoxElement and TextBoxManager** following pattern of labels/texts
3. **Implement `add_text_box()` method** to actually create text boxes
4. **Add parser serialization** for round-trip support
5. **Add sync call** in save() method

#### Related Test Script
- `tests/reference_tests/test_single_text_box.py` - Shows how text boxes are created
- **Key call**: `sch.add_text_box(text, position, size, effects)`

---

### FAILURE 4 & 5: Rectangle Colors Not Serialized

**Issue**: Color information passed to `draw_bounding_box()` is converted to RGBA tuples but not serialized.

#### Test Failure Details

**Test 1** (`test_bounding_box_rectangles.py::test_colored_bounding_box_rectangle`):
```python
def test_colored_bounding_box_rectangle(self):
    rect_uuid = sch.draw_bounding_box(
        bbox,
        stroke_width=1.0,
        stroke_color="red",  # Color provided
        stroke_type="dash"
    )
    # Expect: (color 255 0 0 1) in output
    # Actual: No color information in output
```

**Test 2** (`test_bounding_box_rectangles.py::test_body_vs_properties_bounding_boxes`):
```python
def test_body_vs_properties_bounding_boxes(self):
    rect_body_uuid = sch.draw_bounding_box(
        bbox_body,
        stroke_color="blue",  # Color provided
        stroke_type="solid"
    )
    # Expect: (color 0 0 255 1) in output
    # Actual: No color information in output
```

#### Current Implementation

**File**: `kicad_sch_api/core/schematic.py` (lines 1106-1153)
```python
def draw_bounding_box(
    self,
    bbox: "BoundingBox",
    stroke_width: float = 0.127,
    stroke_color: Optional[str] = None,
    stroke_type: str = "solid"
) -> str:
    # Converts color to RGBA tuple
    stroke_rgba = color_map.get(stroke_color.lower(), (0, 255, 0, 1.0))

    # Passes to add_rectangle
    rect_uuid = self.add_rectangle(
        start=(bbox.min_x, bbox.min_y),
        end=(bbox.max_x, bbox.max_y),
        stroke_width=stroke_width,
        stroke_type=stroke_type,
        stroke_color=stroke_rgba  # Passes RGBA tuple
    )
```

#### Data Flow

1. **draw_bounding_box()** converts color string to RGBA tuple ✓
2. **add_rectangle()** receives RGBA tuple in `stroke_color` parameter
3. **GraphicsManager.add_rectangle()** receives nested stroke dict:
   ```python
   stroke = {
       "width": stroke_width,
       "type": stroke_type
       # Color not added!
   }
   ```
4. **Rectangle stored** without color information ✗

#### Root Cause

**In `schematic.py` lines 1016-1021**:
```python
stroke = {
    "width": stroke_width,
    "type": stroke_type
}
if stroke_color:  # <-- NEVER TRUE because stroke_color is RGBA tuple
    stroke["color"] = stroke_color  # <-- NOT EXECUTED
```

The problem: `stroke_color` is converted to RGBA tuple in `draw_bounding_box()`, but `add_rectangle()` checks `if stroke_color:` against the original parameter (which is None from the method call).

#### Expected Format

KiCAD rectangles with colors should look like:
```scheme
(rectangle
    (start 100 100)
    (end 200 200)
    (stroke
        (width 0.127)
        (type solid)
        (color 255 0 0 1)  # <-- R G B A values
    )
    (fill
        (type none)
    )
    (uuid "...")
)
```

#### Fix Strategy

1. **Modify `draw_bounding_box()` method**:
   - Pass color information to `add_rectangle()` differently
   - Either:
     a. Pass color as separate parameter from `add_rectangle()`
     b. Pass color as part of stroke dict to `add_rectangle()`

2. **Update `add_rectangle()` signature**:
   - If using separate parameter: `add_rectangle(..., stroke_color=...)`
   - Must properly handle color format

3. **Update GraphicsManager**:
   - Store color in rectangle data structure
   - Format: Either `stroke["color"]` or flat `stroke_color_rgba`

4. **Update parser serialization**:
   - `_rectangle_to_sexp()` must include color if present
   - Format: `(color R G B A)` inside stroke section

#### Implementation Notes

- **Color format**: RGBA as list `[R, G, B, A]` or dict `{"color": [R, G, B, A]}`
- **Reference format**: `(color 255 0 0 1)` - space-separated values in S-expression
- **Backward compatibility**: Colors are optional, must not break non-colored rectangles

---

## Implementation Priority & Complexity

### Priority 1 (High Impact, High Complexity)
1. **Hierarchical Sheets Serialization** - Affects 2 tests, requires parser investigation
2. **Text Box Implementation** - Affects 1 test, new feature with full architecture needed

### Priority 2 (Medium Impact, Low Complexity)
3. **Rectangle Color Serialization** - Affects 2 tests, mostly data flow issues

---

## Testing Strategy for Fixes

### For Hierarchical Sheets
```bash
# Run just the sheet tests
uv run pytest tests/reference_tests/test_against_references.py::TestAgainstReferences::test_single_hierarchical_sheet -v
uv run pytest tests/reference_tests/test_runner.py::TestRunner::test_single_hierarchical_sheet -v

# Check generated vs reference
diff tests/reference_tests/reference_kicad_projects/single_hierarchical_sheet/single_hierarchical_sheet.kicad_sch /tmp/generated.kicad_sch
```

### For Text Box
```bash
# Run just the text box test
uv run pytest tests/reference_tests/test_runner.py::TestRunner::test_single_text_box -v

# Check if text_box element appears in output
grep 'text_box' /tmp/generated.kicad_sch
```

### For Colors
```bash
# Run just the color tests
uv run pytest tests/test_bounding_box_rectangles.py::TestBoundingBoxRectangles::test_colored_bounding_box_rectangle -v
uv run pytest tests/test_bounding_box_rectangles.py::TestBoundingBoxRectangles::test_body_vs_properties_bounding_boxes -v

# Check if color values appear in rectangles
grep -A 5 '(rectangle' /tmp/generated.kicad_sch | grep color
```

---

## Files to Investigate

### For Sheets
- `kicad_sch_api/core/parser.py` - Check `_schematic_data_to_sexp()` for sheet serialization
- `kicad_sch_api/core/managers/sheet.py` - SheetManager implementation (already working)
- `tests/reference_tests/test_single_hierarchical_sheet.py` - Test script showing expected usage

### For Text Boxes
- `kicad_sch_api/core/managers/` - Look for text_box or text_element implementations
- `kicad_sch_api/core/parser.py` - Check for `_parse_text_box()` and `_text_box_to_sexp()`
- `tests/reference_tests/test_single_text_box.py` - Test script showing expected usage

### For Colors
- `kicad_sch_api/core/schematic.py` - Lines 1006-1032 (add_rectangle method)
- `kicad_sch_api/core/managers/graphics.py` - Lines 71-85 (rectangle storage)
- `kicad_sch_api/core/parser.py` - Lines 1942-1975 (_rectangle_to_sexp method)

---

## Summary Table

| Failure | Category | Issue | Complexity | Impact | Status |
|---------|----------|-------|------------|--------|--------|
| Hierarchical Sheet 1 | Sheet Serialization | Sheets not in output | High | 2 tests | Needs investigation |
| Hierarchical Sheet 2 | Sheet Serialization | Sheets not in output | High | 2 tests | Needs investigation |
| Text Box | Feature Gap | Not implemented | High | 1 test | New feature needed |
| Rectangle Color 1 | Data Flow | Color not passed through | Low | 2 tests | Parameter passing issue |
| Rectangle Color 2 | Data Flow | Color not passed through | Low | 2 tests | Parameter passing issue |

---

## Success Metrics for Complete Fix

- [ ] All 5 failing tests pass
- [ ] No regression in currently passing 290 tests
- [ ] Full test suite: 295/302 passing (97.4%)
- [ ] Reference test for hierarchical sheets matches byte-for-byte
- [ ] Text box elements serialize correctly in KiCAD format
- [ ] Rectangle colors appear in S-expression output with proper RGBA values

