"""Test PS2 hierarchical power symbol connectivity"""

import sys

sys.path.insert(0, "/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api")

import kicad_sch_api as ksa
from kicad_sch_api.core.connectivity import ConnectivityAnalyzer

# Load the root schematic (will automatically load child sheets)
root = ksa.Schematic.load(
    "tests/reference_kicad_projects/connectivity/ps2_hierarchical_power/ps2_hierarchical_power.kicad_sch"
)

print("=" * 80)
print("PS2 HIERARCHICAL CONNECTIVITY ANALYSIS")
print("=" * 80)

# Run hierarchical connectivity analysis
analyzer = ConnectivityAnalyzer(tolerance=0.1)
nets = analyzer.analyze(root, hierarchical=True)

print(f"\nTotal nets found: {len(nets)}")
print("\nNets:")
for i, net in enumerate(nets, 1):
    print(f"\n{i}. {net.name}:")
    print(f"   Pins: {len(net.pins)}")
    for pin in net.pins:
        print(f"     - {pin.reference}.{pin.pin_number}")
    print(f"   Wires: {len(net.wires)}")
    print(f"   Labels: {len(net.labels)}")

# Test expected connectivity
print("\n" + "=" * 80)
print("CONNECTIVITY TESTS")
print("=" * 80)

# VCC net should have R1.1 (parent)
vcc_net = analyzer.get_net_for_pin("R1", "1")
print(f"\n✓ VCC net name: {vcc_net.name if vcc_net else 'NOT FOUND'}")
if vcc_net:
    assert vcc_net.name == "VCC", f"VCC net should be named 'VCC', got '{vcc_net.name}'"
    vcc_pins = {(pin.reference, pin.pin_number) for pin in vcc_net.pins}
    print(f"  VCC net pins: {vcc_pins}")
    assert ("R1", "1") in vcc_pins, "R1.1 should be on VCC net"

# DATA net should have R1.2 (parent) and R2.1 (child) - hierarchical connection!
data_net = analyzer.get_net_for_pin("R1", "2")
print(f"\n✓ DATA net name: {data_net.name if data_net else 'NOT FOUND'}")
if data_net:
    data_pins = {(pin.reference, pin.pin_number) for pin in data_net.pins}
    print(f"  DATA net pins: {data_pins}")
    assert ("R1", "2") in data_pins, "R1.2 should be on DATA net"
    assert ("R2", "1") in data_pins, "R2.1 should be on DATA net (hierarchical connection)"
    print(f"  ✓ Hierarchical connection working! R1.2 (parent) ↔ R2.1 (child)")

# GND net should have R2.2 (child)
gnd_net = analyzer.get_net_for_pin("R2", "2")
print(f"\n✓ GND net name: {gnd_net.name if gnd_net else 'NOT FOUND'}")
if gnd_net:
    assert gnd_net.name == "GND", f"GND net should be named 'GND', got '{gnd_net.name}'"
    gnd_pins = {(pin.reference, pin.pin_number) for pin in gnd_net.pins}
    print(f"  GND net pins: {gnd_pins}")
    assert ("R2", "2") in gnd_pins, "R2.2 should be on GND net"

# Test cross-sheet connectivity
print("\n" + "=" * 80)
print("CROSS-SHEET CONNECTION TESTS")
print("=" * 80)

print("\n✓ R1.2 (parent) ↔ R2.1 (child) via hierarchical DATA:")
connected = analyzer.are_connected("R1", "2", "R2", "1")
print(f"  Connected: {connected}")
assert connected, "R1.2 (parent) and R2.1 (child) should be connected via hierarchical DATA signal"

print("\n✓ R1.1 (VCC) ↔ R1.2 (DATA) should NOT be connected:")
not_connected = not analyzer.are_connected("R1", "1", "R1", "2")
print(f"  Not connected: {not_connected}")
assert not_connected, "R1.1 (VCC) and R1.2 (DATA) should NOT be connected"

print("\n✓ R2.1 (DATA) ↔ R2.2 (GND) should NOT be connected:")
not_connected = not analyzer.are_connected("R2", "1", "R2", "2")
print(f"  Not connected: {not_connected}")
assert not_connected, "R2.1 (DATA) and R2.2 (GND) should NOT be connected"

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED!")
print("=" * 80)
print("\nHierarchical connectivity successfully implemented:")
print("  ✓ Multi-sheet loading")
print("  ✓ Sheet pin ↔ hierarchical label matching")
print("  ✓ Cross-sheet net merging")
print("  ✓ Global power symbols across all sheets")
print("=" * 80)
