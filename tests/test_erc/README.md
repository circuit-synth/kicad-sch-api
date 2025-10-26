# ERC Test Suite

Comprehensive test suite for Electrical Rules Check (ERC) validation.

## Test Structure

### Test Files

1. **test_erc_data_models.py** - Data model tests
   - ERCViolation creation and serialization
   - ERCResult aggregation and filtering
   - ERCConfig configuration management

2. **test_pin_conflict_matrix.py** - Pin compatibility matrix tests
   - All 12 KiCAD pin types
   - Pin-to-pin conflict rules
   - Matrix symmetry and completeness
   - Custom rule overrides

3. **test_erc_validators.py** - Validator logic tests
   - PinTypeValidator (pin conflicts)
   - ConnectivityValidator (dangling wires, undriven nets)
   - ComponentValidator (duplicates, missing properties)
   - PowerValidator (power flags, power connectivity)
   - ElectricalRulesChecker (orchestration)

## Running Tests

```bash
# Run all ERC tests
uv run pytest tests/test_erc/ -v

# Run specific test file
uv run pytest tests/test_erc/test_erc_data_models.py -v

# Run specific test class
uv run pytest tests/test_erc/test_pin_conflict_matrix.py::TestPinConflictMatrix -v

# Run with coverage
uv run pytest tests/test_erc/ --cov=kicad_sch_api.validation -v
```

## Test Coverage Goals

- **Data Models**: 100% coverage (simple dataclasses)
- **Pin Matrix**: 100% coverage (critical logic)
- **Validators**: >90% coverage (core validation)
- **Integration**: >80% coverage (end-to-end)

## TDD Approach

These tests were written **before** implementation (Test-Driven Development):

1. ✅ Tests define expected behavior
2. ⏭️ Implement code to make tests pass
3. ⏭️ Refactor while keeping tests green
4. ⏭️ Add edge case tests as discovered

## Key Test Scenarios

### Pin Conflict Detection
- Output-to-Output (ERROR)
- Power Output shorts (ERROR)
- Output-to-Power Output (ERROR)
- Input-to-Output (OK)
- Passive-to-anything (OK)
- Unspecified warnings (WARNING)

### Connectivity Validation
- Dangling wires (one endpoint)
- Unconnected input pins
- Undriven nets (no output)
- Proper connections (no warnings)

### Component Validation
- Duplicate references (ERROR)
- Missing values (WARNING)
- Missing footprints (WARNING)
- Invalid reference format (ERROR)

### Power Validation
- Missing PWR_FLAG (WARNING)
- Power input without driver (WARNING)
- Multiple power outputs (ERROR)

## Performance Requirements

Tests include performance validation:
- 50 components: <100ms
- 100 components: <100ms (target from PRD)
- 1000 components: <500ms (target from PRD)

## Next Steps

1. Implement `kicad_sch_api/validation/` module
2. Run tests (they will fail initially - this is expected!)
3. Implement code to make tests pass
4. Iterate until all tests green
5. Add edge case tests as needed

## Test Status

Currently: **Tests written, implementation pending**

Run `uv run pytest tests/test_erc/ -v` to see current status.
