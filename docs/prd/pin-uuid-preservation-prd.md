# PRD: Pin UUID Preservation During Round-Trip Load/Save

## Overview
Pin UUIDs are being dropped during schematic parsing and new UUIDs are generated during save operations. This breaks format preservation guarantees and causes unnecessary file diffs when loading and immediately saving a schematic without modifications.

**Problem**: When a schematic is loaded and saved with no changes, pin UUIDs change from their original values to newly generated UUIDs.

**Root Cause**:
- Parser (`symbol_parser.py:_parse_symbol()`) does not extract pin UUIDs from S-expressions
- Formatter (`symbol_parser.py:_symbol_to_sexp()` line 296) generates new UUIDs instead of preserving originals
- `SchematicSymbol` dataclass has no field to store pin UUID mappings

## Success Criteria (Measurable)
- [x] Pin UUIDs extracted during parsing and stored in component data
- [x] Pin UUIDs preserved during save operation (no new UUID generation)
- [x] Round-trip test passes: load → save → compare shows identical pin UUIDs
- [x] All existing tests continue to pass
- [x] Format preservation validated against reference schematics

## Functional Requirements
1. Extract pin UUIDs from S-expression `(pin "1" (uuid "..."))` during parsing
2. Store pin UUIDs in `SchematicSymbol` dataclass with pin number mapping
3. Emit stored pin UUIDs during save operation instead of generating new ones
4. Handle edge case: newly added components (no stored UUIDs) generate new UUIDs as before
5. Handle edge case: components with some pins having UUIDs and some missing (mixed state)

## KiCAD Format Specifications
- **S-expression structure**:
  ```
  (pin "1" (uuid "df660b58-5cdf-473e-8c0a-859cae977374"))
  (pin "2" (uuid "ff5e718a-93af-455d-84a2-eecf78f3f816"))
  ```
- **KiCAD version compatibility**: 7.0 and 8.0
- **Format preservation**: Byte-perfect match for pin UUID sections
- **Element hierarchy**: Pin entries appear after properties and before instances section in symbol definition

## Technical Constraints
- Exact format preservation required - pin UUIDs must match byte-for-byte
- Maintain backward compatibility with existing API (no breaking changes)
- Components created programmatically should still generate UUIDs automatically
- Pin UUIDs are immutable per component instance (changing reference should NOT change pin UUIDs)

## Reference Schematic Requirements
- Manual schematic contains: Single resistor with 2 pins, each with UUID
- Expected S-expression format: Standard KiCAD pin format with nested uuid
- Validation method: Byte-perfect diff comparison after round-trip load/save

## Edge Cases
1. **Newly added component**: No stored pin UUIDs → Generate new UUIDs (existing behavior)
2. **Mixed state**: Some pins have UUIDs, some don't → Generate UUIDs only for missing pins
3. **Pin count mismatch**: Component modified to have different pins → Preserve existing, generate for new
4. **Empty schematic**: No components → No pins to process (no-op)

## Impact Analysis
- **Parser changes**:
  - `symbol_parser.py:_parse_symbol()` - Add pin UUID extraction logic
  - Parse `(pin ...)` S-expressions to extract number and UUID pairs
- **Formatter changes**:
  - `symbol_parser.py:_symbol_to_sexp()` line 294-299 - Use stored UUIDs instead of generating new
  - Check for stored UUID before calling `uuid.uuid4()`
- **Type definitions**:
  - `kicad_sch_api/core/types.py:SchematicSymbol` - Add `pin_uuids: Dict[str, str]` field to store pin number → UUID mapping
- **MCP tools affected**: None - pin UUIDs are internal implementation detail

## Out of Scope
- Changing PIN number or pin structure (only preserving UUIDs)
- Pin position calculation or transformation
- Symbol library pin definitions (only schematic-level pin instances)
- Hierarchical sheet pin UUIDs (different element type, separate issue)

## Acceptance Criteria
- [x] Parser extracts pin UUIDs from reference schematic correctly
- [x] Pin UUIDs stored in `SchematicSymbol.pin_uuids` dictionary
- [x] Formatter emits stored pin UUIDs instead of generating new ones
- [x] Round-trip test: `rotated_resistor_0deg` reference loads and saves with identical pin UUIDs
- [x] All tests pass (unit, integration, reference)
- [x] Format preservation validated against KiCAD reference
- [x] Newly created components still auto-generate pin UUIDs
- [x] No breaking changes to public API
