# Reference: TL072 Multi-Unit Component

## Purpose

Validates multi-unit component format with TL072 dual op-amp (3 units total).

## Contents

- **U1 unit 1** (First op-amp): pins 1, 2, 3 at (120.65, 66.04)
- **U1 unit 2** (Second op-amp): pins 5, 6, 7 at (120.65, 86.36)
- **U1 unit 3** (Power pins): pins 4, 8 at (120.65, 107.95)

## Critical Format Findings

### 1. Multiple Symbol Entries

Each unit is a **separate `(symbol ...)` S-expression**:

```scheme
(symbol
  (lib_id "Amplifier_Operational:TL072")
  (at 120.65 66.04 0)
  (unit 1)  # Unit number
  (uuid "9050e0cc-5163-4753-9f2c-3112dc03e1ef")  # Unique per unit
  (property "Reference" "U1" ...)  # SAME reference for all units
  ...
)

(symbol
  (lib_id "Amplifier_Operational:TL072")
  (at 120.65 86.36 0)
  (unit 2)  # Different unit
  (uuid "c446c56c-86a3-41ec-a8d3-33a6d8923f12")  # Different UUID
  (property "Reference" "U1" ...)  # SAME reference
  ...
)

(symbol
  (lib_id "Amplifier_Operational:TL072")
  (at 120.65 107.95 0)
  (unit 3)
  (uuid "3db2bdba-9311-493f-acf5-0183341f57e5")
  (property "Reference" "U1" ...)  # SAME reference
  ...
)
```

### 2. Reference Designator

- **All units share the same reference**: "U1"
- Reference is NOT "U1A", "U1B", "U1C" - that's just visual in KiCAD GUI
- Internal storage uses numeric unit field

### 3. Unit Numbering

- Unit numbers: 1, 2, 3 (not A, B, C)
- Unit field: `(unit N)` where N is integer

### 4. Pin Numbering

Each unit has its own set of physical pin numbers:

- **Unit 1**: pins 1, 2, 3 (output, -, +)
- **Unit 2**: pins 5, 6, 7 (output, -, +)
- **Unit 3**: pins 4, 8 (V-, V+)

Total: 8 pins across 3 units (standard DIP-8 package)

### 5. Pin UUIDs

Each unit has **unique pin UUIDs** even though pin numbers differ:

```scheme
# Unit 1
(pin "1" (uuid "7bfab8a0-ddab-4aa1-b126-585b899f5b91"))
(pin "2" (uuid "d8ed85cd-215c-44c2-a172-fbd5b9a9b090"))
(pin "3" (uuid "d47ea1f2-bd72-490a-b280-d25ce7966d90"))

# Unit 2 (different UUIDs, different pin numbers)
(pin "5" (uuid "66189153-87ee-4a5f-97a9-a6c55809cb7d"))
(pin "6" (uuid "0998d6d2-059c-470c-a168-8b8968f7cf76"))
(pin "7" (uuid "2c79ad4b-95c-4f2f-94f8-c7c613955451"))

# Unit 3
(pin "4" (uuid "8ff46536-93dc-4d27-a49f-419662385165"))
(pin "8" (uuid "45683979-fdd0-4d11-9ef3-1dfba0b95e9a"))
```

### 6. Instances Section

Each unit has an instances section with **same reference, different unit**:

```scheme
(instances
  (project "tl072_multiunit_working"
    (path "/330dc103-b920-4b4b-b3a6-ef91b549bc86"
      (reference "U1")    # Same for all units
      (unit 1))))         # Different unit number
```

### 7. Symbol UUIDs

Each unit has a **unique symbol UUID**:

- Unit 1: `9050e0cc-5163-4753-9f2c-3112dc03e1ef`
- Unit 2: `c446c56c-86a3-41ec-a8d3-33a6d8923f12`
- Unit 3: `3db2bdba-9311-493f-acf5-0183341f57e5`

## Implementation Requirements

To correctly add multi-unit components:

1. **Allow duplicate references** with different unit numbers
2. **Generate unique UUIDs** for each unit's symbol
3. **Generate unique pin UUIDs** for each unit's pins
4. **Set correct unit number** in `(unit N)` field
5. **Preserve same reference** across all units
6. **Set correct instances path** with reference + unit

## Used For

- Unit test: Validate multi-unit component addition
- Reference test: Verify format preservation
- Integration test: Verify multi-unit connectivity

## Created

- Date: 2025-01-08
- Issue: #107
- PRD: docs/prd/multi-unit-component-support-prd.md
- KiCAD Version: 9.0
