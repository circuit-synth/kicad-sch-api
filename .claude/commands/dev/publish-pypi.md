# Publish to PyPI Command - kicad-sch-api

## Usage
```bash
/publish-pypi [--test-only]
```

## Description
Publishes kicad-sch-api to PyPI with comprehensive validation, testing, and professional release process.

## Parameters
- `--test-only`: Publish to Test PyPI only (for validation)
- `--check-only`: Run all checks without publishing
- `--force`: Skip some validation checks (use with caution)

## Pre-Release Checklist

### 1. Version and Documentation
- [ ] **Version bumped** in pyproject.toml
- [ ] **CHANGELOG.md updated** with release notes
- [ ] **README.md reviewed** for accuracy
- [ ] **Documentation complete** for new features

### 2. Code Quality
- [ ] **All tests pass**: `uv run pytest tests/ -v`
- [ ] **Code formatted**: `uv run black kicad_sch_api/ tests/`
- [ ] **Imports sorted**: `uv run isort kicad_sch_api/ tests/`
- [ ] **Type checking**: `uv run mypy kicad_sch_api/`
- [ ] **Linting clean**: `uv run flake8 kicad_sch_api/`

### 3. Integration Validation
- [ ] **MCP server builds**: `cd mcp-server && npm run build`
- [ ] **Examples work**: Test all example scripts
- [ ] **Format preservation**: Round-trip tests pass
- [ ] **Performance benchmarks**: Meet target metrics

### 4. Package Validation
- [ ] **Build succeeds**: `python -m build`
- [ ] **Package check**: `twine check dist/*`
- [ ] **Installation test**: `pip install dist/*.whl`
- [ ] **Import test**: `python -c "import kicad_sch_api"`

## Implementation

```bash
#!/bin/bash

# Parse arguments
TEST_ONLY=false
CHECK_ONLY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --force)
            FORCE=true
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

echo "📦 kicad-sch-api PyPI Publishing Process"
echo "=" * 50

# 1. Pre-flight checks
echo "🔍 Running pre-flight checks..."

# Check git status
if [[ -n $(git status --porcelain) && "$FORCE" == "false" ]]; then
    echo "❌ Git working directory not clean. Commit changes first."
    exit 1
fi

# Install build dependencies
echo "📥 Installing build dependencies..."
uv pip install build twine --quiet

# 2. Code quality checks
echo "🎨 Checking code quality..."

# Format check
if ! uv run black --check kicad_sch_api/ tests/ --quiet; then
    echo "❌ Code not formatted. Run: uv run black kicad_sch_api/ tests/"
    exit 1
fi

# Import sort check
if ! uv run isort --check-only kicad_sch_api/ tests/ --quiet; then
    echo "❌ Imports not sorted. Run: uv run isort kicad_sch_api/ tests/"
    exit 1
fi

# Type checking
echo "🔍 Type checking..."
uv run mypy kicad_sch_api/ --ignore-missing-imports || {
    echo "⚠️ Type checking issues found"
    if [[ "$FORCE" == "false" ]]; then
        exit 1
    fi
}

# 3. Comprehensive testing
echo "🧪 Running comprehensive test suite..."

# Core tests
if ! uv run pytest tests/ -v --tb=short; then
    echo "❌ Tests failed"
    exit 1
fi

# Import validation
if ! uv run python -c "import kicad_sch_api; print('✅ Import successful')"; then
    echo "❌ Import test failed"
    exit 1
fi

# MCP server validation
echo "🤖 Validating MCP server..."
cd ../mcp-server
if [[ -f "package.json" ]]; then
    if ! npm run build --silent; then
        echo "❌ MCP server build failed"
        exit 1
    fi
    echo "✅ MCP server builds successfully"
else
    echo "⚠️ MCP server not found, skipping"
fi
cd ../python

# 4. Build package
echo "🏗️ Building package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build
if ! python -m build; then
    echo "❌ Package build failed"
    exit 1
fi

# 5. Package validation
echo "📋 Validating package..."

# Check package integrity
if ! twine check dist/*; then
    echo "❌ Package validation failed"
    exit 1
fi

# Test installation
echo "🧪 Testing package installation..."
TEMP_VENV=$(mktemp -d)
python -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"

if ! pip install dist/*.whl --quiet; then
    echo "❌ Package installation failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
fi

if ! python -c "import kicad_sch_api; print('✅ Package import successful')"; then
    echo "❌ Package import failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
fi

deactivate
rm -rf "$TEMP_VENV"

# 6. Exit if check-only
if [[ "$CHECK_ONLY" == "true" ]]; then
    echo "✅ All pre-publication checks passed"
    echo "📦 Package ready for publication"
    exit 0
fi

# 7. Publish to PyPI
echo "🚀 Publishing to PyPI..."

if [[ "$TEST_ONLY" == "true" ]]; then
    # Publish to Test PyPI
    echo "📡 Publishing to Test PyPI..."
    if [[ -z "$TEST_PYPI_API_TOKEN" ]]; then
        echo "❌ TEST_PYPI_API_TOKEN environment variable not set"
        echo "Set it with: export TEST_PYPI_API_TOKEN=your_token"
        exit 1
    fi
    
    twine upload --repository testpypi dist/* --username __token__ --password "$TEST_PYPI_API_TOKEN"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Successfully published to Test PyPI"
        echo "🔗 View at: https://test.pypi.org/project/kicad-sch-api/"
        echo "📥 Test install: pip install --index-url https://test.pypi.org/simple/ kicad-sch-api"
    else
        echo "❌ Test PyPI publication failed"
        exit 1
    fi
    
else
    # Publish to production PyPI
    echo "📡 Publishing to Production PyPI..."
    
    if [[ -z "$PYPI_API_TOKEN" ]]; then
        echo "❌ PYPI_API_TOKEN environment variable not set"
        echo "Set it with: export PYPI_API_TOKEN=your_token"
        exit 1
    fi
    
    # Final confirmation
    echo "⚠️ WARNING: Publishing to PRODUCTION PyPI"
    echo "This action cannot be undone for this version."
    read -p "Continue? (y/N): " confirm
    
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "❌ Publication cancelled"
        exit 1
    fi
    
    twine upload dist/* --username __token__ --password "$PYPI_API_TOKEN"
    
    if [[ $? -eq 0 ]]; then
        echo "🎉 Successfully published to PyPI!"
        echo "🔗 View at: https://pypi.org/project/kicad-sch-api/"
        echo "📥 Install: pip install kicad-sch-api"
        
        # Get version from pyproject.toml
        VERSION=$(grep '^version = ' ../pyproject.toml | cut -d'"' -f2)
        echo "📋 Published version: $VERSION"
        
    else
        echo "❌ PyPI publication failed"
        exit 1
    fi
fi

echo "✅ Publication process completed"
```

## Usage Examples

```bash
# Check package is ready for publication
/publish-pypi --check-only

# Test publication to Test PyPI
export TEST_PYPI_API_TOKEN=your_test_token
/publish-pypi --test-only

# Publish to production PyPI
export PYPI_API_TOKEN=your_production_token
/publish-pypi

# Force publish (skip some checks)
/publish-pypi --force
```

## Required Environment Variables

### For Test PyPI
```bash
export TEST_PYPI_API_TOKEN=pypi-your_test_token_here
```

### For Production PyPI
```bash
export PYPI_API_TOKEN=pypi-your_production_token_here
```

## Post-Publication Checklist

After successful publication:

1. **Create GitHub release** with changelog
2. **Update documentation** links if needed
3. **Test installation** from PyPI: `pip install kicad-sch-api`
4. **Announce release** in relevant communities
5. **Monitor for issues** and user feedback

## Troubleshooting

**Build failures**:
- Check pyproject.toml configuration
- Verify all dependencies are specified
- Ensure MANIFEST.in includes necessary files

**Publication failures**:
- Verify API tokens are correct
- Check if version already exists on PyPI
- Ensure package name is available
- Review twine error messages

**Installation test failures**:
- Check that all dependencies are properly specified
- Verify package includes all necessary files
- Test in clean virtual environment

This command ensures professional-quality PyPI releases with comprehensive validation and error handling.