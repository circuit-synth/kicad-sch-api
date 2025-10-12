#!/usr/bin/env python3
"""Test: Single wire matching reference."""

import kicad_sch_api as ksa


def main():
    # Create schematic and set exact UUID from reference
    sch = ksa.create_schematic("single_wire")  # Use lowercase to avoid title_block
    sch._data["uuid"] = "e78dd10a-1a27-412e-99e6-67f2df79f534"

    # Add wire with exact UUID matching the reference schematic
    sch.wires.add(
        start=(114.3, 63.5), end=(135.89, 63.5), uuid="9bcb926d-9258-48ec-be9b-1fd0d2e5d397"
    )

    sch.save("test_single_wire.kicad_sch")
    print("✅ Created single wire")

    import subprocess

    subprocess.run(["open", "test_single_wire.kicad_sch"])


if __name__ == "__main__":
    main()
