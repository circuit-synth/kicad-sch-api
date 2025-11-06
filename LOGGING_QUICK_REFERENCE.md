# Logging Framework - Quick Reference Card

Fast lookup guide for the logging framework.

## Initialization (Copy This)

```python
from pathlib import Path
from mcp_server.utils import configure_mcp_logging, get_mcp_logger

# In your server startup
configure_mcp_logging(debug_level=True, json_format=False)
logger = get_mcp_logger()
```

## Common Patterns

### Add Logging to a Function

```python
from mcp_server.utils import log_operation, operation_context

@log_operation(operation_name="my_tool")
def tool_handler(args):
    with operation_context("my_tool", details=args):
        logger.info(f"Processing {args}")
        return result
```

### Log a Component Operation

```python
from mcp_server.utils import ComponentLogger

with ComponentLogger("R1") as logger:
    logger.debug("Setting value")
    logger.info("Configured")
```

### Measure Performance

```python
from mcp_server.utils import log_timing, OperationTimer

@log_timing(threshold_ms=100)  # Warn if > 100ms
def my_function():
    return result

# Or in a block:
with OperationTimer("operation_name", threshold_ms=500):
    # code here
    pass
```

### Log Exceptions

```python
from mcp_server.utils import log_errors, log_exception

@log_errors(operation_name="my_op")
def my_function():
    # Exceptions logged automatically
    return result

# Manual exception logging:
try:
    something()
except ValueError as e:
    log_exception(logger, e, context="my_op", component="R1")
```

### Retry Logic

```python
from mcp_server.utils import log_retry

@log_retry(max_attempts=3, delay_ms=100)
def fetch_data():
    return data
```

### Multi-Step Operation

```python
with operation_context("complex_op"):
    with operation_context("step_1"):
        do_step_1()
    with operation_context("step_2"):
        do_step_2()
```

## Log Searching

### Find Errors

```python
from mcp_server.utils import search_logs
from pathlib import Path

errors = search_logs(Path("logs/mcp_server.log"), level="ERROR")
```

### Find by Component

```python
r1_logs = search_logs(
    Path("logs/mcp_server.log"),
    component="R1"
)
```

### Complex Query

```python
from mcp_server.utils import LogQuery

results = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("ERROR")
    .by_component("R1")
    .by_pattern("pin.*")
    .limit(20)
    .execute()
)
```

### Get Statistics

```python
from mcp_server.utils import get_log_statistics

stats = get_log_statistics(Path("logs/mcp_server.log"))
print(f"Errors: {stats['error_count']}")
print(f"Operations: {stats['operations']}")
print(f"Components: {stats['components']}")
```

## Decorators Cheat Sheet

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@log_operation()` | Track entry/exit | `@log_operation(operation_name="my_op")` |
| `@log_timing()` | Measure time | `@log_timing(threshold_ms=100)` |
| `@log_errors()` | Log exceptions | `@log_errors(operation_name="op")` |
| `@log_retry()` | Auto-retry | `@log_retry(max_attempts=3)` |
| `@timer_decorator()` | Simple timing | `@timer_decorator(logger_obj=logger)` |
| `@trace_calls()` | Detailed tracing | `@trace_calls(log_level=logging.DEBUG)` |

## Context Managers Cheat Sheet

| Context Manager | Purpose | Example |
|-----------------|---------|---------|
| `operation_context()` | Track operation | `with operation_context("op_name"):` |
| `ComponentLogger()` | Component logging | `with ComponentLogger("R1") as logger:` |
| `OperationTimer()` | Measure block | `with OperationTimer("op", threshold_ms=100):` |
| `log_context()` | Generic context | `with log_context("block_name"):` |

## Log Levels

```python
logger.debug("Development details")      # Only in debug mode
logger.info("Important events")          # Always logged
logger.warning("Unexpected but ok")      # Always logged
logger.error("Operation failed")         # Always logged
logger.critical("System failure")        # Always logged
```

## Configuration Presets

### Development (Human-Readable)
```python
configure_mcp_logging(debug_level=True, json_format=False)
```

### Production (JSON Structured)
```python
configure_mcp_logging(debug_level=False, json_format=True)
```

### Custom
```python
configure_mcp_logging(
    log_dir=Path("logs"),
    debug_level=True,
    json_format=False,
    max_bytes=50*1024*1024,  # 50MB per file
    backup_count=10           # Keep 10 backups
)
```

## View Logs

```bash
# Human-readable
tail -f logs/mcp_server.log

# Pretty-print JSON (production)
jq . logs/mcp_server.log | tail -20

# Errors only
tail -f logs/mcp_server.error.log

# Search for pattern
grep "R1" logs/mcp_server.log
```

## Get Logger Instance

```python
from mcp_server.utils import get_mcp_logger

# Generic
logger = get_mcp_logger()

# Component-specific
logger = get_mcp_logger("resistor_R1")

# Then use it
logger.debug("Message")
logger.info("Message")
logger.error("Message")
```

## Real-World Example

```python
from mcp_server.utils import (
    log_operation,
    operation_context,
    ComponentLogger,
    get_mcp_logger,
)

logger = get_mcp_logger("tools")

@log_operation(operation_name="create_resistor")
def tool_create_resistor(schematic_id, ref, value):
    """Create resistor in schematic."""

    with operation_context("create_resistor", component=ref):
        logger.debug(f"Creating {ref} with value {value}")

        with ComponentLogger(ref) as comp_logger:
            comp_logger.debug("Initializing")

            # Add to schematic
            component = add_component(schematic_id, ref, value)

            comp_logger.info("Resistor created successfully")

        logger.info(f"Component {ref} ready")
        return component
```

## File Locations

```
logs/
├── mcp_server.log           # Main log
├── mcp_server.error.log     # Errors only
└── (rotated backups)        # .log.1, .log.2, etc.
```

## Storage Calculation

Default: 10MB per file × 6 files = 60MB maximum

Custom:
```
Max storage = max_bytes × (backup_count + 1)
```

## Decorator Order (When Using Multiple)

```python
# Right order
@log_operation()      # Outermost
@log_timing()         #
@log_errors()         # Innermost
def my_function():
    pass
```

## Environment Variables

None required. All configuration through code.

## Import Everything

```python
from mcp_server.utils import (
    # Configuration
    configure_mcp_logging,
    get_mcp_logger,

    # Context managers
    operation_context,

    # Decorators
    log_operation,
    log_timing,
    log_errors,
    log_retry,
    timer_decorator,

    # Classes
    ComponentLogger,
    OperationTimer,

    # Helpers
    log_exception,
    setup_component_logging,

    # Search
    search_logs,
    LogQuery,
)
```

## Performance Tips

1. Use `debug_level=False` in production
2. Set appropriate `threshold_ms` for slow operation detection
3. Limit log searches with `.limit()`
4. Archive old logs periodically
5. Use JSON format in production for efficient parsing

## Debugging Tips

- Check `logs/mcp_server.error.log` first for problems
- Use `LogQuery().by_level("ERROR")` to find issues
- Look at timing with `.by_pattern("COMPLETE.*")`
- Track components with `.by_component("R1")`
- Use full stdout logs with `debug_level=True` during development

## Links

- **Full Guide:** `mcp_server/LOGGING_GUIDE.md`
- **Examples:** `mcp_server/example_logging_integration.py`
- **Base Framework:** `kicad_sch_api/utils/LOGGING_README.md`
- **Decorators Code:** `kicad_sch_api/utils/logging_decorators.py`
