# Daily Standup Agenda Template

**Print this and post it in your team meeting space**

---

## DAILY STANDUP: MCP Pin Connection Implementation

**Project**: kicad-sch-api v1.0 Release
**Duration**: 15 minutes (09:55-10:10 AM)
**Participants**: Track A, Track B, Track C Leads + Tech Lead
**Facilitator**: Tech Lead

---

## PRE-STANDUP (5 minutes before: 09:55 AM)

**All participants:**
- [ ] Run metrics collection: `bash .dev/standup-checklist.sh`
- [ ] Review yesterday's action items
- [ ] Prepare 3-minute talking points
- [ ] Note any blockers

---

## STANDUP FLOW

### OPENING (10:00 - 10:00) — 0 minutes

**Tech Lead opens with:**

```
"Good morning. We're on Day __ of 14, targeting 10% progress
per day. Let's go through status. Track A first. Three minutes."

START TIMER: 3 minutes for Track A
```

---

### TRACK A UPDATE (10:00 - 10:03) — 3 minutes

**Presenter**: Track A Lead

**Use this template (speak for exactly 3 minutes):**

```
COMPLETED YESTERDAY: [Task A], [Task B], [Task C]
  Example: "Finished server initialization and error handling patterns"

IN PROGRESS: [Task X], about [60%] done, expect done [today/tomorrow]
  Example: "Working on add_component tool, 60% done, complete by EOD"

BLOCKERS: [None / Description of issue]
  Example: "No blockers currently"
  OR: "Blocker: Type checking failing on Pydantic models.
       We're investigating. ETA 1 hour."

ASKS: [Specific request for other tracks]
  Example: "Track B: Need connectivity API signature when ready"
  OR: "None currently"

METRICS:
  - Tools implemented: __/18 (__%)
  - Test coverage: __%
  - Type checking: ☐ PASS ☐ FAIL
```

**STOP at 10:03 - Tech Lead calls time**

---

### TRACK B UPDATE (10:03 - 10:06) — 3 minutes

**Presenter**: Track B Lead

**Use this template:**

```
COMPLETED YESTERDAY: [Task A], [Task B], [Task C]
  Example: "Pin rotation math validated, reference tests set up"

IN PROGRESS: [Task X], about [70%] done, expect done [timing]
  Example: "Implementing wire connectivity, 70% done, complete by EOD"

BLOCKERS: [None / Description]
  Example: "Blocker: Component position API signature changed.
           Waiting on Track A to finalize. No impact yet."

ASKS: [Specific request]
  Example: "Track A: Can you confirm component API signature by EOD?"

METRICS:
  - Pin tests: __/11 passing
  - Reference validations: __/8 passing
  - Coverage: __%
  - Y-axis transformation: ☐ WORKING ☐ DEBUGGING
```

**STOP at 10:06 - Tech Lead calls time**

---

### TRACK C UPDATE (10:06 - 10:09) — 3 minutes

**Presenter**: Track C Lead

**Use this template:**

```
COMPLETED YESTERDAY: [Task A], [Task B], [Task C]
  Example: "Created voltage divider and LED circuit examples"

IN PROGRESS: [Task X], about [50%] done, expect done [timing]
  Example: "Building pattern library, 50% done, complete by Thursday"

BLOCKERS: [None / Description]
  Example: "Blocker: Component APIs still evolving.
           Need stable signatures. Track A ETA?"

ASKS: [Specific request]
  Example: "Track A: Need component creation API finalized.
           Track B: Need wire connectivity for pattern validation."

METRICS:
  - Patterns: __/6 implemented
  - Examples: __/5 created
  - Coverage: __%
  - Tests: __/__ passing
```

**STOP at 10:09 - Tech Lead calls time**

---

### CROSS-TRACK SYNC (10:09 - 10:12) — 3 minutes

**Facilitator**: Tech Lead

**Tech Lead asks (keep answers SHORT):**

1. **"Any critical dependencies blocking anyone?"**
   - Track leads answer YES/NO only
   - If YES: 30-second explanation + owner

2. **"Are we on pace for 2-week delivery?"**
   - Current: __% complete, target: __% (10 × days elapsed)
   - Status: ☐ ON TRACK ☐ BEHIND ☐ AHEAD

3. **"Anything that needs cross-team coordination?"**
   - Doc it briefly, decide on follow-up sync time if needed

4. **"Any escalations needed?"**
   - Any blockers > 4 hours?
   - Any coverage drops?
   - Any type check failures?

**Tech Lead summarizes:**
```
"Key dependency: [X from Track Y needed by Z].
Owner: [name]. Check-in: [time].

We're on pace. Keep focused on deliverables.
Let's go get this done."
```

---

### ACTION ITEMS & CLOSING (10:12 - 10:15) — 3 minutes

**Tech Lead assigns and closes with:**

```
ACTION ITEMS:

1. [Owner]: [Clear task] by [deadline]
   Verification: [how we'll know it's done]

2. [Owner]: [Clear task] by [deadline]
   Verification: [how we'll know it's done]

3. [Owner]: [Clear task] by [deadline]
   Verification: [how we'll know it's done]

TIMELINE CHECK:
  Days elapsed: __ / 14
  Target progress: __% (10% per day)
  Current progress: __%
  Status: ☐ ON TRACK ☐ BEHIND

SCOPE CHECK:
  Unplanned work added: ___
  Scope creep: ___% (should be 0%)

Next standup: Tomorrow 10:00 AM

Go deliver! ✓
```

---

## STANDUP GROUND RULES

### Time Disciplines

```
✓ Each track gets exactly 3 minutes
✓ Tech lead times with stopwatch
✓ Cross-sync gets exactly 3 minutes
✓ Action items get exactly 3 minutes
✓ Total: 15 minutes MAX

If you need more time → schedule side sync
```

### Communication Style

```
✓ Speak clearly and concisely
✓ State facts with metrics, not opinions
✓ "We're behind schedule" not "I think maybe we might be late"
✓ Ask specific questions, not vague ones
✓ Document decisions immediately after
✗ Don't debate solutions (that's for side syncs)
✗ Don't dive into technical details
✗ Don't make excuses (focus on fixes)
```

### Escalation During Standup

```
IF BLOCKER DISCOVERED:
  1. Track lead states it clearly
  2. Tech lead assesses severity
  3. If critical (blocking all work) → emergency sync after standup
  4. If high (slows progress) → Tech lead schedules sync today
  5. If medium → note for next standup
```

---

## WHAT TO BRING TO STANDUP

### Physical/Digital Items

```
☐ Today's date and day number (e.g., "Day 7 of 14")
☐ Metrics from: bash .dev/standup-checklist.sh
☐ List of completed tasks (with commit hashes)
☐ Today's planned tasks
☐ Any blockers (with start time)
☐ Last standup action items (marked done/in-progress)
```

### Talking Points (Prepared)

```
3-minute script (write this out, time it):

"Yesterday we [did A, B, C]. Today we're [doing X, Y, Z],
expect done [timing]. [Blocker status]. We need [specific help]."

Practice this until you can say it in exactly 3 minutes.
```

---

## SAMPLE STANDUPS

### Good Standup (Track A - 2:45 minutes)

```
TRACK A: Server & Framework
─────────────────────────────

"Yesterday we finished the server initialization
(commit abc123) and established error handling patterns (def456).

Today we're working on the Pydantic models for tool inputs
and outputs. We're about 70% done, expect complete by EOD today.

No blockers currently. Everything's moving smoothly.

We need Track B to confirm the component position format
(Point object vs tuple) so we can lock in our tool signatures.
Can we get that by end of day?

Metrics: 6 of 18 tools implemented, 92% test coverage, type
checking passing strict mode. We're on pace."
```

**Analysis: GOOD**
- ✓ Exactly 3 minutes
- ✓ Clear status with percentages
- ✓ Specific ask (format confirmation)
- ✓ Metrics shared
- ✓ No blocker excuses

---

### Problem Standup (Track B - 3:30 minutes)

```
TRACK B: Connectivity
─────────────────────

"So yesterday we tried to implement the pin rotation
transformation, but we hit this issue where the Y-axis
inversion wasn't working right. We looked at it for like
four hours and couldn't figure it out. We think maybe the
coordinate system is wrong? Not sure.

Today we're going to try a different approach. Maybe we need
to use absolute coordinates instead of relative ones? We'll
see. Probably takes the rest of the week to debug.

We kind of need Track A to provide better documentation on
how components work, but they're probably busy.

Anyway, we're at like 60% I guess? Tests are passing mostly.
We're probably okay."
```

**Analysis: PROBLEMS**
- ✗ Ran way over 3 minutes (rambling)
- ✗ Vague problem description (what EXACTLY is broken?)
- ✗ Waited 4 hours before escalating (should have been 30 min)
- ✗ Weak ask ("probably busy") - need specific help
- ✗ No metrics (just "I guess")
- ✗ No clear plan to fix
- ✗ Guessing instead of stating facts

---

### Escalation Standup (Track C - 2:50 minutes)

```
TRACK C: Patterns
─────────────────

"Yesterday we created the voltage divider and LED circuit
examples. Both validated cleanly against KiCAD.

Today we're implementing the add_decoupling_caps pattern.
We're 40% done, expect completion by EOD tomorrow.

BLOCKER: We've discovered that the component reference
format changed this morning. Our patterns are generating
invalid references. We're blocked until Track A clarifies
the new format. Started at 10:15 AM today.

We need Track A to: confirm the reference format change,
provide migration guide for existing patterns. ETA?

Metrics: 1 of 6 patterns complete (the ones without
reference issues), 88% coverage, 2 of 5 examples created.
Below our daily pace due to blocker."
```

**Analysis: GOOD ESCALATION**
- ✓ Clear blocker statement (STARTED AT TIME, DURATION)
- ✓ Specific impact (invalid references)
- ✓ Specific ask (confirmation + migration guide)
- ✓ Metrics show impact
- ✓ Honest about pace impact
- ✓ Owner will see this needs immediate action

---

## AFTER STANDUP CHECKLIST

**All participants (15 minutes after standup):**

```
☐ Update your Kanban board with today's tasks
☐ If you have action item: confirm deadline with owner
☐ If you depend on another track: message them asking ETA
☐ If you're blocked: start highest-priority unblocked work
☐ Send EOD status update to team (1 message per track)

Track Lead (after standup):
☐ Create GitHub issue for any action items
☐ Tag owners + set deadlines
☐ Send email summary to Product Owner if blockers
☐ Update project dashboard with metrics
☐ Schedule any follow-up syncs (if needed)
```

---

## METRICS SUMMARY (For Your Wall)

Print and update daily:

```
╔════════════════════════════════════════════════════════════╗
║      MCP PIN CONNECTION - DAILY STANDUP DASHBOARD          ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  DATE: ____________    DAY __ OF 14    PACE: 10% / day   ║
║                                                            ║
║  PROGRESS:                                                 ║
║    Target today:   __%                                     ║
║    Current:        __%                                     ║
║    Status:    ☐ ON TRACK   ☐ BEHIND   ☐ AHEAD           ║
║                                                            ║
║  TRACK STATUS:                                             ║
║    Track A:  [████░░░░] __% (Server)                      ║
║    Track B:  [████░░░░] __% (Connectivity)                ║
║    Track C:  [████░░░░] __% (Patterns)                    ║
║                                                            ║
║  QUALITY:                                                  ║
║    Tests:     __ / __ passing  (__%)                       ║
║    Coverage:  __%  (target >90%)                           ║
║    Type Check: ☐ PASS  ☐ FAIL                             ║
║                                                            ║
║  BLOCKERS:                                                 ║
║    Critical:  ___ active                                  ║
║    Urgent:    ___ active                                  ║
║                                                            ║
║  NEXT STANDUP: Tomorrow 10:00 AM                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## COMMON MISTAKES & HOW TO AVOID THEM

### ❌ Mistake: Going Over 3 Minutes

**Solution**: Time your standup response. Practice it beforehand.

```
SCRIPT: "[Completed]. [In progress + %]. [Blocker status].
         [Asks]. [Metrics]."

TIME IT: Should take 2-3 minutes exactly.
        If longer → cut out details (save for side sync)
```

### ❌ Mistake: Vague Problem Description

**Solution**: State EXACTLY what's wrong + impact.

```
❌ "I think we might have a coordinate issue"
✓ "Y-axis transformation failing on 90° rotation.
   Pin positions inverted. Blocks wire routing implementation.
   Started 2 hours ago."
```

### ❌ Mistake: Vague Asks

**Solution**: Ask SPECIFICALLY for help.

```
❌ "We might need some help from Track B"
✓ "Track B: We need the component position API signature
   (Point object vs tuple) confirmed by EOD so we can
   finalize tool specifications. Can you do that?"
```

### ❌ Mistake: No Metrics

**Solution**: Bring numbers.

```
❌ "We're making good progress"
✓ "Tools: 8 of 18 implemented (44%), coverage 91%,
   type checking passing, on pace for day target."
```

### ❌ Mistake: Waiting Too Long to Escalate

**Solution**: Escalate after 30 minutes of being blocked.

```
Blocked at: 09:30
Escalate at: 10:00 (30 min later)
Don't wait for standup if it's urgent
```

### ❌ Mistake: Solving Issues in Standup

**Solution**: Use standup to identify, not solve.

```
❌ "Let's discuss the coordinate system fix"
✓ "We hit a blocker with coordinates. Tech Lead, can we
   schedule a 15-minute sync after standup?"

→ Solve in separate meeting, report results tomorrow
```

---

## DECISION MATRIX

**Tech Lead uses this to make fast decisions during standup:**

```
ISSUE PRESENTED | DECISION | ACTION
────────────────┼──────────┼────────────────────────────────
Blocker | Assess severity | If critical → emergency sync now
        | (1-4 min discussion) | If high → sync after standup
        |  | If medium → note for next sync
────────────────┼──────────┼────────────────────────────────
Behind schedule | Compare to target | If < 1 day slip → no change
        | Ask if it catches up | If > 1 day → reduce scope
        | today/tomorrow | or escalate to PO
────────────────┼──────────┼────────────────────────────────
Coverage drop | Check trend | If > 5% drop → PR blocked
        | (Should we add tests?) | until restored
────────────────┼──────────┼────────────────────────────────
Dependency gap | Identify owner | Owner commits to ETA
        | Set ETA | Note as action item
        | | Follow up next standup
────────────────┼──────────┼────────────────────────────────
Scope creep | Calculate % added | If > 10% → defer to v1.1
        | (is there time?) | or cut something
```

---

## STANDUP SUCCESS CRITERIA

**At end of standup, Tech Lead should be able to answer:**

```
☐ Do I know what each track accomplished yesterday?
☐ Do I know what each track is doing today?
☐ Are there any blockers preventing progress?
☐ Are we on pace for delivery?
☐ Are there any quality issues (tests/coverage)?
☐ Do I have clear action items assigned with deadlines?
☐ Do we have clear next steps?

If you answered YES to all 7 → successful standup!
If you answered NO to any → need follow-up conversation.
```

---

**PRINT THIS AND POST IT ABOVE THE MEETING TABLE**
