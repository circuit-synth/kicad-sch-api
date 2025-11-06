# Code Review Checklist Usage Guide

**How to use the comprehensive code review checklists for pin connection PRs.**

---

## Overview

Three complementary documents have been created for reviewing pin connection PRs:

1. **`PR_REVIEW_CHECKLIST_PIN_CONNECTION.md`** (Comprehensive)
   - 14 detailed sections with all review criteria
   - Used for thorough, deep reviews
   - ~2-3 hours per PR
   - Best for: First-time reviews, complex features, architectural changes

2. **`PR_REVIEW_QUICK_CHECKLIST.md`** (Quick Reference)
   - Abbreviated version of comprehensive checklist
   - Can be copied into PR descriptions
   - ~45 minutes per PR
   - Best for: Routine reviews, follow-up PRs, simple features

3. **`GITHUB_PR_TEMPLATE_PIN_CONNECTION.md`** (PR Template)
   - Template for authors to use when creating PRs
   - Self-checking during development
   - Can be pasted directly into GitHub PR description
   - Best for: Preparing for review, ensuring completeness

---

## Choosing Your Approach

### For Pull Request Authors

**Before submitting PR:**

1. Copy `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md` into your PR description
2. Complete all sections as you develop the feature
3. Run all checks locally before submitting:
   ```bash
   uv run pytest tests/ -v
   coverage report -m kicad_sch_api/
   uv run black kicad_sch_api/ tests/
   uv run isort kicad_sch_api/ tests/
   uv run mypy kicad_sch_api/ --strict
   uv run flake8 kicad_sch_api/ tests/
   ```
4. Use `PR_REVIEW_QUICK_CHECKLIST.md` as a final self-review
5. Submit PR with all items checked

### For PR Reviewers

**Choose based on available time:**

| Time Available | Use This | Purpose |
|---|---|---|
| 15 minutes | "Common Issues" section of quick checklist | Spot obvious problems |
| 45 minutes | Quick checklist (all sections) | Routine review |
| 2-3 hours | Comprehensive checklist | Deep review |

**Typical Review Workflow:**

```
1. Read PR description (5 min)
2. Skim code changes (10 min)
3. Check quick checklist items (30 min)
4. Run tests locally if needed (10 min)
5. Leave comments on specific issues (10 min)
Total: ~45-65 minutes
```

### For Maintainers

**Managing reviews:**

1. Assign comprehensive checklist to first reviewer
2. Assign quick checklist to second reviewer
3. Use "Common Issues" section in PR comments if rejecting
4. Require all checklist items checked before merge

---

## How to Use the Comprehensive Checklist

### For Deep Reviews (2-3 hours)

**Phase 1: Planning (10 minutes)**
- [ ] Read PR title and description
- [ ] Understand the GitHub issue
- [ ] Check which track(s) are affected (A, B, or C)
- [ ] Note the issue type (Feature, Fix, Test, etc)

**Phase 2: Functional Review (30 minutes)**
- [ ] Section 1: Functional Correctness
- [ ] Section 8: Track-Specific Items (your track)
- [ ] Verify coordinate system handling (critical!)
- [ ] Check error handling

**Phase 3: Testing Review (25 minutes)**
- [ ] Section 2: Testing (coverage, test quality)
- [ ] Run tests locally if possible
- [ ] Verify reference tests compare against manual KiCAD
- [ ] Check test data is realistic

**Phase 4: Code Quality (20 minutes)**
- [ ] Section 4: Code Quality
- [ ] Verify all quality checks pass
- [ ] Check type hints and naming conventions
- [ ] Verify no hardcoded values

**Phase 5: Logging & Docs (15 minutes)**
- [ ] Section 3: Logging
- [ ] Section 5: Documentation
- [ ] Verify entry/exit logs present
- [ ] Check docstrings are complete

**Phase 6: Final Checks (10 minutes)**
- [ ] Section 7: Git Hygiene
- [ ] Section 10: Final Checks
- [ ] Section 12: Common Issues
- [ ] Decision: Approve, Request Changes, or Comment

---

## How to Use the Quick Checklist

### For Routine Reviews (45 minutes)

**Flow:**

1. **Copy quick checklist** into PR comments (or keep locally)

2. **Functional Correctness** (5 min)
   - Mark items as checked while reviewing
   - Comment on any issues found
   - Focus on the bold items first

3. **Testing** (10 min)
   - Verify test coverage >95%
   - Check tests pass
   - Skim test code briefly

4. **Logging & Code Quality** (15 min)
   - Verify DEBUG logs at entry/exit
   - Check code quality checks pass
   - Type hints complete

5. **Track-Specific** (10 min)
   - Focus on items in your assigned track
   - Verify feature-specific requirements

6. **Final Decision** (5 min)
   - All checked: "Approved"
   - Some unchecked: "Request Changes" with comments
   - Small issues: "Comment" for minor fixes

---

## How to Use the PR Template

### As a PR Author

**When creating a new PR:**

1. Click "Use PR template" when creating PR (if configured)
2. Or copy `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md` into description
3. Fill in all sections as you create the PR
4. Edit during development to keep it current
5. Complete all checklists before final submission

**Use it to self-review:**
- Go through each section
- Check boxes as you verify compliance
- Leave comments in ``` ``` blocks for issues
- Use track-specific section for your feature

**Before marking "Ready for Review":**
- [ ] All "Acceptance Criteria" checked
- [ ] All "Testing" items verified
- [ ] All "Code Quality" items passing
- [ ] All "Performance" items within targets
- [ ] Track-specific section complete

---

## Mapping Issues to Checklists

### By GitHub Issue Number

| Issue | Feature | Track | Key Sections |
|-------|---------|-------|--------------|
| #200 | get_component_pins | A | 8.1, Testing |
| #201 | find_pins_by_name | A | 8.1, Testing |
| #202 | connect_pins routing | B | 8.2, Section 1.3 |
| #203 | auto-junction detection | B | 8.2, Section 1.3 |
| #204 | connectivity validation | B | 8.2, Section 1.3 |
| #205 | testing infrastructure | C | 8.3, Section 2 |
| #206 | reference KiCAD circuits | C | 8.3, Section 2.3 |
| #207 | pin operation logging | A,B,C | Section 3, 8.3 |
| #208 | documentation | C | Section 5, 8.3 |

### By Track

| Track | Issues | Focus Areas | Reviewers |
|-------|--------|-------------|-----------|
| A: Pin Discovery | #200, #201, #207 | Sections 8.1, Logging, Type hints | Developer A |
| B: Wire Routing | #202, #203, #204 | Sections 8.2, Geometry, Algorithm complexity | Developer B |
| C: Testing & Docs | #205, #206, #208 | Sections 8.3, Testing, Documentation | QA/Docs team |

---

## Common Review Scenarios

### Scenario 1: Reviewing Pin Discovery PR (#200)

**Time: 45 minutes**

1. Check it solves #200 (get_component_pins implementation)
2. Focus on:
   - Functional: Pin positions match KiCAD (1.2)
   - Testing: >95% coverage, includes rotation tests (2.1-2.3)
   - Track A items (8.1)
   - Common issues: Y-axis, grid alignment, type hints
3. Use quick checklist or comprehensive section 8.1

**Approval criteria:**
- ✓ Pin positions verified against KiCAD
- ✓ All rotations (0°, 90°, 180°, 270°) work
- ✓ Handles mirrored components
- ✓ >95% test coverage
- ✓ Entry/exit logging present
- ✓ Type hints complete
- ✓ Performance <50ms

### Scenario 2: Reviewing Wire Routing PR (#202)

**Time: 1-2 hours**

1. Check it solves #202 (orthogonal routing)
2. Focus on:
   - Functional: Routing algorithm, grid snapping (1.3)
   - Algorithm complexity (6.2)
   - Coordinate system (1.2) - critical!
   - Testing: Routes match reference KiCAD (2.3)
   - Track B items (8.2)
3. Use comprehensive checklist sections 1.3, 6, 8.2

**Approval criteria:**
- ✓ Direct, orthogonal, h-first, v-first all work
- ✓ Corners snap to grid
- ✓ Endpoints exactly at pin positions
- ✓ Reference tests validate routing
- ✓ Performance <50ms
- ✓ Algorithm complexity reasonable
- ✓ Logging at each routing step

### Scenario 3: Reviewing Documentation PR (#208)

**Time: 30 minutes**

1. Check it solves #208 (documentation)
2. Focus on:
   - Documentation quality (5.1, 5.2)
   - Examples accuracy (test by running examples)
   - Completeness (all 4 docs created)
   - Accuracy (matches actual implementation)
   - Track C items (8.3)
3. Use quick checklist documentation section

**Approval criteria:**
- ✓ User guide clear and complete
- ✓ API reference accurate
- ✓ Architecture doc helpful
- ✓ Troubleshooting covers common issues
- ✓ All examples tested and working
- ✓ Accessible language (not too technical)

---

## Handling Different Review Scenarios

### Review with Issues Found

**If you find issues:**

1. List them clearly in PR comment:
   ```
   ### Issues Found

   1. Coordinate system: Y-negation not happening before rotation
   2. Test coverage: 87% (need >95%)
   3. Missing: Error handling for component not found
   ```

2. Use appropriate GitHub labels:
   - "request-changes" if blocking
   - "needs-review" if minor fixes
   - "wip" if work in progress

3. Mark as "Request Changes" (don't approve yet)

4. Author will respond with fixes

5. You can "approve" after verification

### Review with Minor Issues Only

**If only minor issues (cosmetic, documentation):**

1. List them in PR comment
2. Use "Comment" review type (not "Request Changes")
3. Author can fix before/after merge
4. You can approve after author confirms fixes

### Review with No Issues

**If everything looks good:**

1. Check all items in appropriate checklist
2. Leave approval comment summarizing review
3. Use "Approve" review type
4. PR can be merged after 1-2 approvals

---

## Special Cases

### Large PRs (>500 lines)

- [ ] Request split into smaller PRs if possible
- [ ] If must review whole PR:
  - [ ] Use comprehensive checklist
  - [ ] Spend more time on critical sections
  - [ ] May need 3+ hours
  - [ ] Focus on sections 1, 2, 3, 8

### Complex Features (Orthogonal Routing, Routing Algorithm)

- [ ] Use comprehensive checklist
- [ ] Extra focus on algorithm complexity (6.2)
- [ ] Verify against reference KiCAD circuits
- [ ] Performance testing may be needed
- [ ] May require 2-3 reviewer passes

### Documentation-Only PRs (#208)

- [ ] Use quick checklist
- [ ] Focus on section 5 of comprehensive
- [ ] Verify examples work
- [ ] Check technical accuracy
- [ ] Shorter review (30-45 min)

### Infrastructure PRs (#205, #206)

- [ ] Focus on usability (can others use these fixtures?)
- [ ] Check examples are included
- [ ] Verify documentation exists
- [ ] May need 1-2 hours

---

## Tips for Effective Reviews

### Before You Review

1. **Have the code open** in editor/IDE
2. **Have tests running** locally if possible
3. **Know the issue** - read the GitHub issue first
4. **Have the right checklist** based on issue type
5. **Block 45 minutes** minimum for undistracted review

### During Review

1. **Start with quick scan** - look for obvious issues
2. **Focus on critical items first**:
   - Functional correctness
   - Test coverage
   - Logging
   - Code quality checks
3. **Deep dive as needed** for specific sections
4. **Try running the code** if complex
5. **Leave clear comments** with actionable feedback

### After Review

1. **Summarize findings** in approval/request comment
2. **Use clear labels** (approved, changes-requested, etc)
3. **Be constructive** - help author improve
4. **Follow up** after author makes changes

### Red Flags (Request Changes)

Stop and request changes if you find:

- ❌ Test coverage <95%
- ❌ Code quality checks fail
- ❌ No entry/exit logging
- ❌ Hardcoded values
- ❌ Coordinate system handled incorrectly
- ❌ Breaking changes to public API
- ❌ Security/injection vulnerabilities
- ❌ Algorithm has serious flaws
- ❌ Performance way over targets
- ❌ Documentation missing/inaccurate

---

## Continuous Improvement

### Tracking Issues Found

Keep a log of issues commonly found:

| Issue | Frequency | Prevention |
|-------|-----------|-----------|
| Y-axis confusion | Very High | Add to CLAUDE.md |
| Missing logging | High | Template reminder |
| Type hints incomplete | High | CI check required |
| Coverage <95% | Medium | Enforce in CI |

### Updating Checklists

Review checklists quarterly:
- [ ] What issues are still being missed?
- [ ] What items always pass without effort?
- [ ] Are new patterns emerging?
- [ ] Update checklist based on learnings

---

## Resources

### Related Documents

- `CLAUDE.md` - KiCAD coordinate system (CRITICAL)
- `MCP_PIN_CONNECTION_STRATEGY.md` - Implementation approach
- `GITHUB_ISSUES_PIN_CONNECTION.md` - All issue specifications
- `docs/CONNECTIVITY_IMPLEMENTATION_PLAN.md` - Connectivity approach

### Code References

- `kicad_sch_api/core/geometry.py` - Y-negation example
- `kicad_sch_api/core/pin_utils.py` - Pin positioning
- `tests/test_pin_positioning.py` - Test examples
- `tests/test_pin_to_pin_wiring.py` - Wiring examples

### Testing

- `tests/conftest.py` - Shared fixtures
- `tests/reference_kicad_projects/` - Reference circuits
- `tests/unit/test_pin_rotation.py` - Rotation tests

---

## FAQ

**Q: How long should a review take?**

A: 45 min (quick) to 3 hours (comprehensive), depending on complexity.

**Q: Can I use just the quick checklist?**

A: Yes, for routine reviews. Use comprehensive for complex features.

**Q: What if the PR is huge?**

A: Request split into smaller PRs. Or allocate 3+ hours for comprehensive review.

**Q: Should the author use the template?**

A: Yes! It helps them self-review and makes your review faster.

**Q: What if I disagree with design?**

A: Comment during review, not approval. Discuss before major refactoring.

**Q: Can I approve with outstanding comments?**

A: Only if they're minor (cosmetic, documentation). Otherwise request changes.

---

**Last Updated**: 2025-11-06
**Version**: 1.0
**Maintained by**: Claude Code (Anthropic)
