# Reference Schematic Tests Command - kicad-sch-api

## Usage
```bash
/run-reference-tests [project-name]
```

## Description
Runs comprehensive tests against reference KiCAD schematic projects to validate parsing, manipulation, and format preservation across all schematic element types.

## Parameters
- `project-name` (optional): Specific reference project to test (e.g., "02_multiple_passive_components")
- `--create-missing`: Create test files for reference projects that don't have tests yet
- `--format-validation`: Focus on format preservation testing
- `--performance`: Include performance benchmarking

## Reference Project Structure

```
tests/reference_kicad_projects/
├── README.md                           # Project checklist and status
├── 01_simple_resistor/                 # ✅ Basic component
│   ├── simple_resistor.kicad_sch
│   └── test_simple_resistor.py
├── 02_multiple_passive_components/     # 🔲 Component variety  
│   ├── multiple_passives.kicad_sch
│   └── test_multiple_passives.py
├── 04_label_types/                     # 🔲 All label types
│   ├── label_types.kicad_sch
│   └── test_label_types.py
└── [... 25 more reference projects]
```

## Implementation

```bash
#!/bin/bash

# Parse arguments
PROJECT_NAME=""
CREATE_MISSING=false
FORMAT_VALIDATION=false
PERFORMANCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --create-missing)
            CREATE_MISSING=true
            shift
            ;;
        --format-validation)
            FORMAT_VALIDATION=true
            shift
            ;;
        --performance)
            PERFORMANCE=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            PROJECT_NAME="$1"
            shift
            ;;
    esac
done

# Ensure we're in correct directory
cd python/tests/reference_kicad_projects || {
    echo "❌ Must run from kicad-sch-api root"
    exit 1
}

if [[ -n "$PROJECT_NAME" ]]; then
    # Test specific project
    if [[ ! -d "$PROJECT_NAME" ]]; then
        echo "❌ Reference project not found: $PROJECT_NAME"
        echo "Available projects:"
        ls -1 | grep -E '^[0-9]+_' | head -10
        exit 1
    fi
    
    echo "🧪 Testing reference project: $PROJECT_NAME"
    
    # Run project-specific tests
    if [[ -f "$PROJECT_NAME/test_${PROJECT_NAME}.py" ]]; then
        cd ../../..  # Back to python directory
        uv run pytest "tests/reference_kicad_projects/$PROJECT_NAME/" -v
    else
        echo "⚠️ No test file found for $PROJECT_NAME"
        if [[ "$CREATE_MISSING" == "true" ]]; then
            echo "🔧 Creating test template..."
            # Create test template (implementation below)
        fi
    fi
else
    # Test all reference projects
    echo "🧪 Testing all reference schematic projects..."
    
    cd ../../..  # Back to python directory
    
    # Run all reference tests
    if [[ "$FORMAT_VALIDATION" == "true" ]]; then
        uv run pytest tests/reference_kicad_projects/ -v -k "format_preservation"
    elif [[ "$PERFORMANCE" == "true" ]]; then
        uv run pytest tests/reference_kicad_projects/ -v -k "performance"
    else
        uv run pytest tests/reference_kicad_projects/ -v
    fi
fi
```

## Test Template Generation

When `--create-missing` is used, generates test template:

```python
# Template: test_{project_name}.py
"""
Tests for {project_name} reference schematic.
Tests parsing, manipulation, and format preservation.
"""

import pytest
from pathlib import Path

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.utils.validation import ValidationError


class Test{ProjectName}:
    """Test {project_name} reference schematic functionality."""

    @pytest.fixture
    def reference_schematic_path(self):
        """Get path to reference schematic."""
        return Path(__file__).parent / "{project_name}.kicad_sch"

    @pytest.fixture
    def loaded_schematic(self, reference_schematic_path):
        """Load reference schematic for testing."""
        return Schematic.load(reference_schematic_path)

    def test_parse_{project_name}(self, loaded_schematic):
        """Test parsing {project_name} without errors."""
        # Basic parsing validation
        assert loaded_schematic is not None
        assert loaded_schematic.version is not None
        assert loaded_schematic.uuid is not None
        
        # Validate component count matches expectations
        # TODO: Update expected count based on actual schematic
        expected_components = 1  # Update this
        assert len(loaded_schematic.components) == expected_components

    def test_round_trip_format_preservation(self, reference_schematic_path, tmp_path):
        """Test that format is preserved in round-trip operations."""
        # Load original
        sch = Schematic.load(reference_schematic_path)
        
        # Save to temporary file
        output_path = tmp_path / "output.kicad_sch"
        sch.save(output_path, preserve_format=True)
        
        # Read both files
        with open(reference_schematic_path, 'r') as f:
            original = f.read()
        with open(output_path, 'r') as f:
            output = f.read()
        
        # Validate structural preservation
        assert original.count('(symbol') == output.count('(symbol')
        assert original.count('(property') == output.count('(property')
        
        # TODO: Add specific element validation based on project content

    def test_modify_{project_name}(self, loaded_schematic, tmp_path):
        """Test modifying {project_name} elements."""
        # Make a simple modification
        if len(loaded_schematic.components) > 0:
            first_comp = loaded_schematic.components[0]
            original_value = first_comp.value
            first_comp.value = "modified_value"
            
            # Save and reload
            output_path = tmp_path / "modified.kicad_sch"
            loaded_schematic.save(output_path)
            
            sch2 = Schematic.load(output_path)
            modified_comp = sch2.components.get(first_comp.reference)
            
            assert modified_comp.value == "modified_value"
            assert modified_comp.value != original_value

    def test_validation_{project_name}(self, loaded_schematic):
        """Test validation of {project_name}."""
        issues = loaded_schematic.validate()
        
        # Should have no critical errors
        errors = [issue for issue in issues if issue.level.value in ('error', 'critical')]
        assert len(errors) == 0, f"Validation errors found: {[str(e) for e in errors]}"
```

## Test Execution Examples

```bash
# Test all reference projects
/run-reference-tests

# Test specific project
/run-reference-tests 02_multiple_passive_components

# Test with format validation focus
/run-reference-tests --format-validation

# Test with performance benchmarking
/run-reference-tests --performance

# Create missing test files
/run-reference-tests --create-missing

# Test specific category
/run-reference-tests 04_label_types --format-validation
```

## Expected Coverage by Project

### Basic Components (Projects 01-03)
- **Parse accuracy**: All components extracted correctly
- **Property handling**: Values, footprints, custom properties
- **Position accuracy**: Coordinate preservation
- **Reference validation**: Unique references maintained

### Labels and Text (Projects 04-05)
- **Label types**: Local, global, hierarchical parsing
- **Text elements**: Text boxes, annotations, special characters
- **Font effects**: Size, bold, italic, justification
- **Unicode handling**: International characters preserved

### Hierarchical Design (Projects 06-10)
- **Sheet symbols**: Hierarchical sheet parsing
- **Pin mapping**: Hierarchical pin connections
- **Multi-file projects**: Cross-file reference resolution
- **Deep nesting**: Complex hierarchy validation

### Complex Components (Projects 11-16)
- **Symbol inheritance**: "extends" relationship handling
- **Multi-unit symbols**: Unit numbering and shared properties
- **Large pin counts**: 100+ pin components (MCUs, FPGAs)
- **Special component types**: Power symbols, connectors

### Graphics and Advanced (Projects 17-28)
- **Graphical elements**: Shapes, lines, arcs
- **Images**: Embedded graphics and logos
- **Performance**: Large schematic handling
- **Edge cases**: Format limits and unusual elements

## Quality Metrics

### Performance Targets
- **Parsing time**: <100ms for typical schematics
- **Memory usage**: <50MB for complex schematics  
- **Symbol lookup**: <1ms for cached symbols
- **Bulk operations**: <10ms per component update

### Accuracy Targets
- **Format preservation**: 100% byte-level accuracy for unchanged elements
- **Round-trip fidelity**: 100% data preservation
- **Validation coverage**: All schematic rules validated
- **Error detection**: All format violations caught

## Integration with CI/CD

```yaml
# GitHub Actions integration
- name: Reference Schematic Tests
  run: |
    cd python
    /run-reference-tests --format-validation

- name: Performance Benchmarks
  run: |
    cd python  
    /run-reference-tests --performance
```

## Troubleshooting

**If reference tests fail**:
1. Check that reference schematic files are valid KiCAD format
2. Verify kicad-sch-api installation: `uv run python -c "import kicad_sch_api"`
3. Run single test for debugging: `uv run pytest tests/reference_kicad_projects/01_simple_resistor/ -v -s`
4. Check test logs for specific parsing errors

**If format preservation fails**:
1. Enable debug logging to see parsing details
2. Compare original vs. output files manually
3. Check for whitespace or encoding differences
4. Validate S-expression structure integrity

This command ensures all reference schematics work correctly with kicad-sch-api and maintain professional quality standards.