#!/usr/bin/env python3
"""Test: Single hierarchical sheet matching reference."""

import kicad_sch_api as ksa


def main():
    # Create schematic and set exact UUID from reference
    sch = ksa.create_schematic("single_hierarchical_sheet")  # Use lowercase to avoid title_block
    sch._data["uuid"] = "bfabd21f-2733-4953-b034-506cb9fdf9ab"

    # Add hierarchical sheet with exact UUID matching the reference
    sheet_uuid = sch.add_sheet(
        name="subcircuit1",
        filename="subcircuit1.kicad_sch",
        position=(137.16, 69.85),
        size=(26.67, 34.29),
        stroke_width=0.1524,
        stroke_type="solid",
        project_name="single_hierarchical_sheet",
        page_number="2",
        uuid="0c5266be-4fa5-460f-9a2f-0ee59ba7fd90",
    )

    # Add sheet pins matching the reference with exact UUIDs
    # Sheet bounds: position=(137.16, 69.85), size=(26.67, 34.29)
    # Right edge: x=163.83, Bottom edge: y=104.14, Left edge: x=137.16, Top edge: y=69.85

    sch.add_sheet_pin(
        sheet_uuid=sheet_uuid,
        name="NET1",
        pin_type="input",
        edge="right",
        position_along_edge=7.62,  # 77.47 - 69.85 = 7.62
        uuid="adb66f51-2859-4ace-9abe-5e0b55f948be",
    )

    sch.add_sheet_pin(
        sheet_uuid=sheet_uuid,
        name="NET2",
        pin_type="input",
        edge="bottom",
        position_along_edge=15.24,  # 152.4 - 137.16 = 15.24
        uuid="0c836392-4429-40d9-91c2-d87405912244",
    )

    sch.add_sheet_pin(
        sheet_uuid=sheet_uuid,
        name="NET3",
        pin_type="input",
        edge="left",
        position_along_edge=15.24,  # 104.14 - 88.9 = 15.24
        uuid="c166d84a-1fa1-4e90-92b4-f8b6a553b2ad",
    )

    sch.add_sheet_pin(
        sheet_uuid=sheet_uuid,
        name="NET4",
        pin_type="input",
        edge="top",
        position_along_edge=12.7,  # 149.86 - 137.16 = 12.7
        uuid="fe1dfbfa-ad4a-4fc0-96a5-37056490ac1e",
    )

    sch.save("test_single_hierarchical_sheet.kicad_sch")

    # Create the referenced sub-schematic file so KiCAD can load it
    sub_sch = ksa.create_schematic("subcircuit1")
    sub_sch.save("subcircuit1.kicad_sch")

    print("✅ Created single hierarchical sheet with sub-schematic")

    import subprocess

    subprocess.run(["open", "test_single_hierarchical_sheet.kicad_sch"])


if __name__ == "__main__":
    main()
