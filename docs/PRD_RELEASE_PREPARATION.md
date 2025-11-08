# PRD: Repository Release Preparation & Security Hardening

**Status:** In Progress
**Priority:** P0 (Critical - Blocks Public Release)
**Owner:** Circuit-Synth Team
**Target Version:** 0.5.1
**Target Date:** ASAP (Pre-release blocker)

---

## 1. Executive Summary

### Problem Statement

The kicad-sch-api repository has several critical issues that block public release:

1. **Security Risk:** Potential for credential leaks (`.pypirc` exists locally, no secret detection)
2. **Documentation Drift:** References to non-existent files (`stm32g431_simple.py`)
3. **Packaging Issues:** Python version classifiers mismatch
4. **Root Directory Pollution:** Generated test files cluttering repository
5. **No Release Process:** No automated checks or release guidelines

### Impact

- **Security:** Risk of accidentally leaking PyPI tokens → package compromise
- **User Experience:** Broken documentation links → user confusion, poor first impression
- **PyPI Metadata:** Incorrect Python versions → installation failures
- **Contributor Experience:** Messy repository → difficult to navigate and contribute
- **Release Quality:** No validation → risk of broken releases

### Proposed Solution

Implement comprehensive release preparation with:
1. **Security hardening** - Pre-commit hooks for secret detection
2. **Documentation fixes** - Remove broken references, validate links
3. **Packaging corrections** - Fix Python version metadata
4. **Cleanup automation** - Scripts to maintain clean repository
5. **Release process** - Automated pre-release validation

### Success Metrics

- ✅ Zero secrets in git history
- ✅ Zero broken documentation links
- ✅ 100% metadata accuracy (PyPI classifiers)
- ✅ Clean root directory (no generated files)
- ✅ Automated release validation (8+ checks)

---

## 2. Background & Context

### Current State

**Repository Status:**
- 94 Python files in package
- 29 comprehensive tests
- All examples execute successfully
- Well-structured codebase (core, collections, managers)

**Issues Discovered:**
- `.pypirc` file exists locally (not committed, but risky)
- Documentation references `examples/stm32g431_simple.py` (doesn't exist)
- Python 3.8/3.9 in classifiers, but requires >=3.10
- Generated `.kicad_sch` files and test scripts in root
- Version mismatch between `pyproject.toml` and `__init__.py`
- No automated release validation

### Why Now?

- Preparing for public release to PyPI
- Cannot fix PyPI releases after publishing (versions are immutable)
- Security best practices require secret detection before public repo
- Professional appearance critical for adoption

### Previous Attempts

- `.gitignore` patterns exist but incomplete
- Some pre-commit hooks configured but missing security checks
- No release process documentation

---

## 3. Goals & Non-Goals

### Goals

#### Primary (P0 - Must Have)

1. **Prevent credential leaks** - No PyPI tokens or secrets can be committed
2. **Fix documentation accuracy** - Remove all references to missing files
3. **Correct packaging metadata** - Python versions match requirements
4. **Version consistency** - `pyproject.toml` ↔ `__init__.py` synchronized
5. **Automated validation** - Pre-release checks catch common issues

#### Secondary (P1 - Should Have)

6. **Clean repository** - No generated files in root directory
7. **Release documentation** - Clear checklist and process guide
8. **Cleanup automation** - Scripts for common maintenance tasks
9. **Pre-commit enforcement** - Hooks prevent common mistakes

#### Tertiary (P2 - Nice to Have)

10. **Comprehensive documentation** - Release process, prevention mechanisms
11. **Developer guidance** - Templates and examples for credentials

### Non-Goals

- ❌ Refactoring existing code architecture
- ❌ Adding new features to the library
- ❌ Changing API surface
- ❌ Performance optimizations
- ❌ Test coverage improvements (already at 70%+)
- ❌ Removing existing TODO comments (document as known limitations)

---

## 4. Requirements

### 4.1 Security Requirements (P0)

**REQ-SEC-001: Secret Detection**
- **What:** Pre-commit hook must scan for secrets before every commit
- **Why:** Prevent accidental credential leaks to git history
- **How:** Gitleaks integration with custom PyPI token detection
- **Acceptance:**
  - Gitleaks hook configured in `.pre-commit-config.yaml`
  - `.gitleaks.toml` config catches PyPI tokens
  - Test: Try committing `.pypirc` with token → should block

**REQ-SEC-002: Credential Template**
- **What:** Safe `.pypirc.example` template for users
- **Why:** Guide users on proper credential management
- **How:** Example file with placeholder tokens
- **Acceptance:**
  - `.pypirc.example` exists with `YOUR_TOKEN_HERE` placeholders
  - Documented in README/CONTRIBUTING
  - Whitelisted in gitleaks config

**REQ-SEC-003: Pre-Commit Private Key Detection**
- **What:** Detect API tokens, SSH keys, private keys
- **Why:** Comprehensive secret protection
- **How:** Enable `detect-private-key` hook
- **Acceptance:**
  - Hook configured in `.pre-commit-config.yaml`
  - Test: Try committing SSH key → should block

### 4.2 Documentation Requirements (P0)

**REQ-DOC-001: Remove Missing File References**
- **What:** Remove all references to `stm32g431_simple.py`
- **Why:** Broken links confuse users and damage credibility
- **Where:** `README.md`, `CLAUDE.md`, `docs/HIERARCHY_FEATURES.md`, `examples/README.md`
- **Acceptance:**
  - `grep -r "stm32g431" *.md docs/ examples/` returns no results
  - All documentation links valid

**REQ-DOC-002: Fix Directory Structure References**
- **What:** Correct `examples/README.md` directory structure
- **Why:** Reflects actual layout (flat, not `KEEP/` subdirectory)
- **Acceptance:**
  - README shows correct structure
  - Example paths work: `python examples/voltage_divider.py`

**REQ-DOC-003: Automated Link Validation**
- **What:** Pre-release check validates documentation links
- **Why:** Catch broken references before release
- **Acceptance:**
  - Script checks for missing files
  - Pre-release fails if broken links detected

### 4.3 Packaging Requirements (P0)

**REQ-PKG-001: Python Version Classifiers**
- **What:** Remove Python 3.8/3.9 from `pyproject.toml` classifiers
- **Why:** Package requires >=3.10, classifiers must match
- **Acceptance:**
  - Only py310, py311, py312 in classifiers
  - `requires-python = ">=3.10"` unchanged
  - Black target-version matches

**REQ-PKG-002: Version Consistency**
- **What:** Synchronize version across `pyproject.toml` and `__init__.py`
- **Why:** Inconsistent versions confuse package managers
- **Acceptance:**
  - Both files show same version (0.5.1)
  - Pre-release check validates consistency
  - `import kicad_sch_api; print(__version__)` matches pyproject

### 4.4 Repository Cleanliness Requirements (P1)

**REQ-CLEAN-001: Root Directory Protection**
- **What:** Prevent committing generated files to root
- **Why:** Professional appearance, easier navigation
- **Acceptance:**
  - `.gitignore` blocks `/*.kicad_sch` (except examples/, tests/)
  - Pre-commit hook blocks root `.kicad_sch` commits
  - Pre-commit hook warns about `test_circuit_*.py` in root

**REQ-CLEAN-002: Cleanup Script**
- **What:** Script to remove generated files from root
- **Why:** Easy maintenance for developers
- **Acceptance:**
  - `scripts/clean_root.sh` exists and is executable
  - Removes `*.kicad_sch`, `test_circuit_*.py`, `demo_*.py` from root
  - Safe (doesn't touch examples/ or tests/)

### 4.5 Release Process Requirements (P1)

**REQ-REL-001: Pre-Release Validation Script**
- **What:** Automated script checking 8+ release criteria
- **Why:** Catch issues before publishing to PyPI
- **Checks:**
  1. No secrets in code
  2. No `.pypirc` in git
  3. Root directory clean
  4. Version consistency
  5. Python classifiers correct
  6. No broken doc links
  7. Examples execute successfully
  8. CHANGELOG updated
- **Acceptance:**
  - `scripts/pre_release_check.sh` exists and is executable
  - All checks run and report pass/fail
  - Script exits 0 if all pass, 1 if any fail

**REQ-REL-002: Release Checklist Documentation**
- **What:** Comprehensive `RELEASE_CHECKLIST.md`
- **Why:** Guide maintainers through release process
- **Acceptance:**
  - Documents all pre-release steps
  - Includes build, test, publish commands
  - Covers security best practices
  - Includes rollback procedures

---

## 5. Technical Design

### 5.1 Architecture

**Component Diagram:**

```
kicad-sch-api/
├── .pre-commit-config.yaml       [MODIFIED] Add gitleaks + detection hooks
├── .gitleaks.toml                [NEW] Secret detection rules
├── .pypirc.example               [NEW] Safe credential template
├── .gitignore                    [MODIFIED] Root-level patterns
├── pyproject.toml                [MODIFIED] Fix classifiers
├── kicad_sch_api/__init__.py     [MODIFIED] Fix version
├── README.md                     [MODIFIED] Remove broken links
├── CLAUDE.md                     [MODIFIED] Remove broken links
├── docs/HIERARCHY_FEATURES.md    [MODIFIED] Remove broken links
├── examples/README.md            [MODIFIED] Fix structure
├── scripts/
│   ├── clean_root.sh             [NEW] Cleanup automation
│   └── pre_release_check.sh      [NEW] Release validation
├── RELEASE_CHECKLIST.md          [NEW] Process guide
└── FIXES_APPLIED.md              [NEW] Documentation
```

### 5.2 Implementation Details

#### 5.2.1 Secret Detection (.pre-commit-config.yaml)

```yaml
# Add to repos section
- repo: https://github.com/pre-commit/pre-commit-hooks
  hooks:
    - id: detect-private-key
      name: Detect Private Keys (API tokens, SSH keys)

- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.2
  hooks:
    - id: gitleaks
```

#### 5.2.2 Gitleaks Configuration (.gitleaks.toml)

```toml
# Custom rules for PyPI tokens
[[rules]]
id = "pypi-token"
description = "PyPI API Token"
regex = '''pypi-[A-Za-z0-9-_]{70,}'''
tags = ["key", "pypi"]

# Allowlist for examples
[allowlist]
paths = [
    '''.pypirc.example''',
    '''.*\.md$''',
]
regexes = [
    '''pypi-YOUR_TOKEN_HERE''',
]
```

#### 5.2.3 Pre-Release Check Script (scripts/pre_release_check.sh)

```bash
#!/bin/bash
# Checks:
# 1. No secrets in code (grep for pypi-Ag tokens)
# 2. Root directory clean (no *.kicad_sch)
# 3. Version consistency (pyproject.toml == __init__.py)
# 4. Python classifiers (no 3.8/3.9)
# 5. No broken links (grep for stm32g431)
# 6. Examples work (test voltage_divider.py)
# 7. Git status clean
# 8. CHANGELOG updated

# Exit 0 if all pass, 1 if any fail
```

#### 5.2.4 Root Pollution Prevention (.gitignore)

```gitignore
# Generated schematic files in root
/*.kicad_sch
!examples/*.kicad_sch
!tests/**/*.kicad_sch
```

#### 5.2.5 Pre-Commit Root Check (.pre-commit-config.yaml)

```yaml
- repo: local
  hooks:
    - id: check-root-pollution
      name: Prevent root directory pollution
      entry: bash -c '
        if git diff --cached --name-only | grep -E "^[^/]+\.kicad_sch$"; then
          echo "❌ ERROR: Cannot commit .kicad_sch to root!"
          exit 1
        fi
      '
      language: system
      pass_filenames: false
      always_run: true
```

### 5.3 Data Model Changes

**None** - This is a process/tooling project, no data model changes.

### 5.4 API Changes

**None** - No public API changes.

---

## 6. Implementation Plan

### Phase 1: Security Hardening (Day 1, 2 hours)

**Tasks:**
1. ✅ Create `.pypirc.example` template
2. ✅ Add gitleaks to `.pre-commit-config.yaml`
3. ✅ Create `.gitleaks.toml` configuration
4. ✅ Add `detect-private-key` hook
5. ✅ Test: Try committing secrets → verify blocked

**Deliverables:**
- `.pypirc.example`
- `.gitleaks.toml`
- Updated `.pre-commit-config.yaml`

**Validation:**
```bash
# Test secret detection
echo "password = pypi-AgEI..." > test.txt
git add test.txt
git commit -m "test"  # Should FAIL
```

### Phase 2: Documentation Fixes (Day 1, 1 hour)

**Tasks:**
1. ✅ Remove `stm32g431_simple.py` references from README.md
2. ✅ Remove `stm32g431_simple.py` references from CLAUDE.md
3. ✅ Update docs/HIERARCHY_FEATURES.md
4. ✅ Fix examples/README.md directory structure
5. ✅ Verify all example paths work

**Deliverables:**
- Updated README.md
- Updated CLAUDE.md
- Updated docs/HIERARCHY_FEATURES.md
- Updated examples/README.md

**Validation:**
```bash
# No broken references
grep -r "stm32g431" README.md CLAUDE.md docs/ examples/
# Should return nothing
```

### Phase 3: Packaging Fixes (Day 1, 30 minutes)

**Tasks:**
1. ✅ Remove Python 3.8/3.9 from pyproject.toml classifiers
2. ✅ Update Black target-version to match
3. ✅ Fix version in kicad_sch_api/__init__.py
4. ✅ Verify version consistency

**Deliverables:**
- Updated pyproject.toml
- Updated kicad_sch_api/__init__.py

**Validation:**
```bash
# Check version
python -c "import kicad_sch_api; print(kicad_sch_api.__version__)"
grep 'version = ' pyproject.toml
# Should both show 0.5.1
```

### Phase 4: Repository Cleanup (Day 1, 1 hour)

**Tasks:**
1. ✅ Update .gitignore with root-level patterns
2. ✅ Create scripts/clean_root.sh
3. ✅ Add pre-commit hook for root pollution
4. ✅ Make scripts executable
5. ✅ Test cleanup script

**Deliverables:**
- Updated .gitignore
- scripts/clean_root.sh
- Updated .pre-commit-config.yaml (root check)

**Validation:**
```bash
# Test cleanup
touch test.kicad_sch
./scripts/clean_root.sh
ls *.kicad_sch  # Should be gone
```

### Phase 5: Release Automation (Day 1, 2 hours)

**Tasks:**
1. ✅ Create scripts/pre_release_check.sh with 8 checks
2. ✅ Create RELEASE_CHECKLIST.md
3. ✅ Create FIXES_APPLIED.md documentation
4. ✅ Make scripts executable
5. ✅ Test pre-release script

**Deliverables:**
- scripts/pre_release_check.sh
- RELEASE_CHECKLIST.md
- FIXES_APPLIED.md

**Validation:**
```bash
# Run pre-release check
./scripts/pre_release_check.sh
# Should pass all checks (or show clear failures)
```

### Phase 6: Testing & Validation (Day 2, 2 hours)

**Tasks:**
1. Run pre-commit hooks on all files
2. Run pre-release check script
3. Test all examples execute
4. Verify all documentation accurate
5. Code review all changes

**Validation Checklist:**
- [ ] All pre-commit hooks pass
- [ ] Pre-release script passes
- [ ] All examples run successfully
- [ ] No broken doc links
- [ ] Version consistent
- [ ] No secrets detected
- [ ] Root directory clean

### Phase 7: Documentation & Handoff (Day 2, 1 hour)

**Tasks:**
1. Update CONTRIBUTING.md with new process
2. Add release process to README (optional)
3. Create PR with all changes
4. Document in CHANGELOG.md

---

## 7. Testing Strategy

### 7.1 Security Testing

**Test:** Secret Detection
- Create file with PyPI token
- Try to commit
- **Expected:** Pre-commit hook blocks commit

**Test:** Private Key Detection
- Create file with SSH key pattern
- Try to commit
- **Expected:** Pre-commit hook blocks commit

### 7.2 Documentation Testing

**Test:** No Broken Links
```bash
grep -r "stm32g431" README.md CLAUDE.md docs/ examples/
# Expected: No results
```

**Test:** Examples Work
```bash
uv run python examples/voltage_divider.py
uv run python examples/rc_filter.py
uv run python examples/power_supply.py
uv run python examples/stm32_simple.py
# Expected: All succeed
```

### 7.3 Packaging Testing

**Test:** Version Consistency
```bash
python -c "import kicad_sch_api; print(kicad_sch_api.__version__)"
grep 'version = ' pyproject.toml
# Expected: Both show same version
```

**Test:** Python Classifiers
```bash
grep 'Programming Language :: Python :: 3\.[89]' pyproject.toml
# Expected: No results
```

### 7.4 Automation Testing

**Test:** Pre-Release Script
```bash
./scripts/pre_release_check.sh
# Expected: All checks pass (green)
```

**Test:** Cleanup Script
```bash
touch test.kicad_sch demo_test.py
./scripts/clean_root.sh
ls test.kicad_sch demo_test.py
# Expected: Files deleted
```

### 7.5 Integration Testing

**Test:** Full Release Dry-Run
```bash
# 1. Clean
./scripts/clean_root.sh

# 2. Validate
./scripts/pre_release_check.sh

# 3. Build
uv build

# 4. Check package
tar -tzf dist/kicad-sch-api-*.tar.gz | grep -E '(\.pypirc|test_circuit|demo_)'
# Expected: No secrets or test files
```

---

## 8. Success Metrics

### Launch Criteria (Must Pass Before Release)

1. ✅ **Security:**
   - Pre-commit hooks detect secrets (tested)
   - No `.pypirc` in git history
   - Gitleaks config validated

2. ✅ **Documentation:**
   - Zero broken links (`grep -r stm32g431` returns nothing)
   - All example paths valid
   - Examples README matches structure

3. ✅ **Packaging:**
   - Python classifiers = [3.10, 3.11, 3.12]
   - Version consistent (pyproject.toml == __init__.py)

4. ✅ **Repository:**
   - Root directory clean (no `*.kicad_sch`)
   - Pre-commit hooks block pollution
   - Cleanup script works

5. ✅ **Automation:**
   - Pre-release check passes all 8 checks
   - Scripts executable and documented

### Post-Launch Metrics

**Immediate (Week 1):**
- No security incidents from leaked credentials
- No user reports of broken documentation
- PyPI package installs successfully on Python 3.10+

**Medium-term (Month 1):**
- Pre-commit hooks prevent ≥3 accidental commits
- Pre-release script catches ≥1 issue before release
- Zero bad releases to PyPI

---

## 9. Risks & Mitigations

### Risk 1: Pre-commit Hooks Too Restrictive

**Probability:** Medium
**Impact:** Low
**Description:** Hooks block legitimate commits

**Mitigation:**
- Gitleaks allowlist for examples/docs
- Clear error messages with bypass instructions
- `SKIP=gitleaks git commit` escape hatch

### Risk 2: Scripts Break on Different Environments

**Probability:** Low
**Impact:** Medium
**Description:** Bash scripts assume Linux/Mac

**Mitigation:**
- Use POSIX-compliant bash
- Test on Mac (already done)
- Document requirements in script headers
- Provide manual steps as fallback

### Risk 3: False Sense of Security

**Probability:** Low
**Impact:** High
**Description:** Hooks give false confidence, real secret leaks through

**Mitigation:**
- Multiple layers (detect-private-key + gitleaks)
- Regular gitleaks scans: `gitleaks detect`
- Document limitations clearly
- Periodic manual audits

### Risk 4: Maintenance Burden

**Probability:** Medium
**Impact:** Low
**Description:** Scripts/hooks need updates, become outdated

**Mitigation:**
- `pre-commit autoupdate` keeps hooks current
- Simple, maintainable scripts (<100 lines)
- Clear documentation
- Automated tests for scripts

---

## 10. Open Questions

1. **Q:** Should we run gitleaks on entire git history before release?
   **A:** Yes, run `gitleaks detect --verbose` as final check

2. **Q:** Should we enforce pre-commit hooks in CI/CD?
   **A:** Not in this PRD - future enhancement

3. **Q:** Should examples output to examples/ instead of root?
   **A:** Future improvement - out of scope for this PRD

4. **Q:** Should we add GitHub Actions to validate PRs?
   **A:** Future enhancement - manual validation sufficient for now

---

## 11. Timeline

**Total Effort:** 1-2 days

| Phase | Duration | Status |
|-------|----------|--------|
| Security Hardening | 2 hours | ✅ Complete |
| Documentation Fixes | 1 hour | ✅ Complete |
| Packaging Fixes | 30 min | ✅ Complete |
| Repository Cleanup | 1 hour | ✅ Complete |
| Release Automation | 2 hours | ✅ Complete |
| Testing & Validation | 2 hours | 🔄 In Progress |
| Documentation | 1 hour | ⏳ Pending |

**Target Completion:** End of Day 2

---

## 12. Rollout Plan

### Phase 1: Branch & Development
```bash
git checkout -b chore/release-preparation
# Implement all changes
```

### Phase 2: Testing
```bash
# Run all validations
./scripts/pre_release_check.sh
pre-commit run --all-files
uv run pytest tests/ -v
```

### Phase 3: PR & Review
```bash
# Create PR
git push origin chore/release-preparation
gh pr create --title "chore: Release preparation & security hardening" \
             --body "Implements comprehensive release preparation (see docs/PRD_RELEASE_PREPARATION.md)"
```

### Phase 4: Merge & Release
```bash
# After approval
git checkout main
git merge chore/release-preparation
./scripts/pre_release_check.sh  # Final validation
uv build
uv publish
git tag -a v0.5.1 -m "Release v0.5.1"
git push origin v0.5.1
```

---

## 13. Future Enhancements (Out of Scope)

1. **GitHub Actions CI/CD**
   - Run pre-commit hooks on every PR
   - Automated PyPI publishing on tag
   - Test matrix for Python 3.10, 3.11, 3.12

2. **Example Output Management**
   - Modify examples to output to `examples/output/`
   - Add `examples/output/` to gitignore
   - Better organization of generated files

3. **Dependency Scanning**
   - Dependabot for security updates
   - `safety` checks for vulnerable dependencies

4. **Advanced Secret Detection**
   - GitHub secret scanning (automatic on public repos)
   - Periodic gitleaks scans in CI

5. **Release Automation**
   - `bump2version` for automated version management
   - Automated CHANGELOG generation
   - Release notes from git commits

---

## 14. Appendix

### A. Related Documents

- [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) - Complete release process
- [FIXES_APPLIED.md](../FIXES_APPLIED.md) - Implementation details
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributor guidelines

### B. Tools & Dependencies

- **gitleaks** v8.18.2 - Secret scanning
- **pre-commit** - Git hook framework
- **bash** - Scripting (POSIX-compliant)
- **uv** - Python package manager

### C. References

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Next Review:** After implementation completion
