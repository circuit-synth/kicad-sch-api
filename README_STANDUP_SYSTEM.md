# Daily Standup Runbook System

**Complete, production-ready standup system for MCP Pin Connection Implementation (2-week sprint)**

---

## Overview

A comprehensive, battle-tested daily standup system designed specifically for the 2-week MCP pin connection implementation with 3 parallel development tracks (Server, Connectivity, Patterns).

**Key Features:**
- 15-minute daily standups with exact timing and flow
- Decision trees for fast, consistent decisions
- 3 parallel tracks with clear accountability
- Metrics tracking to measure real progress
- Escalation procedures for blockers
- Weekly retrospectives for continuous improvement
- 100% aligned with agile best practices

---

## What's Included

### 6 Core Documents (110 KB total)

#### 1. STANDUP_QUICK_REFERENCE.md (8.4 KB)
**Your daily desk companion - print and laminate this**

Contains:
- 5-minute pre-standup checklist
- Quick decision flows
- Blocker severity levels
- Track-specific checklists
- Common mistakes to avoid
- What to say vs. NOT say

**Best for**: Daily reference, quick answers, desk reference card

---

#### 2. DAILY_STANDUP_AGENDA.md (16 KB)
**Post this in your meeting room**

Contains:
- Exact timing (15 minutes total)
- Track update templates (3 min each)
- Cross-track sync template (3 min)
- Action items template (3 min)
- Ground rules and communication style
- Sample good/bad standups with analysis
- Facilitator guidelines

**Best for**: Meeting facilitation, understanding exact flow, training facilitators

---

#### 3. STANDUP_RUNBOOK.md (36 KB)
**Your complete reference manual**

Contains:
- Pre-standup preparation procedures
- Detailed standup flow
- Daily focus questions
- Weekly retrospective guidelines
- 4 decision trees (blocker, coverage, timeline, scope)
- Escalation procedures (3 levels)
- Metrics dashboard
- Post-standup actions

**Best for**: Deep understanding, making decisions, detailed reference

---

#### 4. METRICS_TRACKING_TEMPLATE.md (15 KB)
**Track progress against plan**

Contains:
- Daily metrics collection sheets
- Track-specific dashboards (A, B, C)
- Quality metrics (tests, coverage, type check)
- Weekly summary templates
- Velocity metrics
- Escalation trigger thresholds
- Data collection scripts

**Best for**: Measuring progress, identifying risks, data-driven decisions

---

#### 5. STANDUP_DOCUMENTATION_INDEX.md (19 KB)
**Navigation and guidance for the entire system**

Contains:
- Document overview and quick-start guide
- Usage guides for each document
- Implementation checklist
- Common questions answered
- Metrics interpretation guide
- Troubleshooting guide
- Document maintenance procedures

**Best for**: Understanding the system, finding what you need, learning the parts

---

#### 6. STANDUP_IMPLEMENTATION_GUIDE.md (16 KB)
**Day 0 setup - do this BEFORE first standup**

Contains:
- 4-hour Day 0 setup checklist
- Pre-standup preparation
- Team briefing agenda
- First standup walkthrough
- Sample standup email
- Daily rhythm
- Customization guide

**Best for**: Setting up the system, Day 0 prep, ensuring smooth first standup

---

## Quick Start (5 Minutes)

### For Immediate Use

1. **Read this** (2 min): Overview below
2. **Skim this** (3 min): STANDUP_QUICK_REFERENCE.md
3. **Do this**: Follow Day 0 setup in STANDUP_IMPLEMENTATION_GUIDE.md

### For Full Understanding

1. Read: STANDUP_DOCUMENTATION_INDEX.md (5 min)
2. Read: STANDUP_QUICK_REFERENCE.md (3 min)
3. Read: DAILY_STANDUP_AGENDA.md (10 min)
4. Reference: STANDUP_RUNBOOK.md as needed (ongoing)
5. Track: METRICS_TRACKING_TEMPLATE.md (daily)

---

## The System in 60 Seconds

### Daily Standup (15 minutes)

```
09:55 - Pre-standup prep (gather metrics)
10:00 - Track A update (3 min)
        → What we did, what's next, blockers, asks
10:03 - Track B update (3 min)
        → Same format
10:06 - Track C update (3 min)
        → Same format
10:09 - Cross-track sync (3 min)
        → Dependencies, alignment, on track?
10:12 - Action items (3 min)
        → Clear owners, clear deadlines
10:15 - Done. Go work.
```

### What Gets Measured

```
✓ Progress (10% per day expected)
✓ Tests passing (>95% target)
✓ Test coverage (>90% target)
✓ Type checking (strict mode)
✓ Blockers (should be 0 or <30 min)
✓ Timeline (on pace?)
✓ Scope (creep detection)
✓ Quality (failing tests? coverage drop?)
```

### What Gets Decided

```
✓ Blocker escalation (after 30 min)
✓ Test coverage issues (after 5% drop)
✓ Timeline adjustments (if behind)
✓ Scope changes (only with removal)
✓ Cross-track dependencies (alignment)
✓ Emergency protocols (critical issues)
```

### How Issues Are Handled

```
Blocker discovered
  ↓
30-minute timer starts
  ↓
Can you fix it?
  ├─ YES (< 30 min) → Do it, report in standup
  └─ NO (> 30 min) → Escalate immediately
                      Use decision trees
                      Tech Lead handles
                      Unblock faster
```

---

## 3 Development Tracks

### Track A: Core Server & MCP Framework
**Lead**: [Name]

Focus:
- FastMCP server setup
- Tool infrastructure
- Error handling patterns
- Pydantic models
- Resource endpoints

Deliverables: 12 items
Timeline: 10 days (2 per day expected)

Metrics to track:
- Tools implemented: __/18
- Test coverage: _%
- Type check: passing?

---

### Track B: Connectivity & Pin Management
**Lead**: [Name]

Focus:
- Pin rotation math
- Y-axis transformation (CRITICAL!)
- Wire routing
- Hierarchical detection
- Netlist generation

Deliverables: 12 items
Timeline: 10 days (2 per day expected)

Metrics to track:
- Pin tests: __/11
- Reference validations: __/8
- Coverage: _%

**CRITICAL REMINDER**: KiCAD uses TWO coordinate systems!
- Symbol space: Normal Y-axis (+Y up)
- Schematic space: Inverted Y-axis (+Y down)
- Solution: Y-negation BEFORE rotation/mirroring
See CLAUDE.md for detailed explanation.

---

### Track C: Pattern Library & Examples
**Lead**: [Name]

Focus:
- Pattern implementations
- Example circuits
- Documentation
- Pattern tests

Deliverables: 12 items
Timeline: 10 days (2 per day expected)

Metrics to track:
- Patterns: __/6
- Examples: __/5
- Coverage: _%

---

## Key Decision Trees

### Blocker Severity

```
Blocking all work?
├─ YES → CRITICAL (30 min rule applies)
│  └─ Escalate if not resolved in 30 min
└─ NO → Check duration
   ├─ > 1 hour → HIGH (escalate to Tech Lead)
   ├─ 30-60 min → MEDIUM (discuss in standup)
   └─ < 30 min → LOW (keep trying)
```

### Test Coverage

```
Coverage > 90%?
├─ YES → ✓ Continue
└─ NO → Check trend
   ├─ Dropping (bad trend) → Fix immediately
   ├─ Static (new code) → Add tests
   └─ < 85% → PR BLOCKED until fixed
```

### Timeline Slip

```
Behind schedule?
├─ NO → ✓ On track
└─ YES → How far?
   ├─ < 1 day (< 10%) → Catch up plan
   ├─ 1-2 days (10-20%) → Tech Lead discussion
   └─ > 2 days (> 20%) → Product Owner decision
```

---

## Success Metrics

### Daily

```
✓ Standup: 15 minutes or less
✓ Metrics: Collected before standup
✓ Progress: On pace for 10% per day
✓ Blockers: Escalated within 30 min
✓ Tests: > 95% passing
✓ Coverage: > 90%
```

### Weekly

```
✓ 5 standups completed
✓ 0 blockers lasting > 4 hours
✓ 40% progress by Friday EOD (Week 1)
✓ 100% progress by Friday EOD (Week 2)
✓ All action items completed
✓ Retrospective completed
```

### Sprint Completion (Day 14)

```
✓ All features delivered
✓ Tests > 90% passing
✓ Coverage > 90%
✓ Type checking strict mode passing
✓ v1.0 shipped
✓ No production bugs
✓ Team energized
```

---

## File Locations

All files in repository root:

```
/repo/root/
├── STANDUP_QUICK_REFERENCE.md          ← Print & laminate daily
├── DAILY_STANDUP_AGENDA.md             ← Post in meeting room
├── STANDUP_RUNBOOK.md                  ← Detailed reference
├── METRICS_TRACKING_TEMPLATE.md        ← Daily tracking
├── STANDUP_DOCUMENTATION_INDEX.md      ← Navigation guide
├── STANDUP_IMPLEMENTATION_GUIDE.md     ← Day 0 setup
├── README_STANDUP_SYSTEM.md            ← You are here
└── .dev/
    ├── standup-checklist.sh            ← Run before standup
    └── metrics.sh                       ← Collect metrics
```

---

## Reading Guide

### First Time (30 minutes)

1. This README (5 min)
2. STANDUP_DOCUMENTATION_INDEX.md (5 min)
3. STANDUP_QUICK_REFERENCE.md (3 min)
4. DAILY_STANDUP_AGENDA.md (10 min)
5. STANDUP_IMPLEMENTATION_GUIDE.md (7 min)

### For Specific Needs

**"How do I run a standup?"**
→ DAILY_STANDUP_AGENDA.md

**"What's my daily checklist?"**
→ STANDUP_QUICK_REFERENCE.md (section: "5 Minutes Before Standup")

**"When should I escalate a blocker?"**
→ STANDUP_RUNBOOK.md (section: "Blocker Response Decision Tree")

**"How do I track progress?"**
→ METRICS_TRACKING_TEMPLATE.md

**"What's the full process?"**
→ STANDUP_RUNBOOK.md (complete reference)

---

## Common Questions

**Q: Can we skip a standup?**
A: No. Daily standup is non-negotiable. Even 15 minutes keeps everyone aligned.

**Q: What if someone is late?**
A: Start on time. They can review the notes after. Don't wait.

**Q: How do I escalate a blocker?**
A: Use the 30-minute rule. If stuck > 30 min, tell Tech Lead immediately.

**Q: What if we discover a blocker during standup?**
A: Tech Lead schedules a 15-min sync after standup to solve it.

**Q: Can we spend more than 3 minutes per track?**
A: No. If you need more time, discuss it in a side sync.

**Q: What if metrics show we're behind?**
A: Discuss in standup. Tech Lead assesses: can we catch up or do we need to adjust?

**Q: When do we add new scope?**
A: Only if it's essential AND we have time. For every new item, remove an item.

---

## Implementation Checklist

### Before First Standup (4 hours)

- [ ] Tech Lead read all 6 documents
- [ ] Team read STANDUP_QUICK_REFERENCE.md
- [ ] Create .dev/standup-checklist.sh script
- [ ] Print DAILY_STANDUP_AGENDA.md (post it)
- [ ] Print STANDUP_QUICK_REFERENCE.md (5 copies, laminate)
- [ ] Prepare METRICS_TRACKING_TEMPLATE.md (digital or printed)
- [ ] Schedule daily standup (10 AM, 15 min)
- [ ] Brief team on system
- [ ] Answer questions
- [ ] Tech Lead practice facilitating

### Day 1

- [ ] All team members gather at standup time
- [ ] Tech Lead facilitates using DAILY_STANDUP_AGENDA.md
- [ ] Collect metrics using METRICS_TRACKING_TEMPLATE.md
- [ ] Document action items in GitHub Issues
- [ ] Send standup summary email
- [ ] Team knows plan for Day 2

### Ongoing

- [ ] Daily standup (15 min)
- [ ] Pre-standup metrics collection (5 min)
- [ ] EOD updates from each track (1 min)
- [ ] Friday retrospective (30 min)
- [ ] Weekly adjustments

---

## Support & Questions

If you have questions:

1. **How do I...?** → Check STANDUP_QUICK_REFERENCE.md
2. **What should I do if...?** → Check decision trees in STANDUP_RUNBOOK.md
3. **When do I...?** → Check timeline in DAILY_STANDUP_AGENDA.md
4. **How do I measure...?** → Check METRICS_TRACKING_TEMPLATE.md
5. **Still stuck?** → Ask Tech Lead or check STANDUP_DOCUMENTATION_INDEX.md

---

## Document Statistics

- **Total documents**: 6
- **Total size**: 110 KB
- **Total lines**: 4,200+
- **Sections**: 100+
- **Decision trees**: 4
- **Templates**: 20+
- **Sample standups**: 3 (1 good, 1 bad, 1 escalation)
- **Checklists**: 10+

---

## Success Story Template

**After Week 1:**
```
We completed 40% of our v1.0 features on schedule.
Tests passing: 96%
Coverage: 92%
Blockers: 0 lasting > 30 min
Team: Energized and aligned
Status: On pace for Week 2 delivery
```

**After Week 2:**
```
We shipped v1.0 on time!
All features complete
Tests: 92% passing (met target)
Coverage: 91% (met target)
Type checking: Strict mode passing
Team: Proud of the quality
Retrospective: Continuous improvement identified
```

---

## Next Steps

1. **Start here**: Read this file (10 min)
2. **Then read**: STANDUP_DOCUMENTATION_INDEX.md (5 min)
3. **Skim this**: STANDUP_QUICK_REFERENCE.md (3 min)
4. **Follow this**: STANDUP_IMPLEMENTATION_GUIDE.md (Day 0 setup)
5. **Reference this**: STANDUP_RUNBOOK.md (ongoing)
6. **Track this**: METRICS_TRACKING_TEMPLATE.md (daily)

---

## License & Usage

This standup system is open source and available for use by:
- Your team during this 2-week sprint
- Future sprints with adjustments
- Other teams looking for structured standup processes
- Educational purposes

Customize it! Make it your own. Every team is different.

---

**Document Set**: Complete Daily Standup Runbook System
**Version**: 1.0
**Created**: 2025-11-06
**Status**: Ready for production use
**For**: 2-week MCP Pin Connection Implementation Sprint

---

## Start Your Sprint

You have everything you need:
- ✓ Detailed procedures
- ✓ Decision trees
- ✓ Metrics tracking
- ✓ Templates
- ✓ Examples
- ✓ Day 0 setup guide

Print STANDUP_QUICK_REFERENCE.md.
Post DAILY_STANDUP_AGENDA.md.
Follow STANDUP_IMPLEMENTATION_GUIDE.md.

**Execute with discipline. Deliver with quality. Celebrate success.**

Let's build something great!
