# MCP Server PRD - Executive Summary

**Version**: 1.0 | **Date**: 2025-11-06 | **Status**: Draft for Review

---

## Overview

Building an MCP (Model Context Protocol) server for kicad-sch-api to enable AI assistants (Claude, Cursor) to create and manipulate KiCad schematics through natural language.

**Key Differentiator**: First MCP server focused on **schematic creation and manipulation** - existing KiCad MCP servers only do PCB analysis and DRC checking.

---

## Problem & Opportunity

### Current Gaps
- No standardized way for AI to create KiCad schematics programmatically
- Existing MCP servers (lamaalrajih/kicad-mcp) are read-only, analysis-focused
- Manual schematic creation is time-consuming and repetitive

### Target Users
1. **Primary**: AI assistants (Claude Desktop, Cursor) acting for engineers
2. **Secondary**: Engineers using AI to accelerate schematic creation
3. **Tertiary**: Automation engineers building circuit generation pipelines

### Success Metrics (3 months)
- 500+ installations
- 50+ tool calls per active user per week
- <5% error rate on schematic generation
- <500ms P95 latency for operations
- 50+ GitHub stars

---

## Product Vision

> "Make KiCad schematic creation as easy as describing a circuit in natural language, enabling AI assistants to be productive circuit design collaborators."

### Strategic Goals
1. **Empower AI Assistants**: Enable Claude/Cursor to create production-quality schematics
2. **Accelerate Design**: 10× faster circuit prototyping through AI collaboration
3. **Democratize Access**: Lower barrier to entry for circuit design
4. **Showcase API**: Demonstrate kicad-sch-api capabilities through living examples

### Explicitly Out of Scope
- ❌ PCB layout generation (use existing KiCad MCP servers)
- ❌ Component sourcing/purchasing
- ❌ Simulation execution
- ❌ Schematic visual editing UI
- ❌ Real-time collaboration

---

## Core Use Cases

### UC-1: Create Simple Circuit from Description
**User**: "Create a voltage divider with 10k and 1k resistors"

**AI Flow**:
1. `create_schematic(name="Voltage Divider")`
2. `add_component(lib_id="Device:R", reference="R1", value="10k")`
3. `add_component(lib_id="Device:R", reference="R2", value="1k")`
4. `connect_pins(ref1="R1", pin1="2", ref2="R2", pin2="1")`
5. `add_power_symbols(vcc=True, gnd=True)`
6. `save_schematic(path="voltage_divider.kicad_sch")`

### UC-2: Modify Existing Design
**User**: "Change all 10k resistors to 4.7k"

**AI Flow**:
1. `load_schematic(path="circuit.kicad_sch")`
2. `filter_components(lib_id="Device:R", value="10k")`
3. `update_components(updates={"value": "4.7k"})`
4. `save_schematic()`

### UC-3: Generate Standard Circuit Pattern
**User**: "Create an STM32 minimal system"

**AI Flow**: Uses high-level pattern tools to create complete minimal system with MCU, decoupling caps, crystal, reset circuit, and power regulation.

---

## Functional Requirements - Tool Categories

### 1. Schematic Management (5 tools)
- `create_schematic`, `load_schematic`, `save_schematic`, `close_schematic`, `list_projects`

### 2. Component Management (7 tools)
- `add_component`, `list_components`, `update_component`, `remove_component`
- `filter_components`, `get_component_pins`, `search_symbols`

### 3. Connectivity (7 tools)
- `add_wire`, `connect_pins`, `add_label`, `add_junction`
- `analyze_connectivity`, `list_nets`, `get_net_components`

### 4. Power Symbols (2 tools)
- `add_power_symbol` (VCC/GND/VDD/VSS), `add_power_flag`

### 5. Standard Circuit Patterns (5 high-level tools)
- `add_decoupling_caps`, `add_pull_resistor`, `add_led_indicator`
- `add_voltage_divider`, `add_rc_filter`

### 6. Analysis Tools (4 tools)
- `validate_schematic` (ERC), `generate_netlist`, `generate_bom`, `get_statistics`

### 7. Resources (5 read-only URIs)
- `kicad-sch://current/info`, `kicad-sch://current/components`
- `kicad-sch://current/nets`, `kicad-sch://libraries/list`, `kicad-sch://templates/list`

### 8. Prompts (3 conversation templates)
- `create_basic_circuit`, `debug_connectivity`, `suggest_improvements`

**Total**: 35+ tools/resources for comprehensive schematic manipulation

---

## Technical Architecture

### Technology Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| **MCP Framework** | FastMCP 2.0 | Industry standard, production-ready |
| **Transport** | STDIO (primary) | Claude Desktop compatibility |
| **Core Library** | kicad-sch-api 0.5.0+ | Foundation for operations |
| **Data Validation** | Pydantic v2 | Type safety, schema generation |
| **Logging** | structlog | Structured logging, no stdout contamination |
| **Testing** | pytest + pytest-asyncio | Async support, fixtures |

### Project Structure
```
kicad-sch-api/
├── kicad_sch_api/              # Existing core library
├── mcp_server/                 # NEW: MCP server package
│   ├── server.py              # Main FastMCP server
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic models
│   ├── context.py             # Server context (active schematic)
│   ├── tools/                 # Tool implementations (6 modules)
│   ├── resources/             # Resource implementations
│   ├── prompts/               # Prompt templates
│   └── utils/                 # Validation, errors, logging
├── tests/mcp_server/          # Comprehensive test suite
├── docs/
│   ├── MCP_SERVER.md          # User guide
│   ├── MCP_TOOLS.md           # Tool reference
│   └── MCP_EXAMPLES.md        # Usage examples
└── examples/mcp_conversations/ # Example conversations
```

### Key Design Patterns

**Server Context**: Global state tracking active schematic, modifications, path

**Pydantic Models**: Type-safe inputs/outputs with automatic schema generation

**Error Handling**: Structured classification (client 4xx, server 5xx), typed error objects

**Resource Pattern**: Read-only data access via URIs

---

## Implementation Plan (8 weeks)

### Phase 1: Foundation (Week 1-2)
**Milestone**: Basic MCP server with core tools

**Deliverables**:
- FastMCP server with STDIO transport
- 5 core tools: create/load/save schematic, add/list components
- Unit tests + basic documentation

---

### Phase 2: Connectivity & Components (Week 3-4)
**Milestone**: Can build complete simple circuits

**Deliverables**:
- Component management, connectivity, power symbol tools (FR-3, 4, 5)
- Integration tests for circuit building
- Example conversations for common circuits

---

### Phase 3: Patterns & Analysis (Week 5-6)
**Milestone**: High-level patterns and validation

**Deliverables**:
- Standard pattern tools, analysis tools (FR-6, 7)
- Resources and prompts (FR-8, 9)
- Performance optimization + comprehensive testing

---

### Phase 4: Polish & Release (Week 7-8)
**Milestone**: v1.0 production release

**Deliverables**:
- Performance benchmarking + security audit
- Complete documentation (user guide, tool reference, examples)
- Video demos + README update
- PyPI release with [mcp] extra
- Public announcement

---

## Testing Strategy

### Multi-Layer Testing Pyramid
1. **Unit Tests**: Individual tool functionality (>90% coverage target)
2. **Integration Tests**: Complete workflows (e.g., build voltage divider)
3. **Contract Tests**: MCP protocol compliance
4. **Load Tests**: 100 concurrent tool calls, >20 req/s throughput
5. **Property Tests**: Hypothesis-based roundtrip validation

### Test Categories
- Format preservation (exact KiCad compatibility)
- Error handling and validation
- Performance benchmarks
- Security (path traversal, input validation)

---

## Non-Functional Requirements

### Performance Targets
- Tool call latency: <100ms P95 (simple), <500ms P99 (complex)
- Memory footprint: <100MB baseline
- Schematic load/save: <200ms / <300ms (100 components)
- Throughput: >1000 requests/second

### Quality Targets
- Test coverage: >90%
- Type coverage: 100% (strict mypy)
- Tool success rate: >99.9%
- Documentation: 100% of tools documented with examples

### Security
- File system access limited to configured paths
- Pydantic schema enforcement for all inputs
- Path traversal prevention
- No credential exposure in logs/errors

---

## Success Metrics & KPIs

### Adoption (3 months)
- 500+ downloads (PyPI)
- 50+ GitHub stars
- 100+ weekly active users
- 5000+ total tool calls

### Quality
- >90% test coverage
- 100% type coverage
- <1% error rate
- 100% tool documentation

### Performance
- <100ms P95 latency (simple)
- <500ms P99 latency (complex)
- >100 req/s throughput
- <100MB memory footprint

### Community (6 months)
- 5+ community PRs
- 10+ issues reported
- 3+ documentation PRs
- 5+ example contributions

---

## Key Risks & Mitigations

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| FastMCP breaking changes | High | Pin to major version, monitor releases |
| MCP protocol evolution | High | Follow official SDK, participate in community |
| kicad-sch-api bugs | Medium | Comprehensive testing, quick fixes |

### Adoption Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Low discoverability | High | SEO, MCP directory listings, social media |
| Complex setup | Medium | Clear docs, video tutorials, troubleshooting |
| Learning curve | Medium | Comprehensive examples, prompt templates |

### Security Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Path traversal attacks | High | Strict path validation, sandboxing |
| Credential exposure | High | Structured logging, no secrets |
| DOS attacks | Medium | Rate limiting, resource limits |

---

## Critical Enhancements for Phase 1

### Pin Connection & Wire Routing (PRIORITY)

**Issue**: Pin/wire connection accuracy is the make-or-break feature for MCP usability.

**Current State** (v0.5.0):
- ✅ Accurate pin position calculation with full transformations
- ✅ Basic pin-to-pin wiring (`connect_pins_with_wire`)
- ✅ 19 tests covering rotations and references

**Critical Gaps**:
- ❌ AI can't discover available pins programmatically
- ❌ No smart routing (creates diagonal wires, not orthogonal)
- ❌ No automatic junction creation
- ❌ Can't find pins by semantic name ("clock", "VCC", "output")
- ❌ No connection validation tools

**Required MCP Tools** (Phase 1):
1. `get_component_pins` - Discover all pins with metadata (number, name, type, position)
2. `find_pins_by_name` - Semantic pin lookup ("VCC" → pin numbers)
3. `connect_pins` - Enhanced with orthogonal routing + auto-junctions
4. `validate_connectivity` - Check for connection errors before save

**See**: `MCP_PIN_CONNECTION_STRATEGY.md` for complete analysis and implementation plan

---

## Open Questions & Decisions

### Technical
- ⏳ Support multiple open schematics? **Recommendation**: Single (simpler v1)
- ⏳ Include KiCad CLI integration? **Recommendation**: Yes
- ⏳ Support hierarchical sheets in v1? **Recommendation**: No (defer to v2)
- ⏳ Add telemetry (opt-in)? **Recommendation**: Yes (for metrics)
- ⏳ Support undo/redo? **Recommendation**: No (complex state)
- 🔴 **Pin connection enhancements ready?** **Recommendation**: Implement in Phase 1

### Product
- ⏳ Separate MCP server PyPI package? **Recommendation**: Monorepo (easier sync)
- ⏳ Charge for commercial use? **Recommendation**: Free (community focus)
- ⏳ Build hosted service? **Recommendation**: No (self-hosted only v1)

---

## Future Roadmap

### v1.1 (Q2 2025)
- SSE transport for web clients
- Advanced pattern library (filters, regulators, interfaces)
- Hierarchical sheet support
- Enhanced analysis (signal integrity, thermal)

### v1.2 (Q3 2025)
- Multi-schematic projects
- Component library search improvements
- SPICE integration for simulation
- BOM optimization suggestions

### v2.0 (Q4 2025)
- OAuth authentication for multi-user
- Real-time collaboration
- Cloud storage integration
- Advanced AI agent orchestration

---

## Quick Reference: MCP Ecosystem Best Practices

Based on research from authoritative sources (2025):

1. **FastMCP 2.0** is industry standard for Python MCP development
2. **Single-responsibility servers** preferred over monoliths
3. **Pydantic models** essential for type safety
4. **STDIO transport** required for Claude Desktop
5. **Structured logging** (JSON, no stdout) critical for debugging
6. **Multi-layer testing** (unit → integration → contract → load)
7. **Defense in depth security** with 5 protective layers
8. **Existing KiCad MCP** focuses on analysis, not creation (our opportunity)
9. **Documentation quality** correlates 2× with adoption rates

---

## Installation Quick Start (After Implementation)

```bash
# Install with MCP server support
pip install kicad-sch-api[mcp]

# Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**First Test**: Open Claude Desktop and say:
> "Create a simple voltage divider circuit with 10k and 1k resistors"

---

## References

1. MCP Specification: https://modelcontextprotocol.io/
2. FastMCP Framework: https://github.com/jlowin/fastmcp
3. Official Python SDK: https://github.com/modelcontextprotocol/python-sdk
4. MCP Best Practices: https://modelcontextprotocol.info/docs/best-practices/
5. kicad-sch-api: https://github.com/circuit-synth/kicad-sch-api
6. Existing KiCad MCP: https://github.com/lamaalrajih/kicad-mcp

---

**Document Status**: 🟡 Draft - Awaiting Review
**Next Steps**: Review with core team → Incorporate feedback → Begin Phase 1 implementation
