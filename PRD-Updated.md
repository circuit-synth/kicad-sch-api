# Product Requirements Document: kicad-sch-api (Updated)

## Project Overview

**Product Name**: kicad-sch-api  
**Version**: 1.0.0  
**Target Launch**: Q1 2025  
**Repository**: https://github.com/circuit-synth/kicad-sch-api  

### Executive Summary

kicad-sch-api is a **professional enhancement of kicad-skip** that adds exact format preservation, advanced library sourcing, and **AI agent integration via MCP server**. It builds on kicad-skip's excellent developer experience while adding production-ready features and native AI agent support.

---

## Updated Problem Statement

### Market Reality (Corrected Understanding)

1. **KiCAD Official API is PCB-only**: No official schematic API exists
2. **kicad-skip is the de facto standard** for schematic manipulation
3. **Gap: Professional features missing**: Format preservation, library sourcing, AI integration
4. **Gap: No AI agent interface**: Agents need MCP integration for easy schematic manipulation

### Updated Positioning

**Previous**: "Alternative to kicad-skip"  
**Updated**: "Professional enhancement of kicad-skip + AI agent integration"

---

## Product Vision & Goals (Updated)

### Vision Statement
"Transform kicad-skip into a professional-grade API with AI agent integration, preserving its excellent developer experience while adding production capabilities."

### Primary Goals
1. **Enhanced kicad-skip**: Maintain compatibility while adding professional features
2. **Exact Format Preservation**: Guarantee identical output to KiCAD
3. **AI Agent Integration**: Native MCP server for seamless agent interaction
4. **Advanced Library Features**: Multi-source component intelligence
5. **Production Ready**: Comprehensive testing, validation, error handling

### Success Metrics
- **Compatibility**: 95%+ kicad-skip API compatibility
- **Adoption**: >1000 GitHub stars within 6 months  
- **AI Integration**: Used by >3 AI agent frameworks
- **Format Preservation**: 100% identical to KiCAD output
- **Community**: >10 external contributors

---

## Target Users & Use Cases (Updated)

### Primary Users

#### **AI Agent Developers** (NEW PRIMARY)
- **Need**: Easy schematic manipulation interface for agents
- **Use Cases**: Natural language circuit generation, automated design analysis
- **Requirements**: MCP protocol, robust error handling, comprehensive tool set

#### **Existing kicad-skip Users** 
- **Need**: Enhanced features without breaking existing code
- **Use Cases**: Upgrade path with better reliability and features
- **Requirements**: API compatibility, improved performance, format preservation

#### **EDA Tool Developers**
- **Need**: Professional schematic API for integration
- **Use Cases**: Advanced schematic processing, format-preserving operations
- **Requirements**: Exact output, comprehensive validation, production readiness

#### **Automation Engineers**
- **Need**: Reliable CI/CD schematic processing  
- **Use Cases**: Batch operations, automated testing, format validation
- **Requirements**: Format preservation, robust error handling, performance

---

## Core Architecture (Updated)

### 1. **Enhanced kicad-skip Foundation**

```
kicad_sch_api/
├── core/                        # Enhanced from circuit-synth
│   ├── exact_writer.py         # Format-preserving writer
│   ├── atomic_operations.py    # Safe atomic operations  
│   ├── validation.py           # Comprehensive validation
│   └── performance.py          # Performance monitoring
├── compat/                     # kicad-skip compatibility layer
│   ├── schematic.py           # Enhanced Schematic class
│   ├── symbol.py              # Enhanced Symbol class
│   ├── collections.py         # Enhanced collections
│   └── __init__.py            # kicad-skip compatible imports
├── library/                    # Advanced library features
│   ├── sourcing.py            # Multi-source lookup (DigiKey, SnapEDA)
│   ├── cache.py               # Intelligent symbol caching
│   └── resolver.py            # Symbol resolution with fallbacks
├── mcp/                        # MCP server integration (NEW)
│   ├── server.py              # Python MCP command handlers
│   ├── tools.py               # MCP tool definitions
│   └── bridge.py              # Interface bridge
└── utils/                      # Professional utilities
    ├── backup.py              # Backup/restore
    ├── errors.py              # Enhanced error handling
    └── testing.py             # Test utilities
```

### 2. **MCP Server (NEW MAJOR COMPONENT)**

```
mcp-server/                     # TypeScript MCP server
├── package.json
├── tsconfig.json  
├── src/
│   ├── index.ts               # Main MCP server entry point
│   ├── schematic-tools.ts     # Schematic manipulation tools
│   ├── python-bridge.ts       # Python subprocess management
│   ├── types.ts               # TypeScript definitions
│   └── validation.ts          # Input validation
├── dist/                      # Compiled JavaScript
└── examples/
    ├── claude-config.json     # Claude Desktop integration
    └── workflows/             # Example agent workflows
```

---

## Feature Requirements (Updated)

### **Phase 1: Enhanced kicad-skip (MVP)**

#### **1.1 Compatibility Layer**
- **100% API compatibility** with kicad-skip for basic operations
- **Same import structure**: `import kicad_sch_api as skip` works
- **Preserve REPL experience**: Tab completion, named access, collections
- **Enhanced error handling**: Better error messages, graceful degradation

#### **1.2 Format Preservation (CORE DIFFERENTIATOR)**  
- **Exact S-expression output** matching KiCAD's native format
- **Preserve whitespace/indentation** exactly as KiCAD generates
- **Maintain element ordering** and comment structure
- **UUID handling** with proper generation and preservation
- **Round-trip testing**: load → modify → save → load produces identical results

#### **1.3 Atomic Operations**
- **Safe component operations** with automatic cleanup
- **lib_symbols management**: Auto-add/remove symbol definitions
- **Reference validation**: Ensure unique references, proper formatting
- **Backup/restore**: Automatic backups before modifications
- **Transaction support**: Rollback failed operations

### **Phase 2: AI Agent Integration (MAJOR NEW FEATURE)**

#### **2.1 MCP Server Core**
- **TypeScript MCP server** following Anthropic's MCP specification
- **Python bridge** via subprocess for reliable communication
- **Tool schema validation** with comprehensive input checking
- **Error propagation** with detailed error context for agents
- **Session management** for multi-operation workflows

#### **2.2 Essential MCP Tools**
```typescript
// Core schematic manipulation tools
- load_schematic: Load .kicad_sch files
- save_schematic: Save with format preservation
- add_component: Add components with validation
- update_component: Modify component properties  
- remove_component: Safe component removal
- add_wire: Create wire connections
- connect_components: Connect component pins
- find_components: Search by multiple criteria
- analyze_connections: Electrical connection analysis
- validate_schematic: Comprehensive validation
```

#### **2.3 Advanced MCP Tools**  
```typescript
// Advanced capabilities for agents
- search_component_library: Multi-source component search
- batch_update_components: Bulk operations
- optimize_placement: Automatic component placement
- generate_from_netlist: Import from netlist
- export_netlist: Generate netlists
- design_rule_check: Validate against design rules
```

### **Phase 3: Professional Features**

#### **3.1 Advanced Library Integration** 
- **Multi-source component lookup**: DigiKey API, SnapEDA, local libraries
- **Intelligent caching**: Performance-optimized symbol resolution
- **Fallback mechanisms**: Graceful handling of missing symbols
- **Library validation**: Health checks and integrity validation
- **Symbol metadata**: Extended properties (MPN, datasheet, etc.)

#### **3.2 Performance & Production**
- **Performance monitoring**: Built-in timing and profiling
- **Memory optimization**: Efficient handling of large schematics  
- **Concurrent operations**: Thread-safe operations where applicable
- **Comprehensive logging**: Detailed operation logs for debugging
- **Health monitoring**: System health checks and diagnostics

---

## API Design (Updated for Compatibility)

### **Enhanced kicad-skip Compatible API**

```python
# 100% compatible with existing kicad-skip code
import kicad_sch_api as skip

# Load schematic (enhanced with validation)
sch = skip.Schematic('circuit.kicad_sch')

# Existing kicad-skip interface works unchanged
sch.symbol.R1.property.Value.value = "10k"
sch.symbol.R1.dnp.value = True

# NEW: Enhanced operations with format preservation
sch.save_exact('circuit_modified.kicad_sch')  # Guaranteed exact format

# NEW: Professional features
sch.backup()  # Create backup before modifications
sch.validate()  # Comprehensive validation
with sch.atomic_operation():  # Transaction support
    sch.add_component_exact("Device:R", "R5", "1k", (100, 100))

# NEW: Advanced library features
component = sch.find_component_in_libraries("10k resistor 0603")
sch.symbol.R1.update_from_library_source("digikey")
```

### **MCP Agent Interface**

```typescript
// AI agents use natural language translated to MCP calls
// Agent: "Add a 10k resistor at position 100,100"
await mcp.callTool("add_component", {
  lib_id: "Device:R",
  reference: "R1",
  value: "10k", 
  position: { x: 100, y: 100 },
  properties: {
    footprint: "Resistor_SMD:R_0603_1608Metric"
  }
});

// Agent: "Connect R1 pin 1 to C1 pin 2"
await mcp.callTool("connect_components", {
  from_component: "R1",
  from_pin: "1",
  to_component: "C1", 
  to_pin: "2"
});
```

---

## Updated Questions for Approval

### **Technical Architecture**

#### **1. kicad-skip Integration Strategy**
- **Question**: Should we maintain 100% API compatibility with kicad-skip?
- **Options**:
  - A) 100% compatibility (users can drop-in replace)
  - B) 95% compatibility (minor breaking changes for improvements)
  - C) Compatible import but enhanced API alongside
- **Recommendation**: Option A - 100% compatibility for easy adoption

#### **2. MCP Server Architecture**
- **Question**: Should the MCP server be integrated or standalone?
- **Options**:
  - A) Integrated: Single package with both Python API and MCP server
  - B) Standalone: Separate MCP server package that uses kicad-sch-api
  - C) Optional: MCP server as optional extra install
- **Recommendation**: Option A - Integrated for simplicity

#### **3. Format Preservation Implementation**
- **Question**: How should we implement exact format preservation?
- **Options**:
  - A) Replace kicad-skip's writer with circuit-synth's exact writer
  - B) Add format-preserving save methods alongside existing ones
  - C) Make format preservation configurable (exact vs. standard)
- **Recommendation**: Option B - Add alongside existing for compatibility

### **Feature Scope**

#### **4. kicad-skip Enhancement Level**
- **Question**: How extensively should we enhance kicad-skip's core features?
- **Current plan**: Add exact operations, validation, library features
- **Options**: 
  - A) Minimal enhancements (just format preservation)
  - B) Comprehensive enhancements (validation, library, performance)  
  - C) Modular enhancements (users choose what to enable)
- **Your preference?**

#### **5. MCP Tools Scope for v1.0**
- **Question**: Which MCP tools are essential for initial launch?
- **Core tools**: load, save, add/remove components, basic connections
- **Advanced tools**: library search, batch operations, validation
- **Your priority for v1.0 MCP tools?**

#### **6. Library Integration Depth**
- **Question**: How deep should multi-source library integration go?
- **Options**:
  - A) Basic: Local KiCAD libraries + simple external lookup
  - B) Advanced: Full DigiKey/SnapEDA integration with caching
  - C) Professional: Real-time pricing, availability, alternatives
- **Recommendation**: Start with B, plan for C in v1.1

### **Business Strategy**

#### **7. Relationship with kicad-skip**
- **Question**: How should we position relationship with kicad-skip?
- **Options**:
  - A) "Enhanced version" - collaborative approach
  - B) "Professional alternative" - competitive approach  
  - C) "Compatible extension" - additive approach
- **Recommendation**: Option A - Collaborative enhancement

#### **8. AI Agent Market Priority**
- **Question**: Should AI agent integration be a primary or secondary focus?
- **Market trends**: AI integration is hot, MCP gaining adoption
- **Options**:
  - A) Primary: Market as "AI-first schematic API"
  - B) Secondary: Professional API that also supports agents
  - C) Equal: Dual-purpose professional + AI tool
- **Your vision for market positioning?**

### **Implementation**

#### **9. Development Approach**
- **Question**: Should we fork kicad-skip or build a wrapper?
- **Options**:
  - A) Fork kicad-skip and enhance (full control, compatibility risk)
  - B) Wrapper approach (use kicad-skip as dependency, easier maintenance)
  - C) Hybrid (fork with upstream sync, best of both)
- **Recommendation**: Option B - Wrapper for easier maintenance

#### **10. Testing Strategy**
- **Question**: How should we ensure kicad-skip compatibility?
- **Options**:
  - A) Run kicad-skip test suite against our implementation
  - B) Create compatibility test suite with real schematics  
  - C) Both + format preservation tests
- **Recommendation**: Option C - Comprehensive testing

## Next Steps Upon Approval

1. **Finalize architecture** based on your answers
2. **Set up development environment** with kicad-skip as foundation
3. **Create MCP server skeleton** with basic tools
4. **Implement format preservation** enhancement layer
5. **Add circuit-synth's advanced features** as compatibility extensions

This updated PRD positions kicad-sch-api as the natural evolution of kicad-skip with professional features and native AI agent support - a much stronger market position than being "yet another schematic library."

---

**Document Version**: 2.0  
**Last Updated**: 2025-01-13  
**Major Changes**: Added MCP integration, repositioned as kicad-skip enhancement  
**Status**: Ready for Final Approval