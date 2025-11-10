#!/usr/bin/env python3
"""
KiCad Schematic API - Find KiCAD Symbol Libraries

Searches the filesystem for KiCAD symbol library directories using smart,
targeted search to avoid slow full-filesystem scans.

Usage:
    ksa_find_libraries
    ksa_find_libraries --verbose
    ksa_find_libraries --full-search
"""

import argparse
import platform
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def fast_search_macos() -> List[Path]:
    """Use macOS Spotlight (mdfind) for instant search."""
    print("Using macOS Spotlight (fast)...")

    results = set()

    try:
        # Search for .kicad_sym files using Spotlight
        result = subprocess.run(
            ["mdfind", "-name", ".kicad_sym"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line and line.endswith(".kicad_sym"):
                    # Get parent directory
                    path = Path(line).parent
                    results.add(path)

        print(f"  Found {len(results)} potential directories")
        return list(results)

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  Spotlight search failed: {e}")
        return []


def fast_search_linux() -> List[Path]:
    """Use locate command for fast search on Linux."""
    print("Using locate database (fast)...")

    results = set()

    try:
        # Try updatedb first if we have permission
        subprocess.run(["updatedb"], capture_output=True, timeout=30)
    except:
        pass  # May not have permission, that's OK

    try:
        result = subprocess.run(
            ["locate", "*.kicad_sym"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line and line.endswith(".kicad_sym"):
                    path = Path(line).parent
                    results.add(path)

        print(f"  Found {len(results)} potential directories")
        return list(results)

    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  locate search failed: {e}")
        return []


def targeted_search_directories() -> List[Path]:
    """Search only likely directories for KiCAD installations."""
    print("Searching common KiCAD installation directories...")

    system = platform.system()
    search_dirs = []

    if system == "Darwin":  # macOS
        # Search /Applications for KiCAD app bundles specifically
        base_apps = Path("/Applications")
        kicad_apps = []

        if base_apps.exists():
            # Find KiCad*.app directories
            for app_dir in base_apps.glob("KiCad*.app"):
                # Look inside app bundle for symbols
                symbols_path = app_dir / "Contents/SharedSupport/symbols"
                if symbols_path.exists():
                    kicad_apps.append(symbols_path)

        search_dirs = kicad_apps + [
            Path("/Applications"),
            Path.home() / "Applications",
            Path("/opt"),
            Path.home() / "Library/Application Support",
        ]
    elif system == "Linux":
        search_dirs = [
            Path("/usr/share/kicad"),
            Path("/usr/local/share/kicad"),
            Path("/opt"),
            Path.home() / ".local/share/kicad",
        ]
    elif system == "Windows":
        search_dirs = [
            Path("C:/Program Files/KiCad"),
            Path("C:/Program Files (x86)/KiCad"),
            Path.home() / "AppData/Local/KiCad",
        ]

    results = set()

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # If this IS a symbols directory (from KiCad app bundle), add it directly
        if search_dir.name == "symbols" and list(search_dir.glob("*.kicad_sym")):
            print(f"  Found KiCAD symbols: {search_dir}")
            results.add(search_dir)
            continue

        print(f"  Searching {search_dir}...")

        try:
            # Search for .kicad_sym files up to 5 levels deep
            for sym_file in search_dir.rglob("*.kicad_sym"):
                results.add(sym_file.parent)
                # Limit depth to avoid going too deep
                if len(sym_file.parts) - len(search_dir.parts) > 5:
                    continue
        except PermissionError:
            print(f"    ⚠️  Permission denied")
            continue
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
            continue

    print(f"  Found {len(results)} potential directories")
    return list(results)


def filter_library_directories(
    directories: List[Path], min_libraries: int = 50
) -> List[Tuple[Path, int]]:
    """
    Filter directories to find those with significant library collections.

    Args:
        directories: List of directories to check
        min_libraries: Minimum number of .kicad_sym files to be considered valid

    Returns:
        List of (directory, library_count) tuples, sorted by count descending
    """
    valid_dirs = []

    for directory in directories:
        try:
            if not directory.exists() or not directory.is_dir():
                continue

            # Count .kicad_sym files in this directory (not recursive)
            sym_files = list(directory.glob("*.kicad_sym"))
            count = len(sym_files)

            if count >= min_libraries:
                valid_dirs.append((directory, count))

        except (PermissionError, OSError):
            continue

    # Sort by count descending (more libraries = better)
    valid_dirs.sort(key=lambda x: x[1], reverse=True)

    return valid_dirs


def prioritize_official_installations(
    directories: List[Tuple[Path, int]],
) -> List[Tuple[Path, int, str]]:
    """
    Prioritize official KiCAD installations over custom library folders.

    Returns list of (path, count, priority_label) tuples.
    """
    prioritized = []

    for directory, count in directories:
        path_str = str(directory).lower()

        # Detect KiCAD version and priority
        priority = "custom"

        if "kicad" in path_str:
            if "kicad9" in path_str or "kicad/9" in path_str:
                priority = "kicad-9-official"
            elif "kicad8" in path_str or "kicad/8" in path_str:
                priority = "kicad-8-official"
            elif "kicad7" in path_str or "kicad/7" in path_str:
                priority = "kicad-7-official"
            else:
                priority = "kicad-official"

        prioritized.append((directory, count, priority))

    # Sort by priority (newer versions first)
    priority_order = {
        "kicad-9-official": 0,
        "kicad-8-official": 1,
        "kicad-7-official": 2,
        "kicad-official": 3,
        "custom": 4,
    }

    prioritized.sort(key=lambda x: (priority_order.get(x[2], 99), -x[1]))

    return prioritized


def format_env_var_suggestion(path: Path) -> str:
    """Generate environment variable export command for the path."""
    system = platform.system()
    path_str = str(path)

    # Detect which version variable to use
    path_lower = path_str.lower()
    if "kicad9" in path_lower or "kicad/9" in path_lower:
        var_name = "KICAD9_SYMBOL_DIR"
    elif "kicad8" in path_lower or "kicad/8" in path_lower:
        var_name = "KICAD8_SYMBOL_DIR"
    elif "kicad7" in path_lower or "kicad/7" in path_lower:
        var_name = "KICAD7_SYMBOL_DIR"
    else:
        var_name = "KICAD_SYMBOL_DIR"

    if system == "Windows":
        return f'$env:{var_name}="{path_str}"'
    else:
        return f'export {var_name}="{path_str}"'


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point for ksa_find_libraries.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        prog="ksa_find_libraries",
        description="Find KiCAD symbol library directories on your system",
        epilog="Searches common locations and uses platform-specific fast search.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed search progress",
    )

    parser.add_argument(
        "--min-libraries",
        type=int,
        default=50,
        help="Minimum number of .kicad_sym files to consider valid (default: 50)",
    )

    args = parser.parse_args(argv)

    print_header("KiCAD Symbol Library Finder")

    # Phase 1: Try fast search
    candidates = []

    system = platform.system()
    if system == "Darwin":
        candidates = fast_search_macos()
    elif system == "Linux":
        candidates = fast_search_linux()

    # Phase 2: Always add targeted directory search (finds KiCAD app bundles on macOS)
    print("\nAdding targeted search for KiCAD installations...")
    targeted_results = targeted_search_directories()
    candidates.extend(targeted_results)
    # Remove duplicates
    candidates = list(set(candidates))

    if not candidates:
        print("\n❌ No KiCAD library directories found")
        print("\nTroubleshooting:")
        print("1. Is KiCAD installed?")
        print("2. Check installation in standard locations:")
        if system == "Darwin":
            print("   - /Applications/KiCad*.app/")
        elif system == "Linux":
            print("   - /usr/share/kicad/")
            print("   - ~/.local/share/kicad/")
        elif system == "Windows":
            print("   - C:\\Program Files\\KiCad\\")
        return 1

    # Filter to valid library directories
    print(f"\nFiltering {len(candidates)} candidates (min {args.min_libraries} libraries)...")
    valid_dirs = filter_library_directories(candidates, args.min_libraries)

    if not valid_dirs:
        print(f"\n❌ No directories with {args.min_libraries}+ library files found")
        print(f"\nFound {len(candidates)} directories, but none had enough libraries.")
        print("Try lowering --min-libraries threshold (e.g., --min-libraries 20)")
        return 1

    # Prioritize official installations
    prioritized = prioritize_official_installations(valid_dirs)

    # Display results
    print_header(f"Found {len(prioritized)} KiCAD Library Directory(ies)")

    for i, (path, count, priority) in enumerate(prioritized, 1):
        priority_label = {
            "kicad-9-official": "KiCAD 9 (official)",
            "kicad-8-official": "KiCAD 8 (official)",
            "kicad-7-official": "KiCAD 7 (official)",
            "kicad-official": "KiCAD (official)",
            "custom": "Custom/User",
        }.get(priority, priority)

        print(f"{i}. {path}")
        print(f"   Type: {priority_label}")
        print(f"   Libraries: {count} .kicad_sym files")

        if i == 1:
            print(f"   ⭐ RECOMMENDED")

        print()

    # Show setup instructions for best candidate
    best_path, best_count, best_priority = prioritized[0]

    print_header("Setup Instructions")

    print("Add to your shell configuration file:")
    print()

    env_cmd = format_env_var_suggestion(best_path)
    print(f"  {env_cmd}")
    print()

    if system in ["Darwin", "Linux"]:
        shell = (
            Path.home() / ".zshrc" if (Path.home() / ".zshrc").exists() else Path.home() / ".bashrc"
        )
        print(f"For permanent configuration, add to {shell}:")
        print(f"  echo '{env_cmd}' >> {shell}")
        print()

    print("Then restart your terminal or run:")
    print(f"  source ~/.zshrc  # or ~/.bashrc")
    print()

    # Verification
    print("Verify setup with:")
    print(
        "  python -c \"import kicad_sch_api as ksa; print(ksa.SymbolLibraryCache().discover_libraries(), 'libraries')\""
    )
    print()

    return 0


def entry_point() -> None:
    """Entry point for setuptools console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
