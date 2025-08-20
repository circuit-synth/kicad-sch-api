#!/usr/bin/env python3
"""Test: Single label matching reference."""

import kicad_sch_api as ksa


def main():
    # Create schematic and set exact UUID from reference
    sch = ksa.create_schematic("single_label")  # Use lowercase to avoid title_block
    sch._data["uuid"] = "53ff471c-9135-47b5-af2d-5e6bd6f09c50"

    # Add local label with exact UUID matching the reference
    sch.add_label(
        text="LABEL_1",
        position=(130.81, 73.66),
        rotation=0,
        size=1.27,
        uuid="4eb31e2e-679d-4257-b0f7-2b7d4ed9bc2a",
    )

    sch.save("test_single_label.kicad_sch")
    print("✅ Created single label")

    import subprocess

    subprocess.run(["open", "test_single_label.kicad_sch"])


if __name__ == "__main__":
    main()
