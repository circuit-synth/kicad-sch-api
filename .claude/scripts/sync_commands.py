#!/usr/bin/env python3
"""
Sync commands from shared-library to target repo's .claude/commands directory.

This script copies all command files from the shared library to the target repo,
excluding files that start with underscore (which are for library use only).

Usage:
    python .scripts/sync_commands.py

    (assumes you're running from the target repo root directory)
"""

import shutil
from pathlib import Path
import sys


def sync_commands():
    """Copy shared commands to target repo."""

    # Determine paths
    target_repo = Path.cwd()
    target_commands = target_repo / ".claude" / "commands"

    # Find shared-library
    # First check if it's a submodule in current repo
    shared_lib = target_repo / "shared-library"

    if not shared_lib.exists():
        print(f"❌ Error: shared-library submodule not found at {shared_lib}")
        print("Please ensure shared-library is added as a submodule:")
        print("  git submodule add https://github.com/circuit-synth/shared-library.git shared-library")
        return False

    shared_commands = shared_lib / ".claude" / "commands"

    if not shared_commands.exists():
        print(f"❌ Error: shared commands not found at {shared_commands}")
        return False

    if not target_commands.exists():
        print(f"Creating {target_commands}")
        target_commands.mkdir(parents=True, exist_ok=True)

    # Sync commands
    synced_count = 0
    for cmd_file in shared_commands.glob("*.md"):
        # Skip files starting with underscore
        if cmd_file.name.startswith("_"):
            continue

        dest = target_commands / cmd_file.name
        shutil.copy2(cmd_file, dest)
        print(f"✓ Synced {cmd_file.name}")
        synced_count += 1

    print(f"\n✓ Successfully synced {synced_count} commands to {target_commands}")
    return True


if __name__ == "__main__":
    success = sync_commands()
    sys.exit(0 if success else 1)
