#!/bin/bash

################################################################################
# sync-from-main.sh
#
# Synchronizes all worktree branches with the latest changes from main.
# Optionally rebases or merges main into each worktree branch.
#
# Strategy options:
#   rebase   - Rebase branches on top of main (keeps linear history)
#   merge    - Merge main into branches (keeps all history)
#   fast-forward - Only succeeds if fast-forward is possible
#
# Usage:
#   ./sync-from-main.sh [--strategy rebase|merge|fast-forward] [--verbose] [--dry-run] [--help]
#
# Options:
#   --strategy   Sync strategy (default: rebase)
#   --verbose    Show detailed information
#   --dry-run    Show what would be done without making changes
#   --help       Show this help message
#
# Example:
#   ./sync-from-main.sh
#   ./sync-from-main.sh --strategy merge --verbose
#   ./sync-from-main.sh --dry-run
#
################################################################################

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly WORKTREE_DIR="${REPO_ROOT}/worktrees"
readonly LOG_FILE="${REPO_ROOT}/.worktree-sync.log"

# Worktree configuration
declare -A WORKTREES=(
    [pin-discovery]="feat/pin-discovery"
    [wire-routing]="feat/wire-routing"
    [testing-and-docs]="feat/testing-and-docs"
)

# Flags
SYNC_STRATEGY="rebase"
VERBOSE=false
DRY_RUN=false
SYNC_FAILURES=0
SYNC_CONFLICTS=0

################################################################################
# Utility Functions
################################################################################

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "${LOG_FILE}"
}

error() {
    echo -e "${RED}✗${NC} $@" >&2
    ((SYNC_FAILURES++))
    log "ERROR" "$@"
}

success() {
    echo -e "${GREEN}✓${NC} $@"
    log "SUCCESS" "$@"
}

info() {
    echo -e "${BLUE}ℹ${NC} $@"
    log "INFO" "$@"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $@"
    log "WARNING" "$@"
}

detail() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "  ${CYAN}→${NC} $@"
    fi
}

section() {
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}$@${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "SECTION" "$@"
}

print_usage() {
    head -n 30 "$0" | tail -n 27
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Execute command with optional dry-run
execute() {
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}[DRY RUN]${NC} $@"
        log "DRY_RUN" "$@"
        return 0
    else
        "$@"
    fi
}

################################################################################
# Pre-flight Checks
################################################################################

check_prerequisites() {
    section "Checking Prerequisites"

    # Check Git
    if ! command_exists git; then
        error "Git is not installed"
        return 1
    fi
    success "Git is installed"

    # Check we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        return 1
    fi
    success "In a valid git repository"

    # Check main branch exists
    if ! git rev-parse --verify main >/dev/null 2>&1; then
        error "Main branch does not exist"
        return 1
    fi
    success "Main branch exists"

    return 0
}

check_main_working_tree() {
    section "Checking Main Branch Status"

    info "Current branch: $(git rev-parse --abbrev-ref HEAD)"

    # Check for uncommitted changes in main
    if ! git diff-index --quiet HEAD --; then
        error "Uncommitted changes in main working tree"
        warning "Stash or commit changes before syncing"
        return 1
    fi
    success "Main working tree is clean"

    return 0
}

fetch_latest() {
    section "Fetching Latest from Origin"

    if execute git fetch origin main; then
        success "Fetched latest from origin"
    else
        error "Failed to fetch from origin"
        return 1
    fi

    return 0
}

################################################################################
# Synchronization
################################################################################

sync_worktree_rebase() {
    local name="$1"
    local branch="$2"
    local path="$3"

    info "Syncing $name using rebase strategy"

    cd "$path"

    # Check if branch is already rebasing
    if [[ -d ".git/rebase-merge" ]]; then
        error "Rebase in progress for $name. Resolve manually."
        return 1
    fi

    # Show status before
    detail "Before: $(git log -1 --oneline)"

    # Rebase on main
    if execute git rebase main; then
        success "Rebased $name on main"
        detail "After: $(git log -1 --oneline)"
        return 0
    else
        # Rebase failed - likely conflicts
        error "Rebase failed for $name (conflicts detected)"
        detail "Resolve conflicts manually in: $path"
        detail "Then run: git rebase --continue"
        detail "Or to abort: git rebase --abort"
        ((SYNC_CONFLICTS++))
        return 1
    fi
}

sync_worktree_merge() {
    local name="$1"
    local branch="$2"
    local path="$3"

    info "Syncing $name using merge strategy"

    cd "$path"

    # Check if branch is already merging
    if [[ -f ".git/MERGE_HEAD" ]]; then
        error "Merge in progress for $name. Resolve manually."
        return 1
    fi

    # Show status before
    detail "Before: $(git log -1 --oneline)"

    # Merge main
    if execute git merge main; then
        success "Merged main into $name"
        detail "After: $(git log -1 --oneline)"
        return 0
    else
        # Merge failed - likely conflicts
        error "Merge failed for $name (conflicts detected)"
        detail "Resolve conflicts manually in: $path"
        detail "Then run: git add . && git commit -m 'Merge main into $branch'"
        detail "Or to abort: git merge --abort"
        ((SYNC_CONFLICTS++))
        return 1
    fi
}

sync_worktree_fast_forward() {
    local name="$1"
    local branch="$2"
    local path="$3"

    info "Syncing $name using fast-forward strategy"

    cd "$path"

    # Check if fast-forward is possible
    local merge_base=$(git merge-base main HEAD)
    local main_head=$(git rev-parse main)

    if [[ "$merge_base" != "$(git rev-parse HEAD)" ]]; then
        error "Fast-forward not possible for $name (divergent history)"
        detail "Branch has local commits not in main"
        return 1
    fi

    # Show status before
    detail "Before: $(git log -1 --oneline)"

    # Fast-forward merge
    if execute git merge --ff-only main; then
        success "Fast-forward merged main into $name"
        detail "After: $(git log -1 --oneline)"
        return 0
    else
        error "Fast-forward merge failed for $name"
        return 1
    fi
}

sync_worktree() {
    local name="$1"
    local branch="$2"
    local path="$3"

    info "Synchronizing: $name ($branch)"

    if [[ ! -d "$path" ]]; then
        error "Worktree not found: $path"
        return 1
    fi

    # Check worktree status
    if [[ ! -d "$path/.git" ]]; then
        error "Not a valid git worktree: $path"
        return 1
    fi

    cd "$path"

    # Verify we're on the correct branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$current_branch" != "$branch" ]]; then
        error "Worktree is on wrong branch: $current_branch (expected $branch)"
        return 1
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        error "Uncommitted changes in $name"
        warning "Commit or stash changes before syncing"
        return 1
    fi

    # Sync based on strategy
    case "$SYNC_STRATEGY" in
        rebase)
            sync_worktree_rebase "$name" "$branch" "$path"
            ;;
        merge)
            sync_worktree_merge "$name" "$branch" "$path"
            ;;
        fast-forward)
            sync_worktree_fast_forward "$name" "$branch" "$path"
            ;;
        *)
            error "Unknown sync strategy: $SYNC_STRATEGY"
            return 1
            ;;
    esac

    return $?
}

sync_all_worktrees() {
    section "Synchronizing All Worktrees"

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if sync_worktree "$name" "$branch" "$path"; then
            success "Successfully synced: $name"
        else
            error "Failed to sync: $name"
        fi

        echo ""
    done

    return 0
}

################################################################################
# Summary Functions
################################################################################

print_summary() {
    section "Synchronization Summary"

    echo ""
    echo "Strategy: $SYNC_STRATEGY"
    echo "Dry run: $DRY_RUN"
    echo ""

    if [[ $SYNC_CONFLICTS -eq 0 ]] && [[ $SYNC_FAILURES -eq 0 ]]; then
        echo -e "${GREEN}All worktrees synchronized successfully!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}Synchronization encountered issues:${NC}"
        echo "  Conflicts: $SYNC_CONFLICTS"
        echo "  Failures:  $SYNC_FAILURES"
        echo ""

        if [[ $SYNC_CONFLICTS -gt 0 ]]; then
            echo "Next steps:"
            echo "  1. Resolve conflicts in affected worktrees"
            echo "  2. Complete the rebase/merge"
            echo "  3. Re-run this script to verify"
            echo ""
        fi

        return 1
    fi
}

print_detailed_status() {
    section "Worktree Status After Sync"

    echo ""
    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            echo -e "${RED}[MISSING]${NC} $name"
            continue
        fi

        cd "$path"

        local ahead=$(git rev-list --count main..HEAD 2>/dev/null || echo 0)
        local behind=$(git rev-list --count HEAD..main 2>/dev/null || echo 0)
        local head=$(git rev-parse --short HEAD)
        local msg=$(git log -1 --pretty=%s)

        echo -e "${CYAN}$name${NC}"
        echo "  HEAD:   $head - $msg"
        echo "  Ahead:  $ahead commits"
        echo "  Behind: $behind commits"
        echo ""
    done

    return 0
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --strategy)
                SYNC_STRATEGY="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help)
                print_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Validate strategy
    if [[ ! "$SYNC_STRATEGY" =~ ^(rebase|merge|fast-forward)$ ]]; then
        error "Invalid sync strategy: $SYNC_STRATEGY"
        error "Valid options: rebase, merge, fast-forward"
        exit 1
    fi

    # Initialize log
    cat > "${LOG_FILE}" << EOF
================================================================================
Git Worktree Synchronization Log
Started: $(date '+%Y-%m-%d %H:%M:%S')
Strategy: $SYNC_STRATEGY
Dry-run: $DRY_RUN
================================================================================
EOF

    if [[ "$DRY_RUN" == true ]]; then
        warning "DRY RUN MODE - No changes will be made"
    fi

    info "Synchronization started"
    info "Repository: ${REPO_ROOT}"
    info "Worktrees: ${WORKTREE_DIR}"
    info "Strategy: $SYNC_STRATEGY"

    # Run checks
    if ! check_prerequisites; then
        error "Prerequisites check failed"
        exit 1
    fi

    if ! check_main_working_tree; then
        error "Main branch check failed"
        exit 1
    fi

    if ! fetch_latest; then
        error "Failed to fetch latest changes"
        exit 1
    fi

    # Sync worktrees
    sync_all_worktrees

    # Print detailed status if verbose
    if [[ "$VERBOSE" == true ]]; then
        print_detailed_status
    fi

    # Print summary
    print_summary

    # Return appropriate exit code
    if [[ $SYNC_CONFLICTS -eq 0 ]] && [[ $SYNC_FAILURES -eq 0 ]]; then
        log "SUCCESS" "All worktrees synced successfully"
        exit 0
    else
        log "ERROR" "Sync encountered issues (Conflicts: $SYNC_CONFLICTS, Failures: $SYNC_FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
