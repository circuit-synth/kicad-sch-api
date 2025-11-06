# Product Requirements Document: KiCad Schematic API MCP Server

**Version**: 1.0
**Date**: 2025-11-06
**Status**: Draft for Review
**Author**: Circuit-Synth Team

---

## Executive Summary

This PRD defines requirements for building a Model Context Protocol (MCP) server for the kicad-sch-api library. The MCP server will enable AI assistants (Claude, Cursor, etc.) to programmatically create, manipulate, and analyze KiCad schematics through natural language interactions.

**Key Differentiator**: While existing KiCad MCP servers focus on PCB analysis and DRC checking, our server focuses on **schematic creation and manipulation** using the powerful kicad-sch-api library.

---

## 1. Problem Statement

### Current State

**For Python Developers:**
- kicad-sch-api provides powerful schematic manipulation capabilities
- Requires knowledge of Python API and KiCad structure
- Manual coding required for every schematic operation

**For AI Assistants:**
- No standardized way to create KiCad schematics programmatically
- Existing KiCad MCP servers focus on analysis, not creation
- Cannot leverage kicad-sch-api's capabilities through natural language

**For Circuit Designers:**
- Creating schematics from descriptions is manual and time-consuming
- Repetitive patterns require copy-paste or manual recreation
- No AI assistance for schematic generation

### Target Users

1. **Primary**: AI assistants (Claude Desktop, Cursor IDE) acting on behalf of engineers
2. **Secondary**: Engineers using AI to accelerate schematic creation
3. **Tertiary**: Automation engineers building circuit generation pipelines

### Success Metrics

- **Adoption**: 500+ installations within 3 months
- **Usage**: Average 50+ tool calls per active user per week
- **Quality**: <5% error rate on schematic generation
- **Performance**: <500ms P95 latency for simple operations
- **Community**: 50+ GitHub stars within first month

---

## 2. Market Research & Competitive Analysis

### Existing MCP Servers for Electronics

| Server | Focus | Limitations | Opportunity |
|--------|-------|-------------|-------------|
| **lamaalrajih/kicad-mcp** | PCB analysis, DRC, BOM | Read-only, no schematic creation | Complement with creation tools |
| **CAD-MCP** | AutoCAD/GstarCAD control | Not KiCad-specific | KiCad schematic focus |
| **EDA Tools MCP** | Verilog, ASIC flows | Digital design, not schematics | Analog/mixed-signal gap |
| **Hardware MCP** | Mechanical CAD | Not electronic schematics | Electronic circuit focus |

**Key Insight**: No existing MCP server provides comprehensive **schematic creation and manipulation** capabilities for KiCad.

### MCP Ecosystem Trends (2025)

Based on research from multiple sources:

1. **FastMCP Framework**: Industry standard for Python MCP development
2. **Single-Responsibility Servers**: Focused servers preferred over monoliths
3. **OAuth Integration**: Production authentication now standard
4. **Observability**: Prometheus metrics + OpenTelemetry tracing expected
5. **Containerization**: Docker packaging standard for deployment
6. **Vector DB Integration**: Common pattern for RAG workflows

### Best Practices Synthesis

From research across multiple authoritative sources:

#### Tool Design Patterns
- **Single Responsibility**: One clear purpose per server
- **Typed Outputs**: Use Pydantic models for schema validation
- **Context Injection**: Enable progress reporting for long operations
- **Focused Toolsets**: High-level functions, not raw API mappings

#### Error Handling
- **Structured Classification**: Client (4xx), Server (5xx), External (502/503)
- **Typed Error Objects**: category, code, message, retry guidance
- **Safe Defaults**: Return safe values on unexpected errors
- **Comprehensive Logging**: Never write to stdout (breaks STDIO transport)

#### Testing Strategy (Multi-Layer Pyramid)
1. **Unit Tests**: Individual tool functionality
2. **Integration Tests**: Tool interactions and workflows
3. **Contract Tests**: MCP protocol compliance
4. **Load Tests**: Performance under concurrent demand
5. **Chaos Tests**: Resilience during failures

#### Security (Defense in Depth)
1. **Network Isolation**: Local binding by default
2. **Authentication**: JWT/token-based for production
3. **Authorization**: Capability-based ACLs
4. **Input Validation**: Schema enforcement + sanitization
5. **Monitoring**: Audit logging + alerting

#### Performance Targets
- **Throughput**: >1000 requests/second
- **Latency**: <100ms P95 (simple), <500ms P99 (complex)
- **Error Rate**: <0.1%
- **Availability**: 99.9% uptime

---

## 3. Product Vision & Goals

### Vision Statement

> "Make KiCad schematic creation as easy as describing a circuit in natural language, enabling AI assistants to be productive circuit design collaborators."

### Strategic Goals

1. **Empower AI Assistants**: Enable Claude/Cursor to create production-quality schematics
2. **Accelerate Design**: 10× faster circuit prototyping through AI collaboration
3. **Democratize Access**: Lower barrier to entry for circuit design
4. **Showcase API**: Demonstrate kicad-sch-api capabilities through living examples

### Non-Goals (Out of Scope)

- ❌ PCB layout generation (use existing KiCad MCP servers)
- ❌ Component sourcing/purchasing (out of scope for v1)
- ❌ Simulation execution (use EDA Tools MCP server)
- ❌ Schematic visual editing UI (KiCad provides this)
- ❌ Real-time collaboration (single-user focus)

---

## 4. User Stories & Use Cases

### Primary Use Cases

#### UC-1: Create Simple Circuit from Description

**Actor**: AI Assistant (Claude)
**Trigger**: User says "Create a voltage divider with 10k and 1k resistors"
**Flow**:
1. AI calls `create_schematic(name="Voltage Divider")`
2. AI calls `add_component(lib_id="Device:R", reference="R1", value="10k", position=(100, 100))`
3. AI calls `add_component(lib_id="Device:R", reference="R2", value="1k", position=(100, 120))`
4. AI calls `connect_pins(ref1="R1", pin1="2", ref2="R2", pin2="1")`
5. AI calls `add_power_symbols(vcc=True, gnd=True)`
6. AI calls `save_schematic(path="voltage_divider.kicad_sch")`

**Success Criteria**: Valid schematic opens in KiCad without errors

---

#### UC-2: Add LED with Current Limiting Resistor

**Actor**: AI Assistant
**Trigger**: User says "Add a red LED with 220Ω current limiting resistor"
**Flow**:
1. AI calls `add_component(lib_id="Device:LED", reference="D1", value="RED", ...)`
2. AI calls `add_component(lib_id="Device:R", reference="R3", value="220", ...)`
3. AI calls `connect_pins(ref1="D1", pin1="K", ref2="R3", pin2="2")`
4. AI calls `add_label(text="VCC", position=...)`

**Success Criteria**: Correct LED polarity, proper connections, labeled nets

---

#### UC-3: Analyze Existing Schematic

**Actor**: AI Assistant
**Trigger**: User says "What components are in this schematic?"
**Flow**:
1. AI calls `load_schematic(path="existing.kicad_sch")`
2. AI calls `list_components()`
3. AI calls `analyze_connectivity()`
4. AI summarizes: "Contains 15 resistors, 3 capacitors, 2 ICs..."

**Success Criteria**: Accurate component list and connectivity analysis

---

#### UC-4: Modify Existing Design

**Actor**: AI Assistant
**Trigger**: User says "Change all 10k resistors to 4.7k"
**Flow**:
1. AI calls `load_schematic(path="circuit.kicad_sch")`
2. AI calls `filter_components(lib_id="Device:R", value="10k")`
3. AI calls `update_components(component_ids=[...], updates={"value": "4.7k"})`
4. AI calls `save_schematic()`

**Success Criteria**: All matching resistors updated, schematic saved correctly

---

#### UC-5: Generate Standard Circuit Pattern

**Actor**: AI Assistant
**Trigger**: User says "Create an STM32 minimal system"
**Flow**:
1. AI calls `create_schematic(name="STM32 System")`
2. AI calls `add_component(lib_id="MCU_ST_STM32:STM32G431RBTx", ...)`
3. AI calls `add_decoupling_capacitors(ic_ref="U1", values=["100nF", "10uF"])`
4. AI calls `add_crystal(frequency="8MHz", ppm=20)`
5. AI calls `add_reset_circuit()`
6. AI calls `add_power_regulation(input_v=12, output_v=3.3)`

**Success Criteria**: Complete minimal system with all required support circuitry

---

### User Personas

#### Persona 1: "Alex - AI-Assisted Hobbyist"

- **Background**: Mechanical engineer learning electronics
- **Skills**: Basic circuit knowledge, no KiCad experience
- **Goals**: Prototype ideas quickly without learning KiCad interface
- **Pain Points**: Steep learning curve, forgets syntax between projects
- **MCP Value**: "Just describe what I want, AI makes it happen"

#### Persona 2: "Jordan - Professional EE with Repetitive Tasks"

- **Background**: Senior electrical engineer at robotics company
- **Skills**: Expert in circuits, proficient in KiCad
- **Goals**: Automate repetitive schematic patterns, reduce copy-paste
- **Pain Points**: Manual work on standard circuits, testing variations
- **MCP Value**: "Generate 20 test variants in seconds, not hours"

#### Persona 3: "Sam - Automation Engineer"

- **Background**: Software engineer building circuit generation pipelines
- **Skills**: Python expert, learning electronics
- **Goals**: Integrate schematic generation into automated workflows
- **Pain Points**: Complex API surface, hard to test generators
- **MCP Value**: "Natural language = self-documenting test cases"

---

## 5. Functional Requirements

### 5.1 MCP Server Core

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-1.1 | Server uses FastMCP 2.0 framework | P0 | FastMCP dependency in pyproject.toml |
| FR-1.2 | Server name: `kicad-sch-api` | P0 | Registered in MCP client configs |
| FR-1.3 | STDIO transport support | P0 | Works with Claude Desktop config |
| FR-1.4 | Server version in capabilities | P0 | Returns version matching library |
| FR-1.5 | Graceful startup/shutdown | P0 | Proper lifespan management |
| FR-1.6 | Health check endpoint | P1 | Returns "ok" + library version |

### 5.2 Schematic Creation Tools

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-2.1 | `create_schematic` | Create new blank schematic | P0 | `name: str, path?: str` | `SchematicInfo` |
| FR-2.2 | `load_schematic` | Load existing schematic | P0 | `path: str` | `SchematicInfo` |
| FR-2.3 | `save_schematic` | Save current schematic | P0 | `path?: str, auto_annotate?: bool` | `SaveResult` |
| FR-2.4 | `close_schematic` | Close current schematic | P1 | `save?: bool` | `bool` |
| FR-2.5 | `list_projects` | List recent projects | P2 | `limit?: int` | `List[ProjectInfo]` |

### 5.3 Component Management Tools

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-3.1 | `add_component` | Add component to schematic | P0 | `lib_id, reference?, value, position?, rotation?, footprint?, **properties` | `ComponentInfo` |
| FR-3.2 | `list_components` | List all components | P0 | `filter?: dict` | `List[ComponentInfo]` |
| FR-3.3 | `update_component` | Update component properties | P0 | `reference: str, **updates` | `ComponentInfo` |
| FR-3.4 | `remove_component` | Remove component | P0 | `reference: str` | `bool` |
| FR-3.5 | `filter_components` | Find components by criteria | P0 | `lib_id?: str, value?: str, **criteria` | `List[ComponentInfo]` |
| FR-3.6 | `get_component_pins` | List component pins | P1 | `reference: str` | `List[PinInfo]` |
| FR-3.7 | `search_symbols` | Search symbol libraries | P1 | `query: str, library?: str` | `List[SymbolInfo]` |

### 5.4 Connectivity Tools

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-4.1 | `add_wire` | Add wire between points | P0 | `start: Point, end: Point` | `WireInfo` |
| FR-4.2 | `connect_pins` | Wire between component pins | P0 | `ref1, pin1, ref2, pin2, route?: 'direct'\|'orthogonal'` | `WireInfo` |
| FR-4.3 | `add_label` | Add net label | P0 | `text: str, position: Point, type?: 'local'\|'global'\|'hierarchical'` | `LabelInfo` |
| FR-4.4 | `add_junction` | Add wire junction | P1 | `position: Point` | `JunctionInfo` |
| FR-4.5 | `analyze_connectivity` | Get connectivity analysis | P1 | None | `ConnectivityReport` |
| FR-4.6 | `list_nets` | List all nets | P1 | None | `List[NetInfo]` |
| FR-4.7 | `get_net_components` | Components on specific net | P2 | `net_name: str` | `List[ComponentInfo]` |

### 5.5 Power Symbol Tools

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-5.1 | `add_power_symbol` | Add VCC/GND symbol | P0 | `type: 'vcc'\|'gnd'\|'vdd'\|'vss', position: Point, net_name?: str` | `PowerSymbolInfo` |
| FR-5.2 | `add_power_flag` | Add power flag | P1 | `position: Point` | `PowerFlagInfo` |

### 5.6 Standard Circuit Patterns (High-Level Tools)

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-6.1 | `add_decoupling_caps` | Add decoupling capacitors to IC | P1 | `ic_ref, values: List[str], position_offset?` | `List[ComponentInfo]` |
| FR-6.2 | `add_pull_resistor` | Add pull-up/down resistor | P1 | `net: str, type: 'up'\|'down', value: str, position?` | `ComponentInfo` |
| FR-6.3 | `add_led_indicator` | Add LED with current limiting | P1 | `net: str, color?: str, current_ma?: float, position?` | `LEDCircuitInfo` |
| FR-6.4 | `add_voltage_divider` | Add voltage divider | P1 | `r1_value, r2_value, input_net?, output_net?, position?` | `DividerInfo` |
| FR-6.5 | `add_rc_filter` | Add RC low-pass filter | P2 | `r_value, c_value, cutoff_freq?, position?` | `FilterInfo` |

### 5.7 Analysis Tools

| ID | Tool Name | Description | Priority | Inputs | Outputs |
|----|-----------|-------------|----------|--------|---------|
| FR-7.1 | `validate_schematic` | Run ERC validation | P1 | `level?: 'basic'\|'full'` | `ValidationReport` |
| FR-7.2 | `generate_netlist` | Generate netlist | P1 | `format?: 'kicadsexpr'\|'spice'` | `NetlistResult` |
| FR-7.3 | `generate_bom` | Generate bill of materials | P1 | `format?: 'csv'\|'xml'` | `BOMResult` |
| FR-7.4 | `get_statistics` | Get schematic statistics | P2 | None | `SchematicStats` |

### 5.8 Resources (Read-Only Data)

| ID | Resource URI | Description | Priority | Returns |
|----|--------------|-------------|----------|---------|
| FR-8.1 | `kicad-sch://current/info` | Current schematic metadata | P0 | `SchematicInfo` |
| FR-8.2 | `kicad-sch://current/components` | All components (JSON) | P0 | `List[ComponentInfo]` |
| FR-8.3 | `kicad-sch://current/nets` | All nets (JSON) | P1 | `List[NetInfo]` |
| FR-8.4 | `kicad-sch://libraries/list` | Available symbol libraries | P1 | `List[LibraryInfo]` |
| FR-8.5 | `kicad-sch://templates/list` | Available circuit templates | P2 | `List[TemplateInfo]` |

### 5.9 Prompts (Conversation Templates)

| ID | Prompt Name | Description | Priority | Parameters |
|----|-------------|-------------|----------|------------|
| FR-9.1 | `create_basic_circuit` | Template for simple circuits | P1 | `circuit_type: str` |
| FR-9.2 | `debug_connectivity` | Help debug connection issues | P1 | `issue_description: str` |
| FR-9.3 | `suggest_improvements` | Suggest design improvements | P2 | None |

---

## 6. Technical Architecture

### 6.1 Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **MCP Framework** | FastMCP 2.0 | Industry standard, production-ready, extensive features |
| **Transport** | STDIO (primary), SSE (future) | Claude Desktop compatibility, extensibility |
| **Core Library** | kicad-sch-api 0.5.0+ | Foundation for all schematic operations |
| **Data Validation** | Pydantic v2 | Type safety, automatic schema generation, FastMCP integration |
| **Logging** | structlog | Structured logging, JSON output, no stdout contamination |
| **Testing** | pytest + pytest-asyncio | Async support, fixture management, parametrization |
| **Type Checking** | mypy (strict mode) | Static type safety, catch errors early |
| **Code Quality** | black + isort + flake8 | Consistent style, matches main library |

### 6.2 Project Structure

```
kicad-sch-api/
├── kicad_sch_api/              # Core library (existing)
│   └── ...
├── mcp_server/                 # NEW: MCP server package
│   ├── __init__.py            # Server exports
│   ├── server.py              # Main FastMCP server
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic models for tool inputs/outputs
│   ├── context.py             # Server context (active schematic, etc.)
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py
│   │   ├── schematic_tools.py      # FR-2.x: create/load/save
│   │   ├── component_tools.py      # FR-3.x: add/list/update components
│   │   ├── connectivity_tools.py   # FR-4.x: wires/labels/junctions
│   │   ├── power_tools.py          # FR-5.x: power symbols
│   │   ├── pattern_tools.py        # FR-6.x: standard patterns
│   │   └── analysis_tools.py       # FR-7.x: validate/netlist/bom
│   ├── resources/             # Resource implementations
│   │   ├── __init__.py
│   │   └── schematic_resources.py # FR-8.x: read-only data
│   ├── prompts/               # Prompt templates
│   │   ├── __init__.py
│   │   └── circuit_prompts.py     # FR-9.x: conversation templates
│   ├── utils/                 # Utilities
│   │   ├── __init__.py
│   │   ├── validation.py          # Input validation helpers
│   │   ├── errors.py              # Custom exception classes
│   │   └── logging.py             # Logging setup
│   └── README.md              # MCP server documentation
├── tests/
│   └── mcp_server/            # MCP server tests
│       ├── __init__.py
│       ├── conftest.py             # Shared fixtures
│       ├── test_server.py          # Server initialization
│       ├── test_schematic_tools.py # Tool tests
│       ├── test_component_tools.py
│       ├── test_connectivity_tools.py
│       ├── test_pattern_tools.py
│       ├── test_analysis_tools.py
│       ├── test_resources.py       # Resource tests
│       ├── test_prompts.py         # Prompt tests
│       └── test_integration.py     # End-to-end scenarios
├── docs/
│   ├── MCP_SERVER.md          # MCP server user guide
│   ├── MCP_TOOLS.md           # Tool reference documentation
│   └── MCP_EXAMPLES.md        # Usage examples with Claude
├── examples/
│   └── mcp_conversations/     # Example conversations
│       ├── voltage_divider.md
│       ├── led_circuit.md
│       ├── minimal_mcu.md
│       └── ...
├── pyproject.toml             # Updated with [mcp] extra
└── README.md                  # Updated with MCP section
```

### 6.3 Core Architecture Patterns

#### Server Context Management

```python
from contextlib import asynccontextmanager
from typing import Optional
from kicad_sch_api import Schematic

class ServerContext:
    """Global server state."""
    def __init__(self):
        self.current_schematic: Optional[Schematic] = None
        self.schematic_path: Optional[str] = None
        self.modified: bool = False

    def reset(self):
        """Reset context to clean state."""
        self.current_schematic = None
        self.schematic_path = None
        self.modified = False

# Global context instance
ctx = ServerContext()

@asynccontextmanager
async def lifespan(server: FastMCP):
    """Server lifecycle management."""
    logger.info("MCP server starting")
    # Startup: initialize resources
    yield ctx  # Server runs
    # Shutdown: cleanup
    if ctx.current_schematic and ctx.modified:
        logger.warning("Schematic modified but not saved")
    ctx.reset()
    logger.info("MCP server stopped")
```

#### Tool Pattern with Validation

```python
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="kicad-sch-api")

class AddComponentInput(BaseModel):
    """Validated input for add_component tool."""
    lib_id: str = Field(..., description="Library ID (e.g., 'Device:R')")
    reference: Optional[str] = Field(None, description="Component reference")
    value: str = Field(..., description="Component value")
    position: Optional[tuple[float, float]] = Field(None, description="Position (x, y)")
    rotation: float = Field(0.0, ge=0, lt=360, description="Rotation in degrees")
    footprint: Optional[str] = Field(None, description="Footprint")

class ComponentInfo(BaseModel):
    """Component information output."""
    reference: str
    lib_id: str
    value: str
    position: tuple[float, float]
    rotation: float
    uuid: str

@mcp.tool()
def add_component(input: AddComponentInput) -> ComponentInfo:
    """
    Add a component to the current schematic.

    Example:
        add_component(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100)
        )
    """
    if not ctx.current_schematic:
        raise ValueError("No schematic loaded. Call create_schematic() first.")

    comp = ctx.current_schematic.components.add(
        lib_id=input.lib_id,
        reference=input.reference,
        value=input.value,
        position=input.position,
        rotation=input.rotation,
        footprint=input.footprint
    )

    ctx.modified = True

    return ComponentInfo(
        reference=comp.reference,
        lib_id=comp.lib_id,
        value=comp.value,
        position=(comp.position.x, comp.position.y),
        rotation=comp.rotation,
        uuid=comp.uuid
    )
```

#### Error Handling Pattern

```python
from mcp_server.utils.errors import SchematicError, ValidationError

@mcp.tool()
def connect_pins(ref1: str, pin1: str, ref2: str, pin2: str) -> dict:
    """Connect two component pins with a wire."""
    try:
        if not ctx.current_schematic:
            raise SchematicError("No schematic loaded")

        # Get pin positions
        pos1 = ctx.current_schematic.get_component_pin_position(ref1, pin1)
        pos2 = ctx.current_schematic.get_component_pin_position(ref2, pin2)

        if pos1 is None:
            raise ValidationError(f"Pin {pin1} not found on {ref1}")
        if pos2 is None:
            raise ValidationError(f"Pin {pin2} not found on {ref2}")

        # Add wire
        wire = ctx.current_schematic.wires.add(
            points=[pos1, pos2]
        )

        ctx.modified = True

        return {
            "success": True,
            "wire_uuid": wire.uuid,
            "connection": f"{ref1}.{pin1} → {ref2}.{pin2}"
        }

    except SchematicError as e:
        logger.error(f"Schematic error: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in connect_pins: {e}")
        raise SchematicError(f"Failed to connect pins: {e}")
```

#### Resource Pattern

```python
from mcp.server.fastmcp import Context

@mcp.resource("kicad-sch://current/info")
def get_schematic_info() -> dict:
    """Get current schematic metadata."""
    if not ctx.current_schematic:
        return {"error": "No schematic loaded"}

    return {
        "name": ctx.current_schematic.name,
        "path": ctx.schematic_path,
        "modified": ctx.modified,
        "component_count": len(ctx.current_schematic.components),
        "wire_count": len(ctx.current_schematic.wires),
        "label_count": len(ctx.current_schematic.labels)
    }

@mcp.resource("kicad-sch://current/components")
def get_all_components() -> list[dict]:
    """Get all components as JSON."""
    if not ctx.current_schematic:
        return []

    return [
        {
            "reference": comp.reference,
            "lib_id": comp.lib_id,
            "value": comp.value,
            "position": {"x": comp.position.x, "y": comp.position.y},
            "rotation": comp.rotation,
            "footprint": comp.footprint,
            "uuid": comp.uuid
        }
        for comp in ctx.current_schematic.components
    ]
```

### 6.4 Data Models

#### Core Input/Output Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Schematic Models
class SchematicInfo(BaseModel):
    name: str
    path: Optional[str]
    component_count: int
    wire_count: int
    label_count: int
    modified: bool

class SaveResult(BaseModel):
    success: bool
    path: str
    annotated: bool

# Component Models
class ComponentInfo(BaseModel):
    reference: str
    lib_id: str
    value: str
    position: tuple[float, float]
    rotation: float
    footprint: Optional[str]
    uuid: str

class PinInfo(BaseModel):
    number: str
    name: str
    position: tuple[float, float]
    pin_type: str

# Connectivity Models
class WireInfo(BaseModel):
    uuid: str
    points: List[tuple[float, float]]
    net: Optional[str]

class LabelInfo(BaseModel):
    text: str
    position: tuple[float, float]
    type: Literal["local", "global", "hierarchical"]
    uuid: str

class NetInfo(BaseModel):
    name: str
    component_count: int
    components: List[str]  # List of references

# Analysis Models
class ValidationIssue(BaseModel):
    severity: Literal["error", "warning", "info"]
    category: str
    message: str
    component: Optional[str]

class ValidationReport(BaseModel):
    passed: bool
    error_count: int
    warning_count: int
    issues: List[ValidationIssue]

class SchematicStats(BaseModel):
    components: dict[str, int]  # lib_id → count
    total_components: int
    total_wires: int
    total_nets: int
    power_nets: List[str]
```

### 6.5 Configuration Management

```python
from pydantic_settings import BaseSettings
from typing import Optional

class ServerConfig(BaseSettings):
    """Server configuration from environment variables."""

    # Server settings
    server_name: str = "kicad-sch-api"
    server_version: str = "0.5.0"

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    # Paths
    default_schematic_dir: Optional[str] = None
    symbol_library_paths: Optional[str] = None  # Colon-separated

    # Behavior
    auto_annotate: bool = False
    auto_save_backup: bool = True
    grid_size: float = 1.27  # KiCad default grid (mm)

    # Performance
    component_cache_size: int = 1000

    class Config:
        env_prefix = "KICAD_MCP_"
        env_file = ".env"

config = ServerConfig()
```

---

## 7. Non-Functional Requirements

### 7.1 Performance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1.1 | Tool call latency (simple) | <100ms P95 | Prometheus histogram |
| NFR-1.2 | Tool call latency (complex) | <500ms P99 | Prometheus histogram |
| NFR-1.3 | Memory footprint | <100MB baseline | Process monitoring |
| NFR-1.4 | Schematic load time (100 components) | <200ms | Benchmark test |
| NFR-1.5 | Schematic save time | <300ms | Benchmark test |

### 7.2 Reliability

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-2.1 | Tool success rate | >99.9% | Error rate metric |
| NFR-2.2 | Crash recovery | Graceful shutdown | Integration test |
| NFR-2.3 | Error message clarity | 100% actionable | Manual review |
| NFR-2.4 | Data integrity | No corruption | Property test |

### 7.3 Security

| ID | Requirement | Implementation |
|----|-------------|----------------|
| NFR-3.1 | File system access | Limited to configured paths |
| NFR-3.2 | Input validation | Pydantic schema enforcement |
| NFR-3.3 | Path traversal prevention | Validate all file paths |
| NFR-3.4 | No credential exposure | No secrets in logs/errors |

### 7.4 Usability

| ID | Requirement | Implementation |
|----|-------------|----------------|
| NFR-4.1 | Tool descriptions | Clear, example-driven |
| NFR-4.2 | Error messages | Actionable with fix suggestions |
| NFR-4.3 | Documentation | Comprehensive with examples |
| NFR-4.4 | Setup time | <5 minutes from install to first use |

### 7.5 Maintainability

| ID | Requirement | Implementation |
|----|-------------|----------------|
| NFR-5.1 | Code coverage | >90% for tools | pytest-cov |
| NFR-5.2 | Type coverage | 100% (strict mypy) | mypy --strict |
| NFR-5.3 | Documentation | Inline + external | Docstrings + markdown |
| NFR-5.4 | Logging | Structured, searchable | structlog + JSON |

---

## 8. Implementation Plan

### Phase 1: Foundation (Week 1-2)

**Milestone**: Basic MCP server runs and responds to simple tools

**Tasks**:
- [ ] Set up MCP server package structure
- [ ] Configure FastMCP server with STDIO transport
- [ ] Implement server context management
- [ ] Create Pydantic models for core types
- [ ] Implement 5 core tools:
  - `create_schematic`
  - `load_schematic`
  - `save_schematic`
  - `add_component`
  - `list_components`
- [ ] Write unit tests for core tools
- [ ] Create basic documentation

**Deliverable**: MVP MCP server that can create and save schematics

---

### Phase 2: Connectivity & Components (Week 3-4)

**Milestone**: Can build complete simple circuits

**Tasks**:
- [ ] Implement component management tools (FR-3.x)
- [ ] Implement connectivity tools (FR-4.x)
- [ ] Implement power symbol tools (FR-5.x)
- [ ] Add comprehensive error handling
- [ ] Write integration tests for circuit building
- [ ] Create example conversations for common circuits
- [ ] Update documentation with connectivity examples

**Deliverable**: Can create voltage dividers, LED circuits, basic analog circuits

---

### Phase 3: Patterns & Analysis (Week 5-6)

**Milestone**: High-level patterns and validation

**Tasks**:
- [ ] Implement standard pattern tools (FR-6.x)
- [ ] Implement analysis tools (FR-7.x)
- [ ] Add resources for read-only data (FR-8.x)
- [ ] Add prompt templates (FR-9.x)
- [ ] Performance optimization and profiling
- [ ] Comprehensive testing (unit + integration + load)
- [ ] Production-ready error handling

**Deliverable**: Full-featured MCP server with validation and patterns

---

### Phase 4: Polish & Release (Week 7-8)

**Milestone**: v1.0 release ready

**Tasks**:
- [ ] Performance benchmarking and optimization
- [ ] Security audit and hardening
- [ ] Documentation polish (user guide, tool reference, examples)
- [ ] Video demos and GIFs
- [ ] README update with prominent MCP section
- [ ] Release notes and migration guide
- [ ] PyPI package release with [mcp] extra
- [ ] Announce on social media, HN, Reddit

**Deliverable**: Production-ready v1.0 release

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Coverage Target**: >90%

```python
# tests/mcp_server/test_component_tools.py
import pytest
from mcp_server.tools.component_tools import add_component
from mcp_server.context import ServerContext

@pytest.fixture
def ctx_with_schematic():
    ctx = ServerContext()
    ctx.current_schematic = ksa.create_schematic("Test")
    yield ctx
    ctx.reset()

def test_add_component_basic(ctx_with_schematic):
    """Test adding a simple resistor."""
    result = add_component(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100, 100)
    )

    assert result.reference == "R1"
    assert result.lib_id == "Device:R"
    assert result.value == "10k"
    assert result.position == (100, 100)

def test_add_component_auto_reference(ctx_with_schematic):
    """Test auto-generated reference."""
    result = add_component(
        lib_id="Device:R",
        value="10k"
    )

    assert result.reference.startswith("R")

def test_add_component_no_schematic():
    """Test error when no schematic loaded."""
    ctx = ServerContext()

    with pytest.raises(ValueError, match="No schematic loaded"):
        add_component(lib_id="Device:R", value="10k")
```

### 9.2 Integration Tests

```python
# tests/mcp_server/test_integration.py
def test_build_voltage_divider_workflow():
    """Test complete workflow: create schematic → add components → connect → save."""

    # Create schematic
    info = create_schematic(name="Voltage Divider")
    assert info.name == "Voltage Divider"

    # Add components
    r1 = add_component(lib_id="Device:R", reference="R1", value="10k", position=(100, 100))
    r2 = add_component(lib_id="Device:R", reference="R2", value="1k", position=(100, 120))

    # Connect pins
    wire = connect_pins(ref1="R1", pin1="2", ref2="R2", pin2="1")
    assert wire["success"] == True

    # Add power symbols
    add_power_symbol(type="vcc", position=(100, 80))
    add_power_symbol(type="gnd", position=(100, 140))

    # Save
    result = save_schematic(path="/tmp/divider_test.kicad_sch")
    assert result.success == True

    # Verify file exists and is valid
    assert Path(result.path).exists()

    # Load back and verify
    loaded = load_schematic(path=result.path)
    assert loaded.component_count == 4  # R1, R2, VCC, GND
```

### 9.3 Contract Tests (MCP Protocol Compliance)

```python
# tests/mcp_server/test_protocol.py
from mcp.client import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def test_server_capabilities():
    """Test server advertises correct capabilities."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Check capabilities
            assert "tools" in session.server_capabilities
            assert "resources" in session.server_capabilities
            assert "prompts" in session.server_capabilities

async def test_tool_schema_validity():
    """Test all tools have valid schemas."""
    # Connect to server and list tools
    tools = await session.list_tools()

    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool

        # Validate schema is valid JSON Schema
        jsonschema.validate(instance={}, schema=tool["inputSchema"])
```

### 9.4 Load Tests

```python
# tests/mcp_server/test_performance.py
import asyncio
import time

async def test_concurrent_tool_calls():
    """Test server handles 100 concurrent tool calls."""
    start = time.time()

    tasks = [
        list_components() for _ in range(100)
    ]

    results = await asyncio.gather(*tasks)

    duration = time.time() - start

    assert all(r is not None for r in results)
    assert duration < 5.0  # 100 calls in <5s

    # Calculate throughput
    throughput = len(tasks) / duration
    assert throughput > 20  # >20 req/s
```

### 9.5 Property-Based Tests

```python
# tests/mcp_server/test_properties.py
from hypothesis import given, strategies as st

@given(
    value=st.text(min_size=1, max_size=20),
    position=st.tuples(
        st.floats(min_value=0, max_value=500),
        st.floats(min_value=0, max_value=500)
    )
)
def test_add_component_roundtrip(value, position):
    """Property: Adding component then listing should return same data."""
    result = add_component(
        lib_id="Device:R",
        value=value,
        position=position
    )

    components = list_components()

    assert any(
        c.reference == result.reference and
        c.value == result.value and
        c.position == result.position
        for c in components
    )
```

---

## 10. Documentation Plan

### 10.1 User Documentation

| Document | Audience | Content |
|----------|----------|---------|
| **README.md** | All users | Overview, installation, quick start, MCP badge |
| **MCP_SERVER.md** | MCP users | Comprehensive guide, Claude Desktop setup, all tools |
| **MCP_TOOLS.md** | Reference | Complete tool API reference with examples |
| **MCP_EXAMPLES.md** | Learners | Step-by-step examples with Claude conversations |

### 10.2 Example Content Structure

#### MCP_SERVER.md Outline

```markdown
# KiCad Schematic API MCP Server

## Overview
- What is MCP?
- Why use this server?
- Key features

## Installation

### Requirements
- Python 3.10+
- kicad-sch-api 0.5.0+

### Install
```bash
pip install kicad-sch-api[mcp]
```

### Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "KICAD_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## Quick Start

Open Claude Desktop and try:

> "Create a simple voltage divider circuit with 10k and 1k resistors"

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KICAD_MCP_LOG_LEVEL` | `INFO` | Logging level |
| ... | ... | ... |

## Tool Reference

### Schematic Management

#### create_schematic
Creates a new blank schematic...

[Full tool documentation]

## Troubleshooting

### Common Issues
...

## Advanced Usage
...
```

### 10.3 Example Conversation Files

```markdown
# Example: Creating a Voltage Divider

## Conversation with Claude

**User**: Create a voltage divider circuit with 10k and 1k resistors

**Claude**: I'll create a voltage divider circuit for you. Let me build this step by step:

[Uses create_schematic tool]
[Uses add_component for R1]
[Uses add_component for R2]
[Uses connect_pins]
[Uses add_power_symbol for VCC]
[Uses add_power_symbol for GND]
[Uses save_schematic]

**Claude**: I've created your voltage divider circuit with:
- R1: 10kΩ (top resistor)
- R2: 1kΩ (bottom resistor)
- Connected between VCC and GND
- Output taken from the junction

The circuit is saved to: voltage_divider.kicad_sch

The output voltage will be: Vout = Vin × (R2 / (R1 + R2)) = Vin × 0.091

**User**: Can you add a label to the output node?

**Claude**: Of course! Let me add a label to the output.

[Uses add_label tool]

**Claude**: I've added an "OUTPUT" label at the junction between R1 and R2. The schematic has been updated.
```

---

## 11. Success Metrics & KPIs

### 11.1 Adoption Metrics

| Metric | Target (3 months) | Measurement |
|--------|-------------------|-------------|
| **Downloads** | 500+ | PyPI stats |
| **GitHub Stars** | 50+ | GitHub API |
| **Active Users** | 100+ weekly | Telemetry (opt-in) |
| **Tool Calls** | 5000+ total | Telemetry (opt-in) |

### 11.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Test Coverage** | >90% | pytest-cov |
| **Type Coverage** | 100% | mypy --strict |
| **Error Rate** | <1% | Logs analysis |
| **Documentation Coverage** | 100% tools | Manual audit |

### 11.3 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **P95 Latency (simple)** | <100ms | Prometheus |
| **P99 Latency (complex)** | <500ms | Prometheus |
| **Throughput** | >100 req/s | Load test |
| **Memory Footprint** | <100MB | Process monitor |

### 11.4 Community Metrics

| Metric | Target (6 months) | Measurement |
|--------|-------------------|-------------|
| **Community Contributions** | 5+ PRs | GitHub |
| **Issues Reported** | 10+ | GitHub Issues |
| **Documentation Improvements** | 3+ PRs | GitHub |
| **Example Contributions** | 5+ circuits | User submissions |

---

## 12. Risks & Mitigations

### 12.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **FastMCP breaking changes** | Medium | High | Pin to major version, monitor releases |
| **MCP protocol evolution** | Low | High | Follow official SDK, participate in community |
| **kicad-sch-api bugs** | Medium | Medium | Comprehensive testing, quick fixes |
| **Performance issues** | Low | Medium | Early profiling, optimization phase |
| **STDIO transport limitations** | Low | Low | Plan SSE transport for v2 |

### 12.2 Adoption Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Low discoverability** | Medium | High | SEO optimization, MCP directory listings, social media |
| **Complex setup** | Low | Medium | Clear docs, video tutorials, troubleshooting guide |
| **Learning curve** | Medium | Medium | Comprehensive examples, prompt templates |
| **Competition from existing tools** | Low | Low | Differentiate: focus on creation vs analysis |

### 12.3 Security Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Path traversal attacks** | Low | High | Strict path validation, sandboxing |
| **Malicious schematic files** | Low | Medium | Input validation, file size limits |
| **Credential exposure in logs** | Low | High | Structured logging, no secrets |
| **DOS attacks** | Very Low | Medium | Rate limiting, resource limits |

---

## 13. Open Questions & Decisions Needed

### 13.1 Technical Decisions

| Question | Options | Recommendation | Status |
|----------|---------|----------------|--------|
| Should we support multiple open schematics? | Single / Multiple | Single (simpler v1) | ⏳ Pending |
| Include KiCad CLI integration? | Yes / No | Yes (leverage existing) | ⏳ Pending |
| Support hierarchical sheets in v1? | Yes / No | No (defer to v2) | ⏳ Pending |
| Add telemetry (opt-in)? | Yes / No | Yes (for metrics) | ⏳ Pending |
| Support undo/redo? | Yes / No | No (complex state) | ⏳ Pending |

### 13.2 Product Decisions

| Question | Options | Recommendation | Status |
|----------|---------|----------------|--------|
| Separate MCP server PyPI package? | Separate / Monorepo | Monorepo (easier sync) | ⏳ Pending |
| Charge for commercial use? | Free / Paid | Free (community focus) | ⏳ Pending |
| Build hosted service? | Yes / No | No (self-hosted only v1) | ⏳ Pending |
| Support other CAD tools? | Yes / No | No (KiCad focus) | ⏳ Pending |

---

## 14. Future Roadmap (Post-v1.0)

### v1.1 (Q2 2025)
- SSE transport support for web clients
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

## 15. Appendices

### A. Glossary

| Term | Definition |
|------|------------|
| **MCP** | Model Context Protocol - standard for AI-tool integration |
| **FastMCP** | Python framework for building MCP servers |
| **STDIO** | Standard Input/Output transport mechanism |
| **SSE** | Server-Sent Events - streaming transport |
| **Tool** | MCP function that performs actions (has side effects) |
| **Resource** | MCP function that provides read-only data |
| **Prompt** | MCP conversation template |
| **ERC** | Electrical Rules Check - schematic validation |
| **BOM** | Bill of Materials - component list |
| **Netlist** | List of electrical connections |

### B. References

1. **MCP Specification**: https://modelcontextprotocol.io/
2. **FastMCP Framework**: https://github.com/jlowin/fastmcp
3. **Official Python SDK**: https://github.com/modelcontextprotocol/python-sdk
4. **MCP Best Practices**: https://modelcontextprotocol.info/docs/best-practices/
5. **Production Guide**: https://thinhdanggroup.github.io/mcp-production-ready/
6. **kicad-sch-api**: https://github.com/circuit-synth/kicad-sch-api
7. **Existing KiCad MCP**: https://github.com/lamaalrajih/kicad-mcp

### C. Research Summary

**Key Findings from Research (Nov 2025)**:

1. **FastMCP 2.0 is industry standard** for Python MCP development
2. **Single-responsibility pattern** preferred over monolithic servers
3. **Pydantic models** essential for type safety and schema generation
4. **STDIO transport** required for Claude Desktop integration
5. **Structured logging** (JSON, no stdout) critical for debugging
6. **Multi-layer testing** (unit → integration → contract → load) expected
7. **Defense in depth security** with 5 protective layers
8. **Existing KiCad MCP servers** focus on analysis, not creation
9. **MCP ecosystem growing rapidly** in 2025
10. **Documentation quality** correlates 2× with adoption rates

---

## 16. Sign-Off

### Stakeholders

| Role | Name | Approval Status |
|------|------|-----------------|
| **Product Owner** | [To be assigned] | ⏳ Pending |
| **Tech Lead** | [To be assigned] | ⏳ Pending |
| **Library Maintainer** | [To be assigned] | ⏳ Pending |

### Approval Criteria

- [ ] Technical architecture reviewed and approved
- [ ] Resource requirements identified and committed
- [ ] Timeline feasible and realistic
- [ ] Success metrics agreed upon
- [ ] Risk mitigations acceptable
- [ ] Documentation plan comprehensive

### Next Steps

1. **Review PRD** with core team (1 week)
2. **Incorporate feedback** and finalize (3 days)
3. **Create GitHub Project** with milestones
4. **Begin Phase 1 implementation** (Week 1-2)

---

**Document Status**: 🟡 Draft - Awaiting Review
**Last Updated**: 2025-11-06
**Next Review**: [To be scheduled]
