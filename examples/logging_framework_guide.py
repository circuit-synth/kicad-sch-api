"""Production-Ready Logging Framework Guide and Examples.

This file demonstrates how to use the comprehensive logging framework
for the kicad-sch-api MCP server.

Key Features:
- Structured JSON logging for production
- Separate debug/error logs
- File rotation (10MB, keep 5 files)
- No stdout contamination (stderr only)
- Context tracking for operations
- Performance monitoring decorators
- Exception logging helpers
- Log querying and analysis
"""

import logging
from pathlib import Path
from kicad_sch_api.utils.logging import (
    configure_logging,
    operation_context,
    timer_decorator,
    log_exception,
    setup_component_logging,
    get_log_statistics,
    search_logs,
    LogQuery,
)


# ==============================================================================
# PART 1: Configuration Examples
# ==============================================================================


def setup_development_logging():
    """Configure logging for development with verbose output.

    - DEBUG level logging
    - Human-readable format (not JSON)
    - Console output for immediate feedback
    - Files: logs/mcp_server.log, logs/mcp_server.error.log
    """
    print("Setting up DEVELOPMENT logging...")
    configure_logging(
        log_dir=Path("logs"),
        debug_level=True,  # Enable DEBUG logging
        json_format=False,  # Human-readable text format
        max_bytes=10 * 1024 * 1024,  # 10MB per file
        backup_count=5,  # Keep 5 backups
    )
    print("Development logging configured!")
    print("  Main log: logs/mcp_server.log")
    print("  Error log: logs/mcp_server.error.log")
    print("  Level: DEBUG (very verbose)")
    print("  Format: Human-readable text")
    print()


def setup_production_logging():
    """Configure logging for production.

    - INFO level logging (DEBUG disabled)
    - JSON format for structured log parsing
    - No console output (files only)
    - Files: logs/mcp_server.log, logs/mcp_server.error.log
    """
    print("Setting up PRODUCTION logging...")
    configure_logging(
        log_dir=Path("logs"),
        debug_level=False,  # Disable DEBUG logging
        json_format=True,  # Structured JSON format
        max_bytes=10 * 1024 * 1024,  # 10MB per file
        backup_count=5,  # Keep 5 backups
    )
    print("Production logging configured!")
    print("  Main log: logs/mcp_server.log")
    print("  Error log: logs/mcp_server.error.log")
    print("  Level: INFO (concise)")
    print("  Format: Structured JSON")
    print()


# ==============================================================================
# PART 2: Basic Function Logging
# ==============================================================================


def example_basic_logging():
    """Example: Basic logging in a function."""
    print("=" * 70)
    print("EXAMPLE: Basic Function Logging")
    print("=" * 70)

    logger = logging.getLogger(__name__)

    def create_resistor(reference: str, value: str, position: tuple):
        """Create a resistor component."""
        # Log function entry
        logger.debug(
            f"create_resistor: ref={reference}, value={value}, pos={position}"
        )

        # Simulate work
        logger.debug(f"  Validating reference: {reference}")
        logger.debug(f"  Setting value: {value}")
        logger.debug(f"  Positioning at: {position}")

        # Log result at INFO level
        logger.info(f"Created resistor {reference} ({value}) at {position}")

        return {"reference": reference, "value": value, "position": position}

    # Call the function
    print("\nCalling create_resistor('R1', '10k', (100, 100))...")
    result = create_resistor("R1", "10k", (100, 100))
    print(f"Result: {result}")
    print()


# ==============================================================================
# PART 3: Context Manager Usage
# ==============================================================================


def example_operation_context():
    """Example: Using operation_context for tracking."""
    print("=" * 70)
    print("EXAMPLE: Operation Context Tracking")
    print("=" * 70)

    logger = logging.getLogger(__name__)

    def complex_operation():
        """Simulate a complex operation with context tracking."""

        # Track the main operation
        with operation_context(
            "create_voltage_divider",
            details={
                "input_voltage": 5.0,
                "ratio": "2:1",
                "output_pins": ["R1.2", "R2.1"],
            },
        ) as ctx:

            logger.debug("Creating first resistor...")
            with operation_context(
                "add_component",
                component="R1",
                details={"value": "10k"},
            ):
                # Simulate adding R1
                logger.debug("  Validating footprint")
                logger.debug("  Adding to schematic")

            logger.debug("Creating second resistor...")
            with operation_context(
                "add_component",
                component="R2",
                details={"value": "5k"},
            ):
                # Simulate adding R2
                logger.debug("  Validating footprint")
                logger.debug("  Adding to schematic")

            logger.debug("Connecting pins...")
            with operation_context(
                "connect_pins",
                details={"start": "R1.2", "end": "R2.1"},
            ):
                # Simulate routing
                logger.debug("  Finding pin positions")
                logger.debug("  Calculating path")
                logger.debug("  Creating wires")

    print("\nExecuting complex_operation()...")
    complex_operation()
    print("Complex operation completed!")
    print()


# ==============================================================================
# PART 4: Timer Decorator
# ==============================================================================


def example_timer_decorator():
    """Example: Using @timer_decorator for performance logging."""
    print("=" * 70)
    print("EXAMPLE: Performance Measurement with Timer Decorator")
    print("=" * 70)

    logger = logging.getLogger(__name__)

    @timer_decorator(logger_obj=logger)
    def calculate_pin_position(component_ref: str, pin_number: str) -> tuple:
        """Calculate absolute position of a component pin."""
        import time

        # Simulate calculation
        time.sleep(0.01)  # 10ms

        logger.debug(f"  Found pin {pin_number} in component data")
        logger.debug(f"  Relative position: (0.0, 3.81)")
        logger.debug(f"  Applying transformation...")
        logger.debug(f"  Final position: (100.0, 103.81)")

        return (100.0, 103.81)

    print("\nCalling calculate_pin_position('R1', '2')...")
    position = calculate_pin_position("R1", "2")
    print(f"Position: {position}")
    print()

    @timer_decorator(logger_obj=logger)
    def slow_operation() -> None:
        """Simulate a slow operation."""
        import time

        time.sleep(0.05)  # 50ms
        logger.debug("Processing data...")

    print("Calling slow_operation()...")
    slow_operation()
    print()


# ==============================================================================
# PART 5: Exception Logging
# ==============================================================================


def example_exception_logging():
    """Example: Logging exceptions with full context."""
    print("=" * 70)
    print("EXAMPLE: Exception Logging")
    print("=" * 70)

    logger = logging.getLogger(__name__)

    def get_component(reference: str):
        """Get component by reference."""
        logger.debug(f"Looking up component: {reference}")

        # Simulate not finding component
        if reference == "R999":
            log_exception(
                logger,
                ValueError(f"Component {reference} not found"),
                context="get_component",
                reference=reference,
                available_components=["R1", "R2", "C1"],
            )
            return None

        logger.debug(f"Found component: {reference}")
        return {"reference": reference}

    print("\nCalling get_component('R1')...")
    comp = get_component("R1")
    print(f"Result: {comp}")

    print("\nCalling get_component('R999') - this will log an exception...")
    try:
        comp = get_component("R999")
    except ValueError:
        pass
    print()


# ==============================================================================
# PART 6: Component-Specific Logging
# ==============================================================================


def example_component_logging():
    """Example: Logging with component context."""
    print("=" * 70)
    print("EXAMPLE: Component-Specific Logging")
    print("=" * 70)

    # Create adapter that includes component reference in all logs
    logger = setup_component_logging("R1")

    logger.debug("Creating resistor")
    logger.debug("Setting value to 10k")
    logger.debug("Setting footprint to 0603")
    logger.info("Resistor R1 configured successfully")

    print()

    # Use for a different component
    logger2 = setup_component_logging("U1")
    logger2.debug("Creating IC")
    logger2.debug("Setting value to STM32G431")
    logger2.info("IC U1 configured successfully")

    print()


# ==============================================================================
# PART 7: Log Statistics and Analysis
# ==============================================================================


def example_log_statistics():
    """Example: Analyzing log files for statistics."""
    print("=" * 70)
    print("EXAMPLE: Log Statistics")
    print("=" * 70)

    log_path = Path("logs/mcp_server.log")

    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        print("(This example requires logs to be generated first)")
        return

    print(f"\nAnalyzing: {log_path}")

    stats = get_log_statistics(log_path)

    print(f"\nLog Statistics:")
    print(f"  DEBUG entries: {stats.get('debug_count', 0)}")
    print(f"  INFO entries: {stats.get('info_count', 0)}")
    print(f"  WARNING entries: {stats.get('warning_count', 0)}")
    print(f"  ERROR entries: {stats.get('error_count', 0)}")
    print(f"  CRITICAL entries: {stats.get('critical_count', 0)}")

    print(f"\nOperations tracked:")
    for op, count in stats.get("operations", {}).items():
        print(f"  {op}: {count} times")

    print(f"\nComponents touched:")
    for comp in stats.get("components", [])[:10]:  # First 10
        print(f"  {comp}")

    if stats.get("errors"):
        print(f"\nRecent errors:")
        for error in stats.get("errors", [])[:3]:  # Last 3
            print(f"  - {error['message']}")

    print()


# ==============================================================================
# PART 8: Log Querying
# ==============================================================================


def example_log_querying():
    """Example: Searching and querying logs."""
    print("=" * 70)
    print("EXAMPLE: Log Querying")
    print("=" * 70)

    log_path = Path("logs/mcp_server.log")

    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        print("(This example requires logs to be generated first)")
        return

    print(f"\nQuerying: {log_path}")

    # Query 1: Find all errors
    print("\nQuery 1: All ERROR level entries")
    errors = search_logs(log_path, level="ERROR", limit=5)
    print(f"  Found {len(errors)} errors (showing first 5)")
    for error in errors:
        print(f"    - {error.get('message', 'No message')}")

    # Query 2: Find entries for a specific component
    print("\nQuery 2: All entries for component 'R1'")
    r1_logs = search_logs(log_path, component="R1", limit=10)
    print(f"  Found {len(r1_logs)} entries for R1")

    # Query 3: Find all 'add_component' operations
    print("\nQuery 3: All 'add_component' operations")
    add_comp_ops = search_logs(log_path, operation="add_component", limit=10)
    print(f"  Found {len(add_comp_ops)} 'add_component' operations")

    # Query 4: Using fluent interface
    print("\nQuery 4: Using LogQuery fluent interface")
    query = (
        LogQuery(log_path)
        .by_level("INFO")
        .by_pattern(".*pin.*")
        .limit(5)
    )
    results = query.execute()
    print(f"  Found {len(results)} INFO entries matching '*pin*' pattern")

    summary = query.summary()
    print(f"  Summary: {summary}")

    print()


# ==============================================================================
# PART 9: Integration Example - Complete Workflow
# ==============================================================================


def example_complete_workflow():
    """Example: Complete workflow showing all logging features together."""
    print("=" * 70)
    print("EXAMPLE: Complete Integration Workflow")
    print("=" * 70)

    logger = logging.getLogger(__name__)

    @timer_decorator(logger_obj=logger)
    def design_voltage_divider(
        input_voltage: float, r1_value: str, r2_value: str
    ):
        """Design and create a voltage divider circuit."""

        with operation_context(
            "design_voltage_divider",
            details={
                "input_voltage": input_voltage,
                "r1": r1_value,
                "r2": r2_value,
            },
        ):

            logger.debug(f"Starting voltage divider design")

            # Add R1
            r1_logger = setup_component_logging("R1")
            with operation_context("add_component", component="R1"):
                r1_logger.debug("Creating component")
                r1_logger.debug("Setting value to 10k")

            # Add R2
            r2_logger = setup_component_logging("R2")
            with operation_context("add_component", component="R2"):
                r2_logger.debug("Creating component")
                r2_logger.debug("Setting value to 5k")

            # Connect pins
            with operation_context(
                "connect_pins",
                details={"start": "R1.2", "end": "R2.1"},
            ):
                logger.debug("Finding pin positions")
                logger.debug("Calculating routing path")
                logger.debug("Creating wires")

            logger.info("Voltage divider design complete")

    print("\nExecuting design_voltage_divider(5.0, '10k', '5k')...")
    design_voltage_divider(5.0, "10k", "5k")
    print("Workflow completed!")
    print()


# ==============================================================================
# MAIN - Run all examples
# ==============================================================================


def main():
    """Run all logging framework examples."""

    print("\n" + "=" * 70)
    print("KICAD-SCH-API LOGGING FRAMEWORK - COMPLETE GUIDE")
    print("=" * 70)
    print()

    # 1. Setup development logging
    print("[SETUP] Configuring development logging...")
    setup_development_logging()

    # 2. Basic logging
    example_basic_logging()

    # 3. Operation context
    example_operation_context()

    # 4. Timer decorator
    example_timer_decorator()

    # 5. Exception logging
    example_exception_logging()

    # 6. Component logging
    example_component_logging()

    # 7. Log statistics (optional - requires logs to exist)
    example_log_statistics()

    # 8. Log querying (optional - requires logs to exist)
    example_log_querying()

    # 9. Complete workflow
    example_complete_workflow()

    print("=" * 70)
    print("LOGGING FRAMEWORK GUIDE COMPLETE")
    print("=" * 70)
    print()
    print("Log files created:")
    print("  - logs/mcp_server.log (all levels)")
    print("  - logs/mcp_server.error.log (errors only)")
    print()
    print("Next steps:")
    print("  1. Review the log files to see output format")
    print("  2. Inspect example_logging_sample_output.py for expected output")
    print("  3. Integrate logging into your MCP server code")
    print()


if __name__ == "__main__":
    main()
