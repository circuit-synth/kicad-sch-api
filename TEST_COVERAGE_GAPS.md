# Test Coverage Gaps

**Current Overall Coverage: 59%** (3,333 / 8,209 lines of code)

## Critical Gaps (0% coverage)

- `discovery/search_index.py` - **0%** (192 lines) - Component search indexing completely untested
- `core/pin_utils.py` - **0%** (66 lines) - Pin utility functions untested

## High Priority (<30% coverage)

| Module | Coverage | Lines | Issue |
|--------|----------|-------|-------|
| `core/wire_routing.py` | 14% | 112 uncovered | Wire routing algorithm untested |
| `core/simple_manhattan.py` | 14% | 78 uncovered | Manhattan routing algorithm untested |
| `core/managers/text_elements.py` | 24% | 126 uncovered | Text element management missing tests |
| `core/managers/graphics.py` | 27% | 160 uncovered | Graphics/rectangle drawing untested |
| `core/managers/metadata.py` | 31% | 54 uncovered | Metadata management untested |
| `core/managers/sheet.py` | 33% | 102 uncovered | Hierarchical sheet handling untested |

## Medium Priority (30-60% coverage)

| Module | Coverage | Lines | Issue |
|--------|----------|-------|-------|
| `core/geometry.py` | 36% | 23 uncovered | Geometric calculations incomplete |
| `core/managers/wire.py` | 37% | 71 uncovered | Wire manager missing tests |
| `core/managers/file_io.py` | 50% | 40 uncovered | File I/O operations need tests |
| `core/components.py` | 48% | 178 uncovered | Component collection missing tests |
| `core/wires.py` | 54% | 48 uncovered | Wire collection needs more tests |
| `utils/validation.py` | 61% | 66 uncovered | Validation utility functions incomplete |
| `core/junctions.py` | 61% | 29 uncovered | Junction collection needs tests |

## Well Covered (>80%)

- `core/config.py` - **98%** ✅
- `symbols/validators.py` - **95%** ✅
- `core/formatter.py` - **93%** ✅
- `geometry/symbol_bbox.py` - **87%** ✅
- `symbols/resolver.py` - **86%** ✅
- `core/texts.py` - **81%** ✅
- `core/types.py` - **82%** ✅
- `core/managers/validation.py` - **82%** ✅

## Next Steps

1. **Phase 1:** Add tests for zero-coverage modules (search_index, pin_utils)
2. **Phase 2:** Improve routing algorithm tests (wire_routing, simple_manhattan)
3. **Phase 3:** Add graphics and text element manager tests
4. **Phase 4:** Improve component and wire collection test coverage
