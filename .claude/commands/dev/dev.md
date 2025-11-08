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
  ├─ Phase 2: Create Reference Schematic (Interactive)
  ├─ Phase 3: Generate Tests
  ├─ Phase 4: Implementation (iterative with logging)
  └─ Phase 5: Cleanup & PR
```

**Time estimate**: 1-4 hours depending on complexity

---

## Usage

```bash
# Format preservation bug
/dev "Pin UUIDs not preserved during round-trip load/save"

# New element support
/dev "Add support for text box elements with borders and margins"

# API enhancement
/dev "Add optional standard Y-axis coordinate system"

# Round-trip testing
/dev "Comprehensive round-trip testing framework for all schematic elements"
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
- **Maximum 5 questions** unless user asks for more detail
- **Keep questions concise** - use bullet points, not paragraphs
- **Be specific** - reference code/files you found during research
- **Offer options** when possible - makes answering easier
- **Skip obvious questions** - if you can infer from code, don't ask

**Question Format**:
```
I've reviewed the codebase and have a few questions:

1. **{Specific question about scope/requirements}**
   - Option A: {brief description}
   - Option B: {brief description}

2. **{Question about technical approach}**

3. **{Question about edge cases}**

(Continue up to 5 questions)
```

**When to ask more than 5 questions**:
- User explicitly requests detailed discussion
- Multiple major architectural decisions needed
- Significant breaking changes involved
- Complex feature with many unknowns

**Examples of GOOD questions**:
- ✅ "Should empty pin UUIDs generate new UUIDs or raise an error?"
- ✅ "Format preservation: byte-perfect or semantic equivalence acceptable?"
- ✅ "Found 3 similar parsers (A, B, C) - which pattern should I follow?"

**Examples of BAD questions**:
- ❌ "What is the problem?" (too vague - you should know from research)
- ❌ "How does KiCAD work?" (research this yourself)
- ❌ Long paragraphs explaining what you found (user doesn't need your research dump)

**Wait for user responses** before proceeding.

### Step 1.3: Generate PRD

**IMPORTANT - Writing Guidelines**:
Following `CLAUDE.md` writing style requirements:
- ❌ **BANNED**: "professional", "seamless", "revolutionary", "cutting-edge", "powerful", "robust"
- ✅ **USE**: Specific technical claims ("parses pin UUIDs", "preserves S-expression format", "tested against KiCAD 8.0")
- 📝 **TONE**: Write like an engineer sharing a useful tool, NOT a startup selling a product

**Generate PRD** in this format:
```markdown
# PRD: {Feature Name}

## Overview
{What we're building and why - technical and specific}

## Success Criteria (Measurable)
- [ ] {Criterion 1 - specific and testable}
- [ ] {Criterion 2}

## Functional Requirements
1. {Requirement 1}
2. {Requirement 2}

## KiCAD Format Specifications
- S-expression structure: {e.g., (pin "1" (uuid "..."))}
- KiCAD version compatibility: {7.0, 8.0}
- Format preservation: {byte-perfect, semantic equivalence}
- Element hierarchy: {where in schematic structure}

## Technical Constraints
- Exact format preservation required
- Maintain backward compatibility with existing API
- {Other constraints}

## Reference Schematic Requirements
- Manual schematic contains: {what elements to create}
- Expected S-expression format: {show example}
- Validation method: {kicad-cli, diff, visual inspection}

## Edge Cases
- {Edge case 1 and how to handle}
- {Edge case 2}

## Impact Analysis
- Parser changes: {what needs updating}
- Formatter changes: {what needs updating}
- Type definitions: {new dataclasses or fields}
- MCP tools affected: {which tools need updates}

## Out of Scope
- {What we're NOT doing}

## Acceptance Criteria
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] All tests pass (unit, integration, reference)
- [ ] Format preservation validated against KiCAD reference
```

**Save PRD** to: `docs/prd/{feature-name}-prd.md`

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

### Step 2.1: Claude Creates Initial Schematic

**Claude creates schematic** based on PRD requirements:

```python
import kicad_sch_api as ksa

# Create schematic with elements needed for feature
sch = ksa.create_schematic("{feature_name}_reference")

# Add components, wires, labels, etc. as needed
# Populate with elements that demonstrate the feature/bug
# Make it as complete as possible to minimize user editing

sch.save("/tmp/{feature_name}_working.kicad_sch")
```

**Principles for initial schematic creation**:
- ✅ **DO**: Create all components mentioned in PRD
- ✅ **DO**: Add basic wiring and connections if relevant
- ✅ **DO**: Include edge cases (empty values, special characters, etc.)
- ✅ **DO**: Use grid-aligned positions (multiples of 1.27mm)
- ❌ **DON'T**: Worry about perfect positioning (user will adjust)
- ❌ **DON'T**: Add elements not related to the feature being tested

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

### Step 2.5: Reference Checkpoint

**Present reference analysis**:
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
> Ready to proceed to test generation?

**Wait for user confirmation** before proceeding to Phase 3.

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

**Test categories** for KiCAD schematic features:

**Unit Tests** (`tests/unit/test_{feature}.py`):
```python
"""Unit tests for {feature} functionality."""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def test_{feature}_basic():
    """Validates: REQ-1 (basic functionality)"""
    # Setup: Create schematic
    sch = ksa.create_schematic("test")

    # Execute: Add/modify element with feature
    element = sch.add_{element}(...)

    # Assert: Element has expected properties
    assert element.{property} == expected_value

def test_{feature}_edge_case_empty():
    """Validates: EDGE-1 (empty/null value handling)"""
    # Test with empty values, null, special characters
    pass

def test_{feature}_preserves_on_roundtrip():
    """Validates: FORMAT-1 (round-trip preservation)"""
    # Load schematic, save immediately, compare
    sch = ksa.Schematic.load("path/to/reference")
    sch.save("/tmp/roundtrip.kicad_sch")
    # Assert: Files match or semantically equivalent
    pass
```

**Reference Tests** (`tests/reference_tests/test_{feature}_reference.py`):
```python
"""Reference schematic validation for {feature}."""

import pytest
import kicad_sch_api as ksa

REFERENCE_PATH = "tests/reference_kicad_projects/{reference_name}/test.kicad_sch"

def test_parse_{feature}_reference():
    """Validates: Can parse reference schematic with {feature}"""
    sch = ksa.Schematic.load(REFERENCE_PATH)

    # Assert: Elements parsed correctly
    assert len(sch.{elements}) == expected_count
    assert sch.{element}.{property} == expected_value

def test_format_preservation_{feature}():
    """Validates: FORMAT-2 (exact format preservation against reference)"""
    # Load reference
    sch = ksa.Schematic.load(REFERENCE_PATH)

    # Save to temp
    sch.save("/tmp/test_output.kicad_sch")

    # Compare S-expressions (byte-perfect or semantic)
    with open(REFERENCE_PATH, 'r') as f:
        original = f.read()
    with open("/tmp/test_output.kicad_sch", 'r') as f:
        output = f.read()

    # Assert: Format preserved
    assert output == original or semantically_equivalent(output, original)

def test_replicate_{feature}_programmatically():
    """Validates: Can create reference schematic programmatically"""
    # Create schematic from scratch
    sch = ksa.create_schematic("test")

    # Add elements to match reference
    # ... (replicate reference structure)

    # Save and compare to reference
    sch.save("/tmp/programmatic.kicad_sch")
    # Assert: Matches reference format
```

**Integration Tests** (`tests/integration/test_{feature}_integration.py`):
```python
"""Integration tests for {feature} with other components."""

def test_{feature}_with_connectivity():
    """Validates: Feature works with connectivity analysis"""
    pass

def test_{feature}_with_mcp_tools():
    """Validates: MCP tools handle feature correctly"""
    pass
```

**Format Preservation Tests** (use pytest marker `@pytest.mark.format`):
```python
@pytest.mark.format
def test_exact_format_preservation():
    """Critical: Byte-perfect format preservation"""
    pass
```

### Step 3.3: Create Test Files

**Create test files with proper structure**:
```bash
# Unit tests
tests/unit/test_{feature}.py

# Reference tests
tests/reference_tests/test_{feature}_reference.py

# Integration tests (if needed)
tests/integration/test_{feature}_integration.py
```

**Use pytest markers** from `pyproject.toml`:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.format` - Format preservation (CRITICAL)
- `@pytest.mark.validation` - Validation and error handling

### Step 3.4: Test Plan Checkpoint

**Present test plan**:
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
> Ready to proceed to implementation?

**Wait for user approval** before proceeding to Phase 4.

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

### Step 4.2: Iterative Development Loop

**Iteration cycle** (repeat until tests pass):

1. **Implement** based on PRD requirements and reference S-expression format
   - Update parser to extract new fields
   - Update type definitions (dataclasses)
   - Update formatter to emit fields in exact KiCAD format

2. **Run tests** with verbose output:
   ```bash
   # Run specific test file
   uv run pytest tests/unit/test_{feature}.py -v --log-cli-level=DEBUG

   # Run reference tests
   uv run pytest tests/reference_tests/test_{feature}_reference.py -v

   # Run all related tests
   uv run pytest tests/ -k "{feature}" -v
   ```

3. **Analyze logs and failures**:
   - What S-expression structure differs from reference?
   - What fields are missing or incorrect?
   - What values don't match expected format?
   - Are there parsing errors or formatting issues?

4. **Compare against reference schematic**:
   ```bash
   # Generate output from current implementation
   python -c "
   import kicad_sch_api as ksa
   sch = ksa.Schematic.load('tests/reference_kicad_projects/{ref}/test.kicad_sch')
   sch.save('/tmp/current_output.kicad_sch')
   "

   # Diff against reference
   diff tests/reference_kicad_projects/{ref}/test.kicad_sch /tmp/current_output.kicad_sch
   ```

5. **Form hypothesis** about issue:
   - "Missing field X in parser"
   - "Formatter emitting wrong order for fields"
   - "UUID not being preserved in dataclass"
   - "Type conversion losing precision"

6. **Make targeted fix**:
   - Update parser to extract missing field
   - Reorder formatter output to match KiCAD
   - Add field to dataclass
   - Fix type conversion

7. **Re-run tests** and validate improvement:
   ```bash
   uv run pytest tests/reference_tests/test_{feature}_reference.py -v
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

### Step 4.4: Implementation Checkpoint

**When all tests pass and format preserved**:
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
> Please validate:
> 1. Open the generated schematic in KiCAD - does it work?
> 2. Are there any edge cases or scenarios to test?
> 3. Ready to proceed to cleanup?

**Wait for user confirmation** before proceeding to Phase 5.

---

## Phase 5: Cleanup & Pull Request

**Goal**: Production-ready code with PR

### Step 5.1: Code Cleanup

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

### Step 5.2: Best Practices Review

**Check for**:
- [ ] **Security**: No hardcoded paths, validate inputs
- [ ] **Error handling**: All parse/format errors handled gracefully
- [ ] **Type hints**: All functions have proper type annotations
- [ ] **Testing**: All tests still pass after cleanup
- [ ] **Documentation**: Public APIs have docstrings
- [ ] **Format preservation**: Round-trip tests pass
- [ ] **Backward compatibility**: No breaking changes to existing API
- [ ] **MCP compatibility**: If MCP tools affected, verify they still work

**KiCAD-specific checks**:
- [ ] **S-expression format**: Matches KiCAD exactly
- [ ] **Field ordering**: Preserves KiCAD's field order
- [ ] **UUID handling**: UUIDs preserved on round-trip
- [ ] **Grid alignment**: Positions are grid-aligned (if relevant)
- [ ] **KiCAD version**: Compatible with 7.0 and 8.0

### Step 5.3: Commit Message Format

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

### Step 5.4: Create Pull Request

**Run final validation**:
```bash
# All tests pass
uv run pytest tests/ -v

# Code quality
uv run black kicad_sch_api/ tests/ --check
uv run isort kicad_sch_api/ tests/ --check
uv run mypy kicad_sch_api/
uv run flake8 kicad_sch_api/ tests/

# Format preservation tests
uv run pytest tests/reference_tests/ -v -m format
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

### Step 5.5: Final Approval

**Present PR**:
> ✅ Pull request created: {PR URL}
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
> Please review the PR. Any final changes needed?

---

## Key Principles

### Reference-Driven Development
- **Always create reference schematic first** - Claude creates initial, user edits in KiCAD
- **Parse reference to understand format** - S-expression becomes source of truth
- **Replicate exact format in Python** - Byte-perfect or semantically equivalent output
- **Keep references for regression testing** - Future validation and potential training data

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

### Iterative Approach
- Test → Analyze → Fix → Repeat
- Maximum 8 iterations before escalating
- Progress = more tests passing or better format matching
- Diff against reference constantly

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
