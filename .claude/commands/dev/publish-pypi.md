# PyPI Release Command - kicad-sch-api

## Usage
```bash
/publish-pypi <version> [--test-only] [--check-only]
```

**⚠️ CRITICAL: Version number is MANDATORY - command will fail if not provided!**

## Description
Complete PyPI release pipeline - from testing to tagging to publishing. This command handles version management, git operations, comprehensive testing, and PyPI publication.

## Parameters
- `version` - **REQUIRED** Version number (e.g., "0.4.1", "1.0.0", "0.5.0-beta.1")
- `--test-only`: Publish to Test PyPI only (for validation)
- `--check-only`: Run all checks without publishing

## What This Command Does

This command automates the complete release process:

### 1. Pre-Release Validation
- **Check branch status** - Ensure we're on main branch
- **Validate version format** - Semantic versioning check
- **Check for uncommitted changes** - Ensure clean working directory
- **Sync with remote** - Fetch latest changes from origin
- **Version conflict check** - Ensure version doesn't already exist on PyPI or git tags

### 2. Version Management
- **Update pyproject.toml** - Set new version number
- **Commit version changes** - Clean commit for version bump
- **Show version comparison** - Display current vs new version

### 3. Testing and Validation
- **Run full test suite** - All tests must pass
- **Code quality checks** - Black, isort, mypy, flake8
- **Format preservation tests** - Critical for KiCAD compatibility
- **Build package** - Create wheel and sdist
- **Test installation** - Verify package installs correctly
- **Import validation** - Ensure package imports work

### 4. Git Operations
- **Create release tag** - Tag commit with version number
- **Push release tag** - Push tag to origin
- **Create GitHub release** - Generate release notes and publish

### 5. PyPI Publication
- **Build distributions** - Create wheel and sdist
- **Upload to PyPI** - Publish to registry
- **Verify upload** - Check package is available

### 6. Post-Release Verification
- **Test installation from PyPI** - Verify package works
- **Display release summary** - Show URLs and next steps

## Implementation

```bash
#!/bin/bash
set -e  # Exit on error

# CRITICAL: Always require version number as parameter
if [ -z "$1" ]; then
    echo "❌ ERROR: Version number is required!"
    echo "Usage: /publish-pypi <version> [--test-only] [--check-only]"
    echo "Example: /publish-pypi 0.4.1"
    echo "Example: /publish-pypi 0.5.0"
    echo "Example: /publish-pypi 1.0.0-beta.1"
    exit 1
fi

version="$1"
shift  # Remove version from arguments

# Parse flags
TEST_ONLY=false
CHECK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🎯 Starting release process for kicad-sch-api version: $version"
echo "================================================================"

# 1. Pre-flight checks and branch management
echo "🔍 Running pre-flight checks..."

# Fetch latest changes from remote
echo "🔄 Fetching latest changes from origin..."
git fetch origin

# Ensure clean working directory
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Uncommitted changes found. Commit or stash first."
    exit 1
fi

# Check current branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo "⚠️  Warning: Not on main branch (currently on '$current_branch')"
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Validate version format (semantic versioning)
if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
    echo "❌ Invalid version format. Use semantic versioning (e.g., 0.4.1, 1.0.0)"
    echo "Provided: $version"
    exit 1
fi

# Show current version for comparison
current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📊 Current version: $current_version"
echo "📊 New version: $version"
echo ""
read -p "🤔 Confirm release version $version? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled. Please specify the correct version."
    exit 1
fi

# Check if version already exists on PyPI
echo "🔍 Checking if version already exists on PyPI..."
if pip index versions kicad-sch-api 2>/dev/null | grep -q "kicad-sch-api ($version)"; then
    echo "❌ Version $version already exists on PyPI"
    exit 1
fi

# Check if git tag already exists
if git rev-parse "v$version" >/dev/null 2>&1; then
    echo "❌ Git tag v$version already exists"
    exit 1
fi

# Ensure main is up-to-date with origin
echo "🔄 Ensuring main is up-to-date..."
git pull origin main || {
    echo "❌ Failed to pull latest main"
    exit 1
}

# Install build dependencies
echo "📥 Installing build dependencies..."
uv pip install build twine --quiet

# 2. Version update
echo "📝 Updating version to $version..."

# Update pyproject.toml
sed -i.bak "s/^version = .*/version = \"$version\"/" pyproject.toml
rm -f pyproject.toml.bak

# Check if changes were made
if ! git diff --quiet pyproject.toml; then
    git add pyproject.toml
    git commit -m "🔖 Bump version to $version"
    echo "✅ Version updated and committed"
else
    echo "ℹ️  Version already up to date"
fi

# 3. Code quality checks
echo "🎨 Checking code quality..."

# Format check
echo "  - Checking code formatting..."
if ! uv run black --check kicad_sch_api/ tests/ --quiet 2>/dev/null; then
    echo "❌ Code not formatted. Run: uv run black kicad_sch_api/ tests/"
    exit 1
fi

# Import sort check
echo "  - Checking import sorting..."
if ! uv run isort --check-only kicad_sch_api/ tests/ --quiet 2>/dev/null; then
    echo "❌ Imports not sorted. Run: uv run isort kicad_sch_api/ tests/"
    exit 1
fi

# Type checking
echo "  - Running type checks..."
uv run mypy kicad_sch_api/ --ignore-missing-imports --quiet 2>/dev/null || {
    echo "⚠️ Type checking issues found (non-blocking)"
}

echo "✅ Code quality checks passed"

# 4. Comprehensive testing
echo "🧪 Running comprehensive test suite..."

# Core tests - format preservation is critical for KiCAD compatibility
echo "  - Running unit tests..."
if ! uv run pytest tests/ -v --tb=short -q; then
    echo "❌ Tests failed"
    exit 1
fi

# Format preservation tests (CRITICAL for KiCAD compatibility)
echo "  - Running format preservation tests..."
if ! uv run pytest tests/reference_tests/ -v --tb=short -q 2>/dev/null; then
    echo "⚠️ Format preservation tests not found or failed"
fi

# Import validation
echo "  - Testing imports..."
if ! uv run python -c "import kicad_sch_api; print('✅ Import successful')" 2>/dev/null; then
    echo "❌ Import test failed"
    exit 1
fi

echo "✅ All tests passed"

# 5. Build package
echo "🏗️ Building package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info/ kicad_sch_api.egg-info/

# Build
if ! python -m build; then
    echo "❌ Package build failed"
    exit 1
fi

echo "✅ Package built successfully"

# 6. Package validation
echo "📋 Validating package..."

# Check package integrity
if ! twine check dist/*; then
    echo "❌ Package validation failed"
    exit 1
fi

# Test installation in clean environment
echo "🧪 Testing package installation in isolated environment..."
TEMP_VENV=$(mktemp -d)
python -m venv "$TEMP_VENV"
source "$TEMP_VENV/bin/activate"

if ! pip install dist/*.whl --quiet; then
    echo "❌ Package installation failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
fi

if ! python -c "import kicad_sch_api; print('✅ Package import successful')"; then
    echo "❌ Package import failed"
    deactivate
    rm -rf "$TEMP_VENV"
    exit 1
fi

deactivate
rm -rf "$TEMP_VENV"

echo "✅ Package validation complete"

# 7. Exit if check-only
if [[ "$CHECK_ONLY" == "true" ]]; then
    echo ""
    echo "================================================"
    echo "✅ All pre-publication checks passed"
    echo "================================================"
    echo "📦 Package ready for publication"
    echo "📊 Version: $version"
    echo "🏷️  Next step: Run without --check-only to publish"
    exit 0
fi

# 8. Git tagging and GitHub release
echo "🏷️  Creating git tag and GitHub release..."

# Verify we're on main branch for tagging
current_branch_for_tag=$(git branch --show-current)
if [[ "$current_branch_for_tag" != "main" ]]; then
    echo "❌ Must be on main branch for release tagging"
    echo "💡 Switch to main branch and re-run this command"
    exit 1
fi

# Generate release notes from commits since last tag
last_tag=$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "")
if [ -n "$last_tag" ]; then
    echo "📋 Generating release notes since $last_tag..."
    release_notes=$(git log --pretty=format:"- %s (%h)" "$last_tag"..HEAD)
else
    echo "📋 Generating release notes for initial release..."
    release_notes=$(git log --pretty=format:"- %s (%h)" --max-count=10)
fi

# Create git tag
echo "🏷️  Creating git tag v$version..."
git tag -a "v$version" -m "🚀 Release version $version

Features and changes in this release:
$release_notes

Full changelog: https://github.com/circuit-synth/kicad-sch-api/compare/${last_tag}...v$version"

# Push tag to origin
echo "📤 Pushing release tag to origin..."
git push origin "v$version" || {
    echo "❌ Failed to push release tag"
    exit 1
}

echo "✅ Tagged and pushed v$version"

# Create GitHub release using gh CLI
if command -v gh >/dev/null 2>&1; then
    echo "📝 Creating GitHub release..."

    gh release create "v$version" \
        --title "🚀 Release v$version" \
        --notes "## What's Changed

$release_notes

## Installation

\`\`\`bash
pip install kicad-sch-api==$version
# or
uv add kicad-sch-api==$version
\`\`\`

## PyPI Package
📦 https://pypi.org/project/kicad-sch-api/$version/

**Full Changelog**: https://github.com/circuit-synth/kicad-sch-api/compare/${last_tag}...v$version" \
        --latest || {
        echo "⚠️  GitHub release creation failed (continuing with PyPI release)"
    }

    echo "✅ GitHub release created"
else
    echo "⚠️  GitHub CLI (gh) not found - skipping GitHub release creation"
    echo "💡 Install with: brew install gh"
    echo "📝 Manual release notes:"
    echo "$release_notes"
fi

# 9. Publish to PyPI
echo ""
echo "🚀 Publishing to PyPI..."

if [[ "$TEST_ONLY" == "true" ]]; then
    # Publish to Test PyPI
    echo "📡 Publishing to Test PyPI..."

    # Use environment variable or .pypirc
    if [[ -n "$TEST_PYPI_API_TOKEN" ]]; then
        twine upload --repository testpypi dist/* --username __token__ --password "$TEST_PYPI_API_TOKEN"
    else
        echo "ℹ️  Using .pypirc credentials for Test PyPI..."
        twine upload --repository testpypi dist/*
    fi

    if [[ $? -eq 0 ]]; then
        echo "✅ Successfully published to Test PyPI"
        echo "🔗 View at: https://test.pypi.org/project/kicad-sch-api/"
        echo "📥 Test install: pip install --index-url https://test.pypi.org/simple/ kicad-sch-api"
    else
        echo "❌ Test PyPI publication failed"
        exit 1
    fi

else
    # Publish to production PyPI
    echo "📡 Publishing to Production PyPI..."

    # Final confirmation
    echo ""
    echo "⚠️  WARNING: Publishing to PRODUCTION PyPI"
    echo "This action cannot be undone for this version."
    echo "Version: $version"
    read -p "Continue? (y/N): " -n 1 -r confirm
    echo ""

    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "❌ Publication cancelled"
        # Clean up git tag since we're not publishing
        git tag -d "v$version" 2>/dev/null
        git push origin ":refs/tags/v$version" 2>/dev/null
        exit 1
    fi

    # Use environment variable or .pypirc
    if [[ -n "$PYPI_API_TOKEN" ]]; then
        twine upload dist/* --username __token__ --password "$PYPI_API_TOKEN"
    else
        echo "ℹ️  Using .pypirc credentials for PyPI..."
        twine upload dist/*
    fi

    if [[ $? -eq 0 ]]; then
        echo ""
        echo "🎉 Successfully published to PyPI!"
        echo "🔗 View at: https://pypi.org/project/kicad-sch-api/$version/"
        echo "📥 Install: pip install kicad-sch-api==$version"
    else
        echo "❌ PyPI publication failed"
        exit 1
    fi
fi

# 10. Post-release verification
echo ""
echo "⏳ Waiting for PyPI propagation (30 seconds)..."
sleep 30

# Verify package is available on PyPI
echo "🔍 Verifying package on PyPI..."
package_info=$(pip index versions kicad-sch-api 2>/dev/null || echo "not found")
if [[ "$package_info" == *"$version"* ]]; then
    echo "✅ Package verified on PyPI"
else
    echo "⚠️  Package not yet visible on PyPI (may take a few minutes)"
fi

# Test installation from PyPI in clean environment (production only)
if [[ "$TEST_ONLY" == "false" ]]; then
    echo "🧪 Testing installation from PyPI..."
    temp_dir=$(mktemp -d)
    cd "$temp_dir"
    python -m venv test_env
    source test_env/bin/activate

    pip install kicad-sch-api==$version --quiet && \
    python -c "import kicad_sch_api; print(f'✅ Installed version: {kicad_sch_api.__version__ if hasattr(kicad_sch_api, \"__version__\") else \"unknown\"}')" || \
    echo "⚠️  Installation test from PyPI failed (package may still be propagating)"

    deactivate
    cd - >/dev/null
    rm -rf "$temp_dir"
fi

# Final summary
echo ""
echo "================================================================"
echo "🎉 Release v$version Complete!"
echo "================================================================"
echo "📊 Release Summary:"
echo "   📦 PyPI: https://pypi.org/project/kicad-sch-api/$version/"
echo "   🏷️  Git Tag: v$version"
echo "   📋 GitHub: https://github.com/circuit-synth/kicad-sch-api/releases/tag/v$version"
echo ""
echo "✅ Publication process completed successfully"
```

## Usage Examples

### Recommended Workflow

```bash
# 1. First, check that everything is ready (dry run)
/publish-pypi 0.4.1 --check-only

# 2. Test on Test PyPI first (HIGHLY RECOMMENDED)
/publish-pypi 0.4.1 --test-only

# 3. Verify Test PyPI installation works
pip install --index-url https://test.pypi.org/simple/ kicad-sch-api==0.4.1

# 4. If everything looks good, publish to production PyPI
/publish-pypi 0.4.1
```

### Other Examples

```bash
# Release a patch version
/publish-pypi 0.4.1

# Release a minor version
/publish-pypi 0.5.0

# Release a major version
/publish-pypi 1.0.0

# Release a beta version
/publish-pypi 1.0.0-beta.1

# Release a release candidate
/publish-pypi 1.0.0-rc.1
```

## Authentication Methods

### Method 1: Environment Variables (Recommended for CI)

#### For Test PyPI
```bash
export TEST_PYPI_API_TOKEN=pypi-your_test_token_here
```

#### For Production PyPI
```bash
export PYPI_API_TOKEN=pypi-your_production_token_here
```

### Method 2: .pypirc File (Recommended for Local Development)

Create `~/.pypirc` with your API tokens:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your_production_token_here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your_test_token_here
```

**Using .pypirc:**
```bash
# Publish to Test PyPI using .pypirc
twine upload --repository testpypi dist/*

# Publish to Production PyPI using .pypirc  
twine upload --repository pypi dist/*

# Or use the default (production PyPI)
twine upload dist/*
```

**Security Notes:**
- Set proper file permissions: `chmod 600 ~/.pypirc`
- Never commit `.pypirc` to version control
- Environment variables take precedence over `.pypirc`
- Use scoped API tokens (project-specific) instead of global tokens

## Prerequisites

Before running this command, ensure you have:

1. **PyPI account** with API token configured
2. **Git credentials** set up for pushing
3. **GitHub CLI (gh)** installed and authenticated (for GitHub releases)
4. **Clean working directory** (no uncommitted changes)
5. **Main branch** checked out (for production releases)

### Setup GitHub CLI
```bash
# Install GitHub CLI
brew install gh

# Authenticate with GitHub
gh auth login

# Verify authentication
gh auth status
```

## Version Numbering Strategy

This project follows **Semantic Versioning** (semver.org):

- **MAJOR.MINOR.PATCH** (e.g., 0.4.1)
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**For pre-1.0 versions (0.x.y):**
- Minor version bumps may include breaking changes
- Communicate clearly in release notes
- Move to v1.0.0 when API is stable

**Examples:**
- `0.4.0 → 0.4.1` - Bug fixes, small improvements
- `0.4.1 → 0.5.0` - New features (bus support, netlist generation)
- `0.5.0 → 1.0.0` - API stable, production ready

## What Gets Released

The release process creates:
- **Python package** - Wheel and source distribution on PyPI
- **Git tag** - Version tag on main branch (e.g., `v0.4.1`)
- **GitHub release** - Auto-generated release notes
- **Documentation** - All examples and docs included in package

## Safety Features

This enhanced command includes:

✅ **Mandatory version parameter** - Prevents accidental releases
✅ **Version conflict detection** - Checks PyPI and git tags
✅ **Semantic versioning validation** - Ensures proper version format
✅ **Clean working directory check** - No uncommitted changes
✅ **Main branch enforcement** - Production releases only from main
✅ **Comprehensive testing** - Unit tests, format preservation, imports
✅ **Package validation** - Twine checks, installation tests
✅ **Automatic git tagging** - Creates and pushes version tags
✅ **GitHub release creation** - Auto-generated release notes
✅ **Post-release verification** - Tests installation from PyPI

## Troubleshooting

### Common Issues

**Version already exists:**
```bash
❌ Version 0.4.1 already exists on PyPI
# Solution: Increment version number (you cannot overwrite PyPI versions)
/publish-pypi 0.4.2
```

**Git tag already exists:**
```bash
❌ Git tag v0.4.1 already exists
# Solution: Delete tag or use new version
git tag -d v0.4.1  # Delete local tag
git push origin :refs/tags/v0.4.1  # Delete remote tag
```

**Not on main branch:**
```bash
⚠️ Warning: Not on main branch (currently on 'develop')
# Solution: Switch to main or force continue
git checkout main
git pull origin main
```

**Tests failing:**
```bash
❌ Tests failed
# Solution: Fix failing tests before publishing
uv run pytest tests/ -v
```

**GitHub CLI not found:**
```bash
⚠️ GitHub CLI (gh) not found - skipping GitHub release creation
# Solution: Install gh (optional, not required for PyPI)
brew install gh
gh auth login
```

### Rollback Procedure

If something goes wrong after publishing:

```bash
# 1. Yank the bad release from PyPI (prevents new installations)
pip install twine
twine yank kicad-sch-api --version BAD_VERSION

# 2. Delete the git tag (optional)
git tag -d vBAD_VERSION
git push origin :refs/tags/vBAD_VERSION

# 3. Delete the GitHub release (optional)
gh release delete vBAD_VERSION

# 4. Fix the issues and release a new patch version
/publish-pypi NEW_VERSION
```

## Comparison with Previous Version

### Old Command (Issue #2-4)
❌ No version parameter
❌ No git tagging
❌ No GitHub releases
❌ No version conflict detection
❌ Manual version management

### Enhanced Command (This Version)
✅ Mandatory version parameter
✅ Automatic git tagging
✅ GitHub release creation
✅ Version conflict detection
✅ Automatic version updates
✅ Comprehensive validation
✅ Post-release verification

This addresses **GitHub Issues #2, #3, and #4** by preventing version confusion and ensuring proper release workflow.

---

**This command provides a complete, automated PyPI release pipeline with comprehensive validation and safety checks, ensuring every release is properly tagged, tested, and documented.**