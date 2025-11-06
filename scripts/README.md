# Git Worktree Automation Scripts

Production-ready bash scripts for automating git worktree setup and management for parallel development on the kicad-sch-api MCP pin connection project.

## Overview

These scripts enable safe, efficient parallel development across three independent feature branches:

- **pin-discovery** (`feat/pin-discovery`) - Pin discovery and component traversal
- **wire-routing** (`feat/wire-routing`) - Wire endpoint analysis and routing
- **testing-and-docs** (`feat/testing-and-docs`) - Testing infrastructure and documentation

## Scripts

### 1. `setup-worktrees.sh`

Creates all three git worktrees and initializes the worktree environment.

**Usage:**
```bash
./setup-worktrees.sh [--clean] [--verbose] [--help]
```

**Options:**
- `--clean` - Remove existing worktrees before setup
- `--verbose` - Enable verbose output and debugging
- `--help` - Show help message

**What it does:**
1. Validates git repository and prerequisites
2. Checks working tree is clean
3. Verifies main branch is up-to-date with origin
4. Creates three worktrees (or cleans and recreates with `--clean`)
5. Sets up worktree environment files and aliases
6. Creates README documentation in worktree directory

**Example:**
```bash
# First-time setup
./setup-worktrees.sh

# Reset all worktrees
./setup-worktrees.sh --clean

# Setup with debugging
./setup-worktrees.sh --verbose
```

**Output:**
- Creates `/worktrees/` directory with three subdirectories
- Creates `.worktree-env` file with shell aliases and environment variables
- Creates `worktrees/README.md` with worktree documentation
- Generates `.worktree-setup.log` for debugging

### 2. `verify-worktrees.sh`

Validates that all worktrees are properly configured and healthy.

**Usage:**
```bash
./verify-worktrees.sh [--verbose] [--fix] [--help]
```

**Options:**
- `--verbose` - Show detailed information for each worktree
- `--fix` - Attempt to fix common issues (prune locks, set up tracking, etc.)
- `--help` - Show help message

**What it checks:**
1. Git is installed and working
2. Repository is valid and on correct branch
3. All three worktrees exist in expected locations
4. Each worktree is on correct branch
5. No stale locks or prunable worktrees
6. Branch tracking is configured
7. Commit history is valid

**Example:**
```bash
# Quick verification
./verify-worktrees.sh

# Detailed report with debugging
./verify-worktrees.sh --verbose

# Fix common issues
./verify-worktrees.sh --fix

# Check and auto-fix
./verify-worktrees.sh --verbose --fix
```

**Output:**
- Displays health status for each worktree
- Shows commits ahead/behind main
- Lists any issues found
- Provides fix suggestions
- Generates `.worktree-verify.log` for debugging

### 3. `sync-from-main.sh`

Synchronizes all worktree branches with latest changes from main.

**Usage:**
```bash
./sync-from-main.sh [--strategy rebase|merge|fast-forward] [--verbose] [--dry-run] [--help]
```

**Options:**
- `--strategy` - Sync strategy (default: `rebase`)
  - `rebase` - Rebase branches on main (linear history)
  - `merge` - Merge main into branches (preserves history)
  - `fast-forward` - Fast-forward only (fails if not possible)
- `--verbose` - Show detailed information
- `--dry-run` - Preview changes without applying them
- `--help` - Show help message

**What it does:**
1. Fetches latest changes from origin
2. Validates working tree state
3. Synchronizes each worktree branch with main
4. Handles conflicts gracefully with clear instructions
5. Reports final status for all branches

**Example:**
```bash
# Rebase all branches on latest main
./sync-from-main.sh

# Merge main changes instead of rebasing
./sync-from-main.sh --strategy merge

# Preview what would happen
./sync-from-main.sh --dry-run --verbose

# Verbose output for debugging
./sync-from-main.sh --strategy rebase --verbose
```

**Output:**
- Shows progress for each worktree
- Handles merge/rebase conflicts with clear next steps
- Displays final status of all branches
- Generates `.worktree-sync.log` for debugging

### 4. `merge-to-main.sh`

Interactive script for merging feature branches back to main.

**Usage:**
```bash
./merge-to-main.sh [--all] [--dry-run] [--verbose] [--help]
```

**Options:**
- `--all` - Merge all branches without prompting
- `--dry-run` - Preview merges without making changes
- `--verbose` - Show detailed information and diffs
- `--help` - Show help message

**What it does:**
1. Validates main branch is clean and up-to-date
2. Lists available branches with commits ahead of main
3. Allows interactive selection of branches to merge
4. Shows changes for review before each merge
5. Performs merge with descriptive commit messages
6. Optionally pushes changes to origin
7. Provides clear summary and next steps

**Modes:**

**Interactive Mode (default):**
```bash
./merge-to-main.sh
# Select which branches to merge
# Review changes for each branch
# Confirm each merge before proceeding
```

**Automated Mode:**
```bash
./merge-to-main.sh --all
# Merges all branches with commits
# Still prompts for confirmation
```

**Example:**
```bash
# Interactive merge selection
./merge-to-main.sh

# Merge all branches without selection
./merge-to-main.sh --all

# Preview what would be merged
./merge-to-main.sh --dry-run --verbose

# Merge with detailed output
./merge-to-main.sh --verbose
```

**Output:**
- Lists branches with commit counts
- Displays file changes for review
- Creates merge commits with messages
- Reports merge status
- Optionally pushes to origin
- Generates `.worktree-merge.log` for debugging

## Quick Start

### 1. Initial Setup

```bash
cd /path/to/kicad-sch-api

# Create all worktrees
./scripts/setup-worktrees.sh

# Verify setup succeeded
./scripts/verify-worktrees.sh
```

### 2. Start Working

```bash
# Option A: Direct navigation
cd worktrees/pin-discovery
git log --oneline

# Option B: Using aliases (source environment first)
source worktrees/.worktree-env
pin-discovery    # Jump to pin-discovery worktree
git log --oneline
wire-routing     # Jump to wire-routing worktree
testing-and-docs # Jump to testing-and-docs worktree
repo             # Back to repository root
```

### 3. Daily Development Workflow

```bash
# Start work in a worktree
pin-discovery

# Make changes
vim kicad_sch_api/discovery/pin_finder.py
git add kicad_sch_api/discovery/
git commit -m "feat: improve pin discovery algorithm"

# Keep branch up-to-date with main
repo
../scripts/sync-from-main.sh

# Continue working
pin-discovery
git log --oneline main..HEAD  # See your commits
```

### 4. Complete a Feature

```bash
# Push your work
pin-discovery
git push origin feat/pin-discovery

# Create pull request on GitHub
# ... review and approve ...

# Merge when ready
repo
./scripts/merge-to-main.sh
# Select pin-discovery branch
# Review changes
# Confirm merge
# Choose to push to origin
```

## Development Workflow Example

### Scenario: Working on three features in parallel

```bash
# Setup
./scripts/setup-worktrees.sh

# Work on pin discovery
cd worktrees/pin-discovery
# ... make changes ...
git commit -m "feat: add pin discovery"
git push origin feat/pin-discovery

# Switch to wire routing
cd ../wire-routing
# ... make changes ...
git commit -m "feat: improve wire endpoint detection"
git push origin feat/wire-routing

# Switch to testing
cd ../testing-and-docs
# ... make changes ...
git commit -m "feat: add integration tests"
git push origin feat/testing-and-docs

# Keep all branches up-to-date if main changes
cd ../..
./scripts/sync-from-main.sh

# Merge completed features
./scripts/merge-to-main.sh
# Select which branches to merge
# Review and confirm
```

## Environment Variables

When you source `.worktree-env`:

```bash
source worktrees/.worktree-env
```

Available environment variables:
- `KICAD_SCH_API_WORKTREE` - Set to "true" when in worktree environment
- `KICAD_SCH_API_WORKTREE_DIR` - Path to worktrees directory
- `KICAD_SCH_API_REPO_ROOT` - Path to repository root

Available aliases:
- `pin-discovery` - Change to pin-discovery worktree
- `wire-routing` - Change to wire-routing worktree
- `testing-and-docs` - Change to testing-and-docs worktree
- `repo` - Change to repository root

## Common Tasks

### View all worktrees

```bash
git worktree list
```

### View commits in a branch

```bash
cd worktrees/pin-discovery
git log --oneline main..HEAD      # Commits not in main
git log --oneline HEAD..main      # Commits ahead in main
```

### Check branch status

```bash
cd worktrees/wire-routing
git status                         # Current status
git diff                           # Changes not staged
git diff --cached                  # Staged changes
```

### Switch between worktrees

```bash
# Without aliases
cd worktrees/pin-discovery
cd ../wire-routing

# With aliases
source worktrees/.worktree-env
pin-discovery
wire-routing
testing-and-docs
```

### Resolve merge conflicts

If `sync-from-main.sh` encounters conflicts:

```bash
# In the affected worktree
cd worktrees/pin-discovery

# Check status
git status

# Edit conflicted files
vim kicad_sch_api/core/component.py

# Complete the rebase
git rebase --continue
# OR abort if needed
git rebase --abort
```

### Clean up worktrees

```bash
# Remove all worktrees
./scripts/setup-worktrees.sh --clean

# Or manually
git worktree remove worktrees/pin-discovery
git worktree remove worktrees/wire-routing
git worktree remove worktrees/testing-and-docs
rm -rf worktrees/
```

### Troubleshooting

**Worktree is locked:**
```bash
./scripts/verify-worktrees.sh --fix
# Or manually
git worktree prune
```

**Stale worktree references:**
```bash
git worktree list --porcelain | grep prunable
git worktree prune --verbose
```

**Branch is behind main:**
```bash
./scripts/sync-from-main.sh
```

**Merge conflicts when syncing:**
```bash
# Resolve conflicts manually
cd worktrees/pin-discovery
# Edit conflicted files
git rebase --continue
```

**Cannot push branch:**
```bash
cd worktrees/pin-discovery
# Set up tracking
git branch -u origin/feat/pin-discovery
# Then push
git push
```

## Error Handling

All scripts include comprehensive error checking:

- **Prerequisites validation** - Ensures git is installed and repo is valid
- **Working tree checks** - Prevents operations with uncommitted changes
- **Safe defaults** - No force operations unless explicitly requested
- **Conflict detection** - Gracefully handles merge/rebase conflicts
- **Rollback capability** - Clear instructions for reverting operations

## Logging

Each script generates detailed logs:

- `.worktree-setup.log` - Setup operation log
- `.worktree-verify.log` - Verification results
- `.worktree-sync.log` - Synchronization log
- `.worktree-merge.log` - Merge operation log

View logs:
```bash
cat .worktree-setup.log
tail -f .worktree-verify.log
grep ERROR .worktree-merge.log
```

## Best Practices

### Before Starting Work

1. **Verify setup:**
   ```bash
   ./scripts/verify-worktrees.sh
   ```

2. **Sync with main:**
   ```bash
   ./scripts/sync-from-main.sh
   ```

### During Development

1. **Commit frequently:**
   ```bash
   git add [files]
   git commit -m "feat: descriptive message"
   ```

2. **Push regularly:**
   ```bash
   git push origin feat/pin-discovery
   ```

3. **Create pull requests** for code review before merging

### Before Merging

1. **Ensure tests pass:**
   ```bash
   make test
   ```

2. **Sync latest main:**
   ```bash
   ./scripts/sync-from-main.sh
   ```

3. **Review changes:**
   ```bash
   git diff main..HEAD
   ```

4. **Use interactive merge:**
   ```bash
   ./scripts/merge-to-main.sh
   ```

## File Permissions

All scripts require execute permissions:

```bash
chmod +x scripts/*.sh
```

This is done automatically by `setup-worktrees.sh`.

## Requirements

- **Git** >= 2.17 (for worktree support)
- **Bash** 4.0+ (for associative arrays)
- **Standard Unix tools** (grep, sed, awk, etc.)
- **Main branch** up-to-date with origin

## Support

For issues or questions:

1. Check script logs: `.worktree-*.log`
2. Run with `--verbose` flag for detailed output
3. Run `./scripts/verify-worktrees.sh --verbose` for diagnosis
4. See troubleshooting section above

## Related Documentation

- `/GIT_WORKTREE_STRATEGY.md` - Detailed worktree strategy
- `/GIT_WORKTREE_PARALLEL_DEVELOPMENT.md` - Parallel development guide
- `/CLAUDE.md` - Project guidelines and architecture
- `/docs/` - API documentation

## Script Features

### setup-worktrees.sh
- Comprehensive prerequisite checking
- Safe worktree creation with error recovery
- Automatic environment setup
- Documentation generation
- Detailed logging and progress reporting

### verify-worktrees.sh
- Complete health check system
- Issue detection and diagnosis
- Auto-fix capability for common problems
- Detailed status reporting
- Branch commit analysis

### sync-from-main.sh
- Multiple sync strategies (rebase/merge/fast-forward)
- Dry-run capability for preview
- Conflict handling with clear instructions
- Progress tracking
- Status reporting for all branches

### merge-to-main.sh
- Interactive branch selection
- Change preview before merge
- Automatic merge message generation
- Optional origin push
- Comprehensive merge summaries

## License

These scripts are part of the kicad-sch-api project.

## Version History

### v1.0.0 (Current)
- Initial release with four core scripts
- Comprehensive error handling
- Full logging support
- Interactive and automated modes
- Production-ready quality
