# MCP Server Logging Framework Guide

Complete guide to using the logging framework in the kicad-sch-api MCP server.

## Quick Start

### 1. Initialize Logging at Startup

```python
# main.py or server initialization
from pathlib import Path
from mcp_server.utils import configure_mcp_logging

def startup():
    # Development: human-readable output
    configure_mcp_logging(debug_level=True, json_format=False)

    # Production: JSON structured logging
    # configure_mcp_logging(debug_level=False, json_format=True)

    logger = get_mcp_logger()
    logger.info("MCP server starting")
```

### 2. Log Operations

```python
from mcp_server.utils import log_operation, operation_context

@log_operation(operation_name="create_schematic")
def handle_create_schematic(name: str):
    with operation_context("create_schematic", details={"name": name}):
        # ... create schematic ...
        return schematic
```

### 3. View Logs

```bash
# Main log file
tail -f logs/mcp_server.log

# Errors only
tail -f logs/mcp_server.error.log

# Pretty-print JSON (production)
jq . logs/mcp_server.log | tail -20
```

---

## Features Overview

### 1. Decorator-Based Logging

#### @log_operation - Function Entry/Exit

```python
@log_operation(operation_name="add_component")
def add_resistor(schematic, value):
    # Automatically logs:
    # "START: add_component"
    # "COMPLETE: add_component (5.23ms)"
    return component

@log_operation(include_args=True, include_result=True)
def calculate_position(x, y):
    # Logs arguments and return value
    return (x + 10, y + 10)
```

#### @log_timing - Performance Tracking

```python
@log_timing(threshold_ms=100)
def load_symbol_library(library_name):
    # Logs timing, warns if > 100ms
    return library

# Custom logger
@log_timing(log_level=logging.DEBUG)
def fast_operation():
    # Log at DEBUG level
    return result
```

#### @log_errors - Exception Handling

```python
@log_errors(operation_name="get_pin_position")
def get_pin(component, pin_num):
    # Logs exceptions with full context
    # Re-raises exception
    return position

@log_errors(reraise=False)
def safe_operation():
    # Logs exception but doesn't raise
    # Returns None on error
    return result
```

#### @log_retry - Retry Logic

```python
@log_retry(max_attempts=3, delay_ms=100)
def load_from_cache(symbol_name):
    # Retries up to 3 times with exponential backoff
    # Logs each attempt
    return symbol

@log_retry(
    max_attempts=5,
    delay_ms=50,
    backoff=1.5,
    exceptions=(IOError, TimeoutError)
)
def fetch_external_data(url):
    # Only retries on specific exceptions
    return data
```

### 2. Context Managers

#### operation_context - Track Operations

```python
def create_circuit(name):
    with operation_context("create_circuit", details={"name": name}):
        # Logs "START: create_circuit"

        with operation_context("add_components", component="R1"):
            # Nested context for sub-operations
            pass

        # Logs "COMPLETE: create_circuit (X.XXms)"

        return circuit
```

#### OperationTimer - Measure Blocks

```python
from mcp_server.utils import OperationTimer

def process_data(data):
    with OperationTimer("data_processing", threshold_ms=500):
        # Logs: "TIMER: data_processing started"
        # ... processing ...
        # Logs: "TIMER: data_processing completed in 123.45ms"
        return result
```

#### ComponentLogger - Component-Specific Logging

```python
from mcp_server.utils import ComponentLogger

def configure_resistor(ref, value, tolerance):
    with ComponentLogger(ref) as logger:
        logger.debug("Initializing")
        logger.info(f"Setting value to {value}")

        # All logs automatically tagged with [R1]
        # Logs: "[R1] Setting value to 10k"

        logger.info("Configuration complete")

        # Get operation history
        history = logger.get_history()
        summary = logger.summary()
        # Output: "R1: DEBUG=1 INFO=2"
```

### 3. Logging Levels

```python
import logging
from mcp_server.utils import get_mcp_logger

logger = get_mcp_logger("tools")

logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Something unexpected happened")
logger.error("A serious error occurred")
logger.critical("System failure")
```

---

## Usage Patterns

### Pattern 1: Simple Tool Implementation

```python
from mcp_server.utils import (
    log_operation,
    log_timing,
    get_mcp_logger,
)

logger = get_mcp_logger("create_resistor_tool")

@log_operation(operation_name="create_resistor")
@log_timing(threshold_ms=50)
def create_resistor(schematic, reference, value):
    """Create resistor component."""
    logger.debug(f"Creating resistor {reference} with value {value}")

    component = schematic.components.add(
        'Device:R',
        reference=reference,
        value=value,
    )

    logger.info(f"Resistor {reference} created successfully")
    return component
```

**Log Output:**
```
START: create_resistor
Creating resistor R1 with value 10k
Resistor R1 created successfully
COMPLETE: create_resistor (12.45ms)
```

### Pattern 2: Multi-Step Operation

```python
from mcp_server.utils import operation_context, ComponentLogger

def configure_circuit(schematic, config):
    """Configure circuit with multiple steps."""

    with operation_context("configure_circuit"):
        # Step 1: Load components
        with operation_context("load_components"):
            logger.info("Loading components")
            components = load_components(schematic)

        # Step 2: Configure each component
        for comp_ref, comp_config in config.items():
            with ComponentLogger(comp_ref) as comp_logger:
                comp_logger.debug(f"Configuring {comp_ref}")
                configure_component(schematic[comp_ref], comp_config)
                comp_logger.info(f"Configuration complete")

        # Step 3: Validate
        with operation_context("validate"):
            logger.info("Validating circuit")
            validate_circuit(schematic)

        logger.info("Circuit configuration complete")
```

**Log Output:**
```
START: configure_circuit
START: load_components
Loading components
COMPLETE: load_components (5.12ms)
[R1] Configuring R1
[R1] Configuration complete
[C1] Configuring C1
[C1] Configuration complete
START: validate
Validating circuit
COMPLETE: validate (2.34ms)
Circuit configuration complete
COMPLETE: configure_circuit (15.67ms)
```

### Pattern 3: Error Handling

```python
from mcp_server.utils import log_errors, log_exception, get_mcp_logger

logger = get_mcp_logger("pin_operations")

@log_errors(operation_name="get_pin_position")
def get_pin_position(component, pin_num):
    """Get pin position with error logging."""
    try:
        if pin_num < 1:
            raise ValueError(f"Invalid pin number: {pin_num}")

        pins = component.pins
        if pin_num > len(pins):
            raise ValueError(f"Pin {pin_num} not found (max: {len(pins)})")

        return pins[pin_num - 1].position

    except ValueError as e:
        log_exception(
            logger, e,
            context="get_pin_position",
            component=component.reference,
            pin=pin_num
        )
        raise
```

**Log Output:**
```
Exception: ValueError: Invalid pin number: -1
  context: get_pin_position
  component: R1
  pin: -1
Traceback (most recent call last):
  ...
```

### Pattern 4: Performance Monitoring

```python
from mcp_server.utils import log_timing, OperationTimer, get_mcp_logger

logger = get_mcp_logger("performance")

@log_timing(threshold_ms=100)
def calculate_all_positions(schematic):
    """Calculate positions for all components."""
    results = {}
    for component in schematic.components:
        results[component.reference] = calculate_position(component)
    return results

def process_schematic(sch_file):
    """Process schematic with timing."""
    with OperationTimer("total_processing", threshold_ms=500):
        with OperationTimer("load_file"):
            schematic = load_schematic(sch_file)

        with OperationTimer("analyze"):
            analysis = analyze_circuit(schematic)

        with OperationTimer("save_results"):
            save_results(analysis)

    return analysis
```

**Log Output:**
```
TIMER: total_processing started
TIMER: load_file started
TIMER: load_file completed in 45.23ms
TIMER: analyze started
TIMER: analyze completed in 234.56ms
TIMER: save_results started
TIMER: save_results completed in 12.34ms
TIMER: total_processing completed in 292.13ms
```

### Pattern 5: Component Operations

```python
from mcp_server.utils import ComponentLogger, log_operation

@log_operation(operation_name="configure_resistor")
def configure_resistor(component, value, tolerance, footprint):
    """Configure resistor with component logging."""

    with ComponentLogger(component.reference) as logger:
        logger.debug(f"Starting configuration")

        logger.debug(f"Setting value to {value}")
        component.value = value

        logger.debug(f"Setting tolerance to {tolerance}")
        component.set_property("Tolerance", tolerance)

        logger.debug(f"Setting footprint to {footprint}")
        component.footprint = footprint

        logger.info("Configuration complete")

        # Can access history
        history = logger.get_history()
        print(f"Operations: {len(history)}")
        print(logger.summary())  # "R1: DEBUG=3 INFO=1"
```

---

## Log Searching and Analysis

### Search by Component

```python
from pathlib import Path
from mcp_server.utils import search_logs

# Find all logs for R1
r1_logs = search_logs(
    Path("logs/mcp_server.log"),
    component="R1",
    limit=50
)

for entry in r1_logs:
    print(f"{entry['timestamp']}: {entry['message']}")
```

### Search by Operation

```python
# Find all component creation operations
comp_ops = search_logs(
    Path("logs/mcp_server.log"),
    operation="add_component",
    limit=100
)

print(f"Total components added: {len(comp_ops)}")
```

### Search by Level

```python
# Find all errors
errors = search_logs(
    Path("logs/mcp_server.log"),
    level="ERROR"
)

for error in errors:
    print(f"Error: {error['message']}")
    if 'exception' in error:
        print(f"  Type: {error['exception']['type']}")
```

### Fluent Query Interface

```python
from mcp_server.utils import LogQuery

# Find slow operations
slow_ops = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("INFO")
    .by_pattern("COMPLETE.*")
    .limit(100)
    .execute()
)

# Extract timing information
slow = [
    o for o in slow_ops
    if o.get('context', {}).get('elapsed_ms', 0) > 100
]

print(f"Found {len(slow)} slow operations (>100ms)")

# Get summary
summary = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_operation("add_component")
    .summary()
)

print(f"add_component calls: {summary['count']}")
print(f"Levels: {summary['levels']}")
```

---

## Configuration Examples

### Development Configuration

```python
from pathlib import Path
from mcp_server.utils import configure_mcp_logging

# Human-readable output for development
configure_mcp_logging(
    log_dir=Path("logs"),
    debug_level=True,      # DEBUG + INFO + WARNING + ERROR
    json_format=False      # Human-readable text
)
```

**Output:**
```
2025-11-06 10:15:49 [DEBUG   ] mcp_server: Starting component addition
2025-11-06 10:15:49 [INFO    ] mcp_server: Component R1 created successfully
2025-11-06 10:15:49 [WARNING ] mcp_server: Large resistance value
```

### Production Configuration

```python
from pathlib import Path
from mcp_server.utils import configure_mcp_logging

# JSON output for production systems
configure_mcp_logging(
    log_dir=Path("/var/log/mcp-server"),
    debug_level=False,     # INFO + WARNING + ERROR only
    json_format=True       # Structured JSON
)
```

**Output:**
```json
{"timestamp": "2025-11-06T10:15:49.123456", "level": "INFO", "logger": "mcp_server", "message": "Component R1 created", "context": {"operation": "add_component", "component": "R1"}}
```

### Testing Configuration

```python
from pathlib import Path
from mcp_server.utils import configure_mcp_logging

# Temporary logs for tests
configure_mcp_logging(
    log_dir=Path("logs/test"),
    debug_level=True,
    json_format=False
)
```

---

## Common Recipes

### Recipe 1: Log a Tool Invocation

```python
from mcp_server.utils import log_operation, operation_context, get_mcp_logger

logger = get_mcp_logger("tools")

@log_operation(operation_name="tool_create_schematic")
def tool_create_schematic(params):
    """Create schematic via MCP tool."""
    name = params.get("name", "Untitled")

    with operation_context("create_schematic", details={"name": name}):
        logger.debug(f"Creating new schematic: {name}")

        schematic = create_schematic(name)

        logger.info(f"Schematic created with UUID: {schematic.uuid}")

        return {
            "success": True,
            "uuid": str(schematic.uuid),
            "name": name
        }
```

### Recipe 2: Log Performance Issues

```python
from mcp_server.utils import OperationTimer, log_timing

@log_timing(threshold_ms=1000)
def expensive_operation(data):
    """Long-running operation with performance tracking."""
    # Will log WARNING if exceeds 1 second
    return process(data)

def monitor_performance(operations):
    """Monitor multiple operations."""
    for op_name, op_func in operations.items():
        with OperationTimer(op_name, threshold_ms=500):
            op_func()
```

### Recipe 3: Log with Context

```python
from mcp_server.utils import ComponentLogger, operation_context

def batch_update_components(components):
    """Update multiple components with logging."""

    with operation_context("batch_update"):
        for comp_ref, new_config in components.items():
            with ComponentLogger(comp_ref) as logger:
                logger.debug("Updating configuration")

                try:
                    update_component(comp_ref, new_config)
                    logger.info("Update successful")
                except Exception as e:
                    logger.error(f"Update failed: {e}")
                    raise
```

### Recipe 4: Analyze Log Trends

```python
from pathlib import Path
from mcp_server.utils import LogQuery

def analyze_errors():
    """Analyze error trends."""
    errors = (
        LogQuery(Path("logs/mcp_server.log"))
        .by_level("ERROR")
        .limit(1000)
        .execute()
    )

    # Count by component
    by_component = {}
    for error in errors:
        comp = error.get('context', {}).get('component', 'unknown')
        by_component[comp] = by_component.get(comp, 0) + 1

    print("Errors by component:")
    for comp, count in sorted(by_component.items(), key=lambda x: -x[1]):
        print(f"  {comp}: {count}")

def find_slowest_operations():
    """Find slowest operations."""
    ops = (
        LogQuery(Path("logs/mcp_server.log"))
        .by_pattern("COMPLETE.*")
        .limit(1000)
        .execute()
    )

    # Extract timing
    timed_ops = [
        (
            o.get('context', {}).get('operation', 'unknown'),
            o.get('context', {}).get('elapsed_ms', 0)
        )
        for o in ops if 'context' in o
    ]

    # Sort by time
    for op_name, elapsed in sorted(timed_ops, key=lambda x: -x[1])[:10]:
        print(f"{op_name}: {elapsed:.2f}ms")
```

---

## Best Practices

### 1. Use Appropriate Levels

```python
logger.debug("Detailed tracing (development only)")
logger.info("User-facing events (always logged)")
logger.warning("Unexpected but handled issues")
logger.error("Operation failures (important)")
logger.critical("System failures (rare)")
```

### 2. Add Context Early

```python
# Good - context included
with operation_context("load_symbols", details={"library": "Device"}):
    load_library("Device")

# Better - component context
with ComponentLogger("R1") as logger:
    logger.info("Configuring")
```

### 3. Log Significant Events

```python
# Don't:
logger.debug("Starting loop iteration 1")  # Too verbose

# Do:
logger.debug("Processing 1000 components")  # Meaningful
logger.info("Component creation complete")  # Significant
```

### 4. Include Relevant Context

```python
# Poor - missing context
logger.error("Failed to get pin")

# Better - includes component reference
logger.error(f"Failed to get pin: component={ref}, pin={num}")

# Best - use structured context
with ComponentLogger(ref) as logger:
    logger.error(f"Failed to get pin {num}")
```

### 5. Performance Matters

```python
# Don't:
@log_operation
def every_loop_iteration():  # Too much overhead
    pass

# Do:
@log_operation
def significant_operation():  # Only on important operations
    pass
```

---

## Troubleshooting

### Q: Where are log files stored?

A: By default in `logs/mcp_server.log` and `logs/mcp_server.error.log`. Configure with:

```python
configure_mcp_logging(log_dir=Path("custom/path"))
```

### Q: How do I see DEBUG logs?

A: Enable debug level:

```python
configure_mcp_logging(debug_level=True)
```

### Q: How do I search logs?

A: Use `search_logs()` or `LogQuery`:

```python
from mcp_server.utils import search_logs, LogQuery

# Simple search
search_logs(Path("logs/mcp_server.log"), level="ERROR")

# Complex query
LogQuery(Path("logs/mcp_server.log")).by_component("R1").execute()
```

### Q: Are logs rotating?

A: Yes, automatically. Configure with:

```python
configure_mcp_logging()  # 10MB per file, 5 backups by default
```

### Q: How much disk space do logs use?

A: With defaults: ~60MB maximum (10MB × 6 files). Adjust:

```python
from kicad_sch_api.utils.logging import configure_logging
configure_logging(max_bytes=50*1024*1024, backup_count=3)  # 200MB max
```

---

## Integration with MCP Tools

Each tool should follow this pattern:

```python
from mcp_server.utils import (
    log_operation,
    log_timing,
    operation_context,
    get_mcp_logger,
)

logger = get_mcp_logger("tool_name")

@log_operation(operation_name="tool_operation_name")
@log_timing(threshold_ms=1000)
def handle_tool_call(args):
    """Handle MCP tool invocation."""

    with operation_context("tool_operation_name", details=args):
        logger.info(f"Tool invoked with args: {args}")

        try:
            result = perform_operation(args)
            logger.info(f"Tool completed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool failed: {e}", exc_info=True)
            raise
```

---

## Example Log Files

### Development Log (Text Format)

```
2025-11-06 10:15:49 [DEBUG   ] mcp_server.tools: START: create_schematic
2025-11-06 10:15:49 [DEBUG   ] mcp_server.tools: Creating new schematic: MyCircuit
2025-11-06 10:15:49 [INFO    ] mcp_server.tools: Schematic created with UUID: abc123
2025-11-06 10:15:49 [INFO    ] mcp_server.tools: COMPLETE: create_schematic (12.45ms)
2025-11-06 10:15:50 [DEBUG   ] mcp_server.tools: START: add_component
2025-11-06 10:15:50 [DEBUG   ] mcp_server.tools: [R1] Initializing
2025-11-06 10:15:50 [DEBUG   ] mcp_server.tools: [R1] Setting value to 10k
2025-11-06 10:15:50 [INFO    ] mcp_server.tools: [R1] Configuration complete
2025-11-06 10:15:50 [INFO    ] mcp_server.tools: COMPLETE: add_component (5.23ms)
```

### Production Log (JSON Format)

```json
{"timestamp": "2025-11-06T10:15:49.123456", "level": "INFO", "logger": "mcp_server.tools", "message": "COMPLETE: create_schematic (12.45ms)", "context": {"operation": "create_schematic", "status": "success", "elapsed_ms": 12.45}}
{"timestamp": "2025-11-06T10:15:50.234567", "level": "INFO", "logger": "mcp_server.tools", "message": "COMPLETE: add_component (5.23ms)", "context": {"operation": "add_component", "component": "R1", "status": "success", "elapsed_ms": 5.23}}
```

---

## Next Steps

1. **Initialize logging** in your MCP server startup
2. **Add decorators** to tool handler functions
3. **Use operation_context** for multi-step operations
4. **Add component logging** for component-specific operations
5. **Monitor logs** using provided query tools
6. **Analyze performance** and optimize based on timing data

For more details, see:
- `kicad_sch_api/utils/logging.py` - Base framework
- `kicad_sch_api/utils/logging_decorators.py` - Decorators
- `kicad_sch_api/utils/LOGGING_README.md` - Complete reference
