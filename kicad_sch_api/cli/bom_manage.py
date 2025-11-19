#!/usr/bin/env python3
"""
BOM Property Management CLI

Command-line tool for auditing, updating, and transforming component properties
in KiCad schematics for BOM cleanup and standardization.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

from kicad_sch_api.bom.auditor import BOMPropertyAuditor, ComponentIssue


def parse_criteria(criteria_str: str) -> Dict[str, str]:
    """Parse comma-separated criteria into dict.

    Examples:
        "value=10k,footprint=*0805*"
        "reference=R*,lib_id=Device:R"
        "PartNumber="  # Empty property
    """
    if not criteria_str:
        return {}

    criteria = {}
    for pair in criteria_str.split(','):
        if '=' in pair:
            key, value = pair.split('=', 1)
            criteria[key.strip()] = value.strip()

    return criteria


def parse_properties(props_str: str) -> Dict[str, str]:
    """Parse comma-separated property=value pairs."""
    if not props_str:
        return {}

    properties = {}
    for pair in props_str.split(','):
        if '=' in pair:
            key, value = pair.split('=', 1)
            properties[key.strip()] = value.strip()

    return properties


def parse_transformations(transform_str: str) -> List[tuple]:
    """Parse property transformations.

    Examples:
        "MPN->PartNumber"
        "OldName->NewName"
    """
    transformations = []
    for t in transform_str.split(','):
        if '->' in t:
            source, dest = t.split('->', 1)
            transformations.append((source.strip(), dest.strip()))

    return transformations


def cmd_audit(args) -> int:
    """Audit command - find missing properties."""
    auditor = BOMPropertyAuditor()

    # Parse required properties
    required_props = [p.strip() for p in args.check.split(',')]

    # Run audit
    print(f"Scanning directory: {args.directory}")
    print(f"Checking for properties: {', '.join(required_props)}")
    print()

    issues = auditor.audit_directory(
        Path(args.directory),
        required_properties=required_props,
        recursive=not args.no_recursive,
        exclude_dnp=args.exclude_dnp
    )

    # Generate report if requested
    if args.output:
        auditor.generate_csv_report(issues, Path(args.output))
        print(f"Report saved to: {args.output}")
        print()

    # Print summary
    print("Audit Summary:")
    print("=" * 50)

    # Group by schematic
    by_schematic = {}
    for issue in issues:
        if issue.schematic_path not in by_schematic:
            by_schematic[issue.schematic_path] = []
        by_schematic[issue.schematic_path].append(issue)

    total_issues = 0
    for sch_path, sch_issues in sorted(by_schematic.items()):
        count = len(sch_issues)
        total_issues += count
        status = "✓" if count == 0 else "✗"
        print(f"{status} {Path(sch_path).name}... {count} issue(s)")

    print("=" * 50)
    print(f"Total components with missing properties: {total_issues}")

    return 0 if total_issues == 0 else 1


def cmd_update(args) -> int:
    """Update command - bulk property changes."""
    auditor = BOMPropertyAuditor()

    # Parse criteria and properties
    match_criteria = parse_criteria(args.match)
    property_updates = parse_properties(args.set)

    if not match_criteria:
        print("Error: --match criteria required")
        return 1

    if not property_updates:
        print("Error: --set properties required")
        return 1

    # Confirm if not dry-run and not auto-confirmed
    if not args.dry_run and not args.yes:
        print("This will modify schematic files.")
        print(f"Match criteria: {match_criteria}")
        print(f"Property updates: {property_updates}")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 1

    # Run update
    print(f"Scanning directory: {args.directory}")
    print(f"Match criteria: {match_criteria}")
    print(f"Property updates: {property_updates}")
    if args.dry_run:
        print("[DRY RUN - No files will be modified]")
    print()

    count = auditor.update_properties(
        Path(args.directory),
        match_criteria=match_criteria,
        property_updates=property_updates,
        dry_run=args.dry_run,
        recursive=not args.no_recursive,
        exclude_dnp=args.exclude_dnp
    )

    action = "Would update" if args.dry_run else "Updated"
    print()
    print(f"{action} {count} component(s)")

    return 0


def cmd_transform(args) -> int:
    """Transform command - copy/rename properties."""
    auditor = BOMPropertyAuditor()

    # Parse transformations
    transformations = parse_transformations(args.copy)

    if not transformations:
        print("Error: --copy transformations required (e.g., 'MPN->PartNumber')")
        return 1

    # Confirm if not dry-run and not auto-confirmed
    if not args.dry_run and not args.yes:
        print("This will modify schematic files.")
        print(f"Transformations: {transformations}")
        if args.only_if_empty:
            print("Mode: Only copy to empty properties")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 1

    # Run transform
    print(f"Scanning directory: {args.directory}")
    print(f"Transformations: {transformations}")
    if args.only_if_empty:
        print("Mode: Only copy to empty properties")
    if args.dry_run:
        print("[DRY RUN - No files will be modified]")
    print()

    count = auditor.transform_properties(
        Path(args.directory),
        transformations=transformations,
        only_if_empty=args.only_if_empty,
        dry_run=args.dry_run,
        recursive=not args.no_recursive,
        exclude_dnp=args.exclude_dnp
    )

    action = "Would transform" if args.dry_run else "Transformed"
    print()
    print(f"{action} {count} component(s)")

    return 0


def entry_point():
    """Main entry point for ksa-bom CLI."""
    parser = argparse.ArgumentParser(
        description="BOM Property Management for KiCad Schematics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find components missing PartNumber
  ksa-bom audit ~/designs --check PartNumber --output report.csv

  # Set PartNumber for all 10k resistors (preview first)
  ksa-bom update ~/designs \\
    --match "value=10k,lib_id=Device:R" \\
    --set "PartNumber=RC0805FR-0710KL" \\
    --dry-run

  # Copy MPN to PartNumber where PartNumber is empty
  ksa-bom transform ~/designs \\
    --copy "MPN->PartNumber" \\
    --only-if-empty

Pattern matching supports:
  - Exact match: "value=10k"
  - Wildcards: "footprint=*0805*"
  - Multiple criteria: "value=10k,lib_id=Device:R"
  - Empty check: "PartNumber=" (matches missing/empty)
        """,
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    subparsers.required = True

    # Common arguments
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('directory', type=str, help='Directory containing schematics')
    common.add_argument('--no-recursive', action='store_true', help='Do not scan subdirectories')
    common.add_argument('--exclude-dnp', action='store_true', help='Exclude Do-Not-Populate components')

    # Audit command
    audit_parser = subparsers.add_parser(
        'audit',
        parents=[common],
        help='Find components missing required properties',
        description='Scan schematics and identify components missing required properties'
    )
    audit_parser.add_argument(
        '--check',
        type=str,
        required=True,
        help='Comma-separated list of required properties (e.g., "PartNumber,Manufacturer")'
    )
    audit_parser.add_argument(
        '--output',
        type=str,
        help='Path to save CSV report'
    )
    audit_parser.set_defaults(func=cmd_audit)

    # Update command
    update_parser = subparsers.add_parser(
        'update',
        parents=[common],
        help='Bulk update component properties',
        description='Update properties on components matching criteria'
    )
    update_parser.add_argument(
        '--match',
        type=str,
        required=True,
        help='Match criteria (e.g., "value=10k,lib_id=Device:R")'
    )
    update_parser.add_argument(
        '--set',
        type=str,
        required=True,
        help='Properties to set (e.g., "PartNumber=XXX,Manufacturer=YYY")'
    )
    update_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    update_parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    update_parser.set_defaults(func=cmd_update)

    # Transform command
    transform_parser = subparsers.add_parser(
        'transform',
        parents=[common],
        help='Copy/rename component properties',
        description='Copy or rename properties across components'
    )
    transform_parser.add_argument(
        '--copy',
        type=str,
        required=True,
        help='Property transformations (e.g., "MPN->PartNumber")'
    )
    transform_parser.add_argument(
        '--only-if-empty',
        action='store_true',
        help='Only copy to empty destination properties'
    )
    transform_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    transform_parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    transform_parser.set_defaults(func=cmd_transform)

    # Parse and execute
    args = parser.parse_args()

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(entry_point())
