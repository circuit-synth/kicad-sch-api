# Developer Onboarding Guide: kicad-sch-api MCP Pin Connection Implementation

**Purpose**: Get new developers up to speed for the Pin Connection & Wire Routing feature track
**Time Commitment**: 1 hour for Quick Start + 30 min for Track-Specific setup
**Last Updated**: 2025-11-06

---

## Table of Contents

1. [5-Minute Quick Start](#5-minute-quick-start)
2. [Track-Specific Onboarding](#track-specific-onboarding)
3. [Common Questions & Answers](#common-questions--answers)
4. [Development Checklist](#development-checklist)
5. [Emergency Troubleshooting](#emergency-troubleshooting)

---

## 5-Minute Quick Start

### Absolute Minimum Reading (READ THESE FIRST)

These documents are non-negotiable. They establish the foundation that everything else builds on.

1. **Read `/CLAUDE.md` - Sections 1-3 (5 minutes)**
   - Location: `/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/CLAUDE.md`
   - What: KiCAD coordinate system (THE MOST CRITICAL CONCEPT)
   - Why: Pin positions are calculated wrong if you don't understand this
   - Key concept: **Y-axis is INVERTED in schematic space** (unlike math)

   **Critical Line**:
   ```python
   # Symbol space (library): Normal Y, +Y is UP
   Pin 1: (0, +3.81)    # 3.81mm UPWARD

   # Schematic space (placed): Inverted Y, +Y is DOWN
   Pin 1: (100, 96.52)  # Lower Y = VISUALLY AT TOP
   ```

2. **Read `/START_HERE.md` (3 minutes)**
   - Location: `/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/START_HERE.md`
   - What: Overview of entire pin connection implementation
   - Why: Gives you the big picture before diving into details
   - Key points: 8 GitHub issues, 3 parallel tracks, 2 weeks timeline

3. **Read `/IMPLEMENTATION_READINESS_CHECKLIST.md` (2 minutes)**
   - Location: `/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/IMPLEMENTATION_READINESS_CHECKLIST.md`
   - What: Status of all deliverables and what's ready
   - Why: Shows you what's already planned and what you're building toward

### Environment Setup (5 minutes)

```bash
# 1. Verify Python
python --version              # Should be 3.10+

# 2. Navigate to repo
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# 3. Install in development mode
uv pip install -e ".[dev]"

# 4. Verify installation
python -c "import kicad_sch_api; print(kicad_sch_api.__version__)"

# 5. Run quick test to verify everything works
uv run pytest tests/unit/test_components.py -v --tb=short
```

### First Git Commands (5 minutes)

```bash
# 1. Configure git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# 2. Verify you're on main
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git status
git branch

# 3. Pull latest
git pull origin main

# 4. See recent commits
git log --oneline -10

# 5. See your assigned issues
echo "Check GitHub for issues labeled with your track"
```

### First Code to Understand (10 minutes)

**File 1**: `kicad_sch_api/core/types.py`
- Defines data structures (Point, Component, Wire, etc.)
- Understand: What information do we track about components?

**File 2**: `kicad_sch_api/core/pin_utils.py`
- How pin positions are calculated
- Understand: The transformation logic that applies Y-axis inversion

**File 3**: `kicad_sch_api/core/schematic.py`
- Main API entry point
- Understand: How to manipulate a schematic programmatically

---

## Track-Specific Onboarding

Choose your track and complete the 10-minute setup for your track only. You don't need to read the other track setups.

### Track A: Pin Discovery (1 hour total reading)

**Focus**: Enable AI to discover and query component pins
**Issues**: #200, #201, #207
**Directory**: `/kicad-sch-api-track-a` (after setup)

#### Read (30 minutes)

1. **`GITHUB_ISSUES_PIN_CONNECTION.md` - Issues #200, #201, #207**
   - Location: Root directory, search for "Issue #200"
   - What you're building:
     - `get_component_pins()` - List all pins with positions
     - `find_pins_by_name()` - Semantic pin lookup ("VCC", "CLK")
   - Read: Requirements, acceptance criteria, implementation details

2. **`TESTING_AND_LOGGING_GUIDELINES.md` - Sections 1-3**
   - Location: Root directory
   - What: How to write tests and logs for your code
   - Why: You'll be adding lots of DEBUG logging for pin discovery

#### Setup (30 minutes)

```bash
# 1. Create your feature branch (if not already done)
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout -b feature/pin-discovery main
git push origin feature/pin-discovery

# 2. Create worktree for your work
git worktree add ../kicad-sch-api-track-a feature/pin-discovery

# 3. Navigate to your worktree
cd ../kicad-sch-api-track-a

# 4. Install development environment
uv pip install -e ".[dev]"

# 5. Run tests to verify setup
uv run pytest tests/unit/test_components.py -v

# 6. Review files you'll be modifying
# - kicad_sch_api/collections/components.py
# - kicad_sch_api/core/types.py
# - tests/unit/test_get_component_pins.py (you'll create this)
```

#### Your First Task

**Issue #200**: `get_component_pins`
- Add `PinInfo` dataclass to `core/types.py`
- Add `get_pins_info()` method to `ComponentCollection`
- Write unit tests (>10 tests)
- Add comprehensive DEBUG logging

See `GITHUB_ISSUES_PIN_CONNECTION.md` Issue #200 for complete specs.

---

### Track B: Wire Routing (1 hour total reading)

**Focus**: Smart wire routing and automatic junction creation
**Issues**: #202, #203, #204
**Directory**: `/kicad-sch-api-track-b` (after setup)

#### Read (30 minutes)

1. **`GITHUB_ISSUES_PIN_CONNECTION.md` - Issues #202, #203, #204**
   - Location: Root directory, search for "Issue #202"
   - What you're building:
     - Orthogonal routing (L-shaped connections)
     - Automatic junction detection
     - Connectivity validation
   - Read: Requirements, acceptance criteria, implementation details

2. **`MCP_PIN_CONNECTION_STRATEGY.md` - Sections "Problem 2" and "Problem 3"**
   - Location: Root directory
   - What: The gaps you're solving (smart routing, auto-junctions)
   - Why: Understand why these features matter for the MCP server

3. **`TESTING_AND_LOGGING_GUIDELINES.md` - Sections 1-3 and "Wire Creation & Routing"**
   - Location: Root directory
   - What: Logging patterns for wire routing

#### Setup (30 minutes)

```bash
# 1. Create your feature branch (if not already done)
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout -b feature/wire-routing main
git push origin feature/wire-routing

# 2. Create worktree for your work
git worktree add ../kicad-sch-api-track-b feature/wire-routing

# 3. Navigate to your worktree
cd ../kicad-sch-api-track-b

# 4. Install development environment
uv pip install -e ".[dev]"

# 5. Run tests to verify setup
uv run pytest tests/unit/test_wires.py -v

# 6. Review files you'll be modifying
# - kicad_sch_api/core/schematic.py (connect_pins method)
# - kicad_sch_api/core/geometry.py (routing algorithms)
# - kicad_sch_api/core/types.py (ConnectionResult dataclass)
# - kicad_sch_api/managers/wire.py (junction detection)
```

#### Your First Task

**Issue #202**: Orthogonal Routing
- Enhance `connect_pins()` with routing parameter
- Implement L-shaped routing algorithm
- Add comprehensive DEBUG logging
- Write integration tests

See `GITHUB_ISSUES_PIN_CONNECTION.md` Issue #202 for complete specs.

---

### Track C: Testing & Documentation (1 hour total reading)

**Focus**: Test infrastructure and reference circuits
**Issues**: #205, #206, #208
**Directory**: `/kicad-sch-api-track-c` (after setup)

#### Read (30 minutes)

1. **`GITHUB_ISSUES_PIN_CONNECTION.md` - Issues #205, #206, #208**
   - Location: Root directory, search for "Issue #205"
   - What you're building:
     - Test fixtures for other tracks to use
     - 5 reference KiCAD circuits
     - Comprehensive documentation
   - Read: Requirements, acceptance criteria, implementation details

2. **`TESTING_AND_LOGGING_GUIDELINES.md` - Entire document (critical!)**
   - Location: Root directory
   - What: How to structure tests and logging
   - Why: You'll be creating test infrastructure that other tracks depend on

3. **`tests/README.md`**
   - Location: `tests/` directory
   - What: How tests are organized in this project
   - Why: You'll be adding new test files and fixtures

#### Setup (30 minutes)

```bash
# 1. Create your feature branch (if not already done)
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout -b feature/testing-and-docs main
git push origin feature/testing-and-docs

# 2. Create worktree for your work
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs

# 3. Navigate to your worktree
cd ../kicad-sch-api-track-c

# 4. Install development environment
uv pip install -e ".[dev]"

# 5. Run ALL tests to understand test structure
uv run pytest tests/ -v

# 6. Review files you'll be working with
# - tests/conftest.py (fixtures go here)
# - tests/unit/ (unit tests)
# - tests/integration/ (integration tests)
# - tests/reference_tests/ (reference circuit tests)
```

#### Your First Task

**Issue #206**: Reference KiCAD Circuits
- Create 5 reference circuits in KiCAD
- Save them to `tests/reference_kicad_projects/`
- Use "Interactive Reference Testing Strategy" from `CLAUDE.md`
- Coordinate with user for manual circuit creation in KiCAD

See `GITHUB_ISSUES_PIN_CONNECTION.md` Issue #206 for complete specs.

---

## Common Questions & Answers

### "How do I coordinate with other tracks?"

**Strategy**: Minimal dependencies, staged merges

1. **Track A (Pin Discovery)** completes first, merges to main by Day 3
2. **Track B (Wire Routing)** pulls latest main, uses Track A's APIs by Day 4
3. **Track C (Testing & Docs)** runs parallel, integrates at the end

**Daily Sync**: 15-minute standup (see template in `MCP_IMPLEMENTATION_MASTER_PLAN.md`)

**Git Flow**:
```bash
# Each morning (Track B/C only):
git pull origin main        # Get Track A's merged code
git rebase origin main      # Update your branch

# Never push to main directly - create PR instead
git push origin your-branch
# Then: Create PR on GitHub, get review, merge
```

### "What if I break something?"

**No Panic! Here's the recovery process:**

1. **Identify the issue**
   - Run tests: `uv run pytest tests/ -v`
   - Check logs: Look for DEBUG output showing what went wrong

2. **Check git status**
   ```bash
   git status                    # What changed?
   git log --oneline -5          # What was the last commit?
   git diff HEAD~1               # What changed in last commit?
   ```

3. **Revert if necessary**
   ```bash
   # Option 1: Undo last commit (keep changes)
   git reset --soft HEAD~1

   # Option 2: Undo last commit (discard changes)
   git reset --hard HEAD~1

   # Option 3: Revert a specific commit (creates new "undo" commit)
   git revert <commit-hash>
   ```

4. **Ask for help**
   - See "Emergency Contacts" section below
   - Share: Error message, test output, recent commits

### "How do I debug a test failure?"

**Scientific Debugging Process:**

1. **Understand what test expects**
   ```bash
   # Read the test
   less tests/unit/test_your_feature.py

   # Look for: assert statements (expected behavior)
   # Look for: the test name (describes what it's testing)
   ```

2. **Run the specific test with verbose output**
   ```bash
   # Run one test with full output
   uv run pytest tests/unit/test_your_feature.py::test_specific_test -vv

   # Run with print statements shown
   uv run pytest tests/unit/test_your_feature.py::test_specific_test -vv -s
   ```

3. **Add debug logging**
   ```python
   # In your test
   import logging
   logger = logging.getLogger(__name__)

   def test_feature():
       logger.debug("Starting test")
       result = your_function()
       logger.debug(f"Result: {result}")
       assert result == expected
   ```

4. **Enable debug logging output**
   ```bash
   # Set environment variable to see DEBUG logs
   PYTHONPATH=. uv run pytest tests/unit/test_your_feature.py -vv --log-cli-level=DEBUG
   ```

### "What's the KiCAD coordinate system?"

**Read**: `/CLAUDE.md` Section 1 (Critical: KiCAD Coordinate System)

**Quick Summary**:
- Symbol libraries use NORMAL Y-axis (+Y is UP like math)
- Schematics use INVERTED Y-axis (+Y is DOWN like graphics)
- When calculating pin positions, Y must be NEGATED before rotation/mirroring
- **Without this, all pin positions are swapped!**

**Test your understanding**:
```python
# Symbol space (lib): Y positive is UP
Pin1 at (0, 3.81)    # 3.81mm UP

# Schematic space: Y positive is DOWN
# After transformation (Y negation happens):
Pin1 at (100, 96.19)  # Lower Y = visually HIGHER ✓

# If you get:
Pin1 at (100, 103.81)  # Higher Y = visually LOWER ✗ (wrong!)
# Then you forgot to negate Y!
```

### "When should I commit?"

**Commit Strategy**: Small, frequent, logical commits

1. **Good commit size**: ~50-200 lines changed (1-2 features)
2. **Good commit frequency**: At least once per day, ideally every 2-3 hours
3. **Good commit message**:
   ```
   [TRACK][ISSUE] Short description of what changed

   Longer explanation if needed.

   Issue: #200
   ```

**Example commits**:
```bash
# Good
git commit -m "[TRACK-A][#200] Add PinInfo dataclass to types.py"
git commit -m "[TRACK-A][#200] Implement get_pins_info method"
git commit -m "[TRACK-A][#200] Add unit tests for pin discovery"

# Bad (too big)
git commit -m "Finished pin discovery feature"

# Bad (too vague)
git commit -m "Fixed stuff"
```

**When to push**:
- When a test passes (or all your tests pass)
- At end of day (daily push)
- When PR is ready for review

```bash
# Good workflow
git add .
git commit -m "[TRACK][####] Description"
uv run pytest tests/ -v          # Make sure tests still pass
git push origin your-branch
# Create PR on GitHub
```

### "How do I understand the project structure?"

**Quick map of important directories:**

```
/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api/

kicad_sch_api/                    # Main library code
├── core/                         # Core functionality
│   ├── schematic.py             # Main API entry point
│   ├── types.py                 # Data structures
│   ├── pin_utils.py             # Pin position calculations
│   ├── geometry.py              # Geometric algorithms
│   └── parser.py / formatter.py  # KiCAD file reading/writing
├── collections/                 # Enhanced collections
│   └── components.py            # Component management
├── library/                     # Symbol library
│   └── cache.py                 # Symbol caching
└── managers/                    # Operation managers
    └── wire.py                  # Wire operations

tests/                            # Test suite
├── conftest.py                  # Test fixtures (modify for Track C!)
├── unit/                        # Unit tests (add your tests here!)
├── integration/                 # Integration tests
└── reference_tests/             # Reference circuit tests
    └── reference_kicad_projects/ # Actual KiCAD files (Track C creates these!)

docs/                            # Documentation
├── GETTING_STARTED.md           # User guide
├── API_REFERENCE.md             # API docs
└── RECIPES.md                   # Usage examples

Root markdown files:            # Implementation planning docs
├── START_HERE.md                # Read this first
├── CLAUDE.md                    # Critical: coordinate system
├── GITHUB_ISSUES_PIN_CONNECTION.md  # Issue specs
├── MCP_IMPLEMENTATION_MASTER_PLAN.md  # Execution plan
├── GIT_WORKTREE_PARALLEL_DEVELOPMENT.md  # Git workflow
└── TESTING_AND_LOGGING_GUIDELINES.md  # Code standards
```

### "I don't understand what my issue is asking for"

**Resolution process**:

1. **Read the entire issue** in `GITHUB_ISSUES_PIN_CONNECTION.md`
   - User Story (describes why it matters)
   - Acceptance Criteria (how to know it's done)
   - Implementation Details (technical guidance)
   - Testing Requirements (what to test)

2. **Look at similar code**
   - If adding a method, find similar methods in the file
   - If writing tests, find similar tests in the test directory
   - Copy structure, modify details

3. **Ask for clarification**
   - Check "Emergency Contacts" section
   - Create GitHub issue comment with your question
   - Mention the specific acceptance criteria you're unsure about

---

## Development Checklist

### Daily: Start of Day

- [ ] Pull latest from main: `git pull origin main`
- [ ] Update your branch: `git rebase origin main` (if Track B/C)
- [ ] Run all tests: `uv run pytest tests/ -v`
- [ ] Check for DEBUG logging: Review TESTING_AND_LOGGING_GUIDELINES.md
- [ ] Review standup template: See MCP_IMPLEMENTATION_MASTER_PLAN.md

### During Development

- [ ] Write test first (or alongside code)
- [ ] Add DEBUG logging at critical points
- [ ] Run tests frequently: `uv run pytest tests/unit/ -v`
- [ ] Check code formatting: `uv run black kicad_sch_api/` (fixes automatically)
- [ ] Type checking: `uv run mypy kicad_sch_api/` (catches errors)

**Testing Command Pattern**:
```bash
# 1. Run your specific test
uv run pytest tests/unit/test_your_feature.py -v

# 2. Run all unit tests
uv run pytest tests/unit/ -v

# 3. Run everything (before committing)
uv run pytest tests/ -v
```

### During Code Review

- [ ] Read all feedback carefully
- [ ] Ask clarifying questions in review comments
- [ ] Make requested changes
- [ ] Push updated code
- [ ] Wait for approval
- [ ] Merge (don't merge your own code without 2nd opinion)

### End of Day

- [ ] Commit your changes: `git commit -m "[TRACK][####] Description"`
- [ ] Push to your branch: `git push origin your-branch`
- [ ] Run full test suite: `uv run pytest tests/ -v`
- [ ] Update your task status (if using GitHub issues)
- [ ] Document what you'll do tomorrow (in commit message or comment)

### Before Creating PR

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Code formatted: `uv run black kicad_sch_api/ tests/`
- [ ] Type checking passes: `uv run mypy kicad_sch_api/`
- [ ] Linting passes: `uv run flake8 kicad_sch_api/ tests/`
- [ ] No DEBUG logging left in (remove or set to INFO)
- [ ] Docstrings added to all new functions
- [ ] At least 1 unit test per new function

---

## Emergency Troubleshooting

### Test Failures

**Symptom**: `uv run pytest` command shows failures

**Solution**:
1. Run with verbose output: `uv run pytest -vv tests/unit/test_file.py::test_name`
2. Check assertion messages for expected vs actual
3. Add temporary print statements to debug
4. Review TESTING_AND_LOGGING_GUIDELINES.md for logging patterns
5. Contact your track lead if stuck > 30 minutes

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'kicad_sch_api'`

**Solution**:
```bash
# Ensure you're in the right directory
pwd  # Should end with /kicad-sch-api or /kicad-sch-api-track-*

# Reinstall in editable mode
uv pip install -e .

# Verify
python -c "import kicad_sch_api; print('OK')"
```

### Git Conflicts

**Symptom**: `git pull` shows merge conflicts or `CONFLICT` markers

**Solution**:
```bash
# 1. Check status
git status

# 2. If you want to keep your changes:
git checkout --ours <filename>

# 3. If you want to keep their changes:
git checkout --theirs <filename>

# 4. If you want to manually merge:
# Edit the file (remove conflict markers <<<<, ====, >>>>)
# Then:
git add <filename>
git commit -m "Resolve merge conflict"

# 5. If you're totally stuck, ask for help
```

### Coordinate System Confusion

**Symptom**: Pins are calculated at wrong Y positions, or tests expect different values

**Solution**:
1. Read `/CLAUDE.md` Section 1 again (carefully!)
2. Trace through the transformation step-by-step with a simple example
3. Add DEBUG logging: `logger.debug(f"Y-inversion: {y} -> {-y}")`
4. Run test with logging: `uv run pytest -vv --log-cli-level=DEBUG`
5. Contact Track A lead if the calculation is still wrong

**Quick Sanity Check**:
```python
# Component at (100, 100) with pin offset (0, 3.81) in symbol space:

# WRONG (no Y inversion):
pin_y = 100 + 3.81 = 103.81  # Pin at BOTTOM (wrong!)

# RIGHT (Y-inverted):
pin_y = 100 + (-3.81) = 96.19  # Pin at TOP (correct!)
```

### Performance Issues

**Symptom**: Tests take unusually long, or code seems slow

**Solution**:
1. Check symbol library caching: Are you calling cache repeatedly?
2. Check wire calculations: Do you have nested loops over all wires?
3. Use Python profiler: `python -m cProfile -s cumtime your_script.py`
4. Contact performance specialist (if your track has one)

---

## Emergency Contacts

### By Problem Type

| Problem | Contact | Where to Ask |
|---------|---------|--------------|
| Don't understand issue spec | Track Lead | GitHub issue comments |
| Test failure in my code | Track Lead | GitHub issue |
| Git merge conflict | Any Lead | Slack/Discord |
| Coordinate system question | Track A Lead (Pin Discovery) | Slack or GitHub |
| Wire routing question | Track B Lead (Wire Routing) | GitHub issue #202 |
| Test infrastructure question | Track C Lead (Testing) | GitHub issue #205 |
| Someone else's code broken | Whoever broke it first | Direct message |
| Can't push code | DevOps/Git person | Immediate help needed |

### Escalation Path

**If your Track Lead doesn't respond in 30 minutes:**
1. Post in team channel (if using Slack/Discord)
2. Create GitHub issue comment (tag the org)
3. Reach out to project manager
4. Check if there's an on-call person

### Useful Commands When Stuck

```bash
# See your recent commits
git log --oneline -10

# See what you changed
git status
git diff

# See who last touched a file
git log --oneline -n 5 -- path/to/file.py

# Ask for help with full context
git diff > my-changes.patch
# Then share the patch file

# Check if others are having same issue
git log --grep="your search term" --oneline

# Reset to a known good state
git reset --hard origin/main  # WARNING: Loses all local changes!
```

---

## Success Criteria

### By End of Day 1

- [ ] Read all Minimum Required Reading (CLAUDE.md, START_HERE.md)
- [ ] Environment set up and tests passing
- [ ] Know which issue you're working on
- [ ] Have first commit in progress

### By End of Day 3

- [ ] Issue #1 mostly complete (or well started)
- [ ] All tests for Issue #1 written and passing
- [ ] DEBUG logging implemented throughout
- [ ] PR created and reviewed

### By End of Week 1

- [ ] Issue #1 merged to main
- [ ] Issue #2 well underway
- [ ] Coordinated with other tracks
- [ ] No blockers preventing Week 2 progress

---

## Additional Resources

### Core Documentation

- **KiCAD Coordinates**: `/CLAUDE.md` Section 1 (CRITICAL!)
- **Project Architecture**: `/docs/ARCHITECTURE.md`
- **Getting Started Guide**: `/docs/GETTING_STARTED.md`
- **API Reference**: `/docs/API_REFERENCE.md`

### Planning Documents

- **Overall Plan**: `/MCP_IMPLEMENTATION_MASTER_PLAN.md`
- **Issue Specifications**: `/GITHUB_ISSUES_PIN_CONNECTION.md`
- **Git Workflow**: `/GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
- **Testing Standards**: `/TESTING_AND_LOGGING_GUIDELINES.md`

### Code Examples

- **Examples directory**: `/examples/` - Working code examples
- **Test examples**: `/tests/unit/` - Look at existing tests as models
- **Reference circuits**: `/tests/reference_tests/reference_kicad_projects/` - Real KiCAD examples

### Getting Help

1. **Question about code**: Search in `/docs/API_REFERENCE.md`
2. **Question about approach**: Check `/GITHUB_ISSUES_PIN_CONNECTION.md`
3. **Question about testing**: See `/TESTING_AND_LOGGING_GUIDELINES.md`
4. **Question about git**: See `/GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
5. **Still stuck?**: Contact your track lead (see Emergency Contacts)

---

## Quick Reference: Commands You'll Use Daily

```bash
# Work in your worktree
cd ../kicad-sch-api-track-a  # (or track-b or track-c)

# Daily refresh
git pull origin main
git rebase origin main

# Development loop
uv run pytest tests/unit/test_your_feature.py -v
# ... make changes ...
uv run pytest tests/unit/test_your_feature.py -v

# Before committing
uv run black kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
uv run pytest tests/ -v

# When ready
git add .
git commit -m "[TRACK-A][#200] Your description"
git push origin feature/pin-discovery

# Then create PR on GitHub
```

---

## You're Ready!

Everything is set up and documented. You have:

1. **Clear understanding** of what you're building (your issue spec)
2. **Working environment** (uv pip installed, tests passing)
3. **Isolated worktree** (no conflicts with other teams)
4. **Comprehensive logging** (for debugging)
5. **Reference examples** (for how to structure code)

**Next steps:**
1. Read your issue specification completely
2. Write your first test
3. Make your first commit
4. Ask questions if anything is unclear

**Remember**: This is a real, professional codebase with high standards. That's why you have comprehensive guides. If you're ever confused, it means a guide wasn't clear enough - ask for help, and we'll improve it!

---

**Ready to build? Let's go! 🚀**

For status updates or questions, see the issue in GITHUB_ISSUES_PIN_CONNECTION.md and comment there with your progress.
