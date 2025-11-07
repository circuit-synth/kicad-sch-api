# Product Requirements Document: KiCad-to-Python Export

**Feature**: KiCad Schematic to Python Code Converter
**Issue**: #129
**Version**: 1.0
**Date**: 2025-11-07
**Author**: Claude Code (AI Assistant)
**Status**: Draft

---

## Executive Summary

Add the ability to convert existing KiCad schematic files (`.kicad_sch`) into executable Python code that uses the kicad-sch-api library. This feature enables users to learn the API, migrate existing designs to programmatic workflows, and create reusable templates from successful circuit designs.

### Quick Links
- **GitHub Issue**: [#129](https://github.com/circuit-synth/kicad-sch-api/issues/129)
- **Git Worktree**: `../kicad-sch-api-issue-129`
- **Branch**: `feature/issue-129-kicad-to-python`
- **Reference Implementation**: circuit-synth (`/Users/shanemattner/Desktop/circuit_synth_repos/circuit-synth/src/circuit_synth/tools/kicad_integration/`)

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Goals and Non-Goals](#goals-and-non-goals)
3. [User Stories](#user-stories)
4. [Requirements](#requirements)
5. [Proposed Solution](#proposed-solution)
6. [Technical Design](#technical-design)
7. [Implementation Plan](#implementation-plan)
8. [Success Metrics](#success-metrics)
9. [Open Questions](#open-questions)

---

## Problem Statement

### Current State
kicad-sch-api currently supports:
- ✅ Loading existing KiCad schematics: `sch = ksa.Schematic.load('file.kicad_sch')`
- ✅ Modifying schematics programmatically
- ✅ Saving with exact format preservation
- ✅ Creating new schematics from scratch using Python API

### The Gap
There is **no way to export** an existing schematic to Python code. Users cannot:
- See example code for how a schematic was created
- Convert existing KiCad designs to programmatic form
- Generate templates from successful designs
- Version control circuit definitions as readable Python code

### Why This Matters
1. **Learning Barrier**: New users can't see "how would I create this schematic in Python?"
2. **Migration Friction**: Users with existing KiCad projects can't easily transition to programmatic workflows
3. **Reusability Gap**: No way to extract reusable patterns from successful designs
4. **Documentation Challenge**: Can't generate example code for documentation

---

## Goals and Non-Goals

### Goals ✅
1. **Enable Learning**: Generate readable Python code that teaches users the API
2. **Support Migration**: Convert existing KiCad designs to Python workflows
3. **Create Templates**: Extract reusable patterns from successful designs
4. **Round-Trip Capability**: schematic → python → execute → schematic produces identical result
5. **Multiple Access Methods**: CLI, Python API, and utility function interfaces
6. **Comprehensive Coverage**: Support components, wires, labels, and hierarchical sheets

### Non-Goals ❌
1. **Not a Bidirectional Sync Tool**: This is one-way export only (KiCad → Python), not continuous synchronization
2. **Not a Python-to-KiCad Converter**: The inverse direction already exists (API → .kicad_sch)
3. **Not a Format Translator**: Not converting between different circuit description formats
4. **Not an Optimization Tool**: Not analyzing or improving circuit design
5. **Not Real-Time**: No live synchronization or file watching

---

## User Stories

### Story 1: Learning the API (New User)
**As a** new kicad-sch-api user
**I want to** see Python code for an existing schematic
**So that** I can learn how to use the API by example

**Acceptance Criteria**:
- Load any `.kicad_sch` file
- Generate readable, well-commented Python code
- Code runs without errors and produces identical schematic
- Code demonstrates best practices for the API

**Example**:
```bash
$ kicad-to-python examples/resistor_divider.kicad_sch tutorial.py
✅ Generated tutorial.py (45 lines)
   - 3 components
   - 2 wires
   - 2 labels
```

---

### Story 2: Migrating Existing Project (Professional User)
**As a** hardware engineer with existing KiCad projects
**I want to** convert my schematics to Python
**So that** I can integrate them into automated design workflows

**Acceptance Criteria**:
- Convert entire project including hierarchical sheets
- Preserve all component properties (value, footprint, custom fields)
- Generate modular Python code with separate files for subcircuits
- Support batch conversion of multiple schematics

**Example**:
```bash
$ kicad-to-python power_supply.kicad_pro output/
✅ Converted project to output/
   - output/main.py (main schematic)
   - output/buck_converter.py (subcircuit)
   - output/linear_regulator.py (subcircuit)
```

---

### Story 3: Template Generation (Design Reuse)
**As a** circuit designer
**I want to** extract reusable subcircuits from successful designs
**So that** I can create a library of tested circuit patterns

**Acceptance Criteria**:
- Export specific hierarchical sheets as standalone functions
- Include documentation and parameter descriptions
- Generate code that can be imported into other projects
- Support parameterization of common values

**Example**:
```python
# Generated template
from kicad_sch_api import create_schematic

def buck_converter_3v3(sch, position, input_voltage='12V'):
    """
    3.3V Buck Converter

    Args:
        sch: Target schematic
        position: Placement (x, y)
        input_voltage: Input voltage (default: 12V)
    """
    # ... generated circuit code ...
```

---

### Story 4: Documentation Generation (Maintainer)
**As a** library maintainer
**I want to** generate Python examples from reference schematics
**So that** documentation always shows correct, tested code

**Acceptance Criteria**:
- Export reference test schematics to Python
- Include in documentation as runnable examples
- Verify examples stay synchronized with API changes
- Support inline comments and explanations

---

## Requirements

### Functional Requirements

#### FR-1: Component Export
**Priority**: P0 (Must Have)
**Description**: Export all components with full properties

**Details**:
- Component reference (R1, C1, U1, etc.)
- Library identifier (Device:R, Device:C, etc.)
- Value (10k, 100nF, etc.)
- Footprint (Resistor_SMD:R_0603_1608Metric, etc.)
- Position (x, y coordinates)
- Rotation (0°, 90°, 180°, 270°)
- Custom properties (MPN, Tolerance, etc.)

**Example Output**:
```python
r1 = sch.components.add('Device:R', reference='R1', value='10k',
                        position=(100.33, 101.60), rotation=0)
r1.footprint = 'Resistor_SMD:R_0603_1608Metric'
r1.set_property('MPN', 'RC0603FR-0710KL')
r1.set_property('Tolerance', '1%')
```

---

#### FR-2: Wire Export
**Priority**: P0 (Must Have)
**Description**: Export all wire connections

**Details**:
- Wire start point (x, y)
- Wire end point (x, y)
- Wire style (solid, dashed, etc.)
- Preserve wire routing and visual layout

**Example Output**:
```python
# Wire from R1 pin 2 to R2 pin 1
sch.add_wire(start=(110.49, 101.60), end=(140.08, 101.60))

# Vertical wire
sch.add_wire(start=(125.00, 140.00), end=(125.00, 160.00))
```

---

#### FR-3: Label Export
**Priority**: P0 (Must Have)
**Description**: Export all labels and text annotations

**Details**:
- Label text
- Label position (x, y)
- Label type (local, global, hierarchical)
- Label rotation and orientation

**Example Output**:
```python
sch.add_label('VCC', position=(100.00, 90.00), label_type='global')
sch.add_label('OUT', position=(125.00, 101.60), label_type='local')
sch.add_label('POWER_IN', position=(75.00, 100.00), label_type='hierarchical')
```

---

#### FR-4: Hierarchical Sheet Export
**Priority**: P1 (Should Have)
**Description**: Export hierarchical sheets and subcircuits

**Details**:
- Sheet name and filename
- Sheet position and size
- Sheet pins (inputs/outputs)
- Generate separate Python file for each sheet
- Hierarchical structure preservation

**Example Output**:
```python
# In main.py
power_sheet = sch.sheets.add_sheet(
    name='Power Supply',
    filename='power.kicad_sch',
    position=(50.00, 50.00),
    size=(100.00, 100.00)
)
power_sheet.add_pin('VIN', position=(50.00, 60.00), shape='input')
power_sheet.add_pin('VOUT', position=(150.00, 60.00), shape='output')

# In power.py
def create_power_supply():
    sch = create_schematic('Power Supply')
    # ... subcircuit implementation ...
    return sch
```

---

#### FR-5: CLI Command
**Priority**: P0 (Must Have)
**Description**: Command-line interface for export

**Details**:
- Command: `kicad-to-python`
- Input: `.kicad_sch` file or `.kicad_pro` project
- Output: `.py` file or directory
- Options: `--include-hierarchy`, `--add-comments`, `--format`, `--template`

**Example Usage**:
```bash
# Basic export
kicad-to-python input.kicad_sch output.py

# With options
kicad-to-python input.kicad_sch output.py \
    --include-hierarchy \
    --add-comments \
    --format black \
    --template verbose

# Hierarchical project
kicad-to-python project.kicad_pro output_dir/
```

---

#### FR-6: Python API Method
**Priority**: P1 (Should Have)
**Description**: Instance method on Schematic class

**Details**:
- Method: `schematic.export_to_python()`
- Parameters: output path, options
- Returns: Path to generated file

**Example Usage**:
```python
import kicad_sch_api as ksa

# Load and export
sch = ksa.Schematic.load('input.kicad_sch')
sch.export_to_python('output.py',
                     include_hierarchy=True,
                     add_comments=True,
                     format_code=True)
```

---

#### FR-7: Standalone Utility Function
**Priority**: P0 (Must Have)
**Description**: Utility function for one-line conversion

**Details**:
- Function: `ksa.schematic_to_python()`
- Parameters: input path, output path, options
- Returns: Path to generated file

**Example Usage**:
```python
import kicad_sch_api as ksa

# Quick conversion
ksa.schematic_to_python('input.kicad_sch', 'output.py')

# With template
ksa.schematic_to_python('input.kicad_sch', 'output.py',
                        template='minimal')  # or 'verbose', 'documented'
```

---

### Non-Functional Requirements

#### NFR-1: Code Quality
- Generated Python code must be valid and executable
- Follow PEP 8 style guidelines
- Use Black for formatting (if available)
- Include type hints where applicable
- Add docstrings for functions

#### NFR-2: Round-Trip Compatibility
- Running generated Python code must produce byte-identical `.kicad_sch` file
- All component properties must be preserved
- Visual layout (positions, wires) must be identical
- Hierarchical structure must be maintained

#### NFR-3: Performance
- Export time < 1 second for schematics with < 100 components
- Export time < 5 seconds for schematics with < 1000 components
- Memory usage proportional to schematic size

#### NFR-4: Readability
- Generated code must be human-readable
- Use meaningful variable names
- Group related operations (all components, then wires, then labels)
- Include comments explaining complex sections
- Avoid unnecessary verbosity

#### NFR-5: Error Handling
- Graceful handling of malformed schematics
- Clear error messages for missing data
- Warning for unsupported elements
- Validation of generated code syntax

---

## Proposed Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  KiCad-to-Python Export System                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Input Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  • CLI Command: kicad-to-python                                  │
│  • Python API: sch.export_to_python()                           │
│  • Utility: ksa.schematic_to_python()                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Loader Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  • Schematic.load('file.kicad_sch')                             │
│  • Parse S-expressions                                          │
│  • Build object model                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Analysis Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  • Extract components (ref, value, footprint, position)         │
│  • Extract wires (start, end points)                            │
│  • Extract labels (text, position, type)                        │
│  • Extract hierarchical sheets (name, filename, pins)           │
│  • Extract metadata (title, date, author)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Code Generation Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  • PythonCodeGenerator class                                     │
│  • Template system (minimal, verbose, documented)               │
│  • Variable name sanitization                                   │
│  • Code formatting (Black integration)                          │
│  • Comment generation                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  • Write .py file with proper encoding                          │
│  • Make executable (chmod +x)                                   │
│  • Generate supporting files (subcircuits)                      │
│  • Validation and syntax checking                               │
└─────────────────────────────────────────────────────────────────┘
```

---

### Key Components

#### 1. PythonCodeGenerator
**Location**: `kicad_sch_api/exporters/python_generator.py`

**Responsibilities**:
- Convert Schematic object to Python code
- Template management (minimal, verbose, documented)
- Variable name sanitization
- Code formatting

**Interface**:
```python
class PythonCodeGenerator:
    def __init__(self, template: str = 'default'):
        """Initialize generator with template style."""

    def generate(self, schematic: Schematic,
                 include_hierarchy: bool = True,
                 add_comments: bool = True) -> str:
        """Generate Python code from schematic."""

    def format_code(self, code: str) -> str:
        """Format code using Black (if available)."""
```

#### 2. CLI Command
**Location**: `kicad_sch_api/cli/kicad_to_python.py`

**Responsibilities**:
- Command-line argument parsing
- File I/O handling
- Progress reporting
- Error handling

#### 3. API Method
**Location**: `kicad_sch_api/core/schematic.py` (addition)

**Responsibilities**:
- Instance method on Schematic class
- Delegate to PythonCodeGenerator
- Return generated code or file path

#### 4. Utility Function
**Location**: `kicad_sch_api/__init__.py` (export)

**Responsibilities**:
- One-line convenience function
- Load → Generate → Save pipeline

---

## Technical Design

### Module Structure

```
kicad_sch_api/
├── exporters/
│   ├── __init__.py
│   ├── python_generator.py      # Core generator class
│   ├── templates/
│   │   ├── minimal.py.jinja2    # Minimal template
│   │   ├── default.py.jinja2    # Default template
│   │   ├── verbose.py.jinja2    # Verbose template
│   │   └── documented.py.jinja2 # Documented template
│   └── utils.py                 # Helper functions
├── cli/
│   ├── kicad_to_python.py       # CLI command
│   └── ...
└── core/
    ├── schematic.py             # Add export_to_python() method
    └── ...
```

### Code Generation Templates

#### Minimal Template
```python
#!/usr/bin/env python3
import kicad_sch_api as ksa

sch = ksa.create_schematic('{{name}}')

{% for component in components %}
{{component.variable}} = sch.components.add('{{component.lib_id}}', '{{component.ref}}', '{{component.value}}', position=({{component.x}}, {{component.y}}))
{% endfor %}

{% for wire in wires %}
sch.add_wire(start=({{wire.start_x}}, {{wire.start_y}}), end=({{wire.end_x}}, {{wire.end_y}}))
{% endfor %}

if __name__ == '__main__':
    sch.save('output.kicad_sch')
```

#### Documented Template
```python
#!/usr/bin/env python3
"""
{{title}}

Generated from: {{source_file}}
Generated by: kicad-sch-api v{{version}}
Date: {{date}}

This file was automatically generated from a KiCad schematic.
To regenerate the schematic, run: python {{filename}}
"""

import kicad_sch_api as ksa

def create_{{name|sanitize}}():
    """
    Create {{title}} schematic.

    Components:
    {% for comp in components %}
    - {{comp.ref}}: {{comp.value}} ({{comp.lib_id}})
    {% endfor %}

    Returns:
        Schematic object
    """
    # Create schematic
    sch = ksa.create_schematic('{{name}}')

    # Add components
    {% for component in components %}
    # {{component.ref}}: {{component.value}}
    {{component.variable}} = sch.components.add(
        '{{component.lib_id}}',
        reference='{{component.ref}}',
        value='{{component.value}}',
        position=({{component.x}}, {{component.y}}),
        rotation={{component.rotation}}
    )
    {{component.variable}}.footprint = '{{component.footprint}}'
    {% for prop in component.properties %}
    {{component.variable}}.set_property('{{prop.name}}', '{{prop.value}}')
    {% endfor %}

    {% endfor %}

    # Add wires
    {% for wire in wires %}
    sch.add_wire(start=({{wire.start_x}}, {{wire.start_y}}),
                 end=({{wire.end_x}}, {{wire.end_y}}))
    {% endfor %}

    # Add labels
    {% for label in labels %}
    sch.add_label('{{label.text}}',
                  position=({{label.x}}, {{label.y}}),
                  label_type='{{label.type}}')
    {% endfor %}

    return sch

if __name__ == '__main__':
    schematic = create_{{name|sanitize}}()
    schematic.save('{{name}}.kicad_sch')
    print('✅ Schematic generated: {{name}}.kicad_sch')
```

---

### Algorithm: Code Generation

```python
def generate_python_code(schematic: Schematic, options: dict) -> str:
    """
    Generate Python code from schematic.

    Algorithm:
    1. Extract metadata (name, title, version)
    2. Extract all components with properties
    3. Extract all wires
    4. Extract all labels
    5. Extract hierarchical sheets (if enabled)
    6. Load template based on style
    7. Render template with data
    8. Format code (Black, if available)
    9. Validate syntax (compile check)
    10. Return generated code
    """

    # Step 1: Extract metadata
    metadata = {
        'name': schematic.name,
        'title': schematic.title,
        'version': ksa.__version__,
        'date': datetime.now().isoformat(),
        'source_file': schematic.filepath
    }

    # Step 2: Extract components
    components = []
    for component in schematic.components:
        comp_data = {
            'ref': component.reference,
            'variable': sanitize_variable_name(component.reference),
            'lib_id': component.lib_id,
            'value': component.value,
            'footprint': component.footprint,
            'x': component.position.x,
            'y': component.position.y,
            'rotation': component.rotation,
            'properties': extract_custom_properties(component)
        }
        components.append(comp_data)

    # Step 3: Extract wires
    wires = []
    for wire in schematic.wires:
        wire_data = {
            'start_x': wire.start.x,
            'start_y': wire.start.y,
            'end_x': wire.end.x,
            'end_y': wire.end.y
        }
        wires.append(wire_data)

    # Step 4: Extract labels
    labels = []
    for label in schematic.labels:
        label_data = {
            'text': label.text,
            'x': label.position.x,
            'y': label.position.y,
            'type': label.label_type
        }
        labels.append(label_data)

    # Step 5: Extract hierarchical sheets (if enabled)
    sheets = []
    if options.get('include_hierarchy'):
        for sheet in schematic.sheets:
            sheet_data = extract_sheet_data(sheet)
            sheets.append(sheet_data)

    # Step 6-7: Load and render template
    template_name = options.get('template', 'default')
    template = load_template(template_name)
    code = template.render(
        metadata=metadata,
        components=components,
        wires=wires,
        labels=labels,
        sheets=sheets
    )

    # Step 8: Format code
    if options.get('format_code', True):
        code = format_with_black(code)

    # Step 9: Validate syntax
    try:
        compile(code, '<generated>', 'exec')
    except SyntaxError as e:
        raise CodeGenerationError(f"Generated invalid Python: {e}")

    # Step 10: Return
    return code
```

---

### Variable Name Sanitization

```python
def sanitize_variable_name(name: str) -> str:
    """
    Convert component reference to valid Python variable name.

    Rules:
    - Convert to lowercase
    - Replace invalid characters with underscore
    - Prefix with underscore if starts with digit
    - Handle special cases (power nets, etc.)

    Examples:
        R1 → r1
        C10 → c10
        U$1 → u_1
        3V3 → _3v3
        +5V → _5v
    """
    # Handle special power net cases
    power_nets = {
        '3V3': '_3v3',
        '5V': '_5v',
        '12V': '_12v',
        'VCC': 'vcc',
        'GND': 'gnd'
    }
    if name in power_nets:
        return power_nets[name]

    # Convert to lowercase
    var_name = name.lower()

    # Replace invalid characters
    var_name = var_name.replace('$', '_')
    var_name = var_name.replace('+', 'p')
    var_name = var_name.replace('-', 'n')
    var_name = re.sub(r'[^a-z0-9_]', '_', var_name)

    # Prefix if starts with digit
    if var_name and var_name[0].isdigit():
        var_name = '_' + var_name

    return var_name
```

---

## Implementation Plan

### Phase 1: Core Functionality (Week 1)
**Goal**: Basic export working for simple schematics

#### Tasks:
1. **Create PythonCodeGenerator class** (2 days)
   - Basic code generation logic
   - Minimal template support
   - Variable name sanitization

2. **Implement CLI command** (1 day)
   - Argument parsing
   - File I/O
   - Error handling

3. **Add utility function** (0.5 days)
   - `ksa.schematic_to_python()` wrapper
   - Export to `__init__.py`

4. **Write unit tests** (1.5 days)
   - Component export tests
   - Wire export tests
   - Label export tests
   - Round-trip tests

5. **Create reference tests** (1 day)
   - Use existing reference schematics
   - Verify byte-perfect round-trip

**Deliverable**: Basic export working for `single_resistor.kicad_sch`

---

### Phase 2: Enhanced Features (Week 2)
**Goal**: Production-ready with multiple templates

#### Tasks:
1. **Template system** (2 days)
   - Jinja2 integration
   - Multiple templates (minimal, default, verbose, documented)
   - Template selection logic

2. **API method** (1 day)
   - Add `schematic.export_to_python()` method
   - Integration with existing Schematic class

3. **Code formatting** (1 day)
   - Black integration (optional)
   - Fallback formatting
   - Syntax validation

4. **Enhanced testing** (1.5 days)
   - Template tests
   - Format tests
   - Edge case tests

5. **Documentation** (1.5 days)
   - API documentation
   - Usage examples
   - Tutorial

**Deliverable**: Production-ready export with multiple templates

---

### Phase 3: Hierarchical Support (Week 3)
**Goal**: Full hierarchical schematic support

#### Tasks:
1. **Hierarchical analysis** (2 days)
   - Sheet extraction
   - Pin mapping
   - Cross-reference resolution

2. **Multi-file generation** (2 days)
   - Main file + subcircuit files
   - Import statements
   - Directory structure

3. **Hierarchical tests** (1 day)
   - Test with real hierarchical projects
   - Verify structure preservation

4. **Documentation updates** (1 day)
   - Hierarchical examples
   - Best practices

5. **Final polish** (1 day)
   - Performance optimization
   - Error message improvement
   - Code review

**Deliverable**: Full hierarchical support

---

## Success Metrics

### Quantitative Metrics
1. **Adoption**: >50 downloads/week within first month
2. **Round-Trip Accuracy**: 100% byte-perfect for non-hierarchical schematics
3. **Performance**: <1s for <100 component schematics
4. **Test Coverage**: >90% code coverage
5. **Error Rate**: <5% of exports fail

### Qualitative Metrics
1. **User Satisfaction**: Positive feedback in GitHub issues/discussions
2. **Code Quality**: Passes all linting and type checks
3. **Documentation Quality**: No common usage questions in issues
4. **Integration**: Used in at least 3 community projects

---

## Open Questions

### Q1: Import Style
**Question**: Should we use `import kicad_sch_api as ksa` or `from kicad_sch_api import *`?

**Options**:
- A) `import kicad_sch_api as ksa` (explicit, recommended)
- B) `from kicad_sch_api import *` (concise, less typing)
- C) Configurable via template

**Recommendation**: **Option A** for default, **Option C** for flexibility

**Rationale**: Explicit imports are Python best practice and aid readability.

---

### Q2: Verbosity Level
**Question**: How verbose should default generated code be?

**Options**:
- A) Minimal (only essential parameters)
- B) Moderate (common parameters + comments)
- C) Verbose (all parameters + extensive comments)

**Recommendation**: **Option B** for default, with templates for A and C

**Rationale**: Balance between readability and completeness.

---

### Q3: Component Ordering
**Question**: Should we preserve original component ordering or sort alphabetically?

**Options**:
- A) Preserve original order (matches schematic)
- B) Sort alphabetically (R1, R2, R10 vs R1, R10, R2)
- C) Group by type (all resistors, then capacitors, etc.)

**Recommendation**: **Option A** for default

**Rationale**: Preserves design intent and visual layout.

---

### Q4: Error Handling
**Question**: How should we handle components with missing data (no footprint, no value)?

**Options**:
- A) Skip component with warning
- B) Export with empty/None values
- C) Fail entire export

**Recommendation**: **Option B** with warnings

**Rationale**: Allows partial exports, user can fix manually.

---

## Appendices

### Appendix A: Circuit-Synth Analysis

Circuit-synth implementation review:

**Key Files**:
- `kicad_to_python_sync.py`: Main synchronization class
- `python_code_generator.py`: Code generation logic
- `models.py`: Data structures (Circuit, Component, Net)

**Learnings**:
1. ✅ Template-based approach works well
2. ✅ Separate loader → analyzer → generator layers
3. ✅ Variable name sanitization is critical
4. ✅ Support for hierarchical circuits is complex but valuable
5. ⚠️ circuit-synth uses different API (`Component()` vs `sch.components.add()`)

**Adaptations for kicad-sch-api**:
- Use kicad-sch-api object model directly (no intermediate models needed)
- Generate kicad-sch-api API calls instead of circuit-synth API
- Leverage existing `Schematic.load()` infrastructure
- Maintain exact format preservation philosophy

---

### Appendix B: Example Generated Code

**Input**: `resistor_divider.kicad_sch`

**Output**: `resistor_divider.py`
```python
#!/usr/bin/env python3
"""
Resistor Divider Circuit

Generated from: resistor_divider.kicad_sch
Generated by: kicad-sch-api v0.5.0
Date: 2025-11-07T10:30:00
"""

import kicad_sch_api as ksa

def create_resistor_divider():
    """
    Create resistor divider schematic.

    Components:
    - R1: 10k (Device:R)
    - R2: 10k (Device:R)

    Returns:
        Schematic object
    """
    # Create schematic
    sch = ksa.create_schematic('Resistor Divider')

    # Add components
    # R1: 10k
    r1 = sch.components.add(
        'Device:R',
        reference='R1',
        value='10k',
        position=(100.33, 101.60),
        rotation=0
    )
    r1.footprint = 'Resistor_SMD:R_0603_1608Metric'

    # R2: 10k
    r2 = sch.components.add(
        'Device:R',
        reference='R2',
        value='10k',
        position=(100.33, 127.00),
        rotation=0
    )
    r2.footprint = 'Resistor_SMD:R_0603_1608Metric'

    # Add wires
    sch.add_wire(start=(100.33, 96.52), end=(100.33, 90.00))
    sch.add_wire(start=(100.33, 106.68), end=(100.33, 114.30))
    sch.add_wire(start=(100.33, 114.30), end=(100.33, 121.92))
    sch.add_wire(start=(100.33, 132.08), end=(100.33, 140.00))

    # Add labels
    sch.add_label('VCC', position=(100.33, 85.00), label_type='global')
    sch.add_label('OUT', position=(115.00, 114.30), label_type='local')
    sch.add_label('GND', position=(100.33, 145.00), label_type='global')

    return sch

if __name__ == '__main__':
    schematic = create_resistor_divider()
    schematic.save('resistor_divider_regenerated.kicad_sch')
    print('✅ Schematic generated: resistor_divider_regenerated.kicad_sch')
```

---

### Appendix C: Testing Strategy

#### Round-Trip Tests
```python
def test_round_trip_simple_schematic():
    """Test that export → execute → load produces identical schematic."""

    # 1. Load original
    original = ksa.Schematic.load('tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch')

    # 2. Export to Python
    python_code = ksa.schematic_to_python(original, 'temp.py')

    # 3. Execute generated Python
    exec(compile(python_code, 'temp.py', 'exec'))

    # 4. Load regenerated schematic
    regenerated = ksa.Schematic.load('temp_regenerated.kicad_sch')

    # 5. Compare (byte-perfect)
    assert original.to_sexpr() == regenerated.to_sexpr()
```

#### Format Tests
```python
def test_generated_code_is_valid_python():
    """Test that generated code is syntactically valid."""

    sch = ksa.Schematic.load('tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch')
    code = ksa.schematic_to_python(sch)

    # Should compile without errors
    compile(code, '<generated>', 'exec')
```

#### Template Tests
```python
def test_minimal_template():
    """Test minimal template generates compact code."""

    sch = ksa.Schematic.load('tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch')
    code = ksa.schematic_to_python(sch, template='minimal')

    # Should be < 20 lines for single resistor
    assert len(code.split('\n')) < 20
```

---

### Appendix D: File Structure

```
kicad_sch_api/
├── exporters/
│   ├── __init__.py
│   │   # Export: PythonCodeGenerator, schematic_to_python
│   │
│   ├── python_generator.py
│   │   # class PythonCodeGenerator:
│   │   #     def __init__(template: str = 'default')
│   │   #     def generate(schematic: Schematic, **options) -> str
│   │   #     def format_code(code: str) -> str
│   │   #     def validate_syntax(code: str) -> bool
│   │   #     def _extract_components(schematic) -> List[dict]
│   │   #     def _extract_wires(schematic) -> List[dict]
│   │   #     def _extract_labels(schematic) -> List[dict]
│   │   #     def _extract_sheets(schematic) -> List[dict]
│   │   #     def _sanitize_variable_name(name: str) -> str
│   │
│   ├── templates/
│   │   ├── minimal.py.jinja2
│   │   ├── default.py.jinja2
│   │   ├── verbose.py.jinja2
│   │   └── documented.py.jinja2
│   │
│   └── utils.py
│       # Helper functions for code generation
│
├── cli/
│   ├── kicad_to_python.py
│   │   # CLI command implementation
│   │   # def main(args)
│   │   # Argument parsing
│   │   # Progress reporting
│   │
│   └── setup.py
│       # Entry point registration
│
├── core/
│   └── schematic.py
│       # Add method:
│       # def export_to_python(self, output_path, **options) -> Path
│
└── __init__.py
    # Export utility function:
    # def schematic_to_python(input_path, output_path, **options) -> Path
```

---

## References

1. **Circuit-Synth Implementation**: `/Users/shanemattner/Desktop/circuit_synth_repos/circuit-synth/src/circuit_synth/tools/kicad_integration/`
2. **GitHub Issue**: https://github.com/circuit-synth/kicad-sch-api/issues/129
3. **KiCad S-expression Format**: https://dev-docs.kicad.org/en/file-formats/
4. **kicad-sch-api ADR**: `docs/ADR.md`
5. **PEP 8 Style Guide**: https://peps.python.org/pep-0008/
6. **Jinja2 Documentation**: https://jinja.palletsprojects.com/

---

**End of PRD**
