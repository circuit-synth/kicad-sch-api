# KiCAD Coordinate System Guide for LLMs and Developers

**Issue #123 - Pin Placement Issue: LLM Confusion with KiCAD Inverted Y-Axis**

## Table of Contents
1. [The Core Problem](#the-core-problem)
2. [Why LLMs Get Confused](#why-llms-get-confused)
3. [The Two Coordinate Systems](#the-two-coordinate-systems)
4. [The Critical Transformation](#the-critical-transformation)
5. [Visual Examples](#visual-examples)
6. [Implementation Details](#implementation-details)
7. [Common Mistakes and Fixes](#common-mistakes-and-fixes)
8. [Diagnostic Quick Reference](#diagnostic-quick-reference)
9. [Testing and Verification](#testing-and-verification)
10. [Quick Reference](#quick-reference)

---

## The Core Problem

**PROBLEM**: KiCAD uses TWO DIFFERENT coordinate systems, and mixing them causes pins to be placed upside-down, wires to connect to wrong pins, and connectivity analysis to fail completely.

### The Classic LLM Mistake

**What the LLM sees:**
```python
# Symbol library: Pin 1 at (0, +3.81)
# LLM: "Positive value means UP, so add it!"
pin1_y = 100 + 3.81 = 103.81  # ❌ WRONG - Pin 1 now at BOTTOM
```

**Reality:** Pin 1 appears at the TOP visually, but ends up at Y=103.81 (BOTTOM) because the LLM forgot that:
- Symbol library uses +3.81 (positive = "above" in symbol space)
- But schematic space is inverted (higher Y = lower on screen)
- Must NEGATE first: 100 + (-3.81) = 96.52 (TOP)

**Result:** Pin 1 with the "higher" positive value (+3.81) ends up at the BOTTOM instead of the TOP where it belongs.

### Symptom Checklist
- [ ] Pins appear in wrong order (pin 1 at bottom instead of top)
- [ ] Wires connect to wrong component pins
- [ ] Connectivity analysis reports incorrect connections
- [ ] Netlist doesn't match KiCAD's `kicad-cli` output
- [ ] Hierarchical connections fail to resolve

**If you see ANY of these symptoms, you have a coordinate system transformation bug.**

---

## Why LLMs Get Confused

### 1. Mathematical Intuition vs Computer Graphics Reality

**LLMs are trained on mathematical and engineering texts where:**
- Y-axis points UP (+Y = upward, -Y = downward)
- This is universal in mathematics, physics, engineering diagrams
- Pin 1 at "Y = +3.81" naturally means "3.81mm ABOVE origin"

**This causes the classic LLM error:**

```python
# Symbol library defines Pin 1 at (0, +3.81)
# LLM sees "+3.81" and thinks "positive means UP"
# LLM calculates: component_y + pin_y = 100 + 3.81 = 103.81
# Result: Pin 1 at Y=103.81 (HIGHER value = BOTTOM of screen) ❌ WRONG!

# What should happen:
# Negate first: +3.81 → -3.81
# Calculate: 100 + (-3.81) = 96.52
# Result: Pin 1 at Y=96.52 (LOWER value = TOP of screen) ✅ CORRECT!
```

**The trap:** Symbol library has Pin 1 with a POSITIVE Y value (+3.81), so LLM thinks "add this positive value" → places pin at BOTTOM instead of TOP.

**But KiCAD schematics use inverted Y-axis:**
- Y-axis points DOWN (+Y = downward, -Y = upward)
- This is standard in screen coordinates, image processing, UI frameworks
- Higher Y values = lower on screen (toward bottom)
- Lower Y values = higher on screen (toward top)

### 2. Inconsistent Contexts

**The confusion deepens because BOTH systems are used in the same workflow:**

1. **Symbol Libraries** (`.kicad_sym` files): Normal Y-axis (+Y up)
2. **Schematics** (`.kicad_sch` files): Inverted Y-axis (+Y down)

**This is like switching between metric and imperial mid-calculation** - easy to miss, catastrophic when wrong.

### 3. Natural Language is Ambiguous

When a user says "place pin 1 at the top", an LLM might interpret this as:
- **Mathematical**: "Pin 1 has positive Y coordinate" (WRONG in schematic space)
- **Visual**: "Pin 1 has lower Y value than pin 2" (CORRECT in schematic space)

**The value trap:**
- LLM sees Pin 1 defined with Y=+3.81 in symbol library (a "higher" positive value)
- LLM thinks: "positive/higher value means add it to component position"
- LLM calculates: 100 + 3.81 = 103.81
- Result: Pin 1 at Y=103.81 (higher value = BOTTOM of screen) ❌

**Counter-intuitively:** The pin with the "higher" symbol value (+3.81) must be SUBTRACTED to end up at the TOP (lower screen value 96.52)

### 4. Pin Numbers Create False Patterns

**Human intuition says:** "Higher pin numbers are further down"
**Reality in KiCAD:** Pin NUMBER has NO correlation with Y-axis direction

- A resistor might have pin 1 at top (lower Y) and pin 2 at bottom (higher Y)
- An IC might have pin 1 at top-left, and pin numbering can go counterclockwise
- Pin numbers are just identifiers, not positional indicators

---

## The Two Coordinate Systems

### System 1: Symbol Space (Library Definitions)

**Location**: `.kicad_sym` symbol library files
**Y-Axis**: NORMAL (+Y is UP, -Y is DOWN)

```
   +Y
    ↑
    |
    |  Pin 1 at (0, +3.81)  ← 3.81mm UPWARD from origin
    |
----+---→ +X
    |  (0, 0) origin
    |
    |  Pin 2 at (0, -3.81)  ← 3.81mm DOWNWARD from origin
    ↓
   -Y
```

**Example from `Device:R` resistor symbol:**
```lisp
(pin passive line (at 0 3.81 270) (length 2.54)
  (name "1" (effects (font (size 1.27 1.27))))
  (number "1" (effects (font (size 1.27 1.27))))
)
(pin passive line (at 0 -3.81 90) (length 2.54)
  (name "2" (effects (font (size 1.27 1.27))))
  (number "2" (effects (font (size 1.27 1.27))))
)
```

**Interpretation:**
- Pin 1: (0, +3.81) = 3.81mm ABOVE center (visually at TOP in symbol editor)
- Pin 2: (0, -3.81) = 3.81mm BELOW center (visually at BOTTOM in symbol editor)

### System 2: Schematic Space (Placed Components)

**Location**: `.kicad_sch` schematic files
**Y-Axis**: INVERTED (+Y is DOWN, -Y is UP)

```
   -Y (screen top)
    ↑
    |  Pin 1 at Y=96.52   ← LOWER Y value = visually HIGHER
    |
----+---→ +X
    |  Component at (100, 100)
    |
    |  Pin 2 at Y=103.81  ← HIGHER Y value = visually LOWER
    ↓
   +Y (screen bottom)
```

**CRITICAL RULE**: In schematic space:
- **Lower Y values** = visually HIGHER on screen (toward top)
- **Higher Y values** = visually LOWER on screen (toward bottom)
- **X-axis is normal** (increases left to right)

---

## The Critical Transformation

### The Formula

**When placing a component, you MUST negate the Y coordinate:**

```python
# Symbol library definition (normal Y-axis)
symbol_pin_position = (x_offset, y_offset)  # e.g., (0, +3.81) for pin 1

# Component placement in schematic
component_position = (component_x, component_y)  # e.g., (100, 100)

# CORRECT transformation:
schematic_pin_position = (
    component_x + x_offset,
    component_y + (-y_offset)  # NEGATE Y!
)

# Example for pin 1:
# Symbol: (0, +3.81)
# Component at: (100, 100)
# Result: (100, 100 - 3.81) = (100, 96.52)  ✅ Lower Y = visually at TOP
```

### Step-by-Step Transformation Order

**THIS ORDER IS CRITICAL:**

1. **First**: Negate Y coordinate (`y = -y`)
2. **Then**: Apply mirroring (if component is mirrored)
3. **Then**: Apply rotation (if component is rotated)
4. **Finally**: Add to component position

```python
def apply_transformation(point, origin, rotation, mirror):
    x, y = point

    # Step 1: CRITICAL - Convert symbol space to schematic space
    y = -y  # This single line is the entire fix

    # Step 2: Apply mirroring
    if mirror == "x":
        y = -y
    elif mirror == "y":
        x = -x

    # Step 3: Apply rotation
    if rotation == 90:
        x, y = y, -x
    elif rotation == 180:
        x, y = -x, -y
    elif rotation == 270:
        x, y = -y, x

    # Step 4: Translate to component position
    return (origin[0] + x, origin[1] + y)
```

**Without the `y = -y` line, ALL pin positions are wrong.**

---

## Visual Examples

### Example 1: Resistor at Rotation=0°

**Component Position**: (100, 100)
**Rotation**: 0° (no rotation)

```
Symbol Space (library):          Schematic Space (after transformation):
    Y↑                                  Y↓ (screen down)
    |                                   |
    |  Pin 1 (0, +3.81)                 |  (100, 96.52) Pin 1 ← TOP
    |     |                             |     |
----+-----|----→ X                      +-----|--------→ X
    | [Resistor]                        | [Resistor]
    |     |                             |     |
    |  Pin 2 (0, -3.81)                 |  (100, 103.81) Pin 2 ← BOTTOM

Transformation:
Pin 1: (100 + 0, 100 + (-3.81)) = (100, 96.52)   ✅ 96.52 < 100, so HIGHER on screen
Pin 2: (100 + 0, 100 + (--3.81)) = (100, 103.81) ✅ 103.81 > 100, so LOWER on screen
```

### Example 2: Resistor at Rotation=90° (Horizontal)

**Component Position**: (100, 100)
**Rotation**: 90° (rotated clockwise)

```
Symbol Space (library):          Schematic Space (after transformation):
    Y↑                                  Y↓
    |                                   |
    |  Pin 1 (0, +3.81)                 |
    |     |                             |
----+-----|----→ X              Pin 1 ← |
    | [Resistor]                 (96.52,100)--[Resistor]--(103.81,100) → Pin 2
    |     |                             |
    |  Pin 2 (0, -3.81)                 +------------------------------→ X

After negation: Pin 1 (0, -3.81), Pin 2 (0, +3.81)
After rotation 90°: Pin 1 (-3.81, 0), Pin 2 (+3.81, 0)
After translation: Pin 1 (96.52, 100), Pin 2 (103.81, 100)
```

### Example 3: The Bug Without Y-Negation

**This is the classic LLM error - seeing the positive value and adding it directly:**

```
Symbol library defines:
  Pin 1: (0, +3.81)   ← LLM sees "+3.81" and thinks "positive = add it"
  Pin 2: (0, -3.81)

LLM calculates (WITHOUT negation):
  Pin 1: (100 + 0, 100 + 3.81) = (100, 103.81)   ❌ WRONG - pin 1 at BOTTOM
  Pin 2: (100 + 0, 100 + (-3.81)) = (100, 96.52) ❌ WRONG - pin 2 at TOP

Schematic shows pins UPSIDE DOWN:
    |
    |  (100, 96.52) Pin 2 ← WRONG, should be Pin 1
    |     |
    | [Resistor]
    |     |
    |  (100, 103.81) Pin 1 ← WRONG, should be Pin 2
    |

The trap: Pin 1 has the "higher" value (+3.81 in symbol space)
          LLM adds it: 100 + 3.81 = 103.81
          But 103.81 is HIGHER Y = LOWER on screen = BOTTOM
```

**CORRECT - With Y negation:**

```
Symbol library defines:
  Pin 1: (0, +3.81)
  Pin 2: (0, -3.81)

Correct calculation (WITH negation):
  Pin 1: (100 + 0, 100 + (-3.81)) = (100, 96.52)   ✅ CORRECT - pin 1 at TOP
  Pin 2: (100 + 0, 100 + (--3.81)) = (100, 103.81) ✅ CORRECT - pin 2 at BOTTOM

Schematic shows pins correctly:
    |
    |  (100, 96.52) Pin 1 ← CORRECT at TOP (lower Y)
    |     |
    | [Resistor]
    |     |
    |  (100, 103.81) Pin 2 ← CORRECT at BOTTOM (higher Y)

The fix: Negate first: +3.81 → -3.81
         Then add: 100 + (-3.81) = 96.52
         96.52 is LOWER Y = HIGHER on screen = TOP
```

**Impact of the bug:**
- User connects wire to visual top pin (expecting pin 1)
- Actually connecting to pin 2 (because pins are swapped)
- Netlist is completely wrong
- Circuit doesn't work as designed

---

## Implementation Details

### Location in Codebase

**File**: `kicad_sch_api/core/geometry.py`
**Function**: `apply_transformation()`

```python
def apply_transformation(
    point: tuple[float, float],
    origin: tuple[float, float],
    rotation: int,
    mirror: str | None = None
) -> tuple[float, float]:
    """
    Transform a point from symbol space to schematic space.

    CRITICAL: This function handles the Y-axis inversion between
    symbol space (normal Y-axis) and schematic space (inverted Y-axis).

    Args:
        point: (x, y) in symbol space (normal Y-axis)
        origin: Component position in schematic space
        rotation: 0, 90, 180, or 270 degrees
        mirror: "x", "y", or None

    Returns:
        (x, y) in schematic space (inverted Y-axis)
    """
    x, y = point

    # CRITICAL: Negate Y to convert from symbol space (normal Y) to schematic space (inverted Y)
    # This MUST happen BEFORE rotation/mirroring
    y = -y
    logger.debug(f"After Y-axis inversion (symbol→schematic): ({x}, {y})")

    # Apply mirroring
    if mirror == "x":
        y = -y
    elif mirror == "y":
        x = -x

    # Apply rotation (in schematic space)
    if rotation == 90:
        x, y = y, -x
    elif rotation == 180:
        x, y = -x, -y
    elif rotation == 270:
        x, y = -y, x

    # Translate to component position
    return (origin[0] + x, origin[1] + y)
```

### Key Usage Points

**1. Pin Position Calculation** (`kicad_sch_api/core/components.py`):
```python
def list_component_pins(self, reference: str) -> list[PinInfo]:
    """Get all pins for a component with absolute positions."""
    component = self.get(reference)
    symbol_data = self._lib_cache.get_symbol(component.lib_id)

    pins = []
    for pin_def in symbol_data.pins:
        # Apply transformation (includes Y negation)
        absolute_pos = apply_transformation(
            pin_def.position,
            component.position,
            component.rotation,
            component.mirror
        )
        pins.append(PinInfo(..., position=absolute_pos))

    return pins
```

**2. Connectivity Analysis** (`kicad_sch_api/core/connectivity.py`):
```python
def find_connected_pins(self, position: tuple[float, float]) -> list[str]:
    """Find all pins at a given position (with tolerance)."""
    # Pin positions are already in schematic space (inverted Y)
    # Direct comparison is safe
    for component in self.components:
        for pin in component.pins:
            if distance(pin.position, position) < tolerance:
                connected_pins.append(f"{component.reference}.{pin.number}")
    return connected_pins
```

---

## Common Mistakes and Fixes

### Mistake 1: Forgetting Y Negation

**WRONG:**
```python
def get_pin_position(symbol_pin_pos, component_pos):
    return (
        component_pos[0] + symbol_pin_pos[0],
        component_pos[1] + symbol_pin_pos[1]  # ❌ Forgot to negate!
    )
```

**CORRECT:**
```python
def get_pin_position(symbol_pin_pos, component_pos):
    return (
        component_pos[0] + symbol_pin_pos[0],
        component_pos[1] + (-symbol_pin_pos[1])  # ✅ Negated Y
    )
```

### Mistake 2: Negating Y in Wrong Order

**WRONG - Negating after rotation:**
```python
def transform(point, rotation):
    x, y = point

    # Rotate first ❌
    if rotation == 90:
        x, y = y, -x

    # Then negate ❌ WRONG ORDER
    y = -y
    return (x, y)
```

**CORRECT - Negating before rotation:**
```python
def transform(point, rotation):
    x, y = point

    # Negate FIRST ✅
    y = -y

    # Then rotate ✅
    if rotation == 90:
        x, y = y, -x

    return (x, y)
```

**Why order matters:**
- Y negation converts coordinate systems (symbol → schematic)
- Rotation is a geometric operation IN schematic space
- Doing rotation in symbol space gives wrong results

### Mistake 3: Assuming Pin Numbers Correlate with Y Values

**WRONG assumption:**
```python
# ❌ NEVER assume pin numbers indicate position
if pin.number == "1":
    y_position = component.y - offset  # Assuming pin 1 is "above"
else:
    y_position = component.y + offset  # Assuming pin 2 is "below"
```

**CORRECT approach:**
```python
# ✅ ALWAYS use actual pin positions from symbol data
symbol_data = get_symbol(component.lib_id)
pin_def = symbol_data.get_pin(pin_number)
y_position = transform_pin_position(pin_def.position, component)
```

### Mistake 4: Comparing Positions in Different Spaces

**WRONG - Mixing coordinate systems:**
```python
# ❌ symbol_pin_pos is in symbol space (normal Y)
# ❌ wire_pos is in schematic space (inverted Y)
if symbol_pin_pos == wire_pos:  # NEVER EQUAL!
    print("Connected")
```

**CORRECT - Transform to same space first:**
```python
# ✅ Transform symbol pin to schematic space
schematic_pin_pos = apply_transformation(
    symbol_pin_pos, component.position, component.rotation
)
# ✅ Now both in schematic space
if schematic_pin_pos == wire_pos:
    print("Connected")
```

### Mistake 5: The "Higher Value = Higher Position" Fallacy

**WRONG assumption (LLM trained on normal Y-axis):**
```python
# ❌ LLM sees symbol definition with positive Y
symbol_pin1_y = +3.81  # "Positive means UP, higher position"
schematic_pin1_y = component_y + symbol_pin1_y  # Just add it
# Result: 100 + 3.81 = 103.81 (BOTTOM of screen!) ❌
```

**Why this is wrong:**
- Symbol space: +3.81 means "above" (normal Y-axis)
- Schematic space: 103.81 means "below" (inverted Y-axis)
- Direct addition places pin at WRONG location

**CORRECT approach:**
```python
# ✅ Negate to convert coordinate systems
symbol_pin1_y = +3.81
schematic_offset = -symbol_pin1_y  # Negate for coordinate system change
schematic_pin1_y = component_y + schematic_offset
# Result: 100 + (-3.81) = 96.52 (TOP of screen!) ✅
```

**The key insight:** A POSITIVE value in symbol space (+3.81) becomes a NEGATIVE offset in schematic space (-3.81), resulting in a LOWER Y coordinate (96.52), which displays HIGHER on screen (top).

---

## Diagnostic Quick Reference

### Is Your Code Wrong? Check These Patterns

**Pattern 1: Direct Addition of Symbol Y Coordinate**
```python
# ❌ WRONG - This is the classic LLM bug
y = component.y + symbol_pin.y
```
If you see this, you're missing the negation. Fix:
```python
# ✅ CORRECT
y = component.y + (-symbol_pin.y)
```

**Pattern 2: Pin 1 Appears at Bottom**
- Symptom: Pin 1 (defined with positive Y like +3.81) ends up with higher Y value than Pin 2
- Cause: Forgot to negate Y coordinate
- Fix: Add `y = -y` before rotation/translation

**Pattern 3: Wires Connect to Wrong Pins**
- Symptom: Visual inspection shows wire at top pin, but netlist shows connection to bottom pin
- Cause: Pin positions calculated without coordinate system conversion
- Fix: Use `apply_transformation()` which includes Y negation

**Pattern 4: Thinking "Higher Pin Number = Higher Y Value"**
- Symptom: Code assumes Pin 2 has higher Y than Pin 1
- Cause: Confusing pin NUMBER with pin POSITION
- Fix: Always get actual pin positions from symbol data + transformation

---

## Testing and Verification

### Test Coverage

**Unit Tests** (`tests/unit/test_pin_rotation.py`):
- 11 tests covering all rotation angles (0°, 90°, 180°, 270°)
- Verifies pin positions match expected schematic coordinates
- Tests both vertical and horizontal component orientations

**Reference Tests** (`tests/reference_tests/test_pin_rotation_*.py`):
- 8 tests against manually created KiCAD schematics
- Compares against `kicad-cli` netlist output
- Ensures exact compatibility with KiCAD's own calculations

**Connectivity Tests** (`tests/unit/test_connectivity_ps2_hierarchical.py`):
- 11 tests for hierarchical connectivity
- Verifies wires connect to correct pins after transformation
- Tests complex multi-sheet designs

### Running Tests

```bash
# Run all coordinate transformation tests
uv run pytest tests/unit/test_pin_rotation.py -v

# Run reference comparison tests
uv run pytest tests/reference_tests/test_pin_rotation_*.py -v

# Run connectivity tests
uv run pytest tests/unit/test_connectivity_ps2_hierarchical.py -v

# Run all tests
uv run pytest tests/ -v
```

### Manual Verification Steps

1. **Create test schematic:**
   ```python
   import kicad_sch_api as ksa

   sch = ksa.create_schematic("Test")
   r1 = sch.components.add('Device:R', 'R1', '10k', position=(100, 100))

   # Get pin positions
   pins = sch.components.list_component_pins('R1')
   for pin in pins:
       print(f"Pin {pin.number}: {pin.position}")

   sch.save("test.kicad_sch")
   ```

2. **Open in KiCAD** and verify:
   - Pin 1 is at visual top (lower Y value)
   - Pin 2 is at visual bottom (higher Y value)
   - Place wire - it connects to correct pin

3. **Compare netlists:**
   ```bash
   # Generate netlist with KiCAD
   kicad-cli sch export netlist test.kicad_sch -o kicad_netlist.txt

   # Compare with our pin positions
   # Pin numbers in netlist should match visual positions
   ```

### Debugging Coordinate Issues

**If pins appear wrong, add debug logging:**

```python
# In geometry.py
def apply_transformation(point, origin, rotation, mirror):
    x, y = point
    print(f"1. Input (symbol space): ({x}, {y})")

    y = -y
    print(f"2. After Y negation: ({x}, {y})")

    # Apply rotations...
    print(f"3. After rotation: ({x}, {y})")

    result = (origin[0] + x, origin[1] + y)
    print(f"4. Final (schematic space): {result}")

    return result
```

**Expected output for resistor pin 1:**
```
1. Input (symbol space): (0, 3.81)
2. After Y negation: (0, -3.81)
3. After rotation: (0, -3.81)  [no rotation]
4. Final (schematic space): (100, 96.52)
```

---

## Quick Reference

### Cheat Sheet

| Concept | Symbol Space | Schematic Space |
|---------|--------------|-----------------|
| **Y-axis direction** | +Y is UP ↑ | +Y is DOWN ↓ |
| **File type** | `.kicad_sym` | `.kicad_sch` |
| **Where defined** | Symbol libraries | Placed components |
| **Pin 1 at (0, +3.81)** | 3.81mm ABOVE origin | Transforms to LOWER Y (higher on screen) |
| **Pin 2 at (0, -3.81)** | 3.81mm BELOW origin | Transforms to HIGHER Y (lower on screen) |

### Mental Model

**Think of it as a flip:**

```
Symbol Space (library):     →  [FLIP VERTICALLY]  →  Schematic Space:

    +Y ↑                                                -Y ↑
       |                                                   |
     Pin 1                                               Pin 1
       |                                                   |
    [Symbol]                                           [Component]
       |                                                   |
     Pin 2                                               Pin 2
       |                                                   |
    -Y ↓                                                +Y ↓
```

### Key Takeaways

1. **Always negate Y** when transforming from symbol to schematic space
2. **Negate BEFORE rotation** - order matters
3. **Lower Y = higher on screen** in schematic space
4. **The value trap**: Pin 1 with +3.81 (positive value) must be negated to -3.81 to end up at TOP
5. **Never assume** pin numbers indicate position
6. **Always transform** before comparing positions
7. **Test against KiCAD** output to verify correctness

### The Core LLM Error Pattern

**LLM sees:** Pin 1 at Y=+3.81 (positive value)
**LLM thinks:** "Positive = add it" → 100 + 3.81 = 103.81
**Result:** Pin 1 at BOTTOM (higher Y) ❌

**Should be:** Negate first → 100 + (-3.81) = 96.52
**Result:** Pin 1 at TOP (lower Y) ✅

**Remember:** The pin with the "higher" symbol value (+3.81) must be SUBTRACTED to appear at the TOP visually.

### The Golden Rule

**WHEN IN DOUBT: Check if you negated Y before doing anything else**

This single transformation is responsible for:
- ✅ Correct pin positions
- ✅ Proper connectivity analysis
- ✅ Accurate wire routing
- ✅ Correct hierarchical connections
- ✅ Valid netlist generation

**Without it, nothing works.**

---

## Related Documentation

- **CLAUDE.md**: Project overview and development guidelines
- **docs/ADR.md**: Architecture decision records
- **docs/HIERARCHY_FEATURES.md**: Hierarchical schematic features
- **kicad_sch_api/core/geometry.py**: Implementation of transformation
- **tests/unit/test_pin_rotation.py**: Comprehensive test suite

---

## Credits

This issue was discovered during hierarchical connectivity implementation (PR #91) when pin positions didn't match KiCAD's output. The fix was a single line (`y = -y`) that transformed all pin calculations from broken to correct.

**Key insight**: "pin 2 is a higher number than pin 1, but pin 1 is at top" - this observation led to discovering the dual coordinate system issue.

---

**Document Status**: Complete, covers issue #123
**Last Updated**: 2025-11-06
**Maintainer**: kicad-sch-api project
