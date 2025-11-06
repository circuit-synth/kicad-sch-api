# Migration Plan: IndexedCollection Refactoring

**Goal:** Complete migration from core collections (BaseCollection) to modern collections (IndexedCollection)
**Status:** Investigation Complete - Ready for Implementation
**Estimated Time:** 6-8 hours
**Risk Level:** Medium (requires careful testing)

---

## 📊 Current State Analysis

### Modern Collections (READY) ✅
Already implemented in `kicad_sch_api/collections/`:
- ✅ `ComponentCollection` - Full implementation with reference/lib_id/value indexes
- ✅ `WireCollection` - Full implementation with endpoint/type indexes
- ✅ `JunctionCollection` - Full implementation with position index
- ✅ `LabelCollection` - Full implementation with text/position/type indexes
- ✅ `IndexedCollection` (base) - Solid abstract base class

**Status:** These are well-designed, tested, but UNUSED in production

### Core Collections (CURRENTLY ACTIVE) ⚠️
Currently used in `kicad_sch_api/core/`:
- 🔴 `components.py` (892 lines) - Will be replaced
- 🔴 `wires.py` (207 lines) - Will be replaced
- 🔴 `junctions.py` (156 lines) - Will be replaced
- 🔴 `labels.py` (241 lines) - Will be replaced
- 🟡 `texts.py` (252 lines) - Needs modern version created
- 🟡 `no_connects.py` (240 lines) - Needs modern version created
- 🟡 `nets.py` (253 lines) - Needs modern version created
- 🔴 `collections/base.py` (249 lines) - Will be deleted

**Status:** Active but will be deprecated

### Dependencies
Files that import collections:
1. `kicad_sch_api/core/schematic.py` - Imports all 7 collections
2. `kicad_sch_api/core/__init__.py` - Exports Component, ComponentCollection
3. `kicad_sch_api/core/managers/wire.py` - Uses WireCollection type hint
4. Tests - Various test files import collections

---

## 🎯 Migration Strategy

### Phase 1: Create Missing Modern Collections (3 hours)

Create modern IndexedCollection-based versions for the 3 missing collections:

#### 1.1 Create `kicad_sch_api/collections/texts.py`

```python
"""Text collection with specialized indexing."""

import logging
import uuid as uuid_module
from typing import Dict, List, Optional, Tuple, Union

from ..core.types import Point, Text  # Assuming Text type exists
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class TextCollection(IndexedCollection[Text]):
    """
    Text collection with content indexing.

    Extends IndexedCollection with text-specific features:
    - Content indexing for fast text search
    - Position-based queries
    """

    def __init__(self, texts: Optional[List[Text]] = None):
        """Initialize text collection."""
        self._content_index: Dict[str, List[Text]] = {}
        super().__init__(texts)

    # Abstract method implementations
    def _get_item_uuid(self, item: Text) -> str:
        """Extract UUID from text."""
        return item.uuid

    def _create_item(self, **kwargs) -> Text:
        """Create new text (use add() instead)."""
        raise NotImplementedError("Use add() method instead")

    def _build_additional_indexes(self) -> None:
        """Build text-specific indexes."""
        self._content_index.clear()

        for text in self._items:
            content = text.text.lower()  # Case-insensitive index
            if content not in self._content_index:
                self._content_index[content] = []
            self._content_index[content].append(text)

    # Text-specific methods
    def add(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        rotation: float = 0.0,
        size: float = 1.27,
        exclude_from_sim: bool = False,
        text_uuid: Optional[str] = None,
    ) -> Text:
        """Add text to collection."""
        # Implementation similar to core version
        # ... (copy from core/texts.py and adapt)

    def find_by_content(self, content: str, exact: bool = True) -> List[Text]:
        """Find texts by content."""
        # Implementation
        pass
```

**Time:** 1.5 hours (includes testing)

#### 1.2 Create `kicad_sch_api/collections/no_connects.py`

Similar pattern to TextCollection but simpler (position-only index).

**Time:** 1 hour

#### 1.3 Create `kicad_sch_api/collections/nets.py`

Similar pattern with name index.

**Time:** 30 minutes

---

### Phase 2: Update Imports (30 minutes)

#### 2.1 Update `kicad_sch_api/core/schematic.py`

**Before:**
```python
from .components import ComponentCollection
from .junctions import JunctionCollection
from .labels import LabelCollection
from .nets import NetCollection
from .no_connects import NoConnectCollection
from .texts import TextCollection
from .wires import WireCollection
```

**After:**
```python
from ..collections.components import ComponentCollection
from ..collections.junctions import JunctionCollection
from ..collections.labels import LabelCollection
from ..collections.nets import NetCollection
from ..collections.no_connects import NoConnectCollection
from ..collections.texts import TextCollection
from ..collections.wires import WireCollection
```

#### 2.2 Update `kicad_sch_api/core/__init__.py`

**Before:**
```python
from .components import Component, ComponentCollection
```

**After:**
```python
from ..collections.components import Component, ComponentCollection
```

#### 2.3 Update `kicad_sch_api/core/managers/wire.py`

**Before:**
```python
from ..wires import WireCollection
```

**After:**
```python
from ...collections.wires import WireCollection
```

---

### Phase 3: Verify Component Wrapper Compatibility (1 hour)

The `Component` wrapper class exists in BOTH implementations. Need to verify:

1. **Check if Component is identical** in both versions
2. **Identify any differences** in the wrapper API
3. **Ensure tests pass** with modern Component

**Investigation needed:**
```bash
# Compare Component classes
diff kicad_sch_api/core/components.py kicad_sch_api/collections/components.py
```

**Key differences found:**
- Core has 892 lines vs modern 557 lines
- Modern might be missing some methods (need verification)
- Core has `add_ic()` method for multi-unit components
- Need to ensure modern has ALL features from core

**Action:** If modern Component is incomplete, copy missing methods from core version.

---

### Phase 4: Run Test Suite (2 hours)

#### 4.1 Run existing tests
```bash
uv run pytest tests/ -v
```

**Expected failures:**
- Tests that import from `kicad_sch_api.core.components`
- Tests that depend on BaseCollection behavior
- Format preservation tests (should pass if migration is correct)

#### 4.2 Fix failing tests

Common issues to fix:
1. **Import updates** - Change `from kicad_sch_api.core import Component` → `from kicad_sch_api.collections import Component`
2. **Collection behavior differences** - IndexedCollection has lazy indexing, BaseCollection rebuilds immediately
3. **Method signature changes** - Verify all method calls still work

#### 4.3 Run specific test categories
```bash
# Core functionality
uv run pytest tests/test_component_removal.py -v
uv run pytest tests/test_wire_operations.py -v

# Format preservation (CRITICAL)
uv run pytest tests/reference_tests/ -v

# Collection-specific
uv run pytest tests/unit/collections/ -v
```

---

### Phase 5: Delete Old Files (15 minutes)

Once ALL tests pass, delete old core collection files:

```bash
# Backup first (just in case)
mkdir -p backup/core_collections_backup
cp kicad_sch_api/core/{components,wires,labels,junctions,texts,no_connects,nets}.py backup/core_collections_backup/
cp kicad_sch_api/core/collections/base.py backup/core_collections_backup/

# Delete old files
rm kicad_sch_api/core/components.py
rm kicad_sch_api/core/wires.py
rm kicad_sch_api/core/labels.py
rm kicad_sch_api/core/junctions.py
rm kicad_sch_api/core/texts.py
rm kicad_sch_api/core/no_connects.py
rm kicad_sch_api/core/nets.py
rm kicad_sch_api/core/collections/base.py
rmdir kicad_sch_api/core/collections/  # If empty

# Update __init__.py files
```

---

### Phase 6: Update Public API Exports (30 minutes)

#### 6.1 Update `kicad_sch_api/__init__.py`

Ensure collections are properly exported:

**Current:**
```python
from .core.components import Component, ComponentCollection
```

**Should be:**
```python
from .collections.components import Component, ComponentCollection
from .collections.wires import WireCollection
from .collections.labels import LabelCollection
# ... etc for all collections
```

**Or keep internal:**
```python
# Collections accessed via Schematic.components, not directly imported
# Only export Schematic and top-level convenience functions
```

**Decision needed:** Should users import collections directly?

---

### Phase 7: Update Documentation (1 hour)

#### 7.1 Update import statements in docs

Files to update:
- `README.md` - Update any example imports
- `docs/API_REFERENCE.md` - Update import paths
- `docs/GETTING_STARTED.md` - Update tutorial imports
- `docs/RECIPES.md` - Update recipe imports
- `examples/*.py` - Update all example files

**Find/Replace:**
```bash
# Find files with old imports
grep -r "from kicad_sch_api.core import" docs/ examples/

# Update to:
# from kicad_sch_api import Component  (if exported in __init__)
# or just remove imports if not needed
```

#### 7.2 Update architecture documentation

Update `docs/ARCHITECTURE.md` to reflect:
- Modern IndexedCollection architecture
- Removal of old BaseCollection
- Explanation of lazy index rebuilding

---

## 🔍 Key Differences: IndexedCollection vs BaseCollection

### BaseCollection (OLD)
```python
class BaseCollection(Generic[T]):
    # Uses HasUUID protocol with TypeVar bound
    # Rebuilds indexes immediately on every change
    # _add_item() is internal, subclasses define add()
    # Direct UUID access via item.uuid

    def __init__(self, items, collection_name):
        self._items = items or []
        self._uuid_index = {}
        self._rebuild_index()  # Immediate rebuild

    def remove(self, uuid: str) -> bool:
        # ...
        self._rebuild_index()  # Rebuild immediately
```

### IndexedCollection (NEW)
```python
class IndexedCollection(Generic[T], ABC):
    # Uses abstract methods for flexibility
    # Lazy index rebuilding (performance optimization)
    # Base class provides add() method
    # Subclass implements _get_item_uuid()

    def __init__(self, items):
        self._items = []
        self._dirty_indexes = False  # Lazy rebuild flag
        self._uuid_index = {}
        # ... add items

    def remove(self, identifier) -> bool:
        # ...
        self._mark_indexes_dirty()  # Lazy rebuild

    def _ensure_indexes_current(self):
        if self._dirty_indexes:
            self._rebuild_indexes()
```

**Key Benefits of IndexedCollection:**
1. **Performance:** Lazy index rebuilding (only rebuild when needed)
2. **Flexibility:** Abstract methods allow different UUID extraction strategies
3. **Cleaner API:** Standardized `add()` in base class
4. **Better typing:** Full generic support with `Generic[T]`
5. **Automatic indexing:** Subclasses just implement 3 abstract methods

---

## ⚠️ Risk Areas

### HIGH RISK
1. **Format Preservation** - MUST verify schematic output is byte-identical
   - Run all `tests/reference_tests/`
   - Compare saved schematics byte-by-byte

2. **Component Wrapper API** - If modern Component is missing methods
   - Users' code will break
   - Need to ensure 100% API compatibility

### MEDIUM RISK
3. **Test Failures** - Expect 10-20 tests to need updates
   - Mostly import changes
   - Some collection behavior differences

4. **Manager Integration** - WireManager, etc. use collections
   - Type hints need updating
   - Collection method calls need verification

### LOW RISK
5. **Documentation** - Just find/replace work
6. **Performance** - IndexedCollection should be faster (lazy indexing)

---

## 📝 Verification Checklist

After migration, verify:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Format preservation tests pass (`pytest tests/reference_tests/ -v`)
- [ ] Create → Save → Load → Save round-trip is byte-identical
- [ ] All examples run without errors (`python examples/*.py`)
- [ ] README examples work
- [ ] API documentation examples work
- [ ] No old imports remain (`grep -r "from.*\.core\.(components|wires)" .`)
- [ ] Performance is same or better (run benchmarks if available)

---

## 🚀 Execution Plan

### Option A: All-at-once (6-8 hours straight)
1. Create 3 missing collections (3 hours)
2. Update all imports (30 min)
3. Run tests, fix failures (2 hours)
4. Delete old files (15 min)
5. Update docs (1 hour)
6. Final verification (1 hour)

**Pros:** Fast, focused, done in one session
**Cons:** Risky, all-or-nothing, hard to roll back

### Option B: Incremental (3-4 sessions)
**Session 1 (2 hours):** Create 3 missing collections, write unit tests
**Session 2 (2 hours):** Update imports, run test suite
**Session 3 (2 hours):** Fix test failures, verify format preservation
**Session 4 (2 hours):** Delete old files, update docs, final verification

**Pros:** Safer, can roll back at any point, easier to debug
**Cons:** Slower, need to maintain both systems temporarily

---

## 💡 Recommendation

I recommend **Option B (Incremental)** with these steps:

### TODAY: Session 1 (2 hours)
1. Create `collections/texts.py` (1 hour)
2. Create `collections/no_connects.py` (30 min)
3. Create `collections/nets.py` (30 min)
4. Write unit tests for each (included in above times)

### TOMORROW: Session 2 (2 hours)
1. Update Schematic imports (15 min)
2. Update manager imports (15 min)
3. Update `__init__.py` exports (15 min)
4. Run full test suite (15 min)
5. Start fixing test failures (1 hour)

### DAY 3: Session 3 (2 hours)
1. Finish fixing test failures (1 hour)
2. Run format preservation tests (30 min)
3. Verify byte-identical output (30 min)

### DAY 4: Session 4 (2 hours)
1. Delete old core collection files (15 min)
2. Update documentation (1 hour)
3. Run examples (15 min)
4. Final verification (30 min)
5. Commit and push

---

## 🎯 Success Criteria

Migration is complete when:
1. ✅ All 3 missing collections created and tested
2. ✅ Zero test failures
3. ✅ Format preservation verified (byte-identical output)
4. ✅ Old files deleted
5. ✅ Documentation updated
6. ✅ Examples run successfully
7. ✅ No imports from old locations remain

---

## 🔙 Rollback Plan

If something goes wrong:

1. **Git revert** - Just `git reset --hard` to previous commit
2. **Backup restoration** - Restore files from `backup/core_collections_backup/`
3. **Incremental rollback** - If using Option B, can stop at any session

**Safety:** Create a git branch for this work:
```bash
git checkout -b refactor/migrate-to-indexed-collection
# Do all work here
# Only merge to main after full verification
```

---

**Ready to proceed?** Let me know if you want to:
1. Start with creating the 3 missing collections
2. Do a more detailed analysis first
3. Try a different approach
