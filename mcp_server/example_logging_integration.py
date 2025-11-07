"""Example MCP server implementation with integrated logging.

This module demonstrates how to integrate the logging framework into an MCP server.
Shows practical examples of:
- Tool implementation with logging
- Error handling with logging
- Performance monitoring
- Component-specific logging
- Log analysis and searching
"""

from pathlib import Path
from typing import Any, Dict, Optional
import logging

# Import logging utilities
from mcp_server.utils import (
    configure_mcp_logging,
    get_mcp_logger,
    log_operation,
    log_timing,
    log_errors,
    operation_context,
    ComponentLogger,
    OperationTimer,
    search_logs,
    LogQuery,
)


# ============================================================================
# INITIALIZATION
# ============================================================================

def setup_server():
    """Initialize MCP server with logging."""
    print("Initializing MCP server...")

    # Configure logging
    configure_mcp_logging(
        log_dir=Path("logs"),
        debug_level=True,      # Development: verbose
        json_format=False      # Development: human-readable
    )

    logger = get_mcp_logger()
    logger.info("MCP server initialized")
    return logger


# ============================================================================
# EXAMPLE 1: Simple Tool Implementation
# ============================================================================

logger = get_mcp_logger("tools")


@log_operation(operation_name="create_schematic")
@log_timing(threshold_ms=100)
def tool_create_schematic(name: str) -> Dict[str, Any]:
    """Create a new schematic.

    Example:
        result = tool_create_schematic("MyCircuit")
        # Logs: "START: create_schematic"
        # Logs: "Schematic created: MyCircuit"
        # Logs: "COMPLETE: create_schematic (15.23ms)"
    """
    with operation_context("create_schematic", details={"name": name}):
        logger.debug(f"Creating schematic: {name}")

        # Simulate schematic creation
        schematic = {
            "uuid": "abc123",
            "name": name,
            "components": [],
            "wires": [],
        }

        logger.info(f"Schematic created: {name}")

        return {
            "success": True,
            "schematic": schematic,
        }


# ============================================================================
# EXAMPLE 2: Component Operations with Logging
# ============================================================================


@log_operation(operation_name="add_resistor")
def tool_add_resistor(
    schematic_uuid: str,
    reference: str,
    value: str,
    tolerance: Optional[str] = None,
) -> Dict[str, Any]:
    """Add resistor to schematic.

    Example:
        result = tool_add_resistor("abc123", "R1", "10k", "1%")
        # Logs all operations with [R1] context
    """

    with ComponentLogger(reference) as comp_logger:
        comp_logger.debug("Initializing resistor")

        # Simulate component addition
        component = {
            "uuid": f"comp_{reference}",
            "reference": reference,
            "value": value,
            "tolerance": tolerance,
        }

        comp_logger.debug(f"Set value to {value}")
        comp_logger.debug(f"Set tolerance to {tolerance}")
        comp_logger.info("Resistor created successfully")

        # Log component history
        history = comp_logger.get_history()
        logger.debug(f"Component {reference} operations: {len(history)}")

        return {
            "success": True,
            "component": component,
            "summary": comp_logger.summary(),
        }


# ============================================================================
# EXAMPLE 3: Multi-Step Operation
# ============================================================================


def tool_build_circuit(schematic_uuid: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Build circuit with multiple components.

    Example:
        result = tool_build_circuit("abc123", {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "R2", "value": "20k"},
            ]
        })
    """

    with operation_context("build_circuit", details=config):
        logger.info("Building circuit")

        results = []

        # Process each component
        for comp_config in config.get("components", []):
            comp_ref = comp_config["ref"]

            with ComponentLogger(comp_ref) as comp_logger:
                comp_logger.debug("Adding component")

                try:
                    # Simulate component addition
                    result = {
                        "reference": comp_ref,
                        "value": comp_config.get("value"),
                    }

                    comp_logger.info("Component added successfully")
                    results.append(result)

                except Exception as e:
                    comp_logger.error(f"Failed to add component: {e}")
                    raise

        logger.info(f"Circuit built with {len(results)} components")

        return {
            "success": True,
            "components_added": len(results),
            "components": results,
        }


# ============================================================================
# EXAMPLE 4: Error Handling
# ============================================================================


@log_errors(operation_name="get_pin_position")
def tool_get_pin_position(
    schematic_uuid: str,
    component_ref: str,
    pin_num: int,
) -> Dict[str, Any]:
    """Get pin position with comprehensive error logging.

    Example:
        # Valid call
        result = tool_get_pin_position("abc123", "R1", 1)

        # Invalid call - logs error
        result = tool_get_pin_position("abc123", "R1", -1)
    """

    with operation_context(
        "get_pin_position",
        component=component_ref,
        details={"pin": pin_num},
    ):
        logger.debug(f"Getting pin {pin_num} for {component_ref}")

        # Validate pin number
        if pin_num < 1:
            raise ValueError(f"Invalid pin number: {pin_num}")

        # Simulate pin position lookup
        position = {
            "x": 100.0 + (pin_num * 2.54),
            "y": 100.0,
        }

        logger.info(f"Pin {pin_num} position: {position}")

        return {
            "success": True,
            "component": component_ref,
            "pin": pin_num,
            "position": position,
        }


# ============================================================================
# EXAMPLE 5: Performance Monitoring
# ============================================================================


@log_timing(threshold_ms=500)
def tool_analyze_circuit(schematic_uuid: str) -> Dict[str, Any]:
    """Analyze circuit with performance monitoring.

    Example:
        result = tool_analyze_circuit("abc123")
        # Logs timing, warns if > 500ms
    """

    with OperationTimer("circuit_analysis", threshold_ms=500):
        logger.info("Starting circuit analysis")

        # Simulate analysis steps
        analysis = {
            "component_count": 5,
            "wire_count": 4,
            "nets": ["VCC", "GND"],
            "errors": 0,
        }

        logger.debug(f"Found {analysis['component_count']} components")
        logger.debug(f"Found {analysis['wire_count']} wires")
        logger.info("Circuit analysis complete")

        return {
            "success": True,
            "analysis": analysis,
        }


# ============================================================================
# EXAMPLE 6: Logging Search and Analysis
# ============================================================================


def analyze_logs() -> Dict[str, Any]:
    """Analyze logs for debugging and monitoring.

    Example:
        result = analyze_logs()
        print(f"Total operations: {result['total_operations']}")
        print(f"Errors: {result['error_count']}")
    """

    log_path = Path("logs/mcp_server.log")

    if not log_path.exists():
        logger.warning("Log file not found")
        return {"error": "Log file not found"}

    logger.info("Analyzing logs")

    # Find errors
    errors = search_logs(log_path, level="ERROR", limit=100)
    logger.debug(f"Found {len(errors)} errors")

    # Find slow operations
    slow_ops = (
        LogQuery(log_path)
        .by_pattern("COMPLETE.*")
        .limit(1000)
        .execute()
    )

    slow_count = 0
    for op in slow_ops:
        elapsed = op.get("context", {}).get("elapsed_ms", 0)
        if elapsed > 100:
            slow_count += 1

    logger.debug(f"Found {slow_count} slow operations (>100ms)")

    # Find by component
    r1_logs = search_logs(log_path, component="R1", limit=100)
    logger.debug(f"Found {len(r1_logs)} logs for R1")

    logger.info("Log analysis complete")

    return {
        "error_count": len(errors),
        "slow_operations": slow_count,
        "component_r1_logs": len(r1_logs),
        "most_recent_error": errors[-1] if errors else None,
    }


# ============================================================================
# EXAMPLE 7: Context Stacking
# ============================================================================


def tool_complex_operation(schematic_uuid: str) -> Dict[str, Any]:
    """Example of nested context managers.

    Example:
        result = tool_complex_operation("abc123")
        # Logs nested contexts with timing
    """

    with operation_context("complex_operation"):
        logger.info("Starting complex operation")

        # Sub-step 1: Load
        with operation_context("load_data"):
            logger.debug("Loading schematic data")
            # Simulate load

        # Sub-step 2: Process components
        with operation_context("process_components"):
            logger.debug("Processing 10 components")

            for i in range(3):  # Simulate 3 components
                ref = f"C{i+1}"
                with ComponentLogger(ref) as comp_logger:
                    comp_logger.debug("Processing")
                    # Simulate processing
                    comp_logger.info("Processed")

        # Sub-step 3: Validate
        with operation_context("validate"):
            logger.debug("Validating circuit")
            # Simulate validation

        logger.info("Complex operation complete")

        return {"success": True}


# ============================================================================
# EXAMPLE 8: Batch Operations with Logging
# ============================================================================


def tool_batch_update_components(
    schematic_uuid: str,
    updates: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Update multiple components with logging.

    Example:
        result = tool_batch_update_components("abc123", {
            "R1": {"value": "10k", "tolerance": "1%"},
            "R2": {"value": "20k", "tolerance": "1%"},
        })
    """

    with operation_context("batch_update", details={"count": len(updates)}):
        logger.info(f"Updating {len(updates)} components")

        results = {}

        for comp_ref, changes in updates.items():
            with ComponentLogger(comp_ref) as comp_logger:
                comp_logger.debug(f"Applying updates: {changes}")

                try:
                    # Simulate update
                    updated = {
                        "reference": comp_ref,
                        **changes,
                    }

                    comp_logger.info("Updates applied successfully")
                    results[comp_ref] = updated

                except Exception as e:
                    comp_logger.error(f"Update failed: {e}")
                    results[comp_ref] = {"error": str(e)}

        logger.info(f"Batch update complete: {len(results)} components")

        return {
            "success": True,
            "results": results,
        }


# ============================================================================
# MAIN EXAMPLE EXECUTION
# ============================================================================


def run_examples():
    """Run all examples to demonstrate logging."""

    print("\n" + "=" * 70)
    print("MCP Server Logging Framework Examples")
    print("=" * 70 + "\n")

    # Setup logging
    setup_server()
    logger = get_mcp_logger()

    # Example 1: Create schematic
    print("\n1. Creating schematic...")
    result = tool_create_schematic("MyCircuit")
    print(f"   Result: {result['success']}")

    # Example 2: Add component
    print("\n2. Adding resistor R1...")
    result = tool_add_resistor(
        "abc123",
        "R1",
        "10k",
        "1%",
    )
    print(f"   Result: {result['success']}")
    print(f"   Summary: {result['summary']}")

    # Example 3: Build circuit
    print("\n3. Building circuit with multiple components...")
    result = tool_build_circuit(
        "abc123",
        {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "R2", "value": "20k"},
                {"ref": "C1", "value": "100uF"},
            ],
        },
    )
    print(f"   Result: {result['success']}")
    print(f"   Components added: {result['components_added']}")

    # Example 4: Get pin position (success)
    print("\n4. Getting pin position...")
    result = tool_get_pin_position("abc123", "R1", 1)
    print(f"   Result: {result['success']}")
    print(f"   Position: {result['position']}")

    # Example 5: Analyze circuit
    print("\n5. Analyzing circuit...")
    result = tool_analyze_circuit("abc123")
    print(f"   Result: {result['success']}")
    print(f"   Components: {result['analysis']['component_count']}")

    # Example 6: Complex operation
    print("\n6. Running complex operation...")
    result = tool_complex_operation("abc123")
    print(f"   Result: {result['success']}")

    # Example 7: Batch update
    print("\n7. Batch updating components...")
    result = tool_batch_update_components(
        "abc123",
        {
            "R1": {"value": "15k", "tolerance": "1%"},
            "R2": {"value": "25k", "tolerance": "1%"},
        },
    )
    print(f"   Result: {result['success']}")
    print(f"   Updated: {len(result['results'])} components")

    # Example 8: Analyze logs
    print("\n8. Analyzing logs...")
    result = analyze_logs()
    print(f"   Errors: {result['error_count']}")
    print(f"   Slow operations: {result['slow_operations']}")
    print(f"   R1 logs: {result['component_r1_logs']}")

    # Summary
    print("\n" + "=" * 70)
    print("Example execution complete!")
    print("Check logs/mcp_server.log for detailed operation logs")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_examples()
