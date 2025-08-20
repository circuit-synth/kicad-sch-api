#!/usr/bin/env python3
"""
Create a more complex circuit to showcase Manhattan routing capabilities.
Demonstrates routing in a dense component layout.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🏗️  Creating Complex Circuit Example...")
    
    # Create schematic
    sch = ksa.create_schematic("Complex Manhattan Routing")
    
    # Create a 3x3 grid of components (like a maze)
    components = {}
    positions = [
        # Row 1 (top)
        ("R1", Point(25.4, 76.2)),   ("R2", Point(50.8, 76.2)),   ("R3", Point(76.2, 76.2)),
        # Row 2 (middle) 
        ("R4", Point(25.4, 50.8)),   ("R5", Point(50.8, 50.8)),   ("R6", Point(76.2, 50.8)),
        # Row 3 (bottom)
        ("R7", Point(25.4, 25.4)),   ("R8", Point(50.8, 25.4)),   ("R9", Point(76.2, 25.4)),
    ]
    
    print(f"📍 Creating 3×3 component grid:")
    values = ["1k", "2k", "3k", "4k", "5k", "6k", "7k", "8k", "9k"]
    
    for i, (ref, pos) in enumerate(positions):
        comp = sch.components.add("Device:R", ref, values[i], pos)
        components[ref] = comp
        print(f"   {ref} ({values[i]}) at {pos}")
    
    # Add challenge: Connect corners through the maze
    print(f"\n🛣️  Routing through the component maze...")
    
    routes = [
        # Corner to corner routes (most challenging)
        ("R1", "1", "R9", "2", "Top-left to bottom-right"),
        ("R3", "1", "R7", "2", "Top-right to bottom-left"), 
        
        # Edge routes
        ("R1", "2", "R6", "1", "Top-left to middle-right"),
        ("R4", "1", "R8", "2", "Middle-left to bottom-center"),
        
        # Center connections
        ("R2", "2", "R5", "1", "Top-center to center"),
        ("R5", "2", "R8", "1", "Center to bottom-center"),
    ]
    
    successful_routes = 0
    for start_comp, start_pin, end_comp, end_pin, description in routes:
        print(f"\n🔧 {description}:")
        print(f"   Routing {start_comp}-pin{start_pin} → {end_comp}-pin{end_pin}")
        
        wire_uuid = sch.auto_route_pins(start_comp, start_pin, end_comp, end_pin,
                                      routing_mode="manhattan",
                                      clearance=1.27)  # Tight clearance
        
        if wire_uuid:
            print(f"   ✅ Success: {wire_uuid}")
            successful_routes += 1
            
            # Verify connectivity
            connected = sch.are_pins_connected(start_comp, start_pin, end_comp, end_pin)
            print(f"   🔍 Verified connected: {connected}")
        else:
            print(f"   ❌ Failed - could not find path")
    
    # Add component boundary visualization
    print(f"\n📦 Adding bounding box visualization...")
    from kicad_sch_api.core.component_bounds import get_component_bounding_box
    
    for ref, comp in components.items():
        bbox = get_component_bounding_box(comp, include_properties=False)
        
        # Add small corner markers
        sch.add_text(f"{ref[:2]}", Point(bbox.min_x-1, bbox.max_y+1), size=0.4)
        
    # Add routing statistics
    sch.add_text(f"Routes: {successful_routes}/{len(routes)}", Point(25.4, 15), size=1.2)
    sch.add_text("Manhattan routing through component maze", Point(25.4, 12), size=1.0)
    
    print(f"\n📊 Routing Results:")
    print(f"   Successful routes: {successful_routes}/{len(routes)}")
    print(f"   Success rate: {(successful_routes/len(routes)*100):.1f}%")
    
    # Save and open
    filename = "complex_manhattan_routing.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 Look for complex L-shaped paths navigating around components!")
    except Exception as e:
        print(f"⚠️  Could not auto-open KiCAD: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()