# Architecture Decision Record (ADR) - kicad-sch-api

## ADR-001: S-expression Foundation with Enhanced API

**Date**: 2025-08-13
**Status**: Implemented

### Context
Need for professional KiCAD schematic manipulation without losing format fidelity.

### Decision
Use sexpdata library for S-expression parsing with custom object-oriented API layer.

### Rationale
- sexpdata is a proven, lightweight S-expression parser
- Object-oriented API improves developer experience
- Maintains exact format preservation as core differentiator
- Independent implementation allows full control

### Consequences
- ✅ Clean separation between parsing and API layers
- ✅ Exact KiCAD compatibility maintained
- ✅ Developer-friendly interface for common operations
- ⚠️ Slightly higher memory usage due to API abstraction

---

## ADR-002: Component-Centric API Design

**Date**: 2025-08-13
**Status**: Implemented

### Context
Multiple approaches for schematic element access and manipulation.

### Decision
Component-first API with property-based manipulation.

### Rationale
- Components are primary elements engineers work with
- Property-based updates match KiCAD's internal model
- Enables bulk operations on component collections
- Natural mapping to S-expression structure

### Implementation
```python
# Component access
component = sch.components.get_by_reference('R1')
component.value = '10k'
component.footprint = 'Resistor_SMD:R_0603_1608Metric'

# Bulk operations
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)
```

---

## ADR-003: Format Preservation Strategy

**Date**: 2025-08-13
**Status**: Implemented

### Context
KiCAD uses specific S-expression formatting that must be preserved.

### Decision
Parse-modify-serialize cycle maintains original formatting.

### Rationale
- KiCAD is sensitive to formatting changes
- Round-trip compatibility ensures workflow integration
- Preserves comments, spacing, and element ordering
- Core differentiator from other libraries

### Implementation
- Original S-expression structure preserved during parsing
- Modifications applied as targeted changes
- Serialization maintains original formatting patterns
- Validation ensures output matches KiCAD expectations

---

## ADR-004: Testing Strategy with Reference Schematics

**Date**: 2025-08-13
**Status**: Implemented

### Context
Need comprehensive testing for format preservation and functionality.

### Decision
Reference schematic approach with round-trip validation.

### Test Projects
- `single_resistor`: Basic component manipulation
- `resistor_divider`: Multiple components and connections
- `single_hierarchical_sheet`: Complex hierarchical structures
- `single_label*`: Label and net handling

### Validation
- Round-trip: load → modify → save → reload → compare
- Format preservation: exact byte-level comparison where possible
- Functional validation: KiCAD can open and process modified files

---

## ADR-005: Performance Optimization Approach

**Date**: 2025-08-14
**Status**: Planned

### Context
Large schematics (1000+ components) need efficient operations.

### Decision
Implement symbol caching and indexed lookups.

### Planned Implementation
- Symbol library caching to avoid repeated disk access
- Component indexing by reference, value, footprint
- Bulk operation optimization with batched S-expression updates
- Lazy loading for large hierarchical designs

### Trade-offs
- ✅ Significant performance gains for large schematics
- ✅ Maintains API simplicity for small projects
- ⚠️ Increased memory usage for caching
- ⚠️ Cache invalidation complexity

---

## Technology Choices

### Python vs Other Languages
**Decision**: Python primary with TypeScript MCP server

**Rationale**:
- Python dominant in EDA automation
- Rich ecosystem for data manipulation
- TypeScript enables AI agent integration via MCP
- Dual-language approach leverages strengths of both

### sexpdata vs Custom Parser
**Decision**: Use sexpdata with custom enhancements

**Rationale**:
- Mature S-expression parsing foundation
- Focus development on KiCAD-specific features
- Avoid reinventing parsing infrastructure
- Allows customization for format preservation

### pytest vs unittest
**Decision**: pytest for testing framework

**Rationale**:
- More concise test syntax
- Better fixture management
- Rich plugin ecosystem
- Industry standard for modern Python projects

---

## Integration Patterns

### MCP Server Architecture
**Status**: Planned

**Pattern**: Separate TypeScript process communicating with Python core

```typescript
// MCP Server provides AI-friendly interface
interface SchematicAgent {
  loadSchematic(path: string): Promise<SchematicContext>
  addComponent(type: string, properties: ComponentProperties): Promise<Component>
  bulkUpdate(criteria: ComponentCriteria, updates: ComponentUpdates): Promise<void>
}
```

### Error Handling Strategy
**Pattern**: Validation with error collection
- Parse errors collected, not thrown immediately
- Validation warnings vs hard errors
- Context-aware error messages with location information
- Graceful degradation for partial file corruption
