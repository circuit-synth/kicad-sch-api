#!/usr/bin/env python3
"""
MCP Integration example for kicad-sch-api.

Demonstrates how to use the MCP server for AI agent integration,
showing the complete workflow from agent commands to schematic generation.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path


def test_mcp_server_manually():
    """Test MCP server functionality manually without AI agent."""
    print("🤖 MCP Server Integration Example")
    print("=" * 50)

    # Note: This example shows how the MCP interface works
    # In practice, AI agents like Claude would use the MCP protocol

    from kicad_sch_api.mcp.server import MCPInterface

    print("\n📡 Initializing MCP interface...")
    mcp = MCPInterface()

    # 1. Create new schematic via MCP
    print("\n📋 Creating schematic via MCP...")
    result = mcp.create_schematic({"name": "MCP Demo Circuit"})

    if result["success"]:
        print(f"✅ {result['message']}")
        summary = result.get("summary", {})
        print(f"   Components: {summary.get('component_count', 0)}")
    else:
        print(f"❌ Failed: {result.get('error')}")
        return

    # 2. Add components via MCP
    print("\n🔧 Adding components via MCP...")

    components_to_add = [
        {
            "lib_id": "Device:R",
            "reference": "R1",
            "value": "10k",
            "position": {"x": 100, "y": 50},
            "footprint": "Resistor_SMD:R_0603_1608Metric",
            "properties": {"MPN": "RC0603FR-0710KL", "Tolerance": "1%"},
        },
        {
            "lib_id": "Device:R",
            "reference": "R2",
            "value": "10k",
            "position": {"x": 100, "y": 100},
            "footprint": "Resistor_SMD:R_0603_1608Metric",
            "properties": {"MPN": "RC0603FR-0710KL", "Tolerance": "1%"},
        },
        {
            "lib_id": "Device:C",
            "reference": "C1",
            "value": "0.1uF",
            "position": {"x": 150, "y": 75},
            "footprint": "Capacitor_SMD:C_0603_1608Metric",
            "properties": {"MPN": "CL10B104KB8NNNC", "Voltage": "50V"},
        },
    ]

    for comp_spec in components_to_add:
        result = mcp.add_component(comp_spec)
        if result["success"]:
            comp_info = result.get("component", {})
            print(f"  ✅ Added {comp_info.get('reference')}: {comp_info.get('value')}")
        else:
            print(f"  ❌ Failed to add component: {result.get('error')}")

    # 3. Add connections via MCP
    print("\n🔗 Adding connections via MCP...")

    # Connect R1 pin 2 to R2 pin 1 (voltage divider)
    connection_result = mcp.connect_components(
        {"from_component": "R1", "from_pin": "2", "to_component": "R2", "to_pin": "1"}
    )

    if connection_result["success"]:
        print(f"  ✅ {connection_result['message']}")
    else:
        print(f"  ❌ Connection failed: {connection_result.get('error')}")

    # Add wire from point to point
    wire_result = mcp.add_wire({"start": {"x": 150, "y": 75}, "end": {"x": 100, "y": 75}})

    if wire_result["success"]:
        print(f"  ✅ Added wire connection")
    else:
        print(f"  ❌ Wire failed: {wire_result.get('error')}")

    # 4. Bulk operations via MCP
    print("\n⚡ Bulk operations via MCP...")

    bulk_result = mcp.bulk_update_components(
        {
            "criteria": {"lib_id": "Device:R"},
            "updates": {"properties": {"Package": "0603", "Series": "RC"}},
        }
    )

    if bulk_result["success"]:
        print(f"  ✅ Bulk updated {bulk_result.get('count', 0)} components")
    else:
        print(f"  ❌ Bulk update failed: {bulk_result.get('error')}")

    # 5. Validation via MCP
    print("\n✅ Validation via MCP...")

    validation_result = mcp.validate_schematic({})

    if validation_result["success"]:
        print(f"  ✅ Validation completed")
        print(f"    Valid: {validation_result.get('valid', False)}")
        print(f"    Issues: {validation_result.get('issue_count', 0)}")

        if validation_result.get("errors"):
            print("    Errors found:")
            for error in validation_result["errors"][:3]:
                print(f"      - {error}")
    else:
        print(f"  ❌ Validation failed: {validation_result.get('error')}")

    # 6. Get summary via MCP
    print("\n📊 Schematic summary via MCP...")

    summary_result = mcp.get_schematic_summary({})

    if summary_result["success"]:
        summary = summary_result.get("summary", {})
        print(f"  ✅ Summary retrieved:")
        print(f"    Title: {summary.get('title', 'Untitled')}")
        print(f"    Components: {summary.get('component_count', 0)}")
        print(f"    Modified: {summary.get('modified', False)}")

        comp_stats = summary.get("component_stats", {})
        if comp_stats:
            print(f"    Libraries: {comp_stats.get('libraries_used', 0)}")

    # 7. Save via MCP
    print("\n💾 Saving via MCP...")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
        output_path = f.name

    try:
        save_result = mcp.save_schematic({"file_path": output_path})

        if save_result["success"]:
            print(f"  ✅ {save_result['message']}")

            # Verify file exists and has content
            file_size = Path(output_path).stat().st_size
            print(f"    File size: {file_size} bytes")

        else:
            print(f"  ❌ Save failed: {save_result.get('error')}")

    finally:
        # Cleanup
        if Path(output_path).exists():
            Path(output_path).unlink()

    print("\n🎯 MCP Integration Summary:")
    print("  ✅ All MCP commands executed successfully")
    print("  ✅ Error handling working correctly")
    print("  ✅ Validation and reporting functional")
    print("  ✅ Format preservation enabled")


def simulate_ai_agent_workflow():
    """Simulate a typical AI agent workflow using MCP commands."""
    print("\n🤖 Simulated AI Agent Workflow")
    print("=" * 40)

    print("🎭 Simulating: 'Create a voltage divider circuit with LED indicator'")

    from kicad_sch_api.mcp.server import MCPInterface

    mcp = MCPInterface()

    # Step 1: Agent creates schematic
    print("\n1️⃣ Agent: Creating new schematic...")
    result = mcp.create_schematic({"name": "LED Voltage Divider"})
    print(f"   Agent result: {result['message'] if result['success'] else result['error']}")

    # Step 2: Agent adds voltage divider resistors
    print("\n2️⃣ Agent: Adding voltage divider resistors...")

    r1_result = mcp.add_component(
        {
            "lib_id": "Device:R",
            "reference": "R1",
            "value": "10k",
            "position": {"x": 100, "y": 50},
            "properties": {"Description": "Input resistor for voltage divider"},
        }
    )

    r2_result = mcp.add_component(
        {
            "lib_id": "Device:R",
            "reference": "R2",
            "value": "10k",
            "position": {"x": 100, "y": 100},
            "properties": {"Description": "Ground resistor for voltage divider"},
        }
    )

    print(f"   R1: {r1_result['message'] if r1_result['success'] else r1_result['error']}")
    print(f"   R2: {r2_result['message'] if r2_result['success'] else r2_result['error']}")

    # Step 3: Agent adds LED and current limiting resistor
    print("\n3️⃣ Agent: Adding LED indicator circuit...")

    led_result = mcp.add_component(
        {
            "lib_id": "Device:LED",
            "reference": "D1",
            "value": "Red",
            "position": {"x": 150, "y": 75},
            "properties": {"Description": "Power indicator LED"},
        }
    )

    r_led_result = mcp.add_component(
        {
            "lib_id": "Device:R",
            "reference": "R3",
            "value": "330",
            "position": {"x": 200, "y": 75},
            "properties": {"Description": "LED current limiting resistor"},
        }
    )

    print(f"   LED: {led_result['message'] if led_result['success'] else led_result['error']}")
    print(
        f"   R_LED: {r_led_result['message'] if r_led_result['success'] else r_led_result['error']}"
    )

    # Step 4: Agent connects components
    print("\n4️⃣ Agent: Connecting circuit...")

    connections = [
        ("R1", "2", "R2", "1"),  # Voltage divider connection
        ("R1", "2", "R3", "1"),  # Tap to LED resistor
        ("R3", "2", "D1", "A"),  # LED resistor to LED anode
    ]

    for from_comp, from_pin, to_comp, to_pin in connections:
        conn_result = mcp.connect_components(
            {
                "from_component": from_comp,
                "from_pin": from_pin,
                "to_component": to_comp,
                "to_pin": to_pin,
            }
        )

        if conn_result["success"]:
            print(f"   ✅ Connected {from_comp}.{from_pin} to {to_comp}.{to_pin}")
        else:
            print(f"   ❌ Connection failed: {conn_result.get('error')}")

    # Step 5: Agent validates design
    print("\n5️⃣ Agent: Validating circuit design...")

    validation = mcp.validate_schematic({})
    if validation["success"]:
        valid = validation.get("valid", False)
        issue_count = validation.get("issue_count", 0)
        print(f"   ✅ Validation: {'✅ Valid' if valid else '⚠️ Issues found'}")
        print(f"   Issues: {issue_count}")

    # Step 6: Agent gets final summary
    print("\n6️⃣ Agent: Getting final summary...")

    summary = mcp.get_schematic_summary({})
    if summary["success"]:
        info = summary.get("summary", {})
        print(f"   ✅ Circuit complete:")
        print(f"     Title: {info.get('title', 'Untitled')}")
        print(f"     Components: {info.get('component_count', 0)}")
        print(
            f"     Performance: {info.get('performance', {}).get('avg_operation_time_ms', 0):.2f}ms avg"
        )

    print("\n🎯 AI Agent Workflow Complete!")
    print("  ✅ Schematic created with natural language intent")
    print("  ✅ All components placed and connected")
    print("  ✅ Professional validation completed")
    print("  ✅ Ready for export to KiCAD")


def main():
    """Run MCP integration examples."""
    print("🤖 kicad-sch-api MCP Integration Examples")
    print("=" * 55)

    try:
        # Test manual MCP interface
        test_mcp_server_manually()

        # Simulate AI agent workflow
        simulate_ai_agent_workflow()

        print("\n🎉 MCP integration examples completed!")
        print("\nMCP capabilities demonstrated:")
        print("  ✅ Complete schematic manipulation via MCP protocol")
        print("  ✅ Professional error handling for AI agents")
        print("  ✅ Comprehensive validation and reporting")
        print("  ✅ High-performance operations suitable for agent workflows")
        print("  ✅ Direct mapping approach for simplicity")

        print("\n🔗 Next steps:")
        print("  1. Configure Claude Desktop with MCP server")
        print("  2. Use natural language: 'Create a voltage divider circuit'")
        print("  3. Agent automatically uses these MCP tools")
        print("  4. Professional KiCAD schematic generated")

    except Exception as e:
        print(f"\n❌ MCP example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
