# PR Review Quick Checklist - Pin Connection Implementation

**Quick version for pasting into PR template or using in quick reviews.**

Copy this section into your PR template for automated checking.

---

## Functional Correctness

- [ ] Solves the GitHub issue (Issue #___)
- [ ] All acceptance criteria met
- [ ] Edge cases handled (non-existent components, empty lists, etc)
- [ ] Coordinate system correct (Y-negation applied before rotation)
- [ ] Pin positions verified against KiCAD
- [ ] Rotation/mirroring transforms work correctly
- [ ] Wire endpoints exactly at pin positions
- [ ] Junctions grid-aligned and positioned correctly
- [ ] No hardcoded values (use parameters/constants)

## Testing

- [ ] Test coverage >95% (`coverage report -m`)
- [ ] Unit tests included and passing
- [ ] Integration tests included and passing
- [ ] Reference tests comparing against manual KiCAD circuits
- [ ] All tests pass (`uv run pytest tests/ -v`)
- [ ] No flaky tests (deterministic, independent)
- [ ] Tests follow established patterns (fixtures, naming)

## Logging & Debugability

- [ ] Function entry logged: `logger.debug(f"<func>: <context>")`
- [ ] Function exit logged: `logger.debug(f"  Result: <value>")`
- [ ] Intermediate steps logged (transformations, decisions)
- [ ] Errors logged before raising exceptions
- [ ] Structured logging (no string concatenation)
- [ ] Log levels appropriate (DEBUG for detail, INFO for operations)
- [ ] No logging performance impact

## Code Quality

- [ ] Passes black: `uv run black kicad_sch_api/ tests/`
- [ ] Passes isort: `uv run isort kicad_sch_api/ tests/`
- [ ] Passes mypy strict: `uv run mypy kicad_sch_api/ --strict`
- [ ] Passes flake8: `uv run flake8 kicad_sch_api/ tests/`
- [ ] Complete type hints (no `Any` without justification)
- [ ] Descriptive names (snake_case functions, PascalCase classes)
- [ ] No code duplication
- [ ] Reasonable function size (<50 lines preferred)
- [ ] Error handling appropriate (ValueError, KeyError, etc)

## Documentation

- [ ] Docstrings complete (purpose, Args, Returns, Raises)
- [ ] Docstring examples accurate and tested
- [ ] Complex logic has clear comments
- [ ] No obvious-state comments
- [ ] Related issues linked in docstrings/comments

## Performance

- [ ] Simple operations <100ms (pin lookup, single wire)
- [ ] Complex operations <500ms (routing, validation)
- [ ] Algorithm complexity reasonable (no nested loops over wires)
- [ ] No memory leaks or unnecessary object retention
- [ ] Performance measured (not assumed)

## Git Hygiene

- [ ] Commits are small and focused
- [ ] No merge commits (unless merging main)
- [ ] Commit messages clear: `type: subject` (feat/fix/test/docs)
- [ ] Commit messages reference issue: `Resolves #<number>`
- [ ] Branch name descriptive: `<issue>-<description>`
- [ ] Branch up to date with main

## Track-Specific Items

**For Pin Discovery (#200, #201)**:
- [ ] get_component_pins returns all pins with correct data
- [ ] Pin positions match KiCAD symbol library
- [ ] Pin names/types populated correctly
- [ ] find_pins_by_name supports wildcards
- [ ] Handles rotated/mirrored components

**For Wire Routing (#202, #203)**:
- [ ] Orthogonal routing creates proper L-shapes
- [ ] Direct routing: straight line
- [ ] H-first and V-first strategies work
- [ ] Corners snap to grid
- [ ] Auto-junction detection finds T-junctions and crosses
- [ ] No false positive junctions

**For Validation (#204)**:
- [ ] ConnectivityReport generated with issues
- [ ] Issues categorized (error/warning/info)
- [ ] Detects floating components
- [ ] Validates pin connections

**For Testing & Docs (#205-#208)**:
- [ ] Fixtures implemented and usable
- [ ] Reference KiCAD circuits created (voltage divider, LED circuit, etc)
- [ ] All reference values documented
- [ ] Documentation accurate and examples work
- [ ] User guide created (if documentation PR)

## Final Checks

- [ ] No breaking changes to existing API
- [ ] Input validation prevents unexpected crashes
- [ ] Documentation complete (docstrings + examples)
- [ ] All files properly formatted
- [ ] No debug prints left in code
- [ ] No TODO comments without explanation

---

## Reviewer Sign-Off

**Approved by**: ____________
**Date**: ____________
**Issues Found**: ☐ None ☐ (describe below)

```
[ Any issues that must be addressed before merge ]
```

---

## Common Issues in Pin Connection PRs

**Check these first** - most common issues found:

- ❌ **Y-axis wrong**: Y-negation MUST happen BEFORE rotation
- ❌ **No debug logging**: Entry/exit/errors REQUIRED
- ❌ **Coordinate confusion**: Schematic uses inverted Y-axis
- ❌ **Grid alignment**: All positions should be grid-aligned (1.27mm)
- ❌ **Missing junctions**: Wire crossings need junctions for connectivity
- ❌ **Pin position errors**: Verify against KiCAD's symbol library
- ❌ **Type hints incomplete**: Use `mypy --strict` (no Any)
- ❌ **No error handling**: Non-existent components should return None
- ❌ **Hardcoded values**: Use parameters/constants
- ❌ **No reference tests**: Complex features need manual KiCAD validation

---

**For detailed review**: See `/PR_REVIEW_CHECKLIST_PIN_CONNECTION.md`
