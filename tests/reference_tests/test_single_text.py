#!/usr/bin/env python3
"""Test: Single text matching reference."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Single Text")

    # Add text matching the reference
    sch.add_text(
        text="Text here", position=(127.254, 76.454), rotation=0, size=1.27, exclude_from_sim=False
    )

    sch.save("test_single_text.kicad_sch")
    print("✅ Created single text")

    import subprocess

    subprocess.run(["open", "test_single_text.kicad_sch"])


if __name__ == "__main__":
    main()
