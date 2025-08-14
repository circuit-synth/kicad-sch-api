# Contributing to kicad-sch-api

Thank you for your interest in contributing to kicad-sch-api! This document provides guidelines for contributing to the project.

## 🎯 Project Vision

kicad-sch-api aims to be the definitive professional Python library for KiCAD schematic manipulation, providing:
- **Exact format preservation** matching KiCAD's native output
- **Enhanced developer experience** with modern object-oriented API
- **High performance** optimized for large schematics  
- **AI agent integration** via native MCP server
- **Professional quality** suitable for production environments

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/circuit-synth/kicad-sch-api.git
   cd kicad-sch-api
   ```

2. **Initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Set up development environment**:
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install in development mode
   cd python
   uv pip install -e .[dev]
   ```

4. **Verify installation**:
   ```bash
   uv run python -c "import kicad_sch_api; print('✅ Installation successful')"
   uv run pytest tests/test_component_management.py -v
   ```

### MCP Server Setup (Optional)

```bash
cd mcp-server
npm install
npm run build
npm test
```

## 🧪 Testing

### Running Tests

```bash
# Quick development tests
uv run pytest tests/test_component_management.py tests/test_sexpr_parsing.py -v

# Full test suite
uv run pytest tests/ -v --cov=kicad_sch_api

# Format preservation tests
uv run pytest tests/test_format_preservation.py -v

# Reference schematic tests
uv run pytest tests/reference_kicad_projects/ -v
```

### Test Requirements

All contributions must include appropriate tests:
- **Unit tests** for new functionality
- **Integration tests** for file I/O operations
- **Format preservation tests** for schematic modifications
- **Reference schematic tests** for new element types

### Test Coverage

We maintain >80% test coverage. New code should include comprehensive tests:
```bash
# Check coverage
uv run pytest tests/ --cov=kicad_sch_api --cov-report=html
# View report: open htmlcov/index.html
```

## 🎨 Code Style

### Python Code Style

We use **Black** and **isort** for consistent formatting:

```bash
# Format code
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/

# Check style
uv run flake8 kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
```

### Code Standards

- **Type hints**: All public methods must have type annotations
- **Docstrings**: All public methods must have comprehensive docstrings
- **Error handling**: Use validation and error collection patterns
- **Logging**: Appropriate logging levels for debugging
- **Performance**: Consider performance impact for large schematics

### Example Code Style

```python
def add_component(
    self,
    lib_id: str,
    reference: Optional[str] = None,
    value: str = "",
    position: Optional[Union[Point, Tuple[float, float]]] = None,
    **properties: Any,
) -> Component:
    """
    Add a new component to the schematic.
    
    Args:
        lib_id: Library identifier (e.g., "Device:R")
        reference: Component reference (auto-generated if None)
        value: Component value
        position: Component position (auto-placed if None)
        **properties: Additional component properties
        
    Returns:
        Newly created Component
        
    Raises:
        ValidationError: If component data is invalid
    """
    # Implementation with proper validation...
```

## 📋 Contribution Types

### 🐛 Bug Fixes

1. **Report bugs** with clear reproduction steps
2. **Include test case** that demonstrates the bug
3. **Fix with minimal changes** that don't break existing functionality
4. **Add regression test** to prevent future occurrence

### ✨ New Features

1. **Discuss in GitHub Issues** before implementation
2. **Follow existing patterns** and API conventions
3. **Include comprehensive tests** and documentation
4. **Update examples** if API changes

### 📚 Documentation

1. **API documentation** - Update docstrings and examples
2. **User guides** - Add usage examples and tutorials
3. **Reference schematics** - Contribute test schematic projects
4. **Performance guides** - Optimization tips and benchmarks

### 🔧 Performance Improvements

1. **Benchmark first** - Measure current performance
2. **Profile changes** - Ensure improvements are measurable
3. **Maintain accuracy** - Don't sacrifice correctness for speed
4. **Add performance tests** - Prevent performance regressions

## 📝 Pull Request Process

### Before Submitting

1. **Run full test suite**:
   ```bash
   uv run pytest tests/ -v --cov=kicad_sch_api
   ```

2. **Format code**:
   ```bash
   uv run black kicad_sch_api/ tests/
   uv run isort kicad_sch_api/ tests/
   ```

3. **Update documentation** if needed

4. **Add entry to CHANGELOG.md** under `[Unreleased]`

### PR Requirements

- **Clear description** of changes and motivation
- **Test coverage** for new functionality
- **Documentation updates** for user-facing changes
- **Format preservation** validation for schematic operations
- **Performance impact** assessment for large schematics

### PR Template

```markdown
## Description
Brief description of the change and its motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing API)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Format preservation tests pass
- [ ] Reference schematic tests pass
- [ ] Performance impact assessed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
- [ ] All tests pass locally
- [ ] CHANGELOG.md updated
```

## 🌟 Types of Contributions Needed

### High Priority
- **Reference schematic projects** - More KiCAD element coverage
- **Format preservation** improvements - Ensure 100% accuracy
- **Performance optimization** - Large schematic handling
- **MCP tool enhancements** - Additional AI agent capabilities

### Medium Priority  
- **Library sourcing integration** - DigiKey, SnapEDA APIs
- **Advanced validation** - Electrical rule checking
- **Documentation** - More examples and tutorials
- **Platform testing** - Windows, Linux, macOS validation

### Low Priority
- **Visualization tools** - Schematic rendering
- **Import/export** - Additional format support
- **Plugin system** - Extensible architecture
- **GUI tools** - Visual schematic editing

## 🤝 Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints and experiences
- Focus on constructive feedback
- Help others learn and grow

### Be Professional
- Test your changes thoroughly
- Write clear commit messages
- Respond to feedback promptly
- Document your code well

### Be Collaborative
- Ask questions when unsure
- Offer help to other contributors
- Share knowledge and best practices
- Celebrate successes together

## 📞 Getting Help

- **GitHub Issues**: For bugs, feature requests, and questions
- **GitHub Discussions**: For general discussion and community help
- **Documentation**: Check README.md and API documentation first

## 🏷️ Labels and Issue Management

### Issue Labels
- `bug`: Something isn't working correctly
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `performance`: Performance-related issues
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed

### Priority Labels
- `priority-high`: Critical issues blocking users
- `priority-medium`: Important improvements
- `priority-low`: Nice-to-have enhancements

## 📦 Release Process

### Version Strategy
- **Major** (X.0.0): Breaking API changes
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes, backward compatible

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] GitHub release created
- [ ] PyPI package published

---

**Thank you for contributing to kicad-sch-api!** Your contributions help make professional KiCAD schematic manipulation accessible to everyone.