# Test Template Quick Reference

One-page guide to the 6 pin connection test templates.

## Which Template Should I Use?

| Scenario | Template | File |
|----------|----------|------|
| Testing single method behavior | Unit | `01_unit_test_template.py` |
| Testing complete workflows | Integration | `02_integration_test_template.py` |
| Testing against KiCAD files | Reference | `03_reference_test_template.py` |
| Testing multiple cases at once | Parametrized | `04_parametrized_test_template.py` |
| Creating reusable test setup | Fixtures | `05_fixtures_library_template.py` |
| Creating reusable assertions | Helpers | `06_assertion_helpers_template.py` |

## Template Quick Start

### Unit Test (Test a single pin method)

```python
import pytest
import kicad_sch_api as ksa

class TestGetComponentPins:
    @pytest.fixture
    def schematic(self):
        return ksa.create_schematic("Test")

    def test_get_pin_position_exists(self, schematic):
        r1 = schematic.components.add("Device:R", "R1", "10k", (100, 100))
        pin = r1.get_pin_position("1")
        assert pin is not None
```

### Integration Test (Test workflows)

```python
def test_save_load_pins(temp_schematic_file):
    # Create and save
    sch = ksa.create_schematic("Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
    original_pin = r1.get_pin_position("1")
    sch.save(temp_schematic_file)

    # Load and verify
    sch2 = ksa.Schematic.load(temp_schematic_file)
    r1_reloaded = sch2.components.get("R1")
    reloaded_pin = r1_reloaded.get_pin_position("1")

    assert reloaded_pin == original_pin
```

### Reference Test (Test against KiCAD)

```python
def test_pin_vs_kicad():
    # Load manually created KiCAD file
    sch = ksa.Schematic.load("tests/reference_kicad_projects/test/test.kicad_sch")
    r1 = sch.components.get("R1")

    # Get calculated pin position
    pin1 = r1.get_pin_position("1")

    # Compare to expected values (from KiCAD S-expressions)
    assert math.isclose(pin1.x, 96.52, abs_tol=0.05)
    assert math.isclose(pin1.y, 104.14, abs_tol=0.05)
```

### Parametrized Test (Test multiple cases)

```python
@pytest.mark.parametrize("rotation,pin_count", [
    (0, 2),
    (90, 2),
    (180, 2),
    (270, 2),
])
def test_pins_at_rotations(rotation, pin_count):
    sch = ksa.create_schematic("Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100), rotation=rotation)

    pin1 = r1.get_pin_position("1")
    pin2 = r1.get_pin_position("2")

    assert pin1 is not None
    assert pin2 is not None
```

### Fixtures (Reusable setup)

```python
# In conftest.py or test file

@pytest.fixture
def voltage_divider():
    """Create complete voltage divider circuit."""
    sch = ksa.create_schematic("VDiv")
    sch.components.add("power:VCC", "#PWR01", "VCC", (100, 50))
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
    r2 = sch.components.add("Device:R", "R2", "10k", (100, 150))
    sch.components.add("power:GND", "#PWR02", "GND", (100, 200))
    return sch

# In test:
def test_divider_pins(voltage_divider):
    r1 = voltage_divider.components.get("R1")
    pin = r1.get_pin_position("1")
    assert pin is not None
```

### Assertion Helpers (Reusable checks)

```python
# Define custom assertions
def assert_pin_exists(component, pin_number):
    pin = component.get_pin_position(pin_number)
    if pin is None:
        raise AssertionError(f"Pin {pin_number} not found")

def assert_pin_distance(component, pin1, pin2, expected_dist, tol=0.1):
    p1 = component.get_pin_position(pin1)
    p2 = component.get_pin_position(pin2)
    dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
    assert math.isclose(dist, expected_dist, abs_tol=tol)

# In test:
def test_with_helpers(schematic):
    r1 = schematic.components.get("R1")
    assert_pin_exists(r1, "1")
    assert_pin_distance(r1, "1", "2", 3.81)
```

## Common Patterns

### Test Pin Exists
```python
pin = comp.get_pin_position("1")
assert pin is not None
```

### Test Pin Position
```python
pin = comp.get_pin_position("1")
assert math.isclose(pin.x, 100.0, abs_tol=0.05)
assert math.isclose(pin.y, 104.14, abs_tol=0.05)
```

### Test Pin Distance
```python
pin1 = comp.get_pin_position("1")
pin2 = comp.get_pin_position("2")
dist = math.sqrt((pin2.x - pin1.x)**2 + (pin2.y - pin1.y)**2)
assert math.isclose(dist, 3.81, abs_tol=0.1)
```

### Test Pin at All Rotations
```python
for rotation in [0, 90, 180, 270]:
    comp = sch.components.add("Device:R", "R1", "10k", (100, 100), rotation=rotation)
    pin = comp.get_pin_position("1")
    assert pin is not None
```

### Test Multiple Components
```python
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
r2 = sch.components.add("Device:R", "R2", "10k", (150, 100))

pin1_r1 = r1.get_pin_position("1")
pin1_r2 = r2.get_pin_position("1")

assert pin1_r1 != pin1_r2  # Different positions
```

### Test Save/Load
```python
sch = ksa.create_schematic("Test")
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
orig_pin = r1.get_pin_position("1")

sch.save("test.kicad_sch")
sch2 = ksa.Schematic.load("test.kicad_sch")
r1_new = sch2.components.get("R1")
new_pin = r1_new.get_pin_position("1")

assert orig_pin == new_pin
```

## Pytest Fixtures

### Basic Fixture
```python
@pytest.fixture
def schematic():
    return ksa.create_schematic("Test")
```

### Fixture with Setup/Teardown
```python
@pytest.fixture
def temp_file():
    f = tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False)
    path = f.name
    f.close()
    yield path
    os.unlink(path)  # Cleanup
```

### Factory Fixture
```python
@pytest.fixture
def component_factory():
    def _add_component(sch, lib_id, ref, value, position):
        return sch.components.add(lib_id, ref, value, position)
    return _add_component

# Usage:
def test_factory(component_factory):
    sch = ksa.create_schematic("Test")
    r1 = component_factory(sch, "Device:R", "R1", "10k", (100, 100))
```

### Parametrized Fixture
```python
@pytest.fixture(params=[0, 90, 180, 270])
def rotation(request):
    return request.param

def test_rotation(rotation):
    sch = ksa.create_schematic("Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100), rotation=rotation)
    pin = r1.get_pin_position("1")
    assert pin is not None
```

## Running Tests

```bash
# Run all tests in file
pytest test_pins.py -v

# Run specific test
pytest test_pins.py::TestGetPins::test_pin_exists -v

# Run with logging
pytest test_pins.py -v -s

# Run with coverage
pytest test_pins.py --cov=kicad_sch_api --cov-report=html

# Run in watch mode
pytest-watch test_pins.py

# Stop on first failure
pytest test_pins.py -x -v

# Show local variables on failure
pytest test_pins.py -l -v
```

## Tolerance Guidelines

```python
# Exact match (for integers, strings)
assert value == expected

# Floating point with tolerance
import math
assert math.isclose(pin.x, 100.0, abs_tol=0.05)  # ±0.05mm tolerance

# For percentages
assert math.isclose(pin.x, 100.0, rel_tol=0.01)  # ±1% tolerance

# Multiple conditions
assert (pin1.x == pin2.x and pin1.y != pin2.y)  # Vertical alignment

# String matching
assert "Device:R" in component.lib_id
assert component.reference.startswith("R")
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# In test
logger.info("High-level info")      # Test started, completed
logger.debug("Detailed info")        # Intermediate values, calls
logger.warning("Unexpected but ok")  # Non-fatal issues
logger.error("Something failed")     # Errors (use pytest.fail instead)

# Run with logging
pytest test_pins.py -v -s --log-cli-level=DEBUG
```

## Debugging Failed Tests

```bash
# Show full traceback
pytest test_pins.py --tb=long

# Show local variables
pytest test_pins.py -l

# Drop into debugger on failure
pytest test_pins.py --pdb

# Continue after failure
pytest test_pins.py --pdbcls=IPython.terminal.debugger:TerminalPdb

# Verbose output with print statements
pytest test_pins.py -v -s
```

## Coverage

```bash
# Run with coverage
pytest tests/ --cov=kicad_sch_api --cov-report=html

# Check coverage report
open htmlcov/index.html

# Show lines not covered
pytest tests/ --cov=kicad_sch_api --cov-report=term-missing

# Target minimum coverage
pytest tests/ --cov=kicad_sch_api --cov-fail-under=95
```

## File Organization

```
tests/
├── _templates/                      # This library
│   ├── 01_unit_test_template.py    # Copy for unit tests
│   ├── 02_integration_test_template.py
│   ├── 03_reference_test_template.py
│   ├── 04_parametrized_test_template.py
│   ├── 05_fixtures_library_template.py  # Add to conftest.py
│   ├── 06_assertion_helpers_template.py # Add to conftest.py
│   ├── README.md                    # Full documentation
│   └── QUICK_REFERENCE.md          # This file
├── unit/
│   └── test_pin_positions.py       # Copied/customized from template 1
├── test_pin_workflow.py             # Copied/customized from template 2
├── conftest.py                      # Add fixtures & assertions here
└── reference_kicad_projects/
    ├── pin_rotation_0deg/
    │   └── pin_rotation_0deg.kicad_sch
    ├── pin_rotation_90deg/
    └── ...
```

## Copy Template

```bash
# Copy to your test file
cp tests/_templates/01_unit_test_template.py tests/unit/test_my_feature.py

# Edit the copied file
nano tests/unit/test_my_feature.py

# Run tests
pytest tests/unit/test_my_feature.py -v
```

## Essential Imports

```python
# Pytest
import pytest

# Standard library
import math
import logging
import tempfile
import os

# kicad-sch-api
import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

# Logging setup
logger = logging.getLogger(__name__)
```

## Minimal Test Example

```python
import pytest
import math
import kicad_sch_api as ksa

class TestMinimalPins:
    @pytest.fixture
    def schematic(self):
        return ksa.create_schematic("Test")

    def test_pin_exists(self, schematic):
        r1 = schematic.components.add("Device:R", "R1", "10k", (100, 100))
        pin = r1.get_pin_position("1")
        assert pin is not None
        assert math.isclose(pin.x, 100.0, abs_tol=1.0)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## Coverage Checklist

- [ ] Pin exists test
- [ ] Pin position test
- [ ] Pin distance test
- [ ] Multiple pins test
- [ ] Non-existent pin test
- [ ] All rotations test (0°, 90°, 180°, 270°)
- [ ] Multiple components test
- [ ] Save/load test
- [ ] Reference file test
- [ ] Edge cases (origin, large values)
- [ ] Different component types
- [ ] Error handling
- [ ] Wire connectivity test

## Next Steps

1. **Pick a template** based on what you're testing
2. **Copy the template** to your test directory
3. **Customize** the component types and expected values
4. **Run the tests** (they'll fail initially)
5. **Implement the feature** to make tests pass
6. **Add logging** to understand behavior
7. **Achieve >95% coverage** by combining templates

See `README.md` for detailed documentation of each template.
