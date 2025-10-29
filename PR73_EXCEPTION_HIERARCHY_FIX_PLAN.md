# PR #73 Exception Hierarchy Fix Plan

**Date:** 2025-10-29
**Status:** Draft Implementation Plan
**PR:** https://github.com/circuit-synth/kicad-sch-api/pull/73

---

## Executive Summary

PR #73 introduces a modern exception hierarchy but has **critical implementation gaps** that prevent it from being merge-ready. This document provides a comprehensive, step-by-step plan to fix all identified issues while maintaining backward compatibility and project stability.

**Current Status:**
- ✅ Exception hierarchy design is excellent
- ✅ Test coverage is comprehensive (32 tests)
- ❌ Backward compatibility is BROKEN
- ❌ 1 critical test failing
- ❌ Documentation claims don't match implementation

**Estimated Fix Time:** 4-6 hours

---

## Critical Issues Analysis

### Issue #1: Broken Backward Compatibility (CRITICAL)

**Problem:**
The PR claims `utils/validation.py` was updated to import `ValidationError` from `core.exceptions`, but this was NOT done. Two separate `ValidationError` classes now exist:

1. `kicad_sch_api.utils.validation.ValidationError` (old, lines 46-67)
2. `kicad_sch_api.core.exceptions.ValidationError` (new)

**Impact Analysis:**
- **15+ files** currently import from `utils.validation`
- All existing code will use the OLD ValidationError
- New code will use the NEW ValidationError
- Exception catching will fail: `except ValidationError` won't catch both types
- This creates a split-brain situation in the codebase

**Files Affected:**
```
./core/labels.py
./core/managers/file_io.py
./core/managers/base.py
./core/managers/validation.py
./core/parser.py
./core/texts.py
./core/components.py
./core/no_connects.py
./core/schematic.py
./core/nets.py
./__init__.py
./library/cache.py
./symbols/validators.py
./symbols/cache.py
./collections/components.py
```

**Test Evidence:**
```
FAILED tests/unit/test_exceptions.py::TestBackwardCompatibility::test_validation_error_importable_from_utils
AssertionError: assert <class 'kicad_sch_api.utils.validation.ValidationError'> is <class 'kicad_sch_api.core.exceptions.ValidationError'>
```

---

### Issue #2: ValidationError API Incompatibility

**Problem:**
The two ValidationError classes have different signatures:

**Old (utils/validation.py:46-49):**
```python
def __init__(self, message: str, issues: List[ValidationIssue] = None):
    super().__init__(message)
    self.issues = issues or []
```

**New (core/exceptions.py:29-48):**
```python
def __init__(
    self,
    message: str,
    issues: Optional[List[Any]] = None,
    field: str = "",           # NEW - could break positional args
    value: Any = None,         # NEW - could break positional args
):
    self.issues = issues or []
    self.field = field
    self.value = value
    super().__init__(message)
```

**Breaking Change Risk:**
If any code calls `ValidationError(msg, issues_list)` with positional args, this will still work. But if code tries to access `.field` or `.value` on old ValidationError instances, it will fail.

**Recommendation:** This is acceptable as long as:
1. Old ValidationError is replaced by new one
2. New attributes are documented as additions
3. Old code continues to work (new params are optional with defaults)

---

### Issue #3: Type Hint Quality

**Problem:**
Several type hints are too generic:

```python
# Line 32
issues: Optional[List[Any]] = None  # Should be List['ValidationIssue']

# Line 54, 57, 65, 70
def get_errors(self) -> List[Any]:  # Should be List['ValidationIssue']
def get_warnings(self) -> List[Any]:  # Should be List['ValidationIssue']
```

**Impact:** Reduced type safety, IDE autocomplete won't work properly

---

### Issue #4: Circular Import Pattern Inconsistency

**Problem:**
The code uses `TYPE_CHECKING` to avoid circular imports (lines 11-12):

```python
if TYPE_CHECKING:
    from ..utils.validation import ValidationIssue, ValidationLevel
```

But then imports at runtime anyway (lines 57, 68):

```python
def get_errors(self) -> List[Any]:
    from ..utils.validation import ValidationLevel  # Runtime import
    # ...
```

**Analysis:**
This pattern is confused. `TYPE_CHECKING` is only useful when:
1. Import is ONLY needed for type hints
2. Import causes circular dependency
3. Import is NOT needed at runtime

If you need the import at runtime, the `TYPE_CHECKING` block is pointless.

**Recommended Fix:**
Since `ValidationLevel` is needed at runtime in `get_errors()` and `get_warnings()`, either:
- Remove `TYPE_CHECKING` and do normal import (test for circular dependency first)
- Keep runtime imports and remove `TYPE_CHECKING` import
- Use string annotations and keep `TYPE_CHECKING` (but still need runtime import for the actual enum)

---

### Issue #5: Inconsistent Error Context Patterns

**Problem:**
Different exception classes use different attribute patterns:

**ValidationError and subclasses:**
```python
ValidationError(message, field="x", value=-1000)
ReferenceError(message, field="reference", value="R1")
```

**Collection errors:**
```python
ElementNotFoundError(message, element_type="component", identifier="R1")
DuplicateElementError(message, element_type="wire", identifier="uuid-123")
```

**Why this matters:**
- Users must remember which exceptions use `field/value` vs `element_type/identifier`
- Cannot catch and handle errors uniformly
- Harder to build generic error handling logic

**Rationale:**
Looking at the use cases:
- `field/value`: Used for **validation** errors (invalid data in a field)
- `element_type/identifier`: Used for **collection** errors (element operations)

**Recommendation:** This is actually a **good design** because:
- Validation errors are about data correctness → `field/value` makes sense
- Collection errors are about element management → `element_type/identifier` makes sense

**Action:** Document this distinction clearly in code comments and user documentation.

---

### Issue #6: Missing Package-Level Exports

**Problem:**
Users must use full paths to import exceptions:

```python
from kicad_sch_api.core.exceptions import ValidationError
```

**Better UX:**
```python
from kicad_sch_api import ValidationError
```

**Current State:**
- `kicad_sch_api/__init__.py` exports some things but not exceptions
- `kicad_sch_api/core/__init__.py` doesn't export exceptions

---

### Issue #7: Documentation vs Implementation Mismatch

**Problem:**
PR description claims:
> "Updated `kicad_sch_api/utils/validation.py`:
> - Imports `ValidationError` from `core.exceptions`
> - Maintains all existing functionality"

**Reality:**
This was NOT done. The PR description is misleading.

**Impact:**
- Reviewers were misled into thinking backward compatibility was handled
- Merge would have broken production code

---

## Step-by-Step Fix Plan

### Phase 1: Fix Backward Compatibility (CRITICAL - 2 hours)

#### Step 1.1: Update utils/validation.py

**File:** `kicad_sch_api/utils/validation.py`

**Current (lines 46-67):**
```python
class ValidationError(Exception):
    """Exception raised when critical validation errors are found."""

    def __init__(self, message: str, issues: List[ValidationIssue] = None):
        super().__init__(message)
        self.issues = issues or []

    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue to this error."""
        self.issues.append(issue)

    def get_errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [
            issue
            for issue in self.issues
            if issue.level in (ValidationLevel.ERROR, ValidationLevel.CRITICAL)
        ]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [issue for issue in self.issues if issue.level == ValidationLevel.WARNING]
```

**Replace with:**
```python
# Import ValidationError from new exception hierarchy
from ..core.exceptions import ValidationError

# Re-export for backward compatibility
__all__ = ['ValidationError', 'ValidationIssue', 'ValidationLevel', 'SchematicValidator']
```

**Why this works:**
- Existing imports (`from kicad_sch_api.utils.validation import ValidationError`) continue to work
- Now returns the NEW ValidationError from core.exceptions
- Single source of truth
- Backward compatible

**Testing:**
```bash
# Should pass after fix
uv run pytest tests/unit/test_exceptions.py::TestBackwardCompatibility::test_validation_error_importable_from_utils -v
```

#### Step 1.2: Add __all__ Export List

**File:** `kicad_sch_api/utils/validation.py`

**Current:** No `__all__` defined

**Add at top (after imports):**
```python
__all__ = [
    'ValidationError',      # Re-exported from core.exceptions
    'ValidationIssue',
    'ValidationLevel',
    'SchematicValidator',
    'validate_schematic_file',
    'collect_validation_errors',
]
```

**Benefit:** Makes explicit what is part of the public API

---

### Phase 2: Improve Type Hints (30 minutes)

#### Step 2.1: Fix TYPE_CHECKING Pattern

**File:** `kicad_sch_api/core/exceptions.py`

**Option A: Remove TYPE_CHECKING (if no circular dependency)**

Test first:
```python
# At top of file
from typing import Any, List, Optional
from ..utils.validation import ValidationIssue, ValidationLevel

# Remove the TYPE_CHECKING block
```

Run tests to check for circular import. If tests pass, keep this approach.

**Option B: Keep TYPE_CHECKING (if circular dependency exists)**

```python
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.validation import ValidationIssue, ValidationLevel

# In method signatures, use string annotations
def get_errors(self) -> List['ValidationIssue']:
    from ..utils.validation import ValidationLevel
    # ... implementation
```

**Recommendation:** Try Option A first. Option B is only needed if circular import occurs.

#### Step 2.2: Improve Type Hints

**File:** `kicad_sch_api/core/exceptions.py`

**Changes:**

```python
# Line 32 - Change
issues: Optional[List[Any]] = None
# To
issues: Optional[List['ValidationIssue']] = None

# Line 54 - Change
def get_errors(self) -> List[Any]:
# To
def get_errors(self) -> List['ValidationIssue']:

# Line 65 - Change
def get_warnings(self) -> List[Any]:
# To
def get_warnings(self) -> List['ValidationIssue']:
```

**Note:** Use string annotations `'ValidationIssue'` if keeping TYPE_CHECKING pattern.

---

### Phase 3: Add Package-Level Exports (30 minutes)

#### Step 3.1: Export from core/__init__.py

**File:** `kicad_sch_api/core/__init__.py`

**Add:**
```python
# Exception hierarchy
from .exceptions import (
    KiCadSchError,
    ValidationError,
    ReferenceError,
    LibraryError,
    GeometryError,
    NetError,
    ParseError,
    FormatError,
    CollectionError,
    ElementNotFoundError,
    DuplicateElementError,
    CollectionOperationError,
    FileOperationError,
    CLIError,
    SchematicStateError,
)

# Update __all__ to include exceptions
__all__ = [
    # ... existing exports ...
    # Exceptions
    'KiCadSchError',
    'ValidationError',
    'ReferenceError',
    'LibraryError',
    'GeometryError',
    'NetError',
    'ParseError',
    'FormatError',
    'CollectionError',
    'ElementNotFoundError',
    'DuplicateElementError',
    'CollectionOperationError',
    'FileOperationError',
    'CLIError',
    'SchematicStateError',
]
```

#### Step 3.2: Export from main __init__.py

**File:** `kicad_sch_api/__init__.py`

**Add commonly-used exceptions:**
```python
# Exception hierarchy (commonly used)
from .core.exceptions import (
    KiCadSchError,
    ValidationError,
    ElementNotFoundError,
    DuplicateElementError,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    # Exceptions
    'KiCadSchError',
    'ValidationError',
    'ElementNotFoundError',
    'DuplicateElementError',
]
```

**Rationale:** Only export the most commonly used exceptions at package level. Users can still import specialized ones from `core.exceptions`.

---

### Phase 4: Documentation and Examples (1 hour)

#### Step 4.1: Add Docstring Examples

**File:** `kicad_sch_api/core/exceptions.py`

**Enhance key exception docstrings:**

```python
class ValidationError(KiCadSchError):
    """
    Raised when validation fails.

    Supports rich error context with field/value information and can collect
    multiple validation issues.

    Attributes:
        issues: List of ValidationIssue objects providing detailed error context
        field: Name of the field that failed validation (optional)
        value: The invalid value that was provided (optional)

    Examples:
        Basic validation error:
        >>> raise ValidationError("Invalid component reference")

        With field context:
        >>> raise ValidationError("Reference too short", field="reference", value="R")

        With validation issues:
        >>> issues = [ValidationIssue(...), ValidationIssue(...)]
        >>> raise ValidationError("Multiple errors found", issues=issues)

        Collecting errors:
        >>> error = ValidationError("Validation failed")
        >>> error.add_issue(ValidationIssue(...))
        >>> if error.get_errors():
        ...     raise error
    """
```

```python
class ElementNotFoundError(CollectionError):
    """
    Raised when an element is not found in a collection.

    Attributes:
        element_type: Type of element (e.g., 'component', 'wire', 'junction')
        identifier: The identifier used to search (e.g., 'R1', UUID)

    Examples:
        Component not found:
        >>> raise ElementNotFoundError(
        ...     "Component not found",
        ...     element_type="component",
        ...     identifier="R1"
        ... )

        Catching and handling:
        >>> try:
        ...     component = schematic.components.get("R1")
        ... except ElementNotFoundError as e:
        ...     print(f"Could not find {e.element_type}: {e.identifier}")
    """
```

#### Step 4.2: Create Usage Documentation

**File:** `docs/EXCEPTIONS.md` (new file)

```markdown
# Exception Hierarchy Guide

## Overview

kicad-sch-api uses a structured exception hierarchy to provide clear, actionable error information.

## Exception Tree

All exceptions inherit from `KiCadSchError`:

```
Exception
└── KiCadSchError (base for all kicad-sch-api errors)
    ├── ValidationError (data validation failures)
    │   ├── ReferenceError (invalid component references)
    │   ├── LibraryError (library/symbol issues)
    │   ├── GeometryError (invalid positions, dimensions)
    │   └── NetError (net-related errors)
    ├── ParseError (S-expression parsing failures)
    ├── FormatError (file format issues)
    ├── CollectionError (collection operation failures)
    │   ├── ElementNotFoundError (element lookup failures)
    │   ├── DuplicateElementError (duplicate elements)
    │   └── CollectionOperationError (other collection errors)
    ├── FileOperationError (file I/O failures)
    ├── CLIError (KiCad CLI execution failures)
    └── SchematicStateError (invalid schematic state)
```

## Usage Patterns

### Catching Specific Errors

[examples...]

### Rich Error Context

[examples...]

### Backward Compatibility

[examples...]
```

#### Step 4.3: Add Architecture Decision Record

**File:** `.memory_bank/decisionLog.md`

**Add entry:**
```markdown
## ADR-XXX: Exception Hierarchy Architecture

**Date:** 2025-10-29
**Status:** Accepted

### Context
The codebase was using generic Python exceptions (ValueError, KeyError, etc.) which made error handling difficult and debugging harder.

### Decision
Implement a structured exception hierarchy with:
1. Base exception: KiCadSchError
2. Category exceptions: ValidationError, CollectionError, etc.
3. Specialized exceptions: ReferenceError, ElementNotFoundError, etc.

### Consequences

**Positive:**
- Better error handling with specific exception types
- Rich error context (field/value for validation, element_type/identifier for collections)
- Easier debugging with meaningful exception names
- Backward compatible via utils.validation re-export

**Negative:**
- More exception classes to maintain
- Two different context patterns (field/value vs element_type/identifier)
- Requires migration of existing raise statements (Phase 2)

### Implementation Notes
- ValidationError attributes: field, value, issues list
- Collection error attributes: element_type, identifier
- utils.validation.ValidationError re-exports core.exceptions.ValidationError
```

---

### Phase 5: Testing and Verification (1 hour)

#### Step 5.1: Run Exception Tests

```bash
# Test exception hierarchy
uv run pytest tests/unit/test_exceptions.py -v

# Expected: All 32 tests should pass
```

#### Step 5.2: Run Backward Compatibility Tests

```bash
# Test that existing code still works
uv run pytest tests/ -k "validation" -v

# Verify imports work from both locations
python3 << 'EOF'
from kicad_sch_api.utils.validation import ValidationError as V1
from kicad_sch_api.core.exceptions import ValidationError as V2
from kicad_sch_api import ValidationError as V3

assert V1 is V2, "utils.validation should re-export core.exceptions"
assert V2 is V3, "package level should export core.exceptions"
print("✓ All imports reference same ValidationError class")
EOF
```

#### Step 5.3: Run Full Test Suite

```bash
# Run complete test suite
uv run pytest tests/ --tb=short -v

# Document baseline
# Current PR state: 470 passed, 8 skipped, 23 failed
# After fixes: Should have same or better passing rate
```

#### Step 5.4: Test Import Patterns

Create test file `tests/unit/test_exception_imports.py`:

```python
"""Test exception import patterns work correctly."""

def test_all_import_paths_work():
    """Test exceptions can be imported from multiple valid paths."""
    # Core location (canonical)
    from kicad_sch_api.core.exceptions import ValidationError as CoreVE

    # Utils location (backward compatibility)
    from kicad_sch_api.utils.validation import ValidationError as UtilsVE

    # Package level (convenience)
    from kicad_sch_api import ValidationError as PkgVE

    # All should be the same class
    assert CoreVE is UtilsVE
    assert UtilsVE is PkgVE
    assert CoreVE is PkgVE


def test_exception_attributes_work():
    """Test both old and new exception patterns work."""
    from kicad_sch_api import ValidationError

    # Old pattern (should still work)
    error1 = ValidationError("test error")
    assert error1.issues == []

    # New pattern with field/value
    error2 = ValidationError("test", field="x", value=100)
    assert error2.field == "x"
    assert error2.value == 100

    # Backward compat: old code doesn't access new attributes
    error3 = ValidationError("test")
    assert hasattr(error3, 'field')
    assert hasattr(error3, 'value')
```

---

### Phase 6: Update PR Description (15 minutes)

#### Step 6.1: Rewrite PR Description

Update the PR description to accurately reflect what was changed:

```markdown
## Summary

Implements a structured exception hierarchy with 13 exception classes organized under a base `KiCadSchError` class.

Resolves #69

## Changes

### 1. New Exception Hierarchy (`kicad_sch_api/core/exceptions.py`)

Created comprehensive exception hierarchy:
- Base: `KiCadSchError`
- Validation: `ValidationError` + 4 specialized types
- Collections: `CollectionError` + 3 specialized types
- Other: `ParseError`, `FormatError`, `FileOperationError`, `CLIError`, `SchematicStateError`

### 2. Backward Compatibility (`kicad_sch_api/utils/validation.py`)

**FIXED:** Updated to re-export `ValidationError` from `core.exceptions`:
```python
from ..core.exceptions import ValidationError
```

This ensures:
- Existing imports continue to work: `from kicad_sch_api.utils.validation import ValidationError`
- Single source of truth: only one ValidationError class
- All code uses the new exception hierarchy

### 3. Package-Level Exports

Added exports in:
- `kicad_sch_api/core/__init__.py` - all exceptions
- `kicad_sch_api/__init__.py` - commonly-used exceptions

Users can now import via:
```python
from kicad_sch_api import ValidationError, ElementNotFoundError
from kicad_sch_api.core.exceptions import GeometryError, LibraryError
```

### 4. Enhanced Type Hints

- Changed `List[Any]` to `List[ValidationIssue]`
- Improved type safety for better IDE support
- Fixed circular import handling

### 5. Documentation

- Added usage examples to docstrings
- Created `docs/EXCEPTIONS.md` guide
- Added ADR to decision log

### 6. Comprehensive Testing

32 unit tests covering:
- ✅ Exception hierarchy verification
- ✅ Backward compatibility
- ✅ Rich error context
- ✅ Import patterns
- ✅ Exception catching

## Testing Results

```bash
# Exception tests
pytest tests/unit/test_exceptions.py -v
# Result: 32 passed

# Import compatibility tests
pytest tests/unit/test_exception_imports.py -v
# Result: All import patterns work

# Full suite
pytest tests/ --tb=no -q
# Result: [UPDATE AFTER FIXES]
```

## Migration Notes

**This PR is Phase 1** of exception hierarchy adoption:
- ✅ Phase 1 (this PR): Add exception hierarchy, ensure backward compatibility
- 📋 Phase 2 (future PR): Migrate ~40 `raise ValueError/KeyError` to new hierarchy
- 📋 Phase 3 (future PR): Update documentation and examples

## Breaking Changes

**None.** This PR is fully backward compatible:
- Existing `ValidationError` imports work unchanged
- New optional attributes (`field`, `value`) don't break existing usage
- No changes to existing exception raises (Phase 2)
```

---

## Implementation Checklist

### Critical (Must Do)

- [ ] **Step 1.1:** Update `utils/validation.py` to re-export ValidationError from core.exceptions
- [ ] **Step 1.2:** Add `__all__` export list to utils/validation.py
- [ ] **Step 5.1:** Run and pass all exception tests
- [ ] **Step 5.2:** Verify backward compatibility
- [ ] **Step 5.3:** Run full test suite

### Important (Should Do)

- [ ] **Step 2.1:** Fix TYPE_CHECKING pattern (test for circular imports first)
- [ ] **Step 2.2:** Improve type hints (List[Any] → List[ValidationIssue])
- [ ] **Step 3.1:** Export exceptions from core/__init__.py
- [ ] **Step 3.2:** Export common exceptions from main __init__.py
- [ ] **Step 5.4:** Add import pattern tests

### Nice to Have (Could Do)

- [ ] **Step 4.1:** Add docstring examples
- [ ] **Step 4.2:** Create EXCEPTIONS.md documentation
- [ ] **Step 4.3:** Add ADR to decision log
- [ ] **Step 6.1:** Update PR description

---

## Testing Strategy

### Pre-Fix Validation

```bash
# Document current state
uv run pytest tests/unit/test_exceptions.py -v > pre_fix_results.txt

# Should show 1 failure:
# FAILED tests/unit/test_exceptions.py::TestBackwardCompatibility::test_validation_error_importable_from_utils
```

### Post-Fix Validation

```bash
# After Phase 1 fixes
uv run pytest tests/unit/test_exceptions.py -v
# Expected: 32/32 passed

# After Phase 3 fixes
uv run pytest tests/unit/test_exception_imports.py -v
# Expected: All import tests pass

# Full validation
uv run pytest tests/ -v
# Expected: No new failures beyond pre-existing issues
```

---

## Risk Assessment

### High Risk Items
1. ✅ **Backward compatibility** - Mitigated by re-export pattern
2. ✅ **Import failures** - Mitigated by comprehensive import tests

### Medium Risk Items
3. ⚠️ **Circular imports** - Test after removing TYPE_CHECKING
4. ⚠️ **Type hint changes** - Verify mypy passes after changes

### Low Risk Items
5. ✓ **Documentation** - No code impact
6. ✓ **Docstring examples** - No runtime impact

---

## Timeline

**Total Estimated Time: 4-6 hours**

- Phase 1 (Critical): 2 hours
- Phase 2 (Type Hints): 30 minutes
- Phase 3 (Exports): 30 minutes
- Phase 4 (Documentation): 1 hour
- Phase 5 (Testing): 1 hour
- Phase 6 (PR Update): 15 minutes

**Minimum Viable Fix:** Complete Phases 1 and 5 (3 hours)

---

## Success Criteria

### Must Have (Merge Blockers)
✅ All 32 exception tests pass
✅ Backward compatibility test passes
✅ No new test failures in full suite
✅ ValidationError imports work from utils.validation
✅ Single ValidationError class (not two separate ones)

### Should Have (Quality)
✅ Improved type hints (List[ValidationIssue])
✅ Package-level exports for common exceptions
✅ Import pattern tests
✅ Accurate PR description

### Nice to Have (Polish)
✅ Docstring examples
✅ EXCEPTIONS.md documentation
✅ ADR in decision log

---

## Post-Merge Tasks (Future PRs)

### Phase 2: Migrate Generic Exceptions
- Replace ~56 `raise ValueError/KeyError/RuntimeError` with new hierarchy
- Update tests to expect new exception types
- Estimated: 8-12 hours

### Phase 3: Documentation & Examples
- Update API_REFERENCE.md with exception details
- Add exception handling examples to README
- Create error handling guide
- Estimated: 4 hours

---

## Notes for Implementer

1. **Start with Phase 1 Step 1.1** - This is the critical fix
2. **Test immediately after Step 1.1** - Verify backward compat test passes
3. **Phase 2 optional if time-constrained** - Type hints can be improved in follow-up
4. **Don't skip testing** - Phase 5 is non-negotiable
5. **Update PR description accurately** - Don't claim things that weren't done

---

## Questions & Decisions

### Q: Should we keep TYPE_CHECKING pattern?
**A:** Test first. If no circular import occurs, remove it (simpler is better).

### Q: Should we export all exceptions at package level?
**A:** No, only common ones. Specialized exceptions can be imported from core.exceptions.

### Q: What about the different context patterns (field/value vs element_type/identifier)?
**A:** Keep both - they serve different purposes. Document the distinction.

### Q: Should we migrate existing raise statements in this PR?
**A:** No. This PR is Phase 1 (add hierarchy). Migration is Phase 2 (separate PR).

---

**Document Version:** 1.0
**Last Updated:** 2025-10-29
**Author:** Claude Code Review
**Status:** Ready for Implementation
