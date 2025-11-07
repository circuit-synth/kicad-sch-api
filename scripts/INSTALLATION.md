# Git Worktree Scripts - Installation & Setup Guide

Complete installation and first-use guide for the kicad-sch-api git worktree automation scripts.

## What You're Getting

Four production-ready bash scripts for managing parallel development:

1. **setup-worktrees.sh** - Create and initialize worktrees
2. **verify-worktrees.sh** - Validate worktree health
3. **sync-from-main.sh** - Keep branches up-to-date with main
4. **merge-to-main.sh** - Merge features back to main

## Pre-Installation Checklist

Before running the scripts, ensure:

- [ ] You have Git installed (version 2.17 or later)
  ```bash
  git --version
  ```

- [ ] You're in the kicad-sch-api repository
  ```bash
  pwd  # Should end with "kicad-sch-api"
  ls .git
  ```

- [ ] You're on the main branch
  ```bash
  git branch
  ```

- [ ] Main branch is up-to-date with origin
  ```bash
  git fetch origin
  git log main..origin/main  # Should be empty
  ```

- [ ] Your working tree is clean (no uncommitted changes)
  ```bash
  git status
  ```

## Installation Steps

### Step 1: Verify Scripts are Executable

The scripts should already be executable, but verify:

```bash
cd /path/to/kicad-sch-api/scripts
ls -la *.sh
```

All should show `-rwxr-xr-x` (executable).

If not executable, make them executable:

```bash
chmod +x setup-worktrees.sh verify-worktrees.sh sync-from-main.sh merge-to-main.sh
```

### Step 2: Verify Script Contents

Quick syntax check (no actual execution):

```bash
bash -n setup-worktrees.sh
bash -n verify-worktrees.sh
bash -n sync-from-main.sh
bash -n merge-to-main.sh
```

Should complete silently with exit code 0.

### Step 3: Run Initial Setup

From the repository root:

```bash
cd /path/to/kicad-sch-api

# Run setup
./scripts/setup-worktrees.sh
```

This will:
1. Check prerequisites
2. Validate git repository
3. Create three worktrees
4. Set up environment variables and aliases
5. Generate documentation

Expected output:
```
✓ Git is installed
✓ Git repository detected
✓ Repository root verified: /path/to/kicad-sch-api
✓ Main branch exists
✓ Working tree is clean
✓ Main branch is in sync with origin/main
✓ All worktrees created successfully
✓ Created worktree environment file
✓ Created worktree documentation
```

### Step 4: Verify Installation

```bash
./scripts/verify-worktrees.sh
```

Expected output:
```
✓ Git is installed
✓ In a valid git repository
ℹ Worktree exists: pin-discovery
✓ Worktree exists: wire-routing
✓ Worktree exists: testing-and-docs
✓ All checks passed! Worktrees are properly configured.
```

### Step 5: View Worktrees

```bash
git worktree list
```

Expected output:
```
/path/to/kicad-sch-api                    0000000 detached
/path/to/kicad-sch-api/worktrees/pin-discovery   0000000 [feat/pin-discovery]
/path/to/kicad-sch-api/worktrees/wire-routing    0000000 [feat/wire-routing]
/path/to/kicad-sch-api/worktrees/testing-and-docs 0000000 [feat/testing-and-docs]
```

## First Time Usage

### 1. Source the Environment (Optional but Recommended)

```bash
cd /path/to/kicad-sch-api
source worktrees/.worktree-env

# You now have helpful aliases:
pin-discovery      # Jump to pin-discovery worktree
wire-routing       # Jump to wire-routing worktree
testing-and-docs   # Jump to testing-and-docs worktree
repo               # Jump back to repo root
worktree-help      # Show available commands
```

### 2. Navigate to a Worktree

Option A: Using aliases (after sourcing)
```bash
pin-discovery
pwd  # Should be in worktrees/pin-discovery
```

Option B: Direct path
```bash
cd worktrees/pin-discovery
pwd  # Should be in worktrees/pin-discovery
```

### 3. Start Making Changes

```bash
cd worktrees/pin-discovery

# See branch info
git log --oneline -3
git status

# Make changes
vim kicad_sch_api/discovery/pin_finder.py

# Commit
git add kicad_sch_api/discovery/
git commit -m "feat: improve pin discovery"

# Push
git push origin feat/pin-discovery
```

## Common First-Run Issues

### Issue: "Permission denied" when running scripts

**Solution:**
```bash
chmod +x scripts/*.sh
```

### Issue: "command not found" for script

**Solution:**
```bash
# Use explicit path
./scripts/setup-worktrees.sh

# Or navigate to scripts directory
cd scripts
./setup-worktrees.sh
```

### Issue: "Not in a git repository"

**Solution:**
```bash
# Navigate to repository root
cd /path/to/kicad-sch-api

# Verify
git status
```

### Issue: "Uncommitted changes in main working tree"

**Solution:**
```bash
# Stash or commit changes
git status
git stash
# Then re-run setup
./scripts/setup-worktrees.sh
```

### Issue: "Main branch is not in sync with origin/main"

**Solution:**
```bash
git fetch origin
git pull origin main
# Then re-run setup
./scripts/setup-worktrees.sh
```

## Next Steps After Installation

### 1. Read the Documentation

```bash
# Full documentation
cat scripts/README.md

# Quick reference
cat scripts/QUICK_REFERENCE.md

# Worktree guide
cat worktrees/README.md
```

### 2. Explore Your Worktrees

```bash
source worktrees/.worktree-env

# Visit each worktree
pin-discovery && git log --oneline -5
wire-routing && git log --oneline -5
testing-and-docs && git log --oneline -5
```

### 3. Keep Worktrees Updated

```bash
cd /path/to/kicad-sch-api

# Sync all branches with latest main
./scripts/sync-from-main.sh
```

### 4. Regular Verification

```bash
# Check setup health
./scripts/verify-worktrees.sh

# Detailed report
./scripts/verify-worktrees.sh --verbose

# Fix any issues
./scripts/verify-worktrees.sh --fix
```

## Setup Verification Checklist

After installation, verify everything works:

- [ ] All three worktrees exist
  ```bash
  ls -la worktrees/
  ```

- [ ] Each worktree is a valid git repository
  ```bash
  ls -la worktrees/*/git
  ```

- [ ] Can navigate between worktrees
  ```bash
  source worktrees/.worktree-env
  pin-discovery && pwd
  ```

- [ ] Can make changes in a worktree
  ```bash
  cd worktrees/pin-discovery
  git status
  ```

- [ ] Scripts are executable
  ```bash
  ls -la scripts/*.sh
  ```

- [ ] Logs are generated correctly
  ```bash
  ls -la .worktree-*.log
  ```

## System Requirements

**Minimum:**
- Git 2.17 (for worktree support)
- Bash 4.0 (for associative arrays)
- Unix-like system (Linux, macOS, WSL)

**Recommended:**
- Git 2.25+
- Bash 5.0+
- Unlimited disk space for three complete worktrees
- Internet access for pushing to origin

## Disk Space

Each worktree shares the same `.git/objects` directory, so:

- Main repository: ~50 MB (typical)
- Each worktree: ~1 MB (just working directory)
- Total for 3 worktrees: ~50 MB additional

## Troubleshooting

### Verify Git Version

```bash
git --version
# Should output Git 2.17 or higher
```

### Check Worktree Support

```bash
git worktree --help
# Should show help without errors
```

### Diagnose Setup Issues

```bash
./scripts/verify-worktrees.sh --verbose
# Shows detailed status and any issues
```

### View Detailed Logs

```bash
# Setup log
tail -50 .worktree-setup.log

# Verification log
tail -50 .worktree-verify.log

# Look for ERROR entries
grep ERROR .worktree-*.log
```

## Getting Help

### View Script Help

```bash
./scripts/setup-worktrees.sh --help
./scripts/verify-worktrees.sh --help
./scripts/sync-from-main.sh --help
./scripts/merge-to-main.sh --help
```

### Run with Verbose Output

```bash
./scripts/setup-worktrees.sh --verbose
./scripts/verify-worktrees.sh --verbose
./scripts/sync-from-main.sh --verbose
```

### Check Environment Help

```bash
source worktrees/.worktree-env
worktree-help
```

## Maintenance

### Regular Checks

```bash
# Weekly: Verify setup health
./scripts/verify-worktrees.sh

# When syncing: Keep branches updated
./scripts/sync-from-main.sh

# When done with features: Merge to main
./scripts/merge-to-main.sh
```

### Cleanup

If you need to start over:

```bash
# Remove all worktrees and reset
./scripts/setup-worktrees.sh --clean

# Re-create everything
./scripts/setup-worktrees.sh

# Verify new setup
./scripts/verify-worktrees.sh
```

## Integration with Development Workflow

After successful installation, integrate into your workflow:

### In Your Shell Profile (~/.bashrc or ~/.zshrc)

```bash
# Add these aliases for easy script access
alias ws-setup='cd /path/to/kicad-sch-api && ./scripts/setup-worktrees.sh'
alias ws-verify='cd /path/to/kicad-sch-api && ./scripts/verify-worktrees.sh'
alias ws-sync='cd /path/to/kicad-sch-api && ./scripts/sync-from-main.sh'
alias ws-merge='cd /path/to/kicad-sch-api && ./scripts/merge-to-main.sh'

# Source worktree environment when entering repo
cd /path/to/kicad-sch-api && source worktrees/.worktree-env 2>/dev/null || true
```

Then use:
```bash
ws-verify
ws-sync
ws-merge
```

## Uninstall

To completely remove worktrees and revert to single-tree development:

```bash
cd /path/to/kicad-sch-api

# Remove all worktrees
git worktree remove worktrees/pin-discovery
git worktree remove worktrees/wire-routing
git worktree remove worktrees/testing-and-docs

# Clean up directories
rm -rf worktrees/
rm .worktree-env

# Remove branch references if desired
git branch -D feat/pin-discovery feat/wire-routing feat/testing-and-docs

# Clean up logs
rm .worktree-*.log

# Scripts remain for future use
```

## Success!

You're now ready to use git worktrees for parallel development. Start with:

```bash
# Verify everything still works
./scripts/verify-worktrees.sh

# Source environment
source worktrees/.worktree-env

# Jump to your first feature
pin-discovery

# Start coding!
```

For detailed usage, see `/scripts/README.md` or `/scripts/QUICK_REFERENCE.md`.
