# MCP Pin Connection Implementation - Master Plan

**Status**: Ready for Execution
**Duration**: 2 weeks
**Team Size**: 5-6 developers (3 parallel tracks)
**Date Created**: 2025-11-06

---

## Quick Start

### Prerequisites
- All team members have read `CLAUDE.md` (coordinate system critical!)
- Development environment set up: `uv pip install -e ".[dev]"`
- Git configured: `git config --global user.name "[Name]"` and `git config --global user.email "[Email]"`

### Day 0 - Setup (2 hours)

```bash
# 1. Navigate to repo
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# 2. Ensure main is up-to-date
git checkout main
git pull origin main

# 3. Create feature branches
git checkout -b feature/pin-discovery main
git checkout main
git checkout -b feature/wire-routing main
git checkout main
git checkout -b feature/testing-and-docs main

# 4. Create worktrees
git worktree add ../kicad-sch-api-track-a feature/pin-discovery
git worktree add ../kicad-sch-api-track-b feature/wire-routing
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs

# 5. Verify
git worktree list
```

### Day 1+ - Development

Each track works independently following their specific guidelines. See below for details.

---

## Document Structure

This master plan references three critical documents that must be read in order:

### 1. **GITHUB_ISSUES_PIN_CONNECTION.md** ← START HERE
- All GitHub issues with detailed requirements
- User story templates
- Acceptance criteria
- Implementation details for each issue

**Action**: Create GitHub issues using templates in this document

### 2. **GIT_WORKTREE_PARALLEL_DEVELOPMENT.md**
- Parallel track setup
- Daily workflow for each track
- Merge procedures
- Conflict prevention strategy

**Action**: Set up git worktrees for each track

### 3. **TESTING_AND_LOGGING_GUIDELINES.md**
- Logging requirements at every critical point
- Test structure and standards
- Code quality checks
- Debugging procedures

**Action**: Follow these standards in ALL code written

---

## The Three Parallel Tracks

### Track A: Pin Discovery (3 days)
**Issues**: #200, #201, #207
**Focus**: Enable AI to discover pins and connect them semantically
**Files**: `collections/components.py`, `core/types.py`, tests

**Key Deliverables**:
- ✅ `get_component_pins()` - List all pins with metadata
- ✅ `find_pins_by_name()` - Semantic pin lookup ("VCC", "CLK", etc.)
- ✅ Comprehensive DEBUG logging
- ✅ >95% test coverage

**Team**: 2 developers

**Timeline**:
- Day 1: Issue #200 (get_component_pins)
- Day 2: Issue #201 (find_pins_by_name)
- Day 3: Issue #207 (logging throughout)

---

### Track B: Wire Routing & Junctions (4 days)
**Issues**: #202, #203, #204
**Focus**: Smart wire routing and automatic junction creation
**Files**: `core/schematic.py`, `core/geometry.py`, managers/wire.py, tests

**Key Deliverables**:
- ✅ Orthogonal routing (L-shape connections)
- ✅ Automatic routing strategy selection
- ✅ Automatic junction detection and creation
- ✅ Connectivity validation tools
- ✅ >95% test coverage

**Team**: 2 developers

**Timeline**:
- Day 1-2: Issue #202 (orthogonal routing)
- Day 2-3: Issue #203 (auto-junctions)
- Day 3-4: Issue #204 (validation)

**Dependency**: Requires #200 merged to main before pulling

---

### Track C: Testing & Documentation (3 days)
**Issues**: #205, #206, #208
**Focus**: Test infrastructure and comprehensive documentation
**Files**: Tests, reference circuits, docs

**Key Deliverables**:
- ✅ Test fixtures and helpers
- ✅ 5 reference KiCAD circuits
- ✅ User guide for pin connections
- ✅ API reference documentation
- ✅ Troubleshooting guide

**Team**: 1-2 people (QA + optional developer)

**Timeline**:
- Day 1: Issue #206 (create KiCAD reference circuits)
- Day 2: Issue #205 (test infrastructure)
- Day 3: Issue #208 (documentation)

**Parallel**: Can work independently while Tracks A & B code

---

## Critical Success Factors

### 1. Pin Positioning Accuracy
**Why**: If pins are wrong, everything downstream is wrong
**How**: Use existing `apply_transformation()` code from v0.5.0
**Test**: Reference tests validate against actual KiCAD schematics
**Resources**: `MCP_PIN_CONNECTION_STRATEGY.md` section "Current State"

### 2. Comprehensive Logging
**Why**: Users will report issues we can't reproduce
**How**: DEBUG logs at entry, intermediate steps, and exit
**Tests**: Logging visible in test output
**Standards**: `TESTING_AND_LOGGING_GUIDELINES.md` logging section

### 3. Reference KiCAD Circuits
**Why**: Only way to validate we match KiCAD exactly
**How**: Create manually in KiCAD, commit to repo
**Circuits Needed**:
1. voltage_divider/ - 2 resistors with wire
2. led_circuit/ - LED with series resistor
3. parallel_resistors/ - Multiple parallel paths
4. complex_circuit/ - Op-amp circuit
5. ic_connections/ - Multi-pin IC connections

**Timeline**: Day 6 (collaborative - user creates circuits, developers analyze)

### 4. Test-Driven Development
**Why**: Catch bugs early, clear requirements
**How**: Write tests FIRST, then implementation
**Coverage**: >95% on all new code
**Execution**: Run `uv run pytest tests/ -v` before every commit

### 5. Clean Git History
**Why**: Future developers need clear change history
**How**: Small commits with meaningful messages
**Format**: `feat(#200): add get_pins_info method`
**Frequency**: Commit after every small feature

---

## Daily Standup Template

### Questions to Answer

1. **What did I complete yesterday?**
   - Specific issue(s) closed
   - Tests written and passing
   - Code reviewed

2. **What am I working on today?**
   - Specific issue number
   - Expected deliverables
   - Potential blockers

3. **Are there any blockers?**
   - Dependencies not ready?
   - Design questions?
   - Test failures?

### Example

```
Track A - Developer 1:
- Yesterday: Completed #200 (get_component_pins with all tests passing)
- Today: Starting #201 (find_pins_by_name)
- Blockers: None

Track B - Developer 2:
- Yesterday: Set up routing algorithms, basic tests
- Today: Implementing orthogonal L-shape routing
- Blockers: Waiting for #200 to merge to main (needed for pin discovery)

Track C - QA:
- Yesterday: Created voltage_divider reference circuit
- Today: Creating remaining 4 reference circuits with user
- Blockers: Need KiCAD access (have it)
```

---

## Code Review Checklist

**Before each PR/merge, reviewer checks**:

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Coverage >95%: `--cov=kicad_sch_api`
- [ ] Type checking passes: `uv run mypy kicad_sch_api/ --strict`
- [ ] Linting passes: `uv run flake8 kicad_sch_api/ tests/`
- [ ] Formatting correct: `uv run black --check kicad_sch_api/`
- [ ] All critical operations have DEBUG logging
- [ ] Docstrings complete and accurate
- [ ] No credentials/secrets in logs
- [ ] Commit messages are clear
- [ ] Changes match the GitHub issue description

---

## Weekly Milestones

### Week 1 (Days 1-5)

**Monday-Tuesday**:
- Track A: Issue #200 complete (get_component_pins)
- Track B: Starts issue #202 (routing)
- Track C: Starts issue #206 (reference circuits)

**Wednesday**:
- Track A: Issue #200 merged to main
- Track B: Pulls main changes, continues #202
- Track C: Reference circuits created with user input

**Thursday**:
- Track A: Issue #201 complete (find_pins_by_name)
- Track B: Issue #202 complete, starting #203
- Track C: Issue #205 (test infrastructure)

**Friday**:
- Track A: Issue #207 complete (logging)
- Track B: Issue #203 complete, starting #204
- Track C: Issue #205 complete

**End of Week 1**:
- ✅ Core pin discovery functionality ready
- ✅ Reference circuits created
- ✅ Test infrastructure in place

### Week 2 (Days 6-10)

**Monday**:
- Track A: All issues merged, helping with integration
- Track B: Issue #204 (validation) in progress
- Track C: Issue #208 (documentation) in progress

**Tuesday-Wednesday**:
- All tracks: Merging to main
- Track B: Final validation testing

**Thursday-Friday**:
- Integration testing across all features
- Documentation refinement
- Final code quality checks
- Prepare for release

**End of Week 2**:
- ✅ All code complete and tested
- ✅ Documentation complete
- ✅ Reference circuits validated
- ✅ Ready for Phase 1 completion

---

## Risk Mitigation

### Risk 1: Pin Position Errors
**Likelihood**: Low (existing code proven)
**Impact**: High (cascading failures)
**Mitigation**:
- Use proven `apply_transformation()` from v0.5.0
- Extensive reference testing against KiCAD
- DEBUG logging at every calculation step

### Risk 2: Test Coverage Gaps
**Likelihood**: Medium
**Impact**: Medium (bugs escape to production)
**Mitigation**:
- Require >95% coverage for all PRs
- Review coverage reports in code review
- Use parametrized tests for edge cases

### Risk 3: Git Merge Conflicts
**Likelihood**: Low (if files segregated properly)
**Impact**: Medium (development delays)
**Mitigation**:
- Enforce file ownership per track
- Small, frequent commits
- Pull main daily to stay in sync

### Risk 4: AI Users Don't Understand Pins
**Likelihood**: Medium
**Impact**: High (poor user experience)
**Mitigation**:
- Comprehensive error messages
- User guide with examples
- Claude conversation examples
- Logging for debugging user issues

### Risk 5: Reference Circuits Not Ready
**Likelihood**: Low
**Impact**: Medium (can't validate)
**Mitigation**:
- Create early (Day 6)
- Work with user directly
- Simple first, complex later

---

## Definition of "Done"

### For Each Issue

- [ ] Code implementation complete
- [ ] >95% test coverage
- [ ] All tests passing
- [ ] DEBUG logging added to critical points
- [ ] Docstrings complete
- [ ] Code review approved
- [ ] Merged to main
- [ ] Documented in MCP_TOOLS.md

### For Each Track

- [ ] All issues complete
- [ ] All PRs merged
- [ ] Full test suite passes
- [ ] Code quality checks pass
- [ ] No technical debt

### For Phase 1 (Pin Connection)

- [ ] All 8 issues complete
- [ ] Can create voltage divider via MCP
- [ ] Can create LED circuit via MCP
- [ ] Pin positions accurate
- [ ] Orthogonal routing working
- [ ] Auto-junctions working
- [ ] Validation tools working
- [ ] Documentation complete
- [ ] Reference circuits validated
- [ ] Ready for user feedback

---

## Integration Checklist

### Before Final Merge to Main

```bash
# 1. All tracks complete
[ ] Track A: All PRs merged
[ ] Track B: All PRs merged
[ ] Track C: All PRs merged

# 2. Full test suite
[ ] All tests pass: uv run pytest tests/ -v
[ ] Coverage >95%: uv run pytest --cov

# 3. Code quality
[ ] Black: uv run black --check kicad_sch_api/
[ ] Isort: uv run isort --check kicad_sch_api/
[ ] MyPy: uv run mypy kicad_sch_api/ --strict
[ ] Flake8: uv run flake8 kicad_sch_api/

# 4. Reference validation
[ ] All reference circuits load
[ ] Pin positions match KiCAD
[ ] Wire routing valid

# 5. Documentation
[ ] MCP_PIN_CONNECTION_USER_GUIDE.md complete
[ ] API_REFERENCE_PIN_TOOLS.md complete
[ ] TROUBLESHOOTING_PIN_ISSUES.md complete
[ ] All docstrings accurate

# 6. Manual testing
[ ] Can create voltage divider via Claude
[ ] Can create LED circuit via Claude
[ ] Errors produce clear messages
[ ] Logging shows detailed flow
```

---

## Resources & Links

### Documentation (Read First)

1. `CLAUDE.md` - ⚠️ CRITICAL: KiCAD coordinate system
2. `MCP_PIN_CONNECTION_STRATEGY.md` - Strategic overview
3. `GITHUB_ISSUES_PIN_CONNECTION.md` - All GitHub issues
4. `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md` - Git workflow
5. `TESTING_AND_LOGGING_GUIDELINES.md` - Code standards

### GitHub

- Project Board: "Phase 1 - Pin Connection"
- Epic: #199
- Issues: #200-#208
- Labels: mcp-server, pin-discovery, wire-routing, phase-1

### Code References

- Pin positioning: `kicad_sch_api/core/pin_utils.py`
- Transformations: `kicad_sch_api/core/geometry.py`
- Schematic API: `kicad_sch_api/core/schematic.py`
- Existing tests: `tests/unit/test_pin_*.py`

### Key Files to Create

**Track A**:
- `tests/unit/test_get_component_pins.py`
- `tests/unit/test_find_pins_by_name.py`
- `mcp_server/tools/component_tools.py`

**Track B**:
- `tests/unit/test_orthogonal_routing.py`
- `tests/unit/test_junction_detection.py`
- `tests/unit/test_connectivity_validation.py`

**Track C**:
- `tests/mcp_server/conftest.py`
- `tests/helpers/pin_helpers.py`
- `tests/reference_kicad_projects/voltage_divider/.kicad_sch`
- `docs/MCP_PIN_CONNECTION_USER_GUIDE.md`

---

## Success Metrics

### Functional Success
- ✅ Can discover all pins on any component
- ✅ Can find pins by semantic name
- ✅ Can connect two pins with professional orthogonal routing
- ✅ Automatic junctions created where wires meet
- ✅ Connectivity validated before save
- ✅ AI assistants can create complete circuits via Claude

### Quality Success
- ✅ >95% test coverage
- ✅ 100% type coverage (mypy --strict)
- ✅ All new code has DEBUG logging
- ✅ All functions documented
- ✅ Reference circuits validated
- ✅ Zero critical bugs

### Process Success
- ✅ Parallel tracks completed on schedule
- ✅ Minimal git conflicts
- ✅ Clean commit history
- ✅ All PRs reviewed and approved
- ✅ Team communicated effectively

---

## Next Steps

### Immediate (Today)

1. ✅ Read all 5 documents
2. ✅ Create GitHub issues (#199-#208)
3. ✅ Set up git worktrees
4. ✅ Assign developers to tracks
5. ✅ Schedule daily standups

### This Week

1. Execute Track A, B, C Day 1
2. Run daily standups
3. Push code to branches regularly
4. Review test coverage

### Next Week

1. Integrate all tracks
2. Final testing and validation
3. Documentation polish
4. Prepare for user feedback

---

## Questions?

**For specifics on each issue**: See `GITHUB_ISSUES_PIN_CONNECTION.md`
**For git workflow**: See `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
**For code standards**: See `TESTING_AND_LOGGING_GUIDELINES.md`
**For pin positioning**: See `MCP_PIN_CONNECTION_STRATEGY.md`
**For KiCAD coordinate system**: See `CLAUDE.md`

---

**Status**: 🟢 Ready to Launch
**Target Start Date**: Tomorrow (Day 1)
**Expected Completion**: 2 weeks (Week 2, Friday)
**Team Size**: 5-6 developers
**Success Probability**: 85% (with discipline on logging/testing)

**LET'S BUILD THIS! 🚀**
