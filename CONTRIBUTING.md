# Contributing to kicad-sch-api

Thank you for your interest in contributing to kicad-sch-api! We welcome contributions of all kinds.

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please [open an issue](https://github.com/circuit-synth/kicad-sch-api/issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, KiCAD version, OS)
- Minimal code example if possible

### 2. Suggest Features

Have an idea? [Open an issue](https://github.com/circuit-synth/kicad-sch-api/issues) with:
- Clear description of the feature
- Use case and benefits
- Example API if applicable

### 3. Submit Pull Requests

We welcome code contributions! Focus areas:

- **KiCAD Library Integration** - Improved component validation and library parsing
- **Performance Optimizations** - Faster operations on large schematics
- **MCP Server Tools** - Additional tools for AI agent integration
- **Test Coverage** - More comprehensive test cases
- **Format Preservation** - Ensuring exact KiCAD compatibility
- **Documentation** - Improved guides, examples, and API docs

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
uv pip install -e ".[dev]"
```

### 2. Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/reference_tests/ -v     # Format preservation
uv run pytest tests/test_component*.py -v   # Component tests
uv run pytest tests/test_connectivity*.py -v # Connectivity tests
```

### 3. Code Quality Checks

**ALWAYS run these before committing:**

```bash
# Format code
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/

# Type checking
uv run mypy kicad_sch_api/

# Linting
uv run flake8 kicad_sch_api/ tests/
```

Or run all at once:

```bash
uv run black kicad_sch_api/ tests/ && \
uv run isort kicad_sch_api/ tests/ && \
uv run mypy kicad_sch_api/ && \
uv run flake8 kicad_sch_api/ tests/
```

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write clear, documented code
- Add tests for new functionality
- Ensure all tests pass
- Run code quality checks
- Update documentation if needed

### 3. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "feat: Add support for hierarchical label rotation"
git commit -m "fix: Correct pin position calculation for rotated components"
git commit -m "docs: Update API reference with new connectivity methods"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a pull request on GitHub with:
- Clear description of changes
- Motivation/use case
- Test coverage
- Screenshots/examples if applicable

### 5. Code Review

- Respond to review comments
- Make requested changes
- Keep the PR focused and manageable

## Testing Requirements

### For Bug Fixes:
- Add test that reproduces the bug
- Verify test fails before fix
- Verify test passes after fix

### For New Features:
- Add unit tests covering the feature
- Add integration tests if applicable
- Add reference tests for format preservation
- Update documentation

### Format Preservation Tests:

**Critical:** Any changes affecting output format must be verified:

```bash
# Run format preservation tests
uv run pytest tests/reference_tests/ -v
uv run pytest tests/test_format_preservation.py -v
```

See [docs/CLAUDE_GUIDE.md](docs/CLAUDE_GUIDE.md#testing-strategy--format-preservation) for details on format preservation testing strategy.

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for public APIs

```python
def add_component(
    self,
    lib_id: str,
    reference: str,
    value: str,
    position: Tuple[float, float]
) -> Component:
    """Add a component to the schematic.

    Args:
        lib_id: Library identifier (e.g., "Device:R")
        reference: Component reference (e.g., "R1")
        value: Component value (e.g., "10k")
        position: Component position (x, y) in mm

    Returns:
        Component object

    Raises:
        ValidationError: If lib_id is invalid
    """
```

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Documentation

- Document all public APIs
- Include code examples in docstrings
- Update relevant markdown files
- Add to [CHANGELOG.md](CHANGELOG.md)

## Architecture Guidelines

### Core Principles

1. **Exact Format Preservation** - All output must match KiCAD exactly
2. **Performance First** - Optimize for large schematics
3. **Professional Quality** - Comprehensive validation and error handling
4. **Type Safety** - Full type hints and validation

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

### Key Design Patterns

- **Collections** - All element groups use `BaseCollection[T]` pattern
- **Validation** - Use `ValidationLevel` for configurable strictness
- **Indexing** - O(1) lookups via `IndexRegistry`
- **Modification Tracking** - All collections track changes

See [docs/COLLECTIONS.md](docs/COLLECTIONS.md) for collection architecture details.

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking API changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- **GitHub Issues**: [Report bugs or suggest features](https://github.com/circuit-synth/kicad-sch-api/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/circuit-synth/kicad-sch-api/discussions) (if enabled)
- **Email**: shane@circuit-synth.com

## Code of Conduct

### Our Standards

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

---

Thank you for contributing to kicad-sch-api! 🎉
