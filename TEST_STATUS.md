# Test Status

**Last Updated:** 2025-11-04

## Test Overview

According to project documentation and recent issue analysis:

- **Total Tests:** 432 tests
- **Passing:** ~410 tests (95%)
- **Failing:** ~14 tests
- **Skipped:** ~8 tests

## Known Test Issues

### 1. Collection Removal Tests (8 failures)
**Location:** `tests/unit/collections/test_components.py`
**Status:** Tests need updating after PR #55 refactoring
**Impact:** Functionality works, tests use outdated API
**Priority:** High

Failing tests:
- `test_remove_component_by_reference`
- `test_remove_component_by_uuid`
- `test_remove_component_by_object`
- `test_remove_nonexistent_component_by_uuid`
- `test_remove_component_invalid_type_reference`
- `test_remove_component_invalid_type_uuid`
- `test_remove_component_invalid_type_object`
- `test_remove_updates_indexes`

### 2. ERC Validation Tests (6 failures)
**Location:** `tests/test_erc/test_erc_validators.py`
**Status:** Incomplete ERC implementation (partial feature)
**Priority:** Medium

Failing tests:
- `test_detect_dangling_wire`
- `test_detect_unconnected_input`
- `test_detect_undriven_net`
- `test_invalid_reference_format`
- `test_erc_violation_codes_unique`
- `test_erc_suggested_fixes`

**Note:** ERC validation is a work-in-progress feature. Basic validation works, advanced connectivity checking is incomplete.

## Test Coverage

Overall coverage is 59% (3,333 / 8,209 lines).

### Well Covered Modules (>80%)
- `core/config.py` - 98% ✅
- `symbols/validators.py` - 95% ✅
- `core/formatter.py` - 93% ✅
- `geometry/symbol_bbox.py` - 87% ✅
- `symbols/resolver.py` - 86% ✅
- `core/types.py` - 82% ✅

### Modules Needing Coverage
- `discovery/search_index.py` - 0% (untested)
- `core/pin_utils.py` - 0% (untested)
- `core/wire_routing.py` - 14%
- `core/simple_manhattan.py` - 14%
- `core/managers/text_elements.py` - 24%
- `core/managers/graphics.py` - 27%

## Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test categories
uv run python -m pytest tests/reference_tests/ -v     # Format preservation
uv run python -m pytest tests/test_component_removal.py -v  # Component removal
uv run python -m pytest tests/unit/ -v                # Unit tests

# Run with coverage
uv run python -m pytest tests/ --cov=kicad_sch_api --cov-report=html
```

## Test Strategy

The project uses several testing approaches:

1. **Reference-based Testing:** Manual KiCAD files as ground truth for format preservation
2. **Format Preservation:** Byte-for-byte output validation against KiCAD
3. **Unit Tests:** Individual component and function testing
4. **Integration Tests:** File I/O and round-trip validation

## Known Limitations

See [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) for technical limitations that affect testing:
- Pin position calculations don't account for component rotation
- Wire connectivity analysis is simplified
- Component rotation not applied in bounding box calculations

## GitHub Issues

All test-related issues are tracked on GitHub:
- Issue #61: Collection removal test failures
- Issue #63: ERC validation status
- Issue #64: Wire connectivity analysis

## Next Steps

1. Update collection removal tests for new API (Issue #61)
2. Complete ERC implementation or mark as experimental (Issue #63)
3. Add tests for zero-coverage modules
4. Increase overall coverage to 70%+

---

**Note:** While some tests are failing, core functionality (component management, format preservation, file I/O) is stable and production-ready.
