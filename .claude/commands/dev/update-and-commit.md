# Update and Commit Command - kicad-sch-api

## Usage
```bash
/update-and-commit "Brief description of changes"
```

## Description
Comprehensive workflow for documenting progress, updating documentation, and committing changes to kicad-sch-api with professional quality standards.

## Process

### 1. Update Documentation (Only if Needed)
- IF new user-facing features: Update README.md briefly
- IF new MCP tools: Update tool documentation
- IF new API methods: Update examples in README
- NO documentation changes for internal fixes or refactoring

### 2. Format Code Before Committing
**IMPORTANT: Always format code before committing**
```bash
# Format Python code
uv run black kicad_sch_api/ tests/ --quiet
uv run isort kicad_sch_api/ tests/ --quiet

# Format TypeScript (MCP server)
cd mcp-server && npm run format --silent 2>/dev/null || echo "TypeScript formatting skipped"
cd ..

# Format configuration files
prettier --write "*.{json,yml,yaml}" --ignore-path .gitignore 2>/dev/null || echo "Config formatting skipped"
```

### 3. Quality Checks Before Committing
**IMPORTANT: Run basic quality checks**
```bash
# Syntax validation
find kicad_sch_api/ tests/ -name "*.py" -exec python -m py_compile {} \; 2>/dev/null || echo "⚠️ Syntax errors found"

# Quick test run
uv run pytest tests/test_component_management.py tests/test_sexpr_parsing.py -q || echo "⚠️ Core tests failing"

# Import validation
uv run python -c "import kicad_sch_api; print('✅ Import successful')" || echo "⚠️ Import failed"
```

### 4. Commit Changes (Selective and Clean)
**IMPORTANT: Keep commit message under 3 lines**
```bash
# Check status and review changes
git status

# Add specific files (be selective)
git add kicad_sch_api/ tests/ README.md pyproject.toml

# Remove unwanted files if any
git rm unwanted-file.py 2>/dev/null || true

# Commit with professional message
git commit -m "Brief description of change

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 5. File Management Strategy
**IMPORTANT: Be selective about what gets committed**

```bash
# 1. Review git status
git status

# 2. Handle different file categories:

# Core library files - always include
git add kicad_sch_api/

# Tests - include if relevant
git add tests/

# Documentation - include if updated
git add README.md CLAUDE.md

# Configuration - include if changed
git add pyproject.toml pytest.ini

# MCP server - include if relevant
git add mcp-server/src/ mcp-server/package.json

# Remove temporary files
git rm '*.tmp' '*.log' 2>/dev/null || true
git rm -r htmlcov/ .pytest_cache/ 2>/dev/null || true

# 3. Final verification
git status  # Should show only files you want to commit
```

### 6. kicad-sch-api Specific Checks

```bash
# Validate core functionality works
uv run python -c "
import kicad_sch_api as ksa
sch = ksa.create_schematic('Test')
comp = sch.components.add('Device:R', 'R1', '10k')
print(f'✅ Core API working: {comp.reference} = {comp.value}')
"

# Check MCP server builds
cd mcp-server && npm run build --silent && echo "✅ MCP server builds" || echo "⚠️ MCP build failed"
cd ..

# Validate package structure
uv run python setup.py check --strict --metadata || echo "⚠️ Package metadata issues"
```

## Guidelines for kicad-sch-api

- **Be concise**: Commit messages should focus on user impact
- **Focus on features**: Document API improvements, new capabilities
- **Skip internal changes**: Don't document refactoring unless it affects users
- **Professional quality**: Ensure formatting and tests pass

## Examples

### Feature Addition
```bash
/update-and-commit "Add bulk component update operations for large schematics"
```

### Bug Fix
```bash  
/update-and-commit "Fix component reference validation for international characters"
```

### Performance Improvement
```bash
/update-and-commit "Optimize symbol caching for 10x faster library lookups"
```

### MCP Enhancement
```bash
/update-and-commit "Add hierarchical sheet MCP tools for AI agent workflows"
```

## File Categories for kicad-sch-api

### Always Include
- `kicad_sch_api/` - Core library code
- `tests/` - Test files (when relevant)
- `pyproject.toml` - Package configuration
- `README.md` - User documentation

### Include When Relevant
- `mcp-server/` - MCP server changes
- `CLAUDE.md` - Development guidance updates
- `.claude/commands/` - Command updates
- `examples/` - Usage examples

### Never Include
- `htmlcov/` - Coverage reports
- `.pytest_cache/` - Test cache
- `*.log` - Log files
- `test_outputs/` - Temporary test files
- `.venv/` - Virtual environment

## Quality Standards

Before committing, ensure:
- ✅ **Tests pass**: At least quick suite runs successfully
- ✅ **Code formatted**: Black and isort applied
- ✅ **Imports work**: Basic import validation passes
- ✅ **No syntax errors**: All Python files compile
- ✅ **Clean git status**: Only intended files committed

## Professional Commit Messages

Good examples:
- "Add exact format preservation for component properties"
- "Implement high-performance symbol library caching"
- "Add MCP tools for hierarchical sheet manipulation"

Avoid:
- "Fix stuff" or "Various improvements"
- Technical implementation details
- Long explanations of how changes work

This command ensures professional quality commits while maintaining development velocity for kicad-sch-api.