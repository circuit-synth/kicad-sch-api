# Pre-Launch Audit - kicad-sch-api

**Status:** Phase 1 - Discovery & Planning
**Date Started:** 2025-11-05
**Goal:** Comprehensive verification of all CRUD operations, documentation accuracy, and feature completeness

---

## 🎯 Audit Objectives

1. **CRUD Completeness**: Verify Create, Read, Update, Delete operations for all schematic elements
2. **Documentation Accuracy**: Ensure README, API docs, examples match actual implementation
3. **Format Preservation**: Confirm exact KiCAD compatibility for all operations
4. **Edge Case Coverage**: Test boundary conditions, error handling, validation
5. **Example Validation**: Verify all code examples actually work

---

## 📊 Discovery Phase - Inventory

### Core API Surface (from `__init__.py`)

**Exposed Classes:**
- `Schematic` - Main schematic class
- `Component` - Component wrapper
- `ComponentCollection` - Component management
- `SymbolLibraryCache` - Symbol caching
- `get_symbol_cache()` - Cache access function
- `KiCADConfig` / `config` - Configuration
- Exceptions: `KiCadSchError`, `ValidationError`, `ValidationIssue`, `ElementNotFoundError`, `DuplicateElementError`

**Convenience Functions:**
- `load_schematic(file_path)` → Schematic
- `create_schematic(name)` → Schematic

### Schematic Class - Main Methods

#### Component Operations
- ✅ `components` property → ComponentCollection
- ✅ `get_component_pin_position(ref, pin)` → Point
- ✅ `list_component_pins(ref)` → List[(pin, Point)]

#### Wire Operations
- ✅ `wires` property → WireCollection
- ✅ `add_wire(start, end, type)` → str (uuid)
- ✅ `remove_wire(uuid)` → bool
- ✅ `add_wire_to_pin(ref, pin, end_pos)` → str
- ✅ `add_wire_between_pins(ref1, pin1, ref2, pin2)` → str
- ✅ `connect_pins_with_wire(...)` → str (alias)
- ✅ `auto_route_pins(ref1, pin1, ref2, pin2, **opts)` → List[str]

#### Label Operations
- ✅ `labels` property → LabelCollection
- ✅ `add_label(text, position, **opts)` → str (uuid)
- ✅ `remove_label(uuid)` → bool
- ✅ `add_global_label(text, position, **opts)` → str
- ✅ `add_hierarchical_label(text, position, **opts)` → str
- ✅ `remove_hierarchical_label(uuid)` → bool
- ✅ `hierarchical_labels` property → LabelCollection

#### Text Operations
- ✅ `texts` property → TextCollection
- ✅ `add_text(text, position, **opts)` → str
- ✅ `add_text_box(text, start, end, **opts)` → str

#### Junction Operations
- ✅ `junctions` property → JunctionCollection

#### No-Connect Operations
- ✅ `no_connects` property → NoConnectCollection

#### Net Operations
- ✅ `nets` property → NetCollection

#### Sheet Operations (Hierarchy)
- ✅ `sheets` property → SheetManager
- ✅ `hierarchy` property → HierarchyManager
- ✅ `add_sheet(name, filename, position, size, **opts)` → str
- ✅ `add_sheet_pin(sheet_uuid, name, **opts)` → str
- ✅ `remove_sheet(uuid)` → bool
- ✅ `set_hierarchy_context(parent_uuid, sheet_uuid)` → None

#### Graphics Operations
- ✅ `add_rectangle(start, end, **opts)` → str
- ✅ `remove_rectangle(uuid)` → bool
- ✅ `add_image(...)` → str
- ✅ `draw_bounding_box(bbox, **opts)` → None
- ✅ `draw_component_bounding_boxes(**opts)` → None

#### Connectivity Operations
- ✅ `are_pins_connected(ref1, pin1, ref2, pin2)` → bool
- ✅ `get_net_for_pin(ref, pin)` → Net
- ✅ `get_connected_pins(ref, pin)` → List[(ref, pin)]

#### File Operations
- ✅ `save(filepath, preserve_format)` → None
- ✅ `save_as(filepath, preserve_format)` → None
- ✅ `backup(suffix)` → Path

#### Metadata Operations
- ✅ `set_title_block(**kwargs)` → None
- ✅ `set_paper_size(paper)` → None
- ✅ `title_block` property → Dict
- ✅ `uuid` property → str
- ✅ `version` property → str
- ✅ `generator` property → str

#### Validation & Stats
- ✅ `validate()` → List[ValidationIssue]
- ✅ `get_validation_summary()` → Dict
- ✅ `get_statistics()` → Dict

#### Export Operations (via kicad-cli)
- ✅ `run_erc(**kwargs)` → ERCResult
- ✅ `export_netlist(format, **kwargs)` → str
- ✅ `export_bom(**kwargs)` → str
- ✅ `export_pdf(**kwargs)` → Path
- ✅ `export_svg(**kwargs)` → Path
- ✅ `export_dxf(**kwargs)` → Path

### ComponentCollection Methods

**CRUD Operations:**
- ✅ `add(lib_id, reference, value, position, **kwargs)` → Component
- ✅ `add_ic(lib_id, reference, **kwargs)` → Component (multi-unit)
- ✅ `get(reference)` → Optional[Component]
- ✅ `remove(reference)` → bool
- ✅ `remove_by_uuid(uuid)` → bool
- ✅ `remove_component(component)` → bool

**Query Operations:**
- ✅ `filter(**criteria)` → List[Component]
- ✅ `filter_by_type(type)` → List[Component]
- ✅ `in_area(x1, y1, x2, y2)` → List[Component]
- ✅ `near_point(x, y, radius)` → List[Component]

**Bulk Operations:**
- ✅ `bulk_update(criteria, updates)` → int

**Utility:**
- ✅ `sort_by_reference()` → None
- ✅ `sort_by_position(by_x)` → None
- ✅ `validate_all()` → List[ValidationIssue]
- ✅ `get_statistics()` → Dict

**Collection Protocol:**
- ✅ `__len__()` → int
- ✅ `__iter__()` → Iterator[Component]
- ✅ `__getitem__(key)` → Component (by index or reference)
- ✅ `__contains__(reference)` → bool

### Component Wrapper Methods

**Properties (Read/Write):**
- ✅ `uuid` (read-only)
- ✅ `reference` (with validation)
- ✅ `value`
- ✅ `footprint`
- ✅ `position` (Point or tuple)
- ✅ `rotation`
- ✅ `lib_id` (read-only)
- ✅ `library` (read-only)
- ✅ `symbol_name` (read-only)
- ✅ `properties` (dict)
- ✅ `in_bom`
- ✅ `on_board`

**Property Operations:**
- ✅ `get_property(name, default)` → Optional[str]
- ✅ `set_property(name, value)` → None
- ✅ `remove_property(name)` → bool

**Pin Operations:**
- ✅ `pins` property → List[SchematicPin]
- ✅ `get_pin(pin_number)` → Optional[SchematicPin]
- ✅ `get_pin_position(pin_number)` → Optional[Point]

**Transform Operations:**
- ✅ `move(x, y)` → None
- ✅ `translate(dx, dy)` → None
- ✅ `rotate(angle)` → None

**Utility:**
- ✅ `copy_properties_from(other)` → None
- ✅ `get_symbol_definition()` → Optional[SymbolDefinition]
- ✅ `update_from_library()` → bool
- ✅ `validate()` → List[ValidationIssue]
- ✅ `to_dict()` → Dict

### WireCollection - VERIFIED ✅

**Base:** BaseCollection[Wire]
**File:** `kicad_sch_api/core/wires.py`

**CRUD Operations:**
- ✅ `add(start, end, wire_type, stroke_width, stroke_type, uuid)` → Wire
- ✅ `remove(uuid)` → bool
- ✅ `get(uuid)` → Optional[Wire]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `get_horizontal_wires()` → List[Wire]
- ✅ `get_vertical_wires()` → List[Wire]
- ✅ `get_statistics()` → Dict (wire counts, lengths)

**Wire Properties:**
- `start`, `end` (Point)
- `wire_type` (WireType: WIRE, BUS, BUS_ENTRY)
- `stroke_width`, `stroke_type`
- `is_horizontal()`, `is_vertical()`, `length()`

### LabelCollection - VERIFIED ✅

**Base:** BaseCollection[LabelElement]
**File:** `kicad_sch_api/core/labels.py`

**CRUD Operations:**
- ✅ `add(text, position, label_type, rotation, effects, uuid)` → LabelElement
- ✅ `remove(uuid)` → bool
- ✅ `get(uuid)` → Optional[LabelElement]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `find_by_text(text, exact)` → List[LabelElement]
- ✅ `find_at_position(position, tolerance)` → List[LabelElement]
- ✅ `get_statistics()` → Dict

**LabelElement Properties:**
- `text`, `position`, `label_type`, `rotation`
- `effects` (font, size, color)
- `validate()`, `to_dict()`

### TextCollection - VERIFIED ✅

**Base:** BaseCollection[TextElement]
**File:** `kicad_sch_api/core/texts.py`

**CRUD Operations:**
- ✅ `add(text, position, rotation, size, exclude_from_sim, uuid)` → TextElement
- ✅ `remove(uuid)` → bool
- ✅ `get(uuid)` → Optional[TextElement]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `find_by_content(content, exact)` → List[TextElement]
- ✅ `get_statistics()` → Dict

**TextElement Properties:**
- `text`, `position`, `rotation`, `size`
- `exclude_from_sim` (bool)
- `validate()`, `to_dict()`

### JunctionCollection - VERIFIED ✅

**Base:** BaseCollection[Junction]
**File:** `kicad_sch_api/core/junctions.py`

**CRUD Operations:**
- ✅ `add(position, diameter, uuid)` → Junction
- ✅ `remove(uuid)` → bool
- ✅ `get(uuid)` → Optional[Junction]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `find_at_position(position, tolerance)` → List[Junction]
- ✅ `get_statistics()` → Dict

**Junction Properties:**
- `position` (Point)
- `diameter` (float, default 1.27mm)
- `validate()`, `to_dict()`

### NoConnectCollection - VERIFIED ✅

**Base:** BaseCollection[NoConnectElement]
**File:** `kicad_sch_api/core/no_connects.py`

**CRUD Operations:**
- ✅ `add(position, uuid)` → NoConnectElement
- ✅ `remove(uuid)` → bool
- ✅ `get(uuid)` → Optional[NoConnectElement]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `find_at_position(position, tolerance)` → List[NoConnectElement]
- ✅ `get_statistics()` → Dict

**NoConnectElement Properties:**
- `position` (Point)
- `validate()`, `to_dict()`

### NetCollection - VERIFIED ✅

**Base:** BaseCollection[NetElement]
**File:** `kicad_sch_api/core/nets.py`

**CRUD Operations:**
- ✅ `add(name, components, wires, labels)` → NetElement
- ✅ `remove(name)` → bool (uses name as identifier)
- ✅ `get(name)` → Optional[NetElement]
- ✅ Inherited: `find(predicate)`, `filter(**criteria)`, `__iter__()`, `__len__()`

**Specialized Methods:**
- ✅ `get_by_name(name)` → Optional[NetElement]
- ✅ `find_by_component(reference, pin)` → List[NetElement]
- ✅ `get_statistics()` → Dict

**NetElement Properties:**
- `name` (str)
- `components` (List[Tuple[ref, pin]])
- `wires` (List[uuid])
- `labels` (List[uuid])
- `add_connection()`, `remove_connection()`, `add_wire()`, `remove_wire()`, `add_label()`, `remove_label()`

### Specialized Managers - VERIFIED ✅

#### HierarchyManager
**File:** `kicad_sch_api/core/managers/hierarchy.py`

**Key Methods:**
- ✅ `build_hierarchy_tree(root, path)` → HierarchyNode
- ✅ `find_reused_sheets()` → Dict[filename, List[SheetInstance]]
- ✅ `validate_sheet_pins()` → List[SheetPinConnection]
- ✅ `get_validation_errors()` → List[str]
- ✅ `trace_signal_path(signal, start)` → List[SignalPath]
- ✅ `flatten_hierarchy(prefix_refs)` → Schematic
- ✅ `get_hierarchy_statistics()` → Dict
- ✅ `visualize_hierarchy(stats)` → str

#### SheetManager
**File:** `kicad_sch_api/core/managers/sheet.py`

**Key Methods:**
- ✅ `add_sheet(name, filename, position, size, **opts)` → str (uuid)
- ✅ `add_sheet_pin(sheet_uuid, name, type, edge, pos_along_edge)` → str
- ✅ `remove_sheet(uuid)` → bool
- ✅ `remove_sheet_pin(sheet_uuid, pin_uuid)` → bool
- ✅ `get_sheet_by_name(name)` → Optional[Sheet]
- ✅ `get_sheet_by_filename(filename)` → Optional[Sheet]
- ✅ `list_sheet_pins(sheet_uuid)` → List[SheetPin]
- ✅ `update_sheet_size(uuid, size)` → bool
- ✅ `update_sheet_position(uuid, position)` → bool
- ✅ `get_sheet_hierarchy()` → Dict
- ✅ `validate_sheet_references()` → List[ValidationIssue]

#### WireManager
**File:** `kicad_sch_api/core/managers/wire.py`

**Key Methods:**
- ✅ `add_wire(start, end)` → str
- ✅ `remove_wire(uuid)` → bool
- ✅ `add_wire_to_pin(start, ref, pin)` → str
- ✅ `add_wire_between_pins(ref1, pin1, ref2, pin2)` → str
- ✅ `get_component_pin_position(ref, pin)` → Point
- ✅ `list_component_pins(ref)` → List[Tuple[pin, Point]]
- ✅ `auto_route_pins(ref1, pin1, ref2, pin2, strategy)` → List[str]
- ✅ `are_pins_connected(ref1, pin1, ref2, pin2)` → bool
- ✅ `get_net_for_pin(ref, pin)` → Net
- ✅ `get_connected_pins(ref, pin)` → List[Tuple[ref, pin]]

#### GraphicsManager
**File:** `kicad_sch_api/core/managers/graphics.py`

**Key Methods:**
- ✅ `add_rectangle(start, end, stroke, fill, uuid)` → str
- ✅ `add_circle(center, radius, stroke, fill, uuid)` → str
- ✅ `add_arc(start, mid, end, stroke, uuid)` → str
- ✅ `add_polyline(points, stroke, fill, uuid)` → str
- ✅ `add_image(position, scale, data, uuid)` → str
- ✅ `remove_rectangle/circle/arc/polyline/image(uuid)` → bool
- ✅ `update_stroke/fill(uuid, props)` → bool
- ✅ `get_graphics_in_area(start, end)` → List
- ✅ `list_all_graphics()` → List
- ✅ `validate_graphics()` → List[ValidationIssue]

#### MetadataManager
**File:** `kicad_sch_api/core/managers/metadata.py`

**Key Methods:**
- ✅ `set_paper_size(paper)` → None
- ✅ `set_version_info(version, generator)` → None
- ✅ `set_title_block(title, date, rev, company, comments)` → None
- ✅ `get_version/generator/uuid/paper_size/title_block()` → values
- ✅ `copy_metadata_from(source)` → None
- ✅ `validate_metadata()` → List[ValidationIssue]

#### TextElementManager
**File:** `kicad_sch_api/core/managers/text_elements.py`

**Key Methods:**
- ✅ `add_label(text, position, effects, uuid, rotation, size)` → str
- ✅ `add_hierarchical_label(text, position, shape, effects, uuid)` → str
- ✅ `add_global_label(text, position, shape, effects, uuid)` → str
- ✅ `add_text(text, position, effects, uuid)` → str
- ✅ `add_text_box(text, position, size, rotation, **opts)` → str
- ✅ `remove_label/hierarchical_label/global_label/text/text_box(uuid)` → bool
- ✅ `get_labels_at_position(position, tolerance)` → List
- ✅ `update_text_effects(uuid, effects)` → bool
- ✅ `list_all_text_elements()` → List
- ✅ `validate_text_positions()` → List[ValidationIssue]

#### ValidationManager
**File:** `kicad_sch_api/core/managers/validation.py`

**Key Methods:**
- ✅ `validate_schematic()` → List[ValidationIssue]
- ✅ `validate_component_references()` → List[ValidationIssue]
- ✅ `validate_connectivity()` → List[ValidationIssue]
- ✅ `validate_positioning()` → List[ValidationIssue]
- ✅ `validate_design_rules()` → List[ValidationIssue]
- ✅ `validate_metadata()` → List[ValidationIssue]
- ✅ `get_validation_summary(issues)` → Dict

#### FileIOManager
**File:** `kicad_sch_api/core/managers/file_io.py`

**Key Methods:**
- ✅ `load_schematic(path)` → Dict
- ✅ `save_schematic(data, path, preserve_format)` → None
- ✅ `create_backup(path, suffix)` → Path
- ✅ `validate_file_path(path)` → Path
- ✅ `get_file_info(path)` → Dict
- ✅ `create_empty_schematic_data()` → Dict

#### FormatSyncManager
**File:** `kicad_sch_api/core/managers/format_sync.py`

**Key Methods:**
- ✅ `mark_dirty(section, operation, context)` → None
- ✅ `sync_component_to_data(component)` → None
- ✅ `sync_component_from_data(component, data)` → None
- ✅ `sync_all_to_data(components, wires)` → None
- ✅ `sync_all_from_data(components, wires)` → None
- ✅ `perform_incremental_sync(components, wires)` → None
- ✅ `is_dirty(section)` → bool
- ✅ `validate_data_consistency(components, wires)` → List[str]

---

## 📋 Test Plan (To Be Organized)

### Phase 2: Module-by-Module Testing

#### Module 1: Core Schematic Operations
- [ ] Create blank schematic
- [ ] Load existing schematic
- [ ] Save schematic (format preservation)
- [ ] Save as new file
- [ ] Backup schematic
- [ ] Context manager (`with` statement)

#### Module 2: Component CRUD
- [ ] Add component (basic)
- [ ] Add component (with all options)
- [ ] Add IC (multi-unit component)
- [ ] Get component by reference
- [ ] Update component properties
- [ ] Remove component (by reference)
- [ ] Remove component (by UUID)
- [ ] Remove component (by object)
- [ ] Verify lib_symbol cleanup on last removal

#### Module 3: Component Queries
- [ ] Filter by criteria
- [ ] Filter by type
- [ ] Filter by area
- [ ] Filter near point
- [ ] Bulk update
- [ ] Sort operations
- [ ] Statistics

#### Module 4: Wire Operations
- [ ] Add wire (basic)
- [ ] Add wire (different types: normal, bus, bus_entry)
- [ ] Add wire to pin
- [ ] Add wire between pins (direct)
- [ ] Add wire between pins (Manhattan routing)
- [ ] Auto-route with obstacle avoidance
- [ ] Remove wire
- [ ] Wire collection queries

#### Module 5: Label Operations
- [ ] Add local label
- [ ] Add global label
- [ ] Add hierarchical label (all shapes)
- [ ] Add hierarchical label (rotations)
- [ ] Remove label
- [ ] Remove hierarchical label
- [ ] Label collection queries

#### Module 6: Text Operations
- [ ] Add text
- [ ] Add text box
- [ ] Text with effects (size, color, rotation)
- [ ] Text box with border options
- [ ] Remove text (need to verify)

#### Module 7: Junction Operations
- [ ] Add junction
- [ ] Remove junction
- [ ] Junction at wire intersections

#### Module 8: No-Connect Operations
- [ ] Add no-connect
- [ ] Remove no-connect
- [ ] No-connect on component pins

#### Module 9: Sheet/Hierarchy Operations
- [ ] Create parent schematic
- [ ] Add hierarchical sheet
- [ ] Set hierarchy context on child
- [ ] Add sheet pins (all sides)
- [ ] Add sheet pins (all shapes)
- [ ] Remove sheet
- [ ] Hierarchy tree building
- [ ] Sheet reuse detection
- [ ] Signal path tracing

#### Module 10: Graphics Operations
- [ ] Add rectangle
- [ ] Add rectangle (fill options, colors)
- [ ] Remove rectangle
- [ ] Add image
- [ ] Draw bounding box
- [ ] Draw component bounding boxes

#### Module 11: Connectivity Analysis
- [ ] Pin-to-pin connectivity check
- [ ] Get net for pin
- [ ] Get all connected pins
- [ ] Connectivity through wires
- [ ] Connectivity through junctions
- [ ] Connectivity through local labels
- [ ] Connectivity through global labels
- [ ] Connectivity through hierarchical labels
- [ ] Connectivity through power symbols
- [ ] Connectivity through sheet pins

#### Module 12: Pin Operations
- [ ] Get pin position (rotation 0)
- [ ] Get pin position (rotation 90)
- [ ] Get pin position (rotation 180)
- [ ] Get pin position (rotation 270)
- [ ] List all component pins
- [ ] Pin position with mirroring

#### Module 13: Metadata Operations
- [ ] Set title block fields
- [ ] Set paper size
- [ ] Get schematic UUID
- [ ] Get version/generator

#### Module 14: Validation & Stats
- [ ] Validate schematic
- [ ] Get validation summary
- [ ] Get statistics
- [ ] Component validation

#### Module 15: Export Operations (kicad-cli)
- [ ] Run ERC
- [ ] Export netlist (KiCAD format)
- [ ] Export BOM
- [ ] Export PDF
- [ ] Export SVG
- [ ] Export DXF

#### Module 16: Configuration
- [ ] Property positioning config
- [ ] Tolerance config
- [ ] Grid config
- [ ] Component spacing config

#### Module 17: Edge Cases
- [ ] Empty schematic operations
- [ ] Invalid references
- [ ] Duplicate references
- [ ] Invalid lib_ids
- [ ] Off-grid positions
- [ ] Negative positions
- [ ] Large position values
- [ ] Non-existent UUIDs
- [ ] Null/empty values
- [ ] Special characters in text
- [ ] Unicode in labels/text

#### Module 18: Format Preservation
- [ ] Round-trip test (load → save → compare)
- [ ] All reference schematics preservation
- [ ] Property order preservation
- [ ] Whitespace preservation
- [ ] UUID preservation

---

## 📚 Documentation Review (To Be Done)

### README.md
- [ ] Installation instructions accurate
- [ ] Quick start example works
- [ ] Coordinate system explanation accurate
- [ ] Grid alignment explanation accurate
- [ ] All code examples work
- [ ] Feature list matches implementation
- [ ] Known limitations accurate
- [ ] Links to docs work

### API_REFERENCE.md
- [ ] All documented methods exist
- [ ] All parameters correct
- [ ] Return types accurate
- [ ] Examples work
- [ ] Exceptions documented
- [ ] Edge cases mentioned

### GETTING_STARTED.md
- [ ] Tutorial works end-to-end
- [ ] Code examples work
- [ ] Concepts explained correctly

### HIERARCHY_FEATURES.md
- [ ] Hierarchy examples work
- [ ] set_hierarchy_context usage correct
- [ ] Multi-sheet examples work

### RECIPES.md
- [ ] All recipes work
- [ ] Common patterns accurate
- [ ] Wire routing examples work

### ARCHITECTURE.md
- [ ] Design principles accurate
- [ ] Manager descriptions match code
- [ ] Architecture diagrams accurate

### CLAUDE.md
- [ ] Commands work
- [ ] Architecture matches reality
- [ ] Testing strategy accurate
- [ ] Known issues current

### Example Files
- [ ] `examples/example.py` works
- [ ] `examples/hierarchy_example.py` works
- [ ] `examples/component_rotation.py` works
- [ ] `examples/stm32g431_simple.py` works
- [ ] `examples/kicad_cli_exports.py` works

---

## 🐛 Issues Discovered

### CRITICAL Issues
*None yet*

### HIGH Priority Issues
*None yet*

### MEDIUM Priority Issues
*None yet*

### LOW Priority Issues
*None yet*

### Documentation Inconsistencies
*None yet*

---

## ✅ Completed Tests

*Will be updated as testing progresses*

---

## 📝 Notes

### Testing Strategy
- Create automated unit/functional tests first
- Then create manual verification script for visual inspection
- Run test → generate .kicad_sch → open in KiCAD → user verifies
- Document any issues immediately

### Automation Goals
- All tests should be automated where possible
- Manual verification only for visual/format checks
- Tests should be repeatable and comprehensive
- Add to CI/CD pipeline for future PRs

---

**Last Updated:** 2025-11-05 (Phase 1 - Discovery)
