# Pin Connection Implementation Guide

Complete guide to implementing pin connection features using the test template library.

## Overview

This guide walks through implementing a pin connection feature from design to complete coverage. Uses test-driven development (TDD) with the provided template library.

## 1. Design Phase

### Define Requirements

Before writing any code, clarify what you're building:

```
Feature: Get Component Pin Positions

Requirement 1: Get pin position from component reference
  - Input: component reference (e.g., "R1"), pin number (e.g., "1")
  - Output: Point object with (x, y) coordinates
  - Error: Return None if component or pin doesn't exist

Requirement 2: Pin positions respect component transformation
  - Pin positions account for component position
  - Pin positions account for component rotation
  - Pin positions account for component mirroring (if applicable)

Requirement 3: Pin positions persist through save/load
  - Save schematic to file
  - Load schematic from file
  - Pin positions match original values (±tolerance)

Requirement 4: Work with multiple component types
  - Device:R (resistor) - 2 pins
  - Device:C (capacitor) - 2 pins
  - Device:D (diode) - 2 pins
  - Connector_Generic:Conn_01x03_Pin (header) - 3 pins
```

### Document Expected Values

For each requirement, document expected values:

```
Component: Device:R at (100, 100), rotation 0°
  Symbol defines: Pin 1 at (0, 3.81), Pin 2 at (0, -3.81) in symbol space
  Transformation: Y-axis negation (symbol space → schematic space)
  Expected: Pin 1 at (100, 96.19), Pin 2 at (100, 103.81)

Component: Device:R at (100, 100), rotation 90°
  Transformation: Y negation + 90° rotation
  Expected: Pin 1 at (96.19, 100), Pin 2 at (103.81, 100)
```

## 2. Test Design Phase

### Choose Test Templates

Map requirements to templates:

| Requirement | Primary Template | Supporting Templates |
|-------------|------------------|----------------------|
| Basic pin retrieval | Unit (01) | Fixtures (05), Assertions (06) |
| Multiple components | Integration (02) | Parametrized (04), Fixtures (05) |
| Transformations | Parametrized (04) | Unit (01), Reference (03) |
| Save/load | Integration (02) | Fixtures (05) |
| KiCAD compatibility | Reference (03) | Unit (01) |

### Create Test Plan

```
Phase 1: Unit Tests (Basic Functionality)
  ✓ Test pin existence
  ✓ Test pin position returns Point
  ✓ Test non-existent pin returns None
  ✓ Test pin position respects component location
  Target coverage: 60%

Phase 2: Parametrized Tests (Multiple Cases)
  ✓ Test all rotation angles (0°, 90°, 180°, 270°)
  ✓ Test different component types
  ✓ Test different positions
  Target coverage: +20% (total 80%)

Phase 3: Integration Tests (Complete Workflows)
  ✓ Test save/load persistence
  ✓ Test multi-component circuits
  Target coverage: +10% (total 90%)

Phase 4: Reference Tests (KiCAD Compatibility)
  ✓ Test against manually created KiCAD files
  Target coverage: +5% (total 95%)
```

## 3. Implementation Phase

### Step 1: Set Up Test Files

```bash
# Copy unit test template
cp tests/_templates/01_unit_test_template.py tests/unit/test_get_component_pins.py

# Copy integration test template
cp tests/_templates/02_integration_test_template.py tests/test_pin_connection_workflow.py

# Copy parametrized test template
cp tests/_templates/04_parametrized_test_template.py tests/unit/test_pin_rotation.py

# Add fixtures and helpers to conftest.py
cat tests/_templates/05_fixtures_library_template.py >> tests/conftest.py
cat tests/_templates/06_assertion_helpers_template.py >> tests/conftest.py
```

### Step 2: Customize Tests

Edit `tests/unit/test_get_component_pins.py`:

```python
# Replace placeholder fixtures with your setup
@pytest.fixture
def basic_schematic(self):
    """Create schematic with resistor at standard position."""
    logger.info("Creating basic_schematic fixture")
    sch = ksa.create_schematic("Pin Position Test")
    resistor = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100.0, 100.0),
        rotation=0
    )
    return sch

# Customize test for your component
def test_get_existing_pin_position(self, basic_schematic):
    """Test: Getting position of existing pin returns correct Point."""
    comp = basic_schematic.components.get("R1")

    # Act
    pin_pos = comp.get_pin_position("1")

    # Assert
    assert pin_pos is not None
    assert isinstance(pin_pos, Point)

    # For resistor at (100, 100, 0°):
    # Pin 1 should be at (100, ~96.19) based on symbol definition
    assert math.isclose(pin_pos.x, 100.0, abs_tol=0.1)
    assert math.isclose(pin_pos.y, 96.19, abs_tol=0.1)
```

### Step 3: Run Tests (They'll Fail)

```bash
pytest tests/unit/test_get_component_pins.py -v -s

# Expected output:
# FAILED - AttributeError: 'Component' object has no attribute 'get_pin_position'
# FAILED - 3 failures in 0.5s
```

This is expected in TDD! Tests define the API before implementation exists.

### Step 4: Implement Feature

Create `kicad_sch_api/core/components.py`:

```python
class Component:
    """Component wrapper with pin position calculation."""

    def get_pin_position(self, pin_number: str) -> Optional[Point]:
        """
        Get the schematic position of a component pin.

        Args:
            pin_number: Pin number as string (e.g., "1", "2")

        Returns:
            Point at pin position in schematic coordinates, or None if pin doesn't exist
        """
        # Get pin from symbol library
        if not hasattr(self, 'pins') or not self.pins:
            return None

        # Find pin with matching number
        pin = None
        for p in self.pins:
            if p.get('number') == pin_number:
                pin = p
                break

        if pin is None:
            return None

        # Get pin position in symbol space
        pin_x = pin.get('at', {}).get('x', 0)
        pin_y = pin.get('at', {}).get('y', 0)

        # Apply transformations
        # 1. Negate Y (symbol space uses +Y up, schematic uses +Y down)
        pin_y = -pin_y

        # 2. Apply rotation
        pin_x, pin_y = self._rotate_point((pin_x, pin_y), self.rotation)

        # 3. Apply mirroring (if needed)
        if self.mirror:
            pin_x = -pin_x

        # 4. Offset to component position
        result_x = self.position.x + pin_x
        result_y = self.position.y + pin_y

        return Point(result_x, result_y)

    def _rotate_point(self, point, angle):
        """Rotate point by angle around origin."""
        import math
        x, y = point
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        return new_x, new_y
```

### Step 5: Run Tests (Some Pass)

```bash
pytest tests/unit/test_get_component_pins.py -v -s

# Expected output:
# PASSED test_get_existing_pin_position
# PASSED test_get_multiple_pins_different_positions
# PASSED test_pin_position_respects_component_location
# FAILED test_pin_position_with_rotation_invalid_angle
# 4 passed, 1 failed in 0.5s
```

### Step 6: Iterate

- Fix failing tests by improving implementation
- Add more test cases
- Increase coverage
- Run parametrized tests for all rotation angles
- Run integration tests for save/load

### Step 7: Add Reference Tests

Create reference schematic:

```bash
python -c "
import kicad_sch_api as ksa
sch = ksa.create_schematic('Pin Position Reference')
r1 = sch.components.add('Device:R', 'R1', '10k', (96.52, 100.33), rotation=0)
sch.save('tests/reference_kicad_projects/pin_position_0deg/pin_position_0deg.kicad_sch')
"
```

Open in KiCAD and manually add wires to pins to establish reference coordinates:

1. Open the schematic in KiCAD
2. Add a wire connected to pin 1 and pin 2
3. Extract wire endpoint coordinates from the S-expressions
4. Save the schematic

Copy reference template and customize:

```python
def test_pin_position_0_degree_reference(self):
    """Test pin position against KiCAD reference file."""
    sch_path = "tests/reference_kicad_projects/pin_position_0deg/pin_position_0deg.kicad_sch"
    sch = ksa.Schematic.load(sch_path)

    r1 = self.get_component_by_reference(sch, "R1")
    pin1_pos = r1.get_pin_position("1")

    # Expected values from KiCAD wire endpoints
    EXPECTED_PIN1_X = 96.52
    EXPECTED_PIN1_Y = 104.14  # Wire endpoint Y coordinate

    assert math.isclose(pin1_pos.x, EXPECTED_PIN1_X, abs_tol=0.05)
    assert math.isclose(pin1_pos.y, EXPECTED_PIN1_Y, abs_tol=0.05)
```

## 4. Coverage Phase

### Run Coverage Analysis

```bash
pytest tests/unit/test_get_component_pins.py \
        tests/test_pin_connection_workflow.py \
        tests/unit/test_pin_rotation.py \
        --cov=kicad_sch_api.core.components \
        --cov-report=html \
        --cov-report=term-missing

# Expected: >95% coverage
```

### Identify Gaps

Look at coverage report:

```
Name                                              Stmts   Miss  Cover    Missing
──────────────────────────────────────────────────────────────────────────────
kicad_sch_api/core/components.py                   125      3    97%     45-47, 92
```

Add tests for missing lines:

```python
def test_pin_with_mirroring(self):
    """Test pin position with mirrored component."""
    # This covers line 45-47 (mirroring logic)
    sch = ksa.create_schematic("Mirror Test")
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100.0, 100.0),
        mirror="x"  # Mirror on X axis
    )

    pin1 = r1.get_pin_position("1")
    assert pin1 is not None
```

### Verify Edge Cases

```python
# Edge case: Component at grid origin
r1 = sch.components.add("Device:R", "R1", "10k", (0.0, 0.0))
pin1 = r1.get_pin_position("1")
assert pin1 is not None

# Edge case: Component at large position
r2 = sch.components.add("Device:R", "R2", "10k", (500.0, 500.0))
pin2 = r2.get_pin_position("1")
assert pin2 is not None

# Edge case: Non-existent component
pin3 = sch.get_component_pin_position("R999", "1")
assert pin3 is None
```

## 5. Validation Phase

### Run All Tests

```bash
# Run all pin connection tests
pytest tests/unit/test_get_component_pins.py \
        tests/unit/test_pin_rotation.py \
        tests/test_pin_connection_workflow.py \
        tests/reference_tests/test_pin_position_reference.py \
        -v

# Expected: All pass with >95% coverage
```

### Check Against Real KiCAD

```bash
# Create test schematic in KiCAD
python create_test_schematic.py

# Open in KiCAD GUI
open test_schematic.kicad_sch

# Verify visually that pins appear at expected locations
# (pins should align with wire endpoints)

# Run tests to verify programmatically
pytest tests/reference_tests/ -v
```

### Document Expected Behavior

```markdown
## Pin Position Calculation

### Behavior
- `component.get_pin_position(pin_number)` returns Point or None
- Returns None if pin doesn't exist
- Accounts for component position, rotation, and mirroring
- Works with symbols from KiCAD library

### Examples
1. Resistor at (100, 100), 0° rotation, pin 1 → Point(100, 96.52)
2. Resistor at (100, 100), 90° rotation, pin 1 → Point(96.52, 100)
3. Resistor at (100, 100), non-existent pin 99 → None
4. Non-existent component R999 → AttributeError or None

### Tolerance
- Pin positions accurate to ±0.05mm (grid precision)
```

## 6. Integration Phase

### Integrate into Codebase

```bash
# Commit implementation
git add kicad_sch_api/core/components.py
git commit -m "feat: Add get_pin_position() for pin connection support"

# Commit tests
git add tests/unit/test_get_component_pins.py
git add tests/unit/test_pin_rotation.py
git add tests/test_pin_connection_workflow.py
git commit -m "test: Add comprehensive pin position tests (>95% coverage)"

# Commit reference files
git add tests/reference_kicad_projects/pin_position_*/
git commit -m "test: Add KiCAD reference files for pin position validation"
```

### Update Documentation

Add to `docs/PIN_CONNECTIONS.md`:

```markdown
# Pin Connection Features

## Getting Pin Positions

### Basic Usage

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))

# Get pin position in schematic coordinates
pin1_pos = r1.get_pin_position("1")  # Returns Point(100, 96.52)
pin2_pos = r1.get_pin_position("2")  # Returns Point(100, 103.81)

# Non-existent pin returns None
pin99_pos = r1.get_pin_position("99")  # Returns None
```

### Supported Components

See [supported_components.md](supported_components.md) for component types
and pin counts.

### Transformations

Pin positions automatically account for:
- **Position**: Component location on schematic (x, y)
- **Rotation**: 0°, 90°, 180°, 270°
- **Mirroring**: X-axis and Y-axis mirroring

### Testing

See [tests/unit/test_get_component_pins.py](tests/unit/test_get_component_pins.py)
for comprehensive examples.
```

## 7. Maintenance Phase

### Future Tests

When adding related features, add tests for:

```python
# Connecting pins with wires
def test_wire_to_pin(self):
    sch = ksa.create_schematic("Wire Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
    pin1 = r1.get_pin_position("1")
    wire = sch.wires.add(start=(50, 100), end=pin1)
    assert wire is not None

# Labeling pins
def test_label_at_pin(self):
    sch = ksa.create_schematic("Label Test")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
    pin1 = r1.get_pin_position("1")
    label = sch.add_label("VCC", position=pin1)
    assert label is not None

# Hierarchical connections
def test_hierarchical_pin_connection(self):
    parent = ksa.create_schematic("Parent")
    child = ksa.create_schematic("Child")
    # Connect parent sheet pins to child pins
    pass
```

### Regression Testing

Keep reference schematics to detect regressions:

```bash
# Commit reference schematics
git add tests/reference_kicad_projects/

# In future, if implementation changes:
pytest tests/reference_tests/ -v
# If failures occur, verify against latest KiCAD or fix implementation
```

## Complete Example: From Requirement to Implementation

```
Day 1: Design
  - Write requirement: "Get pin positions for pin connections"
  - Document expected values for resistor at various rotations
  - Create test plan: 4 phases, >95% coverage target

Day 2: Unit Testing
  - Copy unit test template
  - Write 8 unit tests for basic pin retrieval
  - Tests fail (API doesn't exist yet)
  - Implement basic `get_pin_position()` method
  - Tests pass! 60% coverage

Day 3: Parametrized Testing
  - Copy parametrized test template
  - Write 12 parametrized tests for rotations, components, positions
  - Add missing rotation logic
  - Tests pass! 80% coverage

Day 4: Integration Testing
  - Copy integration test template
  - Write 6 integration tests for workflows
  - Add save/load support
  - Tests pass! 90% coverage

Day 5: Reference Testing
  - Create reference KiCAD files manually
  - Copy reference test template
  - Write 4 reference tests against real KiCAD
  - Verify exact coordinate matching
  - Tests pass! 95% coverage

Day 6: Cleanup & Documentation
  - Commit all code and tests
  - Update documentation
  - Run full test suite one more time
  - Ready to merge!
```

## Summary

Using the test template library:

1. **Start with requirements** - Define what you're building
2. **Design tests first** - Use TDD approach
3. **Copy relevant templates** - Adapt to your feature
4. **Implement incrementally** - Make tests pass one by one
5. **Achieve >95% coverage** - Use all 6 template types
6. **Reference test** - Validate against KiCAD
7. **Commit and document** - Complete the feature

**Result:** Well-tested, documented, maintainable pin connection implementation.
