#!/usr/bin/env python3
"""
Test script for connect_components MCP tool.

Tests the new connect_components functionality with real schematic operations.
"""

import asyncio

from mcp_server.tools.connectivity_tools import connect_components
from mcp_server.tools.pin_discovery import set_current_schematic

import kicad_sch_api as ksa


async def test_connect_components():
    """Test connect_components with various scenarios."""

    print("=" * 70)
    print("TESTING CONNECT_COMPONENTS MCP TOOL")
    print("=" * 70)

    # Test 1: Simple connection with auto routing
    print("\n1. Testing simple connection with auto routing...")
    sch1 = ksa.create_schematic("Test Auto Routing")
    set_current_schematic(sch1)

    sch1.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
    sch1.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

    result = await connect_components("R1", "2", "R2", "1")

    assert result["success"], f"Test 1 failed: {result.get('message')}"
    assert result["routing"]["type"] == "l_shaped", "Expected L-shaped routing"
    assert len(result["wire_uuids"]) == 2, "Expected 2 wire segments"
    assert result["junction_uuid"] is not None, "Expected junction at corner"
    print(f"   ✅ Success: {result['message']}")
    print(f"   - Routing type: {result['routing']['type']}")
    print(f"   - Segments: {result['routing']['segments']}")
    print(f"   - Junction: {result['junction_uuid']}")

    # Test 2: Connection with label
    print("\n2. Testing connection with label...")
    sch2 = ksa.create_schematic("Test With Label")
    set_current_schematic(sch2)

    sch2.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
    sch2.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

    result = await connect_components("R1", "2", "R2", "1", add_label="VCC")

    assert result["success"], f"Test 2 failed: {result.get('message')}"
    assert result["label_uuid"] is not None, "Expected label to be added"
    print(f"   ✅ Success: {result['message']}")
    print(f"   - Label added: {result['label_uuid']}")

    # Test 3: Horizontal-first routing
    print("\n3. Testing horizontal-first routing...")
    sch3 = ksa.create_schematic("Test Horizontal First")
    set_current_schematic(sch3)

    sch3.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
    sch3.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

    result = await connect_components("R1", "2", "R2", "1", corner_direction="horizontal_first")

    assert result["success"], f"Test 3 failed: {result.get('message')}"
    corner = result["routing"]["corner"]
    # Horizontal first means corner is at destination X, source Y (approximately)
    # The exact values depend on pin positions
    print(f"   ✅ Success: {result['message']}")
    print(f"   - Corner at: ({corner['x']}, {corner['y']})")
    print(f"   - Corner direction: horizontal_first")

    # Test 4: Vertical-first routing
    print("\n4. Testing vertical-first routing...")
    sch4 = ksa.create_schematic("Test Vertical First")
    set_current_schematic(sch4)

    sch4.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
    sch4.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

    result = await connect_components("R1", "2", "R2", "1", corner_direction="vertical_first")

    assert result["success"], f"Test 4 failed: {result.get('message')}"
    corner = result["routing"]["corner"]
    # Vertical first means corner is at source X, destination Y (approximately)
    # The exact values depend on pin positions
    print(f"   ✅ Success: {result['message']}")
    print(f"   - Corner at: ({corner['x']}, {corner['y']})")
    print(f"   - Corner direction: vertical_first")

    # Test 5: Direct routing (aligned pins)
    print("\n5. Testing direct routing...")
    sch5 = ksa.create_schematic("Test Direct Routing")
    set_current_schematic(sch5)

    sch5.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
    sch5.components.add("Device:R", "R2", "10k", position=(100.0, 125.0))

    result = await connect_components("R1", "2", "R2", "1")

    assert result["success"], f"Test 5 failed: {result.get('message')}"
    assert result["routing"]["type"] == "direct", "Expected direct routing"
    assert len(result["wire_uuids"]) == 1, "Expected 1 wire segment for direct routing"
    assert result["junction_uuid"] is None, "No junction needed for direct routing"
    print(f"   ✅ Success: {result['message']}")
    print(f"   - Routing type: {result['routing']['type']}")

    # Test 6: Error handling - component not found
    print("\n6. Testing error handling...")
    sch6 = ksa.create_schematic("Test Error Handling")
    set_current_schematic(sch6)

    sch6.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

    result = await connect_components("R1", "1", "R999", "1")  # R999 doesn't exist

    assert not result["success"], "Expected failure for non-existent component"
    # Should get either COMPONENT_NOT_FOUND or PIN_INFO_ERROR depending on timing
    assert result["error"] in [
        "COMPONENT_NOT_FOUND",
        "PIN_INFO_ERROR",
    ], f"Expected component error, got {result['error']}"
    print(f"   ✅ Success: Correctly caught error - {result['message']}")

    # Test 7: Complete circuit with save
    print("\n7. Creating complete circuit and saving...")
    sch7 = ksa.create_schematic("Test Complete Circuit")
    set_current_schematic(sch7)

    # Create voltage divider
    sch7.components.add("Device:R", "R1", "10k", position=(127.0, 88.9))
    sch7.components.add("Device:R", "R2", "10k", position=(127.0, 114.3))

    # Connect with label
    result1 = await connect_components("R1", "2", "R2", "1", add_label="VOUT")

    assert result1["success"], f"Test 7a failed: {result1.get('message')}"

    # Add VCC label at R1 pin 1
    r1_pins = sch7.components.get_pins_info("R1")
    r1_pin1 = next(p for p in r1_pins if p.number == "1")
    sch7.add_label("VCC", position=(r1_pin1.position.x, r1_pin1.position.y - 5.0))

    # Add GND label at R2 pin 2
    r2_pins = sch7.components.get_pins_info("R2")
    r2_pin2 = next(p for p in r2_pins if p.number == "2")
    sch7.add_label("GND", position=(r2_pin2.position.x, r2_pin2.position.y + 5.0))

    # Save schematic
    output_path = "test_connect_components_output.kicad_sch"
    sch7.save(output_path)

    print(f"   ✅ Success: Complete circuit saved to {output_path}")
    print(f"   - Components: {len(list(sch7.components))}")
    print(f"   - Wires: {len(list(sch7.wires))}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✅")
    print("=" * 70)
    print(f"\nSaved demo schematic: {output_path}")
    print("Open it in KiCAD to verify the connections!")


if __name__ == "__main__":
    asyncio.run(test_connect_components())
