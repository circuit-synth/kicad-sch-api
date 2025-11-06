# Daily Standup Quick Reference Card

**Print this and keep it at your desk during the 2-week sprint.**

---

## 5 Minutes Before Standup

```
☐ Run: bash .dev/standup-checklist.sh
☐ Note: Yesterday's 2-3 main tasks
☐ Note: Today's 2-3 planned tasks
☐ Note: Any blockers discovered
☐ Review: Last standup action items
```

---

## During Standup (Your Track's 3 Minutes)

### Say This (Exactly 3 minutes)

```
"Yesterday we [completed 2-3 items]. Today we're working on
[2-3 items], expected done [timing]. No blockers / Blocker:
[describe]. We need help with [specific ask]."
```

### Metrics to Share

| Metric | Track A | Track B | Track C |
|--------|---------|---------|---------|
| Tests Passing | ?/? | ?/? | ?/? |
| Coverage % | ? | ? | ? |
| Commits | ? | ? | ? |
| Blockers | 0/? | 0/? | 0/? |

### Critical Reminders by Track

**Track A (Server)**:
- FastMCP API signatures stable?
- Error handling patterns consistent?
- Type checking passing (strict)?

**Track B (Connectivity)**:
- Pin rotation tests all passing?
- Coordinate system Y-negation working?
- Reference validations passing?

**Track C (Patterns)**:
- Patterns built on stable component APIs?
- Example circuits valid in KiCAD?
- Documentation updated?

---

## Blocker Assessment (30 seconds)

```
Is it blocking progress RIGHT NOW?
│
├─ YES → How long to unblock?
│  ├─ < 1 hour → Unblock it (assign owner)
│  └─ > 1 hour → Escalate to Tech Lead NOW
│
└─ NO → Wait for standup discussion
```

---

## Quick Blocker Escalation

**If truly urgent (blocking all work):**

```
Message Tech Lead with:
1. What's blocked: [clear 1-sentence description]
2. Since when: [time discovered]
3. What we tried: [2-3 solutions attempted]
4. Owner: [who's on it]
5. ETA to fix: [specific time]
```

**Don't wait if it's a "critical" blocker** - escalate immediately.

---

## Timeline Pace Check

```
TODAY'S DATE: [fill in]
DAYS ELAPSED: ? out of 10
TARGET PROGRESS: 10% per day

Our progress: ? / 10 days = ? %

ON TRACK?  ☐ YES  ☐ NO  ☐ AHEAD

If behind → discuss with Tech Lead in standup
```

---

## After Standup (Next 15 minutes)

```
☐ Update your Kanban board (move tasks)
☐ If you have action item → confirm deadline with owner
☐ If dependent on another track → message them asking ETA
☐ If blocker assigned to you → start working on it
```

---

## Test Coverage Emergency Rules

```
COVERAGE > 90%     → ✓ Continue
COVERAGE 85-90%    → Add tests (next PR)
COVERAGE < 85%     → 🚨 STOP: Fix before merge

If you cause coverage drop > 5%, you must:
1. Add tests to restore it
2. Explain to Tech Lead why it dropped
3. Get approval before merge
```

---

## Escalation Severity Levels

```
🟢 LOW (can wait)
   └─ Minor issue, workaround exists
   └─ Check-in: next standup

🟡 MEDIUM (schedule fix)
   └─ Slows progress but doesn't stop it
   └─ Check-in: same day sync

🟠 HIGH (fix today)
   └─ Significant impact, needs today
   └─ Escalate: immediately to Tech Lead

🔴 CRITICAL (fix NOW)
   └─ Blocking all progress on v1
   └─ Escalate: 🚨 IMMEDIATELY - call Tech Lead
```

---

## Key Dates

```
TODAY (Day 1):        Foundation setup
END OF WEEK 1 (Day 5):    40% complete - on pace
DAY 10 (Week 2 Mid):      80% complete - on track
DAY 14 (Week 2 End):      100% complete - SHIPPED
```

---

## Decision Trees at a Glance

### "Should I escalate this?"

```
Duration blocked > 4 hours?
├─ YES → Escalate to Tech Lead
└─ NO  → Keep trying / ask team in standup
```

### "Am I behind schedule?"

```
Days elapsed / expected progress ratio
├─ < 0.9 → Ahead/on track (great!)
├─ 0.9-1.1 → On track (stay focused)
└─ > 1.1 → Behind (escalate to Tech Lead)
```

### "Can I add this feature?"

```
Do we have time remaining?
├─ YES → Will it exceed scope by >10%?
│  ├─ YES → Defer to v1.1
│  └─ NO  → Add it (estimate effort)
└─ NO  → Defer to v1.1 (no time left)
```

---

## Useful Commands (Copy-Paste)

### Test Status
```bash
uv run pytest tests/ -q --tb=no
```

### Test Coverage
```bash
uv run pytest --cov=kicad_sch_api --cov-report=term-missing
```

### Recent Commits
```bash
git log --oneline -10
```

### Check Uncommitted Work
```bash
git status -s
```

### Find TODOs/FIXMEs
```bash
grep -r "TODO\|FIXME\|BLOCKER" kicad_sch_api --include="*.py"
```

### Full Pre-Standup Check
```bash
bash .dev/standup-checklist.sh
```

---

## What NOT to Say in Standup

```
❌ "I'm still working on what I said yesterday"
   → Use: "Found unexpected complexity, now estimated to finish [time]"

❌ "I don't know why the tests are failing"
   → Use: "Tests failing on [specific issue], investigating, ETA [time]"

❌ "Maybe we have a blocker"
   → Use: "We have a blocker: [specific issue]"

❌ "This might need redesign"
   → Use: "We discovered [specific issue]. Options: [A/B/C]. Recommend [X]"

❌ "I think we're okay timeline-wise"
   → Use: "We're [X%] complete on day [Y], on pace for delivery"
```

---

## What TO Say in Standup

```
✓ "Completed [X] yesterday (commit abc123)"
✓ "Working on [Y] today, expect done by [time]"
✓ "No blockers currently"
✓ "Blocker: [specific issue], need [specific help], ETA [time]"
✓ "We're [X%] done, on track for delivery"
✓ "Found [issue], investigating 2 options, update tomorrow"
```

---

## Key Contacts

```
Tech Lead: [Name]
  Phone: [number]
  Slack: [handle]
  Email: [email]

Product Owner: [Name]
  Phone: [number]
  Slack: [handle]
  Email: [email]

On-Call for blockers: [Name]
  Available: [hours]
  Contact: [method]
```

---

## Track-Specific Quick Guides

### Track A Lead Checklist

```
DAILY CHECKLIST:

☐ Core tools implemented count: _/18
☐ Test coverage: _%
☐ Type checking passing: Y/N
☐ Error patterns consistent: Y/N
☐ API signatures documented: Y/N
☐ PRs ready for review: [count]

BLOCKERS TO WATCH:
☐ FastMCP breaking changes
☐ Type checking errors
☐ Tool signature conflicts
☐ Performance regressions
```

### Track B Lead Checklist

```
DAILY CHECKLIST:

☐ Pin rotation tests: _/11 passing
☐ Reference validations: _/8 passing
☐ Connectivity tests: _/25 passing
☐ Coordinate system Y-negation working: Y/N
☐ Hierarchical context handling: Y/N
☐ Netlist generation accurate: Y/N

BLOCKERS TO WATCH:
☐ Coordinate system edge cases
☐ KiCAD format mismatches
☐ Reference schematic validation failures
☐ Rotation/mirroring bugs
```

### Track C Lead Checklist

```
DAILY CHECKLIST:

☐ Patterns implemented: _/6
☐ Example circuits created: _/5
☐ Documentation pages: _/3
☐ Pattern test coverage: _%
☐ Components built on stable APIs: Y/N
☐ All patterns validate in KiCAD: Y/N

BLOCKERS TO WATCH:
☐ Unstable component APIs
☐ Missing connectivity features
☐ Symbol library gaps
☐ Documentation not matching code
```

---

## Emergency Phone Tree

```
IF YOU'RE BLOCKED FOR > 1 HOUR:

1. Message Tech Lead (Slack)
2. If no response in 15 min → Call Tech Lead
3. If Tech Lead unavailable → Message Product Owner
4. If PO unavailable → Stop work on blocked task, start
   highest-priority unblocked task
```

---

## Sprint Metrics Template

Print this daily to track progress:

```
DATE: _______________

TRACK A: __________ Lead
  Tools: __/18 | Coverage: _% | Blockers: 0/0

TRACK B: __________ Lead
  Tests: __/11 | Validations: __/8 | Blockers: 0/0

TRACK C: __________ Lead
  Patterns: __/6 | Circuits: __/5 | Blockers: 0/0

TIMELINE:
  Days elapsed: __ / 10
  Target progress: __% / 10% per day = 100%
  ON TRACK? ☐ YES ☐ NO

BLOCKERS THIS WEEK:
  1. _________________________ (resolved/in-progress)
  2. _________________________ (resolved/in-progress)
  3. _________________________ (resolved/in-progress)
```

---

## Golden Rules

```
1. BLOCKERS = ESCALATE IMMEDIATELY
   Don't try to solve for > 30 minutes alone

2. DATA NOT OPINIONS
   Bring metrics to standup, not guesses

3. TIME BOUNDARIES
   3 minutes per track, 15 minutes total - respect it

4. DOCUMENTATION
   Every decision gets documented immediately

5. TEST COVERAGE
   < 85% = code review blocked, must be fixed

6. SCOPE DISCIPLINE
   v1 only. Defer nice-to-haves to v1.1

7. HONESTY FIRST
   "We're behind" is better than hidden problems
```

---

**Print this card. Laminate it. Keep it on your desk. Reference it every day.**

**Standup starts in:** _____ minutes

**You are [Track A / B / C]**

**Today's deliverable:** _______________________

**Go deliver! 💪**
