#!/usr/bin/env python3
"""Test: Single hierarchical label matching reference."""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import HierarchicalLabelShape


def main():
    sch = ksa.create_schematic("Single Label Hierarchical")

    # Add hierarchical label matching the reference
    sch.add_hierarchical_label(
        text="HIERARCHICAL_LABEL_1",
        position=(129.54, 91.44),
        shape=HierarchicalLabelShape.INPUT,
        rotation=0,
        size=1.27,
    )

    sch.save("test_single_label_hierarchical.kicad_sch")
    print("✅ Created single hierarchical label")

    import subprocess

    subprocess.run(["open", "test_single_label_hierarchical.kicad_sch"])


if __name__ == "__main__":
    main()
