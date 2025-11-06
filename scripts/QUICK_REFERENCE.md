# Git Worktree Scripts - Quick Reference

A quick lookup guide for common worktree operations.

## One-Time Setup

```bash
# Create all worktrees
./setup-worktrees.sh

# Verify everything works
./scripts/verify-worktrees.sh
```

## Navigation

```bash
# Direct path
cd worktrees/pin-discovery

# Or use aliases (after sourcing environment)
source worktrees/.worktree-env
pin-discovery      # Jump to pin-discovery
wire-routing       # Jump to wire-routing
testing-and-docs   # Jump to testing-and-docs
repo               # Back to repo root
```

## Daily Operations

### Start Work on a Feature

```bash
cd worktrees/pin-discovery
git status
git log --oneline main..HEAD
```

### Make Changes

```bash
cd worktrees/pin-discovery
# Edit files
vim kicad_sch_api/discovery/pin_finder.py

# Commit changes
git add kicad_sch_api/discovery/
git commit -m "feat: improve pin discovery"

# Push to GitHub
git push origin feat/pin-discovery
```

### Stay in Sync with Main

```bash
cd /repo/root
./scripts/sync-from-main.sh
# All branches rebase on latest main
```

### Review Changes

```bash
cd worktrees/pin-discovery
git log --oneline main..HEAD          # See your commits
git diff main                         # See all changes
git show HEAD                         # View last commit
```

## Merging

### Interactive Merge (Recommended)

```bash
cd /repo/root
./scripts/merge-to-main.sh
# Select branches to merge
# Review changes
# Confirm each merge
```

### Merge All Branches

```bash
./scripts/merge-to-main.sh --all
```

### Preview Merge

```bash
./scripts/merge-to-main.sh --dry-run --verbose
```

## Diagnosis & Maintenance

### Check Setup Health

```bash
./scripts/verify-worktrees.sh
```

### Detailed Status

```bash
./scripts/verify-worktrees.sh --verbose
```

### Fix Issues

```bash
./scripts/verify-worktrees.sh --fix
```

### View All Worktrees

```bash
git worktree list
```

## Logs

```bash
# Setup log
cat .worktree-setup.log

# Verification log
cat .worktree-verify.log

# Sync log
cat .worktree-sync.log

# Merge log
cat .worktree-merge.log

# View last 20 lines of any log
tail -20 .worktree-setup.log
```

## Troubleshooting

### Reset Worktrees

```bash
./scripts/setup-worktrees.sh --clean
./scripts/setup-worktrees.sh
```

### Fix Stale Locks

```bash
./scripts/verify-worktrees.sh --fix
```

### Resolve Merge Conflicts (During Sync)

```bash
cd worktrees/pin-discovery
# Edit conflicted files
git rebase --continue
# Or abort
git rebase --abort
```

### Resolve Merge Conflicts (During Merge to Main)

```bash
cd /repo/root
# Edit conflicted files in your editor
git add [resolved files]
git commit -m "Resolve merge conflicts"
```

## Sync Strategies

### Default: Rebase (Linear History)

```bash
./scripts/sync-from-main.sh
# Or explicitly
./scripts/sync-from-main.sh --strategy rebase
```

### Merge (Preserve History)

```bash
./scripts/sync-from-main.sh --strategy merge
```

### Fast-Forward Only

```bash
./scripts/sync-from-main.sh --strategy fast-forward
```

## Git Commands (In Worktree)

### View Status

```bash
git status
git log --oneline -5
```

### Commit Work

```bash
git add [files]
git commit -m "feat: description"
git push origin feat/pin-discovery
```

### Compare with Main

```bash
git log --oneline main..HEAD      # Your commits
git log --oneline HEAD..main      # Commits to catch up on
git diff main..HEAD               # Your changes
```

### Stash Changes

```bash
git stash                         # Save work temporarily
git stash list                    # View stashes
git stash pop                     # Restore work
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Worktree not found | Run `./scripts/setup-worktrees.sh` |
| Branch ahead/behind | Run `./scripts/sync-from-main.sh` |
| Stale locks | Run `./scripts/verify-worktrees.sh --fix` |
| Merge conflicts | Resolve manually, then run `git rebase --continue` |
| Need to reset | Run `./scripts/setup-worktrees.sh --clean` then setup again |
| Branch not tracking | Run `./scripts/verify-worktrees.sh --fix` |

## Tips & Tricks

### Bash Alias for Easier Invocation

Add to your `.bashrc` or `.zshrc`:

```bash
alias ws-setup='./scripts/setup-worktrees.sh'
alias ws-verify='./scripts/verify-worktrees.sh'
alias ws-sync='./scripts/sync-from-main.sh'
alias ws-merge='./scripts/merge-to-main.sh'
```

Then use:
```bash
ws-verify
ws-sync
ws-merge
```

### View Worktree Environment

```bash
source worktrees/.worktree-env
worktree-help
```

### Fast Branch Switching

```bash
# Without aliases
alias pd='cd worktrees/pin-discovery'
alias wr='cd worktrees/wire-routing'
alias td='cd worktrees/testing-and-docs'
alias rr='cd /path/to/repo/root'

# Use: pd, wr, td, rr
```

### Monitor Branch Status

```bash
# Check all branches at once
for dir in worktrees/*/; do
  echo "=== $(basename $dir) ==="
  git -C "$dir" log -1 --oneline
  git -C "$dir" rev-list --count main..HEAD
done
```

## Performance Notes

- First setup takes ~10-30 seconds
- Verification takes ~5-10 seconds
- Sync depends on repo size (usually <30 seconds)
- Merge depends on number of commits (usually <5 seconds)

## Help Commands

```bash
# Script help
./scripts/setup-worktrees.sh --help
./scripts/verify-worktrees.sh --help
./scripts/sync-from-main.sh --help
./scripts/merge-to-main.sh --help

# View available aliases
source worktrees/.worktree-env
worktree-help
```

## File Locations

```
kicad-sch-api/
├── scripts/
│   ├── setup-worktrees.sh       # Create worktrees
│   ├── verify-worktrees.sh      # Check setup
│   ├── sync-from-main.sh        # Keep in sync
│   ├── merge-to-main.sh         # Merge to main
│   ├── README.md                # Full documentation
│   └── QUICK_REFERENCE.md       # This file
├── worktrees/
│   ├── pin-discovery/           # Worktree 1
│   ├── wire-routing/            # Worktree 2
│   ├── testing-and-docs/        # Worktree 3
│   ├── .worktree-env            # Environment setup
│   └── README.md                # Worktree guide
└── .worktree-*.log              # Logs from scripts
```

## Related Documentation

- Full guide: `/scripts/README.md`
- Strategy: `/GIT_WORKTREE_STRATEGY.md`
- Parallel development: `/GIT_WORKTREE_PARALLEL_DEVELOPMENT.md`
- Project guide: `/CLAUDE.md`
