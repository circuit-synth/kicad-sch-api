# Context Portal Configuration for kicad-sch-api

This repository uses Context Portal to enhance development with AI-assisted project memory.

## Setup

```bash
# Install Context Portal
cd tools/context-portal && pip install -e .

# Start Context Portal server  
uvx context-portal --workspace kicad-sch-api --port 8001
```

## Usage in Claude Code

Context Portal provides structured project memory for this repository:

- **Code patterns**: API design decisions, object model choices
- **Architecture decisions**: Why we chose enhanced API vs kicad-skip approach  
- **Testing strategies**: Comprehensive test coverage approach
- **Integration patterns**: MCP server design, S-expression handling
- **Performance optimizations**: Symbol caching, format preservation

## Repository-Specific Context

This is the **kicad-sch-api** repository focused on:
- Professional KiCAD schematic manipulation
- Enhanced object model vs verbose existing solutions
- S-expression parsing with exact format preservation  
- MCP server integration for AI workflows
- Symbol library caching and performance optimization

## Context Categories

- `architecture`: Core API design decisions
- `testing`: Test strategy and coverage
- `performance`: Optimization approaches
- `integration`: MCP server and external tool integration
- `compatibility`: KiCAD format preservation strategies