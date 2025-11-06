#!/bin/bash

################################################################################
# merge-to-main.sh
#
# Interactive script for merging feature branches from worktrees back to main.
# Provides options to:
#   - Select which branches to merge
#   - Review changes before merging
#   - Create merge commits with descriptive messages
#   - Verify merges succeeded
#   - Push changes to origin
#
# Usage:
#   ./merge-to-main.sh [--all] [--dry-run] [--verbose] [--help]
#
# Options:
#   --all        Merge all branches without prompting
#   --dry-run    Show what would be merged without making changes
#   --verbose    Show detailed information
#   --help       Show this help message
#
# Interactive mode (default):
#   - Choose which branches to merge
#   - Review each branch's changes
#   - Confirm before each merge
#
# Example:
#   ./merge-to-main.sh                 # Interactive mode
#   ./merge-to-main.sh --all          # Merge all branches
#   ./merge-to-main.sh --dry-run      # Preview without changes
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
readonly LOG_FILE="${REPO_ROOT}/.worktree-merge.log"

# Worktree configuration
declare -A WORKTREES=(
    [pin-discovery]="feat/pin-discovery"
    [wire-routing]="feat/wire-routing"
    [testing-and-docs]="feat/testing-and-docs"
)

# Descriptions for branches
declare -A BRANCH_DESCRIPTIONS=(
    [feat/pin-discovery]="Pin discovery and component traversal"
    [feat/wire-routing]="Wire endpoint analysis and routing"
    [feat/testing-and-docs]="Testing infrastructure and documentation"
)

# Flags
MERGE_ALL=false
DRY_RUN=false
VERBOSE=false
MERGES_COMPLETED=0
MERGE_FAILURES=0

# State
declare -a BRANCHES_TO_MERGE=()

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
    ((MERGE_FAILURES++))
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
    head -n 35 "$0" | tail -n 32
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Prompt for user input
prompt_yes_no() {
    local prompt="$1"
    local default="${2:-n}"

    while true; do
        if [[ "$default" == "y" ]]; then
            echo -ne "${CYAN}$prompt${NC} [Y/n]: "
        else
            echo -ne "${CYAN}$prompt${NC} [y/N]: "
        fi

        read -r response
        response="${response:-$default}"

        case "$response" in
            [yY])
                return 0
                ;;
            [nN])
                return 1
                ;;
            *)
                echo "Please answer y or n"
                ;;
        esac
    done
}

# Display text with paging
display_content() {
    local content="$1"
    local lines=$(echo "$content" | wc -l)

    if [[ $lines -gt 20 ]] && command_exists less; then
        echo "$content" | less -R
    else
        echo "$content"
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

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        error "Uncommitted changes in main working tree"
        if prompt_yes_no "Stash changes and continue?"; then
            if ! git stash; then
                error "Failed to stash changes"
                return 1
            fi
            success "Stashed changes"
        else
            error "Cannot proceed with uncommitted changes"
            return 1
        fi
    else
        success "Main working tree is clean"
    fi

    return 0
}

################################################################################
# Branch Selection
################################################################################

select_branches_interactive() {
    section "Select Branches to Merge"

    echo ""
    echo "Available branches to merge:"
    echo ""

    local idx=1
    declare -a available_branches
    declare -a branch_names

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local desc="${BRANCH_DESCRIPTIONS[$branch]:-}"
        local path="${WORKTREE_DIR}/${name}"

        # Check if branch has commits ahead of main
        if [[ -d "$path" ]]; then
            cd "$path"
            local ahead=$(git rev-list --count main..HEAD 2>/dev/null || echo 0)

            if [[ $ahead -gt 0 ]]; then
                available_branches+=("$branch")
                branch_names+=("$name")

                echo "  $idx. $name"
                echo "     Branch:  $branch"
                echo "     Commits: $ahead"
                echo "     Description: $desc"
                echo ""

                ((idx++))
            else
                detail "Skipping $name (no commits ahead of main)"
            fi
        fi
    done

    if [[ ${#available_branches[@]} -eq 0 ]]; then
        warning "No branches have commits ahead of main"
        return 1
    fi

    echo ""
    echo "Enter branch numbers to merge (comma-separated, e.g., 1,2 or 'all'):"
    echo "Press Enter to cancel"
    echo ""

    read -r selection

    if [[ -z "$selection" ]]; then
        warning "Merge cancelled"
        return 1
    fi

    if [[ "$selection" == "all" ]]; then
        BRANCHES_TO_MERGE=("${available_branches[@]}")
        return 0
    fi

    # Parse selections
    IFS=',' read -ra selections <<< "$selection"
    for sel in "${selections[@]}"; do
        sel=$(echo "$sel" | xargs) # trim whitespace
        if [[ "$sel" =~ ^[0-9]+$ ]]; then
            local idx=$((sel - 1))
            if [[ $idx -ge 0 ]] && [[ $idx -lt ${#available_branches[@]} ]]; then
                BRANCHES_TO_MERGE+=("${available_branches[$idx]}")
            else
                warning "Invalid selection: $sel"
            fi
        fi
    done

    if [[ ${#BRANCHES_TO_MERGE[@]} -eq 0 ]]; then
        warning "No valid branches selected"
        return 1
    fi

    return 0
}

################################################################################
# Branch Analysis
################################################################################

show_branch_changes() {
    local branch="$1"
    local name="$2"

    section "Changes in Branch: $name ($branch)"

    # Find the worktree path
    local path=""
    for wname in "${!WORKTREES[@]}"; do
        if [[ "${WORKTREES[$wname]}" == "$branch" ]]; then
            path="${WORKTREE_DIR}/${wname}"
            break
        fi
    done

    if [[ -z "$path" ]]; then
        error "Cannot find worktree for branch: $branch"
        return 1
    fi

    cd "$path"

    # Show commits
    echo ""
    echo -e "${CYAN}Commits (compared to main):${NC}"
    echo ""
    git log --oneline main..$branch

    echo ""
    echo -e "${CYAN}Files Changed:${NC}"
    echo ""
    git diff --name-status main..$branch

    if [[ "$VERBOSE" == true ]]; then
        echo ""
        echo -e "${CYAN}Full Diff:${NC}"
        echo ""
        git diff main..$branch | head -100
    fi

    return 0
}

################################################################################
# Merging
################################################################################

merge_branch() {
    local branch="$1"
    local name="$2"

    info "Merging: $name ($branch)"

    # Verify branch is still valid
    if ! git rev-parse --verify "$branch" >/dev/null 2>&1; then
        error "Branch does not exist: $branch"
        return 1
    fi

    # Check if already merged
    if git log main..$branch --oneline | grep -q .; then
        : # Branch has commits to merge
    else
        warning "Branch is already fully merged into main"
        return 0
    fi

    # Create merge message
    local merge_msg="Merge branch '$branch' into main"

    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would merge: $branch"
        detail "Merge message: $merge_msg"
        return 0
    fi

    # Perform merge
    if git merge --no-ff "$branch" -m "$merge_msg"; then
        success "Merged: $name"
        ((MERGES_COMPLETED++))
        return 0
    else
        error "Merge failed for: $name"
        warning "Resolve conflicts manually and complete the merge"
        detail "After resolving: git add . && git commit"
        detail "To abort: git merge --abort"
        return 1
    fi
}

merge_all_branches() {
    section "Merging Branches to Main"

    if [[ ${#BRANCHES_TO_MERGE[@]} -eq 0 ]]; then
        warning "No branches selected for merge"
        return 1
    fi

    # Checkout main
    if ! git checkout main; then
        error "Failed to checkout main"
        return 1
    fi

    success "Checked out main"

    echo ""

    for branch in "${BRANCHES_TO_MERGE[@]}"; do
        # Find the worktree name
        local wname=""
        for wn in "${!WORKTREES[@]}"; do
            if [[ "${WORKTREES[$wn]}" == "$branch" ]]; then
                wname="$wn"
                break
            fi
        done

        # Show changes
        if ! show_branch_changes "$branch" "$wname"; then
            error "Failed to show changes for: $branch"
            ((MERGE_FAILURES++))
            continue
        fi

        echo ""

        # Ask for confirmation
        if prompt_yes_no "Merge $wname into main?"; then
            if merge_branch "$branch" "$wname"; then
                success "Successfully merged: $wname"
            else
                error "Failed to merge: $wname"
            fi
        else
            info "Skipped: $wname"
        fi

        echo ""
    done

    return 0
}

################################################################################
# Post-Merge
################################################################################

show_merge_summary() {
    section "Merge Summary"

    echo ""
    echo "Merges completed: $MERGES_COMPLETED"
    echo "Merge failures:   $MERGE_FAILURES"
    echo ""

    if [[ $MERGES_COMPLETED -gt 0 ]]; then
        echo "Successfully merged branches:"
        for branch in "${BRANCHES_TO_MERGE[@]}"; do
            # This is a simplified view - actual tracking would be needed
            echo "  - $branch"
        done
        echo ""

        echo "Next steps:"
        echo "  1. Review merged changes: git log -p --oneline main"
        echo "  2. Run tests: make test"
        echo "  3. Push to origin: git push origin main"
        echo ""
    fi

    if [[ $MERGE_FAILURES -gt 0 ]]; then
        echo -e "${RED}Merge conflicts occurred. Please resolve them:${NC}"
        echo "  1. Check status: git status"
        echo "  2. Resolve conflicts in editor"
        echo "  3. Complete merge: git add . && git commit"
        echo "  4. Or abort: git merge --abort"
        echo ""
    fi

    return 0
}

prompt_push_origin() {
    if [[ "$DRY_RUN" == true ]]; then
        info "[DRY RUN] Would push to origin"
        return 0
    fi

    if [[ $MERGES_COMPLETED -eq 0 ]]; then
        info "No merges completed, skipping push"
        return 0
    fi

    echo ""

    if prompt_yes_no "Push merged changes to origin?"; then
        info "Pushing main to origin..."

        if git push origin main; then
            success "Pushed to origin"
            return 0
        else
            error "Failed to push to origin"
            warning "Push manually: git push origin main"
            return 1
        fi
    else
        info "Skipped push. Remember to push later: git push origin main"
        return 0
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --all)
                MERGE_ALL=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
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
Git Worktree Merge Log
Started: $(date '+%Y-%m-%d %H:%M:%S')
Dry-run: $DRY_RUN
================================================================================
EOF

    if [[ "$DRY_RUN" == true ]]; then
        warning "DRY RUN MODE - No changes will be made"
    fi

    info "Merge process started"
    info "Repository: ${REPO_ROOT}"

    # Check prerequisites
    if ! check_prerequisites; then
        error "Prerequisites check failed"
        exit 1
    fi

    # Check main working tree
    if ! check_main_working_tree; then
        error "Main branch check failed"
        exit 1
    fi

    # Change to repo root
    cd "$REPO_ROOT"

    # Select branches to merge
    if [[ "$MERGE_ALL" == true ]]; then
        info "Merge all mode enabled"
        BRANCHES_TO_MERGE=("${!WORKTREES[@]}")
        # Convert names to branches
        local temp_branches=()
        for name in "${BRANCHES_TO_MERGE[@]}"; do
            temp_branches+=("${WORKTREES[$name]}")
        done
        BRANCHES_TO_MERGE=("${temp_branches[@]}")
    else
        if ! select_branches_interactive; then
            error "No branches selected"
            exit 1
        fi
    fi

    # Merge branches
    if ! merge_all_branches; then
        error "Merge process encountered errors"
    fi

    # Show summary
    show_merge_summary

    # Ask about push
    prompt_push_origin || true

    # Return appropriate exit code
    if [[ $MERGE_FAILURES -eq 0 ]]; then
        log "SUCCESS" "Merge process completed successfully"
        exit 0
    else
        log "ERROR" "Merge process encountered failures"
        exit 1
    fi
}

# Execute main function
main "$@"
