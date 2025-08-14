# Product Context - kicad-sch-api

## Project Overview

**kicad-sch-api** is a professional Python library for programmatic manipulation of KiCAD schematic files (.kicad_sch) with exact format preservation and enhanced object model.

## Core Value Proposition

- **File-Based Operations**: Manipulate schematics without running KiCAD
- **Enhanced API**: Intuitive object model vs verbose existing solutions  
- **Format Preservation**: Exact compatibility with KiCAD's native output
- **Professional Quality**: Comprehensive validation, error handling, testing
- **Symbol Management**: Advanced library caching and sourcing integration

## Target Users

- **Circuit Design Engineers**: Professional schematic automation
- **EDA Tool Developers**: Building on top of KiCAD workflows
- **AI Agent Developers**: Programmatic circuit generation and modification
- **Automation Engineers**: CI/CD pipelines for circuit design

## Key Differentiators

### vs kicad-skip
- Enhanced object model with convenience methods
- O(1) component lookup vs linear search
- Bulk operations support
- Professional error handling and validation

### vs KiCAD Python API
- Works without running KiCAD instance
- File-based operations for CI/CD compatibility
- Enhanced performance with symbol caching

## Technical Architecture

- **Core Engine**: S-expression parsing with sexpdata
- **Object Model**: Component, Schematic, ComponentCollection classes
- **Symbol Cache**: Lazy-loaded library management  
- **Validation**: Comprehensive error checking and reporting
- **Format Preservation**: Custom formatter maintaining KiCAD compatibility

## Dependencies

- **sexpdata**: S-expression parsing foundation
- **typing-extensions**: Modern type hints
- **pytest**: Testing framework

## Current Status

- ✅ v0.0.1 released on PyPI
- ✅ Core functionality complete
- ✅ Professional packaging
- ✅ Comprehensive test suite
- 🔄 Ongoing: Performance optimization, advanced features