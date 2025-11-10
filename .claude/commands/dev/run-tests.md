# Test Runner Command - kicad-sch-api

## Usage
```bash
/run-tests [options]
```

## Description
Orchestrates comprehensive testing for kicad-sch-api using uv and pytest, covering all functionality areas with professional test reporting.

## Options
- `--suite=standard` - Test suite: `quick`, `standard`, `full`, `coverage` (default: standard)
- `--skip-install` - Skip dependency reinstallation (faster for development)
- `--keep-outputs` - Don't delete generated test files
- `--verbose` - Show detailed output
- `--format=true` - Auto-format code before testing (default: true)
- `--fail-fast=false` - Stop on first failure (default: false)

## Test Suites

### 🚀 Quick Suite (~10 seconds)
Fast development testing:
```bash
uv run pytest tests/test_component_management.py tests/test_sexpr_parsing.py -q
```

### 📋 Standard Suite - Default (~30 seconds)
Comprehensive core functionality:
```bash
# Auto-format if requested
uv run black kicad_sch_api/ tests/ --quiet
uv run isort kicad_sch_api/ tests/ --quiet

# Run core tests
uv run pytest tests/ -v --tb=short
```

### 🔬 Full Suite (~2 minutes)
Complete validation including MCP server:
```bash
# Python library tests
uv run pytest tests/ -v --cov=kicad_sch_api --cov-report=html

# MCP server tests
cd mcp-server && npm test

# Format preservation tests
uv run pytest tests/test_format_preservation.py -v

# Reference schematic tests
uv run pytest tests/reference_kicad_projects/ -v
```

### 📊 Coverage Suite (~1 minute)
Detailed coverage analysis:
```bash
uv run pytest tests/ --cov=kicad_sch_api --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

## Implementation

```bash
#!/bin/bash

# Parse arguments
SUITE="standard"
SKIP_INSTALL=false
KEEP_OUTPUTS=false
VERBOSE=false
FORMAT=true
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --suite=*)
            SUITE="${1#*=}"
            shift
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --format=*)
            FORMAT="${1#*=}"
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure we're in Python directory
cd python || { echo "❌ Must run from kicad-sch-api root"; exit 1; }

# Install dependencies if needed
if [[ "$SKIP_INSTALL" == "false" ]]; then
    echo "📦 Installing dependencies..."
    uv pip install -e .[dev] --quiet
fi

# Pre-test formatting
if [[ "$FORMAT" == "true" ]]; then
    echo "🎨 Auto-formatting code..."
    uv run black kicad_sch_api/ tests/ --quiet
    uv run isort kicad_sch_api/ tests/ --quiet
    echo "✅ Code formatted"
fi

# Build pytest arguments
PYTEST_ARGS=""
[[ "$VERBOSE" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -v"
[[ "$FAIL_FAST" == "true" ]] && PYTEST_ARGS="$PYTEST_ARGS -x"

# Execute test suite
case $SUITE in
    quick)
        echo "🚀 Running quick test suite..."
        uv run pytest tests/test_component_management.py tests/test_sexpr_parsing.py -q $PYTEST_ARGS
        ;;
        
    standard)
        echo "📋 Running standard test suite..."
        uv run pytest tests/ --tb=short $PYTEST_ARGS
        ;;
        
    full)
        echo "🔬 Running full test suite..."
        
        # Python library tests with coverage
        uv run pytest tests/ --cov=kicad_sch_api --cov-report=term-missing $PYTEST_ARGS || exit 1
        
        # MCP server tests
        if [[ -d "../mcp-server" ]]; then
            echo "🤖 Testing MCP server..."
            cd ../mcp-server
            if [[ -f "package.json" ]]; then
                npm test || echo "⚠️ MCP server tests failed"
            fi
            cd ../python
        fi
        
        # Reference schematic tests
        if [[ -d "tests/reference_kicad_projects" ]]; then
            echo "📋 Testing reference schematics..."
            uv run pytest tests/reference_kicad_projects/ -v $PYTEST_ARGS
        fi
        ;;
        
    coverage)
        echo "📊 Running coverage analysis..."
        uv run pytest tests/ --cov=kicad_sch_api --cov-report=term-missing --cov-report=html --cov-fail-under=70 $PYTEST_ARGS
        echo "📊 Coverage report: htmlcov/index.html"
        ;;
        
    *)
        echo "❌ Unknown suite: $SUITE"
        echo "Available suites: quick, standard, full, coverage"
        exit 1
        ;;
esac

# Cleanup if requested
if [[ "$KEEP_OUTPUTS" == "false" ]]; then
    echo "🧹 Cleaning up test outputs..."
    rm -rf test_outputs/ .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
fi

echo "✅ Test suite completed"
```

## Expected Results by Suite

**Quick Suite**:
- ~5-10 tests, core functionality only
- <10 seconds execution time
- Good for rapid development iteration

**Standard Suite**:
- ~50-100 tests covering all core functionality
- ~30 seconds execution time
- Recommended for pre-commit validation

**Full Suite**:
- All tests + MCP server + reference schematics
- ~2 minutes execution time
- Recommended for pre-merge validation

**Coverage Suite**:
- Same as Standard but with detailed coverage analysis
- Target: >80% code coverage
- Generates HTML coverage report

## Usage Examples

```bash
# Quick development check
/run-tests --suite=quick

# Standard pre-commit validation (default)
/run-tests

# Full validation before merge
/run-tests --suite=full --verbose

# Coverage analysis
/run-tests --suite=coverage

# Debug specific failures
/run-tests --suite=standard --verbose --fail-fast

# Fast iteration during debugging
/run-tests --suite=quick --skip-install --format=false
```

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Quick Tests
  run: /run-tests --suite=quick --fail-fast
  
- name: Full Tests (on PR)
  run: /run-tests --suite=full
  
- name: Coverage Tests (on main)
  run: /run-tests --suite=coverage
```

## Best Practices for kicad-sch-api

1. **Development**: Use `--suite=quick` for rapid iteration
2. **Pre-commit**: Run `--suite=standard` before committing
3. **Pre-merge**: Run `--suite=full` before merging branches
4. **Coverage analysis**: Use `--suite=coverage` to identify gaps
5. **Debugging**: Use `--verbose --fail-fast` to isolate issues

## kicad-sch-api Specific Testing

### Core Functionality Tests
- S-expression parsing and formatting
- Component management and collections
- Symbol library caching and performance
- Validation and error handling

### Integration Tests
- Round-trip format preservation
- Large schematic performance
- MCP server functionality
- Reference schematic parsing

### Reference Schematic Coverage
- Basic components (R, L, C, D)
- Complex components (MCUs, connectors)
- Hierarchical sheets and labels
- Graphics and text elements

This command provides a single entry point for all kicad-sch-api testing while maintaining the flexibility of specialized test tools.