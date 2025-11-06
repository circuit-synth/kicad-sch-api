#!/bin/bash

################################################################################
# setup-worktrees.sh
#
# Creates git worktrees for parallel development on kicad-sch-api MCP pin
# connection project. Sets up three worktrees for independent feature branches:
#   - pin-discovery: Pin discovery and component traversal
#   - wire-routing: Wire endpoint analysis and routing
#   - testing-and-docs: Testing infrastructure and documentation
#
# Usage:
#   ./setup-worktrees.sh [--clean] [--verbose] [--help]
#
# Options:
#   --clean      Remove existing worktrees before setup
#   --verbose    Enable verbose output and debugging
#   --help       Show this help message
#
# Requirements:
#   - Git >= 2.17 (worktree support)
#   - Main branch up-to-date with origin
#   - No uncommitted changes in main working tree
#
# Example:
#   ./setup-worktrees.sh
#   ./setup-worktrees.sh --clean --verbose
#
################################################################################

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly WORKTREE_DIR="${REPO_ROOT}/worktrees"
readonly LOG_FILE="${REPO_ROOT}/.worktree-setup.log"

# Worktree configuration
declare -A WORKTREES=(
    [pin-discovery]="feat/pin-discovery"
    [wire-routing]="feat/wire-routing"
    [testing-and-docs]="feat/testing-and-docs"
)

# Flags
CLEAN_WORKTREES=false
VERBOSE=false

################################################################################
# Utility Functions
################################################################################

log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "${LOG_FILE}"

    if [[ "$VERBOSE" == true ]]; then
        echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $message"
    fi
}

error() {
    echo -e "${RED}ERROR:${NC} $@" >&2
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

section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$@${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "SECTION" "$@"
}

print_usage() {
    head -n 25 "$0" | tail -n 22
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

################################################################################
# Pre-flight Checks
################################################################################

check_prerequisites() {
    section "Checking Prerequisites"

    # Check Git version
    if ! command_exists git; then
        error "Git is not installed"
        return 1
    fi

    local git_version=$(git --version | awk '{print $3}')
    info "Git version: $git_version"

    # Check we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        return 1
    fi
    success "Git repository detected"

    # Check we're in the correct repo
    if [[ ! -d "$REPO_ROOT/.git" ]]; then
        error "Cannot find .git directory at expected location: $REPO_ROOT/.git"
        return 1
    fi
    success "Repository root verified: $REPO_ROOT"

    # Verify main branch exists
    if ! git rev-parse --verify main >/dev/null 2>&1; then
        error "Main branch does not exist"
        return 1
    fi
    success "Main branch exists"

    return 0
}

check_working_tree_clean() {
    section "Checking Working Tree Status"

    # Get current branch
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    info "Current branch: $current_branch"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        error "Uncommitted changes in main working tree. Please commit or stash changes."
        git status
        return 1
    fi
    success "Working tree is clean"

    # Check for untracked files (warning only)
    local untracked=$(git ls-files --others --exclude-standard)
    if [[ -n "$untracked" ]]; then
        warning "Untracked files detected (will not affect worktree setup)"
        if [[ "$VERBOSE" == true ]]; then
            echo "$untracked" | head -5
            echo "... (use --verbose to see all)"
        fi
    fi

    return 0
}

check_remote_status() {
    section "Checking Remote Status"

    info "Fetching latest from origin..."
    git fetch origin 2>&1 | grep -v "^From " | grep -v "^\[new" || true

    # Check if main is up to date
    local local_commit=$(git rev-parse main)
    local remote_commit=$(git rev-parse origin/main)

    if [[ "$local_commit" != "$remote_commit" ]]; then
        warning "Main branch is not in sync with origin/main"
        info "Local: $local_commit"
        info "Remote: $remote_commit"
        info "Run: git pull origin main"
        return 1
    fi

    success "Main branch is in sync with origin/main"
    return 0
}

################################################################################
# Worktree Management
################################################################################

remove_existing_worktrees() {
    section "Removing Existing Worktrees"

    if [[ ! -d "$WORKTREE_DIR" ]]; then
        info "No existing worktrees directory found"
        return 0
    fi

    local worktree_count=$(git worktree list | wc -l)
    info "Found $worktree_count worktrees"

    # List all worktrees
    if [[ "$VERBOSE" == true ]]; then
        info "Current worktrees:"
        git worktree list --porcelain
    fi

    # Remove each worktree
    for name in "${!WORKTREES[@]}"; do
        local worktree_path="${WORKTREE_DIR}/${name}"

        if [[ -d "$worktree_path" ]]; then
            info "Removing worktree: $name ($worktree_path)"

            # Remove the worktree
            if git worktree remove "$worktree_path" 2>/dev/null; then
                success "Removed worktree: $name"
            else
                warning "Could not remove worktree $name (may need --force)"
                if git worktree remove --force "$worktree_path" 2>/dev/null; then
                    success "Force removed worktree: $name"
                else
                    error "Failed to remove worktree: $name"
                    return 1
                fi
            fi
        fi
    done

    # Remove worktree directory if empty
    if [[ -d "$WORKTREE_DIR" ]] && [[ -z "$(ls -A "$WORKTREE_DIR")" ]]; then
        rm -rf "$WORKTREE_DIR"
        info "Removed empty worktree directory"
    fi

    return 0
}

create_worktree() {
    local worktree_name="$1"
    local branch_name="$2"
    local worktree_path="${WORKTREE_DIR}/${worktree_name}"

    info "Creating worktree: $worktree_name"
    info "  Branch: $branch_name"
    info "  Path: $worktree_path"

    # Create worktree directory structure
    mkdir -p "$WORKTREE_DIR"

    # Check if branch exists
    if git rev-parse --verify "$branch_name" >/dev/null 2>&1; then
        info "Branch $branch_name already exists, checking out..."
        if ! git worktree add "$worktree_path" "$branch_name" 2>&1 | tee -a "${LOG_FILE}"; then
            error "Failed to add worktree for branch: $branch_name"
            return 1
        fi
    else
        info "Creating new branch: $branch_name (from main)"
        if ! git worktree add -b "$branch_name" "$worktree_path" main 2>&1 | tee -a "${LOG_FILE}"; then
            error "Failed to create worktree with branch: $branch_name"
            return 1
        fi
    fi

    success "Worktree created: $worktree_name -> $branch_name"
    return 0
}

create_all_worktrees() {
    section "Creating Worktrees"

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        if ! create_worktree "$name" "$branch"; then
            error "Failed to create worktree: $name"
            return 1
        fi
    done

    success "All worktrees created successfully"
    return 0
}

################################################################################
# Configuration and Setup
################################################################################

setup_worktree_env() {
    section "Setting Up Worktree Environment"

    local env_file="${WORKTREE_DIR}/.worktree-env"

    cat > "$env_file" << 'EOF'
#!/bin/bash
# Worktree environment configuration
# Source this file to set up environment variables for worktree development

export KICAD_SCH_API_WORKTREE="true"
export KICAD_SCH_API_WORKTREE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export KICAD_SCH_API_REPO_ROOT="$(cd "${KICAD_SCH_API_WORKTREE_DIR}/.." && pwd)"

# Add helpful aliases
alias pin-discovery='cd "${KICAD_SCH_API_WORKTREE_DIR}/pin-discovery"'
alias wire-routing='cd "${KICAD_SCH_API_WORKTREE_DIR}/wire-routing"'
alias testing-and-docs='cd "${KICAD_SCH_API_WORKTREE_DIR}/testing-and-docs"'
alias repo='cd "${KICAD_SCH_API_REPO_ROOT}"'

# Help function
worktree-help() {
    echo "Worktree environment loaded:"
    echo "  KICAD_SCH_API_WORKTREE_DIR: $KICAD_SCH_API_WORKTREE_DIR"
    echo "  KICAD_SCH_API_REPO_ROOT: $KICAD_SCH_API_REPO_ROOT"
    echo ""
    echo "Available aliases:"
    echo "  pin-discovery     - Change to pin-discovery worktree"
    echo "  wire-routing      - Change to wire-routing worktree"
    echo "  testing-and-docs  - Change to testing-and-docs worktree"
    echo "  repo              - Change to repository root"
}
EOF

    chmod +x "$env_file"
    info "Created worktree environment file: $env_file"

    # Create symlinks for easy access
    local repo_env_link="${REPO_ROOT}/.worktree-env"
    if [[ ! -L "$repo_env_link" ]]; then
        ln -s "$env_file" "$repo_env_link"
        info "Created symlink: $repo_env_link"
    fi

    return 0
}

create_readme() {
    section "Creating Worktree Documentation"

    local readme="${WORKTREE_DIR}/README.md"

    cat > "$readme" << 'EOF'
# Git Worktrees for kicad-sch-api MCP Pin Connection

This directory contains git worktrees for parallel development on the MCP pin connection project.

## Worktrees

### pin-discovery (feat/pin-discovery)
- **Purpose**: Pin discovery and component traversal functionality
- **Focus**: Enhanced component navigation, pin finding, symbol caching
- **Tests**: Pin discovery tests, symbol library tests

### wire-routing (feat/wire-routing)
- **Purpose**: Wire endpoint analysis and routing enhancements
- **Focus**: Wire connectivity, endpoint detection, routing optimization
- **Tests**: Wire routing tests, connectivity tests

### testing-and-docs (feat/testing-and-docs)
- **Purpose**: Testing infrastructure and comprehensive documentation
- **Focus**: Test fixtures, examples, user guide, API documentation
- **Tests**: Integration tests, fixture tests, documentation examples

## Quick Start

### Source the environment
```bash
source .worktree-env
# Sets up aliases for easy navigation
```

### Navigate to a worktree
```bash
pin-discovery      # Go to pin-discovery worktree
wire-routing       # Go to wire-routing worktree
testing-and-docs   # Go to testing-and-docs worktree
repo               # Return to main repository
```

### Work in a worktree
```bash
cd worktrees/pin-discovery
git log --oneline     # See commits on this branch
git status            # Check current status
make test             # Run tests
```

## Development Workflow

### 1. Make changes in your worktree
```bash
pin-discovery
# Make changes to pin discovery code
git add kicad_sch_api/discovery/
git commit -m "feat: improve pin discovery"
```

### 2. Push your branch
```bash
git push origin feat/pin-discovery
```

### 3. Create a pull request
- Title: Descriptive title for the feature
- Body: Link to issue, describe changes, reference tests

### 4. Merge to main
Once approved, merge to main:
```bash
repo
../scripts/merge-to-main.sh
```

## Useful Commands

### Sync all branches with latest main
```bash
../scripts/sync-from-main.sh
```

### Verify worktree setup
```bash
../scripts/verify-worktrees.sh
```

### View all worktrees
```bash
git worktree list
```

### Check branch status
```bash
git log --oneline main..HEAD   # See commits not in main
git log --oneline HEAD..main   # See commits ahead in main
```

## Environment Variables

When you source `.worktree-env`:
- `KICAD_SCH_API_WORKTREE_DIR`: Path to worktrees directory
- `KICAD_SCH_API_REPO_ROOT`: Path to repository root
- `KICAD_SCH_API_WORKTREE`: Set to "true"

## Troubleshooting

### Worktree is locked
```bash
git worktree prune
git worktree list --porcelain
```

### Want to remove all worktrees
```bash
repo
../scripts/setup-worktrees.sh --clean
```

### Branch is behind main
```bash
git fetch origin
git rebase origin/main
```

## See Also

- `/CLAUDE.md` - Project guidelines and architecture
- `/GIT_WORKTREE_STRATEGY.md` - Detailed worktree strategy
- `/docs/` - API documentation
- `../scripts/` - Automation scripts
EOF

    success "Created worktree documentation: $readme"
    return 0
}

################################################################################
# Summary and Completion
################################################################################

print_summary() {
    section "Setup Summary"

    echo ""
    echo "Worktrees created successfully:"
    echo ""

    for name in "${!WORKTREES[@]}"; do
        local branch="${WORKTREES[$name]}"
        local path="${WORKTREE_DIR}/${name}"
        echo -e "  ${GREEN}✓${NC} ${name}"
        echo "    Branch:  $branch"
        echo "    Path:    $path"
        echo ""
    done

    echo "Next steps:"
    echo ""
    echo "1. View all worktrees:"
    echo "   git worktree list"
    echo ""
    echo "2. Navigate to a worktree:"
    echo "   cd ${WORKTREE_DIR}/pin-discovery"
    echo ""
    echo "3. Or source the environment for aliases:"
    echo "   source ${WORKTREE_DIR}/.worktree-env"
    echo "   pin-discovery"
    echo ""
    echo "4. Read the documentation:"
    echo "   cat ${WORKTREE_DIR}/README.md"
    echo ""

    log "SUCCESS" "All worktrees set up successfully"
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --clean)
                CLEAN_WORKTREES=true
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

    # Initialize log file
    cat > "${LOG_FILE}" << EOF
================================================================================
Git Worktree Setup Log
Started: $(date '+%Y-%m-%d %H:%M:%S')
================================================================================
EOF

    info "Log file: ${LOG_FILE}"
    info "Repository: ${REPO_ROOT}"
    info "Worktrees: ${WORKTREE_DIR}"

    # Run setup steps
    if ! check_prerequisites; then
        error "Prerequisites check failed"
        exit 1
    fi

    if ! check_working_tree_clean; then
        error "Working tree check failed"
        exit 1
    fi

    if ! check_remote_status; then
        error "Remote status check failed"
        exit 1
    fi

    # Clean existing worktrees if requested
    if [[ "$CLEAN_WORKTREES" == true ]]; then
        if ! remove_existing_worktrees; then
            error "Failed to remove existing worktrees"
            exit 1
        fi
    fi

    # Create new worktrees
    if ! create_all_worktrees; then
        error "Failed to create worktrees"
        exit 1
    fi

    # Setup environment
    if ! setup_worktree_env; then
        error "Failed to setup worktree environment"
        exit 1
    fi

    # Create documentation
    if ! create_readme; then
        error "Failed to create documentation"
        exit 1
    fi

    # Print summary
    print_summary

    success "Setup complete!"
    exit 0
}

# Execute main function
main "$@"
