#!/usr/bin/env python3
"""Test: Create blank schematic matching reference."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Blank Schematic")
    sch.save("test_blank_schematic.kicad_sch")
    print("✅ Created blank schematic")

    import subprocess

    subprocess.run(["open", "test_blank_schematic.kicad_sch"])


if __name__ == "__main__":
    main()
