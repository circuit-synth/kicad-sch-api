# Electrical Rules Check (ERC) User Guide

Complete guide to using ERC validation in kicad-sch-api.

## What is ERC?

Electrical Rules Check (ERC) automatically validates your schematic for common electrical errors like:
- ✅ Output pins shorted together
- ✅ Power supply conflicts
- ✅ Dangling wires
- ✅ Duplicate component references
- ✅ Missing component values

## Quick Start

### Basic Usage

```python
import kicad_sch_api as ksa
from kicad_sch_api.validation import ElectricalRulesChecker

# Load your schematic
sch = ksa.load_schematic("my_circuit.kicad_sch")

# Run ERC
erc = ElectricalRulesChecker(sch)
result = erc.run_all_checks()

# Check results
if result.has_errors():
    print(f"Found {len(result.errors)} errors!")
    for error in result.errors:
        print(f"  - {error.message}")
else:
    print("No errors found!")

# Print summary
print(result.summary())  # "0 errors, 3 warnings"
```

### Understanding Results

The ERC returns an `ERCResult` object with three categories:

```python
# Errors - must be fixed
for error in result.errors:
    print(f"ERROR [{error.error_code}]: {error.message}")
    print(f"  Components: {', '.join(error.component_refs)}")

# Warnings - should be reviewed
for warning in result.warnings:
    print(f"WARNING [{warning.error_code}]: {warning.message}")

# Info - informational messages
for info in result.info:
    print(f"INFO: {info.message}")
```

## Common Errors

### E001: Pin Conflict

**Problem**: Two output pins connected together

```python
# Bad: Two outputs driving same net
sch = ksa.create_schematic("Test")
u1 = sch.components.add("Device:R", "U1", "1k", (100, 100))
u2 = sch.components.add("Device:R", "U2", "1k", (150, 100))
sch.add_wire_between_pins("U1", "2", "U2", "2")  # Both outputs!

# ERC will report: "Pin conflict: output (U1) connected to output (U2)"
```

**Solution**: Use a buffer or remove one output

### E004: Duplicate Reference

**Problem**: Same reference used twice

```python
# Bad: R1 used twice
r1a = sch.components.add("Device:R", "R1", "1k", (100, 100))
r1b = sch.components.add("Device:R", "R1", "2k", (150, 100))  # ERROR!

# ERC will report: "Duplicate reference designator: R1"
```

**Solution**: Rename one component

```python
r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
r2 = sch.components.add("Device:R", "R2", "2k", (150, 100))  # Fixed
```

### W002: Dangling Wire

**Problem**: Wire with only one connection

```python
# Wire goes nowhere
pin_pos = sch.get_component_pin_position("R1", "1")
sch.wires.add(start=pin_pos, end=(pin_pos.x + 20, pin_pos.y))  # WARNING

# ERC will report: "Wire has unconnected endpoint"
```

**Solution**: Connect wire or remove it

### W008: Missing Value

**Problem**: Component has no value

```python
# Bad: No value specified
r1 = sch.components.add("Device:R", "R1", "", (100, 100))

# ERC will report: "Component R1 has no value"
```

**Solution**: Add a value

```python
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
```

## Configuration

### Changing Severity Levels

Make specific warnings into errors (or vice versa):

```python
from kicad_sch_api.validation import ERCConfig

config = ERCConfig()

# Make missing values an error instead of warning
config.set_severity("missing_value", "error")

# Make unconnected inputs just info instead of warning
config.set_severity("unconnected_input", "info")

# Use custom config
erc = ElectricalRulesChecker(sch, config=config)
result = erc.run_all_checks()
```

### Suppressing Warnings

Suppress specific warnings you know are okay:

```python
config = ERCConfig()

# Suppress all W001 warnings globally
config.suppress_warning("W001")

# Suppress W002 only for component R1
config.suppress_warning("W002", component="R1")

erc = ElectricalRulesChecker(sch, config=config)
result = erc.run_all_checks()
```

### Custom Pin Conflict Rules

Override default pin conflict matrix:

```python
from kicad_sch_api.validation import PinConflictMatrix, PinSeverity

# Create custom matrix
matrix = PinConflictMatrix()

# Allow Output-to-Output (downgrade from ERROR to WARNING)
matrix.set_rule("output", "output", PinSeverity.WARNING)

# Use with validator
from kicad_sch_api.validation.validators import PinTypeValidator

pin_validator = PinTypeValidator(sch, pin_matrix=matrix)
violations = pin_validator.validate()
```

## Exporting Results

### JSON Export

```python
# Get results as JSON
json_output = result.to_json()
print(json_output)

# Save to file
with open("erc_report.json", "w") as f:
    f.write(json_output)
```

### Dictionary Export

```python
# Get as Python dict
data = result.to_dict()

# Access fields
print(f"Total checks: {data['total_checks']}")
print(f"Passed: {data['passed_checks']}")
print(f"Duration: {data['duration_ms']}ms")

for error in data['errors']:
    print(f"{error['error_code']}: {error['message']}")
```

### Text Report

```python
# Print detailed text report
print(f"ERC Results: {result.summary()}")
print(f"Checks: {result.passed_checks}/{result.total_checks} passed")
print(f"Duration: {result.duration_ms:.1f}ms")
print()

if result.errors:
    print("ERRORS:")
    for error in result.errors:
        print(f"  [{error.error_code}] {error.message}")
        if error.component_refs:
            print(f"    Components: {', '.join(error.component_refs)}")
        if error.suggested_fix:
            print(f"    Fix: {error.suggested_fix}")
        print()

if result.warnings:
    print("WARNINGS:")
    for warning in result.warnings:
        print(f"  [{warning.error_code}] {warning.message}")
        if warning.component_refs:
            print(f"    Components: {', '.join(warning.component_refs)}")
        print()
```

## Filtering Results

### By Severity

```python
# Get only errors
errors = result.filter_by_severity("error")

# Get only warnings
warnings = result.filter_by_severity("warning")
```

### By Component

```python
# Get all violations affecting R1
r1_violations = result.filter_by_component("R1")

for violation in r1_violations:
    print(f"{violation.severity}: {violation.message}")
```

## Running Specific Checks

Run only certain validation categories:

```python
erc = ElectricalRulesChecker(sch)

# Run only pin type checks
pin_violations = erc.run_check("pin_types")

# Run only connectivity checks
conn_violations = erc.run_check("connectivity")

# Run only component checks
comp_violations = erc.run_check("components")

# Run only power checks
power_violations = erc.run_check("power")
```

## Integration Examples

### CI/CD Pipeline

```python
#!/usr/bin/env python3
import sys
import kicad_sch_api as ksa
from kicad_sch_api.validation import ElectricalRulesChecker

def validate_schematic(filename):
    """Validate schematic for CI/CD."""
    sch = ksa.load_schematic(filename)
    erc = ElectricalRulesChecker(sch)
    result = erc.run_all_checks()

    # Print results
    print(result.summary())

    # Save JSON report
    with open("erc_report.json", "w") as f:
        f.write(result.to_json())

    # Exit with error if violations found
    if result.has_errors():
        print("ERC failed!")
        for error in result.errors:
            print(f"  ERROR: {error.message}")
        sys.exit(1)
    else:
        print("ERC passed!")
        sys.exit(0)

if __name__ == "__main__":
    validate_schematic(sys.argv[1])
```

### Batch Validation

```python
import glob
import kicad_sch_api as ksa
from kicad_sch_api.validation import ElectricalRulesChecker

# Validate all schematics in directory
for filename in glob.glob("schematics/*.kicad_sch"):
    print(f"Validating {filename}...")

    sch = ksa.load_schematic(filename)
    erc = ElectricalRulesChecker(sch)
    result = erc.run_all_checks()

    if result.has_errors():
        print(f"  ❌ {result.summary()}")
    else:
        print(f"  ✅ {result.summary()}")
```

### Pre-Save Validation

```python
def create_and_validate_circuit():
    """Create circuit with automatic validation."""
    sch = ksa.create_schematic("My Circuit")

    # Add components
    r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
    led = sch.components.add("Device:LED", "D1", "RED", (150, 100))

    # Connect
    sch.add_wire_between_pins("R1", "2", "D1", "1")

    # Validate before saving
    erc = ElectricalRulesChecker(sch)
    result = erc.run_all_checks()

    if result.has_errors():
        raise ValueError(f"ERC failed: {result.summary()}")

    # Save only if validation passes
    sch.save("my_circuit.kicad_sch")
    print("Circuit saved successfully!")
```

## Error Code Reference

### Errors (E-xxx)

| Code | Description | Severity |
|------|-------------|----------|
| E001 | Pin conflict (Output-Output) | ERROR |
| E002 | Power output conflict | ERROR |
| E003 | Output to power rail | ERROR |
| E004 | Duplicate reference | ERROR |
| E005 | Invalid reference format | ERROR |

### Warnings (W-xxx)

| Code | Description | Severity |
|------|-------------|----------|
| W001 | Unconnected input pin | WARNING |
| W002 | Dangling wire | WARNING |
| W003 | Undriven net | WARNING |
| W004 | Missing power flag | WARNING |
| W005 | Unspecified pin type | WARNING |
| W007 | Missing footprint | WARNING |
| W008 | Missing value | WARNING |

## Best Practices

### 1. Run ERC Early and Often

```python
# After each major change
erc = ElectricalRulesChecker(sch)
result = erc.run_all_checks()
assert not result.has_errors(), "Fix errors before continuing"
```

### 2. Use Custom Config for Your Standards

```python
# Create company/project config
company_config = ERCConfig()
company_config.set_severity("missing_footprint", "error")  # Stricter
company_config.set_severity("unconnected_input", "info")   # More relaxed

# Reuse across projects
erc = ElectricalRulesChecker(sch, config=company_config)
```

### 3. Document Suppressed Warnings

```python
# If you suppress a warning, document why
config = ERCConfig()

# R1 intentionally has no connection (test point)
config.suppress_warning("W001", component="R1")

# Document in code or schematic
```

### 4. Integrate with Version Control

```bash
# Add ERC check to git pre-commit hook
#!/bin/bash
python3 scripts/run_erc.py my_circuit.kicad_sch || exit 1
```

## Performance

ERC is designed to be fast:

- **Small schematics** (<50 components): <10ms
- **Medium schematics** (50-100 components): <100ms
- **Large schematics** (100-1000 components): <500ms

To check performance:

```python
result = erc.run_all_checks()
print(f"ERC completed in {result.duration_ms:.1f}ms")
```

## Troubleshooting

### "No violations found but I see errors"

Some checks require full net tracing (coming in future update):
- Advanced dangling wire detection
- Undriven net detection
- Complex power validation

### "Too many false positives"

Use configuration to tune sensitivity:

```python
config = ERCConfig()
config.suppress_warning("W001")  # Suppress unconnected inputs
config.set_severity("missing_value", "info")  # Downgrade to info
```

### "Custom components not validated"

Ensure your KiCAD symbol libraries are installed and accessible. ERC reads pin types from actual symbol definitions.

## Further Reading

- **[ERC_PRD.md](ERC_PRD.html)** - Product requirements (for developers)
- **[ERC_ERD.md](ERC_ERD.html)** - Entity relationship diagrams (for developers)
- **[API Reference](API_REFERENCE.html)** - Complete API documentation

## Questions?

- Check the [Recipes guide](RECIPES.html) for more examples
- See [Architecture docs](ARCHITECTURE.html) for system design
- File an issue on [GitHub](https://github.com/circuit-synth/kicad-sch-api/issues)

---

**Happy circuit validation! ⚡**
