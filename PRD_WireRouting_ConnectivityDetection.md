# PRD: Simplified Wire Routing and Connectivity Detection

## 1. Overview

This PRD outlines the development of basic wire routing and connectivity detection for the kicad-sch-api library. **Simplified scope**: Direct pin-to-pin routing and basic connectivity detection only.

## 2. Problem Statement

Currently, the kicad-sch-api library supports:
- Manual pin-to-pin wire connections (`add_wire_between_pins()`)
- Manual wire placement to specific coordinates
- Component placement at specific positions

**Missing capabilities:**
- Simple auto routing between 2 pins (ok to draw through other components)
- Detection when 2 pins are connected via wire routing

## 3. Product Goals

### Primary Goals (Simplified Scope)
- **Direct Pin-to-Pin Auto Routing**: Simple straight-line routing between two component pins
- **Pin Connectivity Detection**: Determine if two specific pins are electrically connected via wires

### Out of Scope
- ❌ Obstacle avoidance and intelligent pathfinding  
- ❌ Component placement algorithms
- ❌ Route optimization and crossing minimization
- ❌ Multi-strategy routing (Manhattan, smart routing)
- ❌ Professional layout generation
- ❌ Spatial queries and complex algorithms

## 4. Technical Implementation

### 4.1 Direct Pin-to-Pin Auto Routing

**Simple Implementation:**
```python
def auto_route_pins(self, comp1_ref: str, pin1_num: str, comp2_ref: str, pin2_num: str) -> Optional[str]:
    """Auto route between two pins with direct connection."""
    pin1_pos = self.get_component_pin_position(comp1_ref, pin1_num)
    pin2_pos = self.get_component_pin_position(comp2_ref, pin2_num)
    
    if not pin1_pos or not pin2_pos:
        return None
    
    # Simple direct routing - just connect the pins
    return self.add_wire(pin1_pos, pin2_pos)
```

**Features:**
- Straight-line wire between two pin positions
- No obstacle avoidance - ok to draw through other components
- Uses existing `add_wire()` and `get_component_pin_position()` methods

### 4.2 Pin Connectivity Detection

**Core Algorithm** (based on kicad-skip coordinate matching):
```python
def are_pins_connected(self, comp1_ref: str, pin1_num: str, comp2_ref: str, pin2_num: str) -> bool:
    """Detect if two pins are connected via wire routing."""
    pin1_pos = self.get_component_pin_position(comp1_ref, pin1_num)
    pin2_pos = self.get_component_pin_position(comp2_ref, pin2_num)
    
    # Check direct wire connections
    for wire in self.wires:
        wire_start = wire.points[0]
        wire_end = wire.points[-1]
        
        if connects_pins(wire_start, wire_end, pin1_pos, pin2_pos):
            return True
    
    # Check indirect connections through wire networks
    return trace_wire_network(self, pin1_pos, pin2_pos)
```

**Key Implementation Details:**
- **Exact coordinate matching** between pin positions and wire endpoints
- **Network tracing** for indirect connections through multiple wires
- **Recursive crawling** to follow connected wire segments

## 5. User Stories

### 5.1 Auto Routing Stories

**As a circuit designer, I want to:**
- Auto route a direct wire between two specific component pins with a single function call
- Have the system handle pin position lookup automatically 
- Get a simple straight-line connection without complex path planning

### 5.2 Connectivity Detection Stories

**As a schematic analyzer, I want to:**
- Check if two specific component pins are electrically connected via existing wires
- Detect both direct connections and indirect connections through wire networks
- Get a simple boolean answer without complex connectivity graphs

## 6. Implementation Status

### Completed Features ✅
- **Direct pin-to-pin auto routing** (`auto_route_pins()`)
- **Pin connectivity detection** (`are_pins_connected()`)  
- **Wire network tracing** with recursive crawling
- **Integration with existing pin positioning system**

### API Examples

```python
import kicad_sch_api as ksa

# Create schematic and add components
sch = ksa.create_schematic('Simple Circuit')
r1 = sch.components.add('Device:R', 'R1', '1k', (50, 50))
r2 = sch.components.add('Device:R', 'R2', '2k', (100, 50))

# Auto route between pins - simple direct connection
wire_uuid = sch.auto_route_pins('R1', '2', 'R2', '1')

# Check if pins are connected
connected = sch.are_pins_connected('R1', '2', 'R2', '1')  # Returns True
```

## 7. Success Metrics

### 7.1 Functional Requirements ✅
- **Auto routing success**: Single function call creates direct wire between any two pins
- **Connectivity detection accuracy**: Correctly identifies pin connections via coordinate matching  
- **API simplicity**: Clean, straightforward method signatures
- **Integration**: Works with existing pin positioning and wire management

### 7.2 Performance Requirements
- **Small circuit performance**: <100ms for circuits with <10 components
- **Connectivity analysis**: <500ms for typical connectivity checks  
- **Memory efficiency**: No significant memory overhead from simplified implementation

---

**Document Status**: Updated for Simplified Scope v2.0  
**Last Updated**: 2025-08-20  
**Author**: Claude Code Agent  
**Scope**: Direct pin-to-pin routing and connectivity detection only