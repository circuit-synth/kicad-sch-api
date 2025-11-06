# Metrics Tracking Template - Daily & Weekly Snapshots

**Use this template to track progress against plan during the 2-week sprint.**

---

## Daily Standup Metrics (Complete Before Standup)

### Day: _________________ (Week 1 / 2, Day __ of 14)

#### Timeline Baseline
- **Days Elapsed**: ___ / 14
- **Target Daily Progress**: 10% per day
- **Expected Cumulative Progress**: __% (10 × days elapsed)

---

### Track A: Core Server & MCP Framework

#### Deliverables Progress

| Item | Planned | Completed | % Done | Notes |
|------|---------|-----------|--------|-------|
| Server initialization | Yes | ☐ | __% | |
| Pydantic models | Yes | ☐ | __% | |
| Tool infrastructure | Yes | ☐ | __% | |
| Error handling | Yes | ☐ | __% | |
| create_schematic tool | Yes | ☐ | __% | |
| load_schematic tool | Yes | ☐ | __% | |
| save_schematic tool | Yes | ☐ | __% | |
| add_component tool | Yes | ☐ | __% | |
| list_components tool | Yes | ☐ | __% | |
| Tool documentation | Yes | ☐ | __% | |
| Resource endpoints | Yes | ☐ | __% | |
| Prompt templates | Yes | ☐ | __% | |
| **TRACK A TOTAL** | **12** | **__** | **__%** | |

#### Quality Metrics

```
Lines of Code Written:     _______ (target: 2000-3000)
Test Count:                ___ / ___ (target: 50+ tests)
Test Coverage:             __% (target: >90%)
Type Check Status:         ☐ Passing (strict mode)
Code Review PRs Pending:   ___ (should be 0-2)
```

#### Blockers & Issues

```
Current Blockers:
[ ] Issue 1: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____

[ ] Issue 2: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____

[ ] Issue 3: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____

Outstanding PRs:
[ ] PR #___ - _____________________ (ready for review)
[ ] PR #___ - _____________________ (waiting for: ___)
```

#### Commits Yesterday

```bash
# Copy output from: git log --oneline -10 --author="[Track A Lead]"
```

___ commits

#### Today's Plan

```
1. _________________________________
2. _________________________________
3. _________________________________

Expected completion:  ☐ All 3    ☐ 2 of 3    ☐ 1 of 3    ☐ None
```

#### Asks for Other Tracks

```
From Track B: _________________ (needed by: ___)
From Track C: _________________ (needed by: ___)
```

---

### Track B: Connectivity & Pin Management

#### Deliverables Progress

| Item | Planned | Completed | % Done | Notes |
|------|---------|-----------|--------|-------|
| Pin rotation math | Yes | ☐ | __% | |
| Y-axis transformation | Yes | ☐ | __% | |
| Pin rotation unit tests (11) | Yes | ☐ | __% | |
| Reference test setup (8) | Yes | ☐ | __% | |
| Wire routing logic | Yes | ☐ | __% | |
| Connect_pins tool | Yes | ☐ | __% | |
| Add_label tool | Yes | ☐ | __% | |
| Add_junction tool | Yes | ☐ | __% | |
| Connectivity analysis | Yes | ☐ | __% | |
| Hierarchical detection | Yes | ☐ | __% | |
| Netlist generation | Yes | ☐ | __% | |
| Documentation | Yes | ☐ | __% | |
| **TRACK B TOTAL** | **12** | **__** | **__%** | |

#### Quality Metrics

```
Pin Rotation Tests:        ___ / 11 passing ✓
Reference Validations:     ___ / 8 passing ✓
Connectivity Tests:        ___ / 25 passing ✓
Coordinate Accuracy:       ±__mm (target: ±0.05mm)
Test Coverage:             __% (target: >90%)
Type Check Status:         ☐ Passing (strict mode)
```

#### Critical Checklist (KiCAD Compatibility)

```
Y-Axis Transformation Working?           ☐ YES  ☐ NO  ☐ IN PROGRESS
- Pin numbers in correct positions?      ☐ YES  ☐ NO
- Y-negation happens before rotation?    ☐ YES  ☐ NO

Pin Rotation Tests (All rotations):
- 0°   rotation passing?                 ☐ YES  ☐ NO
- 90°  rotation passing?                 ☐ YES  ☐ NO
- 180° rotation passing?                 ☐ YES  ☐ NO
- 270° rotation passing?                 ☐ YES  ☐ NO

Reference KiCAD Validation:
- Single component test passing?         ☐ YES  ☐ NO
- Rotated components test passing?       ☐ YES  ☐ NO
- Hierarchical structure test passing?   ☐ YES  ☐ NO
- Wire connectivity test passing?        ☐ YES  ☐ NO
```

#### Blockers & Issues

```
Current Blockers:
[ ] Issue 1: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____

[ ] Issue 2: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____
```

#### Commits Yesterday

___ commits

#### Today's Plan

```
1. _________________________________
2. _________________________________
3. _________________________________
```

#### Asks for Other Tracks

```
From Track A: _________________ (needed by: ___)
From Track C: _________________ (needed by: ___)
```

---

### Track C: Pattern Library & Examples

#### Deliverables Progress

| Item | Planned | Completed | % Done | Notes |
|------|---------|-----------|--------|-------|
| add_decoupling_caps | Yes | ☐ | __% | |
| add_pull_resistor | Yes | ☐ | __% | |
| add_led_indicator | Yes | ☐ | __% | |
| add_voltage_divider | Yes | ☐ | __% | |
| add_rc_filter | Yes | ☐ | __% | |
| Voltage divider example | Yes | ☐ | __% | |
| LED circuit example | Yes | ☐ | __% | |
| MCU minimal system | Yes | ☐ | __% | |
| Power supply example | Yes | ☐ | __% | |
| Filter circuit example | Yes | ☐ | __% | |
| Tool documentation | Yes | ☐ | __% | |
| Pattern tests (>90% coverage) | Yes | ☐ | __% | |
| **TRACK C TOTAL** | **12** | **__** | **__%** | |

#### Quality Metrics

```
Patterns Implemented:      ___ / 6 (target: all 6)
Example Circuits:          ___ / 5 (target: all 5)
All patterns KiCAD valid?: ☐ YES  ☐ NO  ☐ PARTIAL
Test Coverage:             __% (target: >90%)
Documentation Pages:       ___ / 3 (target: all 3)
Type Check Status:         ☐ Passing (strict mode)
```

#### Blockers & Issues

```
Current Blockers:
[ ] Issue 1: _________________ (blocking since: ___)
    Owner: _____ | ETA to fix: _____

Dependency Issues:
[ ] Waiting on API from Track A: _________________
[ ] Waiting on feature from Track B: _________________
```

#### Commits Yesterday

___ commits

#### Today's Plan

```
1. _________________________________
2. _________________________________
3. _________________________________
```

#### Asks for Other Tracks

```
From Track A: _________________ (needed by: ___)
From Track B: _________________ (needed by: ___)
```

---

## Cross-Track Dependency Status

### Critical Dependencies (Update Daily)

| Dependency | Owner | Status | ETA | Risk |
|------------|-------|--------|-----|------|
| Component API finalization | Track A | ☐ Done ☐ In Progress ☐ At Risk | ___ | |
| Pin transformation working | Track B | ☐ Done ☐ In Progress ☐ At Risk | ___ | |
| Connectivity tools ready | Track B | ☐ Done ☐ In Progress ☐ At Risk | ___ | |
| Pattern library enabled | Track C | ☐ Done ☐ In Progress ☐ At Risk | ___ | |

### Shared Resources / Conflicts

```
Any resource conflicts this sprint?

[ ] Build system issues: _____________________
[ ] Symbol library issues: _____________________
[ ] Test environment issues: _____________________
[ ] Documentation conflicts: _____________________

Blocker resolution needed? ☐ YES  ☐ NO
Escalate to: Tech Lead / Product Owner
```

---

## Weekly Summary (Complete Friday EOD)

### Week 1 (Days 1-5) Summary

**Date**: Friday, ________________

#### Overall Progress

```
PLANNED FOR WEEK 1:    40% of 2-week sprint
ACTUAL COMPLETION:     __%
ON TRACK?              ☐ YES (40-50% done)
                       ☐ BEHIND (< 40% done)
                       ☐ AHEAD (> 50% done)
```

#### By Track

```
Track A Completion:    __% (planned: 40%)
  ✓ Successes: [list 2-3]
  ⚠ Challenges: [list 2-3]
  → Next week focus: [top 3 items]

Track B Completion:    __% (planned: 40%)
  ✓ Successes: [list 2-3]
  ⚠ Challenges: [list 2-3]
  → Next week focus: [top 3 items]

Track C Completion:    __% (planned: 40%)
  ✓ Successes: [list 2-3]
  ⚠ Challenges: [list 2-3]
  → Next week focus: [top 3 items]
```

#### Quality Metrics Summary

```
Test Count:                 ___ total tests
Test Coverage:              __% (target: >90%)
Type Checking:              ✓ Passing strict mode
Commits:                    ___ total
Code Review:                All PRs merged: ☐ YES ☐ NO
Blockers Unresolved:        ___ (should be 0)
```

#### Velocity Metrics

```
Planned Tasks Completed:    ___ / 36 (estimate: 14-15 expected)
Unplanned Work Added:       ___ tasks (scope creep? ☐ YES ☐ NO)
Unplanned Blockers:         ___ (document below)
```

#### Blockers Encountered (Week 1)

```
1. BLOCKER: _________________________________
   When discovered: Day __
   Duration blocked: __ hours
   Root cause: _________________________________
   Resolution: _________________________________
   Learning: _________________________________

2. BLOCKER: _________________________________
   [same structure as above]

3. BLOCKER: _________________________________
   [same structure as above]
```

#### Risks & Mitigations (Week 1)

```
Risk 1: _________________________________ (Probability: High/Med/Low)
  Mitigation: _________________________________
  Owner: _____

Risk 2: _________________________________ (Probability: High/Med/Low)
  Mitigation: _________________________________
  Owner: _____

Risk 3: _________________________________ (Probability: High/Med/Low)
  Mitigation: _________________________________
  Owner: _____
```

#### Week 1 Retrospective Insights

```
What Went Well:
- _________________________________
- _________________________________
- _________________________________

What Could Improve:
- _________________________________
- _________________________________
- _________________________________

Adjustments for Week 2:
1. _________________________________
2. _________________________________
3. _________________________________
```

#### Week 2 Plan Confirmation

```
Track A Focus (Days 6-10):
[ ] Item 1: _________________________________
[ ] Item 2: _________________________________
[ ] Item 3: _________________________________

Track B Focus (Days 6-10):
[ ] Item 1: _________________________________
[ ] Item 2: _________________________________
[ ] Item 3: _________________________________

Track C Focus (Days 6-10):
[ ] Item 1: _________________________________
[ ] Item 2: _________________________________
[ ] Item 3: _________________________________

Timeline Adjustment Needed?  ☐ YES  ☐ NO
Scope Adjustment Needed?     ☐ YES  ☐ NO
Resource Adjustment Needed?  ☐ YES  ☐ NO
```

---

## Daily Standup Checklist

### 5 Minutes Before Standup (Fill This In)

```
Track Lead: _____________________
Date: __________________

[ ] Ran test suite: Results: ___/__ passing
[ ] Checked coverage: Current: __%
[ ] Counted commits: ___ yesterday
[ ] Listed blockers: ___ active blockers
[ ] Prepared talking points: ☐ Yes ☐ No
[ ] Metrics ready: ☐ Yes ☐ No
[ ] Dependencies checked: ☐ Yes ☐ No
```

---

## Dashboard Quick Reference

Print this, update daily, put on wall:

```
═════════════════════════════════════════════════════════
  MCP PIN CONNECTION IMPLEMENTATION - SPRINT DASHBOARD
═════════════════════════════════════════════════════════

TODAY: ________________  |  DAY __ OF 14

TARGET PROGRESS:  10% per day = 140% ÷ 14 days
CUMULATIVE TARGET: __ days × 10% = __% (should be at __%)

TRACK STATUS:
─────────────
Track A (Server):      [████░░░░░░░░░] __% (target: __%)
Track B (Connectivity): [████░░░░░░░░░] __% (target: __%)
Track C (Patterns):     [████░░░░░░░░░] __% (target: __%)

TEST STATUS:
────────────
Tests Passing:  ____ / ____ (__%)
Coverage:       __% (target: >90%)
Type Check:     ☐ PASS ☐ FAIL

BLOCKERS:
─────────
🔴 Critical: ___ (active)
🟠 High:     ___ (active)
🟡 Medium:   ___ (active)

ON TRACK?
─────────
☐ YES - Staying on pace
☐ NO  - Behind, needs adjustment
☐ AHEAD - Ahead of schedule

═════════════════════════════════════════════════════════
```

---

## Escalation Trigger Metrics

### Automatic Escalation Triggers

Check these every standup:

```
ESCALATE IF:
────────────
[ ] Any blocker > 4 hours old without owner assigned
[ ] Test coverage < 85% (any track)
[ ] Test suite failing (> 5 tests)
[ ] Schedule slip > 1 day (> 10%)
[ ] Unplanned work > 10% scope addition
[ ] Type checking failing (any errors)
[ ] Code review queue > 3 PRs
[ ] Any track's progress < 90% of daily target
```

### Escalation Email Template

```
TO: Tech Lead [+ Product Owner if scope/timeline]
SUBJECT: [ESCALATION] [Track X] [Issue]

ISSUE: [1 sentence]

IMPACT:
- Track: [A/B/C]
- Days impact: +__ hours/days
- Tests affected: __ failing
- Scope impact: __

CONTEXT:
- Duration: __ minutes/hours
- Cause: _________________
- Attempts: [what's been tried]

NEEDS:
- Decision by: [time]
- On: [specific decision]
```

---

## Data Collection Scripts

Save these and run before daily standup:

### `collect-track-metrics.sh`

```bash
#!/bin/bash
# Collects metrics for your track

TRACK=$1  # A, B, or C
DATE=$(date +%Y-%m-%d)
HOUR=$(date +%H:%M)

echo "COLLECTING METRICS FOR TRACK $TRACK"
echo "Time: $DATE $HOUR"
echo ""

# Test metrics
echo "Test Count:"
uv run pytest --collect-only -q 2>/dev/null | tail -1

echo "Test Results:"
uv run pytest tests/ -q --tb=no 2>&1 | tail -1

echo "Coverage:"
uv run pytest --cov=kicad_sch_api --cov-report=term-missing 2>&1 | grep TOTAL

echo "Commits:"
git log --oneline -5

echo ""
echo "Ready for standup!"
```

### `daily-metrics-snapshot.sh`

```bash
#!/bin/bash
# Full dashboard snapshot

DATE=$(date +%Y-%m-%d_%H:%M)
REPORT="metrics_$DATE.txt"

{
  echo "=== METRICS SNAPSHOT ==="
  echo "Date: $DATE"
  echo ""

  echo "Test Status:"
  uv run pytest --collect-only -q 2>/dev/null | tail -1
  uv run pytest tests/ -q --tb=no 2>&1 | tail -1
  echo ""

  echo "Coverage:"
  uv run pytest --cov=kicad_sch_api --cov-report=term-missing 2>&1 | grep TOTAL
  echo ""

  echo "Code Stats:"
  echo "Lines: $(find kicad_sch_api -name '*.py' | xargs wc -l | tail -1)"
  echo ""

  echo "Recent Work:"
  git log --oneline -10

} | tee "$REPORT"

echo "Saved to: $REPORT"
```

---

## Key Metrics to Watch

### Green Light (Keep Going)

```
✓ Tests passing: > 95%
✓ Coverage: > 90%
✓ Type check: 0 errors
✓ Progress: >= 10% per day
✓ Blockers: < 1 hour duration
✓ PRs: all reviewed within 4 hours
```

### Yellow Light (Monitor Closely)

```
⚠ Tests passing: 85-95%
⚠ Coverage: 85-90%
⚠ Type check: < 5 errors
⚠ Progress: 8-10% per day
⚠ Blockers: 1-4 hours duration
⚠ PRs: some waiting > 4 hours
```

### Red Light (Escalate)

```
🔴 Tests passing: < 85%
🔴 Coverage: < 85%
🔴 Type check: > 5 errors
🔴 Progress: < 8% per day
🔴 Blockers: > 4 hours duration
🔴 PRs: waiting > 8 hours
```

---

**Print this template and fill it in daily.**
**Share metrics every standup.**
**Let data guide decisions.**
