# Logging Framework - Developer Quick Reference

One-page quick reference for common logging tasks.

## Setup

```python
# At application startup
from kicad_sch_api.utils.logging import configure_logging
from pathlib import Path

# Development setup (human-readable, DEBUG level)
configure_logging(debug_level=True, json_format=False)

# Production setup (JSON, INFO level)
configure_logging(debug_level=False, json_format=True)
```

---

## Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

# Entry point
logger.debug(f"function_name: param={param}")

# Intermediate steps
logger.debug(f"  Doing step 1: result={value}")

# Operation complete
logger.info(f"Operation completed successfully")

# Warning (unexpected but handled)
logger.warning(f"Component not found, using default")

# Error (operation failed)
logger.error(f"Invalid pin position: {e}", exc_info=True)
```

---

## Operation Context (Automatic Timing)

```python
from kicad_sch_api.utils.logging import operation_context

# Tracks operation, logs START/COMPLETE with duration
with operation_context("create_schematic", details={"name": "MyCircuit"}):
    sch = ksa.create_schematic("MyCircuit")
    # Logs: "START: create_schematic"
    # ... your code ...
    # Logs: "COMPLETE: create_schematic (12.5ms)"
```

---

## Timer Decorator (Auto Performance Measurement)

```python
from kicad_sch_api.utils.logging import timer_decorator

@timer_decorator(logger_obj=logger)
def calculate_pin_position(component, pin_number):
    # Logs execution time automatically
    return position
    # Logs: "calculate_pin_position completed in 10.45ms"
```

---

## Component-Specific Logging

```python
from kicad_sch_api.utils.logging import setup_component_logging

# Create component logger
logger = setup_component_logging("R1")

logger.debug("Setting value to 10k")
logger.info("Configuration complete")
# Both logs automatically tagged with "[R1]"
```

---

## Exception Logging

```python
from kicad_sch_api.utils.logging import log_exception

try:
    position = get_pin_position(component, pin)
except ValueError as e:
    # Logs exception with context
    log_exception(
        logger, e,
        context="get_pin_position",
        component=component.reference,
        pin=pin
    )
```

---

## Searching Logs

### Simple Search

```python
from kicad_sch_api.utils.logging import search_logs
from pathlib import Path

# Find all errors
errors = search_logs(Path("logs/mcp_server.log"), level="ERROR")

# Find errors for component R1
r1_errors = search_logs(
    Path("logs/mcp_server.log"),
    level="ERROR",
    component="R1"
)

# Pattern search
pin_issues = search_logs(
    Path("logs/mcp_server.log"),
    pattern=".*pin.*"
)
```

### Fluent Query Interface

```python
from kicad_sch_api.utils.logging import LogQuery
from pathlib import Path

# Find all failed add_component operations
results = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_operation("add_component")
    .by_pattern(".*failed.*")
    .limit(20)
    .execute()
)

# Get summary
summary = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("ERROR")
    .summary()
)
```

---

## Log Analysis

```python
from kicad_sch_api.utils.logging import get_log_statistics
from pathlib import Path

# Get statistics
stats = get_log_statistics(Path("logs/mcp_server.log"))

print(f"Debug entries: {stats['debug_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Operations: {stats['operations']}")
print(f"Components: {stats['components']}")
```

---

## Log File Locations

| File | Purpose | Content |
|------|---------|---------|
| `logs/mcp_server.log` | Main log | All DEBUG, INFO, WARNING, ERROR entries |
| `logs/mcp_server.error.log` | Error log | ERROR and CRITICAL only (quick access) |

---

## View Logs

```bash
# Watch main log
tail -f logs/mcp_server.log

# Watch errors only
tail -f logs/mcp_server.error.log

# Search for pattern
grep "pin" logs/mcp_server.log

# Count by level
grep "\[DEBUG" logs/mcp_server.log | wc -l
grep "\[INFO" logs/mcp_server.log | wc -l
grep "\[ERROR" logs/mcp_server.log | wc -l

# JSON pretty-print (production)
jq . logs/mcp_server.log | less
```

---

## Logging Levels Quick Reference

```
DEBUG   - Development visibility (disabled in production)
         Use for: calculations, intermediate values, detailed progress

INFO    - Operation milestones (enabled always)
         Use for: "Created wire", "Schematic saved", operation complete

WARNING - Unexpected but handled
         Use for: "Component not found, using default"

ERROR   - Operation failed (logged to both files)
         Use for: exceptions, invalid data, failures

CRITICAL - System failure (rare)
         Use for: infrastructure failures only
```

---

## Common Patterns

### Pattern 1: Simple Function

```python
def my_function(param):
    logger.debug(f"my_function: param={param}")

    result = do_something(param)
    logger.debug(f"  Result: {result}")

    logger.info("Function completed successfully")
    return result
```

### Pattern 2: Nested Operations

```python
with operation_context("main_operation"):
    logger.debug("Starting sub-task 1")
    with operation_context("sub_task_1"):
        do_task1()

    logger.debug("Starting sub-task 2")
    with operation_context("sub_task_2"):
        do_task2()
```

### Pattern 3: Component Work

```python
logger = setup_component_logging("R1")

logger.debug("Reading value")
value = read_value("R1")

logger.debug(f"Setting value to {value}")
set_value("R1", value)

logger.info("Component configured")
```

### Pattern 4: Error Handling

```python
try:
    result = risky_operation()
except Exception as e:
    log_exception(logger, e, context="risky_operation")
    return None
```

### Pattern 5: Performance Critical

```python
@timer_decorator(logger_obj=logger)
def expensive_operation(data):
    # Automatically logs execution time
    return process_data(data)
```

---

## Debugging Checklist

When something breaks:

1. **Check error log first**
   ```bash
   cat logs/mcp_server.error.log
   ```

2. **Search for component**
   ```python
   errors = search_logs(Path("logs/mcp_server.log"), component="R1")
   ```

3. **Search for operation**
   ```python
   ops = search_logs(Path("logs/mcp_server.log"), operation="add_component")
   ```

4. **Find slow operations**
   ```python
   ops = LogQuery(Path("logs/mcp_server.log")).by_level("INFO").execute()
   slow = [o for o in ops if o['context']['elapsed_ms'] > 100]
   ```

5. **Get full context**
   ```python
   results = LogQuery(Path("logs/mcp_server.log")).by_pattern("error_msg").execute()
   ```

---

## Configuration Examples

### Development

```python
configure_logging(
    debug_level=True,      # Verbose DEBUG output
    json_format=False,     # Human-readable text
    max_bytes=10*1024*1024,  # 10MB per file
    backup_count=5         # Keep 5 backups
)
```

### Production

```python
configure_logging(
    debug_level=False,     # INFO only
    json_format=True,      # Structured JSON
    max_bytes=50*1024*1024,  # 50MB per file
    backup_count=10        # Keep 10 backups
)
```

### Testing

```python
configure_logging(
    log_dir=Path("logs/test"),
    debug_level=True,      # Verbose for test debugging
    json_format=False,
    max_bytes=5*1024*1024,   # 5MB for tests
    backup_count=2
)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No logs appearing | Call `configure_logging()` at startup |
| Can't see DEBUG logs | Set `debug_level=True` |
| Logs not in JSON | Set `json_format=True` |
| Disk filling up | Check `max_bytes` and `backup_count` settings |
| Missing context | Use `operation_context()` or component logger |
| Can't find error | Use `search_logs()` or `LogQuery` |
| Performance slow | Disable DEBUG in production (`debug_level=False`) |

---

## File Reference

| File | Purpose |
|------|---------|
| `kicad_sch_api/utils/logging.py` | Core implementation |
| `kicad_sch_api/utils/LOGGING_README.md` | Full API reference |
| `docs/MCP_SERVER_LOGGING_INTEGRATION.md` | MCP server integration |
| `examples/logging_framework_guide.py` | Working examples |
| `examples/example_logging_sample_output.md` | Sample log outputs |

---

## Example Output

### Development (Text)
```
2025-11-06 10:15:49 [DEBUG   ] __main__: create_resistor: ref=R1, value=10k
2025-11-06 10:15:49 [DEBUG   ] __main__:   Validating reference
2025-11-06 10:15:49 [INFO    ] __main__: Created resistor R1 (10k)
```

### Production (JSON)
```json
{"timestamp":"2025-11-06T10:15:49.123","level":"INFO","message":"Created resistor R1 (10k)","context":{"operation":"add_component","component":"R1","elapsed_ms":12.5}}
```

---

## Copy-Paste Templates

### Function with Logging
```python
def my_function(param):
    """Docstring."""
    logger.debug(f"my_function: param={param}")

    # ... code ...
    intermediate = calculate()
    logger.debug(f"  Intermediate: {intermediate}")

    # ... code ...
    result = finalize(intermediate)
    logger.info(f"Function completed: {result}")
    return result
```

### Operation with Context
```python
with operation_context("operation_name", component="R1"):
    logger.debug("Doing step 1")
    # ... code ...
    logger.debug("Doing step 2")
    # ... code ...
    logger.info("Operation successful")
```

### Component Work
```python
logger = setup_component_logging("R1")
logger.debug("Creating component")
# ... code ...
logger.debug("Configuring properties")
# ... code ...
logger.info("Component ready")
```

---

**For full documentation, see:**
- `kicad_sch_api/utils/LOGGING_README.md`
- `docs/MCP_SERVER_LOGGING_INTEGRATION.md`
- `examples/example_logging_sample_output.md`
