# PRD: Complete KiCAD Schematic Creation, Reading & Editing

## Executive Summary
Build a professional, production-ready Python library for KiCAD schematic manipulation designed as a foundation for other tools and automation. Focus on clean API design, extensibility, simplicity, and exact format preservation. This library serves as the core schematic manipulation layer that other tools (circuit-synth, AI agents, automation scripts) will build upon.

## Vision & Scope
Create a **professional foundation library** for KiCAD schematic manipulation:
- **Clean API**: Simple, pythonic interface designed for tool integration
- **Complete CRUD**: Create, read, update, delete all schematic elements
- **Format Perfect**: Exact KiCAD 9 format preservation
- **Tool Foundation**: Built to be used by other tools, not end users
- **Zero Magic**: What you specify is what you get, no hidden behavior
- **Extensible**: Easy to add new features without breaking existing code
- **Simple Core**: Complexity belongs in tools using this library, not here

## Current Status ✅ 
- **Components**: Working perfectly (R1, C1 display correctly - NO MORE "R?")
- **UUID consistency**: Component instances properly reference schematic UUID
- **S-expression formatting**: Exact KiCAD format preservation
- **Library integration**: References actual KiCAD symbol libraries
- **Property handling**: Proper case preservation (Datasheet, Description)

## Implementation Priorities

### Priority 0: Schematic Reading & Import (NEW - CRITICAL) 📖
**Status**: Foundation for all editing operations
**Timeline**: 2-3 days

**Core Capabilities**:
- Load any valid KiCAD 9 .kicad_sch file (fail on other versions)
- Import ALL component properties including custom fields
- Extract all UUIDs, positions, orientations, values
- Read all wires, labels, junctions, buses
- Import hierarchical structures if present
- Generate complete Python code that recreates the schematic exactly
- Fail on unknown elements (strict parsing)

**Component Property Structure**:
```python
# Separate standard and custom properties
component.reference = "R1"  # Standard property
component.value = "10k"     # Standard property
component.footprint = "R_0603"  # Standard property
component.custom_properties = {  # All custom fields
    "Tolerance": "1%",
    "MPN": "RC0603FR-0710KL",
    "CustomField1": "AnyValue"
}
```

**API Design**:
```python
# Load existing schematic (strict KiCAD 9 only)
sch = ksa.load_schematic("existing_design.kicad_sch")
# Raises VersionError if not KiCAD 9
# Raises SymbolNotFoundError if libraries missing
# Raises UnknownElementError on unknown elements

# Access components with dictionary syntax
try:
    resistor = sch.components["R1"]  # KeyError if not found
except KeyError:
    print("R1 not found")

# Generate complete runnable Python script
code = sch.to_python_code()  # Complete script with imports
with open("recreate_schematic.py", "w") as f:
    f.write(code)
```

**Python Code Generation Format**:
```python
#!/usr/bin/env python3
"""Generated from: existing_design.kicad_sch"""
import kicad_sch_api as ksa

def recreate_schematic():
    # Create schematic with original UUID
    sch = ksa.create_schematic("MyDesign", uuid="59b50626...")
    
    # Components section
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(91.44, 69.85),
        uuid="c7a8a338..."
    )
    r1.footprint = "Resistor_SMD:R_0603_1608Metric"
    r1.custom_properties = {"Tolerance": "1%"}
    
    # Wires section
    sch.wires.add(start=(100.33, 81.28), end=(91.44, 81.28))
    
    # Junctions section
    sch.junctions.add(position=(91.44, 81.28))
    
    # Labels section
    sch.labels.add(text="VOUT", position=(100.33, 81.28))
    
    return sch

if __name__ == "__main__":
    sch = recreate_schematic()
    sch.save("output.kicad_sch")
    print("Schematic recreated successfully")
```

### Priority 1: Component Deletion & Editing 🗑️
**Status**: Simple, unrestricted editing
**Timeline**: 1-2 days after reading

**Philosophy**: Allow ANY edit, even if it breaks the schematic

**Capabilities**:
- Delete components by reference (basic cleanup only)
- Edit ANY property to ANY value
- Move components to any position
- No validation - user is responsible for correctness

**API Design**:
```python
# Simple deletion (basic cleanup only)
sch.components.delete("R5")  # Removes component, that's it

# Unrestricted editing - ANY property, ANY value
resistor = sch.components["R1"]
resistor.value = "100k"  # Standard edit
resistor.set_property("CustomField", "MyValue")  # Custom field
resistor.lib_id = "Device:R_Small"  # Change symbol (even if invalid)
resistor.position = (999999, -50000)  # Any position, even off-page

# Edit multiple properties at once
resistor.update({
    "value": "1M",
    "tolerance": "5%",
    "manufacturer": "Yageo",
    "anything": "any value"  # Creates new field if doesn't exist
})
```

### Priority 2: Backup System 💾
**Status**: Safety for all operations
**Timeline**: 1 day

**Capabilities**:
- Automatic backup before modifications
- Timestamped .bak files
- Configurable backup directory
- Rollback on errors

**API Design**:
```python
# Automatic backup on load
sch = ksa.load_schematic("design.kicad_sch", auto_backup=True)
# Creates: design.kicad_sch.20240115_143022.bak

# Manual backup
sch.create_backup(suffix="before_major_change")
# Creates: design.kicad_sch.before_major_change.bak

# Rollback on error
try:
    sch.components.bulk_delete(criteria={'footprint': 'obsolete'})
    sch.save()
except Exception as e:
    sch.rollback()  # Restore from backup
    raise
```

### Priority 3: Robust Unit Testing Framework 🧪
**Status**: CRITICAL - Current tests failed to detect "R?" issue  
**Timeline**: 1-2 days

**Problem Analysis**:
The existing test suite in `/python/tests/` completely failed to detect that components showed "R?" instead of "R1" in KiCAD. This is unacceptable for a professional library.

**KEY BREAKTHROUGH: Deterministic UUID Support**
Enable **exact file diffing** by allowing manual UUID specification for perfect reference recreation.

**Required Test Categories**:

#### 1. KiCAD Integration Tests (NEW)
```python
class TestKiCADCompatibility:
    def test_component_display_validation(self):
        """Verify components display correct reference designators in KiCAD."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", reference="R1", value="10k", 
                          position=(100, 100), footprint="Resistor_SMD:R_0603_1608Metric")
        
        sch.save("test_output.kicad_sch")
        
        # This test would have caught the "R?" issue
        assert_kicad_opens_without_errors("test_output.kicad_sch")
        assert_component_shows_reference("test_output.kicad_sch", "R1")
```

#### 2. UUID Relationship Tests (NEW)
```python
class TestUUIDConsistency:
    def test_component_instances_match_schematic_uuid(self):
        """Critical: Component instances must use schematic UUID."""
        sch = ksa.create_schematic("Test")
        resistor = sch.components.add("Device:R", reference="R1", ...)
        
        schematic_uuid = sch._data["uuid"]
        component_path = resistor._data["instances"][0]["path"]
        
        # This would have caught the UUID mismatch that caused "R?"
        assert component_path == f"/{schematic_uuid}"
```

#### 3. Property Completeness Tests (NEW)
```python
class TestRequiredProperties:
    def test_all_components_have_essential_properties(self):
        """Verify Footprint, Datasheet, Description always present."""
        sch = ksa.create_schematic("Test")
        resistor = sch.components.add("Device:R", reference="R1", ...)
        
        # These properties are required for KiCAD functionality
        assert "Footprint" in resistor.properties
        assert "Datasheet" in resistor.properties
        assert "Description" in resistor.properties
        assert resistor.properties["Footprint"] != ""
```

#### 4. Deterministic UUID API (NEW)
```python
# Enable exact reproduction of reference files
sch = ksa.create_schematic("Single Resistor", 
                          uuid="d80ef055-e33f-44b7-9702-8ce9cf922ab9")

resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1", 
    value="10k",
    position=(93.98, 81.28),
    footprint="Resistor_SMD:R_0603_1608Metric",
    uuid="a9fd95f7-6e8c-4e46-ba2c-21946a035fdb",  # Match reference exactly
    pin_uuids={
        "1": "0d245fe6-f620-479d-85be-7a0d7f5e7bb8",
        "2": "bebad4a9-c297-4274-b750-0bd65ebe7eff"
    }
)

# Result: Generated file is BYTE-FOR-BYTE identical to reference
# Enables perfect diff testing
```

#### 5. Exact File Diff Tests (NEW)
```python
class TestExactRecreation:
    def test_single_resistor_exact_diff(self):
        """GOLD STANDARD: Generate file identical to reference."""
        # Create with exact UUIDs from reference
        sch = create_single_resistor_with_reference_uuids()
        sch.save("generated_single_resistor.kicad_sch")
        
        reference_file = "python/tests/reference_tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch"
        
        # EXACT file comparison (excluding timestamps)
        assert_files_identical_except_timestamps("generated_single_resistor.kicad_sch", reference_file)
        
    @pytest.mark.parametrize("reference_project", ALL_REFERENCE_PROJECTS)
    def test_exact_recreation_all_references(self, reference_project):
        """Ultimate validation: Recreate ALL references with exact diff."""
        generated = create_reference_with_exact_uuids(reference_project)
        reference = load_reference_file(reference_project)
        
        assert_exact_file_match(generated, reference)
```

#### 6. Reference Project Recreation Tests (ENHANCED)
```python
class TestReferenceProjectRecreation:
    @pytest.mark.parametrize("reference_name", [
        "single_resistor", "two_resistors", "single_hierarchical_sheet"
    ])
    def test_recreate_reference_exactly(self, reference_name):
        """Verify we can recreate reference projects with identical functionality."""
        generated_sch = generate_reference_project(reference_name)
        reference_sch = f"python/tests/reference_tests/reference_kicad_projects/{reference_name}/"
        
        assert_structural_equivalence(generated_sch, reference_sch)
        assert_kicad_functionality_identical(generated_sch, reference_sch)
```

### Priority 4: Wire & Connection APIs (No Routing) 🔌
**Status**: Clean coordinate-based API
**Timeline**: 2 days

**Design Philosophy**:
- Professional API for exact element placement
- No validation, no routing, no intelligence
- Tools using this library handle routing logic
- Simple, extensible, predictable

**Wire & Junction Data Structure** (KiCAD native):
```python
# Wire: point list with stroke properties
wire = {
    "pts": [(100.33, 81.28), (91.44, 81.28)],  # Points
    "stroke": {"width": 0, "type": "default"},
    "uuid": "145c312d-dece-4422-8ba7-b6d439803389"
}

# Junction: position with visual properties
junction = {
    "position": (91.44, 81.28),
    "diameter": 0,
    "color": (0, 0, 0, 0),
    "uuid": "bb8d83da-2bb9-49a5-854d-3fe11ee1db05"
}
```

**Professional API Design**:
```python
# Single segment wire
wire = sch.wires.add(
    start=(100, 100),
    end=(200, 100),
    uuid=None  # Auto-generated by default
)

# Multi-segment wire (if KiCAD supports)
wire = sch.wires.add(
    points=[(100, 100), (150, 100), (150, 150)],
    uuid=None  # Auto-generated by default
)

# Junction placement
junction = sch.junctions.add(position=(150, 100))

# Label types - separate APIs for clarity
label = sch.labels.add(text="VOUT", position=(150, 95))
global_label = sch.global_labels.add(text="VCC", position=(100, 100))
hierarchical_label = sch.hierarchical_labels.add(
    text="DATA_IN", 
    position=(50, 50),
    direction="input"
)

# Bus creation
bus = sch.buses.add(start=(100, 200), end=(300, 200))

# No-connect flag
sch.no_connects.add(position=(100, 150))
```

**Note**: Routing intelligence belongs in tools using this library, not here.

### Priority 5: Hierarchical Labels 🔗
**Status**: Foundation for hierarchical designs
**Timeline**: 1 day after testing framework

**Generic Design Principles**:
- No hardcoded directions - reference KiCAD's label direction system
- Extensible shape system - support all KiCAD shape types
- Generic positioning system - reuse existing Point infrastructure

**API Design**:
```python
# Generic, extensible hierarchical label creation
sch.hierarchical_labels.add(
    text="VCC",
    position=(100, 100),
    direction="input",  # From KiCAD direction enum
    shape="passive"     # From KiCAD shape enum
)

# Agent-friendly bulk creation
labels = [
    {"text": "VCC", "position": (100, 100), "direction": "output"},
    {"text": "GND", "position": (100, 120), "direction": "output"},
    {"text": "DATA[7..0]", "position": (200, 100), "direction": "bidirectional"}
]
sch.hierarchical_labels.add_bulk(labels)
```

**Reference Projects**: `single_label_hierarchical/`
**Test Coverage**: Direction validation, text display, cross-sheet connectivity

### Priority 6: Hierarchical Sheets 📋
**Status**: Multi-sheet capability
**Timeline**: 2 days after hierarchical labels

**Generic Design Principles**:
- File path management - support relative/absolute paths
- Dynamic sheet sizing - calculate based on content or manual override
- Generic pin system - extensible for any pin type/direction

**API Design**:
```python
# Generic hierarchical sheet with dynamic properties
sheet = sch.sheets.add(
    name="Power Supply",
    file="power_supply.kicad_sch",
    position=(100, 100),
    size=(50, 30)  # Or auto-calculate based on pins
)

# Generic sheet pin system
sheet.pins.add(
    name="VCC",
    direction="output",     # From KiCAD direction system
    position=(50, 10),      # Relative to sheet
    shape="line"            # From KiCAD shape system
)

# Agent-friendly batch operations
sheet_pins = [
    {"name": "VCC", "direction": "output", "position": (50, 10)},
    {"name": "GND", "direction": "output", "position": (50, 20)},
    {"name": "ENABLE", "direction": "input", "position": (0, 15)}
]
sheet.pins.add_bulk(sheet_pins)
```

**Reference Projects**: `single_hierarchical_sheet/` (main + subcircuit)
**Test Coverage**: Multi-file coordination, cross-sheet navigation, pin connectivity

### Priority 7: KiCAD Project Generation & kicad-cli Integration 📁
**Status**: Complete project coordination with kicad-cli BOM export
**Timeline**: 2 days after hierarchical sheets

**kicad-cli Integration**:
```python
# Use kicad-cli for BOM export instead of custom implementation
sch.export_bom_via_cli(
    output="bom.csv",
    preset="grouped_by_value",
    fields=["Reference", "Value", "Footprint", "Datasheet", "MPN"],
    group_by="value,footprint",
    exclude_dnp=True
)

# Direct kicad-cli command execution
import subprocess
result = subprocess.run([
    "kicad-cli", "sch", "export", "bom",
    "--output", "bom.csv",
    "--fields", "Reference,Value,Footprint,MPN",
    "--group-by", "Value,Footprint",
    "--exclude-dnp",
    "design.kicad_sch"
], capture_output=True)
```

**Original Project Generation continues below:**
**Status**: Complete project coordination
**Timeline**: 2 days after hierarchical sheets

**Generic Design Principles**:
- Template-based project generation - support different project types
- Extensible settings system - ERC rules, net classes, design settings
- Multi-schematic coordination - automatic UUID management

**API Design**:
```python
# Generic project creation with template support
project = ksa.create_project("MyDesign", template="default")
# Future: template="power_supply", template="microcontroller", etc.

# Generic settings management
project.settings.erc.set_rule("pin_not_connected", "error")
project.settings.net_classes.add(
    name="Power",
    track_width=0.5,
    clearance=0.2,
    via_diameter=0.6
)

# Agent-friendly multi-schematic creation
schematics = [
    {"name": "main", "title": "Main Circuit"},
    {"name": "power", "title": "Power Supply"},
    {"name": "io", "title": "IO Interface"}
]
for sch_def in schematics:
    sch = project.add_schematic(sch_def["name"])
    sch.title_block["title"] = sch_def["title"]

project.save()  # Auto-generates all .kicad_sch + .kicad_pro
```

**Reference Projects**: All `.kicad_pro` files
**Test Coverage**: Multi-file coordination, project settings, ERC validation

## Core Use Cases

### 1. Reading Existing Schematics
```python
# Load any KiCAD schematic
sch = ksa.load_schematic("complex_design.kicad_sch")

# Extract information for analysis
components = sch.components.list()
wires = sch.wires.list()
nets = sch.extract_nets()

# Generate Python code to recreate
code = sch.to_python_code()
```

### 2. Safe Editing with Backups
```python
# Always create backup before editing
sch = ksa.load_schematic("production_design.kicad_sch")
sch.create_backup()

# Delete obsolete components
sch.components.bulk_delete(criteria={'value': 'DNP'})

# Update all resistor tolerances
for component in sch.components.filter(lib_id="Device:R"):
    component.set_property("Tolerance", "1%")

sch.save()
```

### 3. Creating from Scratch
```python
# Create new schematic
sch = ksa.create_schematic("New Design")

# Add components
sch.components.add("Device:R", reference="R1", value="10k")
sch.components.add("Device:C", reference="C1", value="100nF")

# Add connections (API only, no routing)
sch.wires.add(start=(100, 100), end=(200, 100))
sch.junctions.add(position=(150, 100))

sch.save("new_design.kicad_sch")
```

## kicad-skip Comparison & Differentiation

### What kicad-skip Does Well
- **Exploration**: Excellent REPL experience with tab completion
- **Traversal**: Great at finding connected elements via wire crawling
- **Modification**: Good at modifying existing schematics
- **Flexibility**: Direct access to S-expression structure

### Our Advantages
- **Bidirectional**: Read, create, AND edit schematics (kicad-skip is read-focused)
- **Component deletion**: Full CRUD operations on components
- **Backup system**: Automatic safety for all edits
- **Python code generation**: Convert schematics to Python code
- **Format preservation**: Exact KiCAD output matching
- **Agent integration**: Clean API designed for AI/automation
- **Testing**: Comprehensive validation including actual KiCAD functionality
- **Library integration**: Direct reference to KiCAD symbol/footprint libraries
- **UUID management**: Deterministic UUIDs for exact testing (kicad-skip lacks this)
- **kicad-cli integration**: Leverage official KiCAD tools for BOM export
- **Project coordination**: Multi-file .kicad_pro generation (kicad-skip is single-file focused)

### Key Differentiators

#### 1. Professional Generation vs. Exploration
```python
# kicad-skip: Exploration focused
sch = skip.Schematic('existing.kicad_sch')
sch.symbol.R1.property.Value.value = '1k'

# kicad-sch-api: Generation focused  
sch = ksa.create_schematic("New Design")
sch.components.add("Device:R", reference="R1", value="1k", ...)
```

#### 2. Simple, Direct API
```python
# Simple API for direct manipulation
project = ksa.create_project("LED_Driver")
main_sch = project.main_schematic

# Simple bulk operations
components = [
    {"lib_id": "Device:R", "reference": "R1", "value": "10k"},
    {"lib_id": "Device:LED", "reference": "D1", "value": "RED"},
    {"lib_id": "Device:C", "reference": "C1", "value": "100nF"}
]
main_sch.components.add_bulk(components)
```

#### 3. No Validation Philosophy
```python
# kicad-skip: Complex exploration and validation
# kicad-sch-api: Simple, direct, no validation

# We allow ANY edit, even if it breaks the schematic
sch = ksa.load_schematic("design.kicad_sch")
resistor = sch.components.get("R1")

# These all work, even if they create invalid schematics:
resistor.lib_id = "Device:C"  # Change resistor to capacitor
resistor.value = "not_a_valid_value"  # Invalid value
resistor.position = (-99999, 99999)  # Off the page
resistor.set_property("Footprint", "DoesNotExist")  # Invalid footprint

# User is responsible for correctness
# Use kicad-cli or KiCAD itself for validation
```

#### 4. Library Integration
```python
# Direct reference to actual KiCAD libraries
available_resistors = ksa.library.search("Device", component_type="resistor")
footprint_options = ksa.footprints.search("Resistor_SMD", size="0603")
```

## Generic & Extensible Design Requirements

### 1. No Hardcoding Policy
- **Component types**: Reference actual KiCAD symbol libraries
- **Footprints**: Query KiCAD footprint libraries  
- **Directions/Shapes**: Use KiCAD enums, not hardcoded strings
- **Templates**: JSON-based project templates
- **Positioning**: Generic Point/coordinate system

### 2. Library Integration Architecture
```python
class LibraryManager:
    def search_symbols(self, library: str, pattern: str) -> List[Symbol]
    def get_symbol_info(self, lib_id: str) -> SymbolInfo
    def search_footprints(self, library: str, criteria: dict) -> List[Footprint]
    def validate_lib_id(self, lib_id: str) -> bool

class SymbolInfo:
    lib_id: str
    pins: List[PinInfo]
    default_properties: Dict[str, str]
    description: str
    keywords: List[str]
    footprint_filters: List[str]
```

### 3. Centralized UUID Management System (GAME CHANGER)
```python
# Centralized UUID generation with deterministic support
class UUIDManager:
    def __init__(self, deterministic: bool = False):
        self.deterministic = deterministic
        self.uuid_map = {}
        self.counter = 0
    
    def generate_uuid(self, element_type: str = None, identifier: str = None) -> str:
        """Generate UUID for any schematic element."""
        if self.deterministic:
            if identifier and element_type:
                key = f"{element_type}:{identifier}"
                if key in self.uuid_map:
                    return self.uuid_map[key]
            # Fallback to deterministic sequence
            self.counter += 1
            return f"00000000-0000-0000-0000-{self.counter:012d}"
        return str(uuid.uuid4())
    
    def load_reference_uuids(self, reference_project: str):
        """Load UUIDs from reference project for exact recreation."""
        self.uuid_map = parse_uuids_from_reference(reference_project)

# Global UUID functions
def generate_uuid() -> str:
    """Generate standard UUID for schematic elements."""
    return str(uuid.uuid4())

def generate_deterministic_uuid(seed: str) -> str:
    """Generate deterministic UUID from seed for testing."""
    # Use seed to create consistent UUID
    import hashlib
    hash_obj = hashlib.md5(seed.encode())
    hex_dig = hash_obj.hexdigest()
    return f"{hex_dig[:8]}-{hex_dig[8:12]}-{hex_dig[12:16]}-{hex_dig[16:20]}-{hex_dig[20:32]}"

# DEFAULT: Auto-assignment (normal usage)
sch = ksa.create_schematic("Test")  # UUID auto-generated
resistor = sch.components.add(
    "Device:R", 
    reference="R1",
    value="10k",
    position=(100, 100),
    footprint="Resistor_SMD:R_0603_1608Metric"
    # UUID and pin_uuids auto-generated
)

# OPTIONAL: Manual UUID specification (for testing)
sch = ksa.create_schematic("Single Resistor", 
                          uuid="d80ef055-e33f-44b7-9702-8ce9cf922ab9")
resistor = sch.components.add(
    "Device:R",
    reference="R1", 
    value="10k",
    position=(93.98, 81.28),
    footprint="Resistor_SMD:R_0603_1608Metric",
    uuid="a9fd95f7-6e8c-4e46-ba2c-21946a035fdb",  # Optional override
    pin_uuids={  # Optional override
        "1": "0d245fe6-f620-479d-85be-7a0d7f5e7bb8",
        "2": "bebad4a9-c297-4274-b750-0bd65ebe7eff"
    }
)

# UTILITY: Helper for extracting reference UUIDs
reference_uuids = ksa.extract_uuids_from_reference("single_resistor")
# Returns: {"schematic": "d80ef055...", "components": {"R1": "a9fd95f7..."}, "pins": {...}}
```

### 4. Agent Integration Features
```python
# Bulk operations for agent efficiency
sch.components.add_bulk(component_list)
sch.wires.add_bulk(wire_list)
sch.labels.add_bulk(label_list)

# Validation before generation
errors = sch.validate()
if errors:
    sch.fix_validation_errors(auto=True)

# Template-based generation
sch = ksa.from_template("microcontroller_basic", mcu="STM32F103")

# Exact recreation for testing
sch = ksa.recreate_reference("single_resistor")  # Byte-perfect match
```

## MCP Server Integration Planning

### Agent-Friendly API Requirements
- **Bulk operations**: Efficient multi-element creation
- **Validation**: Pre-generation error checking
- **Templates**: Common circuit patterns
- **Library queries**: Dynamic component/footprint discovery
- **Error recovery**: Graceful handling of invalid inputs

### MCP Server Capabilities
```python
# Future MCP server methods
@mcp_method("create_schematic")
def create_schematic(name: str, components: List[dict]) -> dict

@mcp_method("add_hierarchical_design") 
def add_hierarchical_design(project: str, sheets: List[dict]) -> dict

@mcp_method("validate_design")
def validate_design(schematic_data: dict) -> List[str]
```

## Success Metrics

### Quality Gates
- **Exact file recreation**: Byte-for-byte matching of reference projects using deterministic UUIDs
- **All reference projects recreatable**: 100% compatibility with perfect diff testing
- **Zero hardcoding**: All components/footprints from KiCAD libraries
- **Comprehensive testing**: Tests catch issues before manual validation (never again "R?" surprises)
- **Agent readiness**: Clean bulk operations, error handling, template system
- **Format preservation**: Generated files indistinguishable from manual KiCAD

### Ultimate Validation: The Diff Test
```bash
# Generate with exact UUIDs
python test_single_resistor_exact.py

# Perfect diff (only timestamps differ)
diff reference_kicad_projects/single_resistor/single_resistor.kicad_sch generated_single_resistor.kicad_sch
# Output: Only timestamp differences, everything else identical
```

### Performance Requirements
- **Library loading**: Symbol cache under 1 second
- **Generation speed**: 1000+ components per second
- **Memory efficiency**: Handle large schematics (10k+ components)
- **File size**: Optimal S-expression formatting

This PRD positions kicad-sch-api as the professional generation-focused complement to kicad-skip's exploration-focused approach, with clear differentiation and superior agent integration capabilities.

## UUID Management Implementation Details

### Core UUID Functions (Required)
```python
# In kicad_sch_api/utils/uuid_manager.py
import uuid
import hashlib
from typing import Optional, Dict, Any

def generate_uuid() -> str:
    """Generate standard UUID - DEFAULT for all normal usage."""
    return str(uuid.uuid4())

def generate_deterministic_uuid(seed: str) -> str:
    """Generate deterministic UUID from seed - for testing."""
    hash_obj = hashlib.md5(seed.encode())
    hex_dig = hash_obj.hexdigest()
    return f"{hex_dig[:8]}-{hex_dig[8:12]}-{hex_dig[12:16]}-{hex_dig[16:20]}-{hex_dig[20:32]}"

def extract_uuids_from_reference(reference_project: str) -> Dict[str, Any]:
    """Extract all UUIDs from reference project for exact recreation."""
    reference_file = f"python/tests/reference_tests/reference_kicad_projects/{reference_project}/{reference_project}.kicad_sch"
    
    # Parse and extract all UUIDs
    uuids = {
        "schematic": None,
        "components": {},
        "pins": {},
        "sheets": {},
        "labels": {}
    }
    
    # Implementation: Parse S-expressions and extract UUIDs by element type
    return uuids
```

### API Integration Requirements
```python
# Modify all creation methods to support optional UUID
class Schematic:
    def __init__(self, title: str = "Untitled", uuid: Optional[str] = None):
        self.uuid = uuid or generate_uuid()  # Auto-assign by default

class ComponentCollection:
    def add(self, lib_id: str, reference: str, uuid: Optional[str] = None, 
            pin_uuids: Optional[Dict[str, str]] = None, **kwargs):
        component_uuid = uuid or generate_uuid()  # Auto-assign by default
        
        # Auto-generate pin UUIDs if not provided
        if pin_uuids is None:
            symbol_info = self._get_symbol_info(lib_id)
            pin_uuids = {pin.number: generate_uuid() for pin in symbol_info.pins}
```

### Usage Patterns
```python
# DEFAULT: Auto-assignment (99% of usage)
sch = ksa.create_schematic("My Design")  # UUID auto-generated
sch.components.add("Device:R", reference="R1", value="10k", ...)  # All UUIDs auto-generated

# TESTING: Exact UUID control for diff validation
def create_exact_single_resistor():
    """Create single resistor matching reference exactly."""
    uuids = ksa.extract_uuids_from_reference("single_resistor")
    
    sch = ksa.create_schematic("Single Resistor", uuid=uuids["schematic"])
    sch.components.add(
        "Device:R",
        reference="R1",
        value="10k", 
        position=(93.98, 81.28),
        footprint="Resistor_SMD:R_0603_1608Metric",
        uuid=uuids["components"]["R1"],
        pin_uuids=uuids["pins"]["R1"]
    )
    return sch

# Result: Byte-perfect match to reference file for diff testing
```

## Implementation Decisions Summary

### Core Design Choices
1. **Component Properties**: Separate standard and custom properties
   - Standard properties as attributes (reference, value, footprint)
   - Custom properties in dictionary (custom_properties)

2. **Python Code Generation**: Complete runnable scripts
   - Full imports and main block
   - Exact coordinate preservation
   - Complete recreation capability

3. **Error Handling**: Fail fast and clear
   - VersionError for non-KiCAD 9 files
   - SymbolNotFoundError for missing libraries
   - UnknownElementError for unrecognized elements
   - KeyError for missing components

4. **Backup System**: Simple timestamped files
   - Format: design.kicad_sch.YYYYMMDD_HHMMSS.bak
   - Same directory as original
   - Configurable on/off flag

5. **Component Access**: Dictionary-style API
   - `sch.components["R1"]` raises KeyError if not found
   - No None returns, explicit errors

6. **Wire/Junction Structure**: KiCAD-native format
   - Wires support multi-point paths
   - Junctions as positions with visual properties
   - Optional UUID support for all elements (auto-generated by default)

7. **File Version**: Strict KiCAD 9 only
   - No legacy support
   - Explicit version checking

8. **Test Structure**: One file per feature
   - Individual test files for clarity
   - Manual reference test creation
   - Exact diff validation

9. **Unknown Elements**: Fail on unknown
   - No silent skipping
   - No raw preservation
   - Explicit errors for safety

10. **API Style**: Simple and Pythonic
    - `save()` overwrites original by default
    - Direct attribute access
    - Dictionary patterns where appropriate

### Additional Implementation Details

11. **Schematic Metadata**: Clean object attributes
    - Title, date, revision as schematic properties
    - `sch.title`, `sch.date`, `sch.revision`
    - Direct assignment for updates

12. **Instance Paths**: Automatic with override option
    - Auto-adds schematic UUID to path
    - Manual override for testing only
    - Professional handling of hierarchical paths

13. **Component Deletion**: Complete cleanup
    - `sch.components.delete("R1")` removes all traces
    - No orphaned data in schematic
    - Clean, predictable behavior

14. **Property Updates**: Consistent method pattern
    - `component.set_property("MPN", "XYZ123")`
    - Auto-creates if missing
    - Uniform API across all properties

15. **Save Behavior**: Intuitive defaults
    - `sch.save()` overwrites original
    - `sch.save("new.kicad_sch")` saves to new file
    - Clear, expected behavior

16. **Wire Support**: Flexible point handling
    ```python
    # Two-point wire
    sch.wires.add(start=(100, 100), end=(200, 100))
    
    # Multi-point wire (pending KiCAD format verification)
    sch.wires.add(points=[(100, 100), (150, 100), (150, 150)])
    ```

17. **Implementation Priority**: Foundation first
    - Phase 1: Component CRUD operations
    - Phase 2: Wire/junction/label APIs
    - Phase 3: Hierarchical features
    - Phase 4: Advanced features

18. **UUID Strategy**: Professional defaults
    ```python
    # Production use - auto-generated
    component = sch.components.add("Device:R", reference="R1")
    
    # Testing - manual override
    component = sch.components.add("Device:R", reference="R1", 
                                  uuid="test-uuid")
    ```

19. **Component Transformation**: Properties not methods
    ```python
    component.rotation = 90  # 0, 90, 180, 270
    component.mirror_x = True
    component.mirror_y = False
    ```

20. **Power Symbols**: Regular components
    ```python
    # Power symbols treated as components
    gnd = sch.components.add("power:GND", reference="#PWR01", 
                            position=(100, 100))
    vcc = sch.components.add("power:+3.3V", reference="#PWR02",
                            position=(100, 50))
    ```

21. **Label APIs**: Separate for clarity
    ```python
    # Different label types have different APIs
    sch.labels.add(text="VOUT", position=(100, 100))
    sch.global_labels.add(text="VCC", position=(100, 100))
    sch.hierarchical_labels.add(text="DATA", position=(100, 100),
                                direction="input", shape="passive")
    ```

22. **Library Management**: Automatic discovery
    - Auto-discover KiCAD libraries on first use
    - Cache at `~/.cache/kicad-sch-api/`
    - Professional caching with performance metrics
    - No manual registration required

23. **Wire Format**: To be determined
    - Need to verify if KiCAD supports multi-point wires
    - May need multiple wire entries for complex paths
    - Implementation will match KiCAD's exact format

## Design Principles for Professional Tool Foundation

### API Design Philosophy
- **Clean Interfaces**: Every API follows Python best practices
- **Predictable Behavior**: No surprises, no magic, no hidden state
- **Extensible Architecture**: New features don't break existing code
- **Tool Agnostic**: Works with any tool, not tied to specific use cases
- **Performance Conscious**: Fast operations, efficient memory usage
- **Error Transparency**: Clear, actionable error messages

### Testing Philosophy
- **Reference-Based**: Manual KiCAD reference files for validation
- **Exact Matching**: Byte-for-byte output verification
- **Simple Structure**: One test file per feature
- **Professional Coverage**: Every API path tested

### Library Philosophy
- **Foundation Layer**: This is infrastructure, not an application
- **No Intelligence**: Smart behavior belongs in consuming tools
- **User Control**: Tools using this library control all behavior
- **Format Fidelity**: Exact KiCAD format preservation
- **Simple Core**: Complexity lives in tools, not the library

### Professional Standards
- **Type Hints**: Full typing for IDE support and clarity
- **Documentation**: Every public API fully documented
- **Logging**: Structured logging for debugging
- **Versioning**: Semantic versioning for stability
- **Performance**: Profiled and optimized operations

## Success Criteria

### Technical Excellence
- ✅ Exact KiCAD 9 format match
- ✅ Complete CRUD operations for all elements
- ✅ Professional API that other tools can rely on
- ✅ Zero dependencies on specific use cases
- ✅ Extensible without breaking changes

### Tool Integration
- ✅ Clean import: `import kicad_sch_api as ksa`
- ✅ Predictable API: No surprises for tool developers
- ✅ Error handling: Tools can catch and handle all errors
- ✅ Performance: Fast enough for real-time tools
- ✅ Memory efficient: Handles large schematics

### Quality Metrics
- ✅ 100% API documentation coverage
- ✅ All reference projects recreatable
- ✅ Type hints on all public APIs
- ✅ Clean mypy/flake8/black compliance
- ✅ Professional logging throughout