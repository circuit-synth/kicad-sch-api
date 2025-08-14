# Product Requirements Document: kicad-sch-api

## Project Overview

**Product Name**: kicad-sch-api  
**Version**: 1.0.0  
**Target Launch**: Q1 2025  
**Repository**: https://github.com/circuit-synth/kicad-sch-api  

### Executive Summary

kicad-sch-api is the definitive Python library for programmatic manipulation of KiCAD schematic files (.kicad_sch) with **exact format preservation**. Unlike existing solutions, it guarantees that output files maintain identical formatting to KiCAD's native output, making it suitable for production environments and automated workflows.

---

## Problem Statement

### Current Market Gaps

1. **kicad-skip limitations**:
   - No format preservation guarantee
   - Basic component management
   - Limited production readiness

2. **KiCAD Official API limitations**:
   - Requires running KiCAD instance
   - Not suitable for CI/CD or server environments
   - Complex setup for automated workflows

3. **Manual schematic editing**:
   - Time-consuming and error-prone
   - No automation capabilities
   - Difficult to integrate with engineering workflows

### Target Pain Points

- **EDA Tool Developers**: Need reliable schematic file manipulation
- **Automation Engineers**: Require batch processing without GUI dependencies
- **CI/CD Systems**: Need deterministic, format-preserving operations
- **Engineering Teams**: Want programmatic schematic generation and modification

---

## Product Vision & Goals

### Vision Statement
"Enable seamless programmatic control of KiCAD schematics with professional-grade reliability and exact format preservation."

### Primary Goals
1. **Format Preservation**: 100% identical output to native KiCAD
2. **Professional API**: Clean, intuitive interface for external developers
3. **Production Ready**: Robust error handling, validation, and testing
4. **Comprehensive Coverage**: Support all major schematic operations
5. **Zero Dependencies**: No KiCAD runtime requirements

### Success Metrics
- **Technical**: 100% format preservation across all operations
- **Adoption**: >1000 GitHub stars within 6 months
- **Community**: >10 external contributors within 12 months
- **Commercial**: >5 enterprise inquiries for support/integration

---

## Target Users & Use Cases

### Primary Users

#### **EDA Tool Developers**
- **Need**: Integrate schematic manipulation into their tools
- **Use Cases**: Import/export, format conversion, batch processing
- **Requirements**: Reliable API, comprehensive documentation, format preservation

#### **Automation Engineers** 
- **Need**: Automated schematic generation and modification
- **Use Cases**: CI/CD integration, batch updates, testing frameworks
- **Requirements**: Server compatibility, scriptable interface, error handling

#### **Research/Academic**
- **Need**: Programmatic circuit generation for studies
- **Use Cases**: Algorithm testing, design space exploration, educational tools
- **Requirements**: Easy installation, clear examples, Python integration

### Secondary Users

#### **Electronics Engineers**
- **Need**: Custom schematic processing tools
- **Use Cases**: Design rule checking, component updates, documentation
- **Requirements**: User-friendly API, good examples, reliable operation

#### **Open Source Projects**
- **Need**: KiCAD integration in their tools
- **Use Cases**: Library integration, format support, workflow automation
- **Requirements**: Clean licensing, stable API, good documentation

---

## Core Features & Requirements

### 1. **Schematic File Operations** (MVP)

#### File I/O
- **Load schematic** (.kicad_sch files)
- **Save schematic** with exact format preservation
- **Validate schematic** syntax and structure
- **Backup/restore** functionality with automatic backups

#### Format Preservation
- **Exact S-expression formatting** matching KiCAD output
- **Preserve whitespace** and indentation
- **Maintain comment structure** and ordering
- **UUID handling** with proper generation and preservation

### 2. **Component Management** (MVP)

#### Component Operations
- **Add components** with library ID, reference, value, position
- **Remove components** by reference with cleanup
- **Update components** (properties, position, rotation, footprint)
- **Search components** by reference, value, position, properties

#### Property Management
- **Standard properties** (Reference, Value, Footprint, Datasheet)
- **Custom properties** (MPN, Manufacturer, etc.)
- **Property validation** and type checking
- **Batch property updates** across multiple components

### 3. **Connection Management** (MVP)

#### Wire Operations
- **Add wires** between points or pins
- **Remove wires** with connection cleanup  
- **Update wire** routing and positions
- **Validate connections** for electrical correctness

#### Net Management
- **Net discovery** and analysis
- **Label management** (local labels, global labels)
- **Junction management** for multi-wire connections
- **Connection tracing** and validation

### 4. **Symbol and Library Management** (v1.1)

#### Symbol Operations
- **Symbol lookup** from KiCAD libraries
- **Symbol validation** and pin mapping
- **Custom symbol** import and export
- **Symbol caching** for performance

#### Library Integration
- **Local library** scanning and indexing
- **Standard library** integration (Device, Connector, etc.)
- **Symbol resolution** with fallback mechanisms
- **Library validation** and health checks

### 5. **Advanced Operations** (v1.2)

#### Schematic Generation
- **From netlist** import and conversion
- **Template-based** generation
- **Hierarchical schematic** support
- **Multi-sheet** management

#### Design Rule Checking
- **Basic validation** (dangling pins, duplicates)
- **Electrical rules** checking
- **Custom rule** definition and validation
- **Violation reporting** with locations

---

## Technical Architecture

### Core Components

#### **1. S-Expression Engine**
```
kicad_sch_api/
├── core/
│   ├── sexpr_parser.py      # S-expression parsing
│   ├── sexpr_writer.py      # Format-preserving writer
│   ├── validator.py         # File validation
│   └── types.py             # Core data types
```

#### **2. Schematic Operations**
```
├── schematic/
│   ├── document.py          # Main schematic class
│   ├── component_manager.py # Component operations
│   ├── connection_manager.py# Wire/net operations  
│   └── property_manager.py  # Property handling
```

#### **3. Symbol Management**
```
├── symbols/
│   ├── library.py           # Symbol library interface
│   ├── cache.py             # Symbol caching
│   └── resolver.py          # Symbol resolution
```

#### **4. Utilities**
```
├── utils/
│   ├── backup.py            # Backup/restore
│   ├── geometry.py          # Position calculations
│   └── validation.py       # Input validation
```

### Key Design Principles

1. **Exact Format Preservation**: Core differentiator from other libraries
2. **Immutable Operations**: Create new objects rather than modifying in-place
3. **Comprehensive Validation**: Validate all inputs and operations
4. **Error Recovery**: Graceful handling with detailed error messages
5. **Performance**: Optimize for both single operations and batch processing

---

## API Design

### High-Level API Example

```python
import kicad_sch_api as ksa

# Load schematic
schematic = ksa.load_schematic("circuit.kicad_sch")

# Add component
resistor = schematic.add_component(
    lib_id="Device:R",
    reference="R1", 
    value="10k",
    position=(100, 100)
)

# Update properties
resistor.set_property("Footprint", "Resistor_SMD:R_0603_1608Metric")
resistor.set_property("MPN", "RC0603FR-0710KL")

# Add connection
schematic.add_wire(
    start=resistor.pin("1"),
    end=(150, 100)
)

# Save with format preservation
schematic.save("circuit_modified.kicad_sch")
```

### Component Management API

```python
# Component operations
component = schematic.get_component("R1")
components = schematic.find_components(value_pattern="10k*")
schematic.remove_component("R1")

# Batch operations  
for comp in schematic.components:
    if comp.value.startswith("10k"):
        comp.set_property("Tolerance", "1%")
```

### Connection API

```python
# Wire operations
wire = schematic.add_wire(start=(100, 100), end=(200, 100))
schematic.remove_wire(wire)

# Net analysis
nets = schematic.get_nets()
net = schematic.get_net_by_name("VCC")
connected_components = net.get_connected_components()
```

---

## Quality & Testing Strategy

### Testing Requirements

#### **Unit Tests** (>95% coverage)
- All core functions and methods
- Error handling and edge cases
- Format preservation validation
- Performance regression tests

#### **Integration Tests**
- End-to-end workflows
- Real schematic file processing
- Cross-platform compatibility
- Memory usage validation

#### **Format Preservation Tests**
- Byte-level comparison with KiCAD output
- Round-trip testing (load → modify → save → load)
- Complex schematic validation
- Edge case formatting preservation

### Quality Metrics

- **Code Coverage**: >95% line coverage
- **Performance**: <100ms for typical operations
- **Memory**: <50MB for large schematics
- **Format Preservation**: 100% identical to KiCAD

---

## Documentation Requirements

### User Documentation

#### **API Reference**
- Complete function/method documentation
- Parameter descriptions and types
- Return value specifications
- Error condition documentation

#### **User Guide**
- Getting started tutorial
- Common use case examples
- Best practices guide
- Troubleshooting section

#### **Examples**
- Basic operations walkthrough
- Advanced use cases
- Integration examples
- Performance optimization guide

### Developer Documentation

#### **Architecture Guide**
- Component overview
- Data flow diagrams
- Extension points
- Contributing guidelines

#### **Format Specification**
- KiCAD schematic format details
- S-expression structure
- Format preservation requirements
- Validation rules

---

## Licensing & Distribution

### License Strategy
- **MIT License**: Maximum flexibility for commercial and open source use
- **Clean IP**: All code original or properly attributed
- **Contribution License**: CLA for external contributors

### Distribution
- **PyPI Package**: Primary distribution method
- **GitHub Releases**: Tagged releases with changelog
- **Docker Images**: For CI/CD environments
- **Documentation Site**: Professional documentation hosting

---

## Project Timeline & Milestones

### Phase 1: Core Foundation (Weeks 1-4)
- [ ] S-expression parser with format preservation
- [ ] Basic schematic loading/saving
- [ ] Core data types and validation
- [ ] Initial test suite setup

### Phase 2: Component Management (Weeks 5-8)  
- [ ] Component add/remove/update operations
- [ ] Property management system
- [ ] Component search and filtering
- [ ] Symbol library integration

### Phase 3: Connection System (Weeks 9-12)
- [ ] Wire management operations
- [ ] Net discovery and analysis
- [ ] Label and junction handling
- [ ] Connection validation

### Phase 4: Polish & Release (Weeks 13-16)
- [ ] Comprehensive testing and validation
- [ ] Documentation completion
- [ ] Performance optimization
- [ ] Package preparation and release

---

## Questions for Approval

### **Technical Architecture Questions**

#### **1. API Design Philosophy**
- **Question**: Should the API be functional (immutable operations) or object-oriented (mutable objects)?
- **Options**: 
  - A) Functional: `new_schematic = add_component(schematic, component_spec)`
  - B) Object-oriented: `schematic.add_component(component_spec)`
  - C) Hybrid: Support both styles
- **Recommendation**: Object-oriented for ease of use, but with immutable core operations
I'll defer to your judgement. This library and api and mcp server will be used for python scripting or use by llm agents
#### **2. Error Handling Strategy**  
- **Question**: How should the library handle errors and validation failures?
- **Options**:
  - A) Exceptions for all errors
  - B) Return Result objects with success/failure
  - C) Hybrid approach based on error severity
- **Recommendation**: Exceptions for programming errors, Result objects for validation
recommendation is good
#### **3. Symbol Library Integration**
- **Question**: How should we handle symbol library dependencies?
- **Options**:
  - A) Bundle common symbols with the library
  - B) Require users to provide library paths
  - C) Auto-discover from KiCAD installation
  - D) Download symbols on-demand from repositories
- **Recommendation**: Auto-discovery with fallback to bundled essentials
auto discovery, user must provide paths if we can't find them
### **Feature Scope Questions**

#### **4. Version 1.0 Feature Set**
- **Question**: Which features are essential for v1.0 launch?
- **Current MVP**: File I/O, component management, basic connections
- **Additional candidates**: Symbol library integration, design rule checking, hierarchical schematics
- **Your priority ranking?**
pull out all the logic we can from circuit-synth to this new repo

#### **5. Hierarchical Schematic Support**
- **Question**: Should v1.0 include hierarchical schematic support?
- **Complexity**: Significantly increases implementation complexity
- **Market demand**: Important for professional users
- **Recommendation**: Include in v1.1 rather than v1.0
There should be no added complexity since this library just manipulates the files. Adding hierarhcical sheets is just another component to place (might need to update kicad_pro too)


#### **6. Performance vs. Memory Trade-offs**
- **Question**: Should we optimize for speed or memory usage?
- **Use cases**: Large schematics vs. batch processing
- **Options**: In-memory caching vs. lazy loading
- **Your preference?**
Optimize for speed

### **Business Strategy Questions**  

#### **7. Commercial vs. Open Source Balance**
- **Question**: Should any features be reserved for commercial licensing?
- **Options**:
  - A) Fully open source
  - B) Basic open source, advanced features commercial
  - C) Open source library, commercial support/services
- **Recommendation**: Fully open source to maximize adoption
Fully open source

#### **8. Integration with Circuit-Synth**
- **Question**: How tightly should kicad-sch-api integrate with circuit-synth?
- **Options**:
  - A) Completely independent (circuit-synth uses as dependency)
  - B) Shared utilities but separate APIs
  - C) Deep integration with circuit-synth features
- **Recommendation**: Completely independent for maximum reusability
A, completely independent

#### **9. Backward Compatibility**
- **Question**: Should we support older KiCAD schematic formats?
- **KiCAD versions**: v5, v6, v7, v8, v9+
- **Complexity**: Each version has format differences
- **Market need**: Legacy file support vs. current format focus
- **Your target KiCAD versions?**
only kicad 9, we might let users reference old libraries like the digikey kicad library becuase kicad has a built in tool to convert them to the new format

### **Implementation Questions**

#### **10. Testing Strategy**
- **Question**: What's your preference for testing approach?
- **Options**:
  - A) Unit tests + integration tests with real files
  - B) Property-based testing with generated schematics
  - C) Comparison testing against KiCAD's native output
  - D) All of the above
- **Recommendation**: All approaches for comprehensive coverage
All

#### **11. Dependencies**
- **Question**: What external dependencies are acceptable?
- **Current needs**: S-expression parsing, UUID generation, file operations
- **Options**:
  - A) Minimal dependencies (stdlib only)
  - B) Proven libraries (sexpdata, click, etc.)
  - C) Modern libraries with better features
- **Your preference for dependency management?**
What libraries do we use now?  Let's continue with those

#### **12. Performance Requirements**
- **Question**: What are your performance expectations?
- **Typical operations**: Load 1000-component schematic, add component, save
- **Target times**: <100ms total? <1s? <10s?
- **Memory limits**: 50MB? 500MB? No limit?
- **Your performance requirements?**
no idea
---

## Next Steps

### Upon PRD Approval
1. **Create initial project structure** in kicad-sch-api repository
2. **Set up development environment** (testing, CI/CD, documentation)
3. **Begin Phase 1 implementation** with core S-expression handling
4. **Establish contribution guidelines** and issue templates

### Feedback Request
Please review this PRD and provide:
1. **Answers to the questions above**
2. **Any missing requirements** or use cases
3. **Priority adjustments** for features or timeline
4. **Additional concerns** or considerations

This PRD will guide the development and ensure we build exactly what you envision for the kicad-sch-api project.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-13  
**Author**: Claude (Circuit-Synth Analysis)  
**Status**: Awaiting Approval