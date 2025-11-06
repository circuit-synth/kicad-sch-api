# Daily Standup Runbook: MCP Pin Connection Implementation

**Project**: kicad-sch-api MCP Server
**Duration**: 15 minutes daily (Monday-Friday)
**Participants**: 3 parallel development tracks
**Coordinator**: Tech Lead
**Escalation Contact**: Product Owner

---

## Table of Contents

1. [Pre-Standup Preparation](#pre-standup-preparation)
2. [Standup Flow & Timing](#standup-flow--timing)
3. [Daily Focus Questions](#daily-focus-questions)
4. [Weekly Retrospective](#weekly-retrospective)
5. [Decision Trees](#decision-trees)
6. [Escalation Procedures](#escalation-procedures)
7. [Metrics Dashboard](#metrics-dashboard)
8. [Post-Standup Actions](#post-standup-actions)

---

## Pre-Standup Preparation

### 5 Minutes Before Standup

**Time**: 09:55 AM (if standup is at 10:00 AM)

#### For All Developers

**Prepare these talking points:**

```
Status Update Template:
1. Yesterday's Progress (what was completed)
2. Today's Plan (what will be done)
3. Blockers & Risks (anything preventing progress)
4. Help Needed (requests for unblocking)
```

**Gather metrics:**

- [ ] Count commits made yesterday
- [ ] Check test pass/fail status
- [ ] Review any open pull requests
- [ ] Note any failing test suites
- [ ] Document any performance issues discovered
- [ ] List any infrastructure problems

**Check logs:**

```bash
# Terminal Command: Run before standup
echo "=== TEST STATUS ==="
uv run pytest tests/ -q 2>&1 | tail -5

echo "=== RECENT COMMITS ==="
git log --oneline -5

echo "=== BRANCH STATUS ==="
git branch -vv

echo "=== UNCOMMITTED CHANGES ==="
git status --short
```

**Script for automated pre-standup checklist** (save as `.dev/pre-standup.sh`):

```bash
#!/bin/bash
echo "PRE-STANDUP CHECKLIST"
echo "===================="
echo ""
echo "TEST STATUS:"
uv run pytest tests/ -q --tb=no 2>&1 | tail -3
echo ""
echo "RECENT COMMITS:"
git log --oneline -3 --author="$(git config user.name)"
echo ""
echo "OPEN BRANCHES:"
git branch -vv | grep "^\*"
echo ""
echo "UNCOMMITTED CHANGES:"
git status -s | wc -l
echo ""
echo "Ready for standup!"
```

#### For Track Leads

**Prepare metrics dashboard:**

- Track A (Core Server):
  - [ ] Lines of code written
  - [ ] Test coverage percentage
  - [ ] Tool count implemented
  - [ ] Open issues/blockers

- Track B (Connectivity Layer):
  - [ ] Wire routing implementation status
  - [ ] Pin position accuracy metrics
  - [ ] Integration test results
  - [ ] Reference schematic validation count

- Track C (Pattern Library):
  - [ ] Pattern implementations completed
  - [ ] Pattern test coverage
  - [ ] Example schematics created
  - [ ] Documentation pages written

**Check metrics sources:**

```bash
# Code coverage
uv run pytest --cov=kicad_sch_api --cov-report=term-missing | grep TOTAL

# Line count by module
find kicad_sch_api -name "*.py" | xargs wc -l | tail -1

# Test count
uv run pytest --collect-only -q | tail -1

# Open issues in git (via labels/comments)
git log --oneline --grep="FIXME\|TODO" -5
```

---

## Standup Flow & Timing

### Total Duration: 15 minutes

```
09:55 - 10:00: Developer prep + gather metrics
10:00 - 10:03: Track A Update (3 min)
10:03 - 10:06: Track B Update (3 min)
10:06 - 10:09: Track C Update (3 min)
10:09 - 10:12: Cross-Track Sync (3 min)
10:12 - 10:15: Action Items & Closing (3 min)
```

### Track A Update: Core Server & Framework (3 minutes)

**Who**: Track Lead A
**Focus**: FastMCP foundation, tool infrastructure, error handling

**What to share:**

```
COMPLETED YESTERDAY:
- List 2-3 completed tasks with commit hashes
- Example: "Implemented add_component tool (abc1234)"

IN PROGRESS:
- List current task + estimated completion
- Percentage complete (if applicable)

BLOCKERS:
- Any FastMCP version issues?
- Any type checking failures (mypy)?
- Any test coverage drops?
- Any performance regressions?

ASKS FOR TEAM:
- Do we need help from Track B?
- Any shared dependencies needed from Track C?
```

**Metrics to share:**

```
Track A Dashboard:
- Tools implemented: N/18 (percentage %)
- Test coverage: N% (target >90%)
- Type checking: Strict mode passing? (yes/no)
- Open PRs: N (linked)
```

**Example response** (1.5 min):

> "Track A made good progress yesterday. We finished implementing the core server initialization (commit abc1234) and added error handling patterns (def5678). We're currently working on the schematic_tools module - about 60% done, expect completion by EOD today. No blockers currently. We need Track B to finalize the connectivity API signature we discussed so we can match our tool inputs properly."

---

### Track B Update: Connectivity & Pin Management (3 minutes)

**Who**: Track Lead B
**Focus**: Wire routing, pin positions, connection detection, net analysis

**What to share:**

```
COMPLETED YESTERDAY:
- List completed connectivity features
- Reference test cases passing
- Example: "Implemented pin rotation transformation (xyz9012)"

IN PROGRESS:
- Current connectivity implementation
- Test validation status
- Estimated completion

BLOCKERS:
- Pin position calculation issues?
- Coordinate system problems?
- Test failures vs KiCAD output?
- Documentation gaps?

ASKS FOR TEAM:
- Does Track A need coordinate system docs?
- Does Track C need wire connectivity API?
```

**Metrics to share:**

```
Track B Dashboard:
- Pin rotation tests passing: N/11
- Reference schematic validations: N/8
- Connectivity tests passing: N/25
- Pin position accuracy: ±0.05mm?
```

**Critical reminder** (CLAUDE.md section):

> **KiCAD uses TWO coordinate systems!**
> - Symbol space: Normal Y-axis (+Y up)
> - Schematic space: Inverted Y-axis (+Y down)
> - **Solution**: Y-negation must happen BEFORE rotation/mirroring
>
> If tests show pin numbers swapped → check Y-axis transformation!

**Example response** (1.5 min):

> "Track B wrapped up pin rotation testing yesterday - all 11 unit tests pass and 8 reference tests validate against real KiCAD. We're now working on hierarchical connectivity detection and found an interesting issue with how parent/child UUIDs propagate. About 70% complete. Currently blocked on clarifying the hierarchy context API from the library - Track A, do you have the set_hierarchy_context() signature finalized? We need it to validate our netlist generation."

---

### Track C Update: Pattern Library & Examples (3 minutes)

**Who**: Track Lead C
**Focus**: High-level patterns, example circuits, documentation

**What to share:**

```
COMPLETED YESTERDAY:
- Patterns implemented (decoupling caps, LED, resistor divider, etc.)
- Example circuits created
- Documentation written
- Example: "Added 3 pattern tools + 2 example conversations (pqr3456)"

IN PROGRESS:
- Current pattern implementation
- Example circuit creation
- Documentation completion status

BLOCKERS:
- Missing component APIs from Track A?
- Tool signature changes from other tracks?
- Symbol library availability?

ASKS FOR TEAM:
- Do we have final component API signatures?
- Can Track B confirm netlist format for BOM generation?
```

**Metrics to share:**

```
Track C Dashboard:
- Patterns implemented: N/6 (decoupling, LED, divider, filter, pull-resistor, etc.)
- Example conversations: N/5 (voltage divider, LED, minimal MCU, etc.)
- Documentation pages: N/3 (guides, examples, troubleshooting)
- Test coverage for patterns: N%
```

**Example response** (1.5 min):

> "Track C made solid progress on pattern implementations. We finished add_decoupling_caps and add_led_indicator, and started add_voltage_divider - about 50% done. Created 2 example conversations so far. One thing blocking us: the add_component tool signature is still evolving in Track A. We need it finalized so we can lock in our pattern implementations. Also, when Track B has the netlist generation working, we need that for BOM generation in our patterns."

---

### Cross-Track Sync (3 minutes)

**Who**: Tech Lead (facilitate)
**Focus**: Dependency coordination, API alignment, integration planning

**Sync checklist:**

```
DEPENDENCY CHECK:
[ ] Are Track A tool signatures stable for Track B/C?
[ ] Has Track B finalized coordinate system handling?
[ ] Are there any shared data structures misaligned?
[ ] Do all tracks agree on error handling patterns?

API ALIGNMENT:
[ ] Are input/output models consistent across tracks?
[ ] Are there conflicting design decisions?
[ ] Do tool names follow consistent naming patterns?

INTEGRATION POINTS:
[ ] When will Track A/B be ready for integration?
[ ] What testing will happen at integration boundaries?
[ ] Who's responsible for integration glue code?

CRITICAL BLOCKERS:
[ ] Is anything blocking another track?
[ ] Do we need architecture adjustments?
[ ] Are there resource conflicts?
```

**Tech Lead questions to ask:**

1. **Track A → B**: "Are connectivity tool inputs compatible with component positions Track A provides?"

2. **Track B → C**: "Will pattern library patterns get correct pin positions from Track B's transformations?"

3. **Track C → A**: "Do we have all the component types patterns need in the tool library?"

4. **Global**: "Are we tracking to our 2-week timeline? Any scope creep?"

5. **Integration**: "When should we start integration testing between tracks?"

**Example exchange** (2 min):

> **Tech Lead**: "Quick dependency check. Track A, Track B needs the component position API finalized - can we commit to the API by EOD tomorrow?"
>
> **Track A Lead**: "Yes, we can finalize add_component and list_components by EOD tomorrow. We might change the position return format from (x, y) to a Point object though."
>
> **Track B Lead**: "A Point object works better for us actually - easier to work with in transformation math. We can adjust."
>
> **Tech Lead**: "Great. Track B, once you have that, how long until you can deliver wire connectivity?"
>
> **Track B Lead**: "With the Point object, I'd say 2 days. We have the math done, just need to integrate and test."
>
> **Tech Lead**: "Perfect. Track C, that means you'll have connectivity APIs by Thursday - does that work for pattern implementation?"
>
> **Track C Lead**: "Yes, that's our planned dependency."

---

### Action Items & Closing (3 minutes)

**Who**: Tech Lead (document and assign)
**Focus**: Clear ownership, deadlines, blocking issue resolution

**Action item template:**

```
ACTION ITEM FORMAT:
- Description: [Clear, specific task]
- Owner: [Person responsible]
- Deadline: [Date & time]
- Dependencies: [Anything blocking this]
- Risk: [What could prevent completion]
- Status: [Not started / In progress / At risk]
```

**Document these:**

1. **Blockers needing immediate action:**
   - Owner: [assigned]
   - Action: [specific steps to unblock]
   - Deadline: [ASAP / EOD today / EOD tomorrow]
   - Check-in: [next standup / separate sync]

2. **Dependency deliverables:**
   - What: [API signature / feature / documentation]
   - Who: [Track A/B/C lead]
   - By when: [specific date]
   - Verification: [how will we know it's done]

3. **Timeline adjustments:**
   - Current plan: [original timeline]
   - New plan: [if changed]
   - Reason: [scope increase / discovery / blockers]
   - Approval: [stakeholder sign-off needed?]

4. **Knowledge sharing:**
   - Topic: [coordination systems / testing patterns / etc.]
   - Who will share: [expert on topic]
   - When: [separate sync / documentation / code review]
   - Audience: [all tracks / specific track]

**Example closing** (1 min):

> **Tech Lead**: "Great progress across all tracks. Let me recap action items:
>
> **BLOCKER RESOLUTION:**
> - Track B: Clarify hierarchy context API with Track A by EOD today (10 min sync)
> - Action item owner: Track B Lead
> - Check-in: Standup tomorrow
>
> **DEPENDENCY DELIVERABLES:**
> - Track A: Finalize add_component API (Point object format) by EOD tomorrow
> - Verification: PR merged and documented
>
> **TIMELINE:**
> - Still tracking to 2-week delivery
> - No scope creep flagged - great discipline
> - If Track B finds coordinate issues, let's escalate immediately
>
> **KNOWLEDGE SHARING:**
> - Track B: Send the coordinate system docs to Track C by EOD tomorrow
> - Format: Markdown with examples
>
> Let's keep this pace. Standup again tomorrow 10am. Good luck!"

---

## Daily Focus Questions

### Questions to Answer Every Day

**Shared by all tracks:**

1. **Are we on track for 2-week delivery?**
   - What % complete should we be today?
   - Are we at/ahead/behind pace?
   - What would get us back on track?

   **Pace target:**
   - End of Week 1 (5 days): 40% complete
   - End of Week 2 (10 days): 100% complete
   - **Daily target**: 10% progress

2. **Are all tests passing?**
   - What's our test coverage percentage?
   - Are any tests skipped/broken?
   - Does test coverage meet minimum (>90%)?

   **Test dashboard:**
   ```bash
   # Run before standup
   uv run pytest tests/ -v --tb=short 2>&1 | \
     tee /tmp/test_report.txt | tail -20

   echo "Test Coverage:"
   uv run pytest --cov=kicad_sch_api --cov-report=term-missing | \
     grep TOTAL
   ```

3. **Are there blockers preventing progress?**
   - What's stopping us from moving forward?
   - Is it technical / dependency / resource?
   - Who can help unblock?
   - What's the ETA to unblock?

   **Blocker assessment matrix:**
   ```
   SEVERITY LEVELS:
   🔴 CRITICAL - Stops entire track, needs immediate action
   🟠 HIGH    - Slows progress significantly, needs today
   🟡 MEDIUM  - Impacts some tasks, plan workaround
   🟢 LOW     - Minor inconvenience, can wait

   UNBLOCK TIMELINE:
   ASAP (< 1 hour)  - Show stopper, needs immediate action
   Today (< 4 hours) - Should be resolved same day
   Tomorrow         - Can wait until next day
   ```

4. **Do we need to adjust timeline/scope?**
   - What was originally planned for today?
   - What actually happened?
   - What's the gap?
   - Can we catch up tomorrow?

   **Timeline adjustment triggers:**
   - More than 1 day behind schedule → discuss with Product Owner
   - Scope creep > 10% → escalate immediately
   - Test coverage drops below 85% → fix before proceeding
   - Critical blocker > 4 hours → escalate

---

## Weekly Retrospective

### Friday Retrospective Meeting (30 minutes)

**Time**: Friday 3:00 PM - 3:30 PM
**Participants**: All tracks + Product Owner + Tech Lead

#### Part 1: What Went Well (10 minutes)

**Each track shares 2-3 wins:**

```
TEMPLATE:
"This week we [accomplishment]. This was good because [impact].
It helped us [future benefit]."

EXAMPLES:
- "We finished pin rotation transformation. This was good because
  it's a critical foundation for all coordinate calculations.
  It will let us move faster on connectivity detection."

- "We discovered the coordinate system issue early.
  This prevented a catastrophic bug later in integration.
  It forced us to document coordinate systems deeply."

- "We paired on the tool signature design. This was good because
  we caught dependency issues before implementation."
```

**Track A wins:**
- [ ] Example: Completed core server framework
- [ ] Example: Established error handling patterns
- [ ] Example: Documented API design decisions

**Track B wins:**
- [ ] Example: Validated pin transformation math
- [ ] Example: Created pin rotation test suite
- [ ] Example: Discovered coordinate system bug early

**Track C wins:**
- [ ] Example: Created example circuits
- [ ] Example: Documented pattern library
- [ ] Example: Validated patterns against real KiCAD

#### Part 2: What Could Improve (10 minutes)

**Each track identifies 2-3 improvement areas:**

```
TEMPLATE:
"We struggled with [challenge]. Next time we'll [action].
This will help because [benefit]."

EXAMPLES:
- "We struggled with unclear API contracts between tracks.
  Next time we'll write RFCs before implementation.
  This will help because we'll catch conflicts early."

- "We didn't communicate blockers quickly enough.
  Next time we'll escalate blockers within 30 minutes.
  This will help because we can unblock each other faster."

- "Our test organization was scattered.
  Next time we'll structure tests by feature area.
  This will help because tests are easier to find and maintain."
```

**Improvement areas to explore:**

- **Communication**: How well did tracks communicate?
- **Planning**: Were estimates accurate?
- **Testing**: Are tests sufficient?
- **Documentation**: Is code self-documenting?
- **Blockers**: Were issues surfaced early?
- **Collaboration**: Did pairs work well?
- **Tools**: Are our development tools adequate?

#### Part 3: Adjustments for Next Week (10 minutes)

**Product Owner + Tech Lead: Make decisions**

```
DECISION TEMPLATE:
ISSUE: [What we're adjusting]
CURRENT STATE: [How it is now]
CHANGE: [What we're doing differently]
RESPONSIBLE: [Who owns the change]
VALIDATION: [How we'll measure if it works]
START DATE: [When does this take effect]

EXAMPLES:

ISSUE: Unclear API contracts between tracks
CURRENT STATE: Track leads negotiate API details in standup
CHANGE: Create RFC documents before implementation
RESPONSIBLE: Tech Lead (creates template, ensures adoption)
VALIDATION: All tracks use RFC before major feature
START DATE: Monday

ISSUE: Blockers not surfaced quickly
CURRENT STATE: Blockers mentioned in standup
CHANGE: Blockers escalated within 30 min of discovery
RESPONSIBLE: All tracks (own their blockers)
VALIDATION: Zero blockers hidden until standup
START DATE: Monday

ISSUE: Test coverage dropping
CURRENT STATE: Some tests skipped, coverage 78%
CHANGE: No skipped tests, all PRs must maintain >90%
RESPONSIBLE: Tech Lead (enforce in code review)
VALIDATION: pytest-cov shows >90% before merge
START DATE: Immediately
```

**Questions to answer:**

1. **Process changes**: How should we run standups differently?
2. **Communication changes**: How should we communicate better?
3. **Tool changes**: Do we need different tools/processes?
4. **Pace changes**: Should we speed up or slow down?
5. **Scope changes**: Should we adjust what we're building?

**Document decisions:**

- [ ] Decision made
- [ ] Owner assigned
- [ ] Validation method defined
- [ ] Start date set
- [ ] Will be mentioned in Monday standup kickoff

---

## Decision Trees

### Blocker Response Decision Tree

```
BLOCKER DISCOVERED
       │
       ├─ Is it urgent (stops progress now)?
       │  │
       │  ├─ YES → Can it be unblocked in < 1 hour?
       │  │  │
       │  │  ├─ YES → Unblock immediately
       │  │  │       - Assign owner
       │  │  │       - Set 30-min timer
       │  │  │       - Report in standup
       │  │  │
       │  │  └─ NO → Escalate immediately
       │  │          - Notify Tech Lead + Product Owner
       │  │          - Create emergency fix plan
       │  │          - Reassess scope/timeline
       │  │
       │  └─ NO → Can it wait until standup?
       │     │
       │     ├─ YES → Document for standup discussion
       │     │       - Create ticket with details
       │     │       - Identify workaround if available
       │     │       - Plan investigation path
       │     │
       │     └─ NO → Discuss in next sync
       │             - Schedule 15-min call with affected tracks
       │             - Come prepared with context
       │             - Identify next steps
       │
       └─ Has this been blocking us > 4 hours?
          │
          ├─ YES → Escalate to Product Owner for decision
          │       - Is this a timeline/scope issue?
          │       - Can we reduce scope to unblock?
          │       - Do we need more resources?
          │
          └─ NO → Standard blocker resolution process
```

### Test Coverage Drop Decision Tree

```
TEST COVERAGE METRIC CHECKED
       │
       ├─ Coverage > 90%?
       │  │
       │  └─ YES → ✓ Continue
       │
       └─ Coverage 85-90%?
          │
          ├─ Downward trend?
          │  │
          │  ├─ YES → Discuss in standup
          │  │        - What caused drop?
          │  │        - Add tests to restore coverage
          │  │        - PR blocked until restored
          │  │
          │  └─ NO → ✓ Continue (temporary blip)
          │
          └─ Coverage < 85%?
             │
             ├─ Who caused the drop?
             │  │
             │  ├─ Intentional (new code without tests)?
             │  │  │
             │  │  └─ → STOP: Add tests before merge
             │  │      - Violates project standard
             │  │      - Cannot proceed until fixed
             │  │      - Code review must catch this
             │  │
             │  └─ Accidental (removed tests)?
             │     │
             │     └─ → ESCALATE: Why were tests removed?
             │         - Check git history
             │         - Restore deleted tests
             │         - Update documentation
```

### Timeline Slip Decision Tree

```
COMPARING PROGRESS TO PLAN
       │
       ├─ Ahead of schedule?
       │  │
       │  └─ YES → ✓ Great! Document what went well
       │          - Share learnings with other tracks
       │          - Don't add scope (resist scope creep)
       │
       ├─ On schedule?
       │  │
       │  └─ YES → ✓ Continue at current pace
       │
       └─ Behind schedule?
          │
          ├─ How far behind?
          │  │
          │  ├─ < 1 day (< 10%)?
          │  │  │
          │  │  └─ → Can we catch up?
          │  │      If YES: Accelerate, no escalation needed
          │  │      If NO: Discuss in standup, plan recovery
          │  │
          │  ├─ 1-2 days (10-20%)?
          │  │  │
          │  │  └─ → Escalate to Tech Lead
          │  │      - Review actual vs estimated work
          │  │      - Identify what caused slip
          │  │      - Adjust estimates for remaining work
          │  │      - Plan recovery or scope reduction
          │  │
          │  └─ > 2 days (> 20%)?
          │     │
          │     └─ → Escalate to Product Owner
          │         - Major timeline adjustment needed
          │         - Scope cuts likely required
          │         - Resource reallocation considered
          │         - Stakeholder communication needed
          │
          └─ What caused the slip?
             │
             ├─ Underestimated complexity?
             │  → Adjust remaining estimates upward
             │
             ├─ Unexpected technical issue?
             │  → Document learning, share with team
             │
             ├─ Scope creep?
             │  → Remove added scope, return to plan
             │
             ├─ External dependency delay?
             │  → Work on highest-priority unblocked tasks
             │
             └─ Resource constraints?
                → Escalate for team reallocation
```

### Scope Adjustment Decision Tree

```
NEW WORK REQUESTED
       │
       ├─ Is it essential for v1 launch?
       │  │
       │  ├─ YES → Can we complete it in remaining time?
       │  │  │
       │  │  ├─ YES → Add to plan (estimate effort)
       │  │  │       - Adjust timeline or reduce other work
       │  │  │       - Get stakeholder approval
       │  │  │
       │  │  └─ NO → Defer to v1.1
       │  │         - Document as future feature
       │  │         - Create backlog ticket
       │  │
       │  └─ NO → Defer to v1.1
       │         - Document as nice-to-have
       │         - Keep focused on v1 essentials
       │
       └─ Current workload accommodation?
          │
          ├─ Can we absorb it?
          │  │
          │  └─ YES → Add with owner assigned
          │
          └─ NO → Reduce current work
             │
             ├─ Which current work can be deferred?
             │  │
             │  └─ Identify lowest-priority item
             │     - Move to v1.1 backlog
             │     - Announce change in standup
             │     - Update timeline
```

---

## Escalation Procedures

### When & How to Escalate

#### Level 1: Standup Escalation (Yellow Flag)

**When**: Issue surfaced in daily standup
**Action**:
- Present clearly in standup (60 seconds max)
- Tech Lead discusses resolution path
- Owner assigned
- ETA to resolution stated

**Example:**
> "We hit a coordinate system edge case with rotated pins.
> Track B is investigating. ETA 2 hours.
> If not fixed by EOD, we escalate to Level 2."

---

#### Level 2: Tech Lead Escalation (Orange Flag)

**When**:
- Blocker lasting > 4 hours
- Test coverage drops > 10%
- Architecture decision needed
- Timeline impact > 1 day

**How to escalate:**
1. Notify Tech Lead immediately (don't wait for standup)
2. Provide context: problem, impact, what's been tried
3. Suggest 2-3 solution options
4. Request decision

**Escalation template (email/Slack):**

```
TO: Tech Lead
SUBJECT: [ESCALATION] [Track X] [Brief issue]

PROBLEM:
[What's wrong in 1-2 sentences]

IMPACT:
- Timeline impact: +X hours/days
- Scope impact: affects Y feature
- Quality impact: Z tests failing

CONTEXT:
- Started at: [time]
- Attempted solutions: [what's been tried]
- Blocker reason: [why it's stuck]

OPTIONS:
1. [Option A - pros/cons]
2. [Option B - pros/cons]
3. [Option C - pros/cons]

RECOMMENDATION:
Option [X] because [rationale]

REQUEST:
Decision needed by: [time]
```

---

#### Level 3: Product Owner Escalation (Red Flag)

**When**:
- Timeline impact > 2 days
- Major scope change needed
- Architectural redesign required
- External dependency failure
- Resource conflict

**How to escalate:**
1. Notify Product Owner & Tech Lead together
2. Prepare timeline/scope impact analysis
3. Come with 2-3 resolution scenarios
4. Request explicit decision

**Escalation template:**

```
TO: Product Owner, Tech Lead
SUBJECT: [ESCALATION] [Track] Timeline/Scope Impact

EXECUTIVE SUMMARY:
[1-sentence summary of issue]

ORIGINAL COMMITMENT:
- Feature: [what we said we'd build]
- Timeline: [when we said it would be done]
- Quality bar: [what success looks like]

CURRENT SITUATION:
- Issue discovered: [when]
- Impact: +[X] days or -[Y] features
- Risk if unresolved: [what breaks]

SCENARIOS:

SCENARIO A: [Option 1]
- Timeline adjustment: [+X days or -X days]
- Scope impact: [what changes]
- Resource impact: [what's needed]
- Recommendation: [yes/no/maybe]

SCENARIO B: [Option 2]
- Timeline adjustment: [+X days or -X days]
- Scope impact: [what changes]
- Resource impact: [what's needed]
- Recommendation: [yes/no/maybe]

RECOMMENDATION:
Proceed with Scenario [X] because [rationale]

DECISION NEEDED:
By [time] so we can [next step]
```

---

#### Emergency Escalation (🚨 Critical)

**When**: Issue prevents ANY progress on v1

**Immediate actions:**
1. Notify Tech Lead directly (call, not email)
2. Assemble affected track leads
3. 15-minute emergency sync to unblock
4. If still blocked after 15 min → notify Product Owner

**Emergency sync agenda:**

```
EMERGENCY UNBLOCK SYNC (15 minutes)
=====================================

0:00 - Problem statement (1 min)
0:01 - What's been attempted (2 min)
0:03 - Brainstorm solutions (8 min)
0:11 - Assign owner & deadline (2 min)
0:13 - Dismiss (document via email after)
```

---

### Escalation Decision Matrix

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ ISSUE SEVERITY      │ TIME TO      │ ESCALATE TO  │ TIMELINE     │
│                     │ ESCALATE     │              │ IMPACT       │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Minor (cosmetic)    │ Next standup │ None         │ No impact    │
│ Low (workaround OK) │ Next standup │ Tech Lead    │ < 4 hours    │
│ Medium (slows work) │ Same day     │ Tech Lead    │ 4-8 hours    │
│ High (blocks track) │ ASAP (30min) │ Tech Lead    │ 1+ day       │
│ Critical (v1 risk)  │ 🚨 IMMEDIATE │ Both + PO    │ 2+ days      │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Metrics Dashboard

### Daily Metrics Checklist

**Run before standup to populate dashboard:**

```bash
#!/bin/bash
# Save as .dev/metrics-dashboard.sh
# Run: bash .dev/metrics-dashboard.sh

echo "=== KICAD-SCH-API METRICS DASHBOARD ==="
echo "Generated: $(date)"
echo ""

# TEST METRICS
echo "TEST METRICS:"
echo "─────────────"
TEST_COUNT=$(uv run pytest --collect-only -q 2>/dev/null | tail -1)
echo "Total tests: $TEST_COUNT"

uv run pytest tests/ -q --tb=no 2>&1 | tail -1
echo ""

COVERAGE=$(uv run pytest --cov=kicad_sch_api --cov-report=term-missing 2>/dev/null | grep TOTAL)
echo "Coverage: $COVERAGE"
echo ""

# CODE METRICS
echo "CODE METRICS:"
echo "─────────────"
echo "Lines of code:"
find kicad_sch_api -name "*.py" -type f | xargs wc -l | tail -1

echo ""
echo "Last 5 commits:"
git log --oneline -5

echo ""
echo "Current branches:"
git branch -v

echo ""
echo "Uncommitted changes:"
git status -s

# TRACK METRICS
echo ""
echo "TRACK METRICS:"
echo "──────────────"

echo ""
echo "Track A (Server) commits:"
git log --oneline -5 --grep="tool\|server\|mcp"

echo ""
echo "Track B (Connectivity) commits:"
git log --oneline -5 --grep="wire\|pin\|connect"

echo ""
echo "Track C (Pattern) commits:"
git log --oneline -5 --grep="pattern\|example\|circuit"
```

### Weekly Metrics Report

**Friday EOD metrics snapshot:**

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Test Count** | 150+ | ? | |
| **Test Coverage** | >90% | ? | |
| **Type Check** | Strict ✓ | ? | |
| **Tools Implemented** | N/18 | ? | |
| **Pin Tests Passing** | 11/11 | ? | |
| **Reference Validations** | 8/8 | ? | |
| **Example Circuits** | 5+ | ? | |
| **Documentation Pages** | 3+ | ? | |
| **Days Elapsed** | 5/10 | ? | |
| **Timeline Pace** | 50% | ? | |
| **Blockers Resolved** | 100% same-day | ? | |
| **Scope Creep** | 0% | ? | |

---

## Post-Standup Actions

### Immediate (Next 30 minutes)

- [ ] Tech Lead sends action items email to team
- [ ] Blocked track lead initiates unblocking conversation
- [ ] Each track updates their Kanban board
- [ ] Cross-track dependencies confirmed in async tools

### Same Day

- [ ] Dependency deliverables tracked (is it on pace?)
- [ ] If blocker hit, escalate within 30 min per decision tree
- [ ] Documentation updated with standup decisions
- [ ] Any timeline/scope changes communicated to stakeholders

### EOD Summary

**Each track lead sends 1-minute EOD update:**

```
TRACK [X] EOD UPDATE
====================

COMPLETED TODAY:
- [Task 1]: [commitment kept? yes/no]
- [Task 2]: [commitment kept? yes/no]

PROGRESS TO PLAN:
- Scheduled: [X tasks]
- Completed: [Y tasks]
- On track: yes/no

BLOCKERS:
- [Blocker 1]: [still blocked? or unblocked?]

TOMORROW'S FOCUS:
- [Task for tomorrow]

HELP NEEDED:
- [Ask from other tracks]
```

### Weekly (Friday EOD)

- [ ] Metrics dashboard snapshot captured
- [ ] Retrospective scheduled for Friday 3pm
- [ ] Next week's plan reviewed for feasibility
- [ ] Lessons learned documented

---

## Common Standup Mistakes to Avoid

### ❌ Don't

```
- Talk for more than your time limit (3 min per track)
- Discuss solutions in standup (that's what side channels are for)
- Bring up new blockers for first time (should be pre-signaled)
- Hide blockers hoping to solve them yourself (escalate early)
- Commit to unrealistic timelines (be honest about estimates)
- Skip metrics preparation (numbers tell the story)
- Ignore decision tree guidance (it exists for a reason)
```

### ✓ Do

```
- Prepare talking points (1-2 min prep before standup)
- Bring metrics/data (not guesses)
- State blockers clearly with impact assessment
- Ask specific questions to other tracks
- Commit only to what you can deliver
- Escalate early (within 30 min of blocker discovery)
- Follow decision trees (they remove ambiguity)
- Document decisions immediately after standup
- Give credit to teammates in wins
```

---

## Quick Reference: Commands & Scripts

### Pre-Standup Checklist Script

```bash
# Save as: .dev/standup-checklist.sh
# Run: bash .dev/standup-checklist.sh

#!/bin/bash
echo "PRE-STANDUP CHECKLIST - $(date +%H:%M)"
echo "========================================"
echo ""

# 1. Test Status
echo "1. TEST STATUS:"
uv run pytest tests/ -q --tb=no 2>&1 | tail -3
echo ""

# 2. Coverage
echo "2. TEST COVERAGE:"
uv run pytest --cov=kicad_sch_api --cov-report=term-missing tests/ 2>&1 | grep TOTAL
echo ""

# 3. Recent work
echo "3. YOUR RECENT COMMITS:"
git log --oneline -5 --author="$(git config user.name)"
echo ""

# 4. Blockers check
echo "4. BLOCKING ISSUES:"
grep -r "FIXME\|BLOCKER\|URGENT" kicad_sch_api --include="*.py" | head -5 || echo "None found"
echo ""

# 5. Uncommitted work
echo "5. UNCOMMITTED CHANGES:"
git status -s | wc -l
echo "files changed (run 'git status' for details)"
echo ""

echo "Ready for standup! ✓"
```

### Metrics Dashboard Script

```bash
# Save as: .dev/metrics.sh
# Run: bash .dev/metrics.sh

#!/bin/bash
echo "METRICS DASHBOARD"
echo "================="
echo "Time: $(date)"
echo ""
echo "TESTS:"
uv run pytest --collect-only -q 2>&1 | tail -1
uv run pytest tests/ -v --tb=no 2>&1 | grep -E "passed|failed|error" | tail -1
echo ""
echo "COVERAGE:"
uv run pytest --cov=kicad_sch_api --cov-report=term-missing 2>&1 | grep TOTAL
echo ""
echo "CODE:"
echo "Lines: $(find kicad_sch_api -name '*.py' | xargs wc -l | tail -1 | awk '{print $1}')"
echo ""
echo "GIT:"
git log --oneline -1
```

### Blocker Escalation Template

Save as `.dev/escalate-blocker.md`:

```markdown
# BLOCKER ESCALATION TEMPLATE

**Issue**:
**Severity**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
**Found at**: [time]
**Duration**: [how long blocked]

## Problem
[Describe the issue clearly]

## Impact
- Track: [A/B/C]
- Timeline impact: [+X hours/days]
- Feature impact: [what's blocked]

## What We've Tried
- [Attempted solution 1]
- [Attempted solution 2]

## Options
1. [Option A with pros/cons]
2. [Option B with pros/cons]

## Recommendation
[Which option and why]

## Decision Needed By
[Time]
```

---

## Emergency Contact & Escalation Path

```
ESCALATION PATH
═══════════════

Developer → 30 min timer starts
   ↓
Track Lead → Collects context, decides escalation level
   ↓
Tech Lead → Resolves L2 blockers, may escalate to L3
   ↓
Product Owner → Makes L3 decisions (timeline/scope)
   ↓
🚨 If 4 hours blocked and PO unavailable → reduce scope
```

---

## Closing Notes

### Standup Philosophy

This standup runbook is designed around **three core principles**:

1. **Transparency**: Know where we actually are, not where we hope to be
2. **Accountability**: Clear owners, deadlines, and responsibility
3. **Unblocking**: Focus on removing obstacles to progress

### Key Success Factors

- **15 minutes or less**: Respect everyone's time
- **Prepared metrics**: Data-driven, not opinion-driven
- **Clear decisions**: Use decision trees, don't debate in standup
- **Fast escalation**: Blockers surfaced immediately, not hidden
- **Document everything**: Every decision has a paper trail

### Remember

> "The best standups are the boring ones where everything is going well and we're on pace to deliver. Drama means we've already waited too long to escalate something."

---

**Document Version**: 1.0
**Last Updated**: 2025-11-06
**Next Review**: Week 1 retrospective (Friday EOD)
**Owner**: Tech Lead
**Distribution**: All development tracks + Product Owner
