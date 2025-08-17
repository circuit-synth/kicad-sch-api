# Product Requirements Document: kicad-sch-api

## Executive Summary

`kicad-sch-api` is an independent, professional Python library for programmatic KiCAD schematic manipulation with exact format preservation. Built as a foundational library for tools and AI agents, it provides complete CRUD operations, multi-source component library integration, and a modern Python API designed for extensibility and performance.

## Product Vision

**Vision Statement**: Create the definitive Python library for KiCAD schematic automation - a reliable foundation that tools, AI agents, and engineers can build upon with confidence.

**Core Principles**:
- **Independent Innovation**: Not a wrapper or enhancement - a ground-up professional implementation
- **Foundation First**: Built to be the base layer for higher-level tools and automation
- **Format Perfection**: Byte-for-byte KiCAD compatibility with exact format preservation
- **Modern Architecture**: Clean Python patterns, no legacy baggage
- **Extensible Design**: Plugin architecture for libraries, validation, and future features

## Target Users

### Primary Users (Equal Priority)
1. **Tool Developers**: Building automation, verification, or design tools on top of our API
2. **AI Agent Developers**: Integrating schematic manipulation into AI workflows via MCP

### Secondary Users  
- **Circuit Engineers**: Automating repetitive tasks and bulk operations
- **EDA Companies**: Integrating KiCAD support into their toolchains
- **Educational Institutions**: Teaching programmatic EDA workflows

## Core Requirements

### 1. Complete CRUD Operations (Foundation)

#### Create
- New schematics with configurable metadata (version, generator, paper size)
- Components with full property support (standard and custom)
- Wires, junctions, labels (local, global, hierarchical)
- Hierarchical sheets and multi-sheet designs
- Power symbols and no-connect flags
- Optional manual UUID specification for testing

#### Read  
- Parse any KiCAD 9 .kicad_sch file (strict version checking)
- Extract all components, properties, connections, metadata
- Generate Python code that recreates schematics exactly
- Support for hierarchical designs and complex projects
- Fail explicitly on unknown elements (no silent corruption)

#### Update
- Modify any component property without restrictions
- Move, rotate, mirror components
- Change wire routing and connections
- Update labels and hierarchical references
- Bulk operations for efficiency
- No validation by default (user/tool responsible)

#### Delete
- Remove components with basic cleanup
- Delete wires, junctions, labels
- Remove hierarchical sheets
- Clear entire schematics

### 2. Library Integration (Multi-Source)

**Priority Order**:
1. Local KiCAD symbol libraries (.kicad_sym files)
2. DigiKey API (with caching)
3. SnapEDA integration
4. User-defined sources (plugin architecture)

**Features**:
- Symbol search and discovery
- Footprint recommendations
- Component property population (MPN, datasheet, etc.)
- Fallback mechanisms for missing symbols
- Performance-optimized caching

### 3. Validation System

**Configurable Levels**:
- **None**: No validation (default for speed)
- **Basic**: Reference uniqueness, required properties
- **Standard**: Electrical rules, connection validity
- **Full**: kicad-cli ERC integration

**Initial Implementation**: kicad-cli ERC only (built-in, reliable)

### 4. MCP Server Integration

**Design Alongside CRUD** (not after):
- TypeScript MCP server as separate package
- Python bridge for reliable communication
- Comprehensive tool definitions for all CRUD operations
- Error propagation with context
- Session management for multi-step operations

**Core MCP Tools**:
```typescript
- create_schematic
- load_schematic
- save_schematic
- add_component
- update_component
- delete_component
- add_wire
- connect_components
- validate_design
- search_libraries
```

### 5. Modern Python API

**Design Philosophy**:
- Clean, pythonic interfaces
- Type hints throughout
- Predictable behavior (no magic)
- Explicit errors (no None returns)
- Performance by default

**Example API**:
```python
import kicad_sch_api as ksa

# Create with optional UUID override
sch = ksa.create_schematic("My Circuit", uuid="specific-uuid")

# Add component with optional manual UUIDs
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1", 
    value="10k",
    position=(100, 100),
    uuid="manual-uuid"  # Optional for testing
)

# Direct property access
resistor.footprint = "Resistor_SMD:R_0603_1608Metric"
resistor.set_property("MPN", "RC0603FR-0710KL")

# Bulk operations
sch.components.bulk_update(
    criteria={"lib_id": "Device:R"},
    updates={"Tolerance": "1%"}
)

# Multi-source library search
component = ksa.libraries.search("STM32F103", sources=["digikey", "snapeda"])

# Save with exact format preservation
sch.save("output.kicad_sch")
```

## Technical Architecture

### Core Structure
```
kicad-sch-api/
├── PRD.md                          # This document
├── python/
│   ├── kicad_sch_api/
│   │   ├── core/                   # CRUD operations, types, parser
│   │   ├── library/                # Multi-source library integration
│   │   ├── validation/             # Configurable validation levels
│   │   └── plugins/                # Extension system
│   └── tests/
│       ├── unit/                    # Component-level tests
│       ├── integration/             # Full workflow tests
│       └── reference/               # KiCAD compatibility tests
└── mcp-server/
    ├── src/
    │   ├── tools/                   # MCP tool definitions
    │   ├── bridge/                  # Python communication
    │   └── handlers/                # Request processing
    └── examples/                    # Integration examples
```

### Key Technologies
- **S-expression parsing**: sexpdata (proven library)
- **Validation**: kicad-cli ERC (official tool)
- **API patterns**: Modern Python with type hints
- **Testing**: pytest with reference schematics
- **MCP**: TypeScript server with Python bridge

## Implementation Phases

### Phase 1: CRUD Foundation (Current)
**Timeline**: 2-3 weeks
- [x] Component creation with properties
- [x] Basic wire and junction support
- [ ] Complete schematic reading/import
- [ ] Python code generation from schematics
- [ ] Component update without restrictions
- [ ] Component deletion with cleanup

### Phase 2: Library Integration
**Timeline**: 2-3 weeks
- [ ] Local KiCAD library discovery
- [ ] Symbol search and caching
- [ ] DigiKey API integration
- [ ] SnapEDA integration
- [ ] Plugin architecture for custom sources

### Phase 3: MCP Server
**Timeline**: 2-3 weeks
- [ ] TypeScript project setup
- [ ] Python bridge implementation
- [ ] Core CRUD tools
- [ ] Library search tools
- [ ] Session management
- [ ] Error handling

### Phase 4: Validation & Testing
**Timeline**: 1-2 weeks
- [ ] kicad-cli ERC integration
- [ ] Configurable validation levels
- [ ] Comprehensive test suite
- [ ] Performance benchmarks
- [ ] Documentation

### Phase 5: Advanced Features
**Timeline**: Ongoing
- [ ] Hierarchical sheet management
- [ ] Net extraction and analysis
- [ ] BOM generation
- [ ] Design rule checking
- [ ] Performance optimizations

## Success Metrics

### Technical
- **Format Fidelity**: 100% round-trip compatibility with KiCAD 9
- **Performance**: Handle 1000+ component schematics in <1 second
- **Test Coverage**: >90% code coverage
- **API Completeness**: All KiCAD schematic elements supported

### Adoption
- **GitHub Stars**: 500+ in first 6 months
- **PyPI Downloads**: 1000+ monthly active users
- **MCP Integrations**: 3+ AI frameworks using our server
- **Community PRs**: 10+ external contributors

### Quality
- **Zero Data Loss**: Never corrupt or lose schematic data
- **Exact Preservation**: Generated files indistinguishable from KiCAD
- **Clear Errors**: Every failure has actionable error message
- **Documentation**: 100% public API documented

## Design Decisions

### Why Independent (Not Wrapper)?
- **Innovation Freedom**: Not constrained by others' design choices
- **Performance**: Direct implementation without wrapper overhead  
- **Maintenance**: Full control over codebase and fixes
- **Future-Proof**: Can evolve with KiCAD without dependency issues

### Why Foundation Library?
- **Single Responsibility**: Do schematic manipulation perfectly
- **Tool Agnostic**: Let tools decide business logic
- **Composable**: Easy to integrate into any workflow
- **Testable**: Clear boundaries and responsibilities

### Why MCP Alongside CRUD?
- **Market Timing**: AI integration is happening now
- **Design Influence**: MCP needs inform API design
- **Parallel Development**: Different skill sets can work simultaneously
- **Early Validation**: Test API usability via MCP tools

### Why No Validation by Default?
- **Performance**: Validation is expensive
- **Flexibility**: Tools may have custom rules
- **Simplicity**: Less code, fewer bugs
- **User Control**: Explicit validation when needed

## Risks & Mitigations

### Technical Risks
- **KiCAD Format Changes**: Version detection and compatibility layers
- **Library API Limits**: Caching and rate limiting strategies
- **Performance at Scale**: Profiling and optimization sprints
- **MCP Protocol Changes**: Abstraction layer for protocol updates

### Project Risks  
- **Scope Creep**: Strict adherence to foundation principle
- **Complexity Growth**: Regular refactoring and simplification
- **Testing Burden**: Automated test generation from references
- **Documentation Lag**: Documentation-first development

## Open Questions

### Wire Representation
- Single segment only vs multi-point wires?
- *Decision pending KiCAD format investigation*

### Hierarchical Complexity
- How deep should sheet nesting support go?
- *Start with 2 levels, expand based on usage*

### Library Caching Strategy
- Memory vs disk caching?
- *Hybrid approach with configurable limits*

### MCP Session State
- Stateless vs stateful operations?
- *Stateless with optional session context*

## Summary

kicad-sch-api is positioned as the professional foundation for KiCAD schematic automation. By focusing on being an independent, high-quality library with complete CRUD operations, multi-source component libraries, and modern API design, we enable tool developers and AI agents to build powerful automation on a reliable base.

Our commitment to exact format preservation, extensible architecture, and parallel MCP development ensures we meet both current needs and future opportunities in the rapidly evolving EDA automation space.

---

**Document Version**: 1.0  
**Created**: January 2025  
**Status**: Active Development  
**Next Review**: After Phase 1 completion