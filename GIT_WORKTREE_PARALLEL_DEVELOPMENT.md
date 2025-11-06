# Git Worktree Strategy: Parallel Development Plan

**Purpose**: Enable 3 teams to work on 3 separate tracks simultaneously without blocking each other
**Status**: Ready for Implementation
**Git**: Main branch is `main` (always deployable)

---

## Overview

We'll use **git worktrees** to create isolated working directories for 3 parallel tracks:

- **Track A (Pin Discovery)**: Issues #200, #201, #207 (2 developers)
- **Track B (Wire Routing)**: Issues #202, #203, #204 (2 developers)
- **Track C (Testing & Docs)**: Issues #205, #206, #208 (1-2 developers)

Each track gets its own worktree, allowing independent branches and testing.

---

## Initial Setup (Day 0)

### 1. Create Primary Repository Worktree

```bash
# Navigate to main repo
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# Verify we're on main and up-to-date
git branch -vv
git pull origin main

# List existing worktrees (should only show primary)
git worktree list
```

### 2. Create Feature Branches

```bash
# Create base branches for each track
git checkout main
git pull origin main

# Track A: Pin Discovery
git checkout -b feature/pin-discovery main

# Track B: Wire Routing
git checkout main
git checkout -b feature/wire-routing main

# Track C: Testing & Docs
git checkout main
git checkout -b feature/testing-and-docs main

# Verify branches
git branch -a
```

### 3. Create Worktrees

```bash
# From main repo directory (/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api)

# Create Track A worktree
git worktree add ../kicad-sch-api-track-a feature/pin-discovery

# Create Track B worktree
git worktree add ../kicad-sch-api-track-b feature/wire-routing

# Create Track C worktree
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs

# Verify worktrees created
git worktree list

# Output should show:
# /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api       (bare)
# /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-a feature/pin-discovery
# /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-b feature/wire-routing
# /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-c feature/testing-and-docs
```

---

## Track Structure

### Track A: Pin Discovery (3 days)

**Directory**: `/kicad-sch-api-track-a`
**Branch**: `feature/pin-discovery`
**Issues**: #200, #201, #207

**Files to Modify**:
```
kicad_sch_api/
├── collections/
│   └── components.py          (add get_pins_info, find_pins_by_name)
├── core/
│   └── types.py               (add PinInfo dataclass)
└── __init__.py                (export new functions)

mcp_server/
├── models.py                  (add PinInfoOutput pydantic model)
└── tools/
    └── component_tools.py     (add get_component_pins MCP tool)

tests/
├── unit/
│   ├── test_get_component_pins.py         (NEW)
│   └── test_find_pins_by_name.py          (NEW)
└── integration/
    └── test_pin_discovery_workflow.py     (NEW)
```

**Developers**: [Developer A, Developer B]

### Track B: Wire Routing (4 days)

**Directory**: `/kicad-sch-api-track-b`
**Branch**: `feature/wire-routing`
**Issues**: #202, #203, #204

**Files to Modify**:
```
kicad_sch_api/
├── core/
│   ├── schematic.py           (enhance connect_pins, add routing logic)
│   ├── geometry.py            (add routing algorithms)
│   └── types.py               (add ConnectionResult dataclass)
└── managers/
    └── wire.py                (add junction detection)

tests/
├── unit/
│   ├── test_orthogonal_routing.py         (NEW)
│   ├── test_junction_detection.py         (NEW)
│   └── test_connectivity_validation.py    (NEW)
└── integration/
    └── test_routing_workflows.py          (NEW)
```

**Developers**: [Developer B, Developer C]

### Track C: Testing & Docs (2-3 days)

**Directory**: `/kicad-sch-api-track-c`
**Branch**: `feature/testing-and-docs`
**Issues**: #205, #206, #208

**Files to Create/Modify**:
```
tests/
├── mcp_server/
│   ├── conftest.py                        (NEW fixtures)
│   └── helpers/
│       └── pin_helpers.py                 (NEW helpers)
├── reference_kicad_projects/
│   ├── voltage_divider/                   (NEW reference)
│   ├── led_circuit/                       (NEW reference)
│   ├── parallel_resistors/                (NEW reference)
│   ├── complex_circuit/                   (NEW reference)
│   └── ic_connections/                    (NEW reference)
└── reference_tests/
    └── test_pin_connections_reference.py  (NEW)

docs/
├── MCP_PIN_CONNECTION_USER_GUIDE.md       (NEW)
├── API_REFERENCE_PIN_TOOLS.md             (NEW)
├── PIN_CONNECTION_ARCHITECTURE.md         (NEW)
└── TROUBLESHOOTING_PIN_ISSUES.md          (NEW)
```

**Developers**: [QA/Documentation, optionally a developer]

---

## Daily Workflow

### For Each Track

**Start of day**:
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-X

# Check status
git status
git log --oneline -5

# See what changed in other tracks (informational)
git fetch origin
```

**During development**:
```bash
# Make changes
vim kicad_sch_api/...

# Test frequently
uv run pytest tests/... -v

# Add debug logging (see TESTING_GUIDELINES.md)

# Commit small changes
git add specific_files.py
git commit -m "feat: specific change"

# Push for backup
git push origin feature/[name]
```

**End of day**:
```bash
# Ensure everything is committed
git status

# Create summary for standup
git log --oneline HEAD~5..HEAD
```

---

## Handling Dependencies

### When Track A Completes (#200)

1. **In main repo**:
   ```bash
   cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

   # Create PR for feature/pin-discovery
   gh pr create --base main --head feature/pin-discovery

   # After review and merge
   git checkout main
   git pull origin main
   ```

2. **In Track B and Track C**:
   ```bash
   cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-b

   # Pull in the merged changes
   git fetch origin main
   git merge origin/main
   # Resolve any conflicts if they exist

   # Now can use get_component_pins in code
   ```

### Conflict Prevention Strategy

**Golden Rule**: Each track modifies **different files**

| Track A | Track B | Track C |
|---------|---------|---------|
| `collections/components.py` | `core/schematic.py` | `tests/` |
| `core/types.py` (PinInfo) | `core/geometry.py` | `docs/` |
| `mcp_server/tools/component_tools.py` | `managers/wire.py` | (no lib code) |

---

## Testing During Parallel Development

### Track A Tests
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-a

# Run Track A tests
uv run pytest tests/unit/test_get_component_pins.py -v
uv run pytest tests/unit/test_find_pins_by_name.py -v

# Full test suite (should not break existing)
uv run pytest tests/ -v -m "not slow"

# Check coverage
uv run pytest tests/unit/test_get_component_pins.py --cov=kicad_sch_api.collections
```

### Track B Tests
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-b

# Must pull Track A first
git fetch origin main && git merge origin/main

# Run Track B tests
uv run pytest tests/unit/test_orthogonal_routing.py -v

# Run all tests
uv run pytest tests/ -v
```

### Track C Tests
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-c

# Reference tests
uv run pytest tests/reference_tests/ -v

# Validate reference circuits manually
```

---

## Merge to Main

### Pre-Merge Checklist

**All tracks must**:
1. ✅ Pass full test suite: `uv run pytest tests/ -v`
2. ✅ Have >95% coverage on new code
3. ✅ Have DEBUG logging at all critical points
4. ✅ Have comprehensive docstrings
5. ✅ Pass code quality:
   ```bash
   uv run black kicad_sch_api/ tests/
   uv run isort kicad_sch_api/ tests/
   uv run mypy kicad_sch_api/ --strict
   uv run flake8 kicad_sch_api/ tests/
   ```

### Merge Order

1. **Track A** → `main` (no dependencies)
2. **Track B** → `main` (after A merged, pulls main changes)
3. **Track C** → `main` (after A & B merged, pulls main changes)

```bash
# Merge from Track A
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout main
git pull origin main
git merge --no-ff feature/pin-discovery
git push origin main
```

### Create Pull Requests

```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-a
gh pr create \
  --title "feat: Pin discovery tools (get_component_pins, find_pins_by_name)" \
  --body "Implements issues #200 and #201.

  - Add get_pins_info to ComponentCollection
  - Semantic pin name lookup
  - >95% test coverage
  " \
  --label "feature,pin-discovery,phase-1"
```

---

## Cleanup

### After All Tracks Merged

```bash
# Delete worktrees
git worktree remove ../kicad-sch-api-track-a
git worktree remove ../kicad-sch-api-track-b
git worktree remove ../kicad-sch-api-track-c

# Delete branches
git branch -d feature/pin-discovery
git branch -d feature/wire-routing
git branch -d feature/testing-and-docs

# Delete remote branches
git push origin --delete feature/pin-discovery
git push origin --delete feature/wire-routing
git push origin --delete feature/testing-and-docs
```

---

## Quick Reference

### Setup
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# Create branches
git checkout -b feature/pin-discovery main
git checkout -b feature/wire-routing main
git checkout -b feature/testing-and-docs main

# Create worktrees
git worktree add ../kicad-sch-api-track-a feature/pin-discovery
git worktree add ../kicad-sch-api-track-b feature/wire-routing
git worktree add ../kicad-sch-api-track-c feature/testing-and-docs
```

### Daily Work
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-X
git status
vim [files]
uv run pytest tests/ -v
git commit -m "feat: description"
git push origin feature/[name]
```

### Merge
```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout main && git pull origin main
git merge --no-ff feature/[name]
git push origin main

# In other tracks
git fetch origin main && git merge origin/main
```

---

## Success Indicators

✅ Three independent worktrees created and working
✅ Developers can work without blocking each other
✅ Merges happen with minimal conflicts
✅ All tests pass after each merge
✅ Documentation stays in sync with code
✅ Final main branch has all features integrated

**Next**: See TESTING_AND_LOGGING_GUIDELINES.md for development standards
