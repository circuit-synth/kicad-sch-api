# Release Checklist

This checklist ensures clean, secure, and professional releases to PyPI.

## Pre-Release Checklist

### 1. Security & Credentials ✅

- [ ] **No secrets in code**: Run `./scripts/check_secrets.sh` (or gitleaks scan)
- [ ] **No .pypirc committed**: Verify `.pypirc` is in `.gitignore` and not in git
- [ ] **PyPI token stored securely**: Use environment variables or `~/.pypirc` (NOT in repo)
- [ ] **Pre-commit hooks installed**: Run `pre-commit install` if not already active

### 2. Code Quality ✅

```bash
# Format code
uv run black kicad_sch_api/ tests/ mcp_server/
uv run isort kicad_sch_api/ tests/ mcp_server/

# Type checking
uv run mypy kicad_sch_api/

# Linting
uv run flake8 kicad_sch_api/ tests/
```

- [ ] All code formatted with Black
- [ ] Imports sorted with isort
- [ ] Type checking passes (mypy)
- [ ] Linting passes (flake8)
- [ ] No critical TODOs remaining (document known limitations instead)

### 3. Testing ✅

```bash
# Run all tests
uv run pytest tests/ -v

# Run examples to verify they work
uv run python examples/COMBINED.py
```

- [ ] All tests pass (unit + integration + reference)
- [ ] All examples execute successfully
- [ ] Format preservation tests pass (critical!)
- [ ] Test coverage ≥70% (`pytest --cov`)

### 4. Documentation ✅

- [ ] **README.md** is accurate and up-to-date
- [ ] **CHANGELOG.md** updated with new version
- [ ] **API_REFERENCE.md** matches actual API
- [ ] **Examples** all work and are documented
- [ ] No broken links in documentation
- [ ] No references to missing files or examples
- [ ] Version number consistency (pyproject.toml, __init__.py, docs)

### 5. Repository Cleanliness ✅

```bash
# Clean up generated files
./scripts/clean_root.sh

# Check git status
git status
```

- [ ] No generated `.kicad_sch` files in root
- [ ] No test/demo scripts in root (`test_circuit_*.py`, `demo_*.py`)
- [ ] No lock files (`~*.kicad_sch.lck`)
- [ ] No `__pycache__` or `.pyc` files committed
- [ ] No large binary files committed

### 6. Version Management ✅

Update version in **TWO places**:

1. **`pyproject.toml`**: `version = "X.Y.Z"`
2. **`kicad_sch_api/__init__.py`**: `__version__ = "X.Y.Z"`

```bash
# Verify version consistency
python -c "import kicad_sch_api; print(kicad_sch_api.__version__)"
```

- [ ] Version bumped appropriately (patch/minor/major)
- [ ] Version consistent across all files
- [ ] CHANGELOG.md has entry for new version

### 7. PyPI Metadata ✅

Verify in `pyproject.toml`:

- [ ] **Python version classifiers** match `requires-python`
- [ ] **Keywords** are accurate and relevant
- [ ] **URLs** are correct (homepage, docs, issues, changelog)
- [ ] **Description** is accurate
- [ ] **License** is correct (MIT)
- [ ] **Dependencies** are up-to-date and minimal

### 8. Build & Package ✅

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
uv build

# Verify package contents
tar -tzf dist/kicad-sch-api-*.tar.gz | head -20
unzip -l dist/kicad_sch_api-*.whl | head -20
```

- [ ] Build succeeds without errors
- [ ] Package includes correct files (no test files, no secrets)
- [ ] Package size is reasonable (<5MB)

### 9. Test PyPI Upload (Recommended) ✅

```bash
# Upload to Test PyPI first
uv publish --publish-url https://test.pypi.org/legacy/

# Install from Test PyPI and verify
pip install --index-url https://test.pypi.org/simple/ kicad-sch-api
python -c "import kicad_sch_api; print(kicad_sch_api.__version__)"
```

- [ ] Test PyPI upload succeeds
- [ ] Package installs from Test PyPI
- [ ] Basic import works

### 10. Git Tagging ✅

```bash
# Create git tag
git tag -a v0.X.Y -m "Release version 0.X.Y"

# Push tag (ONLY after PyPI release succeeds)
git push origin v0.X.Y
```

- [ ] Git tag created with version number
- [ ] Tag pushed to GitHub (after successful PyPI release)

## Release Commands

### Production PyPI Release

```bash
# 1. Final verification
./scripts/pre_release_check.sh

# 2. Build package
uv build

# 3. Upload to PyPI
uv publish

# 4. Create GitHub release
gh release create v0.X.Y --title "Release v0.X.Y" --notes "See CHANGELOG.md"
```

## Post-Release Checklist

- [ ] PyPI package uploaded successfully
- [ ] GitHub release created with notes
- [ ] Git tag pushed to origin
- [ ] Documentation deployed (ReadTheDocs builds automatically)
- [ ] Announcement posted (if applicable)
- [ ] Version bumped to next dev version (e.g., `0.X.Y+1-dev`)

## Emergency Rollback

If something goes wrong:

1. **Cannot unpublish from PyPI** (by design)
2. **Yank the release** on PyPI (marks as broken)
   ```bash
   # Use PyPI web interface to yank release
   ```
3. **Release hotfix version** (e.g., 0.5.2 if 0.5.1 was bad)
4. **Document the issue** in CHANGELOG.md

## Security Best Practices

### Never Commit:
- `.pypirc` files
- API tokens or passwords
- Private keys
- `.env` files with secrets

### Always Use:
- Environment variables for secrets
- `~/.pypirc` for PyPI credentials (in home directory, not repo)
- Pre-commit hooks to catch secrets
- `.gitignore` patterns for sensitive files

### Tools for Secret Detection:
- `pre-commit` with `detect-private-key` hook
- `gitleaks` for comprehensive secret scanning
- GitHub secret scanning (automatic on public repos)

---

**Remember**: Once published to PyPI, a version **CANNOT be re-uploaded**. Always test thoroughly before publishing!
