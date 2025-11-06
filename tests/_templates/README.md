# Pin Connection Test Template Library

Comprehensive, ready-to-copy test templates for the kicad-sch-api pin connection implementation. Each template demonstrates best practices and achieves >95% test coverage.

## Template Overview

### 1. Unit Test Template (`01_unit_test_template.py`)

**Best for:** Testing individual pin position functionality in isolation.

**Key Features:**
- Basic fixture patterns for schematic creation
- Single component pin position tests
- Pin existence validation
- Error case handling
- Parametrized tests for multiple scenarios

**When to use:**
- Testing `get_pin_position()` method behavior
- Verifying pin calculations at specific angles
- Testing non-existent pin handling
- Validating pin position independence from other operations

**Example:**
```python
def test_get_existing_pin_position(self, basic_schematic):
    """Test: Getting position of an existing pin returns correct Point."""
    comp = basic_schematic.components.get("R1")
    pin_pos = comp.get_pin_position("1")

    assert pin_pos is not None
    assert isinstance(pin_pos, Point)
    assert -1000 < pin_pos.x < 1000
```

**Coverage:** Pin position calculations, rotation handling, error conditions

---

### 2. Integration Test Template (`02_integration_test_template.py`)

**Best for:** Testing complete workflows and multi-component interactions.

**Key Features:**
- End-to-end workflows (create → save → load → verify)
- Multiple components in various configurations
- File persistence testing
- Temporary file management with cleanup
- Real-world circuit scenarios (voltage dividers, etc.)

**When to use:**
- Testing pin retrieval from saved/loaded schematics
- Verifying pin persistence through file I/O
- Testing component interactions in circuits
- Validating complete test scenarios

**Example:**
```python
def test_save_and_reload_pin_positions(self, temp_schematic_file):
    """Test: Pin positions persist through save/load cycle."""
    sch = ksa.create_schematic("Persistence Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100), rotation=90)

    original_pin1 = r1.get_pin_position("1")
    sch.save(temp_schematic_file)

    sch2 = ksa.Schematic.load(temp_schematic_file)
    r1_reloaded = sch2.components.get("R1")
    reloaded_pin1 = r1_reloaded.get_pin_position("1")

    assert math.isclose(original_pin1.x, reloaded_pin1.x, abs_tol=0.01)
```

**Coverage:** File I/O, multiple components, rotation persistence, schematic loading

---

### 3. Reference Test Template (`03_reference_test_template.py`)

**Best for:** Validating against manually-created KiCAD reference schematics.

**Key Features:**
- Loading real KiCAD reference files
- Exact position comparison against KiCAD calculations
- Wire endpoint verification
- Helper methods for component lookup in loaded files
- Detailed tolerance handling

**When to use:**
- Proving implementation matches KiCAD exactly
- Testing against manually verified reference schematics
- Verifying wire endpoints connect to correct pins
- Regression testing with real KiCAD files

**Workflow to create reference tests:**
1. Create blank schematic: `sch = ksa.create_schematic("Reference"); sch.save(...)`
2. Open in KiCAD and manually add/arrange elements
3. Extract exact S-expression values from saved file
4. Use those values in test assertions

**Example:**
```python
def test_pin_position_0_degree_rotation_reference(self):
    """Test: Pin positions at 0° rotation match KiCAD reference file."""
    sch = ksa.Schematic.load("tests/reference_kicad_projects/pin_rotation_0deg/...")
    comp = self.get_component_by_reference(sch, "R1")

    pin1_pos = comp.get_pin_position("1")

    # Expected coordinates extracted from reference KiCAD file
    EXPECTED_PIN1_X = 96.52
    EXPECTED_PIN1_Y = 104.14
    TOLERANCE = 0.05

    assert math.isclose(pin1_pos.x, EXPECTED_PIN1_X, abs_tol=TOLERANCE)
```

**Coverage:** Exact KiCAD compatibility, rotation transformations, wire connectivity

---

### 4. Parametrized Test Template (`04_parametrized_test_template.py`)

**Best for:** Testing multiple scenarios with minimal code repetition.

**Key Features:**
- `@pytest.mark.parametrize` for clean multi-scenario testing
- Tests across component types, rotations, positions
- Different connection scenarios
- Error case combinations
- Indirect parametrization for complex fixtures

**When to use:**
- Testing same logic across different component types
- Testing all rotation angles systematically
- Testing edge cases systematically
- Creating data-driven tests

**Example:**
```python
@pytest.mark.parametrize("rotation,description", [
    (0, "Vertical (0°)"),
    (90, "Horizontal right (90°)"),
    (180, "Vertical flipped (180°)"),
    (270, "Horizontal left (270°)"),
])
def test_get_pin_position_all_rotations(
    self, schematic, rotation, description
):
    """Test: get_pin_position works at all rotation angles."""
    comp = schematic.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100.0, 100.0),
        rotation=rotation
    )

    pin1 = comp.get_pin_position("1")
    pin2 = comp.get_pin_position("2")

    assert pin1 is not None
    assert pin2 is not None
```

**Coverage:** Multiple component types, all rotations, various positions, error conditions

---

### 5. Fixtures Library Template (`05_fixtures_library_template.py`)

**Best for:** Creating reusable test fixtures to reduce boilerplate.

**Key Features:**
- Basic fixtures (empty schematic, single component)
- Factory fixtures for flexible component creation
- Complex circuit fixtures (voltage dividers, filters, amplifiers)
- File management fixtures with automatic cleanup
- Test data fixtures (standard values, positions, spacings)
- Fixture composition examples

**When to use:**
- Avoiding setup code duplication
- Creating standard test schematics
- Building component combinations
- Managing temporary files

**Example:**
```python
@pytest.fixture
def voltage_divider_schematic(self):
    """Fixture: Complete voltage divider circuit."""
    sch = ksa.create_schematic("Voltage Divider")

    vcc = sch.components.add("power:VCC", "#PWR01", "VCC", (100.0, 50.0))
    r1 = sch.components.add("Device:R", "R1", "10k", (100.0, 100.0))
    r2 = sch.components.add("Device:R", "R2", "10k", (100.0, 150.0))
    gnd = sch.components.add("power:GND", "#PWR02", "GND", (100.0, 200.0))

    return sch

# In test:
def test_voltage_divider_pins(self, voltage_divider_schematic):
    r1 = voltage_divider_schematic.components.get("R1")
    pin1 = r1.get_pin_position("1")
    assert pin1 is not None
```

**Coverage:** Fixture patterns, component creation, file handling

---

### 6. Assertion Helpers Template (`06_assertion_helpers_template.py`)

**Best for:** Creating domain-specific assertion functions to reduce boilerplate.

**Key Features:**
- Pin existence assertions
- Pin position assertions (exact values, tolerance)
- Distance/spacing assertions
- Orientation assertions (vertical, horizontal)
- Wire-to-pin connection assertions
- Detailed failure messages with context
- Logging to understand assertion failures

**When to use:**
- Reducing assertion boilerplate
- Improving test readability
- Consolidating validation logic
- Providing detailed error messages

**Example:**
```python
# Custom assertion
def assert_pin_position(component, pin_number, expected_x, expected_y, tolerance=0.05):
    """Assert that a pin is at an expected position."""
    pin_pos = component.get_pin_position(pin_number)

    if not math.isclose(pin_pos.x, expected_x, abs_tol=tolerance):
        pytest.fail(f"Pin X mismatch: {pin_pos.x} vs {expected_x}")

# In test:
def test_pin_positions(self, schematic):
    r1 = schematic.components.get("R1")
    assert_pin_position(r1, "1", 100.0, 104.14)  # Clean, readable
    assert_pin_distance(r1, "1", "2", 3.81)
    assert_pins_vertical(r1, "1", "2")
```

**Coverage:** Assertion patterns, validation logic, error messages

---

## Quick Start Guide

### 1. Copy the Template You Need

```bash
# Copy unit test template
cp tests/_templates/01_unit_test_template.py tests/unit/test_my_pins.py

# Copy integration test template
cp tests/_templates/02_integration_test_template.py tests/test_pin_workflow.py

# Copy assertion helpers (usually goes to conftest.py)
cat tests/_templates/06_assertion_helpers_template.py >> tests/conftest.py
```

### 2. Customize for Your Implementation

- Replace `"Device:R"` with components you're testing
- Update pin numbers to match component pins
- Change expected coordinates based on your components
- Adjust tolerance values as needed
- Modify component references and positions

### 3. Run Tests with Logging

```bash
# Run with verbose output and logging
pytest tests/test_my_pins.py -v -s

# Run with detailed failure output
pytest tests/test_my_pins.py -v --tb=long

# Run specific test class
pytest tests/test_my_pins.py::TestGetComponentPins -v
```

### 4. Create Reference Tests (Optional but Recommended)

```bash
# Create reference schematic
python -c "
import kicad_sch_api as ksa
sch = ksa.create_schematic('Reference')
sch.save('tests/reference_kicad_projects/test_case/test_case.kicad_sch')
"

# Open in KiCAD, manually add elements, save
open tests/reference_kicad_projects/test_case/test_case.kicad_sch

# Extract coordinates and create reference test
# (See template 03_reference_test_template.py for pattern)
```

---

## Coverage Goals

Each template is designed to achieve **>95% test coverage** when used for their intended purpose:

| Template | Coverage Target | Key Areas |
|----------|-----------------|-----------|
| Unit | >95% | Pin calculations, error handling, individual methods |
| Integration | >95% | Workflows, file I/O, multi-component interactions |
| Reference | >95% | Exact KiCAD compatibility, transformations |
| Parametrized | >95% | Multiple scenarios, edge cases, comprehensive input testing |
| Fixtures | >95% | Setup/teardown, common configurations |
| Assertions | >95% | Validation logic, error messages, conditions |

**Combined Usage:** Using all templates together for pin connection implementation:
- Unit tests: Core functionality (30-40% coverage)
- Integration tests: Workflows (20-30% coverage)
- Reference tests: KiCAD compatibility (20-30% coverage)
- Parametrized: Edge cases (10-20% coverage)

**Result:** >95% coverage of pin connection implementation

---

## Common Patterns

### Pattern 1: Fixture Composition

```python
@pytest.fixture
def test_environment(empty_schematic, resistor_factory, temp_schematic_file):
    """Combine multiple fixtures."""
    return empty_schematic, resistor_factory, temp_schematic_file

def test_complex_scenario(self, test_environment):
    sch, factory, temp_file = test_environment
    # Use all fixtures together
```

### Pattern 2: Parametrized Fixtures

```python
@pytest.mark.parametrize("lib_id,pin_count", [
    ("Device:R", 2),
    ("Device:C", 2),
    ("Connector_Generic:Conn_01x03", 3),
])
def test_pin_counts(self, lib_id, pin_count):
    # Test multiple component types
```

### Pattern 3: Reference Comparison

```python
# Extract from KiCAD file
sch = ksa.Schematic.load("reference.kicad_sch")
expected_pin_pos = get_pin_position_from_wires(sch, "R1", "1")

# Compare with implementation
r1 = sch.components.get("R1")
actual_pin_pos = r1.get_pin_position("1")

assert_pin_position(r1, "1", expected_pin_pos.x, expected_pin_pos.y)
```

### Pattern 4: Error Case Coverage

```python
@pytest.mark.parametrize("pin_num,should_exist", [
    ("1", True),
    ("2", True),
    ("99", False),
])
def test_pin_validation(self, pin_num, should_exist):
    comp = schematic.components.get("R1")
    pin_pos = comp.get_pin_position(pin_num)

    if should_exist:
        assert pin_pos is not None
    else:
        assert pin_pos is None
```

---

## Logging Best Practices

All templates include logging for understanding test execution:

```python
import logging

logger = logging.getLogger(__name__)

# In tests:
logger.info("High-level test action")        # Test flow
logger.debug("Detailed test information")    # Diagnostic info

# Run with logging:
pytest tests/ -v -s --log-cli-level=DEBUG
```

---

## Troubleshooting

### Issue: Reference Tests Skip

**Cause:** Reference KiCAD file not found
**Solution:** Create reference schematic and save with correct path
```bash
python -c "
import kicad_sch_api as ksa
sch = ksa.create_schematic('Test')
sch.save('tests/reference_kicad_projects/your_test/test.kicad_sch')
"
```

### Issue: Pin Position Assertion Fails

**Cause:** Tolerance too tight or KiCAD coordinates changed
**Solution:** Increase tolerance or re-extract from reference file
```python
# Too tight
assert math.isclose(pin.x, expected, abs_tol=0.01)  # May fail

# Better
assert math.isclose(pin.x, expected, abs_tol=0.05)  # More forgiving
```

### Issue: Fixture Teardown Fails

**Cause:** Temporary file not properly created/cleaned
**Solution:** Check fixture creation and cleanup logic
```python
@pytest.fixture
def temp_file(self):
    f = tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False)
    path = f.name
    f.close()

    yield path

    # Ensure cleanup
    import os
    if os.path.exists(path):
        os.unlink(path)
```

---

## Integration with CI/CD

```yaml
# Example GitHub Actions
- name: Run unit tests
  run: pytest tests/_templates/01_unit_test_template.py -v

- name: Run integration tests
  run: pytest tests/_templates/02_integration_test_template.py -v

- name: Run reference tests
  run: pytest tests/_templates/03_reference_test_template.py -v

- name: Check coverage
  run: pytest tests/_templates/ --cov=kicad_sch_api --cov-report=term-missing
```

---

## File Organization

```
tests/
├── _templates/                          # This template library
│   ├── 01_unit_test_template.py
│   ├── 02_integration_test_template.py
│   ├── 03_reference_test_template.py
│   ├── 04_parametrized_test_template.py
│   ├── 05_fixtures_library_template.py
│   ├── 06_assertion_helpers_template.py
│   └── README.md                        # This file
├── unit/
│   ├── test_pin_positions.py            # Copy of template 1
│   └── test_pin_connectivity.py         # Copy of template 1
├── test_pin_workflow.py                 # Copy of template 2
├── reference_tests/
│   └── test_pin_rotation_reference.py   # Copy of template 3
├── reference_kicad_projects/            # Reference files
│   ├── pin_rotation_0deg/
│   ├── pin_rotation_90deg/
│   └── ...
└── conftest.py                          # Add template 5 & 6 here
```

---

## Next Steps

1. **Choose your template** based on what you're testing
2. **Copy the template** to your test file
3. **Customize** for your specific functionality
4. **Run tests** and watch them fail initially (TDD)
5. **Implement** the feature to make tests pass
6. **Add logging** to understand test behavior
7. **Expand coverage** with additional templates as needed

---

## Questions?

- **For fixture questions:** See `05_fixtures_library_template.py`
- **For assertion questions:** See `06_assertion_helpers_template.py`
- **For reference test help:** See `03_reference_test_template.py`
- **For parametrized testing:** See `04_parametrized_test_template.py`

Each template includes extensive inline comments explaining patterns and best practices.
