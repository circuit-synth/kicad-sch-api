#!/bin/bash
# Pre-release verification script
# Runs all checks before publishing to PyPI

set -e

echo "🔍 Pre-Release Verification"
echo "======================================"
echo ""

# Track failures
FAILURES=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

function check_fail() {
    echo -e "${RED}❌ $1${NC}"
    FAILURES=$((FAILURES + 1))
}

function check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Check for secrets
echo "1️⃣  Checking for secrets..."
if [ -f .pypirc ]; then
    if git ls-files --error-unmatch .pypirc 2>/dev/null; then
        check_fail ".pypirc is tracked by git! Remove it immediately!"
    else
        check_pass ".pypirc exists but not tracked by git"
    fi
fi

if grep -r "pypi-Ag" . --include="*.py" --include="*.md" --exclude-dir=".git" --exclude-dir=".venv" 2>/dev/null | grep -v ".example" | grep -v "YOUR_TOKEN_HERE"; then
    check_fail "Found potential PyPI tokens in code!"
else
    check_pass "No PyPI tokens found in code"
fi

# 2. Check root directory cleanliness
echo ""
echo "2️⃣  Checking root directory..."
if ls *.kicad_sch 2>/dev/null | grep -v "^examples/" | grep -v "^tests/"; then
    check_warn "Generated .kicad_sch files in root. Run: ./scripts/clean_root.sh"
else
    check_pass "No generated schematic files in root"
fi

if ls test_circuit_*.py demo_*.py 2>/dev/null; then
    check_warn "Test/demo scripts in root. Consider moving to examples/"
else
    check_pass "No test/demo scripts in root"
fi

# 3. Check version consistency
echo ""
echo "3️⃣  Checking version consistency..."
PYPROJECT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
INIT_VERSION=$(grep '__version__ = ' kicad_sch_api/__init__.py | cut -d'"' -f2)

if [ "$PYPROJECT_VERSION" = "$INIT_VERSION" ]; then
    check_pass "Version consistent: $PYPROJECT_VERSION"
else
    check_fail "Version mismatch! pyproject.toml: $PYPROJECT_VERSION, __init__.py: $INIT_VERSION"
fi

# 4. Check Python version classifiers
echo ""
echo "4️⃣  Checking Python classifiers..."
if grep -q '"Programming Language :: Python :: 3.8"' pyproject.toml || \
   grep -q '"Programming Language :: Python :: 3.9"' pyproject.toml; then
    check_fail "Python 3.8/3.9 in classifiers but requires-python >= 3.10!"
else
    check_pass "Python version classifiers match requirements"
fi

# 5. Check for broken documentation links
echo ""
echo "5️⃣  Checking documentation..."
if grep -r "stm32g431_simple.py" README.md CLAUDE.md docs/ examples/ 2>/dev/null; then
    check_fail "References to missing stm32g431_simple.py found!"
else
    check_pass "No references to missing files"
fi

# 6. Check examples work
echo ""
echo "6️⃣  Testing examples..."
if command -v uv &> /dev/null; then
    if uv run python examples/voltage_divider.py > /dev/null 2>&1; then
        check_pass "voltage_divider.py works"
    else
        check_fail "voltage_divider.py failed!"
    fi
else
    check_warn "uv not found, skipping example tests"
fi

# 7. Check git status
echo ""
echo "7️⃣  Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    check_warn "Uncommitted changes detected. Commit before release."
    git status --short
else
    check_pass "Working directory clean"
fi

# 8. Check CHANGELOG updated
echo ""
echo "8️⃣  Checking CHANGELOG..."
if grep -q "\[Unreleased\]" CHANGELOG.md; then
    check_warn "CHANGELOG has [Unreleased] section. Update for release."
else
    if grep -q "$PYPROJECT_VERSION" CHANGELOG.md; then
        check_pass "CHANGELOG updated for version $PYPROJECT_VERSION"
    else
        check_fail "CHANGELOG missing entry for version $PYPROJECT_VERSION"
    fi
fi

# Summary
echo ""
echo "======================================"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "Ready to release version $PYPROJECT_VERSION"
    echo ""
    echo "Next steps:"
    echo "  1. uv build"
    echo "  2. uv publish"
    echo "  3. git tag -a v$PYPROJECT_VERSION -m 'Release v$PYPROJECT_VERSION'"
    echo "  4. git push origin v$PYPROJECT_VERSION"
    exit 0
else
    echo -e "${RED}❌ $FAILURES critical checks failed!${NC}"
    echo ""
    echo "Fix the issues above before releasing."
    exit 1
fi
