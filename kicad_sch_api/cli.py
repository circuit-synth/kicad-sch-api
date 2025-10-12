#!/usr/bin/env python3
"""
KiCAD Schematic API - Command Line Interface

Provides helpful commands for testing and usage of the library.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def test_installation() -> bool:
    """Test that the library is working correctly."""
    print("🧪 Testing KiCAD Schematic API Library...")

    try:
        # Test basic import
        import kicad_sch_api

        version = getattr(kicad_sch_api, "__version__", "unknown")
        print(f"✅ Library imports successfully: v{version}")

        # Test core functionality
        import kicad_sch_api as ksa

        sch = ksa.create_schematic("test")
        print("✅ Can create schematic")

        # Test component addition
        sch.components.add(lib_id="Device:R", reference="R1", value="10k", position=(100, 100))
        print("✅ Can add components")

        # Test library access
        from kicad_sch_api.library.cache import get_symbol_cache

        cache = get_symbol_cache()
        stats = cache.get_performance_stats()
        print(f"✅ Symbol cache available: {stats['total_symbols_cached']} symbols")

        print("🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def show_status() -> bool:
    """Show current installation status."""
    print("📊 KiCAD Schematic API Library Status")
    print("=" * 40)

    # Check installation
    try:
        import kicad_sch_api

        version = getattr(kicad_sch_api, "__version__", "unknown")
        print(f"✅ Library installed: v{version}")
    except ImportError:
        print("❌ Library not installed")
        return False

    # Check KiCAD libraries
    try:
        from kicad_sch_api.library.cache import get_symbol_cache

        cache = get_symbol_cache()
        stats = cache.get_performance_stats()
        print(
            f"✅ KiCAD libraries: {len(cache._lib_stats)} libraries, {stats['total_symbols_cached']} symbols"
        )
    except Exception as e:
        print(f"⚠️  KiCAD library access: {e}")

    return True


def create_demo() -> bool:
    """Create a demo schematic to test functionality."""
    print("🎨 Creating demo schematic...")

    try:
        import kicad_sch_api as ksa

        # Create demo schematic
        sch = ksa.create_schematic("Demo_Circuit")

        # Add components
        resistor = sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        capacitor = sch.components.add(
            "Device:C", reference="C1", value="100nF", position=(150, 100)
        )
        led = sch.components.add("Device:LED", reference="D1", value="LED", position=(200, 100))

        # Save schematic
        sch.save("demo_circuit.kicad_sch")

        print("✅ Demo schematic created: demo_circuit.kicad_sch")
        print("📁 Contains: resistor, capacitor, and LED")
        print("🔗 Try opening in KiCAD: kicad demo_circuit.kicad_sch")

        return True

    except Exception as e:
        print(f"❌ Demo creation failed: {e}")
        return False


def init_cache() -> bool:
    """Initialize the component discovery cache."""
    print("🔄 Initializing component discovery cache...")

    try:
        from kicad_sch_api.discovery.search_index import ensure_index_built

        component_count = ensure_index_built()
        print(f"✅ Component cache initialized: {component_count} components indexed")
        return True
    except Exception as e:
        print(f"❌ Cache initialization failed: {e}")
        return False


def check_kicad() -> bool:
    """Check KiCAD installation and library access."""
    print("🔍 Checking KiCAD installation...")

    try:
        # Check if KiCAD command is available
        result = subprocess.run(["kicad", "--version"], capture_output=True, timeout=10)
        if result.returncode == 0:
            version_output = result.stdout.decode().strip()
            print(f"✅ KiCAD found: {version_output}")
        else:
            print("⚠️  KiCAD command found but version check failed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ KiCAD command not found in PATH")
        print("   Please ensure KiCAD is installed and accessible")

    # Check library directories
    try:
        from kicad_sch_api.library.cache import get_symbol_cache

        cache = get_symbol_cache()

        print("📚 KiCAD Library Status:")
        for lib_name, lib_stats in cache._lib_stats.items():
            print(f"   • {lib_name}: {lib_stats.symbol_count} symbols")

        return True
    except Exception as e:
        print(f"❌ Library access failed: {e}")
        return False


def show_mcp_info() -> None:
    """Show information about MCP server integration."""
    print("🤖 MCP Server Integration")
    print("=" * 25)
    print()
    print("This library serves as a foundation for MCP servers.")
    print("For AI agent integration, install the dedicated MCP server:")
    print()
    print("  pip install mcp-kicad-sch-api")
    print("  code mcp install mcp-kicad-sch-api")
    print()
    print("Related projects:")
    print("  • mcp-kicad-sch-api: https://github.com/circuit-synth/mcp-kicad-sch-api")
    print("  • Claude Code: https://claude.ai/code")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KiCAD Schematic API - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kicad-sch-api --test                  # Test library installation
  kicad-sch-api --demo                  # Create demo schematic
  kicad-sch-api --status                # Show library status
        """,
    )

    # Main options
    parser.add_argument("--test", action="store_true", help="Test that the library is working")
    parser.add_argument("--status", action="store_true", help="Show library installation status")
    parser.add_argument("--demo", action="store_true", help="Create a demo schematic")
    parser.add_argument(
        "--init-cache", action="store_true", help="Initialize component discovery cache"
    )
    parser.add_argument(
        "--check-kicad", action="store_true", help="Check KiCAD installation and libraries"
    )
    parser.add_argument(
        "--mcp-info", action="store_true", help="Show MCP server integration information"
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        print("🚀 KiCAD Schematic API - Command Line Interface")
        print()
        print("This is a pure Python library for KiCAD schematic manipulation.")
        print()
        print("🧪 Test the installation:")
        print("  kicad-sch-api --test")
        print()
        print("🎨 Create a demo schematic:")
        print("  kicad-sch-api --demo")
        print()
        print("🤖 For AI agent integration:")
        print("  kicad-sch-api --mcp-info")
        print()
        print("🆘 For all options:")
        print("  kicad-sch-api --help")
        return

    # Execute requested actions
    success = True

    if args.test:
        success &= test_installation()

    if args.status:
        success &= show_status()

    if args.demo:
        success &= create_demo()

    if args.init_cache:
        success &= init_cache()

    if args.check_kicad:
        success &= check_kicad()

    if args.mcp_info:
        show_mcp_info()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
