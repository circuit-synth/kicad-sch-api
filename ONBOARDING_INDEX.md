# Onboarding Documentation Index

**Last Updated**: 2025-11-06
**Purpose**: Quick navigation to all onboarding materials

---

## Start Here (First 30 Minutes)

Read these three documents in this exact order:

### 1. `/ONBOARDING_QUICK_REFERENCE.md` (5 minutes)
- **What**: Single-page quick reference card
- **Contains**: Day 1 checklist, critical concepts, quick commands
- **Best for**: Fast initial understanding, easy to scan
- **Action**: Read this first, bookmark it

### 2. `/DEVELOPER_ONBOARDING.md` (45 minutes)
- **What**: Comprehensive onboarding guide (829 lines)
- **Contains**: Quick start, track-specific setup, common questions, checklists
- **Best for**: Thorough understanding, reference during development
- **Action**: Read completely for your track, skim other sections

### 3. `/CLAUDE.md` - Sections 1-3 (10 minutes)
- **What**: KiCAD coordinate system explanation
- **Contains**: The TWO coordinate systems, Y-axis inversion, examples
- **Best for**: Understanding pin position calculations
- **Action**: CRITICAL - must understand before writing pin code
- **Location**: `/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/CLAUDE.md`

**Total Time**: ~60 minutes, then you're ready to start coding

---

## Essential Reading by Topic

### Understanding What You're Building

1. **`START_HERE.md`** (9 minutes)
   - Overview of entire project
   - What the 8 GitHub issues are
   - 3 parallel tracks
   - Quick timeline

2. **`MCP_PIN_CONNECTION_STRATEGY.md`** (15 minutes)
   - Why pin connection is critical
   - Current gaps in the library
   - What you're solving
   - Technical recommendations

3. **Your Issue Spec** (20 minutes)
   - Location: `GITHUB_ISSUES_PIN_CONNECTION.md`
   - Search for your issue (#200, #202, #205, etc.)
   - Read: User Story, Acceptance Criteria, Implementation Details
   - This is your blueprint

### Environment Setup & Git Workflow

1. **`GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`** (15 minutes)
   - How to set up your worktree
   - Daily git workflow
   - How to avoid conflicts
   - Merge procedures

2. **`MCP_IMPLEMENTATION_MASTER_PLAN.md`** (15 minutes)
   - High-level execution plan
   - Critical success factors
   - Daily standup template
   - Risk mitigation

### Code Quality Standards

1. **`TESTING_AND_LOGGING_GUIDELINES.md`** (30 minutes)
   - Logging standards and templates
   - Testing patterns and examples
   - Code quality requirements
   - Debugging procedures
   - Copy-paste ready code examples

2. **`IMPLEMENTATION_READINESS_CHECKLIST.md`** (5 minutes)
   - Status of all deliverables
   - What's ready to code
   - Priority ordering

---

## By Track

### Track A: Pin Discovery
**Total Reading Time**: 1 hour

1. **DEVELOPER_ONBOARDING.md** - Section "Track A: Pin Discovery"
2. **GITHUB_ISSUES_PIN_CONNECTION.md** - Issues #200, #201, #207
3. **TESTING_AND_LOGGING_GUIDELINES.md** - Full document
4. **CLAUDE.md** - Section 1 (coordinate system)

**Key Files You'll Modify**:
- `kicad_sch_api/core/types.py`
- `kicad_sch_api/collections/components.py`
- Tests in `tests/unit/`

---

### Track B: Wire Routing
**Total Reading Time**: 1 hour

1. **DEVELOPER_ONBOARDING.md** - Section "Track B: Wire Routing"
2. **GITHUB_ISSUES_PIN_CONNECTION.md** - Issues #202, #203, #204
3. **MCP_PIN_CONNECTION_STRATEGY.md** - Sections "Problem 2" and "Problem 3"
4. **TESTING_AND_LOGGING_GUIDELINES.md** - Full document

**Key Files You'll Modify**:
- `kicad_sch_api/core/schematic.py`
- `kicad_sch_api/core/geometry.py`
- `kicad_sch_api/managers/wire.py`
- Tests in `tests/unit/`

---

### Track C: Testing & Documentation
**Total Reading Time**: 1 hour

1. **DEVELOPER_ONBOARDING.md** - Section "Track C: Testing & Documentation"
2. **GITHUB_ISSUES_PIN_CONNECTION.md** - Issues #205, #206, #208
3. **TESTING_AND_LOGGING_GUIDELINES.md** - FULL DOCUMENT (entire file)
4. **tests/README.md** - How tests are organized

**Key Files You'll Create**:
- Test fixtures in `tests/conftest.py`
- Reference circuits in `tests/reference_kicad_projects/`
- Documentation in `docs/`

---

## Reference Documents (Keep These Nearby)

### Specification Documents
- **`GITHUB_ISSUES_PIN_CONNECTION.md`** (1200 lines)
  - All 8 issue specs with complete details
  - Acceptance criteria for each
  - Implementation guidance
  - Testing requirements

### Planning & Strategy Documents
- **`MCP_IMPLEMENTATION_MASTER_PLAN.md`** (400 lines)
- **`MCP_PIN_CONNECTION_STRATEGY.md`** (600 lines)
- **`MCP_SERVER_SUMMARY.md`** (400 lines)
- **`START_HERE.md`** (300 lines)

### Technical Guides
- **`CLAUDE.md`** (700 lines) - KiCAD coordinate system (CRITICAL)
- **`TESTING_AND_LOGGING_GUIDELINES.md`** (800 lines)
- **`GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`** (400 lines)

---

## When You Have Questions

### "What should I code?"
→ Find your issue in `GITHUB_ISSUES_PIN_CONNECTION.md`

### "How do I set up git?"
→ Read `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`

### "How do I test my code?"
→ See `TESTING_AND_LOGGING_GUIDELINES.md` section "Test Templates"

### "How do I write good logging?"
→ See `TESTING_AND_LOGGING_GUIDELINES.md` section "Logging Templates"

### "Why are pins backwards?"
→ Read `CLAUDE.md` section 1 (Y-axis inversion)

### "What's the project structure?"
→ See `DEVELOPER_ONBOARDING.md` section "How do I understand the project structure?"

### "How do I debug?"
→ See `DEVELOPER_ONBOARDING.md` section "How do I debug a test failure?"

### "When do I commit?"
→ See `DEVELOPER_ONBOARDING.md` section "When should I commit?"

### "What if I break something?"
→ See `DEVELOPER_ONBOARDING.md` section "What if I break something?"

---

## Quick Command Reference

### Installation
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
uv pip install -e ".[dev]"
```

### Worktree Setup (Your Track)
```bash
# Create branch
git checkout -b feature/pin-discovery main  # Track A
git checkout -b feature/wire-routing main   # Track B
git checkout -b feature/testing-and-docs main  # Track C

# Create worktree
git worktree add ../kicad-sch-api-track-a feature/pin-discovery
git worktree add ../kicad-sch-api-track-b feature/wire-routing
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs
```

### Daily Development
```bash
# Test
uv run pytest tests/unit/test_your_feature.py -v

# Format & check
uv run black kicad_sch_api/
uv run mypy kicad_sch_api/

# Commit
git commit -m "[TRACK][####] Description"
git push origin your-branch
```

### Full Reference
See `ONBOARDING_QUICK_REFERENCE.md` for all commands

---

## File Map: Where Everything Is

```
/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/

ONBOARDING DOCUMENTS (Read These):
├── ONBOARDING_INDEX.md                    ← You're here
├── ONBOARDING_QUICK_REFERENCE.md          ← Print this!
├── DEVELOPER_ONBOARDING.md                ← Main guide
├── CLAUDE.md                              ← CRITICAL: Coordinates
├── START_HERE.md                          ← Overview

PLANNING & SPECIFICATION:
├── GITHUB_ISSUES_PIN_CONNECTION.md        ← Your issue specs
├── MCP_IMPLEMENTATION_MASTER_PLAN.md      ← Execution plan
├── MCP_PIN_CONNECTION_STRATEGY.md         ← Strategic analysis
├── GIT_WORKTREE_PARALLEL_DEVELOPMENT.md   ← Git workflow
├── TESTING_AND_LOGGING_GUIDELINES.md      ← Code standards
└── IMPLEMENTATION_READINESS_CHECKLIST.md  ← Status

EXISTING PROJECT DOCS:
├── README.md                              ← Project overview
├── docs/GETTING_STARTED.md                ← User guide
├── docs/API_REFERENCE.md                  ← API docs
├── docs/ARCHITECTURE.md                   ← System design
└── tests/README.md                        ← Test structure

CODE DIRECTORIES (What You'll Modify):
├── kicad_sch_api/
│   ├── core/
│   │   ├── types.py                       ← Add PinInfo (Track A)
│   │   ├── pin_utils.py                   ← Pin calculations
│   │   ├── schematic.py                   ← Enhance connect_pins (Track B)
│   │   └── geometry.py                    ← Routing algorithms (Track B)
│   ├── collections/
│   │   └── components.py                  ← Add methods (Track A)
│   └── managers/
│       └── wire.py                        ← Junction detection (Track B)
└── tests/
    ├── conftest.py                        ← Add fixtures (Track C)
    ├── unit/
    │   ├── test_get_component_pins.py      ← Create (Track A)
    │   ├── test_find_pins_by_name.py       ← Create (Track A)
    │   └── test_*.py                       ← Create (Track B)
    ├── integration/
    │   └── test_*.py                       ← Create (Track A/B)
    └── reference_kicad_projects/
        └── */                              ← Create (Track C)
```

---

## Reading Checklist

### Required (Must Read Before Coding)
- [ ] `ONBOARDING_QUICK_REFERENCE.md` (5 min) - Get oriented
- [ ] `CLAUDE.md` Sections 1-3 (10 min) - Understand coordinates
- [ ] `DEVELOPER_ONBOARDING.md` for your track (30 min) - Track setup
- [ ] Your issue spec in `GITHUB_ISSUES_PIN_CONNECTION.md` (20 min) - Know what to build

**Total**: ~65 minutes

### Highly Recommended (Read Before Day 2)
- [ ] `START_HERE.md` (10 min) - Project overview
- [ ] `TESTING_AND_LOGGING_GUIDELINES.md` (30 min) - Code standards
- [ ] `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md` (15 min) - Git workflow

### Reference (Keep Nearby, Use As Needed)
- [ ] `MCP_IMPLEMENTATION_MASTER_PLAN.md` - For daily standups
- [ ] `MCP_PIN_CONNECTION_STRATEGY.md` - For understanding why features matter
- [ ] `IMPLEMENTATION_READINESS_CHECKLIST.md` - For status updates

---

## Quick Onboarding Summary

| Time | Action | Document |
|------|--------|----------|
| 5 min | Print quick reference | `ONBOARDING_QUICK_REFERENCE.md` |
| 10 min | Read critical coordinate info | `CLAUDE.md` Sections 1-3 |
| 30 min | Read track-specific setup | `DEVELOPER_ONBOARDING.md` |
| 20 min | Read your issue spec | `GITHUB_ISSUES_PIN_CONNECTION.md` |
| 5 min | Set up git worktree | `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md` |
| 5 min | Run first test | Your command line |
| **75 min** | **You're ready to code!** | Start your first issue |

---

## Success Metrics

### End of Day 1
- Read all required documents
- Environment installed
- Tests passing
- First commit made

### End of Week 1
- First issue 50% complete
- All tests passing
- Coordinated with other tracks
- No blockers

### End of Week 2
- All assigned issues complete
- >95% test coverage
- Documentation polished
- Ready for user feedback

---

## Still Have Questions?

### Can't find answer in docs?
1. Search `DEVELOPER_ONBOARDING.md` - has 829 lines of Q&A
2. Search `TESTING_AND_LOGGING_GUIDELINES.md` - has code examples
3. Ask your track lead on GitHub/Slack

### Need help with...
- **Git**: See `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
- **Coordinates**: See `CLAUDE.md` Section 1
- **Code specs**: See `GITHUB_ISSUES_PIN_CONNECTION.md`
- **Testing**: See `TESTING_AND_LOGGING_GUIDELINES.md`
- **General**: See `DEVELOPER_ONBOARDING.md`

### Emergency?
See `DEVELOPER_ONBOARDING.md` section "Emergency Troubleshooting"

---

## Next Steps

1. **Right Now**: Read `ONBOARDING_QUICK_REFERENCE.md` (5 min)
2. **Next**: Read `DEVELOPER_ONBOARDING.md` section for your track (30 min)
3. **Then**: Read your issue spec in `GITHUB_ISSUES_PIN_CONNECTION.md` (20 min)
4. **Then**: Set up your worktree using `GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
5. **Then**: Write your first test and make your first commit

**You're all set! Let's build this! 🚀**

---

**Document Version**: 1.0
**Created**: 2025-11-06
**Maintained By**: Development Team
**Questions?**: Check DEVELOPER_ONBOARDING.md Common Questions section
