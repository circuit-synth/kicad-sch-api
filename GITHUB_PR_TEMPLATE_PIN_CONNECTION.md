# GitHub PR Template - Pin Connection Implementation

**Use this template for all PRs related to pin connection epic (#199) and sub-issues (#200-#208).**

Copy the content below into your PR description on GitHub.

---

## PR Description

**Issue**: Resolves #___ (e.g., #200, #201, #202)
**Type**: Feature / Enhancement / Fix / Refactor / Test / Docs
**Priority**: P0 / P1 / P2

### Summary

[Brief description of what this PR does - 2-3 sentences]

### Problem Statement

[What problem does this solve? Why is it needed?]

### Solution Approach

[How does this PR solve the problem?]

### Changes Made

- [ ] Implementation of feature X
- [ ] Addition of tests for feature X
- [ ] Documentation updates
- [ ] Performance optimizations
- [ ] Bug fixes

[Add specific file changes and explain what was changed]

---

## Acceptance Criteria Verification

- [ ] **Solves GitHub Issue**: All AC from issue #___ are met
  - [ ] AC1: [Description]
  - [ ] AC2: [Description]
  - [ ] AC3: [Description]

- [ ] **Functional Requirements**:
  - [ ] Feature works as specified
  - [ ] Edge cases handled
  - [ ] Error cases tested
  - [ ] Coordinate system correct (Y-negation before rotation)

- [ ] **Testing**:
  - [ ] Test coverage >95%
  - [ ] Unit tests included
  - [ ] Integration tests included
  - [ ] Reference tests included (if applicable)
  - [ ] All tests passing (`uv run pytest tests/ -v`)

- [ ] **Code Quality**:
  - [ ] `uv run black kicad_sch_api/ tests/` ✓
  - [ ] `uv run isort kicad_sch_api/ tests/` ✓
  - [ ] `uv run mypy kicad_sch_api/ --strict` ✓
  - [ ] `uv run flake8 kicad_sch_api/ tests/` ✓

- [ ] **Logging**:
  - [ ] Function entry/exit logged at DEBUG level
  - [ ] Intermediate values logged
  - [ ] Errors logged before raising
  - [ ] Structured logging (not string concatenation)

- [ ] **Documentation**:
  - [ ] Docstrings complete and accurate
  - [ ] Code comments for complex logic
  - [ ] Examples tested and working
  - [ ] Related issues linked

---

## Testing

### Tests Included

- **Unit Tests**: `tests/unit/test_<feature>.py`
  - [ ] Test case 1: [Description]
  - [ ] Test case 2: [Description]
  - [ ] Test case 3: [Description]
  - [ ] Coverage: ___% (must be >95%)

- **Integration Tests**: `tests/integration/test_<feature>.py`
  - [ ] Workflow test 1: [Description]
  - [ ] Workflow test 2: [Description]

- **Reference Tests**: `tests/reference_tests/test_<feature>_reference.py`
  - [ ] Compare to manual KiCAD circuit
  - [ ] Validate wire positions
  - [ ] Validate junction locations
  - [ ] Validate routing strategy

### Test Execution

```bash
# All tests pass
uv run pytest tests/ -v

# Coverage report
coverage report -m kicad_sch_api/

# Code quality
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/
uv run mypy kicad_sch_api/ --strict
uv run flake8 kicad_sch_api/ tests/
```

### Test Results

```
[Paste output of test execution]
```

---

## Performance

- [ ] **Simple operations** <100ms:
  - Pin position lookup: [__ms]
  - Get all pins: [__ms]
  - Find pins by name: [__ms]

- [ ] **Complex operations** <500ms:
  - Wire routing: [__ms]
  - Junction detection: [__ms]
  - Connectivity validation: [__ms]

- [ ] **No performance regressions**:
  - Benchmark results: [__ms] (previous: [__ms])

---

## Track-Specific Verification

**[Select the track(s) this PR addresses]**

### Track A: Pin Discovery (#200, #201, #207)

- [ ] **get_component_pins (#200)**:
  - [ ] Returns list of PinInfo with all details
  - [ ] Pin positions accurate to KiCAD
  - [ ] Pin names from symbol library
  - [ ] Pin types correctly classified
  - [ ] Handles all rotations (0°, 90°, 180°, 270°)
  - [ ] Handles mirrored components
  - [ ] Performance <50ms

- [ ] **find_pins_by_name (#201)**:
  - [ ] Wildcard patterns work (* ?)
  - [ ] Case-insensitive matching
  - [ ] find_pins_by_type also works
  - [ ] Returns empty list when no matches
  - [ ] No false positives

- [ ] **Logging for Pin Operations (#207)**:
  - [ ] Entry logged with context
  - [ ] Exit logged with results
  - [ ] All DEBUG level
  - [ ] No performance impact

### Track B: Wire Routing (#202, #203, #204)

- [ ] **Orthogonal Routing (#202)**:
  - [ ] Direct routing: straight line ✓
  - [ ] Orthogonal: L-shape ✓
  - [ ] H-first strategy ✓
  - [ ] V-first strategy ✓
  - [ ] Auto strategy selection ✓
  - [ ] Corners snap to grid ✓
  - [ ] Endpoints exactly at pins ✓
  - [ ] Performance <50ms ✓

- [ ] **Auto-Junction Detection (#203)**:
  - [ ] T-junctions detected ✓
  - [ ] Cross-junctions detected ✓
  - [ ] No false positives ✓
  - [ ] Grid-aligned ✓
  - [ ] No duplicates ✓

- [ ] **Connectivity Validation (#204)**:
  - [ ] ConnectivityReport generated ✓
  - [ ] Issues categorized ✓
  - [ ] Detects floating components ✓
  - [ ] Helpful error messages ✓

### Track C: Testing & Documentation (#205-#208)

- [ ] **Testing Infrastructure (#205)**:
  - [ ] Fixtures created and working ✓
  - [ ] Helper functions implemented ✓
  - [ ] Easy to extend ✓

- [ ] **Reference KiCAD Circuits (#206)**:
  - [ ] voltage_divider created ✓
  - [ ] led_circuit created ✓
  - [ ] parallel_resistors created ✓
  - [ ] junction_test created ✓
  - [ ] ic_connections created ✓
  - [ ] All loadable in KiCAD ✓
  - [ ] Expected values documented ✓

- [ ] **Pin Operation Logging (#207)**:
  - [ ] Pin position lookup logged ✓
  - [ ] Wire creation logged ✓
  - [ ] Connection operations logged ✓
  - [ ] Junction detection logged ✓
  - [ ] All DEBUG level ✓

- [ ] **Documentation (#208)**:
  - [ ] User guide created ✓
  - [ ] API reference created ✓
  - [ ] Architecture doc created ✓
  - [ ] Troubleshooting guide created ✓
  - [ ] Examples accurate ✓

---

## Potential Reviewer Questions

**Q: How does the coordinate system work?**

A: [Explain KiCAD's inverted Y-axis and how it's handled in this PR]

**Q: Why are junctions created at specific positions?**

A: [Explain junction detection tolerance and grid alignment]

**Q: How does the routing algorithm handle complex layouts?**

A: [Explain handling of overlapping wires, priority, etc]

**Q: What if a component has no pins?**

A: [Explain error handling for edge cases]

---

## Related Issues

- Closes #___ (or relates to #___)
- Depends on #___ (if applicable)
- Blocks #___ (if applicable)

---

## Additional Notes

[Any additional information, gotchas, design decisions, or open questions]

---

## Checklist for Reviewers

**Reviewers**: Please verify:

- [ ] Issue requirements are met
- [ ] Tests are comprehensive (>95% coverage)
- [ ] Code quality checks pass
- [ ] Logging is present at entry/exit and DEBUG level
- [ ] Coordinate system handling is correct
- [ ] Performance within targets
- [ ] Documentation complete and accurate
- [ ] No breaking changes
- [ ] Commits are clean and well-organized

**Approve** if all items above are checked.

**Request Changes** if:
- Test coverage <95%
- Code quality checks fail
- Logging missing or incomplete
- Documentation missing or inaccurate
- Performance exceeds targets
- Issues with coordinate system or algorithm logic

---

## After Merge

- [ ] Update CHANGELOG.md with feature summary
- [ ] Update documentation if needed
- [ ] Tag release if this completes the epic
- [ ] Notify MCP server team of API changes (if any)

---

**PR Template Version**: 1.0
**Last Updated**: 2025-11-06
