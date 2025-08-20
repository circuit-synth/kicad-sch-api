#!/usr/bin/env python3
"""Test: Single text box matching reference."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Single Text Box")

    # Add text box matching the reference
    sch.add_text_box(
        text="Text box goes here",
        position=(116.84, 71.12),
        size=(59.69, 35.56),
        rotation=0,
        font_size=1.27,
        margins=(0.9525, 0.9525, 0.9525, 0.9525),
        stroke_width=0,
        stroke_type="solid",
        fill_type="none",
        justify_horizontal="left",
        justify_vertical="top",
        exclude_from_sim=False,
    )

    sch.save("test_single_text_box.kicad_sch")
    print("✅ Created single text box")

    import subprocess

    subprocess.run(["open", "test_single_text_box.kicad_sch"])


if __name__ == "__main__":
    main()
