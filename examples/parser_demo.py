#!/usr/bin/env python3
"""
Demonstration of the new modular parser system.

This example shows how to use the new ElementParserRegistry
and specialized parsers for different S-expression elements.
"""

import logging
import sexpdata

from kicad_sch_api.parsers.registry import ElementParserRegistry
from kicad_sch_api.parsers.wire_parser import WireParser
from kicad_sch_api.parsers.symbol_parser import SymbolParser
from kicad_sch_api.parsers.label_parser import LabelParser, HierarchicalLabelParser

# Enable debug logging to see what's happening
logging.basicConfig(level=logging.WARNING)  # Reduce noise


def main():
    """Demonstrate the new parser system."""
    print("🔧 KiCAD Schematic API - New Parser System Demo")
    print("=" * 50)

    # Create registry and register specialized parsers
    registry = ElementParserRegistry()
    registry.register("wire", WireParser())
    registry.register("symbol", SymbolParser())
    registry.register("label", LabelParser())
    registry.register("hierarchical_label", HierarchicalLabelParser())

    print(f"📋 Registered parsers: {registry.get_registered_types()}")
    print()

    # Example S-expression elements (using sexpdata.Symbol for type names)
    test_elements = [
        # Wire element
        [sexpdata.Symbol("wire"),
         [sexpdata.Symbol("pts"), [sexpdata.Symbol("xy"), 100.0, 100.0], [sexpdata.Symbol("xy"), 150.0, 100.0]],
         [sexpdata.Symbol("stroke"), [sexpdata.Symbol("width"), 0.0], [sexpdata.Symbol("type"), sexpdata.Symbol("default")]],
         [sexpdata.Symbol("uuid"), "12345678-1234-5678-9abc-123456789abc"]],

        # Label element
        [sexpdata.Symbol("label"), "VCC",
         [sexpdata.Symbol("at"), 125.0, 95.0, 0],
         [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]]],
         [sexpdata.Symbol("uuid"), "87654321-4321-8765-cba9-876543210987"]],

        # Unknown element (will be skipped)
        [sexpdata.Symbol("unknown_element"), "some_data"]
    ]

    # Parse elements using the registry
    print("🔍 Parsing S-expression elements:")
    print()

    for i, element in enumerate(test_elements, 1):
        element_type = element[0] if element else "unknown"
        print(f"Element {i}: {element_type}")

        result = registry.parse_element(element)
        if result:
            print(f"  ✅ Successfully parsed")
            print(f"  📊 Result keys: {list(result.keys())}")
            if "points" in result:
                print(f"  📍 Points: {len(result['points'])} points")
            if "text" in result:
                print(f"  📝 Text: '{result['text']}'")
        else:
            print(f"  ❌ No parser available")
        print()

    # Demonstrate batch parsing
    print("📦 Batch parsing multiple elements:")
    results = registry.parse_elements(test_elements)
    print(f"  ✅ Successfully parsed {len(results)} of {len(test_elements)} elements")

    # Show parsing statistics
    successful_types = [r.get("type", "unknown") for r in results if "type" in r]
    print(f"  📊 Parsed types: {set(successful_types)}")

    print()
    print("✨ New parser system benefits:")
    print("  • Modular and testable parsers")
    print("  • Easy to add new element types")
    print("  • Clear separation of concerns")
    print("  • Comprehensive error handling")
    print("  • Extensible with fallback parsers")


if __name__ == "__main__":
    main()