---
description: Core development workflow - from problem to PR for KiCAD schematic features
---

# /dev - Development Workflow for KiCAD Schematic API

**Purpose**: Complete development workflow from problem description to pull request, using KiCAD reference-driven development with comprehensive testing and format preservation validation.

**Use when**: Building features, fixing bugs, or adding functionality that requires systematic development with PRD, reference schematics, tests, and iterative implementation.

---

## Workflow Overview

```
/dev (end-to-end development)
  ├─ Phase 1: Generate PRD (research → ask questions → document)
  │   └─ STOP: User reviews PRD
  ├─ Phase 2: Create Reference Schematic (Interactive - agent creates, user refines)
  │   └─ STOP: User edits in KiCAD, says "done"
  ├─ Phase 3: Generate Tests (autonomous - no stop)
  ├─ Phase 4: Implementation (autonomous + communicative - shows progress)
  │   └─ STOP if stuck after 8 iterations
  ├─ Phase 4.5: Manual Validation (Interactive - agent guides, user inspects)
  │   └─ STOP: User validates in KiCAD
  └─ Phase 5: Cleanup & PR (autonomous - no stop)
```

**Time estimate**: 1-4 hours depending on complexity

---

## Reviewing and Fixing Existing PRs

**If you encounter an existing PR with failing CI**, follow these steps to fix it:

### Step 1: Checkout the PR branch
```bash
gh pr checkout {PR_NUMBER}
```

### Step 2: Fix formatting issues
```bash
# Format code
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/
```

### Step 3: Fix other CI failures
```bash
# Run tests to identify failures
uv run pytest tests/ -v

# Fix type errors
uv run mypy kicad_sch_api/

# Fix linting issues
uv run flake8 kicad_sch_api/ tests/
```

### Step 4: Commit and push fixes
```bash
git add -A
git commit -m "chore: Fix CI formatting and test failures

Apply black and isort formatting to pass CI checks.
Fix any test failures and type errors.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin {BRANCH_NAME}
```

### Step 5: Resolve merge conflicts (if needed)
```bash
# Fetch and merge main
git fetch origin main
git merge origin/main

# Resolve conflicts manually or use preferred versions:
# - Use theirs for files unrelated to the PR's purpose
# - Manually resolve conflicts in PR-specific changes

git add {resolved_files}
git commit -m "Merge branch 'main' into {branch_name}"
git push origin {BRANCH_NAME}
```

### Step 6: Merge the PR
```bash
# Squash merge (preferred for clean history)
gh pr merge {PR_NUMBER} --squash --delete-branch

# Or regular merge if history preservation needed
gh pr merge {PR_NUMBER} --merge --delete-branch
```

**Key Principle**: ALWAYS fix CI locally before pushing. Never leave a PR with failing checks.

---

## Usage

```bash
# Format preservation bug
/dev "Pin UUIDs not preserved during round-trip load/save"

# New element support
/dev "Add support for text box elements with borders and margins"
```

---

## Phase 1: Generate PRD

**Goal**: Create comprehensive Product Requirements Document

### Step 1.1: Research and Analyze (Silent)

**Before asking questions**, do research to understand context:

1. **Search codebase** for related functionality:
   - Use Grep/Glob to find similar features
   - Read relevant parser/formatter files
   - Check existing tests for patterns
   - Review related PRDs in `docs/prd/`

2. **Understand the problem domain**:
   - What KiCAD elements are involved?
   - What S-expression format is affected?
   - What existing code handles similar cases?
   - What reference schematics exist that might help?

3. **Identify knowledge gaps**:
   - What can't be determined from code alone?
   - What requires user preference/decision?
   - What scope clarification is needed?
   - What technical constraints are unclear?

**DO NOT present research findings to user** - use this to formulate smart questions.

### Step 1.2: Ask Clarifying Questions

**After research**, ask targeted questions to fill knowledge gaps:

**Question Guidelines**:
- **Maximum 5 questions** unless user explicitly requests more detail
- **Keep concise** - use bullet points, not paragraphs
- **Be specific** - reference code/files found during research
- **Offer options** when possible (makes answering easier)
- **Skip obvious** - if you can infer from code, don't ask
- **Focus on**: scope clarification, user preferences, architectural decisions, edge case handling

**Wait for user responses** before proceeding.

### Step 1.3: Generate PRD

**IMPORTANT - Writing Guidelines**: Follow `CLAUDE.md` - NO marketing language, engineer tone, specific technical claims only.

**PRD Structure** (save to `docs/prd/{feature-name}-prd.md`):
- Overview (what we're building - technical and specific)
- Success Criteria (measurable checkboxes)
- Functional Requirements (numbered list)
- KiCAD Format Specifications (S-expression structure, version compatibility, preservation requirements)
- Technical Constraints (backward compatibility, format preservation)
- Reference Schematic Requirements (what to create, expected format)
- Edge Cases (specific scenarios and handling)
- Impact Analysis (parser/formatter/type/MCP changes)
- Out of Scope
- Acceptance Criteria (includes "All tests pass", "Format preservation validated")

### Step 1.4: User Checkpoint

**Present PRD and ask**:
> I've created a PRD for this feature. Please review:
>
> [Show PRD]
>
> Does this accurately capture what we're building? Any missing requirements or concerns?

**Wait for user approval** before proceeding to Phase 2.

---

## Phase 2: Create Reference Schematic (Interactive)

**Goal**: Create KiCAD reference schematic that demonstrates the feature/behavior

This is a **critical phase** - the reference schematic becomes the source of truth for exact KiCAD format.

### Step 2.0: Trusted Actions Decision

**Decide who creates reference**:
- **Agent creates** (most common): Testing format preservation, new elements, API behavior. Agent can reliably use `add_component()`, `add_wire()`, `add_label()`, etc.
- **Human creates** (rare): Testing those APIs themselves, or when aesthetics matter.

### Step 2.1: Create Initial Schematic

**Agent creates schematic** with elements from PRD. **IMPORTANT: Keep references MINIMAL - one component per reference schematic whenever possible.** This makes debugging easier, tests clearer, and references more focused.

**Reference Schematic Guidelines:**
- **One component per schematic** - simpler is better
- **Minimal elements** - only what's needed to demonstrate the feature
- **Grid-aligned positions** (multiples of 1.27mm)
- **Generic positioning** like (100, 100) - functional > beautiful
- **Multiple references** - create separate schematics for different test cases rather than one complex schematic

If human should create: provide blank schematic instead.

**Tell user** what was created and open in KiCAD for optional refinement.

### Step 2.2: Open for User Editing

**Claude opens schematic**:
```bash
open /tmp/{feature_name}_working.kicad_sch
```

**Tell user**:
> I've created an initial schematic at `/tmp/{feature_name}_working.kicad_sch` and opened it in KiCAD.
>
> Please:
> 1. Review/adjust the schematic to demonstrate the feature
> 2. Add any missing elements (components, wires, labels, properties, pins)
> 3. Ensure positions are clean and layout is readable
> 4. **For format preservation bugs**: Make sure the element exists with all required fields
> 5. Save the schematic (Cmd+S / Ctrl+S)
> 6. Tell me "saved" or "done" when ready
>
> What I've included so far:
> {List components, wires, labels, etc. that were pre-created}

### Step 2.3: User Edits in KiCAD

**User performs manual editing**:
- Add/modify components, wires, labels, properties
- Adjust positioning for clarity
- Add edge cases or variations
- Ensure schematic demonstrates the feature being developed
- **Save changes** in KiCAD

**User signals completion**: "saved", "done", or similar

### Step 2.4: Claude Analyzes and Copies Reference

**Claude processes the saved schematic**:

1. **Read the user-saved schematic**:
   ```python
   sch = ksa.Schematic.load("/tmp/{feature_name}_working.kicad_sch")
   ```

2. **Analyze what user created**:
   ```python
   # Log what's in the schematic
   print(f"Components: {len(sch.components)}")
   print(f"Wires: {len(sch.wires)}")
   print(f"Labels: {len(sch.labels)}")
   # etc.
   ```

3. **Parse S-expression to understand exact format**:
   ```python
   # Read raw file to see exact S-expression structure
   with open("/tmp/{feature_name}_working.kicad_sch", 'r') as f:
       raw_content = f.read()

   # Identify the specific S-expression structure for the feature
   # This becomes the format we must replicate
   ```

4. **Determine reference location**:
   - Ask user: "Where should I save this reference? Suggestions: `tests/reference_kicad_projects/{feature_name}/` or `tests/reference_kicad_projects/{custom_name}/`?"
   - Or propose a name based on the feature

5. **Copy to reference location**:
   ```bash
   mkdir -p tests/reference_kicad_projects/{reference_name}
   cp /tmp/{feature_name}_working.kicad_sch tests/reference_kicad_projects/{reference_name}/test.kicad_sch
   ```

6. **Create README for reference**:
   ```markdown
   # Reference: {Feature Name}

   ## Purpose
   {What this reference schematic demonstrates}

   ## Contents
   - Components: {list}
   - Wires: {count}
   - Labels: {count}
   - {Other elements}

   ## Key S-expression Format
   ```
   {Show relevant S-expression snippet}
   ```

   ## Used For
   - Testing: {which tests use this}
   - Validation: {what format preservation this validates}
   - Training: {potential future ML/comparison use}

   ## Created
   Date: {date}
   Issue: #{issue_number}
   PRD: docs/prd/{feature-name}-prd.md
   ```

### Step 2.5: Reference Analysis Summary

**Analyze and summarize reference** (informational):
> ✅ Reference schematic created and saved to `tests/reference_kicad_projects/{reference_name}/`
>
> **Contents**:
> - {N} components
> - {M} wires
> - {K} labels
> - {Other elements}
>
> **Key Format Discovered**:
> ```
> {Show relevant S-expression snippet}
> ```
>
> This reference will be used to:
> 1. Understand exact KiCAD format requirements
> 2. Guide implementation to match byte-perfect output
> 3. Validate format preservation in tests
>
> Proceeding to test generation...

---

## Phase 3: Generate Tests

**Goal**: Create comprehensive test suite from PRD and reference schematic

### Step 3.1: Analyze Requirements and Reference

**Extract from PRD**:
- All functional requirements
- All acceptance criteria
- All edge cases
- Format preservation requirements

**Extract from Reference Schematic**:
- Exact S-expression format to replicate
- Element properties and structure
- Expected values and types

### Step 3.2: Generate Test Plan

**Create test files**:
- **Unit tests** (`tests/unit/test_{feature}.py`): Basic functionality, edge cases (empty/null values), round-trip preservation
- **Reference tests** (`tests/reference_tests/test_{feature}_reference.py`): Parse reference schematic, exact format preservation (load→save→compare), programmatic replication
- **Integration tests** (if needed): Connectivity analysis, MCP tools compatibility

**Use pytest markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.format` (CRITICAL for format preservation), `@pytest.mark.validation`

### Step 3.3: Verify Test Coverage

Map each test to PRD requirements. Ensure all functional requirements, edge cases, and acceptance criteria have corresponding tests.

### Step 3.4: Test Summary (Informational)

**Summarize test coverage** (informational - no approval needed):
> ✅ Test suite created with {X} tests:
>
> **Unit Tests** ({N} tests):
> - Basic functionality
> - Edge cases
> - Round-trip preservation
>
> **Reference Tests** ({M} tests):
> - Parse reference schematic
> - Exact format preservation
> - Programmatic replication
>
> **Integration Tests** ({K} tests, if applicable):
> - Connectivity integration
> - MCP tools integration
>
> **Requirement Coverage**:
> - [x] REQ-1: {requirement}
> - [x] REQ-2: {requirement}
> - All {N} requirements covered
>
> Proceeding to implementation...

---

## Phase 4: Implementation (Reference-Driven & Iterative)

**Goal**: Implement solution that passes all tests and preserves exact KiCAD format

### Step 4.1: Add Strategic Logging

**Add comprehensive debug logging** using Python's logging module:

**Parser logging** (`kicad_sch_api/parsers/elements/`):
```python
import logging
logger = logging.getLogger(__name__)

def _parse_element(self, item):
    """Parse element from S-expression."""
    logger.debug(f"Parsing {element_type}: {item}")

    # Parse fields
    for sub_item in item[1:]:
        element_type = str(sub_item[0])
        logger.debug(f"  Field: {element_type} = {sub_item[1:] if len(sub_item) > 1 else None}")

    # Log parsed result
    logger.debug(f"Parsed {element_type}: {result}")
    return result
```

**Formatter logging** (`kicad_sch_api/parsers/elements/`):
```python
def _element_to_sexp(self, element_data):
    """Convert element to S-expression."""
    logger.debug(f"Formatting {element_type}: {element_data}")

    # Build S-expression
    sexp = [Symbol(element_type)]

    # Log each added field
    for field_name, field_value in element_data.items():
        logger.debug(f"  Adding field: {field_name} = {field_value}")
        sexp.append(...)

    logger.debug(f"Generated S-expression: {sexp}")
    return sexp
```

**Data transformation logging**:
```python
# Type conversions
logger.debug(f"Converting position: tuple {pos} -> Point({pos.x}, {pos.y})")

# UUID handling
logger.debug(f"Preserving UUID: {uuid} for {element_type}")

# Format decisions
logger.debug(f"Using format: byte-perfect vs semantic (decided: {format_type})")
```

**Logging Principles for Python**:
- ✅ **DO**: Use `logger.debug()` for development insights
- ✅ **DO**: Use `logger.warning()` for format deviations or unexpected values
- ✅ **DO**: Use `logger.error()` for parsing/formatting failures
- ✅ **DO**: Include context (element type, field name, values)
- ❌ **DON'T**: Use `print()` statements
- ❌ **DON'T**: Log inside tight loops (performance)
- ❌ **DON'T**: Log sensitive data

**Enable debug logging during development**:
```python
# In test file or main script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Step 4.2: Iterative Development Loop (Communicative + Log-Driven)

**IMPORTANT**: Be communicative during iteration so human can follow along and interrupt if needed.

**At start of implementation, explain approach**:
> Starting implementation for {feature}. My approach based on PRD:
>
> 1. **Parser changes** (PRD Section X.Y):
>    - Extract {field} from S-expression
>    - Handle edge case: {specific edge case}
>
> 2. **Type changes** (PRD Section X.Z):
>    - Add {field} to {dataclass}
>
> 3. **Formatter changes** (PRD Section X.W):
>    - Emit {field} in KiCAD format: `({element} {structure})`
>
> Running tests to establish baseline...

**Iteration cycle** (repeat until tests pass):

1. **Implement** based on PRD requirements and reference S-expression format
   - Update parser to extract new fields
   - Update type definitions (dataclasses)
   - Update formatter to emit fields in exact KiCAD format

2. **Run tests** with verbose output and debug logging:
   ```bash
   # Run specific test file with debug logs
   uv run pytest tests/unit/test_{feature}.py -v --log-cli-level=DEBUG

   # Run reference tests
   uv run pytest tests/reference_tests/test_{feature}_reference.py -v

   # Run all related tests
   uv run pytest tests/ -k "{feature}" -v
   ```

3. **Analyze logs and failures** (use debug logs from Step 4.1):
   - What S-expression structure differs from reference?
   - What fields are missing or incorrect?
   - What values don't match expected format?
   - Are there parsing errors or formatting issues?
   - **Check debug logs** for parser/formatter decisions

4. **Communicate progress** after each iteration:
   > **Iteration {N}**:
   > - Tests: {X} passing, {Y} failing (was {X-1} passing)
   > - Issue found: {specific problem from logs}
   > - Fix attempted: {what I'm trying - reference PRD Section X.Y}
   > - Hypothesis: {why I think this will work}

5. **Compare against reference schematic**:
   ```bash
   # Generate output from current implementation
   python -c "
   import kicad_sch_api as ksa
   sch = ksa.Schematic.load('tests/reference_kicad_projects/{ref}/test.kicad_sch')
   sch.save('/tmp/current_output.kicad_sch')
   "

   # Diff against reference (use logs to understand differences)
   diff tests/reference_kicad_projects/{ref}/test.kicad_sch /tmp/current_output.kicad_sch
   ```

6. **Form hypothesis** about issue (based on logs and diff):
   - "Missing field X in parser" (check parser debug logs)
   - "Formatter emitting wrong order for fields" (check formatter debug logs)
   - "UUID not being preserved in dataclass" (check data transformation logs)
   - "Type conversion losing precision" (check type conversion logs)

7. **Make targeted fix**:
   - Update parser to extract missing field
   - Reorder formatter output to match KiCAD
   - Add field to dataclass
   - Fix type conversion
   - **Add more debug logging** if root cause unclear

8. **Re-run tests** and validate improvement:
   ```bash
   uv run pytest tests/reference_tests/test_{feature}_reference.py -v --log-cli-level=DEBUG
   ```

**Progress indicators** (you're making progress if):
- ✅ More tests pass than previous iteration
- ✅ Diff shows fewer differences
- ✅ S-expression structure closer to reference
- ✅ Logs reveal new information about format

**Stuck indicators** (escalate if):
- ❌ Same failures after 3 iterations
- ❌ No new information from logs or diffs
- ❌ Tests pass but format doesn't match reference
- ❌ Unclear which parser/formatter section to modify

**Maximum iterations**: 8 attempts before asking for guidance

**If stuck after 8 iterations**:
> I've attempted 8 iterations but haven't resolved the issue yet. Here's what I've learned:
>
> **Current Status**:
> - {N} tests passing, {M} tests failing
> - Main issue: {specific problem}
>
> **S-expression Diff**:
> ```
> {Show key differences between output and reference}
> ```
>
> **Hypotheses Tried**:
> 1. {Hypothesis 1} - Result: {outcome}
> 2. {Hypothesis 2} - Result: {outcome}
>
> **Stuck because**: {specific blocker}
>
> **Options**:
> a) Try different approach: {alternative approach}
> b) Need more information: {what information}
> c) Simplify scope: {what to descope}
>
> Which would you like me to try?

### Step 4.3: Format Preservation Validation

**Once tests pass**, perform explicit format validation:

```bash
# Load and save reference schematic
uv run python -c "
import kicad_sch_api as ksa
sch = ksa.Schematic.load('tests/reference_kicad_projects/{ref}/test.kicad_sch')
sch.save('/tmp/format_validation.kicad_sch')
"

# Byte-perfect comparison
diff tests/reference_kicad_projects/{ref}/test.kicad_sch /tmp/format_validation.kicad_sch

# If byte-perfect fails, check semantic equivalence
# (whitespace, field order differences acceptable for some elements)
```

**Validation criteria**:
- ✅ **Byte-perfect**: Ideal - files are identical
- ✅ **Semantic equivalence**: Acceptable - same meaning, minor formatting differences
- ❌ **Missing fields**: Not acceptable - data loss
- ❌ **Wrong values**: Not acceptable - incorrect output

### Step 4.4: Implementation Complete Summary

**When all tests pass and format preserved** (informational):
> ✅ All tests passing:
> - {N} unit tests ✅
> - {M} reference tests ✅
> - {K} integration tests ✅
>
> ✅ Format preservation validated:
> - Byte-perfect match: {YES/NO}
> - Semantic equivalence: {YES/NO}
> - All required fields preserved: ✅
>
> **Diff Summary**:
> ```
> {Show diff output - should be minimal or empty}
> ```
>
> Tests pass! Now proceeding to interactive manual validation...

---

## Phase 4.5: Interactive Manual Validation

**Goal**: Prove the feature works through guided manual inspection in KiCAD

This phase creates demo schematics and walks the user through step-by-step verification, proving the feature works before creating the PR.

### Step 4.5.1: Plan Validation Scenario

**Based on the feature**, determine what to demonstrate and help user think about manual tests.

**For format preservation bugs** (e.g., pin UUIDs):
- Create schematic with feature element
- Show original values
- Perform round-trip (load → save → load)
- Compare values to prove preservation
- **Manual test questions**: "What should I check in KiCAD to confirm this works? Should I verify the element is editable? Should I check properties panel?"

**For new element support** (e.g., text boxes):
- Create schematic with new element
- Show it renders correctly in KiCAD
- Verify all properties are accessible
- Prove it can be modified
- **Manual test questions**: "What visual checks guarantee this works? Can you edit it in KiCAD? Does it export correctly? Are there edge cases to try (empty text, special characters)?"

**For API enhancements** (e.g., new methods):
- Create schematic using new API
- Show the result in KiCAD
- Verify expected behavior
- Test edge cases interactively
- **Manual test questions**: "What scenarios prove this API works correctly? What would break if the implementation was wrong? What edge cases should we try?"

**For connectivity/routing features**:
- Create schematic with connections
- Show connection data
- Verify wires connect to correct pins visually
- Compare netlist output
- **Manual test questions**: "How can we confirm connectivity is correct? Should we compare netlist with kicad-cli? Should we check ERC in KiCAD?"

**Prompt user to think about manual tests**:
> Based on this feature, what manual checks would give you confidence it works correctly?
>
> Suggestions:
> - {Suggestion 1 based on feature type}
> - {Suggestion 2}
> - {Suggestion 3}
>
> Any additional scenarios you want to test?

### Step 4.5.2: Create Validation Script

**Write a Python script** that demonstrates the feature:

```python
# Example: Pin UUID preservation validation
import kicad_sch_api as ksa
import json

print("=" * 70)
print("INTERACTIVE VALIDATION: {Feature Name}")
print("=" * 70)

# Step 1: Create demo schematic
print("\n1️⃣ Creating demo schematic...")
sch = ksa.create_schematic("validation_demo")
# Add relevant elements for the feature
component = sch.components.add(...)
sch.save("/tmp/validation_demo.kicad_sch")
print("✅ Saved to /tmp/validation_demo.kicad_sch")

# Step 2: Extract baseline data
print("\n2️⃣ Extracting baseline data...")
# Read and display feature-specific data
# Save baseline for comparison

# Step 3: Prepare for user inspection
print("\n" + "=" * 70)
print("📋 BASELINE DATA:")
print("-" * 70)
# Display relevant data clearly
print("-" * 70)
```

### Step 4.5.3: Guide User Through Validation

**Open schematic and provide clear instructions**:

```python
# Open in KiCAD
import subprocess
subprocess.run(["open", "/tmp/validation_demo.kicad_sch"])

print("\n" + "=" * 70)
print("✋ WHAT YOU SHOULD SEE:")
print("=" * 70)
print("- {Specific element} at position {X, Y}")
print("- {Property} should be {value}")
print("- {Other observable characteristics}")

print("\n✋ WHAT TO DO:")
print("1. Look at {element} - verify it appears correctly")
print("2. {Optional: inspect properties, modify something}")
print("3. Close KiCAD (don't save changes)")
print("4. Tell me 'closed' when ready to continue")
print("=" * 70)
```

**Keep instructions simple**:
- ✅ One schematic at a time
- ✅ Clear bullet points for what to look for
- ✅ Simple actions ("close KiCAD", "tell me closed")
- ❌ Don't overwhelm with technical details
- ❌ Don't ask user to verify code/UUIDs manually

### Step 4.5.4: Run Validation Tests

**After user inspects**, run automated validation:

```python
print("\n" + "=" * 70)
print("🔄 VALIDATION TEST")
print("=" * 70)

# Perform feature-specific validation
# Example: Round-trip test
print("\n1️⃣ Loading original...")
sch = ksa.Schematic.load("/tmp/validation_demo.kicad_sch")

print("2️⃣ Performing {operation}...")
# Do the operation that tests the feature
sch.save("/tmp/validation_roundtrip.kicad_sch")

print("3️⃣ Comparing results...")
sch2 = ksa.Schematic.load("/tmp/validation_roundtrip.kicad_sch")

# Compare relevant data
all_passed = True
print("\n📋 Comparison Results:")
print("-" * 70)
# Show clear pass/fail for each check
if feature_data_matches:
    print("✅ {Feature}: PRESERVED")
else:
    print("❌ {Feature}: CHANGED (BAD!)")
    all_passed = False

print("-" * 70)

if all_passed:
    print("\n🎉 SUCCESS: Feature is working correctly!")
else:
    print("\n❌ FAILURE: Feature has issues")
```

### Step 4.5.5: Show File-Level Proof

**For format preservation features**, show byte-level comparison:

```bash
echo "📄 ORIGINAL FILE - {Feature} section:"
echo "========================================================"
grep -A 2 '{pattern}' /tmp/validation_demo.kicad_sch

echo ""
echo "📄 AFTER OPERATION - {Feature} section:"
echo "========================================================"
grep -A 2 '{pattern}' /tmp/validation_roundtrip.kicad_sch

echo ""
echo "🔍 CHECKING IF IDENTICAL:"
echo "========================================================"
if diff <(grep -A 2 '{pattern}' /tmp/validation_demo.kicad_sch) \
        <(grep -A 2 '{pattern}' /tmp/validation_roundtrip.kicad_sch) > /dev/null 2>&1; then
    echo "✅ IDENTICAL - Byte-perfect preservation!"
else
    echo "❌ DIFFERENT - Format changed"
fi
```

### Step 4.5.6: Validation Examples by Feature Type

**Format Preservation (e.g., pin UUIDs, properties)**:
```
1. Create schematic with element
2. Show baseline values
3. User inspects in KiCAD → closes
4. Round-trip: load → save → load
5. Compare values (should be identical)
6. Show byte-level diff (should be empty)
```

**New Element Support (e.g., text boxes, shapes)**:
```
1. Create schematic with new element
2. Show element properties
3. User inspects in KiCAD → verifies rendering
4. User optionally modifies in KiCAD → saves
5. Load modified schematic
6. Verify modifications were preserved
```

**API Enhancement (e.g., new methods)**:
```
1. Use new API to create schematic
2. Show resulting structure
3. User inspects in KiCAD → verifies result
4. Try edge cases (empty values, special chars)
5. Verify all cases work correctly
```

**Connectivity/Routing Features**:
```
1. Create schematic with connections
2. Show connection data
3. User inspects in KiCAD → verifies wires connect correctly
4. Run netlist comparison vs kicad-cli
5. Verify nets match exactly
```

### Step 4.5.7: Validation Checkpoint (USER APPROVAL REQUIRED)

**Present validation summary and request approval**:
> ✅ Interactive validation complete!
>
> **What we proved:**
> 1. ✅ {Feature aspect 1} works correctly
> 2. ✅ {Feature aspect 2} is preserved
> 3. ✅ KiCAD opens and displays correctly
> 4. ✅ {Format/behavior} matches expectations
>
> **Evidence:**
> - Manual inspection: User confirmed {what}
> - Automated tests: {N} checks passed
> - File comparison: Byte-perfect match (if applicable)
>
> **Ready to proceed to cleanup and PR?**
> - Type "yes" to proceed with cleanup and PR creation
> - Type "no" or describe issues to go back to implementation

**WAIT for user confirmation** before proceeding to Phase 5.

**If user reports issues:**
- Return to Phase 4 (Implementation)
- Add more debug logging
- Fix identified problems
- Re-run Phase 4.5 validation

---

## Phase 5: Cleanup & Pull Request

**Goal**: Production-ready code with documentation and PR

### Step 5.1: Update Documentation

**Update user-facing documentation** for the new feature:

**README.md** - Add example to relevant section:
```markdown
### {Feature Category}

```python
# Example demonstrating new feature
{code example}
```

**📖 See [API Reference](docs/API_REFERENCE.md#{feature-anchor}) for details**
```

**API_REFERENCE.md** - Add to appropriate section:
```markdown
#### {Feature Name}

{Description of what this feature does}

```python
# Usage examples
{comprehensive examples}
```

**Parameters:**
- `param1` (type): Description
- `param2` (type, optional): Description

**Returns:** Return type and description

**Notes:**
- Important behavior
- Edge cases
- Format preservation details
```

**Documentation guidelines**:
- ✅ Follow existing documentation structure
- ✅ Use code examples (copy from validation phase)
- ✅ Link between README and API_REFERENCE
- ✅ Document all parameters and return types
- ✅ Include notes about format preservation if relevant
- ✅ Keep technical, avoid marketing language
- ❌ Don't create new documentation files unless necessary
- ❌ Don't document internal implementation details

**Files to check**:
- `README.md` - Main library documentation
- `docs/API_REFERENCE.md` - Complete API documentation
- `docs/RECIPES.md` - If adding a common pattern
- `docs/GETTING_STARTED.md` - If affects getting started

### Step 5.2: Code Cleanup

**Remove debug logging**:
```python
# Comment out debug logs (preserve for future debugging)
# logger.debug(f"Parsing {element_type}: {item}")  # DEBUG: Commented for cleanup

# Keep production-level logging
logger.warning(f"Unexpected element type: {element_type}")
logger.error(f"Failed to parse {element}: {error}")
```

**Refactor if needed**:
- Extract repeated code into helper functions
- Improve variable names for clarity
- Add production comments (explain WHY, not WHAT)
- Simplify complex logic

**Format code** (REQUIRED):
```bash
# Format with black
uv run black kicad_sch_api/ tests/

# Sort imports
uv run isort kicad_sch_api/ tests/

# Type checking
uv run mypy kicad_sch_api/

# Linting
uv run flake8 kicad_sch_api/ tests/
```

### Step 5.3: Best Practices Review

**Verify**:
- [ ] Security (no hardcoded paths, validate inputs)
- [ ] Error handling (all parse/format errors handled)
- [ ] Type hints (all functions annotated)
- [ ] All tests pass after cleanup
- [ ] Public APIs have docstrings
- [ ] S-expression format matches KiCAD exactly
- [ ] Field ordering preserved
- [ ] UUIDs preserved on round-trip
- [ ] Grid alignment correct (if relevant)
- [ ] Compatible with KiCAD 7.0 and 8.0
- [ ] Backward compatibility maintained
- [ ] MCP tools still work (if affected)

### Step 5.4: Commit Message Format

**Follow conventional commits** (from `CLAUDE.md`):

```
<type>(<scope>): <subject>

<body>

<footer>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Refactoring
- `perf`: Performance
- `chore`: Tooling, deps

**Example**:
```
fix(parser): Preserve pin UUIDs during round-trip load/save

Pin UUIDs were being dropped during schematic parsing because the
Component dataclass didn't have a field to store them. This fix:

- Adds pin_uuids field to SchematicSymbol dataclass
- Updates symbol parser to extract pin UUIDs from S-expression
- Updates formatter to emit pin entries with preserved UUIDs
- Adds round-trip test to verify UUID preservation

Fixes #139

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Step 5.5: Pre-PR CI Validation and Fixing

**CRITICAL**: Before creating a PR, ensure all CI checks will pass by running and fixing issues locally.

**Run complete CI validation suite**:
```bash
# 1. Format code (FIX, don't just check)
uv run black kicad_sch_api/ tests/
uv run isort kicad_sch_api/ tests/

# 2. Verify formatting is correct
uv run black kicad_sch_api/ tests/ --check
uv run isort kicad_sch_api/ tests/ --check

# 3. Type checking
uv run mypy kicad_sch_api/

# 4. Linting
uv run flake8 kicad_sch_api/ tests/

# 5. All tests pass
uv run pytest tests/ -v

# 6. Format preservation tests
uv run pytest tests/reference_tests/ -v -m format
```

**If any checks fail:**
1. **Fix formatting issues** immediately with `black` and `isort`
2. **Fix type errors** reported by `mypy`
3. **Fix linting issues** reported by `flake8`
4. **Fix failing tests** by returning to implementation phase
5. **Re-run all checks** until everything passes

**NEVER create a PR with failing CI** - fix all issues locally first.

### Step 5.6: Create Pull Request

**Final validation before PR**:
```bash
# Confirm all checks pass
uv run black kicad_sch_api/ tests/ --check && \
uv run isort kicad_sch_api/ tests/ --check && \
uv run mypy kicad_sch_api/ && \
uv run flake8 kicad_sch_api/ tests/ && \
uv run pytest tests/ -v

# If all pass, proceed with PR
echo "✅ All checks passed - ready for PR"
```

**Generate PR description**:
```markdown
## Summary
{1-2 sentence technical summary - NO marketing language}

## Changes
- {Change 1: specific file/module}
- {Change 2: specific file/module}
- {Change 3: specific file/module}

## Testing
- ✅ {N} unit tests (all passing)
- ✅ {M} reference tests (all passing)
- ✅ {K} integration tests (all passing)
- ✅ Format preservation validated against reference schematic

## Requirements Validated
- [x] REQ-1: {requirement description}
- [x] REQ-2: {requirement description}
- [x] All acceptance criteria met

## Format Preservation
- Reference schematic: `tests/reference_kicad_projects/{ref}/`
- Byte-perfect match: {YES/NO}
- Semantic equivalence: {YES/NO}
- KiCAD validation: Opens correctly in KiCAD {version}

## Related
- Closes #{issue number}
- PRD: docs/prd/{feature-name}-prd.md
- Reference: tests/reference_kicad_projects/{ref}/README.md

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Create PR**:
```bash
# Commit changes
git add .
git commit -m "{commit message following conventional commits format}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR
git push origin HEAD
gh pr create --title "{PR title}" --body "{PR description}"
```

### Step 5.7: PR Summary and Completion

**Present completed PR**:
> ✅ **Pull request created**: {PR URL}
>
> **Summary**:
> - {N} tests added (all passing)
> - {M} files changed
> - All requirements validated
> - Format preservation confirmed
>
> **Files Changed**:
> - `kicad_sch_api/parsers/elements/{parser}.py` - Parser updates
> - `kicad_sch_api/core/types.py` - Type definitions
> - `tests/unit/test_{feature}.py` - Unit tests
> - `tests/reference_tests/test_{feature}_reference.py` - Reference tests
> - `tests/reference_kicad_projects/{ref}/` - Reference schematic
> - `docs/prd/{feature}-prd.md` - PRD documentation
>
> **Development workflow complete!** PR is ready for review.

---

## Key Principles

### Reference-Driven Development (TDD with KiCAD as Oracle)
- **Reference = source of truth** - Human creates in KiCAD GUI (known-good)
- **Tests compare against reference** - Agent knows when implementation succeeds
- **Agent iterates autonomously** - Test pass = exact format match
- **Parse reference to understand format** - S-expression becomes specification
- **Replicate exact format in Python** - Byte-perfect or semantically equivalent output
- **Keep references for regression testing** - Future validation and potential training data

### Trusted Actions (Maximize Automation)
- **Agent CAN automate**: `add_component()`, `add_wire()`, `add_label()`, basic connectivity
- **Agent produces ugly but functional**: Complex routing, aesthetic positioning
- **Human required**: Testing the APIs themselves, beautiful layouts, aesthetic judgment
- **Decision rule**: If testing API behavior → agent creates reference. If testing aesthetics → human creates.
- **Most common**: Agent creates functional reference, human optionally refines

### Communicative Implementation
- **Explain approach** before implementing (reference PRD sections)
- **Show progress** after each iteration (tests passing, issues found, fixes tried)
- **Reference PRD** when discussing requirements
- **Human can interrupt** if agent going wrong direction
- **Autonomous but transparent** - human follows along without blocking

### KiCAD Format Preservation
- **Exact S-expression matching** - Primary goal of the library
- **Field order matters** - Preserve KiCAD's ordering
- **UUID preservation critical** - Never generate new UUIDs for existing elements
- **Grid alignment** - Positions must be grid-aligned (multiples of 1.27mm)

### Strategic Logging (Python)
- Use `logging` module, not `print()`
- Debug logs during development, comment out before PR
- Keep warning/error logs for production
- Log at parse/format decision points
- Logs drive hypothesis formation

### Iterative Approach (Log-Driven)
- Test → Analyze Logs → Fix → Repeat
- Maximum 8 iterations before escalating
- Progress = more tests passing or better format matching
- Diff against reference constantly
- Use debug logs to understand failures

### Manual Validation (Belt-and-Suspenders)
- **Always validate manually** even when tests pass
- **Help user think** about what to check
- **Guide step-by-step** - simple, clear instructions
- **One schematic at a time** - respect human constraints
- **Prove it works** before creating PR

### Writing Guidelines (CRITICAL)
- **NO marketing language** - follow `CLAUDE.md` banned words list
- **Technical claims only** - "parses pin UUIDs" not "professional parsing"
- **Engineer tone** - sharing a tool, not selling a product

---

## Output Artifacts

At completion, you'll have:

1. **PRD** (`docs/prd/{feature}-prd.md`)
   - Technical requirements (no marketing language)
   - KiCAD format specifications
   - Success criteria

2. **Reference Schematic** (`tests/reference_kicad_projects/{ref}/`)
   - `test.kicad_sch` - KiCAD reference file
   - `README.md` - Documentation of purpose and contents
   - Source of truth for exact format

3. **Test Suite** (`tests/`)
   - Unit tests for functionality
   - Reference tests for format preservation
   - Integration tests if needed
   - 100% requirement coverage

4. **Implementation** (production code)
   - Parser updates (`kicad_sch_api/parsers/`)
   - Type definitions (`kicad_sch_api/core/types.py`)
   - Formatter updates (`kicad_sch_api/parsers/`)
   - All tests passing
   - Format preservation validated

5. **Pull Request**
   - Conventional commit format
   - Detailed description
   - All quality checks passing
   - Ready for review

---

## When to Use This Workflow

| Use Case | Use `/dev` | Notes |
|----------|-----------|-------|
| Format preservation bug (e.g., #139) | ✅ Yes | Critical - use reference schematic to validate exact format |
| New element support (e.g., #115, #117) | ✅ Yes | Create reference schematic manually, replicate in Python |
| API enhancement (e.g., #142, #134) | ✅ Yes | Reference demonstrates desired behavior |
| Round-trip testing (e.g., #141) | ✅ Yes | Multiple reference schematics for comprehensive testing |
| Quick typo fix or docs update | ❌ No | Just fix directly, no need for full workflow |
| Exploratory research | ❌ No | Use manual investigation first |

---

## Tips for Best Results

**Good problem statements**:
- ✅ "Pin UUIDs not preserved during round-trip load/save"
- ✅ "Add support for text box elements with borders and margins"
- ✅ "Add optional standard Y-axis coordinate system for easier API usage"

**Poor problem statements**:
- ❌ "Make it work" (what specifically?)
- ❌ "Fix the parser" (which part?)
- ❌ "Add stuff" (what stuff?)

**Prepare for success**:
- Be ready to edit schematic in KiCAD during Phase 2
- Have KiCAD installed and ready to open files
- Know which KiCAD elements are involved
- Be available for checkpoint approvals (4 checkpoints)

**Trust the process**:
- **Don't skip phases** - each validates the previous
- **Let iteration happen** - 8 attempts is reasonable for complex format issues
- **Use checkpoints** - catch issues early
- **Reference schematic is critical** - take time to create it properly

**Naming is hard**:
- Reference directory names will evolve
- Include README.md in each reference directory
- Document what the reference is for
- Future: may reorganize for better discoverability

---

## Model Configuration

**Default model**: Uses your configured default (typically `claude-sonnet-4-5`)
- All phases use same model
- Uses Claude Code subscription (free)
- No API costs

---

**This is your complete development workflow for kicad-sch-api. Use it for systematic feature development with reference-driven testing and exact KiCAD format preservation.**
