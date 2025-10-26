# Entity Relationship Diagram: Electrical Rules Check (ERC)

**Feature**: ERC Validation System
**Version**: 1.0
**Date**: 2024-10-26

---

## System Overview

The ERC system validates electrical connectivity and design rules in KiCAD schematics through interconnected validators and data models.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Schematic                                    │
│  - uuid: str                                                     │
│  - components: ComponentCollection                               │
│  - wires: WireCollection                                         │
│  - labels: LabelCollection                                       │
│  - nets: Dict[str, Net]                                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ 1:1
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ElectricalRulesChecker                              │
│  - schematic: Schematic                                          │
│  - config: ERCConfig                                             │
│  - validators: List[Validator]                                   │
│  + run_all_checks() -> ERCResult                                 │
│  + run_check(check_type: str) -> List[ERCViolation]              │
└────┬────────┬────────┬────────┬────────┬──────────────────────┘
     │        │        │        │        │
     │ 1:1    │ 1:1    │ 1:1    │ 1:1    │ 1:1
     │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌──────────┐
│ Pin  │ │Connect │ │Comp    │ │Power │ │Hierarchy │
│Type  │ │ivity   │ │onent   │ │Valid │ │Validator │
│Valid │ │Valid   │ │Valid   │ │ator  │ │          │
│ator  │ │ator    │ │ator    │ │      │ │          │
└──┬───┘ └────┬───┘ └────┬───┘ └──┬───┘ └────┬─────┘
   │          │          │        │          │
   │          │          │        │          │
   │ uses     │ creates  │creates │creates   │ creates
   │          │          │        │          │
   ▼          ▼          ▼        ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ERCViolation                                │
│  - violation_type: str                                           │
│  - severity: str ("error", "warning", "info")                    │
│  - message: str                                                  │
│  - component_refs: List[str]                                     │
│  - net_name: Optional[str]                                       │
│  - pin_numbers: List[str]                                        │
│  - location: Optional[Point]                                     │
│  - suggested_fix: Optional[str]                                  │
│  - error_code: str                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ N:1 collected by
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ERCResult                                  │
│  - errors: List[ERCViolation]                                    │
│  - warnings: List[ERCViolation]                                  │
│  - info: List[ERCViolation]                                      │
│  - total_checks: int                                             │
│  - passed_checks: int                                            │
│  - duration_ms: float                                            │
│  + has_errors() -> bool                                          │
│  + summary() -> str                                              │
│  + to_dict() -> Dict                                             │
│  + to_json() -> str                                              │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                       ERCConfig                                  │
│  - severity_overrides: Dict[str, str]                            │
│  - suppressed_warnings: Set[str]                                 │
│  - custom_rules: List[CustomRule]                                │
│  - pin_conflict_matrix: PinConflictMatrix                        │
│  + set_severity(rule: str, severity: str)                        │
│  + suppress_warning(code: str, component: str)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ 1:1 uses
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PinConflictMatrix                              │
│  - matrix: Dict[Tuple[str, str], int]                            │
│  + check_connection(pin1: str, pin2: str) -> int                 │
│  + set_rule(pin1: str, pin2: str, severity: int)                 │
│  + get_default_matrix() -> Dict                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Entity Descriptions

### Core Entities

#### 1. ElectricalRulesChecker
**Purpose**: Main orchestrator for all ERC validation

**Attributes**:
- `schematic: Schematic` - The schematic being validated
- `config: ERCConfig` - Configuration for validation rules
- `validators: List[Validator]` - All registered validators

**Methods**:
- `run_all_checks() -> ERCResult` - Execute all validators
- `run_check(check_type: str) -> List[ERCViolation]` - Run specific check
- `add_validator(validator: Validator)` - Register custom validator

**Relationships**:
- 1:1 with Schematic (validates one schematic)
- 1:1 with ERCConfig (uses one configuration)
- 1:N with Validators (has multiple validators)
- Creates ERCResult (output)

---

#### 2. ERCViolation
**Purpose**: Represents a single validation violation

**Attributes**:
- `violation_type: str` - Category (e.g., "pin_conflict", "dangling_wire")
- `severity: str` - "error", "warning", or "info"
- `message: str` - Human-readable description
- `component_refs: List[str]` - Affected component references
- `net_name: Optional[str]` - Affected net name
- `pin_numbers: List[str]` - Affected pin numbers
- `location: Optional[Point]` - Schematic coordinates
- `suggested_fix: Optional[str]` - Recommended fix
- `error_code: str` - Unique code (e.g., "E001", "W042")

**Relationships**:
- N:1 with ERCResult (many violations in one result)
- Created by Validators

---

#### 3. ERCResult
**Purpose**: Aggregates all validation results

**Attributes**:
- `errors: List[ERCViolation]` - Error-level violations
- `warnings: List[ERCViolation]` - Warning-level violations
- `info: List[ERCViolation]` - Info-level violations
- `total_checks: int` - Total validations performed
- `passed_checks: int` - Number of passed checks
- `duration_ms: float` - Execution time

**Methods**:
- `has_errors() -> bool` - Quick error check
- `summary() -> str` - Human-readable summary
- `to_dict() -> Dict` - JSON-serializable dict
- `to_json() -> str` - JSON string
- `filter_by_severity(severity: str) -> List[ERCViolation]`
- `filter_by_component(ref: str) -> List[ERCViolation]`

**Relationships**:
- 1:N with ERCViolation (contains many violations)
- Created by ElectricalRulesChecker

---

#### 4. ERCConfig
**Purpose**: Configuration for validation rules

**Attributes**:
- `severity_overrides: Dict[str, str]` - Custom severity levels
- `suppressed_warnings: Set[str]` - Suppressed warning codes
- `custom_rules: List[CustomRule]` - User-defined rules
- `pin_conflict_matrix: PinConflictMatrix` - Pin compatibility matrix

**Methods**:
- `set_severity(rule: str, severity: str)` - Override default severity
- `suppress_warning(code: str, component: str)` - Suppress specific warning
- `add_custom_rule(rule: CustomRule)` - Add user rule
- `load_profile(name: str)` - Load rule profile (strict/standard/relaxed)

**Relationships**:
- 1:1 with ElectricalRulesChecker (configures one checker)
- 1:1 with PinConflictMatrix (defines pin rules)

---

### Validator Entities

#### 5. PinTypeValidator
**Purpose**: Validates pin-to-pin connections

**Attributes**:
- `pin_matrix: PinConflictMatrix` - Pin compatibility rules
- `schematic: Schematic` - Schematic being validated

**Methods**:
- `validate_pin_connections() -> List[ERCViolation]`
- `check_net_pins(net_name: str) -> List[ERCViolation]`
- `get_pin_type(component_ref: str, pin_num: str) -> str`

**Key Validations**:
- Output-to-Output conflicts (ERROR)
- Power Output shorts (ERROR)
- Output-to-Power Output (ERROR)
- Unspecified pin warnings (WARNING)

**Relationships**:
- Uses PinConflictMatrix for rules
- Creates ERCViolation objects
- Accesses Schematic components and nets

---

#### 6. ConnectivityValidator
**Purpose**: Validates wire connectivity

**Attributes**:
- `schematic: Schematic`
- `min_connections: int` - Minimum connections for valid net

**Methods**:
- `find_dangling_wires() -> List[ERCViolation]`
- `find_undriven_nets() -> List[ERCViolation]`
- `find_unconnected_pins() -> List[ERCViolation]`
- `trace_net(start_point: Point) -> List[Point]`

**Key Validations**:
- Wires with only one endpoint (WARNING)
- Input pins without drivers (WARNING)
- Nets without output pins (WARNING)

**Relationships**:
- Accesses Schematic wires collection
- Accesses Schematic components collection
- Creates ERCViolation objects

---

#### 7. ComponentValidator
**Purpose**: Validates component properties

**Attributes**:
- `schematic: Schematic`
- `reference_pattern: Pattern` - Regex for valid references

**Methods**:
- `find_duplicate_references() -> List[ERCViolation]`
- `validate_component_properties() -> List[ERCViolation]`
- `check_reference_format(ref: str) -> bool`

**Key Validations**:
- Duplicate reference designators (ERROR)
- Missing values (WARNING)
- Missing footprints (WARNING)
- Invalid reference format (ERROR)

**Relationships**:
- Accesses Schematic components collection
- Creates ERCViolation objects

---

#### 8. PowerValidator
**Purpose**: Validates power supply connections

**Attributes**:
- `schematic: Schematic`
- `power_net_names: Set[str]` - Known power net names

**Methods**:
- `validate_power_flags() -> List[ERCViolation]`
- `check_power_continuity() -> List[ERCViolation]`
- `find_power_conflicts() -> List[ERCViolation]`
- `is_power_net(net_name: str) -> bool`

**Key Validations**:
- Power Input without driver (WARNING)
- Missing PWR_FLAG (WARNING)
- Multiple voltage sources (ERROR)
- Power net shorts (ERROR)

**Relationships**:
- Accesses Schematic nets
- Accesses Schematic components
- Creates ERCViolation objects

---

#### 9. HierarchyValidator
**Purpose**: Validates hierarchical schematic structure

**Attributes**:
- `schematic: Schematic`
- `child_schematics: List[Schematic]`

**Methods**:
- `validate_sheet_pins() -> List[ERCViolation]`
- `validate_bus_aliases() -> List[ERCViolation]`
- `check_hierarchical_labels() -> List[ERCViolation]`

**Key Validations**:
- Sheet pin mismatches (ERROR)
- Hierarchical label mismatches (ERROR)
- Bus alias inconsistency (ERROR)

**Relationships**:
- Accesses Schematic sheet instances
- May access child schematics
- Creates ERCViolation objects

---

### Supporting Entities

#### 10. PinConflictMatrix
**Purpose**: Defines pin type compatibility rules

**Attributes**:
- `matrix: Dict[Tuple[str, str], int]` - Pin type pair → severity

**Constants**:
- `OK = 0` - Connection allowed
- `WARNING = 1` - Connection warns
- `ERROR = 2` - Connection forbidden

**Methods**:
- `check_connection(pin1_type: str, pin2_type: str) -> int`
- `set_rule(pin1_type: str, pin2_type: str, severity: int)`
- `get_default_matrix() -> Dict` - KiCAD default matrix
- `load_from_file(path: str)` - Load custom matrix

**Default Matrix** (partial):
```python
{
    ("output", "output"): ERROR,
    ("power_output", "power_output"): ERROR,
    ("output", "power_output"): ERROR,
    ("input", "output"): OK,
    ("bidirectional", "output"): OK,
    ("passive", "*"): OK,  # Wildcard
    ("unspecified", "*"): WARNING,
}
```

**Relationships**:
- 1:1 with ERCConfig
- Used by PinTypeValidator

---

#### 11. Net
**Purpose**: Represents an electrical net (extended from existing)

**Additional Attributes for ERC**:
- `drivers: List[Tuple[str, str]]` - (component_ref, pin_num) driving net
- `loads: List[Tuple[str, str]]` - Input pins on net
- `power_flags: List[Point]` - PWR_FLAG locations
- `is_power_net: bool` - Detected as power net

**Methods**:
- `has_driver() -> bool` - Check if net is driven
- `driver_count() -> int` - Number of outputs
- `is_properly_powered() -> bool` - Power Input has Power Output

**Relationships**:
- N:1 with Schematic (many nets in one schematic)
- Referenced by ERCViolation

---

#### 12. CustomRule (Abstract)
**Purpose**: Base class for user-defined validation rules

**Attributes**:
- `rule_id: str` - Unique identifier
- `severity: str` - Default severity
- `description: str` - Human-readable description

**Methods**:
- `validate(schematic: Schematic) -> List[ERCViolation]` - Abstract
- `get_metadata() -> Dict` - Rule information

**Relationships**:
- N:1 with ERCConfig (multiple rules in config)
- Creates ERCViolation objects

---

## Data Flow Diagram

```
User Code
    │
    ├─> Create/Load Schematic
    │       │
    │       ▼
    │   Schematic Object
    │       │
    ├───────┴──> ElectricalRulesChecker(schematic, config)
    │                   │
    │                   ├─> Initialize Validators
    │                   │   ├─> PinTypeValidator
    │                   │   ├─> ConnectivityValidator
    │                   │   ├─> ComponentValidator
    │                   │   ├─> PowerValidator
    │                   │   └─> HierarchyValidator
    │                   │
    ▼                   ▼
run_all_checks()    Each Validator:
    │                   │
    │                   ├─> Access Schematic Data
    │                   ├─> Apply Validation Rules
    │                   ├─> Create ERCViolations
    │                   └─> Return Violations
    │                           │
    ▼                           │
Collect All Violations  ◄───────┘
    │
    ├─> Filter by Severity
    ├─> Apply Config Overrides
    ├─> Suppress Configured Warnings
    │
    ▼
Create ERCResult
    │
    ├─> errors: List[ERCViolation]
    ├─> warnings: List[ERCViolation]
    ├─> info: List[ERCViolation]
    ├─> Statistics
    │
    ▼
Return to User
    │
    └─> User processes results
        ├─> Print summary
        ├─> Fix errors
        └─> Re-run ERC
```

## Validation Flow Sequence

```
ElectricalRulesChecker.run_all_checks()
│
├─[1]─> PinTypeValidator.validate_pin_connections()
│       │
│       ├─> For each net in schematic:
│       │   ├─> Get all pins on net
│       │   ├─> Get pin types from symbol cache
│       │   ├─> Check each pin pair against matrix
│       │   └─> Create ERCViolation if conflict
│       │
│       └─> Return violations
│
├─[2]─> ConnectivityValidator.find_dangling_wires()
│       │
│       ├─> For each wire:
│       │   ├─> Count connections at endpoints
│       │   └─> Create violation if <2 connections
│       │
│       └─> Return violations
│
├─[3]─> ConnectivityValidator.find_undriven_nets()
│       │
│       ├─> For each net:
│       │   ├─> Check if any output pin on net
│       │   └─> Create violation if no driver
│       │
│       └─> Return violations
│
├─[4]─> ComponentValidator.find_duplicate_references()
│       │
│       ├─> Build reference → component map
│       ├─> Find duplicates
│       └─> Create violations for duplicates
│
├─[5]─> PowerValidator.validate_power_flags()
│       │
│       ├─> For each power net:
│       │   ├─> Check for Power Output or PWR_FLAG
│       │   └─> Create violation if missing
│       │
│       └─> Return violations
│
├─[6]─> HierarchyValidator.validate_sheet_pins()
│       │
│       ├─> For each hierarchical sheet:
│       │   ├─> Match pins to labels in child
│       │   └─> Create violation if mismatch
│       │
│       └─> Return violations
│
└─> Aggregate all violations into ERCResult
```

## Database Schema (if persisting results)

```sql
-- ERC Results Table
CREATE TABLE erc_results (
    id INTEGER PRIMARY KEY,
    schematic_uuid TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    total_checks INTEGER,
    passed_checks INTEGER,
    duration_ms REAL,
    has_errors BOOLEAN
);

-- ERC Violations Table
CREATE TABLE erc_violations (
    id INTEGER PRIMARY KEY,
    result_id INTEGER REFERENCES erc_results(id),
    violation_type TEXT NOT NULL,
    severity TEXT NOT NULL,  -- 'error', 'warning', 'info'
    error_code TEXT NOT NULL,
    message TEXT NOT NULL,
    net_name TEXT,
    location_x REAL,
    location_y REAL,
    suggested_fix TEXT
);

-- Component References in Violations
CREATE TABLE violation_components (
    id INTEGER PRIMARY KEY,
    violation_id INTEGER REFERENCES erc_violations(id),
    component_ref TEXT NOT NULL,
    pin_number TEXT
);

-- Suppressed Warnings
CREATE TABLE suppressed_warnings (
    id INTEGER PRIMARY KEY,
    schematic_uuid TEXT NOT NULL,
    error_code TEXT NOT NULL,
    component_ref TEXT,
    reason TEXT,
    suppressed_at DATETIME
);
```

## Extension Points

### Adding Custom Validators

```python
from kicad_sch_api.validation import BaseValidator, ERCViolation

class CustomSignalIntegrityValidator(BaseValidator):
    """Custom validator for signal integrity checks."""

    def validate(self, schematic: Schematic) -> List[ERCViolation]:
        violations = []

        # Custom logic
        for component in schematic.components:
            if self.has_signal_integrity_issue(component):
                violations.append(ERCViolation(
                    violation_type="signal_integrity",
                    severity="warning",
                    message="High-speed signal without termination",
                    component_refs=[component.reference],
                    error_code="C001"
                ))

        return violations

# Register with ERC
erc = ElectricalRulesChecker(sch)
erc.add_validator(CustomSignalIntegrityValidator())
```

### Custom Pin Conflict Matrix

```python
# Create custom matrix
custom_matrix = PinConflictMatrix()

# Set custom rule: Allow Output-to-Output (override default error)
custom_matrix.set_rule("output", "output", PinConflictMatrix.WARNING)

# Use in config
config = ERCConfig()
config.pin_conflict_matrix = custom_matrix

erc = ElectricalRulesChecker(sch, config=config)
```

---

## Summary

This ERD defines a comprehensive, extensible ERC validation system with:

- **5 Core Validators**: Pin Type, Connectivity, Component, Power, Hierarchy
- **3 Result Types**: ERCViolation, ERCResult, ERCConfig
- **Extensibility**: Custom rules, configurable matrix, validator plugins
- **Performance**: Optimized for O(n) complexity
- **Compatibility**: Matches KiCAD 7/8 ERC behavior

The system is designed to be:
- **Modular**: Each validator is independent
- **Configurable**: Users can customize all rules
- **Testable**: Clear interfaces for unit testing
- **Scalable**: Efficient for large schematics

---

**Document Version**: 1.0
**Last Updated**: 2024-10-26
**Status**: Ready for Implementation
