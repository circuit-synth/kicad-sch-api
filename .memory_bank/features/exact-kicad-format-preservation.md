# Product Requirements Document: Exact KiCAD Format Preservation

## Overview

The kicad-sch-api must generate schematic files that match KiCAD's native format exactly, enabling seamless interoperability with KiCAD's schematic editor. The current implementation generates files that are structurally correct but have formatting and syntax differences that prevent proper rendering in KiCAD.

## Problem Statement

**Current State**: Generated schematic files contain:
- Incorrect S-expression formatting (quoted symbols vs unquoted)
- Missing critical component fields (unit, dnp, fields_autoplaced)
- Incomplete symbol definitions (missing pin UUIDs, instances section)
- Wrong symbol naming in lib_symbols section

**Impact**: KiCAD displays a blank schematic with error messages like:
```
Expecting 'input, output, bidirectional, tri_state, passive...' in 'file.kicad_sch', line 68, offset 11
```

## Success Criteria

### Primary Objectives
1. **Exact Format Matching**: Generated `.kicad_sch` files must be byte-for-byte compatible with KiCAD's output
2. **Universal Symbol Support**: Solution must work with any symbol from any KiCAD library
3. **Visual Rendering**: Symbols must display correctly in KiCAD with proper graphics and pins
4. **Round-trip Compatibility**: Load → Modify → Save must preserve format exactly

### Acceptance Tests
- [ ] Single resistor schematic renders correctly in KiCAD
- [ ] Generated file passes KiCAD's internal validation
- [ ] Diff between reference and generated shows only intentional differences (UUID, position, etc.)
- [ ] Solution works with Device:R, Device:C, and other basic components
- [ ] Complex symbols (multi-unit ICs) render correctly

## Technical Requirements

### 1. S-Expression Formatting Rules
- **Pin definitions**: `(pin passive line` NOT `(pin "passive" "line"`
- **Symbol names**: Use full lib_id `"Device:R"` NOT just `"R"`
- **Consistent quoting**: String values quoted, symbols unquoted
- **Exact indentation**: Match KiCAD's tab/space conventions

### 2. Component Structure
Required fields for component symbols:
```
(symbol
    (lib_id "Device:R")
    (at x y rotation)
    (unit 1)                    # Missing
    (exclude_from_sim no)       # Missing  
    (in_bom yes)
    (on_board yes)
    (dnp no)                    # Missing
    (fields_autoplaced yes)     # Missing
    (uuid "component-uuid")
    (property "Reference" "R1"
        (at x y rotation)       # Missing positioning
        (effects ...)           # Missing effects
    )
    (property "Value" "10k" ...) # Missing positioning/effects
    (pin "1" (uuid "pin-uuid"))  # Missing
    (pin "2" (uuid "pin-uuid"))  # Missing
    (instances                   # Missing entire section
        (project "project_name"
            (path "/root-uuid"
                (reference "R1")
                (unit 1)
            )
        )
    )
)
```

### 3. Library Symbol Integration
- **Direct passthrough**: Use actual parsed symbol data from .kicad_sym files
- **No modification**: Preserve exact symbol structure from KiCAD libraries
- **Complete definitions**: Include all symbol units (R_0_1, R_1_1, etc.)

### 4. Schematic Metadata
Required sections:
- `sheet_instances` with proper path structure
- `embedded_fonts no` at root level
- Proper UUID generation and management

## Implementation Strategy

### Phase 1: Fix Symbol Definition Format
1. **Remove format conversion**: Pass raw S-expression data directly from library parser
2. **Fix pin syntax**: Ensure pin types are unquoted symbols
3. **Correct symbol naming**: Use full lib_id in symbol definitions

### Phase 2: Complete Component Structure  
1. **Add missing component fields**: unit, dnp, fields_autoplaced, exclude_from_sim
2. **Implement pin UUIDs**: Generate and assign UUIDs for each component pin
3. **Add instances section**: Create proper project/path/reference structure

### Phase 3: Schematic Metadata
1. **Sheet instances**: Add required sheet_instances section
2. **Root metadata**: Ensure all required root-level fields present
3. **Property positioning**: Calculate proper positioning for all properties

### Phase 4: Validation & Testing
1. **Reference validation**: Test against all reference schematics
2. **KiCAD integration test**: Verify files load/save correctly in KiCAD
3. **Round-trip testing**: Ensure load→modify→save preserves format

## Technical Approach

### Core Principle: Zero Format Translation
The key insight is to **avoid format translation entirely**. Instead:

1. **Parse once**: Read symbol definitions from .kicad_sym files into raw S-expression format
2. **Store raw**: Keep parsed data in original S-expression structure  
3. **Write directly**: Output raw S-expressions without conversion to dictionary format
4. **Minimal modification**: Only modify what's necessary (positions, values, UUIDs)

### Data Flow
```
KiCAD Library (.kicad_sym) 
    ↓ sexpdata.loads()
Raw S-Expression List
    ↓ Store in SymbolDefinition
Cache with Raw Data
    ↓ Direct passthrough
Schematic lib_symbols Section
    ↓ sexpdata.dumps()
Valid KiCAD Schematic (.kicad_sch)
```

## Risk Mitigation

### Format Compatibility Risk
- **Risk**: New KiCAD versions change format
- **Mitigation**: Version-specific format handling, automated testing with multiple KiCAD versions

### Performance Risk  
- **Risk**: Large library files slow down symbol loading
- **Mitigation**: Lazy loading, symbol-specific caching, performance monitoring

### Complexity Risk
- **Risk**: S-expression handling becomes complex and error-prone
- **Mitigation**: Comprehensive test suite, clear separation of concerns, extensive logging

## Dependencies

### External
- **sexpdata**: S-expression parsing library
- **KiCAD 9.0+**: Target format compatibility
- **pytest**: Testing framework

### Internal
- **ExactFormatter**: Must handle raw S-expression data
- **SExpressionParser**: Must preserve original structure
- **SymbolLibraryCache**: Must store raw parsed data

## Success Metrics

### Functionality
- [ ] 100% of reference schematics render correctly in KiCAD
- [ ] Zero format translation errors in test suite
- [ ] Round-trip testing passes for all test cases

### Performance  
- [ ] Symbol loading < 500ms for common libraries
- [ ] Schematic save time < 100ms for simple circuits
- [ ] Memory usage scales linearly with symbol count

### Quality
- [ ] No hardcoded symbol definitions
- [ ] Clean separation between parsing and formatting
- [ ] Comprehensive error handling and validation

## Future Enhancements

1. **Advanced Symbol Features**: Multi-unit symbols, alternate representations
2. **Performance Optimization**: Symbol pre-loading, intelligent caching
3. **Format Validation**: Real-time validation against KiCAD spec
4. **Library Management**: Automatic library discovery, version management

---

*This PRD ensures the kicad-sch-api achieves professional-grade format preservation essential for seamless KiCAD integration.*