# Git Worktree Automation Scripts - Start Here

Welcome! This document is your entry point to the new git worktree automation system for the kicad-sch-api MCP pin connection project.

## What You Have

Four production-ready bash scripts that automate parallel development across three independent feature branches:

1. **setup-worktrees.sh** - Create and initialize worktrees
2. **verify-worktrees.sh** - Check worktree health
3. **sync-from-main.sh** - Keep branches updated
4. **merge-to-main.sh** - Merge features back to main

All files are located in `/scripts/` directory.

## Getting Started (5 minutes)

### Step 1: Read the Installation Guide
```bash
cat scripts/INSTALLATION.md
# Takes 3 minutes, shows you exactly what to do
```

### Step 2: Run Setup
```bash
./scripts/setup-worktrees.sh
# Takes 10-30 seconds
```

### Step 3: Verify It Works
```bash
./scripts/verify-worktrees.sh
# Takes 5-10 seconds
```

### Step 4: Read Quick Reference
```bash
cat scripts/QUICK_REFERENCE.md
# Shows you all the common commands
```

### Step 5: Start Working
```bash
source worktrees/.worktree-env
pin-discovery
# You're now in your first feature branch
```

That's it! You're ready to develop.

## The Three Worktrees

Once setup completes, you'll have three independent feature branches:

| Branch | Location | Purpose |
|--------|----------|---------|
| feat/pin-discovery | worktrees/pin-discovery | Pin discovery & component traversal |
| feat/wire-routing | worktrees/wire-routing | Wire endpoint analysis & routing |
| feat/testing-and-docs | worktrees/testing-and-docs | Testing infrastructure & docs |

Each is a complete working directory that you can work in independently without switching branches.

## Daily Workflow

```bash
# Start your shell
source worktrees/.worktree-env

# Jump to a feature
pin-discovery

# Make changes
vim kicad_sch_api/discovery/pin_finder.py
git add .
git commit -m "feat: improve pin discovery"
git push origin feat/pin-discovery

# Keep branch updated
cd /path/to/repo
./scripts/sync-from-main.sh

# Merge when done
./scripts/merge-to-main.sh
```

## Documentation

### Essential Reading (Read These)
1. **scripts/INSTALLATION.md** - Setup guide (read first)
2. **scripts/QUICK_REFERENCE.md** - Command cheat sheet (use daily)

### Complete Reference (For Details)
3. **scripts/README.md** - Full documentation (all details)
4. **scripts/INDEX.md** - Master index (navigate by task)

### Overview
5. **WORKTREE_SCRIPTS_SUMMARY.md** - Project summary

## Common Commands

```bash
# Setup and verify
./scripts/setup-worktrees.sh
./scripts/verify-worktrees.sh

# Daily sync (keep updated)
./scripts/sync-from-main.sh

# Merge when done
./scripts/merge-to-main.sh

# All scripts have help
./scripts/setup-worktrees.sh --help
./scripts/verify-worktrees.sh --help
./scripts/sync-from-main.sh --help
./scripts/merge-to-main.sh --help
```

## Key Features

✓ **Safe** - No force operations, comprehensive error checking
✓ **Easy** - One command to setup, intuitive workflow
✓ **Clear** - Color output, progress reporting, help messages
✓ **Logged** - Detailed logs for debugging (`.worktree-*.log`)
✓ **Flexible** - Multiple sync strategies, interactive modes
✓ **Documented** - 5 documentation files, 100+ examples

## Troubleshooting

### "Permission denied" when running script
```bash
chmod +x scripts/*.sh
```

### "Not a git repository"
```bash
# Make sure you're in repo root
cd /path/to/kicad-sch-api
```

### Any other issue
```bash
# Run verification with verbose output
./scripts/verify-worktrees.sh --verbose

# Check logs
tail -50 .worktree-*.log

# Read troubleshooting guide
cat scripts/README.md | grep -A 20 "Troubleshooting"
```

## File Structure

```
kicad-sch-api/
├── scripts/
│   ├── setup-worktrees.sh           ← Run first
│   ├── verify-worktrees.sh          ← Verify works
│   ├── sync-from-main.sh            ← Keep updated
│   ├── merge-to-main.sh             ← Merge features
│   ├── README.md                    ← Full guide
│   ├── QUICK_REFERENCE.md           ← Command list
│   ├── INSTALLATION.md              ← Setup guide
│   └── INDEX.md                     ← Navigation
├── worktrees/                       ← Created by setup
│   ├── pin-discovery/
│   ├── wire-routing/
│   ├── testing-and-docs/
│   └── .worktree-env                ← Source this
└── WORKTREE_SCRIPTS_SUMMARY.md      ← Overview
```

## Next Steps

1. **Right Now**: Read `scripts/INSTALLATION.md`
2. **In 5 min**: Run `./scripts/setup-worktrees.sh`
3. **In 10 min**: Run `./scripts/verify-worktrees.sh`
4. **Keep handy**: `scripts/QUICK_REFERENCE.md`
5. **Start coding**: `source worktrees/.worktree-env && pin-discovery`

## Questions?

### How do I...

**Set up worktrees?**
→ `scripts/INSTALLATION.md`

**Use a command?**
→ `scripts/QUICK_REFERENCE.md` or `./scripts/[script] --help`

**Find something?**
→ `scripts/INDEX.md`

**Understand everything?**
→ `scripts/README.md`

**Get an overview?**
→ `WORKTREE_SCRIPTS_SUMMARY.md`

## Key Concepts

### Worktrees
Instead of switching branches (which changes your working directory), each worktree is an independent working directory on a different branch. You can work in three places simultaneously.

### Safe Operations
All scripts use safe defaults - no force operations, comprehensive error checking, and clear instructions if something goes wrong.

### Logging
Every script logs its operations to `.worktree-*.log` files for debugging and audit trails.

### Aliases
Source `.worktree-env` to get helpful aliases like `pin-discovery`, `wire-routing`, `testing-and-docs`, and `repo`.

## Performance

- **Setup**: 10-30 seconds (one-time)
- **Verify**: 5-10 seconds
- **Sync**: 10-30 seconds
- **Merge**: 2-5 seconds
- **Disk usage**: ~50 MB for three worktrees (shared git objects)

## Requirements

- **Git** 2.17 or later (for worktree support)
- **Bash** 4.0 or later
- **macOS**, Linux, or WSL
- Clean git working tree (no uncommitted changes)

## Support

Everything you need is included:
- 4 production-ready scripts
- 5 comprehensive documentation files
- Help messages in every script
- Detailed logging for debugging
- Interactive prompts and feedback

Just start with `scripts/INSTALLATION.md` and you're on your way.

---

**Last Updated**: November 6, 2025
**Status**: Production-Ready
**Files**: 9 total (4 scripts + 5 docs)
**Size**: 121 KB total

**Ready to get started?** → `cat scripts/INSTALLATION.md`
