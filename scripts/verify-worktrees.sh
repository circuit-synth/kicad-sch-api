#!/bin/bash

################################################################################
# verify-worktrees.sh
#
# Validates that all worktrees are set up correctly and provides a health
# report on the worktree configuration. Checks:
#   - All required worktrees exist
#   - Branches are correctly configured
#   - No stale locks
#   - All branches track from main
#   - No divergence between branches
#
# Usage:
#   ./verify-worktrees.sh [--verbose] [--fix] [--help]
#
# Options:
#   --verbose    Show detailed information for each worktree
#   --fix        Attempt to fix common issues (prune locks, etc.)
#   --help       Show this help message
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
#
# Example:
#   ./verify-worktrees.sh
#   ./verify-worktrees.sh --verbose
#   ./verify-worktrees.sh --fix
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
readonly LOG_FILE="${REPO_ROOT}/.worktree-verify.log"

# Worktree configuration
declare -A WORKTREES=(
    [pin-discovery]="feat/pin-discovery"
    [wire-routing]="feat/wire-routing"
    [testing-and-docs]="feat/testing-and-docs"
)

# Flags
VERBOSE=false
FIX_ISSUES=false
ISSUES_FOUND=0

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
    ((ISSUES_FOUND++))
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

################################################################################
# Core Verification Functions
################################################################################

verify_prerequisites() {
    section "Verifying Prerequisites"

    # Check Git
    if ! command_exists git; then
        error "Git is not installed"
        return 1
    fi
    success "Git is installed"
    detail "Version: $(git --version)"

    # Check we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        return 1
    fi
    success "In a valid git repository"

    # Check repo root
    if [[ ! -d "$REPO_ROOT/.git" ]]; then
        error "Cannot find .git directory"
        return 1
    fi
    success "Repository root is correct"

    # Check main branch exists
    if ! git rev-parse --verify main >/dev/null 2>&1; then
        error "Main branch does not exist"
        return 1
    fi
    success "Main branch exists"

    return 0
}

verify_worktree_directory() {
    section "Verifying Worktree Directory"

    if [[ ! -d "$WORKTREE_DIR" ]]; then
        error "Worktree directory does not exist: $WORKTREE_DIR"
        return 1
    fi
    success "Worktree directory exists"
    detail "Location: $WORKTREE_DIR"

    return 0
}

verify_all_worktrees_exist() {
    section "Verifying All Worktrees Exist"

    local all_exist=true

    for name in "${!WORKTREES[@]}"; do
        local path="${WORKTREE_DIR}/${name}"
        local branch="${WORKTREES[$name]}"

        if [[ ! -d "$path" ]]; then
            error "Worktree missing: $name"
            detail "Expected path: $path"
            all_exist=false
        else
            success "Worktree exists: $name"
            detail "Path: $path"
        fi
    done

    if [[ "$all_exist" == false ]]; then
        warning "Some worktrees are missing. Run: ./setup-worktrees.sh"
        return 1
    fi

    return 0
}

verify_worktree_branches() {
    section "Verifying Worktree Branches"

    local all_correct=true

    for name in "${!WORKTREES[@]}"; do
        local expected_branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            error "Cannot verify branch for missing worktree: $name"
            all_correct=false
            continue
        fi

        # Get actual branch
        local actual_branch=$(cd "$path" && git rev-parse --abbrev-ref HEAD)

        if [[ "$actual_branch" == "$expected_branch" ]]; then
            success "Worktree $name is on correct branch"
            detail "Branch: $actual_branch"
        else
            error "Worktree $name is on wrong branch"
            detail "Expected: $expected_branch"
            detail "Actual: $actual_branch"
            all_correct=false
        fi
    done

    if [[ "$all_correct" == false ]]; then
        return 1
    fi

    return 0
}

verify_no_stale_locks() {
    section "Checking for Stale Locks"

    # Try to prune first
    if git worktree prune 2>/dev/null; then
        detail "Pruned stale worktree data"
    fi

    local locked_worktrees=0

    while IFS= read -r line; do
        if [[ "$line" =~ prunable ]]; then
            warning "Found stale worktree: $line"
            ((locked_worktrees++))

            if [[ "$FIX_ISSUES" == true ]]; then
                warning "Attempting to clean stale worktree..."
                git worktree prune --verbose
            fi
        fi
    done < <(git worktree list --porcelain)

    if [[ $locked_worktrees -eq 0 ]]; then
        success "No stale locks detected"
    else
        error "Found $locked_worktrees stale locks"
        if [[ "$FIX_ISSUES" == false ]]; then
            info "Run with --fix to clean up stale locks"
        fi
        return 1
    fi

    return 0
}

verify_branch_commits() {
    section "Verifying Branch Commit History"

    local all_commits_valid=true

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            continue
        fi

        info "Branch: $branch ($name)"

        # Get commit count on branch
        local commits_ahead=$(cd "$path" && git rev-list --count main..$branch 2>/dev/null || echo 0)
        local commits_behind=$(cd "$path" && git rev-list --count $branch..main 2>/dev/null || echo 0)

        detail "Commits ahead of main: $commits_ahead"
        detail "Commits behind main: $commits_behind"

        # Show recent commits if verbose
        if [[ "$VERBOSE" == true ]] && [[ $commits_ahead -gt 0 ]]; then
            detail "Recent commits:"
            cd "$path" && git log --oneline -3 main..$branch 2>/dev/null | while read -r line; do
                detail "  $line"
            done
        fi
    done

    return 0
}

verify_branch_tracking() {
    section "Verifying Branch Tracking"

    local all_tracking=true

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            continue
        fi

        # Check if branch is tracking origin
        local tracking=$(cd "$path" && git for-each-ref --format='%(upstream)' refs/heads/$branch)

        if [[ -z "$tracking" ]]; then
            warning "Branch $branch is not tracking origin"
            detail "Suggested: git branch -u origin/$branch"
            all_tracking=false
        else
            success "Branch $branch is tracking: $tracking"
        fi
    done

    if [[ "$all_tracking" == false ]] && [[ "$FIX_ISSUES" == true ]]; then
        info "Setting up tracking for branches..."
        for name in "${!WORKTREES[@]}"; do
            local branch="${WORKTREES[$name]}"
            local path="${WORKTREE_DIR}/${name}"

            if cd "$path" && ! git for-each-ref --format='%(upstream)' refs/heads/$branch | grep -q origin; then
                if git branch -u origin/$branch 2>/dev/null; then
                    success "Set tracking for $branch"
                fi
            fi
        done
    fi

    return 0
}

verify_worktree_status() {
    section "Verifying Worktree Status"

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            continue
        fi

        info "Worktree: $name"

        # Check working tree status
        cd "$path"

        # Uncommitted changes
        if ! git diff-index --quiet HEAD --; then
            warning "Uncommitted changes in $name"
            if [[ "$VERBOSE" == true ]]; then
                git status --short | head -5
            fi
        else
            detail "Working tree is clean"
        fi

        # Untracked files
        local untracked=$(git ls-files --others --exclude-standard | wc -l)
        if [[ $untracked -gt 0 ]]; then
            detail "Untracked files: $untracked"
        else
            detail "No untracked files"
        fi
    done

    return 0
}

verify_git_list() {
    section "Git Worktree List"

    echo ""
    git worktree list
    echo ""

    return 0
}

################################################################################
# Summary Functions
################################################################################

print_detailed_report() {
    section "Detailed Worktree Report"

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"

        if [[ ! -d "$path" ]]; then
            echo -e "${RED}[MISSING]${NC} $name"
            continue
        fi

        echo ""
        echo -e "${CYAN}Worktree: $name${NC}"
        echo "  Path:   $path"
        echo "  Branch: $branch"

        cd "$path"

        # Get HEAD info
        local head_hash=$(git rev-parse --short HEAD)
        local head_msg=$(git log -1 --pretty=%s)
        echo "  HEAD:   $head_hash - $head_msg"

        # Get tracking info
        local tracking=$(git for-each-ref --format='%(upstream)' refs/heads/$branch)
        if [[ -n "$tracking" ]]; then
            echo "  Track:  $tracking"
        fi

        # Get counts
        local ahead=$(git rev-list --count main..$branch 2>/dev/null || echo 0)
        local behind=$(git rev-list --count $branch..main 2>/dev/null || echo 0)
        echo "  Ahead:  $ahead commits"
        echo "  Behind: $behind commits"
    done

    echo ""
    return 0
}

print_summary() {
    section "Verification Summary"

    if [[ $ISSUES_FOUND -eq 0 ]]; then
        echo ""
        echo -e "${GREEN}All checks passed! Worktrees are properly configured.${NC}"
        echo ""
        echo "You can start working in the worktrees:"
        echo ""
        echo "  cd ${WORKTREE_DIR}/pin-discovery"
        echo "  cd ${WORKTREE_DIR}/wire-routing"
        echo "  cd ${WORKTREE_DIR}/testing-and-docs"
        echo ""
        return 0
    else
        echo ""
        echo -e "${RED}Found $ISSUES_FOUND issue(s) during verification.${NC}"
        echo ""
        echo "Common fixes:"
        echo "  1. Re-run setup:    ./setup-worktrees.sh"
        echo "  2. Fix issues:      ./verify-worktrees.sh --fix"
        echo "  3. View details:    ./verify-worktrees.sh --verbose"
        echo ""
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --verbose)
                VERBOSE=true
                shift
                ;;
            --fix)
                FIX_ISSUES=true
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

    # Initialize log
    cat > "${LOG_FILE}" << EOF
================================================================================
Git Worktree Verification Log
Started: $(date '+%Y-%m-%d %H:%M:%S')
================================================================================
EOF

    info "Verification started"
    info "Repository: ${REPO_ROOT}"
    info "Worktrees: ${WORKTREE_DIR}"

    # Run verification steps
    verify_prerequisites || true
    verify_worktree_directory || true
    verify_all_worktrees_exist || true
    verify_worktree_branches || true
    verify_no_stale_locks || true
    verify_branch_tracking || true
    verify_branch_commits || true
    verify_worktree_status || true
    verify_git_list

    # Print detailed report if verbose
    if [[ "$VERBOSE" == true ]]; then
        print_detailed_report
    fi

    # Print summary
    print_summary

    log "INFO" "Verification complete (Issues: $ISSUES_FOUND)"

    if [[ $ISSUES_FOUND -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Execute main function
main "$@"
