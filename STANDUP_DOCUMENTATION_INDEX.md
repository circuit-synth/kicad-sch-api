# Standup Documentation Index & Guide

**Complete set of daily standup documentation for MCP Pin Connection Implementation**

---

## Document Overview

### 4 Core Documents Created

This comprehensive runbook package includes:

1. **STANDUP_RUNBOOK.md** (36 KB)
   - Detailed reference guide for all standup processes
   - Complete decision trees and escalation procedures
   - Pre-standup, during, and post-standup procedures
   - Weekly retrospective guidelines
   - **Best for**: Deep understanding, reference during implementation

2. **STANDUP_QUICK_REFERENCE.md** (8.4 KB)
   - Printable quick-reference card for daily use
   - 5-minute pre-standup checklist
   - Blocker assessment quick-flow
   - Track-specific checklists
   - **Best for**: Desk reference, printing and lamination

3. **DAILY_STANDUP_AGENDA.md** (16 KB)
   - Meeting agenda template for actual standup meetings
   - Exact timing and flow (15 minutes total)
   - Sample good and bad standups with analysis
   - Facilitator guidelines for Tech Lead
   - **Best for**: Posting in meeting room, facilitating actual meetings

4. **METRICS_TRACKING_TEMPLATE.md** (15 KB)
   - Daily metrics collection and tracking sheets
   - Weekly summary templates
   - Track-specific dashboards
   - Escalation trigger thresholds
   - **Best for**: Capturing data, measuring progress, identifying risks

---

## Quick Start: Using These Documents

### For Tech Lead / Facilitator

**Day 1 (Before first standup):**
1. Read: STANDUP_RUNBOOK.md sections 1-3
2. Print: DAILY_STANDUP_AGENDA.md
3. Post: Agenda in meeting room
4. Prepare: Metrics tracking sheet

**Every standup day:**
1. Reference: DAILY_STANDUP_AGENDA.md (timing + flow)
2. Facilitate: 15-minute standup using template
3. Track: Update METRICS_TRACKING_TEMPLATE.md
4. Escalate: Use decision trees from STANDUP_RUNBOOK.md

**Friday EOD (Weekly retrospective):**
1. Review: Weekly summary section in METRICS_TRACKING_TEMPLATE.md
2. Guide: Use STANDUP_RUNBOOK.md section 4 (retrospective)
3. Plan: Next week adjustments with team

---

### For Team Developers

**Day 1 (Before first standup):**
1. Read: STANDUP_QUICK_REFERENCE.md (5 min)
2. Print & laminate: STANDUP_QUICK_REFERENCE.md
3. Keep at desk during sprint

**Every standup day (5 min before):**
1. Run: `bash .dev/standup-checklist.sh`
2. Reference: STANDUP_QUICK_REFERENCE.md
3. Prepare 3-minute talking points
4. Note any blockers

**During standup:**
1. Speak for exactly 3 minutes using template
2. Share metrics with team
3. State asks clearly
4. Listen to action items

**After standup:**
1. Update your task board
2. If you have action item: confirm deadline
3. If dependent on another track: message for ETA

---

## Document-by-Document Usage Guide

### 1. STANDUP_RUNBOOK.md (Full Reference)

**Sections:**
- Pre-Standup Preparation (5.4 KB)
- Standup Flow & Timing (11 KB)
- Daily Focus Questions (4.2 KB)
- Weekly Retrospective (3.8 KB)
- Decision Trees (6.4 KB)
- Escalation Procedures (5.2 KB)
- Metrics Dashboard (2.1 KB)
- Post-Standup Actions (1.8 KB)

**Read when you need to:**
- Understand the full process
- Make a decision using decision trees
- Escalate a blocker (use escalation procedures)
- Run a retrospective (Friday EOD)
- Understand daily focus questions

**Keep open for reference:**
- During standups (Tech Lead)
- When escalating blockers
- When running retrospectives

---

### 2. STANDUP_QUICK_REFERENCE.md (Daily Reference Card)

**Sections:**
- 5 minutes before standup checklist
- Blocker assessment quick-flow
- Timeline pace check
- After standup actions
- Test coverage emergency rules
- Escalation severity levels
- Key dates
- Decision trees (condensed)
- Useful commands
- Track-specific checklists

**Use this for:**
- Daily desk reference
- Pre-standup prep (5 min)
- Quick decision-making
- Common mistakes to avoid
- What to say vs. NOT say

**Best practices:**
- Print it
- Laminate it
- Keep it at your desk
- Reference it every day

---

### 3. DAILY_STANDUP_AGENDA.md (Meeting Agenda)

**Sections:**
- Pre-standup (5 min before)
- Standup flow (exact timing)
- Track A/B/C update templates (3 min each)
- Cross-track sync (3 min)
- Action items & closing (3 min)
- Ground rules
- Sample standups (good and bad)
- After standup checklist

**Use this for:**
- Facilitating actual standups
- Understanding exact flow
- Seeing examples of good/bad standups
- Training new facilitators
- Keeping standup to 15 minutes

**Best practices:**
- Print it
- Post it in meeting room
- Use it to facilitate each standup
- Reference it if standup goes off track

---

### 4. METRICS_TRACKING_TEMPLATE.md (Progress Tracking)

**Sections:**
- Daily metrics (before standup)
- Track A/B/C dashboards
- Quality metrics
- Blocker checklist
- Weekly summary
- Velocity metrics
- Dashboard display format
- Escalation triggers
- Data collection scripts

**Use this for:**
- Collecting daily metrics (before standup)
- Tracking progress against plan
- Identifying blockers early
- Weekly progress reporting
- Spotting trend issues

**Best practices:**
- Fill out daily (takes 5 min)
- Share numbers in standup
- Use for decision-making
- Keep historical snapshots
- Reference when behind schedule

---

## Implementation Checklist

### Week 1 Setup

**Before Sprint Starts:**
- [ ] Print DAILY_STANDUP_AGENDA.md (post in meeting room)
- [ ] Print STANDUP_QUICK_REFERENCE.md (5 copies for team)
- [ ] Laminate STANDUP_QUICK_REFERENCE.md cards
- [ ] Create METRICS_TRACKING_TEMPLATE.md sheets (print or digital)
- [ ] Share all 4 documents with team via email + repo
- [ ] Read all 4 documents yourself (Tech Lead)
- [ ] Familiarize team with quick reference guide
- [ ] Prepare metrics tracking approach (digital/physical)

**Day 1 (First Standup):**
- [ ] Do pre-standup 5-minute prep with each track lead
- [ ] Collect baseline metrics using METRICS_TRACKING_TEMPLATE.md
- [ ] Run first standup using DAILY_STANDUP_AGENDA.md
- [ ] Capture action items in GitHub Issues
- [ ] Send standup summary email to team + Product Owner

**Daily (Every Standup Day):**
- [ ] Developers run pre-standup checklist (5 min before)
- [ ] Tech Lead reviews metrics from previous day
- [ ] Facilitate 15-minute standup using agenda template
- [ ] Update METRICS_TRACKING_TEMPLATE.md with daily data
- [ ] Document action items with deadlines
- [ ] Escalate blockers using decision trees

**Friday EOD (Weekly Retrospective):**
- [ ] Run retrospective following STANDUP_RUNBOOK.md section 4
- [ ] Complete weekly summary in METRICS_TRACKING_TEMPLATE.md
- [ ] Document lessons learned
- [ ] Plan adjustments for next week
- [ ] Send weekly summary to Product Owner

---

## How to Use Decision Trees

### Decision Trees Are In:

1. **STANDUP_RUNBOOK.md** (detailed versions with explanations)
   - Blocker Response Decision Tree
   - Test Coverage Drop Decision Tree
   - Timeline Slip Decision Tree
   - Scope Adjustment Decision Tree

2. **STANDUP_QUICK_REFERENCE.md** (condensed versions)
   - Quick blocker assessment
   - Timeline pace check
   - Can I add this feature?

### How to Use Them:

**Step 1: Identify the issue**
- Is it a blocker? Use Blocker Response DT
- Is test coverage dropping? Use Coverage DT
- Are we behind timeline? Use Timeline DT
- Is someone asking for new scope? Use Scope DT

**Step 2: Follow the tree**
- Start at top of diagram
- Answer YES/NO questions
- Follow arrows to decision point

**Step 3: Take action**
- Decision tree tells you what to do
- Execute that action
- Document the result

**Step 4: Report result**
- Share in next standup
- Update action item tracker
- Close if complete

**Example:**

```
Q: "We've been blocked on coordinate system math for 2 hours"

Use: Blocker Response Decision Tree
  ├─ Is it urgent? YES (we can't move forward)
  │  ├─ Can fix in < 1 hour? Unknown, depends on issue
  │  │  ├─ If YES → Unblock immediately (assign owner, 30-min timer)
  │  │  └─ If NO → Escalate to Tech Lead immediately
  └─ Report result in standup

Action: Contact Tech Lead now. Don't wait for standup.
        2-hour rule has been exceeded.
```

---

## Metrics Interpretation Guide

### Green Light (Keep Going)

```
✓ Progress: 10% per day or better
✓ Tests: > 95% passing
✓ Coverage: > 90%
✓ Type check: 0 errors
✓ Blockers: none > 30 minutes
✓ PRs: reviewed within 4 hours
✓ Scope creep: 0%

ACTION: Continue at current pace. Good discipline!
```

### Yellow Light (Monitor & Plan)

```
⚠ Progress: 8-10% per day (slightly behind)
⚠ Tests: 85-95% passing
⚠ Coverage: 85-90%
⚠ Type check: < 5 errors
⚠ Blockers: 1-4 hour duration
⚠ PRs: some waiting > 4 hours
⚠ Scope creep: < 10%

ACTION: Discuss in standup. Plan recovery. No escalation yet.
        Can we catch up by end of day? Need extra focus?
```

### Red Light (Escalate Immediately)

```
🔴 Progress: < 8% per day (behind schedule)
🔴 Tests: < 85% passing (tests failing)
🔴 Coverage: < 85% (dropping)
🔴 Type check: > 5 errors
🔴 Blockers: > 4 hour duration
🔴 PRs: waiting > 8 hours to review
🔴 Scope creep: > 10%

ACTION: Escalate to Tech Lead immediately.
        This needs urgent attention.
        May require timeline/scope adjustment.
```

---

## Escalation Flow Diagram

```
ISSUE DISCOVERED
       │
       ├─ Is it urgent (blocking all work)?
       │  │
       │  ├─ YES → Can fix in < 30 min?
       │  │  │
       │  │  ├─ YES → Fix immediately
       │  │  │       Report in standup
       │  │  │
       │  │  └─ NO → ESCALATE NOW
       │  │          Don't wait for standup
       │  │          Contact Tech Lead immediately
       │  │
       │  └─ NO → Can wait until standup?
       │     │
       │     ├─ YES → Present in standup
       │     │       Tech Lead makes decision
       │     │
       │     └─ NO → Schedule 15-min sync
       │             Come prepared with context
       │
       └─ Has been blocking > 4 hours?
          │
          └─ YES → ESCALATE TO PRODUCT OWNER
                   Timeline/scope decision needed
```

---

## Common Questions Answered

### Q: What if standup goes over 15 minutes?

**A:** Tech Lead must enforce timing. Use these tactics:

1. Before: "We have 15 minutes total, 3 per track"
2. During: "Track B, you're at 2 minutes, wrap up"
3. If needed: "Sounds like a detailed discussion. Let's schedule a 15-minute sync after this"

**Why enforce it:**
- Respects everyone's time
- Keeps focus on status, not solutions
- Prevents rabbit-holes
- Keeps energy up

---

### Q: What if someone doesn't have a blocker?

**A:** That's great! Say clearly:

```
"No blockers currently. We're moving well on [task].
Expect completion by [time]."
```

Then move to next topic. Nothing wrong with smooth progress!

---

### Q: What if we discover a blocker DURING standup?

**A:** Tech Lead handles it:

1. Track lead clearly states the issue
2. Tech Lead says: "Let's sync on this right after standup"
3. Schedule 15-minute sync after standup
4. Continue with other tracks
5. Solve it in dedicated time
6. Report solution next standup

**Don't** try to solve it during standup.

---

### Q: When should I escalate a blocker?

**A:** Use this rule:

```
BLOCKER DISCOVERED → 30-MIN TIMER STARTS

Can you fix it?
├─ YES → Do it. Report in standup.
└─ NO → ESCALATE at 30-min mark
        Don't wait, don't hope
        Escalate immediately
```

**Why 30 minutes?**
- Gives time for quick investigation
- But not too long to impact delivery
- Forces escalation discipline
- Prevents hidden blockers

---

### Q: What if a track is behind schedule?

**A:** Use Timeline Slip Decision Tree:

```
How far behind?

< 1 day (< 10%) → Can catch up?
  ├─ YES → Accelerate, report progress
  └─ NO → Discuss recovery plan in standup

1-2 days (10-20%) → Escalate to Tech Lead
  └─ Adjust estimates? Reduce scope?

> 2 days (> 20%) → Escalate to Product Owner
  └─ Timeline/scope adjustment needed
```

**Report honestly:** "We're 1.5 days behind. Here's why. Here's the plan to catch up."

---

### Q: What if test coverage drops?

**A:** Use Coverage Drop Decision Tree:

```
Coverage dropped from 92% to 88% = 4% drop

Is it intentional (new code without tests)?
├─ YES → STOP. Add tests. PR blocked until restored.
└─ NO → Why did it drop? Fix it.

RULE: New code without tests = PR rejection
      Coverage < 85% = cannot merge
```

**Action:** Fix coverage before merging. Don't compromise.

---

### Q: Should we adjust scope mid-sprint?

**A:** Only if necessary. Use Scope Decision Tree:

```
New work requested

Is it essential for v1?
├─ YES → Can we complete it in time?
│  ├─ YES → Add to plan (reduce other work)
│  └─ NO → Defer to v1.1
└─ NO → Defer to v1.1
```

**Key:** Protect v1 delivery. Defer non-essential to v1.1.
**Never:** Add scope without removing scope (scope creep).

---

## Sample Week Schedule

### Week 1 Daily Schedule

```
MONDAY (Day 1)
  09:55 - Pre-standup prep (all)
  10:00 - First standup (15 min)
  10:15 - Action item assignment
  10:30 - Work on tasks

TUESDAY-THURSDAY (Days 2-4)
  09:55 - Pre-standup prep (bash .dev/standup-checklist.sh)
  10:00 - Daily standup (15 min)
  10:15 - Continue tasks
  EOD   - Update metrics

FRIDAY (Day 5)
  09:55 - Pre-standup prep
  10:00 - Final standup
  14:00 - Weekly retrospective (30 min)
  15:00 - Plan adjustments for Week 2

WEEKEND
  Reflect on week, prepare for Week 2
```

### Weekly Meeting Summary

```
STANDUPS (5 per week):
  - Total time: 75 minutes (15 min × 5 days)
  - Purpose: Track progress, surface blockers
  - Attendees: 3 track leads + Tech Lead

RETROSPECTIVE (Friday 3pm):
  - Duration: 30 minutes
  - Purpose: Reflect, adjust, plan
  - Attendees: All tracks + PO
  - Outcome: Adjustments for Week 2

TOTAL MEETING TIME: ~2 hours per week
MEETING EFFICIENCY: 30% of typical agile team
```

---

## Integration with GitHub

### GitHub Issue Template for Action Items

```markdown
# Action Item: [Description]

**From Standup**: [Date]
**Assigned to**: [Owner]
**Due**: [Deadline]
**Priority**: [Critical / High / Medium / Low]

## Description
[Clear description of what needs to be done]

## Success Criteria
[How we know it's complete]

## Dependencies
[Any blockers or dependencies]

## Notes
[Any additional context]
```

### GitHub Label Suggestions

```
standup-action    - Action item from standup
blocker           - Blocking progress
critical-blocker  - Blocking all work, urgent
scope-creep       - Additional scope added
type-check-fail   - Type checking failures
coverage-drop     - Test coverage dropped below threshold
```

---

## Troubleshooting Common Issues

### Issue: Standups Keep Running Over 15 Minutes

**Cause**: Solving problems during standup
**Solution**:
1. Enforce hard time limit (use timer)
2. Say: "Schedule a sync for this topic"
3. Move detailed discussions to side channels

---

### Issue: Blockers Not Escalated Quickly

**Cause**: Developers trying to solve alone
**Solution**:
1. Remind: "30-minute rule - escalate if stuck"
2. Tech Lead checks blockers proactively
3. Show how decision trees speed resolution

---

### Issue: Test Coverage Dropping

**Cause**: New code without tests
**Solution**:
1. Add pre-commit hook to check coverage
2. Code review checks coverage trend
3. Block PRs with coverage drops

---

### Issue: Metrics Not Being Tracked

**Cause**: Too manual, not automated
**Solution**:
1. Create `.dev/metrics.sh` script to auto-collect
2. Run before standup (takes 2 min)
3. Copy metrics into METRICS_TRACKING_TEMPLATE.md

---

### Issue: Scope Creep Happening

**Cause**: Not saying "no" to new requests
**Solution**:
1. Use Scope Decision Tree
2. Defer non-essential to v1.1
3. For every new task: remove equal work or extend timeline

---

## Success Indicators

### By End of Week 1, You'll Know It's Working If:

```
✓ Every standup finishes in 15 minutes
✓ Blockers are escalated within 30 minutes
✓ Test coverage stays > 90%
✓ Type checking passes
✓ All action items have owners + deadlines
✓ No surprises (everyone is communicating)
✓ Each track is 40% complete on plan
✓ Team feels informed and aligned
```

### By End of Week 2, You'll Know It's Working If:

```
✓ All sprint goals delivered
✓ v1.0 ships on schedule
✓ Test coverage > 90%
✓ Type checking strict mode passing
✓ Zero critical bugs found post-launch
✓ Team is energized, not burnt out
✓ Retrospective shows continuous improvement
✓ Product Owner confident in quality
```

---

## Final Reminders

### Core Principles

1. **Transparency**: Real status, not hopeful status
2. **Accountability**: Clear owners, clear deadlines
3. **Unblocking**: Fast escalation, fast resolution
4. **Discipline**: 15 minutes, 3 per track, no exceptions
5. **Documentation**: Every decision documented
6. **Quality**: Never compromise on tests or coverage

### Golden Rules

1. **Never hide blockers** - escalate within 30 min
2. **Never commit to impossible deadlines** - be honest
3. **Never skip tests** - coverage < 85% = PR blocked
4. **Never merge type check failures** - strict mode always
5. **Never add scope without removing scope** - no creep
6. **Never discuss solutions in standup** - that's for syncs
7. **Never run over 15 minutes** - enforce hard stop

### Remember

> "The best standups are boring. Everyone's on track, no surprises, we're on pace to deliver. Exciting standups mean we waited too long to escalate something."

---

## Document Maintenance

### Who Owns What

| Document | Owner | Review Frequency |
|----------|-------|-----------------|
| STANDUP_RUNBOOK.md | Tech Lead | Before sprint, after retrospectives |
| STANDUP_QUICK_REFERENCE.md | Tech Lead | After sprint (for next sprint) |
| DAILY_STANDUP_AGENDA.md | Tech Lead | Before sprint, validate each week |
| METRICS_TRACKING_TEMPLATE.md | Metrics Owner | Update daily, review weekly |

### Version Control

- All documents in `/repo/root/`
- Update versions after major changes
- Keep in git for history tracking
- Include in project onboarding

### Feedback Loop

After sprint ends:
1. Retrospective discusses what worked
2. Update documents based on learnings
3. Version bump documents
4. Share improvements with team
5. Use for next sprint

---

**Document Set Version**: 1.0
**Created**: 2025-11-06
**Last Updated**: 2025-11-06
**For Sprint**: MCP Pin Connection Implementation (2 weeks)
**Status**: Ready for use

---

## Quick Links

- **Detailed Runbook**: STANDUP_RUNBOOK.md
- **Quick Reference Card**: STANDUP_QUICK_REFERENCE.md (print & laminate)
- **Meeting Agenda**: DAILY_STANDUP_AGENDA.md (post in meeting room)
- **Metrics Template**: METRICS_TRACKING_TEMPLATE.md (fill out daily)
- **This Index**: STANDUP_DOCUMENTATION_INDEX.md (you are here)

**Start with STANDUP_QUICK_REFERENCE.md. Reference STANDUP_RUNBOOK.md for details.**
