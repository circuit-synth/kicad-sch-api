# PRD: Complete Property Data Model

**Issue:** #74 - Property rotations and formatting lost on save
**Branch:** `feature/complete-property-data-model`
**Status:** Ready for Review
**Priority:** High (breaks bidirectional workflows)

---

## Executive Summary

kicad-sch-api currently only captures property **names** and **values**, losing all formatting data (position, rotation, font, justification, hide flags). This breaks round-trip fidelity and the bidirectional workflow between Python and KiCad.

**Solution:** Implement complete property data structures that capture all KiCad property attributes and reconstruct them correctly.

---

## 1. Problem Statement

### 1.1 Current Behavior (BROKEN)

```python
# User rotates component in KiCad → property text rotates too
# User runs Python script
sch = Schematic.load("design.kicad_sch")
sch.save("design.kicad_sch")
# Result: All property rotations reset to 0° ❌
```

### 1.2 Impact

**For circuit-synth bidirectional tests:**
- Test 20 fails: Component rotation preserved, but property text renders wrong
- Any manual KiCad formatting is lost on Python regeneration
- Forces users to re-format properties after every code generation

**For kicad-sch-api users:**
- Violates "complete round-trip fidelity" principle
- Cannot use kicad-sch-api for mixed manual+programmatic workflows
- Data loss on every save

---

## 2. Investigation Findings

### 2.1 Complete KiCad Property Structure

From real schematic analysis:

```lisp
(property "Reference" "R1"
    (at 102 99 45)              ; position (x, y) + rotation
    (effects
        (font (size 1.27 1.27))  ; font width, height
        (justify left)           ; left|right|center (optional)
        (hide yes)               ; visibility (optional)
    )
)
```

**Attributes:**
1. **name**: String (e.g., "Reference")
2. **value**: String (e.g., "R1")
3. **position**: `(x, y)` tuple of floats
4. **rotation**: Float (degrees, 0-360)
5. **font_size**: `(width, height)` tuple
6. **justification**: String ("left"|"right"|"center"|None)
7. **hide**: Boolean

### 2.2 What We Currently Capture

```python
# In _parse_property():
return {
    "name": item[1],    # ✓ Captured
    "value": item[2],   # ✓ Captured
}
# Everything else: ❌ LOST
```

### 2.3 Data Flow

**LOADING:**
```
KiCad File
  → Parser.parse()
    → SymbolParser._parse_symbol()
      → _parse_property() [INCOMPLETE - only name/value]
      → Returns symbol_data dict
    → dict converted to SchematicSymbol dataclass
  → Schematic.components
```

**SAVING:**
```
SchematicSymbol
  → SymbolParser._symbol_to_sexp()
    → _create_property_with_positioning() [RECREATES with defaults]
  → S-expression
    → Formatter
  → KiCad File
```

---

## 3. Proposed Solution

### 3.1 Architecture

**Create proper data structures** that mirror KiCad's property format:

1. `PropertyEffects` - Font, justification, hide flag
2. `ComponentProperty` - Complete property with all attributes
3. Update `SchematicSymbol` to store property objects

### 3.2 Data Model

#### PropertyEffects

```python
@dataclass
class PropertyEffects:
    """Font and formatting effects for a property."""
    font_size: tuple[float, float] = (1.27, 1.27)  # (width, height)
    justification: Optional[str] = None  # "left"|"right"|"center"|None
    hide: bool = False

    def to_sexp(self) -> List:
        """Convert to S-expression: (effects ...)"""
        import sexpdata

        effects = [sexpdata.Symbol("effects")]

        # Font
        effects.append([
            sexpdata.Symbol("font"),
            [sexpdata.Symbol("size"), self.font_size[0], self.font_size[1]]
        ])

        # Justification (optional)
        if self.justification:
            effects.append([
                sexpdata.Symbol("justify"),
                sexpdata.Symbol(self.justification)
            ])

        # Hide flag (optional)
        if self.hide:
            effects.append([
                sexpdata.Symbol("hide"),
                sexpdata.Symbol("yes")
            ])

        return effects
```

#### ComponentProperty

```python
@dataclass
class ComponentProperty:
    """
    A component property with complete formatting data.

    Represents: (property "Name" "Value" (at x y rotation) (effects ...))
    """
    name: str
    value: str
    position: Optional[tuple[float, float]] = None  # (x, y) - None = use defaults
    rotation: float = 0.0  # degrees
    effects: PropertyEffects = field(default_factory=PropertyEffects)

    def to_sexp(self) -> List:
        """Convert to complete S-expression."""
        import sexpdata

        sexp = [
            sexpdata.Symbol("property"),
            self.name,
            self.value,
        ]

        # Position (required in KiCad files)
        if self.position:
            x, y = self.position
            # Format as int if whole number
            x = int(x) if x == int(x) else x
            y = int(y) if y == int(y) else y
            r = int(self.rotation) if self.rotation == int(self.rotation) else self.rotation
            sexp.append([sexpdata.Symbol("at"), x, y, r])

        # Effects
        sexp.append(self.effects.to_sexp())

        return sexp

    @classmethod
    def from_sexp(cls, sexp: List) -> "ComponentProperty":
        """Parse from S-expression."""
        # Will be implemented in SymbolParser._parse_property()
        pass
```

#### Updated SchematicSymbol

```python
@dataclass
class SchematicSymbol:
    """Component symbol in a schematic."""

    # Existing fields
    uuid: str
    lib_id: str
    position: Point
    rotation: float = 0.0
    unit: int = 1
    in_bom: bool = True
    on_board: bool = True
    pins: List[SchematicPin] = field(default_factory=list)

    # NEW: Property objects instead of just values
    reference_property: Optional[ComponentProperty] = None
    value_property: Optional[ComponentProperty] = None
    footprint_property: Optional[ComponentProperty] = None
    custom_properties: Dict[str, ComponentProperty] = field(default_factory=dict)

    # Backward-compatible accessors
    @property
    def reference(self) -> str:
        """Get reference value (backward compatible)."""
        return self.reference_property.value if self.reference_property else ""

    @reference.setter
    def reference(self, value: str):
        """Set reference value, preserving formatting."""
        if self.reference_property:
            self.reference_property.value = value
        else:
            # Create new property with defaults
            self.reference_property = ComponentProperty("Reference", value)

    @property
    def value(self) -> str:
        """Get value (backward compatible)."""
        return self.value_property.value if self.value_property else ""

    @value.setter
    def value(self, value: str):
        """Set value, preserving formatting."""
        if self.value_property:
            self.value_property.value = value
        else:
            self.value_property = ComponentProperty("Value", value)

    @property
    def footprint(self) -> Optional[str]:
        """Get footprint value (backward compatible)."""
        return self.footprint_property.value if self.footprint_property else None

    @footprint.setter
    def footprint(self, value: Optional[str]):
        """Set footprint value, preserving formatting."""
        if value is None:
            self.footprint_property = None
        elif self.footprint_property:
            self.footprint_property.value = value
        else:
            # Footprint defaults to hidden
            self.footprint_property = ComponentProperty(
                "Footprint",
                value,
                effects=PropertyEffects(hide=True)
            )

    @property
    def properties(self) -> Dict[str, str]:
        """Get custom property values (backward compatible)."""
        return {name: prop.value for name, prop in self.custom_properties.items()}
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Define Data Structures

**File:** `kicad_sch_api/core/types.py`

**Tasks:**
1. Add `PropertyEffects` dataclass
2. Add `ComponentProperty` dataclass with `to_sexp()` method
3. Update `SchematicSymbol`:
   - Add property object fields
   - Add backward-compatible accessors
   - Deprecate direct `properties` dict access (keep for compatibility)

**Estimated Time:** 1 hour

### 4.2 Phase 2: Update Parsing

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

**Tasks:**

1. **Rewrite `_parse_property()`:**
```python
def _parse_property(self, item: List[Any]) -> Optional[ComponentProperty]:
    """Parse complete property with all attributes."""
    if len(item) < 3:
        return None

    prop = ComponentProperty(
        name=str(item[1]),
        value=str(item[2])
    )

    # Parse sub-elements
    for sub_item in item[3:]:
        if not isinstance(sub_item, list) or len(sub_item) == 0:
            continue

        element_type = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None

        # Parse position and rotation
        if element_type == "at" and len(sub_item) >= 3:
            prop.position = (float(sub_item[1]), float(sub_item[2]))
            if len(sub_item) > 3:
                prop.rotation = float(sub_item[3])

        # Parse effects
        elif element_type == "effects":
            prop.effects = self._parse_property_effects(sub_item)

    return prop

def _parse_property_effects(self, effects_sexp: List) -> PropertyEffects:
    """Parse (effects ...) sub-element."""
    effects = PropertyEffects()

    for item in effects_sexp[1:]:
        if not isinstance(item, list):
            continue

        element_type = str(item[0]) if isinstance(item[0], sexpdata.Symbol) else None

        if element_type == "font":
            for font_item in item[1:]:
                if isinstance(font_item, list) and len(font_item) >= 3:
                    if str(font_item[0]) == "size":
                        effects.font_size = (float(font_item[1]), float(font_item[2]))

        elif element_type == "justify" and len(item) > 1:
            effects.justification = str(item[1])

        elif element_type == "hide":
            effects.hide = True

    return effects
```

2. **Update `_parse_symbol()`:**
```python
# In _parse_symbol(), when handling properties:
elif element_type == "property":
    prop = self._parse_property(sub_item)  # Returns ComponentProperty
    if prop:
        if prop.name == "Reference":
            symbol_data["reference_property"] = prop
        elif prop.name == "Value":
            symbol_data["value_property"] = prop
        elif prop.name == "Footprint":
            symbol_data["footprint_property"] = prop
        else:
            symbol_data["custom_properties"][prop.name] = prop
```

**Estimated Time:** 2 hours

### 4.3 Phase 3: Update Writing

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

**Tasks:**

1. **Update `_symbol_to_sexp()` to use property objects:**
```python
def _symbol_to_sexp(self, symbol_data: Dict[str, Any], schematic_uuid: str = None) -> List[Any]:
    # ... lib_id, position, rotation, uuid ...

    # Reference property
    ref_prop = symbol_data.get("reference_property")
    if ref_prop:
        sexp.append(ref_prop.to_sexp())
    elif symbol_data.get("reference"):
        # Fallback: create with defaults (for programmatically created components)
        ref_prop = ComponentProperty(
            "Reference",
            symbol_data["reference"],
            effects=PropertyEffects(hide=("power:" in symbol_data.get("lib_id", "")))
        )
        sexp.append(ref_prop.to_sexp())

    # Value property
    val_prop = symbol_data.get("value_property")
    if val_prop:
        sexp.append(val_prop.to_sexp())
    elif symbol_data.get("value"):
        val_prop = ComponentProperty("Value", symbol_data["value"])
        sexp.append(val_prop.to_sexp())

    # Footprint property
    fp_prop = symbol_data.get("footprint_property")
    if fp_prop:
        sexp.append(fp_prop.to_sexp())
    elif symbol_data.get("footprint") is not None:
        fp_prop = ComponentProperty(
            "Footprint",
            symbol_data["footprint"],
            effects=PropertyEffects(hide=True)
        )
        sexp.append(fp_prop.to_sexp())

    # Custom properties
    for prop_name, prop in symbol_data.get("custom_properties", {}).items():
        sexp.append(prop.to_sexp())

    # ... pins, instances, etc ...
```

2. **Remove/deprecate `_create_property_with_positioning()`** if no longer needed

**Estimated Time:** 1.5 hours

### 4.4 Phase 4: Update Dataclass Conversion

**File:** Find where `symbol_data` dict is converted to `SchematicSymbol`

**Task:** Ensure property object fields are passed correctly

**Estimated Time:** 0.5 hours

---

## 5. Testing Strategy

### 5.1 Unit Tests

**File:** `tests/test_property_data_model.py` (new)

#### Test 5.1.1: Parse Property with All Attributes
```python
def test_parse_complete_property():
    """Test parsing property with position, rotation, and effects."""
    from kicad_sch_api.parsers.elements.symbol_parser import SymbolParser
    import sexpdata

    parser = SymbolParser()

    # Sample property S-expression
    prop_sexp = [
        sexpdata.Symbol("property"),
        "Reference",
        "R1",
        [sexpdata.Symbol("at"), 102.0, 99.0, 45.0],
        [
            sexpdata.Symbol("effects"),
            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
            [sexpdata.Symbol("justify"), sexpdata.Symbol("left")],
        ]
    ]

    prop = parser._parse_property(prop_sexp)

    assert prop.name == "Reference"
    assert prop.value == "R1"
    assert prop.position == (102.0, 99.0)
    assert prop.rotation == 45.0
    assert prop.effects.font_size == (1.27, 1.27)
    assert prop.effects.justification == "left"
    assert prop.effects.hide == False
```

#### Test 5.1.2: Property to S-Expression
```python
def test_property_to_sexp():
    """Test converting ComponentProperty to S-expression."""
    from kicad_sch_api.core.types import ComponentProperty, PropertyEffects

    prop = ComponentProperty(
        name="Reference",
        value="R1",
        position=(102.0, 99.0),
        rotation=45.0,
        effects=PropertyEffects(font_size=(1.27, 1.27), justification="left")
    )

    sexp = prop.to_sexp()

    # Verify structure
    assert str(sexp[0]) == "property"
    assert sexp[1] == "Reference"
    assert sexp[2] == "R1"

    # Find (at x y rotation)
    at_elem = next(e for e in sexp if isinstance(e, list) and str(e[0]) == "at")
    assert at_elem[1] == 102.0
    assert at_elem[2] == 99.0
    assert at_elem[3] == 45.0

    # Find (effects ...)
    effects_elem = next(e for e in sexp if isinstance(e, list) and str(e[0]) == "effects")
    assert effects_elem is not None
```

### 5.2 Integration Tests

**File:** `tests/test_property_roundtrip.py` (new)

#### Test 5.2.1: Complete Round-Trip
```python
def test_property_data_roundtrip():
    """Test that ALL property data survives load/save cycle."""
    from kicad_sch_api import Schematic
    from pathlib import Path

    # Create test schematic with specific property formatting
    test_content = '''
(kicad_sch (version 20250114) (generator "eeschema")
  (uuid "test-uuid")
  (paper "A4")
  (lib_symbols
    (symbol "Device:R"
      (pin_numbers (hide yes))
      (pin_names (offset 0))
      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0.254)) (fill (type none))))
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )
  )
  (symbol
    (lib_id "Device:R")
    (at 100 100 90)
    (unit 1)
    (uuid "comp-uuid")
    (property "Reference" "R1"
      (at 102 99 45)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Value" "10k"
      (at 102 101 135)
      (effects (font (size 1.5 1.5)) (justify right))
    )
    (property "Footprint" "Resistor_SMD:R_0603_1608Metric"
      (at 98 100 90)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
)
'''

    test_file = Path("test_roundtrip.kicad_sch")
    test_file.write_text(test_content)

    try:
        # Load
        sch = Schematic.load(str(test_file))
        comp = sch.components[0]

        # Verify parsed data
        assert comp.reference == "R1"
        assert comp.reference_property.position == (102.0, 99.0)
        assert comp.reference_property.rotation == 45.0
        assert comp.reference_property.effects.justification == "left"

        assert comp.value == "10k"
        assert comp.value_property.position == (102.0, 101.0)
        assert comp.value_property.rotation == 135.0
        assert comp.value_property.effects.font_size == (1.5, 1.5)
        assert comp.value_property.effects.justification == "right"

        assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"
        assert comp.footprint_property.effects.hide == True

        # Save
        sch.save(str(test_file))

        # Reload
        sch2 = Schematic.load(str(test_file))
        comp2 = sch2.components[0]

        # Verify ALL data preserved
        assert comp2.reference_property.position == (102.0, 99.0)
        assert comp2.reference_property.rotation == 45.0  # ← CRITICAL
        assert comp2.reference_property.effects.justification == "left"

        assert comp2.value_property.rotation == 135.0  # ← CRITICAL
        assert comp2.value_property.effects.font_size == (1.5, 1.5)
        assert comp2.value_property.effects.justification == "right"

        assert comp2.footprint_property.effects.hide == True

    finally:
        test_file.unlink(missing_ok=True)
```

#### Test 5.2.2: Property Value Updates Preserve Formatting
```python
def test_value_update_preserves_formatting():
    """Test that updating property values preserves formatting."""
    # ... load schematic with formatted properties ...

    # Update value
    comp.value = "47k"

    # Save and reload
    sch.save(str(test_file))
    sch2 = Schematic.load(str(test_file))

    # Value changed, formatting preserved
    assert sch2.components[0].value == "47k"
    assert sch2.components[0].value_property.rotation == 135.0
    assert sch2.components[0].value_property.effects.font_size == (1.5, 1.5)
```

#### Test 5.2.3: Programmatic Component Creation
```python
def test_programmatic_component_has_defaults():
    """Test that components created programmatically get sensible defaults."""
    from kicad_sch_api import Schematic

    sch = Schematic.create("test")

    # Add component (no formatting specified)
    comp = sch.add_component(
        "Device:R",
        reference="R1",
        value="10k",
        position=(100, 100)
    )

    # Should have property objects with defaults
    assert comp.reference_property is not None
    assert comp.reference_property.value == "R1"
    assert comp.reference_property.rotation == 0.0  # Default
    assert comp.reference_property.effects.font_size == (1.27, 1.27)  # Default

    # Save and verify
    test_file = Path("test_programmatic.kicad_sch")
    sch.save(str(test_file))

    # Should have valid S-expressions
    content = test_file.read_text()
    assert 'property "Reference"' in content
    assert 'at' in content
    assert 'effects' in content

    test_file.unlink()
```

### 5.3 Backward Compatibility Tests

**File:** `tests/test_backward_compatibility.py` (new)

#### Test 5.3.1: Old Property Access Patterns Work
```python
def test_old_property_access_works():
    """Test that code using old API still works."""
    sch = Schematic.load("test.kicad_sch")
    comp = sch.components[0]

    # Old API should work
    assert isinstance(comp.reference, str)
    assert isinstance(comp.value, str)
    assert isinstance(comp.footprint, str) or comp.footprint is None

    # Setting should work
    comp.reference = "R2"
    comp.value = "22k"
    comp.footprint = "Resistor_SMD:R_0805_2012Metric"

    # Should preserve formatting when set
    sch.save("test_modified.kicad_sch")
    # ... verify formatting preserved ...
```

### 5.4 Existing Tests

**Task:** Run existing test suite and fix any breaks

```bash
pytest tests/ -v
```

Expected: Most tests should pass due to backward-compatible accessors. Fix any that break.

---

## 6. Breaking Changes

### 6.1 For External Users (if any)

**Public API changes:**
- `SchematicSymbol` internal structure changes
- New fields: `reference_property`, `value_property`, `footprint_property`, `custom_properties`
- Old fields maintained as properties for backward compatibility

**Migration:**
```python
# Old way (still works):
comp.reference = "R1"
print(comp.reference)

# New way (for full control):
comp.reference_property.rotation = 45.0
print(comp.reference_property.rotation)
```

### 6.2 For circuit-synth

**Required changes:**
1. Update kicad-sch-api submodule pointer
2. Test all bidirectional tests
3. Update any code that directly accesses `component._data`
4. No API changes needed for most code (backward compatible)

---

## 7. Success Criteria

✅ **Functional:**
- [ ] Property rotations preserved through load/save
- [ ] Property positions preserved
- [ ] Property font sizes preserved
- [ ] Property justification preserved
- [ ] Property hide flags preserved
- [ ] Property values can be updated via API
- [ ] New components get sensible defaults

✅ **Quality:**
- [ ] All new unit tests pass
- [ ] All integration tests pass
- [ ] All existing tests pass
- [ ] Type hints complete and correct
- [ ] Code coverage >80%

✅ **Documentation:**
- [ ] CHANGELOG.md updated
- [ ] Inline code documentation complete
- [ ] PRD this document serves as design doc

---

## 8. Risks and Mitigation

### Risk 1: Dataclass Conversion Issues
**Risk:** `symbol_data` dict → `SchematicSymbol` conversion might filter out new fields

**Mitigation:** Investigate conversion code path and update to pass property objects

**Status:** Need to trace conversion location

### Risk 2: Existing Code Breaks
**Risk:** Code that directly accesses properties dict might break

**Mitigation:**
- Backward-compatible accessors maintain old API
- Run full test suite
- Fix any breakage before merge

### Risk 3: Performance Impact
**Risk:** More complex data structures might slow parsing

**Mitigation:**
- Property objects are lightweight
- No significant impact expected
- Benchmark if concerned

---

## 9. Timeline

**Total Estimated Time:** 6-8 hours

| Phase | Time | Description |
|-------|------|-------------|
| Phase 1 | 1h | Define data structures |
| Phase 2 | 2h | Update parsing |
| Phase 3 | 1.5h | Update writing |
| Phase 4 | 0.5h | Fix dataclass conversion |
| Testing | 2h | Write and run all tests |
| Debugging | 1h | Fix any issues |
| Documentation | 0.5h | Update CHANGELOG |

---

## 10. Follow-Up Work

### 10.1 Future Enhancements

1. **Custom property formatting support** - Currently custom properties use defaults
2. **Property positioning calculation** - Smart defaults based on component size
3. **Property auto-rotation** - Optionally rotate properties with component

### 10.2 Related Issues

- Test 20 in circuit-synth will pass once this is fixed
- Any other formatting issues in bidirectional tests

---

## 11. Appendix

### A. Example Property Data

**Simple property (minimal):**
```python
ComponentProperty(
    name="Reference",
    value="R1"
)
# Uses default position, rotation=0, standard effects
```

**Formatted property (complete):**
```python
ComponentProperty(
    name="Reference",
    value="R1",
    position=(102.0, 99.0),
    rotation=45.0,
    effects=PropertyEffects(
        font_size=(1.27, 1.27),
        justification="left",
        hide=False
    )
)
```

### B. File Structure

```
kicad_sch_api/
├── core/
│   └── types.py          # PropertyEffects, ComponentProperty, SchematicSymbol
├── parsers/
│   └── elements/
│       └── symbol_parser.py  # Parsing and writing logic
└── tests/
    ├── test_property_data_model.py
    ├── test_property_roundtrip.py
    └── test_backward_compatibility.py
```

---

**Status:** ✅ Ready for review and implementation
**Next Step:** Review this PRD → Get approval → Begin Phase 1
