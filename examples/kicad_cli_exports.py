"""
Comprehensive example of KiCad CLI export functionality.

This example demonstrates all export capabilities:
- ERC (Electrical Rule Check)
- Netlist export (8 formats)
- BOM (Bill of Materials) export
- PDF documentation
- SVG graphics
- DXF for CAD

Works with local kicad-cli or automatically falls back to Docker!
"""

import kicad_sch_api as ksa
from pathlib import Path


def main():
    print("=" * 70)
    print("KiCad CLI Export Example")
    print("=" * 70)
    print()

    # Check what's available
    info = ksa.cli.get_executor_info()
    print("🔍 KiCad CLI Availability:")
    print(f"   Local: {'✅ ' + info.local_version if info.local_available else '❌'}")
    print(f"   Docker: {'✅' if info.docker_available else '❌'}")
    print(f"   Active mode: {info.active_mode}")
    print()

    # Create a simple example schematic
    print("📝 Creating example schematic...")
    sch = ksa.create_schematic("Export Demo")

    # Add some components
    r1 = sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
    r2 = sch.components.add("Device:R", reference="R2", value="10k", position=(150, 100))
    c1 = sch.components.add("Device:C", reference="C1", value="100nF", position=(125, 150))

    # Add wire connections
    sch.add_wire(start=(100, 110), end=(150, 110))

    # Add labels
    sch.add_label("VCC", position=(100, 90), label_type="global")
    sch.add_label("GND", position=(125, 160), label_type="global")

    # Save schematic
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    sch_path = output_dir / "export_demo.kicad_sch"
    sch.save(sch_path)
    print(f"✅ Schematic saved: {sch_path}")
    print()

    # ========================================================================
    # 1. RUN ERC (Electrical Rule Check)
    # ========================================================================
    print("🔍 Running ERC (Electrical Rule Check)...")
    try:
        erc_report = sch.run_erc(format="json")
        print(f"   Errors: {erc_report.error_count}")
        print(f"   Warnings: {erc_report.warning_count}")

        if erc_report.has_errors():
            print("   ⚠️  ERC Errors found:")
            for error in erc_report.get_errors():
                print(f"      - {error.description}")
        else:
            print("   ✅ No ERC errors")
    except Exception as e:
        print(f"   ⚠️  ERC skipped: {e}")
    print()

    # ========================================================================
    # 2. EXPORT NETLISTS (Multiple Formats)
    # ========================================================================
    print("📋 Exporting netlists...")

    # KiCad S-expression netlist (default)
    try:
        netlist = sch.export_netlist(format="kicadsexpr")
        print(f"   ✅ KiCad netlist: {netlist}")
    except Exception as e:
        print(f"   ⚠️  Netlist export failed: {e}")

    # SPICE netlist for simulation
    try:
        spice = sch.export_netlist(format="spice")
        print(f"   ✅ SPICE netlist: {spice}")
    except Exception as e:
        print(f"   ⚠️  SPICE export failed: {e}")

    print()

    # ========================================================================
    # 3. EXPORT BOM (Bill of Materials)
    # ========================================================================
    print("📦 Exporting BOM...")
    try:
        bom = sch.export_bom(
            fields=["Reference", "Value", "Footprint", "${QUANTITY}"],
            labels=["Refs", "Value", "Footprint", "Qty"],
            group_by=["Value"],
            exclude_dnp=True,
        )
        print(f"   ✅ BOM exported: {bom}")

        # Show BOM content
        if bom.exists():
            content = bom.read_text()
            print("   📄 BOM Preview:")
            for line in content.split("\n")[:5]:  # First 5 lines
                print(f"      {line}")
    except Exception as e:
        print(f"   ⚠️  BOM export failed: {e}")
    print()

    # ========================================================================
    # 4. EXPORT PDF DOCUMENTATION
    # ========================================================================
    print("📄 Exporting PDF documentation...")
    try:
        pdf = sch.export_pdf(
            theme="KiCad Classic",
            black_and_white=False,
        )
        print(f"   ✅ PDF exported: {pdf}")
    except Exception as e:
        print(f"   ⚠️  PDF export failed: {e}")
    print()

    # ========================================================================
    # 5. EXPORT SVG GRAPHICS
    # ========================================================================
    print("🎨 Exporting SVG graphics...")
    try:
        svgs = sch.export_svg()
        for svg in svgs:
            print(f"   ✅ SVG: {svg}")
    except Exception as e:
        print(f"   ⚠️  SVG export failed: {e}")
    print()

    # ========================================================================
    # 6. EXPORT DXF FOR CAD
    # ========================================================================
    print("📐 Exporting DXF for CAD...")
    try:
        dxfs = sch.export_dxf()
        for dxf in dxfs:
            print(f"   ✅ DXF: {dxf}")
    except Exception as e:
        print(f"   ⚠️  DXF export failed: {e}")
    print()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("✅ Export Demo Complete!")
    print("=" * 70)
    print()
    print("All exports saved to:", output_dir.absolute())
    print()
    print("💡 Tips:")
    print("   - Set KICAD_CLI_MODE=docker to force Docker mode")
    print("   - Set KICAD_CLI_MODE=local to force local mode")
    print("   - All exports use KiCad's official tools for accuracy")
    print()


if __name__ == "__main__":
    main()
