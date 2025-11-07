# Documentation

Welcome to the kicad-sch-api documentation!

## 📚 Documentation Index

### Getting Started
Start here if you're new to the library.

**[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete beginner's guide
- What is kicad-sch-api and why use it?
- Installation
- Your first circuit in 5 minutes
- Understanding positions and coordinates
- Common patterns
- Next steps

### Why Use This Library?
Understand the value proposition and use cases.

**[WHY_USE_THIS_LIBRARY.md](WHY_USE_THIS_LIBRARY.md)** - Value proposition and comparisons
- The problem: Manual design doesn't scale
- What makes this library different?
- Real-world use cases
- Comparison to alternatives
- When to use (and when not to use)
- Success stories

### API Reference
Complete reference for all methods and classes.

**[API_REFERENCE.md](API_REFERENCE.md)** - Full API documentation
- Creating and loading schematics
- Component operations
- Wire operations
- Label operations
- Collections API
- Configuration
- Complete examples with all options

### Common Recipes
Solutions to common tasks.

**[RECIPES.md](RECIPES.md)** - Practical examples and patterns
- Basic circuit patterns (voltage dividers, filters, LEDs)
- Component management (finding, updating, validating)
- Wiring and connectivity
- Circuit analysis (BOM, statistics, validation)
- Batch operations (test generation, parameter sweeps)
- Advanced patterns (templates, configuration-driven)

### Orthogonal Routing
Automatic wire routing with Manhattan-style paths.

**[ORTHOGONAL_ROUTING.md](ORTHOGONAL_ROUTING.md)** - Wire routing guide
- Overview of orthogonal (Manhattan) routing
- Direction modes (AUTO, HORIZONTAL_FIRST, VERTICAL_FIRST)
- KiCAD Y-axis inversion explained
- Practical examples (voltage dividers, filter chains, power distribution)
- Integration with MCP servers
- Best practices and troubleshooting

### Architecture
Understand how the library works internally.

**[ARCHITECTURE.md](ARCHITECTURE.md)** - Internal architecture and design
- High-level architecture diagram
- Core components explained
- Data flow examples
- Design patterns used
- Performance optimizations
- Extension points

## 📖 Quick Links by Task

### I want to...

#### Learn the Basics
1. Read [GETTING_STARTED.md](GETTING_STARTED.md) - Beginner-friendly intro
2. Try the LED circuit example (5 minutes)
3. Check `../examples/basic_usage.py` for more examples

#### Understand Why to Use This
1. Read [WHY_USE_THIS_LIBRARY.md](WHY_USE_THIS_LIBRARY.md)
2. See real-world use cases
3. Check comparisons to alternatives

#### Build a Specific Circuit
1. Check [RECIPES.md](RECIPES.md) for your circuit type
2. Copy and modify the example
3. Refer to [API_REFERENCE.md](API_REFERENCE.md) for details

#### Automate Circuit Generation
1. Read "Batch Operations" section in [RECIPES.md](RECIPES.md)
2. See parameter sweep and test generation examples
3. Check template system in "Advanced Patterns"

#### Integrate with AI Agents
1. Install [mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)
2. Use with Claude Code or compatible AI agents
3. Reference [API_REFERENCE.md](API_REFERENCE.md) for operations

#### Use Automatic Wire Routing
1. Read [ORTHOGONAL_ROUTING.md](ORTHOGONAL_ROUTING.md) for routing guide
2. Use `create_orthogonal_routing()` for Manhattan-style routing
3. Choose appropriate direction mode for your circuit
4. Integrate with MCP server for AI-powered routing

#### Understand the Codebase
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for overview
2. Check module docstrings in source code
3. See test files for usage examples

#### Find Specific Method Documentation
1. Go to [API_REFERENCE.md](API_REFERENCE.md)
2. Use table of contents to jump to section
3. See complete parameter and return type docs

## 📂 Additional Documentation

In the main repository:

- **[../README.md](../README.md)** - Project overview and quick start
- **[../CLAUDE.md](../CLAUDE.md)** - Development guide for Claude Code
- **[../examples/](../examples/)** - Complete working examples
- **[../tests/](../tests/)** - Test suite (shows all features)

## 🎯 Learning Path

### Beginner (1-2 hours)
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Try the LED circuit example
3. Browse [RECIPES.md](RECIPES.md) for your use case
4. Experiment with `examples/basic_usage.py`

### Intermediate (Half day)
1. Read [WHY_USE_THIS_LIBRARY.md](WHY_USE_THIS_LIBRARY.md) for context
2. Study [RECIPES.md](RECIPES.md) recipes for your domain
3. Reference [API_REFERENCE.md](API_REFERENCE.md) as needed
4. Try `examples/advanced_usage.py`
5. Create your first automated circuit generator

### Advanced (1-2 days)
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand internals
2. Study all recipes in [RECIPES.md](RECIPES.md)
3. Integrate with your workflow (CI/CD, testing, etc.)
4. Consider contributing new recipes or features

### Expert (Ongoing)
1. Contribute to the library
2. Build MCP servers or extensions
3. Create templates for your organization
4. Help others in GitHub issues

## 💡 Tips for Success

### Do's
✅ Start simple - try the LED example first
✅ Use recipes as templates - copy and modify
✅ Leverage collections for efficient operations
✅ Use type hints - excellent IDE support
✅ Validate your circuits - use built-in validation
✅ Test in KiCAD - open generated files to verify

### Don'ts
❌ Don't guess at API - check API_REFERENCE.md
❌ Don't manually calculate pins - use add_wire_between_pins()
❌ Don't write S-expressions - use high-level API
❌ Don't skip validation - catch errors early
❌ Don't ignore format preservation tests - they matter

## 🤝 Contributing to Documentation

Found an issue or want to improve documentation?

1. Fork the repository
2. Edit the relevant `.md` file
3. Submit a pull request

### Documentation Style Guide

- **Use examples**: Every concept needs a code example
- **Be practical**: Focus on real-world use cases
- **Be concise**: Get to the point quickly
- **Link between docs**: Help readers navigate
- **Update examples**: Keep them working with latest API

## 📞 Getting Help

### Documentation Issues
- File an issue: https://github.com/circuit-synth/kicad-sch-api/issues
- Label it "documentation"

### Usage Questions
1. Check [GETTING_STARTED.md](GETTING_STARTED.md)
2. Search [RECIPES.md](RECIPES.md) for your use case
3. Review [API_REFERENCE.md](API_REFERENCE.md)
4. Check `../examples/` directory
5. File an issue if still stuck

### Bug Reports
1. Check if it's documented behavior in [API_REFERENCE.md](API_REFERENCE.md)
2. Create minimal reproduction example
3. File issue with "bug" label

## 🔄 Documentation Updates

This documentation is actively maintained. Last major update: November 2025

**Changelog:**
- Nov 2025: Added orthogonal routing documentation
  - ORTHOGONAL_ROUTING.md: Complete guide to automatic wire routing
  - Integration tests and examples for routing
  - Y-axis inversion explained with practical examples
- Oct 2025: Initial comprehensive documentation created
  - GETTING_STARTED.md: Complete beginner guide
  - WHY_USE_THIS_LIBRARY.md: Value proposition and comparisons
  - API_REFERENCE.md: Full API documentation
  - RECIPES.md: Common patterns and solutions
  - ARCHITECTURE.md: Internal design documentation

---

**Ready to get started? Begin with [GETTING_STARTED.md](GETTING_STARTED.md)!** 🚀
