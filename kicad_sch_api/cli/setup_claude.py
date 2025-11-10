#!/usr/bin/env python3
"""
KiCad Schematic API - Claude Code Setup Command

Copies kicad-sch-api Claude Code commands to user's local .claude/ directory.

Usage:
    ksa_claude_setup
    ksa_claude_setup --verbose
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional


def get_package_claude_dir() -> Path:
    """Get the path to the .claude directory in the package."""
    # Get the package installation directory
    package_dir = Path(__file__).parent.parent.parent  # kicad-sch-api root
    claude_dir = package_dir / ".claude"

    if not claude_dir.exists():
        raise FileNotFoundError(
            f"Package .claude directory not found at {claude_dir}. "
            "This may indicate an installation issue."
        )

    return claude_dir


def copy_commands_with_prefix(
    source_dir: Path, target_dir: Path, prefix: str = "ksa-", verbose: bool = False
) -> int:
    """
    Copy .claude command files from source to target with a prefix.

    Args:
        source_dir: Source .claude/commands directory
        target_dir: Target .claude/commands directory
        prefix: Prefix to add to command files
        verbose: Print verbose output

    Returns:
        Number of files copied
    """
    copied_count = 0

    # Find all .md files in source commands directory
    source_commands = source_dir / "commands"
    if not source_commands.exists():
        if verbose:
            print(f"No commands directory found at {source_commands}")
        return 0

    for source_file in source_commands.rglob("*.md"):
        # Validate the file content
        try:
            content = source_file.read_text()
            # Basic validation: ensure it's markdown and not empty
            if not content.strip():
                if verbose:
                    print(f"  ⚠ Skipping empty file: {source_file.name}")
                continue

            # Ensure it starts with markdown (# or text, not binary)
            if "\x00" in content:
                if verbose:
                    print(f"  ⚠ Skipping binary file: {source_file.name}")
                continue

        except Exception as e:
            if verbose:
                print(f"  ⚠ Skipping unreadable file {source_file.name}: {e}")
            continue

        # Calculate relative path from commands directory
        rel_path = source_file.relative_to(source_commands)

        # Add prefix to the filename
        new_name = f"{prefix}{source_file.name}"
        target_file = target_dir / "commands" / rel_path.parent / new_name

        # Create parent directory if needed
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file (use copy instead of copy2 to set current timestamp)
        shutil.copy(source_file, target_file)
        copied_count += 1

        if verbose:
            print(f"  ✓ Copied: {rel_path} -> {target_file.relative_to(target_dir)}")

    return copied_count


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point for ksa_claude_setup.

    Args:
        argv: Command-line arguments (None = sys.argv)

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        prog="ksa_claude_setup",
        description="Install kicad-sch-api Claude Code commands to your .claude/ directory",
        epilog="Commands are prefixed with 'ksa-' to avoid naming conflicts.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output of files being copied",
    )

    args = parser.parse_args(argv)

    try:
        # Get user's home directory
        home_dir = Path.home()
        target_claude_dir = home_dir / ".claude"

        # Create .claude/commands if it doesn't exist
        target_commands_dir = target_claude_dir / "commands"
        target_commands_dir.mkdir(parents=True, exist_ok=True)

        if args.verbose:
            print(f"Target directory: {target_claude_dir}")

        # Get package .claude directory
        source_claude_dir = get_package_claude_dir()

        if args.verbose:
            print(f"Source directory: {source_claude_dir}")
            print(f"Copying commands with 'ksa-' prefix...")

        # Copy commands with prefix
        copied_count = copy_commands_with_prefix(
            source_dir=source_claude_dir,
            target_dir=target_claude_dir,
            prefix="ksa-",
            verbose=args.verbose,
        )

        # Success message
        print(f"✅ Setup complete! Copied {copied_count} commands to {target_claude_dir}/commands/")
        print(f"   Commands available in Claude Code:")

        # List some example commands
        example_commands = []
        for cmd_file in (target_commands_dir).rglob("ksa-*.md"):
            cmd_name = "/" + cmd_file.stem
            example_commands.append(cmd_name)
            if len(example_commands) >= 5:
                break

        for cmd in sorted(example_commands):
            print(f"   - {cmd}")

        if copied_count > 5:
            print(f"   ... and {copied_count - 5} more")

        return 0

    except PermissionError as e:
        print(f"❌ Permission error: {e}", file=sys.stderr)
        print(
            f"   Unable to write to {target_claude_dir}. Check permissions.",
            file=sys.stderr,
        )
        return 1

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def entry_point() -> None:
    """Entry point for setuptools console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
