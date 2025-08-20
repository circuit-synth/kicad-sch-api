# Product Requirements Document: Manhattan Routing with Obstacle Avoidance

## Executive Summary

This PRD defines the requirements for implementing Manhattan-style wire routing with obstacle avoidance capabilities in the kicad-sch-api library. This builds upon the existing direct wire routing functionality to provide intelligent routing around component obstacles, filling a significant gap in the KiCAD schematic automation ecosystem.

## Market Research & Context

### Current State of Schematic Auto-Routing

**Research Summary:**
1. **PCB vs Schematic Routing**: Most EDA auto-routing research and tooling focuses on PCB layout, not schematic capture
2. **KiCAD Limitations**: KiCAD's Eeschema has no native automatic wire routing for schematics - only manual wire placement with grid snapping
3. **Industry Gap**: Major EDA tools (Altium, Eagle, KiCAD) lack sophisticated schematic auto-routing compared to their PCB routing capabilities
4. **Academic Foundation**: Manhattan routing is well-established in EDA research, constrained to horizontal/vertical paths for manufacturability

### Key Findings from Research

**Algorithmic Complexity:**
- Even simple routing problems (Steiner tree) are NP-complete
- Modern EDA tools rely on heuristics rather than optimal solutions
- Grid-based approaches are fundamental for constraint satisfaction

**Manhattan Grid Constraints:**
- Based on orthogonal routing (horizontal and vertical only)
- Standard KiCAD grid: 1.27mm (50 mil) for electrical connections
- Critical for maintaining design rule compliance and readability

**Auto-Routing Approaches:**
- **Global Routing**: Coarse-grain path planning around obstacles
- **Detailed Routing**: Fine-grain wire placement on grid
- **Interactive Routing**: Human-guided path with automated refinement
- **Rip-up and Reroute**: Iterative improvement through path modification

## Product Vision

**Enable intelligent schematic wire routing that matches the quality of manual engineering while dramatically reducing design time.**

Create a professional-grade Manhattan routing system that:
- Automatically routes around component obstacles
- Maintains perfect KiCAD grid alignment for electrical connectivity
- Provides multiple routing strategies (shortest path, clearance optimization, aesthetic quality)
- Integrates seamlessly with existing direct routing capabilities

## User Stories & Use Cases

### Primary User Persona: Circuit Design Engineers
Engineers using kicad-sch-api for automated schematic generation who need reliable wire routing in complex layouts.

**User Stories:**

1. **As a circuit designer**, I want to automatically route wires between distant components so that I don't have to manually calculate paths around obstacles.

2. **As an automation engineer**, I want the routing algorithm to respect component boundaries so that wires don't visually overlap with component symbols.

3. **As a schematic reviewer**, I want auto-routed wires to follow clean Manhattan paths so that the schematic remains readable and professional.

4. **As a KiCAD user**, I want routed wires to maintain perfect grid alignment so that electrical connectivity works correctly in KiCAD.

5. **As a design tool developer**, I want configurable routing strategies so that I can optimize for different scenarios (density vs aesthetics vs speed).

### Use Cases

**UC1: Dense Component Layout Routing**
- Context: Multiple components placed close together
- Goal: Route connections without wires passing through component bodies
- Success: Clean routing with appropriate clearance margins

**UC2: Long-Distance Connection Routing** 
- Context: Components far apart with obstacles in between
- Goal: Find efficient path with minimal wire length and turns
- Success: Reasonable path length with clean Manhattan geometry

**UC3: Multi-Net Routing**
- Context: Multiple wire networks need routing simultaneously  
- Goal: Route all connections without interference
- Success: All nets routed with no design rule violations

**UC4: Hierarchical Design Integration**
- Context: Routing within hierarchical sheets with port connections
- Goal: Integrate with existing label-based connectivity
- Success: Proper routing to hierarchical labels and ports

## Technical Requirements

### Functional Requirements

**FR1: Manhattan Grid Compliance**
- All wire segments must be horizontal or vertical
- All wire endpoints and junctions must snap to 1.27mm KiCAD grid
- Wire paths must maintain electrical connectivity standards

**FR2: Component Obstacle Avoidance**
- Calculate accurate bounding boxes for all component symbols
- Route paths that maintain configurable clearance from components
- Handle component rotation and different symbol types

**FR3: Multi-Strategy Routing**
- **Shortest Path**: Minimize total wire length
- **Clearance Optimized**: Maximize distance from obstacles  
- **Aesthetic**: Prioritize clean appearance and minimal turns
- **Performance**: Fast routing for large schematics

**FR4: Path Quality Optimization**
- Minimize number of wire segments and direction changes
- Prefer routing along standard directions (horizontal first, then vertical)
- Avoid unnecessary detours while maintaining obstacle clearance

**FR5: Integration with Existing API**
- Extend current `auto_route_pins()` method with routing strategy parameter
- Maintain backward compatibility with direct routing
- Integrate with existing connectivity detection system

### Non-Functional Requirements

**NFR1: Performance**
- Route simple two-component connections in <100ms
- Handle schematics with 100+ components efficiently
- Scalable algorithm complexity for large designs

**NFR2: Reliability**
- 99%+ success rate for routeable connections
- Graceful degradation to direct routing when paths are blocked
- Robust handling of edge cases and invalid inputs

**NFR3: Configurability** 
- Adjustable clearance margins (default: 1.27mm)
- Selectable routing strategies per connection
- Configurable optimization parameters

**NFR4: Quality**
- Generated routes must pass KiCAD design rule checks
- Maintain exact format preservation for output files
- Professional visual quality matching manual routing

## Technical Architecture

### Core Components

**1. Enhanced Bounding Box System** ✅ (Complete)
- Accurate component bounds calculation using circuit-synth algorithms
- Support for different component types and orientations
- World coordinate transformation for placed components

**2. Manhattan Routing Engine**
- Grid-based pathfinding using A* or Dijkstra's algorithm
- Obstacle map generation from component bounding boxes
- Multiple routing strategies with cost function optimization

**3. Path Post-Processing**
- Wire segment optimization and cleanup
- Turn minimization and aesthetic improvements
- Grid alignment verification and correction

**4. Integration Layer**
- Extension of existing `Schematic.auto_route_pins()` API
- Strategy selection and parameter configuration
- Fallback to direct routing for unroutable paths

### Algorithm Design

**High-Level Approach:**
1. **Preprocessing**: Build obstacle map from component bounding boxes
2. **Global Routing**: Find coarse path using grid-based search
3. **Detailed Routing**: Refine path to exact wire segments
4. **Post-Processing**: Optimize for aesthetics and minimize turns

**Routing Strategy Options:**
- `RoutingStrategy.SHORTEST`: Minimize Manhattan distance
- `RoutingStrategy.CLEARANCE`: Maximize obstacle clearance
- `RoutingStrategy.AESTHETIC`: Balance distance, turns, and clearance
- `RoutingStrategy.DIRECT`: Fallback to existing direct routing

### Data Structures

**Grid Representation:**
```python
class RoutingGrid:
    grid_size: float = 1.27  # KiCAD standard grid
    obstacles: Set[GridPoint]
    boundaries: BoundingBox
    
class PathNode:
    position: GridPoint
    cost: float
    parent: Optional[PathNode]
    strategy_bonus: float
```

## Implementation Plan

### Phase 1: Core Routing Engine (Current Sprint)
- [x] Research and PRD development
- [x] Enhanced bounding box system implementation  
- [ ] Grid-based pathfinding algorithm (A*)
- [ ] Basic Manhattan routing with obstacle avoidance
- [ ] Unit tests and validation

### Phase 2: Multiple Routing Strategies
- [ ] Implement SHORTEST, CLEARANCE, AESTHETIC strategies
- [ ] Cost function optimization for each strategy
- [ ] Performance optimization and benchmarking
- [ ] Integration testing with complex layouts

### Phase 3: API Integration & Polish
- [ ] Extend `auto_route_pins()` with strategy parameter
- [ ] Comprehensive error handling and fallback logic
- [ ] Documentation and usage examples
- [ ] Integration with existing connectivity detection

### Phase 4: Advanced Features (Future)
- [ ] Multi-net routing optimization
- [ ] Component rotation support
- [ ] Hierarchical sheet routing integration  
- [ ] Interactive routing suggestions

## Success Metrics

### Functional Success
- [ ] Successfully routes 95%+ of testable component pairs
- [ ] Generated wire paths maintain 1.27mm grid alignment
- [ ] All routed connections pass KiCAD connectivity verification
- [ ] Clean Manhattan geometry with minimal unnecessary turns

### Performance Success  
- [ ] Simple routing completed in <100ms
- [ ] Complex schematics (100+ components) routed in <5 seconds
- [ ] Memory usage remains reasonable for large designs

### Quality Success
- [ ] Visual quality comparable to manual routing
- [ ] Professional schematic appearance maintained
- [ ] Integration maintains exact KiCAD format preservation
- [ ] Zero regression in existing functionality

## Risk Assessment

### Technical Risks
**High**: Algorithm complexity for dense component layouts
- *Mitigation*: Implement multiple strategies, fallback to direct routing

**Medium**: Performance with large schematics  
- *Mitigation*: Grid partitioning and local optimization

**Low**: Integration with existing codebase
- *Mitigation*: Comprehensive testing and backward compatibility

### Market Risks
**Low**: Limited user adoption due to complexity
- *Mitigation*: Simple API with intelligent defaults

## Dependencies

### External Dependencies
- **circuit-synth bounding box algorithms**: Already integrated ✅
- **KiCAD symbol library access**: Available via existing cache system ✅
- **Grid snapping utilities**: Part of existing wire routing system ✅

### Internal Dependencies  
- **Existing wire routing system**: Foundation for direct routing ✅
- **Component positioning system**: Required for obstacle map generation ✅
- **Connectivity detection**: Integration point for validation ✅

## Future Considerations

### Potential Enhancements
1. **Machine Learning Integration**: Learn from manual routing patterns
2. **Multi-Layer Routing**: Support for hierarchical sheet pin routing
3. **Real-Time Interactive Routing**: Live path preview during manual placement
4. **Advanced Optimization**: Multi-objective optimization for complex trade-offs

### Scalability Considerations
1. **Grid Partitioning**: Divide large schematics into routing regions
2. **Parallel Processing**: Multi-threaded routing for independent nets
3. **Incremental Updates**: Efficient re-routing when components move

## Conclusion

This Manhattan routing implementation addresses a significant gap in the KiCAD schematic automation ecosystem. By building on proven EDA routing algorithms and integrating with our existing precise grid system, we can provide professional-quality automated routing that enhances productivity while maintaining the high standards expected in electronic design.

The modular architecture allows for iterative development, starting with basic obstacle avoidance and evolving toward sophisticated multi-strategy routing that rivals commercial EDA tools.