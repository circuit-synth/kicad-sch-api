# Product Context - kicad-sch-api

## Project Overview

**kicad-sch-api** is a professional-grade Python library for programmatic manipulation of KiCAD schematic files (.kicad_sch) with a focus on exact format preservation and AI agent integration.

## Core Value Proposition

1. **Exact Format Preservation**: Unlike existing solutions, maintains KiCAD's exact file formatting, ensuring compatibility with KiCAD workflows
2. **Performance Optimization**: Fast bulk operations, symbol caching, and indexed lookups for large schematics  
3. **AI-Ready Integration**: Native MCP (Model Context Protocol) server for seamless AI agent workflows
4. **Professional API Design**: Modern, object-oriented interface that abstracts complex S-expression manipulation

## Target Users

### Primary Users
- **Circuit Design Engineers**: Automating repetitive schematic tasks, batch component updates
- **EDA Tool Developers**: Building higher-level design automation tools
- **AI/Automation Engineers**: Creating intelligent design assistants and verification tools

### Secondary Users  
- **Hardware Startups**: Streamlining design iteration and component management
- **Educational Institutions**: Teaching automated EDA workflows
- **PCB Service Providers**: Batch processing customer designs

## Key Differentiators

### vs Other Solutions
- **Enhanced API**: Object-oriented design with modern Python patterns
- **Format Preservation**: Exact output matching KiCAD native format
- **Performance**: Optimized for large schematics and bulk operations
- **AI Integration**: Native MCP server for agent workflows

### vs Manual KiCAD Usage
- **Automation**: Bulk operations that would take hours manually
- **Consistency**: Programmatic validation and standardization
- **Integration**: Part of larger automated design flows

## Architecture Highlights

```
Core Library (Python)     MCP Server (TypeScript)     AI Agents
       ↓                        ↓                        ↓
   Schematic API  ←→  Model Context Protocol  ←→  Claude/GPT/etc
       ↓
S-expression Parser (sexpdata library)
       ↓  
   KiCAD Files (.kicad_sch)
```

## Success Metrics

### Technical
- **Format Fidelity**: 100% round-trip compatibility with KiCAD
- **Performance**: Handle 1000+ component schematics efficiently
- **API Coverage**: Support for all major schematic elements

### Adoption
- **PyPI Downloads**: Growing usage in automation workflows
- **Community Contributions**: Active developer ecosystem
- **Integration Examples**: Real-world usage patterns

## Current Status

- ✅ **Core Library**: Professional S-expression parsing and manipulation
- ✅ **Component Management**: Add, modify, delete components with properties
- ✅ **Format Preservation**: Exact KiCAD compatibility maintained
- ✅ **Testing Infrastructure**: Comprehensive test coverage with reference schematics
- 🚧 **MCP Server**: TypeScript implementation for AI integration
- 🚧 **Performance Optimization**: Symbol caching and bulk operations
- ⏳ **Advanced Features**: Hierarchical sheets, complex routing