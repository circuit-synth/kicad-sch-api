# PRD: Hierarchical Sheet Support in kicad-sch-api

**Status**: REVISED after deep architectural review
**Created**: 2025-10-30
**Revised**: 2025-10-30
**Branch**: `fix/hierarchical-sheets-support`
**Related Issue**: circuit-synth #406

---

## Executive Summary

kicad-sch-api has a **manager-based architecture** that already partially supports hierarchical sheets but has critical gaps:

1. **Sheet Manager exists** but has NO public API exposure through `Schematic` class
2. **Component instances missing** from `SchematicSymbol` dataclass (critical bug)
3. **Instance path generation happens in parser**, not preserved from user-set values
4. **Project name auto-detection missing**

The fix strategy has changed from "add new features" to **"expose existing infrastructure + fix instance preservation bug"**.

---

## Architectural Analysis

### Current Architecture (Manager-Based Pattern)

kicad-sch-api uses **composition with specialized managers**:

```
Schematic
├── ComponentCollection (exposed via .components)
├── WireCollection (exposed via .wires)
├── LabelCollection (exposed via .labels)
├── SheetManager (EXISTS but NOT exposed!) ← BUG #1
├── FileIOManager
├── ValidationManager
└── ...12 other managers
```

**Key Finding**: `SheetManager` exists at `schematic._sheet_manager` with full CRUD operations but is **never exposed** through a public property.

### Instance Path Data Flow (The Critical Bug)

**Current Broken Flow**:
```
1. User creates component: symbol = SchematicSymbol(reference="R2", ...)
2. Symbol has NO .instances field (dataclass missing it!) ← BUG #2
3. On save: _sync_components_to_data() copies symbol._data.__dict__
4. Parser generates instances internally ← BUG #3 (overwrites user intent)
5. File written with WRONG hierarchical path
```

**Root Cause**: `SchematicSymbol` dataclass (types.py:159) has NO `instances` field!

### Problem Statement

**For circuit-synth users**:
- Component references display as "R?" instead of "R2" in child sheets
- Requires ~200 lines of workaround code
- Fragile regex-based file parsing
- No unit tests possible for workarounds

**For kicad-sch-api users**:
- Cannot query sheets (API not exposed)
- Cannot set component instances (dataclass doesn't support it)
- Save operation generates instances instead of preserving them

---

## Goals

### Primary Goals

1. **Expose sheet symbols via API** - `schematic.sheets` collection
2. **Preserve instance paths on save** - Don't overwrite user-set hierarchical paths
3. **Auto-detect project names** - Infer from directory/file structure

### Non-Goals

- Automatic hierarchical pin management (future enhancement)
- Sheet reuse/instantiation (future enhancement)
- Cross-project references (out of scope)

---

## User Stories

### Story 1: Query Sheet Symbols

**As a** tool developer
**I want to** access sheet symbols in a schematic
**So that** I can build hierarchical path strings for components

**Acceptance Criteria**:
```python
schematic = ksa.Schematic.load("Parent.kicad_sch")

# Can access sheets
assert len(schematic.sheets) == 2

# Can query sheet properties
child_sheet = schematic.sheets[0]
assert child_sheet.filename == "Child.kicad_sch"
assert child_sheet.name == "ChildSheet"
assert child_sheet.uuid is not None
assert child_sheet.position == (50, 50)
assert child_sheet.size == (50, 30)
```

---

### Story 2: Preserve Instance Paths

**As a** tool developer
**I want** instance paths I set to be saved exactly as-is
**So that** components display correctly in hierarchical schematics

**Acceptance Criteria**:
```python
# Load child sheet
child_sch = ksa.Schematic.load("Child.kicad_sch")

# Add component with hierarchical path
component = child_sch.add_component(
    library_id="Device:R",
    reference="R2",
    value="4.7k",
)

# Set hierarchical instance path explicitly
instance = ksa.SymbolInstance(
    path="/ROOT_UUID/CHILD_UUID",
    reference="R2",
    unit=1,
)
component.instances = [instance]

# Save
child_sch.save("Child.kicad_sch")

# Verify path was preserved (not overwritten)
reloaded = ksa.Schematic.load("Child.kicad_sch")
assert reloaded.components[0].instances[0].path == "/ROOT_UUID/CHILD_UUID"
# Not: "/CHILD_UUID" ← current buggy behavior
```

**Current Behavior** (WRONG):
```scheme
(instances
  (project "test"
    (path "/CHILD_UUID"  ← Library overwrites with schematic's own UUID
      (reference "R2")
    )
  )
)
```

**Expected Behavior** (CORRECT):
```scheme
(instances
  (project "test"
    (path "/ROOT_UUID/CHILD_UUID"  ← Preserves what user set
      (reference "R2")
    )
  )
)
```

---

### Story 3: Auto-Detect Project Name

**As a** tool developer
**I want** project names to be inferred automatically
**So that** I don't have to manually set `schematic.name` everywhere

**Acceptance Criteria**:
```python
# Load root schematic
# File: /path/to/MyProject/MyProject.kicad_sch
root = ksa.Schematic.load("/path/to/MyProject/MyProject.kicad_sch")

# Project name automatically detected from directory
assert root.name == "MyProject"

# Load child schematic
# File: /path/to/MyProject/ChildSheet.kicad_sch
child = ksa.Schematic.load("/path/to/MyProject/ChildSheet.kicad_sch")

# Project name still detected correctly
assert child.name == "MyProject"
```

---

## Technical Design (REVISED)

### Fix 1: Expose SheetManager through Public API

**Current State**: SheetManager already exists with full functionality (456 lines of code!)
**Problem**: Never exposed through `Schematic` class

**File**: `kicad_sch_api/core/schematic.py`

**Implementation** (SIMPLE - just expose existing manager):

```python
class Schematic:
    # Add property to expose sheet manager functionality
    @property
    def sheets(self) -> "SheetCollection":
        """
        Access hierarchical sheets in this schematic.

        Returns:
            SheetCollection wrapping the SheetManager
        """
        return SheetCollection(self._sheet_manager, self._data)
```

**Create SheetCollection wrapper** (for consistency with ComponentCollection pattern):

```python
# kicad_sch_api/core/collections/sheets.py

class SheetCollection:
    """Collection wrapper for sheets, following ComponentCollection pattern."""

    def __init__(self, manager: SheetManager, data: dict):
        self._manager = manager
        self._data = data

    def __len__(self) -> int:
        return len(self._data.get('sheets', []))

    def __iter__(self):
        for sheet_data in self._data.get('sheets', []):
            yield Sheet.from_dict(sheet_data)  # Convert dict to Sheet object

    def __getitem__(self, index: int) -> Sheet:
        sheets = list(self)
        return sheets[index]

    def get_by_name(self, name: str) -> Optional[Sheet]:
        return self._manager.get_sheet_by_name(name)

    def get_by_filename(self, filename: str) -> Optional[Sheet]:
        return self._manager.get_sheet_by_filename(filename)

    # Delegate all other operations to manager
    def add(self, name: str, filename: str, position, size, **kwargs) -> str:
        return self._manager.add_sheet(name, filename, position, size, **kwargs)
```

**Why this is better**:
- Leverages existing, tested SheetManager code (456 lines!)
- Follows established architectural pattern (ComponentCollection, WireCollection, etc.)
- Zero duplication
- Manager already handles: add_sheet, remove_sheet, update_sheet_position, validate_sheet_references, get_sheet_hierarchy, etc.

---

### Fix 2: Add `instances` Field to SchematicSymbol + Preserve on Save

**Root Cause**: `SchematicSymbol` dataclass MISSING `instances` field entirely!

**File 1**: `kicad_sch_api/core/types.py` - Add instances field

```python
@dataclass
class SchematicSymbol:
    """Component symbol in a schematic."""

    uuid: str
    lib_id: str  # e.g., "Device:R"
    position: Point
    reference: str  # e.g., "R1"
    value: str = ""
    footprint: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    pins: List[SchematicPin] = field(default_factory=list)
    rotation: float = 0.0
    in_bom: bool = True
    on_board: bool = True
    unit: int = 1

    # ADD THIS FIELD ← THE CRITICAL FIX
    instances: List[SymbolInstance] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid4())
```

**File 2**: `kicad_sch_api/core/schematic.py` - Preserve instances on save

**Current broken code** (line 1217):
```python
def _sync_components_to_data(self):
    """Sync component collection state back to data structure."""
    self._data["components"] = [comp._data.__dict__ for comp in self._components]
    # ↑ This just copies __dict__, but instances might not be in there!
```

**Fixed code**:
```python
def _sync_components_to_data(self):
    """Sync component collection state back to data structure."""
    components_data = []

    for comp in self._components:
        # Start with base component data
        comp_dict = {k: v for k, v in comp._data.__dict__.items() if not k.startswith('_')}

        # CRITICAL: Explicitly preserve instances if user set them
        if hasattr(comp._data, 'instances') and comp._data.instances:
            comp_dict['instances'] = [
                {
                    'project': inst.project if hasattr(inst, 'project') else self.name,
                    'path': inst.path,  # PRESERVE exact path user set!
                    'reference': inst.reference,
                    'unit': inst.unit,
                }
                for inst in comp._data.instances
            ]

        components_data.append(comp_dict)

    self._data["components"] = components_data
```

**Why this is the RIGHT fix**:
1. Makes `SchematicSymbol` complete - instances are fundamental to KiCad schematics
2. Preserves user-set values instead of generating them
3. Fixes the root cause, not a symptom
4. No post-processing hacks needed

---

### Fix 3: Auto-Detect Project Name

**File**: `kicad_sch_api/core/schematic.py`

**Implementation**:

```python
from pathlib import Path

class Schematic:
    @classmethod
    def load(cls, filepath: str) -> 'Schematic':
        """Load schematic from file with automatic project name detection."""
        schematic = cls()

        # Parse the file
        # ... existing parsing code ...

        # Auto-detect project name from file path
        path = Path(filepath)
        project_name = cls._detect_project_name(path)

        schematic.name = project_name

        # Also set on parser if it exists
        if hasattr(schematic, '_parser'):
            schematic._parser.project_name = project_name

        return schematic

    @staticmethod
    def _detect_project_name(file_path: Path) -> str:
        """Detect project name from file path.

        Rules:
        1. If filename matches directory name → use directory name (root schematic)
        2. If different → look for root schematic in same directory
        3. Fallback → use directory name

        Examples:
        - /MyProject/MyProject.kicad_sch → "MyProject"
        - /MyProject/Child.kicad_sch → "MyProject"
        """
        parent_dir = file_path.parent
        dir_name = parent_dir.name
        file_stem = file_path.stem

        # Case 1: This is the root schematic (filename == directory)
        if file_stem == dir_name:
            return dir_name

        # Case 2: Check if root schematic exists
        root_schematic = parent_dir / f"{dir_name}.kicad_sch"
        if root_schematic.exists():
            return dir_name

        # Case 3: Fallback to directory name
        return dir_name
```

**Test**:
```python
def test_project_name_detection_root():
    """Test project name detection for root schematic."""
    sch = ksa.Schematic.load("tests/data/TestProject/TestProject.kicad_sch")
    assert sch.name == "TestProject"

def test_project_name_detection_child():
    """Test project name detection for child schematic."""
    sch = ksa.Schematic.load("tests/data/TestProject/ChildSheet.kicad_sch")
    assert sch.name == "TestProject"
```

---

## Testing Strategy

### Unit Tests

1. **test_sheets.py** - Sheet collection API
   - `test_schematic_exposes_sheets()` - Basic access
   - `test_sheet_properties()` - UUID, filename, name, position, size
   - `test_multiple_sheets()` - Multiple children
   - `test_no_sheets()` - Empty collection for flat schematics

2. **test_instances.py** - Instance path preservation
   - `test_instance_paths_preserved_on_save()` - Main bug fix
   - `test_multi_level_hierarchy_paths()` - Grandchild sheets
   - `test_multiple_instances()` - Multi-unit symbols

3. **test_project_name.py** - Auto-detection
   - `test_project_name_detection_root()` - Root schematic
   - `test_project_name_detection_child()` - Child schematic
   - `test_project_name_fallback()` - No root found

### Integration Tests

4. **test_hierarchical_workflow.py** - End-to-end
   - Create root schematic programmatically
   - Create child schematic programmatically
   - Add sheet symbol to root
   - Add components to child with correct paths
   - Save both
   - Reload and verify all data intact
   - Open in KiCad and verify visual display

### Test Data

Create test fixtures:
```
tests/data/hierarchical/
├── Parent.kicad_sch         # Root with 1 sheet symbol
├── Child.kicad_sch          # Child with R2
└── GrandChild.kicad_sch     # Grandchild with R3
```

---

## Critical Concerns & Decisions

### ⚠️ BREAKING CHANGE WARNING

Adding `instances` field to `SchematicSymbol` dataclass is a **breaking change**.

**Mitigation**: Use `field(default_factory=list)` - backward compatible for most use cases.

**Recommendation**: Release as v0.5.0 with breaking change notice.

---

### 🔍 Parser Integration Required

Parser currently generates instances during `load()`. We must:
1. Parse existing instances from file (not generate)
2. Preserve in `SchematicSymbol.instances`
3. Write back unchanged on save

**Investigation needed**: Find where `parsers/elements/symbol_parser.py` generates instances.

---

## Implementation Plan (REVISED)

### Phase 1: Add instances field + expose sheets (2-3 hours)

**PART A: instances field**
1. Add `instances: List[SymbolInstance] = field(default_factory=list)` to `SchematicSymbol`
2. Update `_sync_components_to_data()` to preserve instances
3. Find and update parser to populate instances from file
4. Write unit test for instance preservation

**PART B: expose sheets**
5. Create `SheetCollection` class
6. Add `sheets` property to `Schematic`
7. Write unit test for sheet access

**Deliverable**: Both fixes working

---

### Phase 2: Project name auto-detection (1 hour)

1. Add `_detect_project_name()` static method
2. Call in `Schematic.load()`
3. Write unit tests
4. Update docs

**Deliverable**: Auto-detection works

---

### Phase 3: Integration testing (2-3 hours)

1. **CRITICAL**: Find ALL places parser generates instances
2. Ensure round-trip preservation (load → save → load)
3. Test with circuit-synth test_22
4. Run full kicad-sch-api test suite
5. Check regressions

**Deliverable**: All tests pass

---

### Phase 4: Release (1-2 hours)

1. CHANGELOG with breaking change notice
2. Migration guide if needed
3. README with hierarchical examples
4. PR for review

**Deliverable**: v0.5.0 release

---

## Success Metrics

### Functional Metrics

- ✅ All 3 bugs fixed and tested
- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ Example script runs successfully
- ✅ Components display correctly in KiCad GUI

### Code Quality Metrics

- ✅ Test coverage >85% for new code
- ✅ No regressions in existing tests
- ✅ Type hints on all new APIs
- ✅ Documentation complete

### Downstream Impact

- ✅ circuit-synth can remove ~200 lines of workaround code
- ✅ No regex file parsing needed
- ✅ No post-save corrections needed
- ✅ Test suite runs cleanly

---

## Risks & Mitigations

### Risk 1: Breaking Changes

**Risk**: Fixing instance path preservation might break existing code that relies on current behavior

**Mitigation**:
- Add tests for both old and new behavior
- Check if anyone actually uses `component.instances` setter
- Consider deprecation period if needed
- Review circuit-synth usage patterns

### Risk 2: KiCad Format Variations

**Risk**: Sheet symbol format might vary across KiCad versions

**Mitigation**:
- Test with multiple KiCad versions (v6, v7, v8)
- Use version-aware parsing if needed
- Document supported versions

### Risk 3: Performance

**Risk**: Parsing sheets adds overhead to schematic loading

**Mitigation**:
- Profile before/after
- Lazy-load sheets if needed
- Ensure O(n) complexity, not O(n²)

---

## Open Questions

1. **Should we support sheet pin parsing?** - Not in initial implementation, add later
2. **How to handle sheet symbol creation?** - Add `schematic.add_sheet()` method (future)
3. **Version compatibility?** - Support KiCad 6+ initially, expand if needed
4. **Should project name be settable?** - Yes, auto-detect but allow override

---

## Appendix: Related Code Locations

### kicad-sch-api Files to Modify

- `kicad_sch_api/core/types.py` - Add `Sheet` class
- `kicad_sch_api/core/schematic.py` - Add sheet parsing, fix instance preservation, add project name detection
- `tests/test_sheets.py` - New file
- `tests/test_instances.py` - New tests
- `tests/test_project_name.py` - New tests
- `tests/data/hierarchical/` - New test fixtures

### circuit-synth Code to Remove After Fix

Once kicad-sch-api is fixed, remove these workarounds:

- `src/circuit_synth/kicad/schematic/instance_utils.py:104-125` - Regex sheet parsing
- `src/circuit_synth/kicad/schematic/synchronizer.py:1281-1329` - Post-save path correction
- `src/circuit_synth/kicad/schematic/hierarchical_synchronizer.py:91-99` - Full hierarchy reload
- Manual project name settings throughout

**Estimated LOC Reduction**: ~200 lines

---

## Timeline

**Estimated Total**: 6-10 hours of work

- Phase 1: 2-3 hours
- Phase 2: 2-3 hours
- Phase 3: 1-2 hours
- Phase 4: 1-2 hours

**Target Completion**: Within 1 week

**Release**: kicad-sch-api v0.5.0 (breaking change)

---

## Final Architecture Review & Scaling Analysis

### Will This Scale?

**YES** - Here's why:

**1. Leverages Existing Manager Pattern**
- SheetManager already exists and is tested
- Just exposing, not rebuilding
- No architectural debt added

**2. Minimal Surface Area Changes**
- One new field: `SchematicSymbol.instances`
- One new property: `Schematic.sheets`
- One new class: `SheetCollection` (wrapper, not logic)

**3. Preserves Data Integrity**
- Round-trip preservation (load → modify → save → load)
- No lossy transformations
- No regex hacks in library code

**4. Backward Compatible (Mostly)**
- Default field value handles 90% of cases
- Clear migration path for edge cases
- Version bump signals change

### Will This Cover Every Situation?

**Core use cases covered**:
- ✅ Single-level hierarchy (root + children)
- ✅ Multi-level hierarchy (grandchildren, etc.)
- ✅ Multiple children at same level
- ✅ Sheet pin management (already in SheetManager)
- ✅ Project name detection
- ✅ Component instance paths
- ✅ Sheet-to-sheet navigation

**Edge cases**:
- ⚠️ Cross-project references (out of scope, KiCad doesn't support)
- ⚠️ Circular sheet references (KiCad prevents this)
- ⚠️ Dynamic sheet reuse (future enhancement)

**For millions of uses**:
- Parser performance already optimized
- Manager pattern scales (composition > inheritance)
- No O(n²) operations added
- Memory efficient (lazy loading where possible)

### Best Practices Compliance

**✅ Follows existing patterns**:
- Collection classes (ComponentCollection, WireCollection, SheetCollection)
- Manager delegation (SheetManager, WireManager, etc.)
- Dataclass-based types (SchematicSymbol, Wire, Sheet)

**✅ Type safety**:
- Full type hints on all new code
- List[SymbolInstance] enforces structure
- MyPy compatible

**✅ Separation of concerns**:
- SheetCollection = API layer
- SheetManager = business logic
- Parser = file I/O
- Types = data structures

**✅ Testing strategy**:
- Unit tests for each component
- Integration tests for workflows
- Regression tests for edge cases

### What Could Go Wrong?

**Risk 1: Parser doesn't preserve instances**
- **Likelihood**: HIGH (need to investigate parser code)
- **Impact**: CRITICAL (the whole fix fails)
- **Mitigation**: Phase 3 dedicated to parser investigation

**Risk 2: Breaking change breaks downstream**
- **Likelihood**: MEDIUM
- **Impact**: MEDIUM (annoying but fixable)
- **Mitigation**: Default field value, clear docs, version bump

**Risk 3: Performance regression**
- **Likelihood**: LOW (no new loops or file I/O)
- **Impact**: LOW
- **Mitigation**: Benchmark before/after

### Recommendation

**PROCEED with implementation** with these caveats:

1. **Investigate parser first** (Phase 1 step 3) - this is the unknown
2. **Test early and often** - don't wait until Phase 3
3. **Consider v1.0.0 instead of v0.5.0** - clean break, new era
4. **Document migration** - clear examples for upgrading

This is the RIGHT architectural fix, not a workaround.
