#!/usr/bin/env python3
"""
Simple example demonstrating pin-to-pin wiring for voltage divider circuit.

This creates a basic voltage divider circuit using the new pin-to-pin wiring API.
"""

import kicad_sch_api as ksa

def main():
    """Create a simple voltage divider circuit with pin-to-pin wiring."""
    print("🔧 Creating Voltage Divider Circuit with Pin-to-Pin Wiring")
    print("=" * 60)
    
    # Create schematic
    sch = ksa.create_schematic("Voltage Divider")
    
    # Add components
    print("📦 Adding components...")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))  # Top resistor
    r2 = sch.components.add("Device:R", "R2", "10k", (100, 150))  # Bottom resistor
    print(f"   Added {r1.reference} ({r1.value}) at ({r1.position.x:.1f}, {r1.position.y:.1f})")  
    print(f"   Added {r2.reference} ({r2.value}) at ({r2.position.x:.1f}, {r2.position.y:.1f})")
    
    # Wire the voltage divider: R1 pin 2 (bottom) to R2 pin 1 (top)
    print("\n🔗 Wiring voltage divider...")
    divider_wire = sch.add_wire_between_pins("R1", "2", "R2", "1")
    if divider_wire:
        print(f"   ✅ Connected R1 pin 2 → R2 pin 1 (voltage divider connection)")
    else:
        print("   ❌ Failed to connect voltage divider")
    
    # Add input and output connections
    input_wire = sch.add_wire_to_pin((50, 100), "R1", "1")  # VIN to R1 top
    output_wire = sch.add_wire_to_pin((150, 125), "R1", "2")  # VOUT from divider tap
    gnd_wire = sch.add_wire_to_pin((50, 150), "R2", "2")  # GND to R2 bottom
    
    print(f"   ✅ Added input connection (VIN)")
    print(f"   ✅ Added output connection (VOUT)")  
    print(f"   ✅ Added ground connection (GND)")
    
    # Show circuit summary
    print(f"\n📊 Circuit Summary:")
    print(f"   Components: {len(sch.components)}")
    print(f"   Wires: {len(sch.wires)}")
    
    # Show all wire connections
    print(f"\n🔍 Wire connections:")
    for i, wire in enumerate(sch.wires, 1):
        start = wire.points[0]
        end = wire.points[1] 
        print(f"   Wire {i}: ({start.x:.1f}, {start.y:.1f}) → ({end.x:.1f}, {end.y:.1f})")
    
    # Save schematic
    output_file = "voltage_divider.kicad_sch"
    sch.save(output_file)
    print(f"\n💾 Saved to: {output_file}")
    
    print(f"\n✨ Voltage divider circuit complete!")
    print(f"   This circuit divides input voltage by 2 (assuming equal resistors)")
    print(f"   Pin-to-pin wiring ensures exact electrical connections")

if __name__ == "__main__":
    main()