# Quick Reference Card: MCP Pin Connection Developer Onboarding

**Print this out or bookmark it. You'll reference it constantly.**

---

## Day 1: The First Hour

```
Step 1: Read (15 min)
  → CLAUDE.md (Sections 1-3) - THE CRITICAL THING
  → START_HERE.md (overview)

Step 2: Install (5 min)
  cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
  uv pip install -e ".[dev]"

Step 3: Verify (5 min)
  uv run pytest tests/unit/test_components.py -v

Step 4: Know Your Role
  Track A? Read GITHUB_ISSUES_PIN_CONNECTION.md Issue #200
  Track B? Read GITHUB_ISSUES_PIN_CONNECTION.md Issue #202
  Track C? Read GITHUB_ISSUES_PIN_CONNECTION.md Issue #205

TOTAL TIME: ~45 minutes
```

---

## The Critical Thing (Memorize This)

```python
# ❌ WRONG (common mistake):
Y_absolute = component_y + pin_offset_y
# Pin 1 at offset (0, 3.81) -> (100, 103.81) = VISUALLY AT BOTTOM

# ✅ RIGHT (what KiCAD does):
Y_absolute = component_y + (-pin_offset_y)
# Pin 1 at offset (0, 3.81) -> (100, 96.19) = VISUALLY AT TOP

# WHY: Symbol space uses normal Y (up=positive)
#      Schematic space uses inverted Y (down=positive)
#      So Y must be NEGATED during transformation
```

**File**: `/CLAUDE.md` Section 1
**Test understanding**: If pins are backwards, you forgot the negation

---

## Your Worktree Setup

```bash
# From main directory:
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# Create your feature branch (pick one):
git checkout -b feature/pin-discovery main        # Track A
git checkout -b feature/wire-routing main         # Track B
git checkout -b feature/testing-and-docs main     # Track C

# Create worktree:
git worktree add ../kicad-sch-api-track-a feature/pin-discovery     # Track A
git worktree add ../kicad-sch-api-track-b feature/wire-routing      # Track B
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs  # Track C

# Work from your worktree:
cd ../kicad-sch-api-track-a  # (or track-b or track-c)

# Install:
uv pip install -e ".[dev]"

# Verify:
uv run pytest tests/ -v
```

---

## Daily Workflow

```bash
# Morning
cd ../kicad-sch-api-track-a  # Your worktree
git pull origin main
git rebase origin main

# Development (repeat this cycle)
# 1. Write test
# 2. Run test (watch it fail)
# 3. Write code
# 4. Run test (watch it pass)
# 5. Add DEBUG logging
uv run pytest tests/unit/test_your_feature.py -v

# When test passes
git add .
git commit -m "[TRACK-A][#200] Your description here"

# Evening
uv run pytest tests/ -v              # All tests
uv run black kicad_sch_api/          # Format code
git push origin feature/pin-discovery
```

---

## Quick Debug Commands

```bash
# Run one test with full output
uv run pytest tests/unit/test_file.py::test_name -vv -s

# Run with debug logging
PYTHONPATH=. uv run pytest tests/unit/test_file.py -vv --log-cli-level=DEBUG

# See what you changed
git diff

# See your last commit
git log -1 --name-status

# See this branch vs main
git diff main...HEAD

# Go back to last good state
git reset --hard HEAD~1  # WARNING: Loses all changes!

# Check your git tree
git log --oneline -10
```

---

## Code Quality Checklist

Before committing, run:

```bash
# 1. Tests (must pass)
uv run pytest tests/ -v

# 2. Format code (auto-fixes)
uv run black kicad_sch_api/ tests/

# 3. Type checking
uv run mypy kicad_sch_api/

# 4. Linting
uv run flake8 kicad_sch_api/

# All at once:
uv run black kicad_sch_api/ tests/ && \
uv run isort kicad_sch_api/ tests/ && \
uv run mypy kicad_sch_api/ && \
uv run flake8 kicad_sch_api/ tests/ && \
uv run pytest tests/ -v
```

---

## Logging Template (Copy-Paste This)

```python
import logging

logger = logging.getLogger(__name__)

def your_function(param1, param2):
    """What this function does."""

    # ENTRY POINT
    logger.debug(f"your_function: param1={param1}, param2={param2}")

    # DO STUFF
    result = do_something(param1)
    logger.debug(f"  After do_something: {result}")

    # TRANSFORM
    final = transform(result, param2)
    logger.debug(f"  After transform: {final}")

    # RETURN
    logger.debug(f"  RESULT: {final}")
    return final
```

---

## Testing Template (Copy-Paste This)

```python
import pytest
from kicad_sch_api import Schematic

class TestYourFeature:
    """Test suite for your feature."""

    def test_basic_functionality(self):
        """Test that basic functionality works."""
        # Arrange
        sch = Schematic.create_blank()

        # Act
        result = your_function(sch)

        # Assert
        assert result is not None
        assert result.something == expected

    def test_with_logging(self, caplog):
        """Test that appropriate logging occurs."""
        import logging
        caplog.set_level(logging.DEBUG)

        result = your_function(sch)

        assert "Expected log message" in caplog.text
```

---

## File Modification Map

### Track A: Pin Discovery
```
Modify:
  kicad_sch_api/core/types.py          ← Add PinInfo dataclass
  kicad_sch_api/collections/components.py  ← Add get_pins_info(), find_pins_by_name()
  kicad_sch_api/__init__.py            ← Export new classes/functions

Create:
  tests/unit/test_get_component_pins.py    ← New test file
  tests/unit/test_find_pins_by_name.py     ← New test file
  tests/integration/test_pin_discovery_workflow.py
```

### Track B: Wire Routing
```
Modify:
  kicad_sch_api/core/schematic.py      ← Enhance connect_pins()
  kicad_sch_api/core/geometry.py       ← Add routing algorithms
  kicad_sch_api/core/types.py          ← Add ConnectionResult dataclass
  kicad_sch_api/managers/wire.py       ← Add junction detection

Create:
  tests/unit/test_orthogonal_routing.py
  tests/unit/test_junction_detection.py
  tests/unit/test_connectivity_validation.py
  tests/integration/test_routing_workflows.py
```

### Track C: Testing & Documentation
```
Create:
  tests/conftest.py (new fixtures!)
  tests/reference_kicad_projects/voltage_divider/
  tests/reference_kicad_projects/led_circuit/
  tests/reference_kicad_projects/parallel_resistors/
  tests/reference_kicad_projects/complex_circuit/
  tests/reference_kicad_projects/ic_connections/
  docs/PIN_CONNECTION_USER_GUIDE.md
  docs/TROUBLESHOOTING_PIN_CONNECTIONS.md
```

---

## Issue Specs (Bookmark These!)

| Track | Issue | What | Time |
|-------|-------|------|------|
| A | #200 | `get_component_pins()` | 1 day |
| A | #201 | `find_pins_by_name()` | 1 day |
| A | #207 | DEBUG logging everywhere | 1 day |
| B | #202 | Orthogonal routing | 1.5 days |
| B | #203 | Auto-junction detection | 1.5 days |
| B | #204 | Connectivity validation | 1 day |
| C | #205 | Test infrastructure | 1 day |
| C | #206 | Reference circuits | 1 day |
| C | #208 | Documentation | 1 day |

**All specs in**: `/GITHUB_ISSUES_PIN_CONNECTION.md`

---

## Help Resources (Order of Priority)

```
1. Your issue spec (GITHUB_ISSUES_PIN_CONNECTION.md)
   → Most detailed guidance

2. Similar code in the repo
   → Copy structure, modify details

3. TESTING_AND_LOGGING_GUIDELINES.md
   → How to test and log your code

4. Your track lead
   → Ask within 30 min if stuck

5. CLAUDE.md
   → For coordinate system questions

6. docs/API_REFERENCE.md
   → For API details
```

---

## Common Error Solutions

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: kicad_sch_api` | `uv pip install -e .` (in right directory!) |
| Tests fail with import errors | Ensure you're in worktree (`cd ../kicad-sch-api-track-*`) |
| Git says "conflict" | Run `git status`, edit files, `git add`, `git commit` |
| Code formatting issues | `uv run black kicad_sch_api/` |
| Pins at wrong Y position | Read CLAUDE.md Section 1 - you forgot Y negation |
| Tests take forever | Check for nested loops or repeated cache lookups |
| "Permission denied" on git push | Check you have write access to repo |

---

## Success Checklist

### Each Day
- [ ] Tests passing
- [ ] At least one commit
- [ ] DEBUG logging added where needed
- [ ] No code formatting issues

### Each Issue (When Done)
- [ ] All acceptance criteria met
- [ ] >95% test coverage
- [ ] All tests passing
- [ ] DEBUG logging throughout
- [ ] Code formatted and type-checked
- [ ] PR created and reviewed
- [ ] Merged to main

### Each Week
- [ ] Day 1: Issue #1 or #2 started and understood
- [ ] Day 3: Issue #1 complete and merged
- [ ] Day 5: Issue #2 complete and merged
- [ ] End: All assigned issues merged, ready for next phase

---

## Absolute Minimum (If You Remember Nothing Else)

```
1. Read CLAUDE.md Section 1 (Y-axis inversion)
2. Read your issue in GITHUB_ISSUES_PIN_CONNECTION.md
3. Write test first, then code
4. Add DEBUG logging everywhere
5. Run: uv run pytest tests/ -v (before each commit)
6. Commit frequently with clear messages
7. Ask for help if stuck > 30 min
8. Never push directly to main
```

---

## Questions?

### Quick Answers
- **"How do I...?"** → See Daily Workflow section
- **"What should I code?"** → See your issue in GITHUB_ISSUES_PIN_CONNECTION.md
- **"How do I test?"** → See Testing Template
- **"How do I log?"** → See Logging Template
- **"Pins are backwards?"** → See The Critical Thing section

### Stuck?
1. Check this card first (3 min)
2. Search DEVELOPER_ONBOARDING.md (5 min)
3. Search your issue spec (5 min)
4. Ask your track lead (on Slack/GitHub)

---

**Print this. Keep it visible. You've got this! 🚀**
