# BOM Property Management User Guide

Complete guide to managing Bill of Materials (BOM) properties in KiCad schematics using kicad-sch-api.

## Overview

The BOM property management tools help you maintain consistent component properties across your schematic designs. Use these tools to:

- **Audit** schematics for missing required properties (like PartNumber, Manufacturer)
- **Update** properties in bulk across multiple components
- **Transform** properties by copying or renaming them

## Installation

```bash
pip install kicad-sch-api
```

The BOM tools are included in the main kicad-sch-api package and accessible via:
- Python API: `kicad_sch_api.bom` module
- Command-line: `ksa-bom` command

## Quick Start

### Command-Line Usage

```bash
# Find components missing PartNumber
ksa-bom audit ~/my_designs --check PartNumber --output report.csv

# Set PartNumber for all 10k resistors (preview first)
ksa-bom update ~/my_designs \
  --match "value=10k,lib_id=Device:R" \
  --set "PartNumber=RC0805FR-0710KL" \
  --dry-run

# Copy MPN to PartNumber where PartNumber is empty
ksa-bom transform ~/my_designs \
  --copy "MPN->PartNumber" \
  --only-if-empty
```

### Python API Usage

```python
import kicad_sch_api as ksa
from kicad_sch_api.bom import BOMPropertyAuditor
from pathlib import Path

# Create auditor instance
auditor = BOMPropertyAuditor()

# Audit for missing properties
issues = auditor.audit_directory(
    Path("~/my_designs"),
    required_properties=["PartNumber", "Manufacturer"],
    recursive=True,
    exclude_dnp=True
)

# Generate CSV report
auditor.generate_csv_report(issues, Path("report.csv"))

# Bulk update properties
count = auditor.update_properties(
    Path("~/my_designs"),
    match_criteria={"value": "10k", "lib_id": "Device:R"},
    property_updates={"PartNumber": "RC0805FR-0710KL", "Manufacturer": "Yageo"},
    dry_run=False
)

print(f"Updated {count} components")
```

## Common Use Cases

### 1. Audit Legacy Schematics

Find all components missing required properties:

```bash
# Generate comprehensive audit report
ksa-bom audit ~/legacy_projects \
  --check "PartNumber,Manufacturer,Tolerance" \
  --output audit_report.csv \
  --exclude-dnp
```

The CSV report includes:
- Schematic path
- Component reference (R1, C2, etc.)
- Value
- Footprint
- Library ID
- Missing properties
- Additional properties (Tolerance, Manufacturer, MPN)

Open `audit_report.csv` in Excel to review and prioritize cleanup.

### 2. Standardize Resistor Part Numbers

Add part numbers to all resistors based on value:

```bash
# 10k resistors
ksa-bom update ~/designs \
  --match "value=10k,lib_id=Device:R,footprint=*0805*" \
  --set "PartNumber=RC0805FR-0710KL,Manufacturer=Yageo,Tolerance=1%" \
  --dry-run  # Preview first

# Remove --dry-run to apply changes
ksa-bom update ~/designs \
  --match "value=10k,lib_id=Device:R,footprint=*0805*" \
  --set "PartNumber=RC0805FR-0710KL,Manufacturer=Yageo,Tolerance=1%" \
  --yes
```

### 3. Migrate Property Names

Rename or copy properties across all components:

```bash
# Copy MPN to PartNumber (only where PartNumber is empty)
ksa-bom transform ~/designs \
  --copy "MPN->PartNumber" \
  --only-if-empty \
  --yes

# Copy ManufacturerPN to PartNumber (overwrite existing)
ksa-bom transform ~/designs \
  --copy "ManufacturerPN->PartNumber" \
  --yes
```

### 4. Add Tolerance to All Capacitors

```bash
# Add 10% tolerance to all ceramic capacitors
ksa-bom update ~/designs \
  --match "lib_id=Device:C,footprint=*0805*" \
  --set "Tolerance=10%" \
  --yes

# Add 20% tolerance to electrolytic capacitors
ksa-bom update ~/designs \
  --match "lib_id=Device:C_Polarized" \
  --set "Tolerance=20%" \
  --yes
```

### 5. Clean Up DNP Components

Exclude Do-Not-Populate components from audits:

```bash
# Only audit components that will be populated
ksa-bom audit ~/designs \
  --check PartNumber \
  --exclude-dnp \
  --output production_bom_audit.csv
```

## Pattern Matching

The BOM tools support flexible pattern matching:

### Exact Match
```bash
--match "value=10k"                    # Exact value
--match "reference=R1"                 # Exact reference
--match "lib_id=Device:R"              # Exact library ID
```

### Wildcard Match
```bash
--match "reference=R*"                 # All resistors (R1, R2, ...)
--match "footprint=*0805*"             # All 0805 footprints
--match "value=*nF"                    # All capacitors in nanofarads
```

### Multiple Criteria (AND Logic)
```bash
--match "value=10k,lib_id=Device:R"               # 10k resistors only
--match "value=10k,footprint=*0805*,Tolerance="   # 10k 0805 resistors missing tolerance
```

### Empty/Missing Properties
```bash
--match "PartNumber="                  # Components with no PartNumber
--match "Manufacturer=,Tolerance="     # Missing both Manufacturer AND Tolerance
```

## Command Reference

### Audit Command

Find components missing required properties.

```bash
ksa-bom audit <directory> [OPTIONS]
```

**Options:**
- `--check <properties>`: Comma-separated list of required properties
- `--output <file>`: Path to save CSV report
- `--exclude-dnp`: Exclude Do-Not-Populate components
- `--no-recursive`: Don't scan subdirectories

**Examples:**
```bash
# Basic audit
ksa-bom audit ~/designs --check PartNumber

# Multi-property audit with report
ksa-bom audit ~/designs \
  --check "PartNumber,Manufacturer,Tolerance" \
  --output full_audit.csv

# Production-only audit
ksa-bom audit ~/designs \
  --check PartNumber \
  --exclude-dnp \
  --output production_audit.csv
```

### Update Command

Bulk update properties on matching components.

```bash
ksa-bom update <directory> [OPTIONS]
```

**Options:**
- `--match <criteria>`: Match criteria (required)
- `--set <properties>`: Properties to set (required)
- `--dry-run`: Preview changes without modifying files
- `--yes`: Skip confirmation prompt
- `--exclude-dnp`: Exclude Do-Not-Populate components
- `--no-recursive`: Don't scan subdirectories

**Examples:**
```bash
# Preview update
ksa-bom update ~/designs \
  --match "value=10k" \
  --set "PartNumber=RC0805FR-0710KL" \
  --dry-run

# Apply update
ksa-bom update ~/designs \
  --match "value=10k,lib_id=Device:R" \
  --set "PartNumber=RC0805FR-0710KL,Manufacturer=Yageo" \
  --yes

# Update only components missing property
ksa-bom update ~/designs \
  --match "value=100nF,PartNumber=" \
  --set "PartNumber=GRM188R71C104KA01" \
  --yes
```

### Transform Command

Copy or rename properties across components.

```bash
ksa-bom transform <directory> [OPTIONS]
```

**Options:**
- `--copy <transformations>`: Property transformations (e.g., "MPN->PartNumber")
- `--only-if-empty`: Only copy to empty destination properties
- `--dry-run`: Preview changes without modifying files
- `--yes`: Skip confirmation prompt
- `--exclude-dnp`: Exclude Do-Not-Populate components
- `--no-recursive`: Don't scan subdirectories

**Examples:**
```bash
# Copy MPN to PartNumber (only where PartNumber is empty)
ksa-bom transform ~/designs \
  --copy "MPN->PartNumber" \
  --only-if-empty \
  --yes

# Copy and overwrite
ksa-bom transform ~/designs \
  --copy "ManufacturerPN->PartNumber" \
  --yes

# Preview transformation
ksa-bom transform ~/designs \
  --copy "OldField->NewField" \
  --dry-run
```

## Python API Reference

### BOMPropertyAuditor Class

Main class for BOM property management.

```python
from kicad_sch_api.bom import BOMPropertyAuditor
from pathlib import Path

auditor = BOMPropertyAuditor()
```

#### audit_directory()

Scan directory for schematics and audit all.

```python
issues = auditor.audit_directory(
    directory: Path,
    required_properties: List[str],
    recursive: bool = True,
    exclude_dnp: bool = False
) -> List[ComponentIssue]
```

**Parameters:**
- `directory`: Path to directory containing schematics
- `required_properties`: List of required property names
- `recursive`: Scan subdirectories (default: True)
- `exclude_dnp`: Skip DNP components (default: False)

**Returns:** List of ComponentIssue objects

**Example:**
```python
issues = auditor.audit_directory(
    Path("~/designs"),
    required_properties=["PartNumber", "Manufacturer"],
    recursive=True,
    exclude_dnp=True
)

print(f"Found {len(issues)} components with missing properties")
```

#### audit_schematic()

Audit a single schematic file.

```python
issues = auditor.audit_schematic(
    schematic_path: Path,
    required_properties: List[str],
    exclude_dnp: bool = False
) -> List[ComponentIssue]
```

#### generate_csv_report()

Generate CSV report from audit results.

```python
auditor.generate_csv_report(
    issues: List[ComponentIssue],
    output_path: Path
)
```

#### update_properties()

Bulk update properties on matching components.

```python
count = auditor.update_properties(
    directory: Path,
    match_criteria: Dict[str, str],
    property_updates: Dict[str, str],
    dry_run: bool = False,
    recursive: bool = True,
    exclude_dnp: bool = False
) -> int
```

**Parameters:**
- `directory`: Path to directory containing schematics
- `match_criteria`: Dict of field=pattern criteria (all must match)
- `property_updates`: Dict of property=value updates to apply
- `dry_run`: Preview only, don't modify files (default: False)
- `recursive`: Scan subdirectories (default: True)
- `exclude_dnp`: Skip DNP components (default: False)

**Returns:** Number of components updated

**Example:**
```python
count = auditor.update_properties(
    Path("~/designs"),
    match_criteria={"value": "10k", "lib_id": "Device:R"},
    property_updates={
        "PartNumber": "RC0805FR-0710KL",
        "Manufacturer": "Yageo",
        "Tolerance": "1%"
    },
    dry_run=False
)

print(f"Updated {count} components")
```

#### transform_properties()

Copy or rename properties.

```python
count = auditor.transform_properties(
    directory: Path,
    transformations: List[Tuple[str, str]],
    only_if_empty: bool = False,
    dry_run: bool = False,
    recursive: bool = True,
    exclude_dnp: bool = False
) -> int
```

**Parameters:**
- `directory`: Path to directory containing schematics
- `transformations`: List of (source_property, dest_property) tuples
- `only_if_empty`: Only copy to empty destination properties (default: False)
- `dry_run`: Preview only, don't modify files (default: False)
- `recursive`: Scan subdirectories (default: True)
- `exclude_dnp`: Skip DNP components (default: False)

**Returns:** Number of components transformed

**Example:**
```python
count = auditor.transform_properties(
    Path("~/designs"),
    transformations=[("MPN", "PartNumber")],
    only_if_empty=True,
    dry_run=False
)

print(f"Transformed {count} components")
```

### PropertyMatcher Class

Flexible pattern matching for component properties.

```python
from kicad_sch_api.bom import PropertyMatcher
```

#### parse_criteria()

Parse criteria string into dict.

```python
criteria = PropertyMatcher.parse_criteria("value=10k,footprint=*0805*")
# Returns: {"value": "10k", "footprint": "*0805*"}
```

#### matches()

Check if component matches all criteria.

```python
is_match = PropertyMatcher.matches(
    component,
    {"value": "10k", "footprint": "*0805*"}
)
```

## Best Practices

### 1. Always Preview First

Use `--dry-run` to preview changes before applying:

```bash
# Preview
ksa-bom update ~/designs --match "..." --set "..." --dry-run

# Apply after verifying
ksa-bom update ~/designs --match "..." --set "..." --yes
```

### 2. Version Control

Commit schematics before bulk operations:

```bash
git commit -am "Before BOM property updates"
ksa-bom update ~/designs --match "..." --set "..." --yes
git diff  # Review changes
git commit -am "Updated PartNumber properties"
```

### 3. Incremental Updates

Update properties incrementally, one property type at a time:

```bash
# Step 1: Add PartNumbers
ksa-bom update ~/designs --match "value=10k" --set "PartNumber=XXX" --yes

# Step 2: Add Manufacturers
ksa-bom update ~/designs --match "PartNumber=XXX" --set "Manufacturer=YYY" --yes

# Step 3: Add Tolerances
ksa-bom update ~/designs --match "PartNumber=XXX" --set "Tolerance=1%" --yes
```

### 4. Exclude DNP Components

For production BOM compliance, always exclude DNP:

```bash
ksa-bom audit ~/designs \
  --check PartNumber \
  --exclude-dnp \
  --output production_audit.csv
```

### 5. Use Specific Match Criteria

Be as specific as possible to avoid unintended changes:

```bash
# Too broad - might match unintended components
ksa-bom update ~/designs --match "value=10k" --set "..."

# Better - specific to resistors with footprint
ksa-bom update ~/designs \
  --match "value=10k,lib_id=Device:R,footprint=*0805*" \
  --set "..."
```

## Troubleshooting

### No Components Matched

If update/transform reports 0 components:

1. Verify match criteria with audit:
   ```bash
   ksa-bom audit ~/designs --check PartNumber --output debug.csv
   ```

2. Check CSV to see actual component values

3. Adjust match criteria based on actual values

### Properties Not Updating

1. Verify schematic files are writable
2. Check for file permission issues
3. Use `--dry-run` to see what would be updated
4. Verify match criteria is correct

### CSV Report Empty

1. Check that directory contains `.kicad_sch` files
2. Verify `--no-recursive` isn't preventing subdirectory scan
3. Check that required properties are actually missing

## Integration with Workflow

### Manufacturing BOM Export

```bash
# 1. Audit and fix missing properties
ksa-bom audit ~/design --check PartNumber --exclude-dnp --output audit.csv

# 2. Fix issues found in audit
ksa-bom update ~/design --match "..." --set "..." --yes

# 3. Verify compliance
ksa-bom audit ~/design --check PartNumber --exclude-dnp
```

### Property Standardization Pipeline

```python
from kicad_sch_api.bom import BOMPropertyAuditor
from pathlib import Path

def standardize_bom_properties(design_dir: Path):
    """Standardize BOM properties across all schematics."""
    auditor = BOMPropertyAuditor()

    # 1. Copy MPN to PartNumber where missing
    auditor.transform_properties(
        design_dir,
        transformations=[("MPN", "PartNumber")],
        only_if_empty=True
    )

    # 2. Add default tolerance to all resistors
    auditor.update_properties(
        design_dir,
        match_criteria={"lib_id": "Device:R", "Tolerance": ""},
        property_updates={"Tolerance": "1%"}
    )

    # 3. Generate final audit report
    issues = auditor.audit_directory(
        design_dir,
        required_properties=["PartNumber", "Manufacturer", "Tolerance"],
        exclude_dnp=True
    )

    auditor.generate_csv_report(issues, design_dir / "bom_audit_final.csv")

    return len(issues)

# Run standardization
remaining_issues = standardize_bom_properties(Path("~/my_design"))
print(f"{remaining_issues} components still need attention")
```

## See Also

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Getting Started](GETTING_STARTED.md) - Library basics
- [Recipes](RECIPES.md) - Code examples and patterns
