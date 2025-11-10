# Dead Code Analysis Command - kicad-sch-api

## Usage
```
/dead-code-analysis [target-script]
```

## Description
Performs comprehensive dead code analysis for kicad-sch-api by running ALL functionality and observing which functions are actually called. This provides accurate utilization metrics by exercising:

1. **Core Schematic Operations** - Load, save, component management, validation
2. **S-Expression Parsing** - All parsing and formatting functionality  
3. **Component Collections** - Filtering, bulk operations, indexing
4. **Symbol Library Management** - Caching, discovery, multi-source lookup
5. **MCP Server Integration** - All MCP tools and Python bridge
6. **Validation Systems** - Error collection, comprehensive validation
7. **Format Preservation** - Round-trip testing, exact output matching
8. **Performance Systems** - Caching, optimization, benchmarking

## Parameters
- `target-script` (optional): Path to script to run for function call analysis. Defaults to comprehensive test suite.
- `--comprehensive`: Runs full system functionality test (default behavior)

## Output Files
- `function_calls.log`: Raw debug output from script execution
- `unique_function_calls.txt`: List of unique functions that were called
- `Dead_Code_Analysis_Report.md`: Comprehensive analysis report
- `*.backup`: Backup files for all instrumented source files

## Examples
```bash
# Analyze dead code using comprehensive test suite
/dead-code-analysis

# Analyze using specific test script
/dead-code-analysis tests/test_comprehensive_operations.py

# Analyze using MCP server test
/dead-code-analysis tests/test_mcp_integration.py
```

## Implementation for kicad-sch-api
The command performs the following automated steps:

### 1. Function Instrumentation
- Scans all Python files in `kicad_sch_api/`
- Adds `logging.debug(f"CALLED: {function_name} in {file_path}")` to every function
- Creates backup files (`.backup`) before modification
- Preserves existing function logic and formatting

### 2. Comprehensive Testing
- Runs test scripts covering all major functionality areas
- Captures function calls during real usage scenarios
- Tests both Python API and MCP server integration

### 3. Analysis & Reporting
- Extracts unique function calls from execution log
- Compares against all instrumented functions
- Groups suspected dead code by module
- Generates comprehensive markdown report

## kicad-sch-api Test Coverage Areas

### Core Library Testing
```python
# test_comprehensive_kicad_sch_api.py
import kicad_sch_api as ksa

def test_core_schematic_operations():
    """Test all core schematic functionality"""
    
    # File operations
    sch = ksa.create_schematic("Dead Code Test")
    
    # Component management
    components = []
    for i in range(20):
        comp = sch.components.add(f"Device:R", f"R{i+1}", f"{i+1}k", (i*10, 50))
        comp.set_property("MPN", f"RC0603FR-07{i+1}0KL")
        components.append(comp)
    
    # Filtering and search
    resistors = sch.components.filter(lib_id="Device:R")
    high_value = sch.components.filter(value_pattern="k")
    in_area = sch.components.in_area(0, 40, 100, 60)
    
    # Bulk operations
    sch.components.bulk_update(
        criteria={'lib_id': 'Device:R'},
        updates={'properties': {'Tolerance': '1%'}}
    )
    
    # Validation
    issues = sch.validate()
    
    # Performance stats
    stats = sch.get_performance_stats()
    
    return sch

def test_symbol_library_comprehensive():
    """Test all symbol library functionality"""
    from kicad_sch_api.library.cache import get_symbol_cache
    
    cache = get_symbol_cache()
    
    # Library discovery
    discovered = cache.discover_libraries()
    
    # Symbol search
    symbols = cache.search_symbols("resistor", limit=10)
    
    # Performance metrics
    perf_stats = cache.get_performance_stats()
    
    # Library management
    cache.add_library_path("/some/test/path.kicad_sym")
    
    return cache

def test_parser_and_formatter():
    """Test all parsing and formatting functionality"""
    from kicad_sch_api.core.parser import SExpressionParser
    from kicad_sch_api.core.formatter import ExactFormatter
    
    parser = SExpressionParser(preserve_format=True)
    formatter = ExactFormatter()
    
    # Test parsing
    test_content = '''(kicad_sch (version 20250114) 
        (symbol (lib_id "Device:R") (at 100 50 0)
            (property "Reference" "R1" (at 100 46.99 0))
        ))'''
    
    parsed = parser.parse_string(test_content)
    formatted = formatter.format(parsed)
    
    return parser, formatter

def test_validation_comprehensive():
    """Test all validation functionality"""
    from kicad_sch_api.utils.validation import SchematicValidator, validate_schematic_file
    
    validator = SchematicValidator(strict=True)
    
    # Test all validation methods
    valid_ref = validator.validate_reference("R1")
    invalid_ref = validator.validate_reference("1R")
    valid_lib = validator.validate_lib_id("Device:R") 
    invalid_lib = validator.validate_lib_id("InvalidFormat")
    
    return validator
```

### MCP Server Testing
```python
def test_mcp_server_comprehensive():
    """Test all MCP server functionality"""
    from kicad_sch_api.mcp.server import MCPInterface
    
    mcp = MCPInterface()
    
    # Test all MCP commands
    commands = [
        ('ping', {}),
        ('create_schematic', {'name': 'MCP Test'}),
        ('add_component', {
            'lib_id': 'Device:R', 
            'reference': 'R1', 
            'value': '10k',
            'position': {'x': 100, 'y': 50}
        }),
        ('get_component', {'reference': 'R1'}),
        ('find_components', {'lib_id': 'Device:R'}),
        ('validate_schematic', {}),
        ('get_schematic_summary', {}),
    ]
    
    for command, params in commands:
        try:
            result = mcp.handlers[command](params)
            print(f"✅ MCP command: {command}")
        except Exception as e:
            print(f"⚠️ MCP command {command} failed: {e}")
    
    return mcp
```

## Expected Results for kicad-sch-api

With comprehensive testing, expect these utilization rates:
- **Core schematic operations**: 85-95%
- **Component management**: 80-90%
- **S-expression parsing**: 70-85%
- **Symbol library caching**: 60-75%
- **MCP server integration**: 70-85%
- **Validation systems**: 60-80%
- **Utility functions**: 40-60%

## Target Test Scripts

1. **test_comprehensive_kicad_sch_api.py** - Core API functionality
2. **test_mcp_server_integration.py** - MCP server and tools
3. **test_performance_benchmarks.py** - Large schematic handling
4. **test_format_preservation.py** - Round-trip validation
5. **test_reference_schematics.py** - All reference project parsing

## Safety Notes
- Creates backup files before modifying source code
- Only adds logging statements, doesn't change logic
- Can be run multiple times safely
- Restore backups: `find . -name "*.backup" | while read backup; do mv "$backup" "${backup%.backup}"; done`

## Implementation Path
```bash
# From kicad-sch-api/python directory
python .claude/commands/dev/dead-code-analysis.py [target-script]
```

This analysis will help identify which parts of the transferred circuit-synth logic are actually being used vs. which can be safely removed or refactored.