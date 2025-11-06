# Git Worktree Strategy for Refactoring

**Goal:** Parallel development with safe integration points
**Approach:** Feature branches + worktrees for parallel work
**Benefit:** Work on multiple phases simultaneously, test independently

---

## 🌳 Branching Strategy

```
main (protected)
└── refactor/base (Phase 1 - foundation)
    ├── refactor/collections (Phase 2 - all collections)
    │   ├── refactor/components
    │   ├── refactor/wires
    │   ├── refactor/labels
    │   └── refactor/other-collections
    ├── refactor/schematic (Phase 3 - Schematic integration)
    ├── refactor/tests (Phase 4 - testing)
    └── refactor/docs (Phase 5 - documentation)
```

### Branch Flow

1. **`refactor/base`** - Core infrastructure (BaseCollection, IndexRegistry, PropertyDict)
   - This is the foundation - everything depends on it
   - Merge first

2. **`refactor/collections`** - All collection implementations
   - Depends on: `refactor/base`
   - Can split into sub-branches for parallel work

3. **`refactor/schematic`** - Schematic class updates
   - Depends on: `refactor/collections`

4. **`refactor/tests`** - Comprehensive testing
   - Can work in parallel with collections
   - Depends on: `refactor/base`

5. **`refactor/docs`** - Documentation
   - Can work in parallel
   - Independent of code changes

---

## 📂 Worktree Setup

### Directory Structure

```
circuit_synth_repos/
├── kicad-sch-api/              # Main worktree (main branch)
├── kicad-sch-api-base/         # Worktree for base infrastructure
├── kicad-sch-api-components/   # Worktree for components
├── kicad-sch-api-other/        # Worktree for other collections
├── kicad-sch-api-schematic/    # Worktree for Schematic updates
├── kicad-sch-api-tests/        # Worktree for tests
└── kicad-sch-api-docs/         # Worktree for documentation
```

### Setup Commands

```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api

# Create base branch and worktree (FOUNDATION)
git checkout -b refactor/base
git worktree add ../kicad-sch-api-base refactor/base

# Create collections branch from base
git checkout -b refactor/collections refactor/base
git worktree add ../kicad-sch-api-collections refactor/collections

# Create component-specific branches (PARALLEL WORK)
git checkout -b refactor/components refactor/collections
git worktree add ../kicad-sch-api-components refactor/components

git checkout -b refactor/other-collections refactor/collections
git worktree add ../kicad-sch-api-other refactor/other-collections

# Create Schematic branch from collections
git checkout -b refactor/schematic refactor/collections
git worktree add ../kicad-sch-api-schematic refactor/schematic

# Create test branch from base (PARALLEL WITH COLLECTIONS)
git checkout -b refactor/tests refactor/base
git worktree add ../kicad-sch-api-tests refactor/tests

# Create docs branch from main (COMPLETELY PARALLEL)
git checkout main
git checkout -b refactor/docs
git worktree add ../kicad-sch-api-docs refactor/docs

# Return to main
git checkout main
```

---

## 🔄 Parallel Development Strategy

### Phase 2: Base Infrastructure (Sequential - Foundation)
**Worktree:** `kicad-sch-api-base`
**Branch:** `refactor/base`
**Time:** 4 hours
**Status:** MUST complete first (foundation)

**Work in this worktree:**
```bash
cd ../kicad-sch-api-base

# Implement:
# - kicad_sch_api/collections/base.py
# - IndexSpec, IndexRegistry, PropertyDict
# - BaseCollection
# - ValidationLevel
# - Unit tests

# When complete:
git add .
git commit -m "feat: implement base collection infrastructure

- Add IndexSpec and IndexRegistry for centralized index management
- Add PropertyDict for automatic modification tracking
- Add ValidationLevel enum for configurable validation
- Add BaseCollection abstract base class
- Add comprehensive unit tests (100% coverage)

BREAKING CHANGE: New collection architecture foundation"

git push -u origin refactor/base
```

---

### Phase 3: Collections (PARALLEL - Multiple worktrees!)

Once `refactor/base` is complete, we can work on **3 worktrees simultaneously**:

#### Worktree 1: Components (Most Complex)
**Worktree:** `kicad-sch-api-components`
**Branch:** `refactor/components`
**Time:** 4 hours
**Depends on:** `refactor/base` ✅

```bash
cd ../kicad-sch-api-components

# Merge latest base
git merge refactor/base

# Implement:
# - Component wrapper (all 72 methods)
# - ComponentCollection
# - ICManager integration
# - Spatial queries
# - Comprehensive tests

git add .
git commit -m "feat: implement enhanced Component and ComponentCollection

- Complete Component wrapper with all 72 methods
- ComponentCollection with IndexRegistry
- Multi-unit IC support via ICManager
- Spatial queries (in_area, near_point)
- PropertyDict integration
- 95% test coverage"

git push -u origin refactor/components
```

#### Worktree 2: Wires, Labels, Junctions (Medium Complexity)
**Worktree:** `kicad-sch-api-other`
**Branch:** `refactor/other-collections`
**Time:** 2-3 hours
**Depends on:** `refactor/base` ✅

```bash
cd ../kicad-sch-api-other

# Merge latest base
git merge refactor/base

# Implement:
# - WireCollection
# - LabelCollection
# - JunctionCollection
# - Tests

git add .
git commit -m "feat: implement Wire, Label, Junction collections

- WireCollection with endpoint indexing
- LabelCollection with text/position indexes
- JunctionCollection with position indexing
- Full CRUD operations
- 90% test coverage"

git push -u origin refactor/other-collections
```

#### Worktree 3: Tests (PARALLEL - Can start early!)
**Worktree:** `kicad-sch-api-tests`
**Branch:** `refactor/tests`
**Time:** 4 hours
**Depends on:** `refactor/base` ✅

```bash
cd ../kicad-sch-api-tests

# Merge latest base
git merge refactor/base

# Implement tests AHEAD of implementation:
# - Write test cases based on specs
# - Test BaseCollection thoroughly
# - Performance benchmarks
# - Format preservation tests

# As collections are implemented, merge and run tests:
git merge refactor/components
git merge refactor/other-collections

# Run tests
uv run pytest tests/ -v --cov

git add .
git commit -m "test: comprehensive test suite for refactored collections

- 150+ tests covering all collections
- 90%+ coverage
- Performance benchmarks
- Format preservation validation"

git push -u origin refactor/tests
```

---

### Phase 4: Schematic Integration (After Collections)
**Worktree:** `kicad-sch-api-schematic`
**Branch:** `refactor/schematic`
**Time:** 2 hours
**Depends on:** `refactor/collections` ✅

```bash
cd ../kicad-sch-api-schematic

# Merge all collection branches
git merge refactor/components
git merge refactor/other-collections

# Update Schematic class:
# - Import from new collections
# - Remove redundant methods
# - Update managers

git add .
git commit -m "refactor: update Schematic to use new collections

- Import from kicad_sch_api.collections
- Remove redundant methods (add_wire, add_label, remove_wire)
- Keep advanced operations (add_wire_between_pins, auto_route_pins)
- Update managers for new collection API
- Clean, consistent API

BREAKING CHANGE: Removed redundant Schematic methods"

git push -u origin refactor/schematic
```

---

### Phase 5: Documentation (COMPLETELY PARALLEL!)
**Worktree:** `kicad-sch-api-docs`
**Branch:** `refactor/docs`
**Time:** 4 hours
**Depends on:** Nothing! (can work anytime)

```bash
cd ../kicad-sch-api-docs

# Write documentation:
# - API_REFERENCE_V2.md
# - ARCHITECTURE_V2.md
# - MIGRATION_GUIDE.md
# - EXAMPLES.md
# - Update README.md

git add .
git commit -m "docs: comprehensive documentation overhaul

- Complete API reference with examples
- Architecture guide explaining design
- Migration guide v0.4 -> v0.5
- Real-world usage examples
- Updated README with new patterns"

git push -u origin refactor/docs
```

---

## 🔀 Merge Strategy

### Option A: Sequential Merges (Safest)
```bash
# 1. Merge base first
git checkout main
git merge refactor/base
git push

# 2. Merge collections
git merge refactor/components
git merge refactor/other-collections
git push

# 3. Merge Schematic
git merge refactor/schematic
git push

# 4. Merge tests
git merge refactor/tests
git push

# 5. Merge docs
git merge refactor/docs
git push
```

### Option B: Feature Integration Branch (Recommended)
```bash
# Create integration branch
git checkout -b refactor/integration main

# Merge everything into integration for testing
git merge refactor/base
git merge refactor/components
git merge refactor/other-collections
git merge refactor/schematic
git merge refactor/tests
git merge refactor/docs

# Run ALL tests
uv run pytest tests/ -v

# Test against circuit-synth
cd ../circuit-synth
pytest tests/ -v

# If all pass:
git checkout main
git merge refactor/integration --no-ff
git tag v0.5.0
git push --tags
```

### Option C: Pull Requests (Most Professional)
```bash
# Create PRs for review:
# 1. PR: refactor/base -> main
# 2. PR: refactor/components -> main (after base merged)
# 3. PR: refactor/other-collections -> main (after base merged)
# 4. PR: refactor/schematic -> main (after collections merged)
# 5. PR: refactor/tests -> main
# 6. PR: refactor/docs -> main
```

---

## 🚀 Optimal Workflow

### Day 1 Morning (4 hours): Foundation
```bash
# Work in base worktree
cd ../kicad-sch-api-base

# Implement base infrastructure
# Test thoroughly
# Commit and push
```

### Day 1 Afternoon (4 hours): Parallel Development Starts!
```bash
# Terminal 1: Components (you or Claude instance 1)
cd ../kicad-sch-api-components
git merge refactor/base
# Implement ComponentCollection

# Terminal 2: Other collections (you or Claude instance 2)
cd ../kicad-sch-api-other
git merge refactor/base
# Implement Wire, Label, Junction collections

# Terminal 3: Tests (you or Claude instance 3)
cd ../kicad-sch-api-tests
git merge refactor/base
# Write comprehensive tests
```

### Day 2 Morning (2 hours): Integration
```bash
# Merge collections into schematic branch
cd ../kicad-sch-api-schematic
git merge refactor/components
git merge refactor/other-collections

# Update Schematic class
```

### Day 2 Afternoon (4 hours): Testing & Validation
```bash
# Run all tests
cd ../kicad-sch-api-tests
git merge refactor/components
git merge refactor/other-collections
git merge refactor/schematic

uv run pytest tests/ -v --cov

# Test against circuit-synth
cd ../circuit-synth
pytest tests/ -v
```

### Day 3 (4 hours): Documentation & Cleanup
```bash
# Finalize documentation
cd ../kicad-sch-api-docs
# Complete all docs

# Create integration branch and test
cd ../kicad-sch-api
git checkout -b refactor/integration
git merge refactor/base
git merge refactor/components
git merge refactor/other-collections
git merge refactor/schematic
git merge refactor/tests
git merge refactor/docs

# Final validation
uv run pytest tests/ -v

# If all good:
git checkout main
git merge refactor/integration
git tag v0.5.0
git push --tags
```

---

## 🧹 Cleanup After Merge

```bash
# Remove worktrees
git worktree remove ../kicad-sch-api-base
git worktree remove ../kicad-sch-api-components
git worktree remove ../kicad-sch-api-other
git worktree remove ../kicad-sch-api-schematic
git worktree remove ../kicad-sch-api-tests
git worktree remove ../kicad-sch-api-docs

# Delete branches (optional, can keep for history)
git branch -d refactor/base
git branch -d refactor/components
git branch -d refactor/other-collections
git branch -d refactor/schematic
git branch -d refactor/tests
git branch -d refactor/docs
git branch -d refactor/collections
git branch -d refactor/integration
```

---

## 🎯 Benefits of This Approach

1. **Parallel Development**
   - Work on 3 things simultaneously
   - Don't wait for sequential completion
   - Faster overall timeline

2. **Safe Integration**
   - Each branch is testable independently
   - Easy to rollback specific changes
   - Integration branch for final validation

3. **Clear Commits**
   - Each branch has focused commits
   - Easy to review
   - Clear history

4. **Flexible**
   - Can merge in different orders if needed
   - Can abandon branches without affecting others
   - Can work offline

5. **Professional**
   - Industry-standard approach
   - Easy for others to contribute
   - Clean git history

---

## 🚀 Ready to Start?

**Shall I:**
1. **Set up the worktrees** (run the commands)?
2. **Start with base implementation** in the base worktree?
3. **Both** - set up AND start implementing?

**Command to run:**
```bash
# I can execute this entire setup
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api
git checkout -b refactor/base
git worktree add ../kicad-sch-api-base refactor/base
cd ../kicad-sch-api-base
# Start implementing...
```

**Just say "SET UP WORKTREES" and I'll create the entire structure!**
