# Production-Ready Logging Framework

A comprehensive, production-grade logging framework for the kicad-sch-api MCP server built on Python's standard `logging` module.

## Quick Start

### 1. Configure at Startup

```python
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging

# In your main.py or __init__.py
def startup():
    # Development: human-readable, DEBUG level
    configure_logging(debug_level=True, json_format=False)

    # Production: JSON structured, INFO level
    # configure_logging(debug_level=False, json_format=True)
```

### 2. Use in Functions

```python
import logging
from kicad_sch_api.utils.logging import operation_context, timer_decorator

logger = logging.getLogger(__name__)

@timer_decorator(logger_obj=logger)
def my_function(param):
    """Function with automatic performance logging."""

    with operation_context("my_operation", details={"param": param}):
        logger.debug(f"Processing: {param}")
        # ... your code ...
        logger.info(f"Completed successfully")

    return result
```

### 3. View Logs

```bash
# Main log file
tail -f logs/mcp_server.log

# Errors only
tail -f logs/mcp_server.error.log

# With JSON pretty-printing (production)
jq . logs/mcp_server.log | tail -20
```

---

## Features

### 1. Structured Logging

**Development Format (Human-Readable):**
```
2025-11-06 10:15:49 [DEBUG   ] __main__: Processing component R1
2025-11-06 10:15:49 [INFO    ] __main__: Component R1 added successfully
```

**Production Format (JSON):**
```json
{"timestamp": "2025-11-06T10:15:49.123456", "level": "INFO", "logger": "__main__", "message": "Component R1 added", "context": {"operation": "add_component", "component": "R1"}}
```

### 2. File Rotation

Logs are automatically rotated when they reach 10MB:
- `logs/mcp_server.log` - Main log file (current)
- `logs/mcp_server.log.1` - Previous rotations
- `logs/mcp_server.log.2`
- ...up to 5 backups (configurable)

**Storage:** ~50MB maximum with default settings (10MB × 5 backups)

### 3. Separate Error Logs

Critical errors are also logged to dedicated error file:
- `logs/mcp_server.error.log` - ERROR and CRITICAL only
- Quick access to failures without sifting through DEBUG logs

### 4. Context Tracking

Operations are automatically tracked with timing:
```python
with operation_context("create_schematic", details={"name": "MyCircuit"}):
    # ... code ...
    # Logs: "COMPLETE: create_schematic (12.5ms)"
```

### 5. Performance Monitoring

Decorator for automatic timing:
```python
@timer_decorator(logger_obj=logger)
def expensive_operation():
    # Logs: "expensive_operation completed in 42.15ms"
    return result
```

### 6. Component-Specific Logging

Logs automatically tagged with component reference:
```python
logger = setup_component_logging("R1")
logger.debug("Setting value")  # Logs as "[R1] Setting value"
```

### 7. Exception Logging

Full stack traces with context:
```python
log_exception(logger, e, context="get_pins", component="R1", pin="2")
# Logs exception with all context information
```

### 8. Log Querying

Search and analyze logs programmatically:
```python
# Find errors
errors = search_logs(Path("logs/mcp_server.log"), level="ERROR")

# Find operations
ops = search_logs(Path("logs/mcp_server.log"), operation="add_component")

# Find by component
r1_logs = search_logs(Path("logs/mcp_server.log"), component="R1")

# Fluent query interface
results = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("ERROR")
    .by_component("R1")
    .limit(20)
    .execute()
)
```

---

## API Reference

### Configuration

#### `configure_logging(log_dir, debug_level, json_format, max_bytes, backup_count)`

Configure logging for development or production.

**Parameters:**
- `log_dir` (Path): Directory for log files (default: `Path("logs")`)
- `debug_level` (bool): Enable DEBUG logging (default: `False`)
- `json_format` (bool): Use JSON format (default: `True`)
- `max_bytes` (int): Max file size before rotation (default: 10MB)
- `backup_count` (int): Number of backups to keep (default: 5)

**Example:**
```python
# Development setup
configure_logging(debug_level=True, json_format=False)

# Production setup
configure_logging(debug_level=False, json_format=True)
```

### Operation Context

#### `operation_context(operation_name, component=None, **details)`

Context manager for tracking operations with automatic timing.

**Parameters:**
- `operation_name` (str): Name of operation
- `component` (str, optional): Component reference
- `**details`: Additional details to include in logs

**Returns:** `OperationContext` object

**Example:**
```python
with operation_context("create_resistor", component="R1", value="10k"):
    # Logs "START: create_resistor"
    # ... your code ...
    # Logs "COMPLETE: create_resistor (12.5ms)"
```

### Timer Decorator

#### `@timer_decorator(logger_obj=None)`

Decorator for automatic function timing.

**Parameters:**
- `logger_obj` (Logger, optional): Logger to use (default: module logger)

**Example:**
```python
@timer_decorator(logger_obj=logger)
def calculate_pin_position(component, pin):
    return position  # Logs "calculate_pin_position completed in 10.45ms"
```

### Exception Logging

#### `log_exception(logger, exception, context=None, **extra_info)`

Log an exception with full context and additional information.

**Parameters:**
- `logger` (Logger): Logger instance
- `exception` (Exception): The exception to log
- `context` (str, optional): Context description
- `**extra_info`: Additional information to include

**Example:**
```python
try:
    position = get_pin_position(comp, pin)
except ValueError as e:
    log_exception(logger, e, context="get_pin_position",
                  component=comp.reference, pin=pin)
```

### Component Logging

#### `setup_component_logging(component_ref)`

Create a logger adapter for a specific component.

**Parameters:**
- `component_ref` (str): Component reference (e.g., "R1")

**Returns:** LoggerAdapter with component context

**Example:**
```python
logger = setup_component_logging("R1")
logger.debug("Setting value")  # Logs "[R1] Setting value"
```

### Log Statistics

#### `get_log_statistics(log_path)`

Get statistics from a log file.

**Parameters:**
- `log_path` (Path): Path to log file

**Returns:** Dictionary with statistics

**Example:**
```python
stats = get_log_statistics(Path("logs/mcp_server.log"))
print(f"Errors: {stats['error_count']}")
print(f"Operations: {stats['operations']}")
```

### Log Searching

#### `search_logs(log_path, pattern=None, level=None, operation=None, component=None, limit=100)`

Search log file for entries matching criteria.

**Parameters:**
- `log_path` (Path): Path to log file
- `pattern` (str, optional): Regex pattern for message
- `level` (str, optional): Log level ("DEBUG", "INFO", "ERROR", etc.)
- `operation` (str, optional): Operation name
- `component` (str, optional): Component reference
- `limit` (int): Max results to return (default: 100)

**Returns:** List of matching log entries

**Example:**
```python
# Find all errors
errors = search_logs(Path("logs/mcp_server.log"), level="ERROR")

# Find component-specific issues
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

#### `LogQuery(log_path)`

Fluent interface for building complex log queries.

**Methods:**
- `.by_pattern(pattern)` - Filter by message pattern
- `.by_level(level)` - Filter by log level
- `.by_operation(operation)` - Filter by operation name
- `.by_component(component)` - Filter by component
- `.limit(limit)` - Limit number of results
- `.execute()` - Execute query and return results
- `.summary()` - Get summary of query results

**Example:**
```python
# Find slow add_component operations
slow_adds = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_operation("add_component")
    .limit(50)
    .execute()
)

slow = [o for o in slow_adds
        if o.get('context', {}).get('elapsed_ms', 0) > 100]

# Get summary
summary = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("ERROR")
    .summary()
)
```

---

## Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Development visibility, detailed progress | Position calculations, intermediate values |
| **INFO** | Operation milestones, significant events | "Created wire from R1 to R2", "Schematic saved" |
| **WARNING** | Unexpected but handled situations | "Component not found, using default" |
| **ERROR** | Operation failed | "Invalid pin position", "File not found" |
| **CRITICAL** | System failure (rare) | Major infrastructure failure |

**Best Practices:**
- Use DEBUG for development (disabled in production)
- Use INFO for user-facing operations
- Use WARNING for recoverable issues
- Use ERROR for failures
- Use CRITICAL only for system-level failures

---

## Configuration Examples

### Development Setup

```python
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging

configure_logging(
    log_dir=Path("logs"),
    debug_level=True,  # Verbose
    json_format=False,  # Human-readable
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5,
)
```

**Output:**
- Console: DEBUG and above
- File: All levels
- Format: Human-readable text
- Includes full stack traces

### Production Setup

```python
configure_logging(
    log_dir=Path("/var/log/mcp-server"),
    debug_level=False,  # INFO and above only
    json_format=True,  # Structured JSON
    max_bytes=50 * 1024 * 1024,  # 50MB
    backup_count=10,  # Keep 10 backups
)
```

**Output:**
- Console: None (suppressed)
- File: INFO, WARNING, ERROR, CRITICAL
- Format: Structured JSON for log aggregation
- No stack traces in main log (only error log)

### Testing Setup

```python
configure_logging(
    log_dir=Path("logs/test"),
    debug_level=True,
    json_format=False,
    max_bytes=5 * 1024 * 1024,  # 5MB for tests
    backup_count=2,
)
```

---

## Usage Patterns

### Pattern 1: Basic Function Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    """Process data with logging."""
    logger.debug(f"Processing {len(data)} items")

    result = []
    for item in data:
        logger.debug(f"  Processing item: {item}")
        result.append(transform(item))

    logger.info(f"Processed {len(data)} items successfully")
    return result
```

### Pattern 2: Operation Tracking

```python
from kicad_sch_api.utils.logging import operation_context

def create_circuit():
    """Create circuit with operation tracking."""

    with operation_context("create_circuit"):
        # Add components
        with operation_context("add_component", component="R1"):
            logger.debug("Adding resistor")

        # Add wires
        with operation_context("add_wire"):
            logger.debug("Routing connection")

        # Validate
        with operation_context("validate"):
            logger.debug("Checking connectivity")
```

### Pattern 3: Performance Monitoring

```python
from kicad_sch_api.utils.logging import timer_decorator

@timer_decorator(logger_obj=logger)
def expensive_calculation(data):
    """Calculate something expensive."""
    # Automatically logs execution time
    return result
```

### Pattern 4: Component-Specific Logging

```python
from kicad_sch_api.utils.logging import setup_component_logging

def configure_resistor(ref, value):
    """Configure resistor with component logging."""
    logger = setup_component_logging(ref)

    logger.debug(f"Setting value to {value}")
    # All logs automatically include [R1] tag
```

### Pattern 5: Error Handling

```python
from kicad_sch_api.utils.logging import log_exception

def get_component_pin(component_ref, pin_number):
    """Get pin with comprehensive error logging."""
    try:
        return find_pin(component_ref, pin_number)
    except ValueError as e:
        log_exception(logger, e,
                      context="get_component_pin",
                      component=component_ref,
                      pin=pin_number)
        return None
```

---

## Troubleshooting

### Issue: No log files created

**Check:**
1. Is `configure_logging()` called at startup?
2. Does the `logs/` directory exist?
3. Are write permissions correct?

**Solution:**
```python
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging

# Explicitly create and configure
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

configure_logging(log_dir=log_dir)
```

### Issue: DEBUG logs not appearing

**Cause:** `debug_level=False` in production

**Solution:**
```python
# For development with DEBUG:
configure_logging(debug_level=True)

# For production with DEBUG (be careful with storage):
configure_logging(debug_level=True, json_format=True)
```

### Issue: Logs are difficult to read

**Cause:** Using JSON format in development

**Solution:**
```python
# For development, use text format:
configure_logging(json_format=False)

# For production, use JSON:
configure_logging(json_format=True)
```

### Issue: Logs filling disk

**Cause:** Rotation not configured properly

**Check:**
```python
# Verify rotation settings
configure_logging(
    max_bytes=10 * 1024 * 1024,  # 10MB per file
    backup_count=5,  # Keep 5 backups = 50MB max
)
```

**Calculate:**
```
Max storage = (max_bytes × (backup_count + 1))
            = (10MB × 6) = 60MB maximum
```

### Issue: Missing context in logs

**Cause:** Not using `operation_context()` or component logger

**Solution:**
```python
# Good: Use operation context
with operation_context("my_operation"):
    logger.info("Doing something")

# Good: Use component logger
logger = setup_component_logging("R1")
logger.info("Configuring component")

# Less helpful: No context
logger.info("Doing something")
```

---

## Performance Considerations

### Log Impact

- Logging adds ~1-2ms per operation
- JSON formatting adds ~0.5ms per entry
- File rotation is automatic and non-blocking
- Query operations are O(n) in log file size

### Optimization Tips

1. **Production**: Disable DEBUG logging to reduce I/O
2. **Large Logs**: Use `search_logs()` with limits to avoid loading entire files
3. **Monitoring**: Archive old logs periodically to manage disk space
4. **JSON Parsing**: Use `jq` or similar tools for efficient JSON analysis

---

## Examples

Complete examples available in:
- `examples/logging_framework_guide.py` - Comprehensive usage guide
- `examples/example_logging_sample_output.md` - Sample output documentation
- `docs/MCP_SERVER_LOGGING_INTEGRATION.md` - MCP server integration guide

Run the guide:
```bash
uv run python examples/logging_framework_guide.py
```

---

## Integration Checklist

- [ ] Call `configure_logging()` at server startup
- [ ] Wrap major operations with `operation_context()`
- [ ] Add `@timer_decorator()` to performance-critical functions
- [ ] Use `setup_component_logging()` for component operations
- [ ] Replace manual exception logging with `log_exception()`
- [ ] Configure rotation (10MB, 5-10 backups)
- [ ] Test in development with text format
- [ ] Test in production with JSON format
- [ ] Set up log monitoring/analysis
- [ ] Document custom log queries for debugging

---

## Related Documentation

- **Testing Guidelines**: `TESTING_AND_LOGGING_GUIDELINES.md`
- **MCP Integration**: `docs/MCP_SERVER_LOGGING_INTEGRATION.md`
- **Sample Output**: `examples/example_logging_sample_output.md`

---

**Status:** Production Ready
**Last Updated:** November 6, 2024
**Version:** 1.0
