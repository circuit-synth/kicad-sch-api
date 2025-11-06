# Manual Test Schematics

This directory contains scripts for generating test schematics to validate the collection architecture.

## Usage

Generate test schematics for manual inspection:

```bash
python manual_tests/generate_test_schematics.py
```

This creates 6 test schematics:
- `test_1_basic_components.kicad_sch` - Basic component creation
- `test_2_labels.kicad_sch` - Label management
- `test_3_wires_and_junctions.kicad_sch` - Wire/junction connectivity
- `test_4_batch_mode.kicad_sch` - Batch mode performance (50 components)
- `test_5_complex_circuit.kicad_sch` - Complex circuit integration
- `test_6_filter_operations.kicad_sch` - Filter operations

Open the generated files in KiCad to verify proper rendering and component placement.

## Note

Generated `.kicad_sch` files are gitignored as they are temporary test artifacts.
