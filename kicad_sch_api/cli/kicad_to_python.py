#!/usr/bin/env python3
"""
KiCad-to-Python CLI Command

Convert KiCad schematic files to executable Python code.

Usage:
    kicad-to-python input.kicad_sch output.py
    kicad-to-python input.kicad_sch output.py --template verbose
    kicad-to-python project.kicad_pro output_dir/ --include-hierarchy
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import kicad_sch_api as ksa
from kicad_sch_api.exporters.python_generator import (
    CodeGenerationError,
    PythonCodeGenerator,
    TemplateNotFoundError,
)


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (None = sys.argv)

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        prog="kicad-to-python",
        description="Convert KiCad schematics to Python code",
        epilog="For more information: https://github.com/circuit-synth/kicad-sch-api",
    )

    # Positional arguments
    parser.add_argument(
        "input", type=Path, help="Input KiCad schematic (.kicad_sch) or project (.kicad_pro)"
    )

    parser.add_argument(
        "output", type=Path, help="Output Python file (.py) or directory (for hierarchical)"
    )

    # Options
    parser.add_argument(
        "--template",
        choices=["minimal", "default", "verbose", "documented"],
        default="default",
        help="Code template style (default: default)",
    )

    parser.add_argument(
        "--include-hierarchy", action="store_true", help="Include hierarchical sheets"
    )

    parser.add_argument("--no-format", action="store_true", help="Skip Black code formatting")

    parser.add_argument("--no-comments", action="store_true", help="Skip explanatory comments")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    try:
        # Validate input file
        if not args.input.exists():
            print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
            return 1

        if args.input.suffix not in [".kicad_sch", ".kicad_pro"]:
            print(f"❌ Error: Input must be .kicad_sch or .kicad_pro file", file=sys.stderr)
            return 1

        # Load schematic
        if args.verbose:
            print(f"📖 Loading schematic: {args.input}")

        schematic = ksa.Schematic.load(args.input)

        if args.verbose:
            comp_count = len(list(schematic.components))
            wire_count = len(list(schematic.wires))
            label_count = len(list(schematic.labels))
            print(f"   Found {comp_count} components")
            print(f"   Found {wire_count} wires")
            print(f"   Found {label_count} labels")

        # Generate Python code
        if args.verbose:
            print(f"🔨 Generating Python code...")

        generator = PythonCodeGenerator(
            template=args.template,
            format_code=not args.no_format,
            add_comments=not args.no_comments,
        )

        code = generator.generate(
            schematic=schematic, include_hierarchy=args.include_hierarchy, output_path=args.output
        )

        # Report success
        lines = len(code.split("\n"))
        print(f"✅ Generated {args.output} ({lines} lines)")

        if args.verbose:
            print(f"   Template: {args.template}")
            print(f"   Formatted: {not args.no_format}")
            print(f"   Comments: {not args.no_comments}")

        return 0

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}", file=sys.stderr)
        return 1

    except CodeGenerationError as e:
        print(f"❌ Code generation error: {e}", file=sys.stderr)
        return 1

    except TemplateNotFoundError as e:
        print(f"❌ Template error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def entry_point():
    """Entry point for setuptools console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
