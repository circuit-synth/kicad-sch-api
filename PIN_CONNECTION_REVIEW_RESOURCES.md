# Pin Connection PR Review Resources

**Complete set of code review checklists and templates for the pin connection implementation (Epic #199 and sub-issues #200-#208).**

---

## Documents Overview

### 1. Comprehensive Code Review Checklist
**File**: `PR_REVIEW_CHECKLIST_PIN_CONNECTION.md`
**Size**: 25 KB | ~500 lines
**Purpose**: Deep, thorough code review of pin connection PRs
**Best For**:
- First-time reviewers
- Complex features (routing algorithms, etc)
- Architectural changes
- Initial reviews of new features

**What It Covers**:
1. Functional Correctness (9 sub-sections)
2. Testing (4 sub-sections)
3. Logging & Debugability (5 sub-sections)
4. Code Quality (5 sub-sections)
5. Documentation (3 sub-sections)
6. Performance (4 sub-sections)
7. Git Hygiene (3 sub-sections)
8. Track-Specific Items (3 tracks × 3-5 items each)
9. Related Components Verification (3 sub-sections)
10. Final Checks (4 sub-sections)
11. Reviewer Sign-Off (section for approval)
12. Common Issues Checklist (10 most common issues)
13. Quick Review Flow (for busy reviewers)
14. Reference Materials (links and examples)

**Time Commitment**: 2-3 hours per PR

**How to Use**:
- Print or open in PDF
- Check items as you review
- Use section 12 (Common Issues) for spot-checking
- Use section 8 (Track-Specific) for your assigned track
- Write sign-off in section 11

---

### 2. Quick Reference Checklist
**File**: `PR_REVIEW_QUICK_CHECKLIST.md`
**Size**: 5 KB | ~100 lines
**Purpose**: Fast, efficient review of pin connection PRs
**Best For**:
- Routine reviews
- Follow-up reviews (after author makes changes)
- Simple features
- Developers with limited review time

**What It Covers**:
- Functional Correctness (9 items)
- Testing (5 items)
- Logging & Debugability (5 items)
- Code Quality (9 items)
- Documentation (4 items)
- Performance (3 items)
- Git Hygiene (5 items)
- Track-Specific Items (15+ items per track)
- Final Checks (3 items)
- Reviewer Sign-Off (section)
- Common Issues (10 most critical)

**Time Commitment**: 45 minutes per PR

**How to Use**:
- Copy and paste into PR description or comments
- Check off items as you verify
- Focus on bold items first
- Use "Common Issues" section for quick spot-checks
- Takes ~5 minutes per section

---

### 3. GitHub PR Template
**File**: `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md`
**Size**: 7 KB | ~200 lines
**Purpose**: Template for PR authors to use when creating PRs
**Best For**:
- PR authors preparing submission
- Self-review before asking for review
- Tracking implementation progress
- Ensuring completeness before review

**What It Covers**:
- PR Description (issue, type, summary)
- Acceptance Criteria Verification (specific to each issue)
- Testing (test suites, coverage, execution results)
- Performance (latency targets, benchmarks)
- Track-Specific Verification (detailed per track)
- Potential Reviewer Questions (FAQ)
- Related Issues (linking)
- Additional Notes
- Reviewer Checklist
- Post-Merge Tasks

**How to Use**:
- Copy into new PR description on GitHub
- Fill in all sections while developing feature
- Edit during development to keep current
- Use as self-review checklist
- Submit PR with all items completed/checked

---

### 4. Checklist Usage Guide
**File**: `CHECKLIST_USAGE_GUIDE.md`
**Size**: 13 KB | ~350 lines
**Purpose**: Guide for how to use all the checklists effectively
**Best For**:
- First-time users of these checklists
- Understanding when to use which checklist
- Learning review best practices
- Mapping issues to specific sections

**What It Covers**:
- Overview of all three documents
- Choosing your review approach (author vs reviewer)
- Deep review workflow (6 phases, 2-3 hours)
- Quick review workflow (45 minutes)
- How to use PR template (as author)
- Mapping issues to checklists
- Common review scenarios (examples)
- Handling different review situations
- Special cases (large PRs, complex features)
- Tips for effective reviews
- Continuous improvement
- FAQ

**How to Use**:
- Read this first if new to pin connection reviews
- Reference appropriate section based on your role
- Follow the workflows for your review type
- Check the mapping table to find relevant sections
- Use scenario examples as templates

---

## Quick Start Guide

### For PR Authors

**Preparing to submit a PR**:

1. **During development**:
   - Reference `CLAUDE.md` for coordinate system details
   - Check `GITHUB_ISSUES_PIN_CONNECTION.md` for acceptance criteria
   - Keep logging in mind (entry/exit at DEBUG level)

2. **Before submitting**:
   - Copy `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md` into PR description
   - Complete all template sections
   - Run all quality checks:
     ```bash
     uv run pytest tests/ -v
     coverage report -m kicad_sch_api/
     uv run black kicad_sch_api/ tests/
     uv run isort kicad_sch_api/ tests/
     uv run mypy kicad_sch_api/ --strict
     uv run flake8 kicad_sch_api/ tests/
     ```
   - Use quick checklist as final self-review

3. **Submit PR**:
   - All template sections completed
   - All quality checks passing
   - Description clearly explains changes
   - Track-specific section for your feature

### For PR Reviewers

**Choosing your review approach**:

| Available Time | Use This | Reference |
|---|---|---|
| 15 min | Common Issues only | Quick Checklist, Section 12 |
| 45 min | Quick Checklist | PR_REVIEW_QUICK_CHECKLIST.md |
| 2-3 hours | Comprehensive Checklist | PR_REVIEW_CHECKLIST_PIN_CONNECTION.md |
| First-time | Usage Guide | CHECKLIST_USAGE_GUIDE.md |

**Basic review flow** (45 minutes):

1. Read PR description (5 min)
2. Skim code changes (10 min)
3. Quick checklist: Functional Correctness (5 min)
4. Quick checklist: Testing (5 min)
5. Quick checklist: Code Quality (10 min)
6. Quick checklist: Track-Specific (5 min)
7. Decision & comments (5 min)

**Deep review flow** (2-3 hours):

1. Read PR description and issue (10 min)
2. Comprehensive checklist Section 1-2 (30 min)
3. Comprehensive checklist Section 3-5 (30 min)
4. Comprehensive checklist Section 6-8 (30 min)
5. Comprehensive checklist Section 9-13 (30 min)
6. Decision & detailed comments (10 min)

### For Maintainers

**Setting up review process**:

1. **Configure GitHub PR template**:
   - Copy `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md` content
   - Set as default in `.github/pull_request_template.md`
   - Or provide link in repository guidelines

2. **Create review labels**:
   - Add to GitHub: "reviewed-approved", "review-requested"
   - Use in project board to track review status

3. **Assign reviewers**:
   - Track A (Pin Discovery): Senior Python developer
   - Track B (Wire Routing): Algorithm/geometry specialist
   - Track C (Testing & Docs): QA/Documentation lead
   - All tracks: Require 1-2 approvals before merge

4. **Require checks**:
   - CI must pass (tests, coverage, code quality)
   - At least 1 approval required
   - All conversations resolved

---

## Document Sizes and Details

| Document | File Size | Sections | Time | Best For |
|----------|-----------|----------|------|----------|
| Comprehensive Checklist | 25 KB | 14 | 2-3 hrs | Deep reviews |
| Quick Checklist | 5 KB | 10 | 45 min | Routine reviews |
| PR Template | 7 KB | 12 | N/A | PR submission |
| Usage Guide | 13 KB | 14 | 30 min | Learning |
| **Total** | **50 KB** | **50** | **N/A** | Complete toolkit |

---

## Key Sections by Issue

### Issue #200: get_component_pins
**Primary Sections**:
- Comprehensive: 1.2, 1.3, 2.1-2.3, 3.1-3.3, 8.1
- Quick: Functional Correctness, Testing, Track A
- **Critical**: Coordinate system (1.2), Pin positions, Test coverage

### Issue #201: find_pins_by_name
**Primary Sections**:
- Comprehensive: 1.1, 2.1-2.3, 4.1-4.3, 8.1
- Quick: Functional Correctness, Testing, Code Quality, Track A
- **Critical**: Pattern matching logic, Error handling

### Issue #202: connect_pins routing
**Primary Sections**:
- Comprehensive: 1.3, 2.2, 6.2, 8.2
- Quick: Functional Correctness, Code Quality, Track B
- **Critical**: Algorithm correctness, Grid snapping, Performance

### Issue #203: auto-junction detection
**Primary Sections**:
- Comprehensive: 1.3, 2.2, 6.2, 8.2
- Quick: Functional Correctness, Track B
- **Critical**: Junction detection accuracy, No false positives

### Issue #204: connectivity validation
**Primary Sections**:
- Comprehensive: 1.1, 2.1, 8.2
- Quick: Functional Correctness, Testing, Track B
- **Critical**: Report generation, Issue detection

### Issue #205: testing infrastructure
**Primary Sections**:
- Comprehensive: 2.1-2.4, 8.3
- Quick: Testing, Track C
- **Critical**: Fixture usability, Extensibility

### Issue #206: reference KiCAD circuits
**Primary Sections**:
- Comprehensive: 2.2-2.3, 8.3
- Quick: Testing, Track C
- **Critical**: Reference circuit quality, Expected values documented

### Issue #207: pin operation logging
**Primary Sections**:
- Comprehensive: 3.1-3.5, 8.3
- Quick: Logging & Debugability, All Tracks
- **Critical**: Entry/exit logging, Debug level, Performance

### Issue #208: documentation
**Primary Sections**:
- Comprehensive: 5.1-5.3, 8.3
- Quick: Documentation, Track C
- **Critical**: Accuracy, Completeness, Examples work

---

## Most Important Sections (Don't Miss!)

### Universal Critical Items
- **Coordinate System Correctness** (Comprehensive 1.2): Y-negation BEFORE rotation
- **Test Coverage >95%** (Comprehensive 2.1): Non-negotiable
- **Entry/Exit Logging** (Comprehensive 3.1): Required for all functions
- **Code Quality Checks Pass** (Comprehensive 4.1): black, isort, mypy, flake8
- **No Hardcoded Values** (Comprehensive 4.3): Parameters/constants only
- **Grid Alignment** (Comprehensive 1.2): All positions 1.27mm grid-aligned

### Track-Specific Critical Items
- **Track A (Pin Discovery)**:
  - Pin positions exactly match KiCAD symbol library
  - All rotations (0°, 90°, 180°, 270°) verified
  - Mirrored components tested

- **Track B (Wire Routing)**:
  - Orthogonal routing produces proper L-shapes
  - Corners snap to grid
  - Endpoints exactly at pin positions
  - Junction detection has no false positives

- **Track C (Testing & Documentation)**:
  - Reference circuits loadable in KiCAD
  - Expected values documented
  - All examples tested and working
  - Clear, accessible writing

---

## Common Review Mistakes to Avoid

### What NOT to Do

- ❌ Skip the coordinate system check
  - It's the most critical concept in this library
  - Every pin positioning feature depends on it

- ❌ Accept <95% test coverage
  - Non-negotiable requirement
  - Use `coverage report -m` to verify

- ❌ Skip logging review
  - Required for maintainability
  - Check section 3.1 carefully

- ❌ Assume grid alignment is OK
  - Must verify positions are 1.27mm multiples
  - Check geometry.snap_to_grid() is used

- ❌ Approve without running tests locally
  - CI can miss edge cases
  - Especially for geometry/routing changes

- ❌ Miss the "Common Issues" section
  - Reviews 10 most-found issues
  - Great for spot-checking

---

## Integration with GitHub

### PR Template Setup

To auto-use this template on PRs:

1. Create `.github/pull_request_template.md`
2. Copy content from `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md`
3. All new PRs will have this template by default

### Issue Template Setup

To create specific issues:

1. Create `.github/ISSUE_TEMPLATE/pin-connection.md`
2. Reference `GITHUB_ISSUES_PIN_CONNECTION.md` for issue specs
3. Use for creating new pin-related issues

### Labels

Create GitHub labels:
- `review-approved` - Ready to merge
- `review-requested` - Waiting for review
- `needs-changes` - Issues found, author response needed
- `pin-discovery` - Track A feature
- `wire-routing` - Track B feature
- `testing-docs` - Track C feature

---

## Related Documentation

These documents provide context and background:

| Document | Purpose | Key Section |
|----------|---------|-------------|
| CLAUDE.md | KiCAD coordinate system | "The Two Coordinate Systems" |
| MCP_PIN_CONNECTION_STRATEGY.md | Implementation strategy | Entire document |
| GITHUB_ISSUES_PIN_CONNECTION.md | Issue specifications | Each issue spec |
| docs/CONNECTIVITY_IMPLEMENTATION_PLAN.md | Connectivity design | Algorithm section |
| docs/ADR.md | Architecture decisions | Design rationale |

---

## FAQ

**Q: Which document should I read first?**
A: Start with this one (PIN_CONNECTION_REVIEW_RESOURCES.md), then CHECKLIST_USAGE_GUIDE.md

**Q: Can I use just the quick checklist?**
A: Yes, for most routine reviews. Use comprehensive for complex features.

**Q: What if I find an issue?**
A: See CHECKLIST_USAGE_GUIDE.md section "Handling Different Review Scenarios"

**Q: Should the PR author fill out the template?**
A: Yes! It helps them self-review and makes your review faster.

**Q: What's the most important thing to check?**
A: Coordinate system correctness (Y-negation before rotation). It's referenced in CLAUDE.md.

**Q: How do I stay consistent with other reviewers?**
A: Use the same checklist (quick or comprehensive). It enforces consistency.

**Q: Can these documents be updated?**
A: Yes, quarterly review recommended. See CHECKLIST_USAGE_GUIDE.md "Continuous Improvement"

---

## Support & Questions

**Having trouble using these checklists?**

1. Check CHECKLIST_USAGE_GUIDE.md section "FAQ"
2. Review specific scenario from "Common Review Scenarios"
3. Reference the mapping table: "Mapping Issues to Checklists"
4. Check example in your assigned track section

**Found an issue with the checklist?**

1. Document the issue
2. Reference the document and line number
3. Suggest improvement
4. Submit as issue with label "documentation"

---

**Last Updated**: 2025-11-06
**Version**: 1.0
**Maintained by**: Claude Code (Anthropic)
**License**: Same as kicad-sch-api (GPL v3)

---

## Document Checklist

All documents created for this review resource set:

- [x] `PR_REVIEW_CHECKLIST_PIN_CONNECTION.md` - Comprehensive (25 KB)
- [x] `PR_REVIEW_QUICK_CHECKLIST.md` - Quick Reference (5 KB)
- [x] `GITHUB_PR_TEMPLATE_PIN_CONNECTION.md` - PR Template (7 KB)
- [x] `CHECKLIST_USAGE_GUIDE.md` - Usage Guide (13 KB)
- [x] `PIN_CONNECTION_REVIEW_RESOURCES.md` - This Index (this file)

**Total Package**: ~50 KB of comprehensive review resources covering all aspects of pin connection PRs.
