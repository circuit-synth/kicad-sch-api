#!/usr/bin/env python3
"""Test: Complete title block with date, revision, company, and comments."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("kicad-sch-api demo")

    # Set complete title block information matching the reference
    sch.set_title_block(
        title="kicad-sch-api demo",
        date="2025-08-17",
        rev="v0.0.1",
        company="Circuit-Synth",
        comments={1: "first comment", 2: "second comment", 3: "third comment"},
    )

    sch.save("test_sch_title.kicad_sch")
    print("✅ Created schematic with complete title block")

    import subprocess

    subprocess.run(["open", "test_sch_title.kicad_sch"])


if __name__ == "__main__":
    main()
