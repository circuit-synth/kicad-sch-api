# Product Requirements Document: Electrical Rules Check (ERC)

**Feature**: Electrical Rules Check (ERC) Validation
**Issue**: #32
**Priority**: 🔴 HIGHEST
**Estimated Effort**: 6-8 hours
**Target Version**: 0.5.0

---

## Executive Summary

Implement comprehensive Electrical Rules Check (ERC) validation for KiCAD schematics, enabling automated detection of electrical design errors before manufacturing. This feature brings professional-grade circuit validation to kicad-sch-api, matching KiCAD's built-in ERC capabilities.

## Problem Statement

### Current State
- **No circuit validation available** - Users cannot verify schematic electrical correctness
- **Manual error detection only** - Designers must visually inspect for errors
- **Risk of manufacturing issues** - Electrical errors may reach production
- **No AI validation** - AI-generated circuits cannot be automatically validated

### User Pain Points
1. Cannot detect output-to-output shorts programmatically
2. No way to verify power supply connectivity
3. Missing wire detection requires manual inspection
4. Duplicate component references go unnoticed
5. Undriven nets are hard to identify

### Impact
- **Professional credibility** - Library cannot be used for production without validation
- **AI agent reliability** - AI-generated circuits cannot be trusted without ERC
- **User confidence** - Users hesitant to adopt without quality checks

## Goals & Success Metrics

### Primary Goals
1. ✅ Implement industry-standard ERC validation
2. ✅ Match KiCAD's ERC capabilities
3. ✅ Provide actionable error reports
4. ✅ Support customizable severity levels

### Success Metrics
- **Coverage**: Detect all major KiCAD ERC error types
- **Accuracy**: <1% false positives
- **Performance**: <100ms for 100-component schematics
- **Usability**: Clear, actionable error messages

## Requirements

### Functional Requirements

#### FR1: Pin Type Validation
**Must Support All KiCAD Pin Types**:
- Input (PT_INPUT)
- Output (PT_OUTPUT)
- Bidirectional (PT_BIDI)
- Tri-state (PT_TRISTATE)
- Passive (PT_PASSIVE)
- Not Internally Connected/Free (PT_NIC)
- Unspecified (PT_UNSPECIFIED)
- Power Input (PT_POWER_IN)
- Power Output (PT_POWER_OUT)
- Open Collector (PT_OPENCOLLECTOR)
- Open Emitter (PT_OPENEMITTER)
- Not Connected (PT_NC)

#### FR2: Pin Conflict Matrix
Implement ERC conflict matrix following KiCAD standards:

**Error Conditions** (must detect):
- Output ↔ Output (driving conflict)
- Power Output ↔ Power Output (power short)
- Output ↔ Power Output (logic/power conflict)

**Warning Conditions** (should warn):
- Unspecified ↔ Any pin type
- Input with no driver
- Tri-state ↔ Output

**OK Conditions** (explicitly allowed):
- Input ↔ Output
- Passive ↔ Any
- Bidirectional ↔ Any logic type
- Power Input ↔ Power Output

#### FR3: Connectivity Validation

**Must Detect**:
1. **Unconnected Required Pins**
   - Input pins without connections
   - Power input pins without power source

2. **Dangling Wires**
   - Wires with only one connection
   - Wires not connected to any pin

3. **Undriven Nets**
   - Nets with only input pins
   - Power nets without power output

4. **Multiple Drivers**
   - Multiple outputs on same net (conflict)
   - Multiple power outputs (short)

#### FR4: Component Validation

**Must Detect**:
1. **Duplicate References**
   - Same reference used multiple times (e.g., R1, R1)

2. **Invalid References**
   - Missing references
   - Malformed reference format

3. **Missing Properties**
   - Components without values
   - Missing footprints (warning)

#### FR5: Power Supply Validation

**Must Detect**:
1. **Power Flags**
   - Power input pins without PWR_FLAG or power output

2. **Power Continuity**
   - VCC/GND nets properly connected
   - Power supply presence

3. **Power Conflicts**
   - Multiple voltage sources on same net

#### FR6: Hierarchical Design Validation

**Must Detect**:
1. **Sheet Pin Mismatches**
   - Hierarchical labels without matching sheet pins
   - Type mismatches (input/output)

2. **Bus Consistency**
   - Bus alias consistency across hierarchy
   - Bus member consistency

#### FR7: Net Labeling Validation

**Must Detect**:
1. **Conflicting Labels**
   - Multiple different labels on same net

2. **Suspicious Patterns**
   - Very similar label names (e.g., VCC vs VCC1)
   - Common typos

### Non-Functional Requirements

#### NFR1: Performance
- **Target**: <100ms for typical schematics (<100 components)
- **Maximum**: <500ms for large schematics (<1000 components)
- **Scalability**: O(n) complexity where n = number of nets

#### NFR2: Usability
- **Clear Error Messages**: Include component references, net names, pin numbers
- **Severity Levels**: Error, Warning, Info
- **Actionable**: Suggest fixes where possible

#### NFR3: Configurability
- **Customizable Rules**: Users can adjust severity levels
- **Rule Suppression**: Ability to suppress specific warnings
- **Profile Support**: Different rule sets for different projects

#### NFR4: Compatibility
- **KiCAD 7/8 Compatible**: Match KiCAD ERC behavior
- **Standard Compliance**: Follow industry ERC standards

## User Stories

### US1: AI Agent Validation
**As an** AI agent generating circuits
**I want to** automatically validate electrical correctness
**So that** I can ensure generated circuits are safe to manufacture

**Acceptance Criteria**:
- ERC runs automatically after circuit generation
- Returns structured error report
- Errors include specific fix suggestions

### US2: Manual Design Validation
**As a** circuit designer using the library
**I want to** validate my schematic before saving
**So that** I catch errors before manufacturing

**Acceptance Criteria**:
- Simple API: `sch.run_erc()`
- Returns all errors and warnings
- Can configure severity levels

### US3: Batch Validation
**As a** design automation engineer
**I want to** validate hundreds of schematics
**So that** I can ensure design quality at scale

**Acceptance Criteria**:
- Fast performance (<100ms per schematic)
- Parallel execution support
- Summary reports

### US4: Custom Rule Configuration
**As an** experienced designer
**I want to** customize ERC rules
**So that** I can match my organization's standards

**Acceptance Criteria**:
- Configurable severity levels
- Rule suppression
- Custom rule definitions

## Technical Design

### Architecture

```
ElectricalRulesChecker
├── PinTypeValidator
│   ├── pin_conflict_matrix
│   └── validate_pin_connections()
├── ConnectivityValidator
│   ├── find_dangling_wires()
│   ├── find_undriven_nets()
│   └── find_unconnected_pins()
├── ComponentValidator
│   ├── find_duplicate_references()
│   └── validate_component_properties()
├── PowerValidator
│   ├── validate_power_flags()
│   └── check_power_continuity()
└── HierarchyValidator
    ├── validate_sheet_pins()
    └── validate_bus_aliases()
```

### API Design

```python
# Basic usage
from kicad_sch_api.validation import ElectricalRulesChecker

sch = ksa.load_schematic("circuit.kicad_sch")
erc = ElectricalRulesChecker(sch)

# Run all checks
results = erc.run_all_checks()

# Access results
for error in results.errors:
    print(f"ERROR: {error.message}")
    print(f"  Component: {error.component_ref}")
    print(f"  Location: {error.location}")

# Check specific categories
pin_conflicts = erc.check_pin_conflicts()
dangling_wires = erc.check_dangling_wires()
power_issues = erc.check_power_supply()

# Custom configuration
config = ERCConfig()
config.set_severity("unconnected_input", "warning")  # Downgrade to warning
config.suppress_warning("W001", component="R1")       # Suppress specific warning

erc = ElectricalRulesChecker(sch, config=config)
results = erc.run_all_checks()
```

### Data Models

```python
@dataclass
class ERCViolation:
    """Single ERC violation."""
    violation_type: str           # "pin_conflict", "dangling_wire", etc.
    severity: str                 # "error", "warning", "info"
    message: str                  # Human-readable description
    component_refs: List[str]     # Affected components
    net_name: Optional[str]       # Affected net
    pin_numbers: List[str]        # Affected pins
    location: Optional[Point]     # Schematic location
    suggested_fix: Optional[str]  # How to fix
    error_code: str              # e.g., "E001", "W042"

@dataclass
class ERCResult:
    """Complete ERC results."""
    errors: List[ERCViolation]
    warnings: List[ERCViolation]
    info: List[ERCViolation]
    total_checks: int
    passed_checks: int
    duration_ms: float

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        return f"{len(self.errors)} errors, {len(self.warnings)} warnings"
```

### Pin Conflict Matrix Implementation

```python
class PinConflictMatrix:
    """KiCAD-compatible pin conflict matrix."""

    # Severity levels
    OK = 0
    WARNING = 1
    ERROR = 2

    # Default matrix (matches KiCAD defaults)
    MATRIX = {
        # (pin_type_1, pin_type_2): severity
        ("output", "output"): ERROR,
        ("power_output", "power_output"): ERROR,
        ("output", "power_output"): ERROR,
        ("input", "output"): OK,
        ("passive", "*"): OK,  # Passive OK with everything
        ("unspecified", "*"): WARNING,
        # ... full matrix
    }

    def check_connection(self, pin1_type: str, pin2_type: str) -> int:
        """Check if connection is OK, warning, or error."""
        pass
```

## Validation Rules

### Error-Level Violations (E-xxx)

| Code | Violation | Description |
|------|-----------|-------------|
| E001 | Output to Output | Two or more output pins connected |
| E002 | Power Output Conflict | Multiple power outputs on same net |
| E003 | Output to Power Output | Logic output connected to power rail |
| E004 | Duplicate Reference | Same reference designator used twice |
| E005 | Unconnected NC Pin | Pin marked NC has connection |
| E006 | Multiple Net Labels | Different labels on same net |

### Warning-Level Violations (W-xxx)

| Code | Violation | Description |
|------|-----------|-------------|
| W001 | Unconnected Input | Input pin has no connection |
| W002 | Dangling Wire | Wire has only one endpoint |
| W003 | Undriven Net | Net has no output driver |
| W004 | Missing Power Flag | Power net without PWR_FLAG |
| W005 | Unspecified Pin Type | Pin with unspecified electrical type |
| W006 | Similar Labels | Labels with similar names on different nets |
| W007 | Missing Footprint | Component has no footprint assigned |
| W008 | Missing Value | Component has no value |

### Info-Level Violations (I-xxx)

| Code | Violation | Description |
|------|-----------|-------------|
| I001 | Single-Pin Net | Net has only one connection |
| I002 | Passive-Only Net | Net has only passive pins |

## Implementation Phases

### Phase 1: Core Infrastructure (2 hours)
- [ ] Create `ElectricalRulesChecker` class
- [ ] Implement `ERCViolation` and `ERCResult` dataclasses
- [ ] Create `ERCConfig` for configuration
- [ ] Basic test framework

### Phase 2: Pin Validation (2 hours)
- [ ] Implement `PinConflictMatrix`
- [ ] Implement `PinTypeValidator`
- [ ] Add all 12 KiCAD pin types
- [ ] Test pin-to-pin conflict detection

### Phase 3: Connectivity Validation (2 hours)
- [ ] Implement `ConnectivityValidator`
- [ ] Dangling wire detection
- [ ] Undriven net detection
- [ ] Unconnected pin detection

### Phase 4: Component & Power Validation (2 hours)
- [ ] Implement `ComponentValidator`
- [ ] Implement `PowerValidator`
- [ ] Duplicate reference detection
- [ ] Power flag validation

### Phase 5: Integration & Testing (2 hours)
- [ ] Comprehensive test suite
- [ ] Reference schematic validation
- [ ] Documentation
- [ ] Performance optimization

## Testing Strategy

### Unit Tests
- Pin conflict matrix (all combinations)
- Individual validators (each rule)
- Configuration system
- Error message generation

### Integration Tests
- Complete ERC run on sample schematics
- Known-good schematics (should pass)
- Known-bad schematics (should fail with expected errors)

### Reference Tests
- KiCAD-created schematics with deliberate errors
- Compare results with KiCAD's ERC output
- Ensure compatibility

### Performance Tests
- 10-component schematic: <10ms
- 100-component schematic: <100ms
- 1000-component schematic: <500ms

## Questions for Product Owner

### Scope Questions

1. **KiCAD Version Compatibility**
   - Should we match KiCAD 7, KiCAD 8, or both?
   - Are there version-specific ERC differences we need to handle?

2. **Customization Level**
   - How customizable should the pin conflict matrix be?
   - Should users be able to add custom validation rules?
   - Do we need rule profiles (strict, standard, relaxed)?

3. **Hierarchy Handling**
   - How deep should hierarchical validation go?
   - Should we validate across hierarchy boundaries?
   - Should sheet pin type mismatches be errors or warnings?

4. **Power Flag Handling**
   - Should missing PWR_FLAG be an error or warning?
   - Do we auto-detect power symbols (like GND, VCC)?
   - How to handle custom power symbols?

### Feature Priority

5. **Which validations are MUST-HAVE for v1?**
   - Pin conflicts (Output-Output)? ✅
   - Duplicate references? ✅
   - Dangling wires? ✅
   - Power validation? ✅
   - Hierarchical validation? ❓
   - Bus validation? ❓
   - Advanced routing checks? ❓

6. **Performance vs. Completeness**
   - Is <100ms for 100 components acceptable?
   - Should we optimize for speed or thoroughness?
   - Is incremental/cached validation needed?

### API Design

7. **Integration Points**
   - Should `Schematic.save()` automatically run ERC?
   - Should we raise exceptions on errors or just return results?
   - Do we need both programmatic and CLI interfaces?

8. **Error Reporting**
   - Text reports? JSON? HTML?
   - Should we generate visual annotations on schematic?
   - Integration with CI/CD systems?

### Compatibility

9. **Third-Party Tools**
   - Should output be compatible with KiCAD's ERC report format?
   - Need to support external ERC rule files?
   - Integration with other EDA tools?

10. **Future Extensibility**
    - Plugin system for custom rules?
    - AI-powered error detection?
    - Learning from user corrections?

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Detects all major pin conflicts (Output-Output, Power shorts)
- ✅ Finds duplicate references
- ✅ Identifies dangling wires
- ✅ Validates power connectivity
- ✅ Clear, actionable error messages
- ✅ <100ms for 100-component schematics
- ✅ Comprehensive test coverage (>90%)

### Full Release
- ✅ All KiCAD ERC checks implemented
- ✅ Configurable severity levels
- ✅ Hierarchical validation
- ✅ Bus validation
- ✅ Custom rule support
- ✅ Multiple output formats
- ✅ Performance benchmarks met

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| KiCAD ERC changes | High | Medium | Version detection, compatibility layer |
| Performance issues | Medium | Low | Caching, incremental validation |
| False positives | High | Medium | Extensive testing, user feedback |
| Complex hierarchy | Medium | Medium | Phased approach, start simple |
| Pin type confusion | High | Medium | Clear documentation, examples |

## Dependencies

### Internal
- Symbol library cache (for pin type lookup)
- Net connectivity analysis (for net tracing)
- Component collections (for reference checking)

### External
- None (pure Python implementation)

## Documentation Requirements

1. **User Guide**
   - How to run ERC
   - Understanding error messages
   - Configuration examples
   - Common fixes

2. **API Reference**
   - ElectricalRulesChecker class
   - ERCConfig options
   - ERCResult structure
   - All violation codes

3. **Developer Guide**
   - Architecture overview
   - Adding custom rules
   - Pin conflict matrix
   - Performance considerations

## Appendix

### KiCAD Pin Type Reference

Complete enumeration with ERC behavior:

| Type | Symbol | Must Connect | Can Drive | Notes |
|------|--------|--------------|-----------|-------|
| Input | I | Yes | No | Requires driver |
| Output | O | No | Yes | Can drive nets |
| Bidirectional | B | No | Yes | I/O port |
| Tri-state | T | No | Yes | Can be high-Z |
| Passive | P | Yes | No | Resistors, caps |
| Free/NIC | F | No | No | Not connected internally |
| Unspecified | U | No | No | Unknown, always warns |
| Power Input | W | Yes | No | VCC, GND |
| Power Output | w | No | Yes | Regulator output |
| Open Collector | C | No | Yes | Needs pull-up |
| Open Emitter | E | No | Yes | Needs pull-down |
| Not Connected | N | No | No | Must stay open |

---

**Document Version**: 1.0
**Last Updated**: 2024-10-26
**Author**: Claude Code
**Status**: Ready for Review
