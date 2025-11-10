# Review Implementation Command - kicad-sch-api

## Usage
```bash
/review-implementation [component]
```

## Description
Performs comprehensive code review and analysis of kicad-sch-api implementation, focusing on professional quality, performance, and API design.

## Parameters
- `component` (optional): Specific component to review (`core`, `library`, `mcp`, `utils`, `tests`)
- `--performance`: Focus on performance analysis
- `--api-design`: Focus on API usability review
- `--format-preservation`: Focus on format preservation validation

## Review Areas

### 1. Core Library Review
```bash
/review-implementation core
```

**Focuses on**:
- **S-expression parsing** accuracy and performance
- **Component management** API design and efficiency
- **Schematic operations** completeness and validation
- **Type system** correctness and usability
- **Error handling** comprehensiveness and clarity

**Key Questions**:
- Does the API feel intuitive and pythonic?
- Are bulk operations efficient for large schematics?
- Is format preservation truly exact?
- Do validation errors provide actionable feedback?

### 2. Library Management Review
```bash
/review-implementation library
```

**Focuses on**:
- **Symbol caching** performance and accuracy
- **Library discovery** robustness across platforms
- **Multi-source integration** (future: DigiKey, SnapEDA)
- **Cache invalidation** and persistence

**Key Questions**:
- Does caching provide measurable performance improvement?
- Is library discovery reliable across different KiCAD installations?
- Are cache miss scenarios handled gracefully?

### 3. MCP Integration Review
```bash
/review-implementation mcp
```

**Focuses on**:
- **Tool completeness** for AI agent workflows
- **Error handling** quality for agent consumption
- **Python bridge** reliability and performance
- **TypeScript integration** professional standards

**Key Questions**:
- Do MCP tools cover all essential schematic operations?
- Are error messages clear enough for AI agents to understand?
- Is the Python bridge robust against subprocess failures?

### 4. Testing Strategy Review
```bash
/review-implementation tests
```

**Focuses on**:
- **Test coverage** completeness and quality
- **Reference schematics** representativeness
- **Format preservation** validation accuracy
- **Performance benchmarks** relevance

**Key Questions**:
- Do tests cover all critical functionality?
- Are reference schematics representative of real-world usage?
- Is format preservation testing comprehensive enough?

## Review Checklist

### API Design Quality
- [ ] **Intuitive naming**: Method and property names are self-explanatory
- [ ] **Consistent patterns**: Similar operations follow same patterns
- [ ] **Type safety**: Proper type hints throughout
- [ ] **Error messages**: Clear, actionable error descriptions
- [ ] **Performance**: O(1) lookups, efficient bulk operations

### Code Quality Standards
- [ ] **Documentation**: All public methods have docstrings
- [ ] **Logging**: Appropriate logging levels and messages
- [ ] **Validation**: Input validation on all public methods
- [ ] **Error handling**: Graceful degradation, no silent failures
- [ ] **Memory efficiency**: No memory leaks, efficient data structures

### Format Preservation
- [ ] **Round-trip accuracy**: load → save → load produces identical results
- [ ] **Whitespace preservation**: Indentation and spacing maintained
- [ ] **Element ordering**: Order of elements preserved
- [ ] **Quote consistency**: String quoting matches KiCAD conventions

### Performance Benchmarks
- [ ] **Symbol lookup**: <1ms for cached symbols
- [ ] **Component operations**: <100ms for 1000 components
- [ ] **File I/O**: <500ms for complex schematics
- [ ] **Memory usage**: <100MB for large schematics

### AI Agent Integration
- [ ] **Tool completeness**: All essential operations available
- [ ] **Error context**: Detailed error information for debugging
- [ ] **Response format**: Consistent, structured responses
- [ ] **Performance**: <1s response time for typical operations

## Review Process

### 1. Automated Analysis
```bash
# Code quality metrics
uv run flake8 kicad_sch_api/ --statistics
uv run mypy kicad_sch_api/ --show-error-codes

# Test coverage
uv run pytest tests/ --cov=kicad_sch_api --cov-report=term-missing

# Performance profiling
uv run python -m cProfile -s cumulative tests/test_performance.py
```

### 2. Manual Review Checklist
- [ ] **API consistency** with established patterns
- [ ] **Documentation completeness** for public methods
- [ ] **Error handling** quality and coverage
- [ ] **Performance characteristics** meet benchmarks
- [ ] **Type annotations** accuracy and completeness

### 3. Integration Validation
- [ ] **MCP tools** work correctly with sample agents
- [ ] **Format preservation** validated with real KiCAD files
- [ ] **Library integration** discovers symbols correctly
- [ ] **Bulk operations** perform efficiently

## Professional Standards

### Code Review Standards
- **Readability**: Code should be self-documenting
- **Maintainability**: Clear separation of concerns
- **Testability**: Easy to unit test and mock
- **Performance**: Optimized for real-world usage patterns
- **Documentation**: Comprehensive API documentation

### API Design Standards
- **Intuitive**: Natural mental model for schematic operations
- **Consistent**: Similar operations use similar patterns
- **Powerful**: Supports both simple and complex operations
- **Safe**: Validates inputs and prevents corruption
- **Fast**: Optimized for large schematic workflows

## Review Output

The review generates:
- **Quality metrics** and scores
- **Performance benchmarks** vs. targets
- **API usability** assessment
- **Improvement recommendations** prioritized by impact
- **Comparison analysis** vs. other schematic manipulation solutions

This ensures kicad-sch-api maintains professional quality standards while providing superior functionality to existing solutions.