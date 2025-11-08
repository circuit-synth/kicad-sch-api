#!/bin/bash
# Clean up generated files from root directory
# Run this periodically to keep the repo clean

set -e

echo "🧹 Cleaning up generated files from root directory..."

# Remove generated schematic files
rm -f *.kicad_sch
rm -f ~*.kicad_sch.lck
rm -f *.kicad_prl
rm -f *.kicad_pro

# Remove generated test/demo scripts
rm -f test_circuit_*.py
rm -f demo_*.py
rm -f generate_*.py

# Remove generated PDFs
rm -f demo_*.pdf

echo "✅ Root directory cleaned!"
echo ""
echo "These files should be in examples/ or tests/ directories, not in root."
echo "Update examples to output to examples/ directory if needed."
