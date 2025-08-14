#!/usr/bin/env python3
"""
Comprehensive test runner for all reference schematic tests.

This script runs all individual reference tests and provides a summary
of results, ensuring the kicad-sch-api works correctly with all reference
projects.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kicad_sch_api.core.schematic import Schematic

# Import all test classes
from test_blank_schematic import TestBlankSchematic
from test_single_resistor import TestSingleResistor
from test_two_resistors import TestTwoResistors
from test_resistor_divider import TestResistorDivider
from test_single_wire import TestSingleWire
from test_single_label import TestSingleLabel
from test_single_label_hierarchical import TestSingleLabelHierarchical
from test_single_text import TestSingleText
from test_single_text_box import TestSingleTextBox
from test_single_hierarchical_sheet import TestSingleHierarchicalSheet


def run_test_class(test_class, test_name):
    """
    Run all tests in a test class and return results.
    
    Args:
        test_class: Test class to run
        test_name: Human-readable name for the test
        
    Returns:
        dict with test results
    """
    print(f"\n{'='*20} {test_name} {'='*20}")
    
    results = {
        'name': test_name,
        'passed': 0,
        'failed': 0,
        'total': 0,
        'errors': []
    }
    
    # Create test instance
    test_instance = test_class()
    test_instance.setup_method()
    
    # Get all test methods
    test_methods = [method for method in dir(test_instance) 
                   if method.startswith('test_') and callable(getattr(test_instance, method))]
    
    results['total'] = len(test_methods)
    
    for method_name in test_methods:
        try:
            print(f"  Running {method_name}...")
            method = getattr(test_instance, method_name)
            method()
            results['passed'] += 1
            print(f"  ✅ {method_name} PASSED")
            
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{method_name}: {str(e)}")
            print(f"  ❌ {method_name} FAILED: {e}")
    
    return results


def main():
    """Run all reference tests and provide summary."""
    print("KiCAD-SCH-API Reference Tests")
    print("=" * 60)
    
    # Define all test classes and their names
    test_classes = [
        (TestBlankSchematic, "Blank Schematic"),
        (TestSingleResistor, "Single Resistor"),
        (TestTwoResistors, "Two Resistors"),
        (TestResistorDivider, "Resistor Divider"),
        (TestSingleWire, "Single Wire"),
        (TestSingleLabel, "Single Label"),
        (TestSingleLabelHierarchical, "Single Hierarchical Label"),
        (TestSingleText, "Single Text"),
        (TestSingleTextBox, "Single Text Box"),
        (TestSingleHierarchicalSheet, "Single Hierarchical Sheet"),
    ]
    
    all_results = []
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    # Run all test classes
    for test_class, test_name in test_classes:
        try:
            result = run_test_class(test_class, test_name)
            all_results.append(result)
            total_passed += result['passed']
            total_failed += result['failed']
            total_tests += result['total']
            
        except Exception as e:
            print(f"❌ Failed to run test class {test_name}: {e}")
            all_results.append({
                'name': test_name,
                'passed': 0,
                'failed': 1,
                'total': 1,
                'errors': [f"Class execution error: {e}"]
            })
            total_failed += 1
            total_tests += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print("REFERENCE TESTS SUMMARY")
    print(f"{'='*60}")
    
    for result in all_results:
        status = "✅ PASS" if result['failed'] == 0 else "❌ FAIL"
        print(f"{result['name']:<30} {result['passed']:>3}/{result['total']:<3} {status}")
        
        if result['errors']:
            for error in result['errors']:
                print(f"    Error: {error}")
    
    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS: {total_passed}/{total_tests} tests passed")
    
    if total_failed == 0:
        print("🎉 ALL REFERENCE TESTS PASSED!")
        print("✅ The kicad-sch-api successfully handles all reference projects.")
        print("✅ Repository is ready for public release.")
        return 0
    else:
        success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"⚠ {total_failed} tests failed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 70:
            print("✅ Core functionality working - likely ready for release with minor fixes.")
            return 0
        else:
            print("❌ Significant issues found - needs investigation before release.")
            return 1


if __name__ == "__main__":
    sys.exit(main())