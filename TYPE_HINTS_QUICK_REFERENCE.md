# Type Hints Quick Reference Guide

## Quick Summary

- **Total Errors**: 382
- **Critical Priority Files**: 5 (parser, validation, schematic, validators, components)
- **Estimated Time**: 3-4 weeks
- **Easy Wins Available**: ~100 errors (quick to fix)

## Error Distribution

```
no-untyped-def      173  ████████████████████████████░░░░ (45%)
arg-type             46  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░ (12%)
union-attr           33  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (9%)
assignment           31  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (8%)
var-annotated        27  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (7%)
no-any-return        16  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (4%)
attr-defined         16  ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (4%)
unreachable          10  █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ (3%)
```

## Top Files by Error Count

| Rank | File | Errors | Est. Hours |
|------|------|--------|-----------|
| 1 | core/parser.py | 59 | 8-10 |
| 2 | core/managers/validation.py | 34 | 6-8 |
| 3 | core/schematic.py | 29 | 6-8 |
| 4 | symbols/validators.py | 27 | 5-6 |
| 5 | core/components.py | 25 | 5-6 |
| 6 | core/nets.py | 19 | 3-4 |
| 7 | core/types.py | 18 | 3-4 |
| 8 | core/texts.py | 13 | 2-3 |
| 9 | core/labels.py | 13 | 2-3 |
| 10 | library/cache.py | 11 | 2-3 |

## Common Fixes (by Type)

### Fix Type 1: Add Return Type `-> None`
**Pattern**: `__post_init__` and other void methods
**Count**: ~100+ instances
**Difficulty**: Easy (1-2 min each)

```python
# Before
def __post_init__(self):
    self.x = float(self.x)

# After
def __post_init__(self) -> None:
    self.x = float(self.x)
```

**Files**: types.py, junctions.py, wires.py, formatter.py, config.py, etc.

### Fix Type 2: Fix Implicit Optional
**Pattern**: `param: Type = None` → `param: Type | None = None`
**Count**: ~30 instances
**Difficulty**: Easy (1 min each)

```python
# Before
def method(issues: list[ValidationIssue] = None):
    pass

# After
def method(issues: list[ValidationIssue] | None = None):
    pass
```

**Files**: wires.py, components.py, schematic.py, validation.py, managers/

### Fix Type 3: Add Type Annotation to Variable
**Pattern**: `var = set()` → `var: set[Type] = set()`
**Count**: ~25 instances
**Difficulty**: Easy-Medium (2-5 min each)

```python
# Before
visited = set()
counts = {}

# After
visited: set[str] = set()
counts: dict[str, int] = {}
```

**Files**: wire_routing.py, manhattan_routing.py, components.py, managers/

### Fix Type 4: Fix Enum Type Mismatch
**Pattern**: `ValidationIssue(level="error")` → `ValidationIssue(level=ValidationLevel.ERROR)`
**Count**: ~10 instances
**Difficulty**: Easy (1-2 min each)

**Files**: symbols/validators.py (10 instances), components.py (4 instances)

### Fix Type 5: Add Parameter Type
**Pattern**: `def func(param):` → `def func(param: Type):`
**Count**: ~50+ instances
**Difficulty**: Medium (5-10 min each)

```python
# Before
def are_pins_connected(schematic, comp1_ref: str, pin1_num: str):
    pass

# After
def are_pins_connected(schematic: Schematic, comp1_ref: str, pin1_num: str) -> bool:
    pass
```

**Files**: wire_routing.py, wires.py, parser.py, schematic.py, etc.

### Fix Type 6: Handle Any Return
**Pattern**: `return sexpdata.dumps(...)` needs type handling
**Count**: ~15 instances
**Difficulty**: Medium (5-10 min each)

```python
# Before
def format_value(...) -> str:
    return sexpdata.dumps(value)

# After
def format_value(...) -> str:
    result: Any = sexpdata.dumps(value)
    return str(result)
```

**Files**: formatter.py, parser.py, managers/

### Fix Type 7: Add Type Narrowing
**Pattern**: `union_var.method()` needs `isinstance()` check
**Count**: ~10 instances
**Difficulty**: Medium (5-10 min each)

```python
# Before
hierarchy.append(item)

# After
if isinstance(hierarchy, list):
    hierarchy.append(item)
```

**Files**: managers/sheet.py, symbols/resolver.py

## Mypy Configuration Explained

### `disallow_untyped_defs = true`
All function definitions must have return types and parameter types.

**Impact**: Most errors come from this rule (~173 errors)

### `disallow_incomplete_defs = true`
All function parameters must have type annotations.

**Impact**: Requires parameter types, not just return types

### `no_implicit_optional = true`
Parameters with `None` default must be marked `Optional` or use `Type | None`.

**Impact**: ~31 errors for missing Optional

### `check_untyped_defs = true`
Functions calling untyped functions are reported as errors.

**Impact**: Cascading errors if core functions lack types

## Recommended Fix Order

### Phase 1: Quick Wins (1 day)
1. `core/config.py` - 1 error, super quick
2. `core/types.py` - 18 errors, mostly `__post_init__` → `-> None`
3. Fix implicit Optional defaults in 4 files

**Expected**: Reduce to ~350 errors

### Phase 2: Low-Hanging Fruit (2-3 days)
1. Fix all Enum type mismatches (symbols/validators.py)
2. Fix simple return type annotations
3. Fix variable type annotations in wire_routing.py

**Expected**: Reduce to ~250 errors

### Phase 3: Medium Complexity (1 week)
1. `utils/validation.py` - blocking file
2. `core/managers/validation.py` - 34 errors
3. `core/components.py` - 25 errors

**Expected**: Reduce to ~100 errors

### Phase 4: Complex Files (1-2 weeks)
1. `core/parser.py` - 59 errors, most complex
2. `core/schematic.py` - 29 errors
3. `symbols/validators.py` - 27 errors (if not done in Phase 2)

**Expected**: Reduce to 0 errors

## Mypy Strict Mode Features

This project enforces 11 strict type checking rules:

```
✅ warn_return_any          - Flag Any returns
✅ warn_unused_configs      - Flag unused config
✅ disallow_untyped_defs    - Require types on all functions
✅ disallow_incomplete_defs - Require all parameter types
✅ check_untyped_defs       - Check untyped function calls
✅ disallow_untyped_decorators - Type decorators
✅ no_implicit_optional     - No implicit Optional
✅ warn_redundant_casts     - Flag unnecessary casts
✅ warn_unused_ignores      - Flag stale # type: ignore
✅ warn_no_return           - Flag missing returns
✅ warn_unreachable         - Flag dead code
✅ strict_equality          - Strict equality checks
```

This is **professional-grade** strictness!

## Testing After Fixes

```bash
# Verify no mypy errors
uv run mypy kicad_sch_api/

# Run tests to ensure functionality
uv run pytest tests/ -v

# Run format preservation tests (critical)
uv run pytest tests/test_format_preservation.py -v
uv run pytest tests/reference_tests/ -v

# Run code quality checks
uv run black kicad_sch_api/ tests/ && \
uv run isort kicad_sch_api/ tests/ && \
uv run flake8 kicad_sch_api/ tests/
```

## Type Annotation Examples

### Function Return Type
```python
def get_component(ref: str) -> Component | None:
    """Return component or None if not found."""
    return self.components.get(ref)
```

### Multiple Parameter Types
```python
def add_wire(
    self, 
    start: Point, 
    end: Point, 
    wire_type: WireType = WireType.WIRE
) -> Wire:
    """Add a wire to the schematic."""
    return Wire(uuid=str(uuid4()), points=[start, end], wire_type=wire_type)
```

### Collection Types
```python
def filter_components(
    self,
    criteria: dict[str, Any]
) -> list[Component]:
    """Filter components by criteria."""
    return [c for c in self.components if self._matches(c, criteria)]
```

### Optional Types
```python
from typing import Optional

def get_property(
    self,
    name: str,
    default: str | None = None
) -> Optional[str]:
    """Get component property."""
    return self.properties.get(name, default)
```

### Union Types
```python
def process_position(
    self,
    pos: Point | tuple[float, float]
) -> Point:
    """Accept Point or tuple."""
    if isinstance(pos, Point):
        return pos
    return Point(pos[0], pos[1])
```

### Callback Types
```python
from typing import Callable

def apply_transform(
    self,
    transform: Callable[[Component], Component]
) -> list[Component]:
    """Apply transformation function to all components."""
    return [transform(c) for c in self.components]
```

## Common Mistakes to Avoid

### Mistake 1: Using `Any` Excessively
```python
# ❌ Wrong - defeats type checking
def parse(self, data: Any) -> Any:
    return data

# ✅ Right - specific types
def parse(self, data: dict[str, Any]) -> SchematicSymbol:
    return SchematicSymbol(...)
```

### Mistake 2: Forgetting `Optional`
```python
# ❌ Wrong - violates no_implicit_optional
def find(self, name: str = None) -> Component:
    pass

# ✅ Right
def find(self, name: str | None = None) -> Component | None:
    pass
```

### Mistake 3: Not Narrowing Union Types
```python
# ❌ Wrong - might not be a list
items.append(value)

# ✅ Right - check type first
if isinstance(items, list):
    items.append(value)
```

### Mistake 4: Casting Instead of Typing
```python
# ❌ Wrong - hides the problem
def format(...) -> str:
    return cast(str, sexpdata.dumps(value))

# ✅ Right - handle the Any properly
def format(...) -> str:
    result: Any = sexpdata.dumps(value)
    if isinstance(result, str):
        return result
    return str(result)
```

## Key Files to Watch

### Foundation Files (Type first, then other work)
- `core/types.py` - Core data types
- `utils/validation.py` - Validation system
- `core/config.py` - Configuration

### Core Infrastructure Files (Can build on foundation)
- `core/parser.py` - S-expression parsing
- `core/schematic.py` - Main Schematic class
- `core/managers/validation.py` - Validation manager

### Dependent Files (Fix after core)
- `core/components.py` - Component management
- `symbols/validators.py` - Symbol validation
- `library/cache.py` - Symbol caching

## Running Mypy with Options

```bash
# Full strict check
uv run mypy kicad_sch_api/

# Check single file
uv run mypy kicad_sch_api/core/types.py

# Show detailed errors
uv run mypy kicad_sch_api/ --pretty

# Count errors
uv run mypy kicad_sch_api/ 2>&1 | grep "error:" | wc -l

# Show only specific error type
uv run mypy kicad_sch_api/ 2>&1 | grep "no-untyped-def"

# Get summary
uv run mypy kicad_sch_api/ --no-pretty 2>&1 | tail -1
```

## Resources

- **Python Typing Docs**: https://docs.python.org/3/library/typing.html
- **Mypy Docs**: https://mypy.readthedocs.io/
- **PEP 484**: Type Hints https://www.python.org/dev/peps/pep-0484/
- **PEP 591**: Read-only properties https://www.python.org/dev/peps/pep-0591/

