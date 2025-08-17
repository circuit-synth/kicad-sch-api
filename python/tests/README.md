# Test Framework Documentation

## Overview

The kicad-sch-api test framework has been refactored to use a cleaner, more maintainable approach:

1. **Top-level test scripts** (`test_*.py` in project root) - Simple Python scripts that demonstrate API usage
2. **Test runner** (`python/tests/test_runner.py`) - Validates that test scripts run and produce valid KiCAD files
3. **Reference projects** (`python/tests/reference_tests/reference_kicad_projects/`) - Manually created KiCAD projects for validation

## Test Structure

### Top-Level Test Scripts

Located in the project root, these scripts serve as both tests and examples:

- `test_single_resistor.py` - Creates a schematic with one resistor
- `test_two_resistors.py` - Creates a schematic with two resistors
- `test_blank_schematic.py` - Creates an empty schematic
- `test_resistor_divider.py` - Creates a resistor divider circuit
- Additional test scripts for features as they're implemented

Each script:
1. Imports `kicad_sch_api`
2. Creates a schematic using the API
3. Saves the result as a `.kicad_sch` file
4. Prints a success message

### Test Runner

The main test runner (`test_runner.py`) provides:

- **Structural validation** - Ensures generated files are valid KiCAD schematics
- **Component counting** - Verifies correct number of components
- **Script execution** - Runs test scripts in isolated environments
- **Clean execution** - No side effects or leftover files

### Reference Comparison Tests

For exact format preservation testing, use `test_against_references.py`:

- Compares generated output with reference KiCAD projects
- Identifies formatting differences
- Validates semantic equivalence (ignoring UUIDs)

## Running Tests

### Quick Validation
```bash
# Run all structural tests
cd python
uv run pytest tests/test_runner.py -v

# Run specific test
uv run pytest tests/test_runner.py::TestRunner::test_single_resistor -v
```

### Reference Comparison
```bash
# Compare against reference projects (may show formatting differences)
cd python
uv run pytest tests/test_against_references.py -v
```

### Manual Testing
```bash
# Run individual test script
uv run python test_single_resistor.py

# Opens generated file in KiCAD (macOS)
open test_single_resistor.kicad_sch
```

## Test Categories

1. **Implemented & Tested**
   - Single resistor placement
   - Multiple component placement
   - Blank schematic creation
   - Basic resistor divider

2. **Pending Implementation**
   - Wire connections
   - Labels (local, global, hierarchical)
   - Text elements and text boxes
   - Hierarchical sheets
   - Power symbols
   - Multi-unit components

## Adding New Tests

1. Create a new `test_*.py` file in the project root
2. Follow the existing pattern:
   ```python
   import kicad_sch_api as ksa
   
   def main():
       sch = ksa.create_schematic("Test Name")
       # Add components/elements
       sch.save("test_name.kicad_sch")
       print("✅ Created test schematic")
   
   if __name__ == "__main__":
       main()
   ```

3. Add the test to `TestRunner.test_scripts` list
4. Create a corresponding test method in `TestRunner`
5. If needed, create a reference project in KiCAD for comparison

## Design Philosophy

The refactored test framework prioritizes:

1. **Simplicity** - Test scripts are simple, readable examples
2. **Validation** - Focus on structural correctness over byte-perfect matching
3. **Maintainability** - Clear separation between test scripts and validation
4. **Documentation** - Test scripts serve as API usage examples
5. **Progressive Development** - Tests for features as they're implemented

## Known Limitations

- Format preservation is not yet byte-perfect with KiCAD output
- Some formatting differences in generated files (quotes, spacing)
- Wire, label, and hierarchical features not yet implemented
- Reference comparison tests may fail due to formatting differences

These will be addressed as the API matures and formatting is refined.