# PRD: Reference Designator Fix - Simple Scope

## Problem
Generated schematic shows "R?" instead of "R1" in KiCAD.

## Goal
Make generated file match reference file exactly (except UUIDs/dates).

## Files to Compare
- **Generated**: `/Users/shanemattner/Desktop/kicad-sch-api/simple_circuit.kicad_sch`
- **Reference**: `/Users/shanemattner/Desktop/kicad-sch-api/python/tests/reference_tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch`

## Test Command
```bash
uv run single_resistor_test.py
```

## Tasks
1. Add logging to identify where generation differs from reference
2. Fix property name casing (datasheet → Datasheet, description → Description)
3. Fix positioning to match reference coordinates
4. Ensure exact format preservation

## Success Criteria
Generated file matches reference file structure exactly, component displays "R1" in KiCAD.