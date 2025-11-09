# PRD: Text Effects Preservation and Modification

## Overview

Parse, preserve, and allow modification of KiCAD's text effects (font, size, position, rotation, justification, visibility) for all schematic text elements. No custom abstractions - just read what KiCAD has, let users modify it, and write it back correctly.

**Technical goal**: Extend existing S-expression preservation to support modifying text effects across all text-containing elements.

## Success Criteria

- [ ] Parse effects from component properties (Reference, Value, Footprint, custom)
- [ ] Parse effects from labels (local, global, hierarchical)
- [ ] Parse effects from text and text boxes
- [ ] Parse effects from sheet properties
- [ ] Provide API to modify parsed effects
- [ ] Preserve unmodified effects byte-perfectly
- [ ] Write modified effects in correct KiCAD format
- [ ] All tests pass
- [ ] Format preservation validated against reference schematics

## Functional Requirements

### REQ-1: Parse KiCAD Effects

Parse the `(effects ...)` S-expression from all text elements:

```
(effects
  (font
    (size 1.27 1.27)
    [bold]
    [italic]
    [(face "Arial")]
    [(thickness 0.3)]
  )
  [(justify left bottom)]
  [(hide yes)]
)
```

Extract to dictionary format:
```python
{
    'font_size': (1.27, 1.27),
    'bold': True,  # or False if absent
    'italic': False,
    'font_face': 'Arial',  # or None
    'font_thickness': 0.3,  # or None
    'justify_h': 'left',  # or None
    'justify_v': 'bottom',  # or None
    'visible': False  # True if hide absent
}
```

### REQ-2: Modify Component Property Effects

Simple API to change property effects:

```python
# Get component
comp = sch.get_component("R1")

# Modify Reference property effects
comp.set_property_effects("Reference", {
    'font_size': (1.5, 1.5),
    'bold': True,
    'position': (0, -2.54),  # Relative to component
    'rotation': 0
})

# Modify Value property effects
comp.set_property_effects("Value", {
    'font_size': (1.2, 1.2),
    'italic': True,
    'visible': True
})

# Modify Footprint visibility
comp.set_property_effects("Footprint", {
    'visible': False
})

# Get current effects
ref_effects = comp.get_property_effects("Reference")
# Returns: {'font_size': (1.5, 1.5), 'bold': True, ...}
```

### REQ-3: Modify Label Effects

Simple API for label text effects:

```python
# Create label (uses KiCAD defaults)
label = sch.add_label("VCC", position=(100, 100))

# Modify effects
label.set_effects({
    'font_size': (1.5, 1.5),
    'bold': True,
    'justify_h': 'center'
})

# Get current effects
effects = label.get_effects()
```

Same for global labels and hierarchical labels.

### REQ-4: Modify Text and Text Box Effects

```python
# Free text
text = sch.add_text("Title", position=(50, 50))
text.set_effects({
    'font_size': (3.0, 3.0),
    'bold': True,
    'justify_h': 'center'
})

# Text box
text_box = sch.add_text_box("Notes", position=(100, 100), size=(50, 30))
text_box.set_effects({
    'font_size': (1.0, 1.0),
    'italic': True
})
```

### REQ-5: Modify Sheet Property Effects

```python
# Modify sheet name and filename property effects
sheet = sch.get_sheet_by_name("Power Supply")
sheet.set_name_effects({
    'font_size': (1.5, 1.5),
    'bold': True
})
sheet.set_filename_effects({
    'font_size': (1.0, 1.0),
    'italic': True
})
```

### REQ-6: Format Preservation

When modifying effects:

1. **Parse existing S-expression** from `__sexp_*` or element data
2. **Extract current values** for all properties
3. **Merge user changes** (only override specified keys)
4. **Regenerate S-expression** in KiCAD format
5. **Preserve field order** and structure

Example:
```python
# Original S-expression from KiCAD file:
# (property "Reference" "R1"
#     (at 0 -2.54 0)
#     (effects
#         (font (size 1.27 1.27))
#         (justify left)
#     )
# )

# User modifies:
comp.set_property_effects("Reference", {'bold': True})

# Resulting S-expression preserves everything except adds bold:
# (property "Reference" "R1"
#     (at 0 -2.54 0)
#     (effects
#         (font (size 1.27 1.27) bold)  # Added bold
#         (justify left)                 # Preserved
#     )
# )
```

## KiCAD Format Specifications

### Effects S-Expression

Complete format:
```
(effects
  (font
    [(face FONT_NAME)]
    (size HEIGHT WIDTH)
    [(thickness THICKNESS)]
    [bold]
    [italic]
  )
  [(justify [left|right|center] [top|bottom|center])]
  [(hide yes)]
)
```

### Position and Rotation

Property position is stored separately from effects:
```
(property "Reference" "R1"
    (at X Y ROTATION)  # Position relative to component, with rotation
    (effects ...)
)
```

For labels and text:
```
(label "VCC"
    (at X Y ROTATION)  # Absolute position and rotation
    (effects ...)
)
```

## Technical Constraints

### Backward Compatibility

- Existing code without effects modification works unchanged
- Default behavior matches current auto-generation
- Elements loaded from files preserve original formatting unless explicitly modified

### Format Preservation

- Use existing `__sexp_*` preservation mechanism
- Parse effects on-demand when modifying
- Regenerate only when user explicitly changes effects
- Preserve byte-perfect format for unmodified elements

### KiCAD Compatibility

- Output matches KiCAD 7.0, 8.0, 9.0 format
- No custom S-expression sections
- All effects are standard KiCAD properties

## Reference Schematic Requirements

Create reference schematics demonstrating:

1. **Component with modified property effects** - resistor with custom Reference/Value fonts
2. **Labels with modified effects** - local, global, hierarchical with custom fonts
3. **Text with modified effects** - free text with large, bold font
4. **Text box with modified effects** - text box with italic text

Parse these reference schematics, modify effects programmatically, verify output matches expected format.

## Edge Cases

### Empty/Null Values in Modifications

```python
# Only modify specified keys, preserve others
comp.set_property_effects("Reference", {'bold': True})
# Preserves existing font_size, justify, etc.

# Explicit None means "use KiCAD default"
comp.set_property_effects("Reference", {'font_size': None})
# Removes custom size, uses KiCAD default (1.27, 1.27)
```

### Invalid Values

- Invalid font_size: Raise ValueError
- Invalid justify values: Raise ValueError with valid options
- Unrecognized keys: Ignore with warning

### Loaded vs New Elements

- **Loaded elements**: Parse existing effects, merge with user changes
- **New elements**: Generate effects from user values or KiCAD defaults
- Preserve unmodified fields in both cases

## Impact Analysis

### Core Types (`kicad_sch_api/core/types.py`)

Add methods to existing dataclasses:

```python
@dataclass
class SchematicSymbol:
    ...
    def get_property_effects(self, prop_name: str) -> Dict[str, Any]:
        """Get effects for a property."""
        ...

    def set_property_effects(self, prop_name: str, effects: Dict[str, Any]):
        """Set effects for a property."""
        ...

@dataclass
class Label:
    ...
    def get_effects(self) -> Dict[str, Any]:
        """Get label text effects."""
        ...

    def set_effects(self, effects: Dict[str, Any]):
        """Set label text effects."""
        ...

# Similar for Text, TextBox, Sheet, etc.
```

### Parser Changes (`kicad_sch_api/parsers/`)

**Minimal changes** - parsers already preserve full S-expressions:
- Add helper: `parse_effects_sexp()` to extract effects dict from S-expression
- Parsers continue to store full S-expressions

### Formatter Changes (`kicad_sch_api/parsers/`)

**Extend existing formatters**:
- Add helper: `merge_effects()` to combine existing + user changes
- Add helper: `create_effects_sexp()` to generate S-expression from dict
- Modify property/label/text emission to use merged effects

### MCP Server Changes

- Add `get_property_effects` and `set_property_effects` MCP tools
- Add `set_label_effects`, `set_text_effects` MCP tools
- Document effects dict structure

## Out of Scope

- Named style registries
- Style inheritance
- Auto-layout algorithms
- Label collision detection
- Batch operations
- Visual preview
- Semantic position strings ("above", "below") - use numeric offsets instead

## Acceptance Criteria

### Functionality

- [ ] Can parse effects from all text element types
- [ ] Can modify component property effects
- [ ] Can modify label effects (local, global, hierarchical)
- [ ] Can modify text and text box effects
- [ ] Can modify sheet property effects
- [ ] Effects merge correctly (user values override existing)
- [ ] Works for loaded elements (preserves unmodified fields)
- [ ] Works for newly created elements

### Testing

- [ ] All existing tests pass
- [ ] Unit tests for effects parsing
- [ ] Unit tests for effects merging
- [ ] Reference tests validate exact KiCAD format
- [ ] Round-trip tests ensure preservation of unmodified fields
- [ ] Tests for all element types (properties, labels, text, text boxes, sheets)

### Format Preservation

- [ ] Loaded elements with unmodified effects preserve byte-perfect S-expression
- [ ] Modified effects only change specified fields
- [ ] Field ordering matches KiCAD standard
- [ ] All element types handled correctly
- [ ] Effects S-expression structure matches KiCAD exactly

### Documentation

- [ ] API documentation for get/set effects methods
- [ ] Examples for each element type
- [ ] MCP tool descriptions updated
- [ ] PRD reviewed and approved

## Related Issues

- #134: Add User Control for Component Label Positioning and Styling

## Priority

**High** - Required to truly preserve component properties and enable programmatic styling

## Effort Estimate

**Medium** - Straightforward extension of existing S-expression preservation:
- Effects parsing helpers: Small
- Component property effects: Small (builds on existing)
- Label effects: Small
- Text/TextBox effects: Small
- Sheet effects: Small
- Testing: Medium
- Documentation: Small

**Total estimate**: 1-2 weeks for complete implementation and testing
