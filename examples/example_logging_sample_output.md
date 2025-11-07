# Sample Logging Output - kicad-sch-api MCP Server

This document shows example log outputs from the production-ready logging framework
for the kicad-sch-api MCP server.

## Overview

The logging framework provides:
- **Structured JSON logging** for production environments
- **Human-readable text logging** for development
- **Separate debug and error logs** for easy filtering
- **Context tracking** with operation hierarchies
- **Performance monitoring** with execution timings
- **Component-specific logging** for pin/component issues

---

## 1. DEVELOPMENT LOGGING (Human-Readable Text Format)

### Example: Creating a Simple Resistor

When running in **development mode** (`debug_level=True, json_format=False`):

```
2024-11-06 10:15:32 [DEBUG   ] kicad_sch_api.utils.logging: Logging configured: log_dir=logs, debug=True, json=False
2024-11-06 10:15:32 [DEBUG   ] __main__: create_resistor: ref=R1, value=10k, pos=(100, 100)
2024-11-06 10:15:32 [DEBUG   ] __main__:   Validating reference: R1
2024-11-06 10:15:32 [DEBUG   ] __main__:   Setting value: 10k
2024-11-06 10:15:32 [DEBUG   ] __main__:   Positioning at: (100, 100)
2024-11-06 10:15:32 [INFO    ] __main__: Created resistor R1 (10k) at (100, 100)
```

**Key Features:**
- Timestamp in human-readable format
- Log level clearly visible
- Logger name and module information
- Progressive indentation shows hierarchy
- Start with DEBUG for entry and intermediate steps
- End with INFO for completion

---

### Example: Complex Operation with Context

```
2024-11-06 10:15:33 [DEBUG   ] __main__: START: create_voltage_divider
2024-11-06 10:15:33 [DEBUG   ] __main__: Creating first resistor...
2024-11-06 10:15:33 [DEBUG   ] __main__: START: add_component
2024-11-06 10:15:33 [DEBUG   ] __main__:   Validating footprint
2024-11-06 10:15:33 [DEBUG   ] __main__:   Adding to schematic
2024-11-06 10:15:33 [INFO    ] __main__: COMPLETE: add_component (12.5ms)
2024-11-06 10:15:33 [DEBUG   ] __main__: Creating second resistor...
2024-11-06 10:15:33 [DEBUG   ] __main__: START: add_component
2024-11-06 10:15:33 [DEBUG   ] __main__:   Validating footprint
2024-11-06 10:15:33 [DEBUG   ] __main__:   Adding to schematic
2024-11-06 10:15:33 [INFO    ] __main__: COMPLETE: add_component (11.8ms)
2024-11-06 10:15:33 [DEBUG   ] __main__: Connecting pins...
2024-11-06 10:15:33 [DEBUG   ] __main__: START: connect_pins
2024-11-06 10:15:33 [DEBUG   ] __main__:   Finding pin positions
2024-11-06 10:15:33 [DEBUG   ] __main__:   Calculating path
2024-11-06 10:15:33 [DEBUG   ] __main__:   Creating wires
2024-11-06 10:15:33 [INFO    ] __main__: COMPLETE: connect_pins (8.3ms)
2024-11-06 10:15:33 [INFO    ] __main__: COMPLETE: create_voltage_divider (34.7ms)
```

**What to notice:**
- Nested operations with START/COMPLETE markers
- Each operation gets duration in milliseconds
- Indentation shows operation hierarchy
- DEBUG messages provide detailed tracing
- INFO messages show progress checkpoints

---

### Example: Performance Measurement (Timer Decorator)

```
2024-11-06 10:15:34 [DEBUG   ] __main__: calculate_pin_position: R1.2
2024-11-06 10:15:34 [DEBUG   ] __main__:   Found pin 2 in component data
2024-11-06 10:15:34 [DEBUG   ] __main__:   Relative position: (0.0, 3.81)
2024-11-06 10:15:34 [DEBUG   ] __main__:   Applying transformation...
2024-11-06 10:15:34 [DEBUG   ] __main__:   Final position: (100.0, 103.81)
2024-11-06 10:15:34 [DEBUG   ] __main__: calculate_pin_position completed in 10.45ms
```

---

### Example: Component-Specific Logging

```
2024-11-06 10:15:35 [DEBUG   ] __main__: [R1] Creating resistor
2024-11-06 10:15:35 [DEBUG   ] __main__: [R1] Setting value to 10k
2024-11-06 10:15:35 [DEBUG   ] __main__: [R1] Setting footprint to 0603
2024-11-06 10:15:35 [INFO    ] __main__: [R1] Resistor R1 configured successfully
2024-11-06 10:15:35 [DEBUG   ] __main__: [U1] Creating IC
2024-11-06 10:15:35 [DEBUG   ] __main__: [U1] Setting value to STM32G431
2024-11-06 10:15:35 [INFO    ] __main__: [U1] IC U1 configured successfully
```

**Component reference automatically included in all logs from that component**

---

### Example: Exception Logging

```
2024-11-06 10:15:36 [DEBUG   ] __main__: Looking up component: R999
2024-11-06 10:15:36 [ERROR   ] __main__: get_component: Exception: ValueError: Component R999 not found [reference=R999, available_components=['R1', 'R2', 'C1']]
2024-11-06 10:15:36 [ERROR   ] __main__: Traceback (most recent call last):
  File "/Users/example/kicad_sch_api/examples/logging_framework_guide.py", line 165, in get_component
    raise ValueError(f"Component {reference} not found")
ValueError: Component R999 not found
```

**Stack trace included for debugging**

---

## 2. PRODUCTION LOGGING (Structured JSON Format)

### Example: Creating a Simple Resistor

When running in **production mode** (`debug_level=False, json_format=True`):

```json
{"timestamp": "2024-11-06T10:15:32.123456", "level": "INFO", "logger": "__main__", "message": "Logging configured: log_dir=logs, debug=False, json=True", "module": "logging", "function": "configure_logging", "line": 180}
{"timestamp": "2024-11-06T10:15:33.456789", "level": "INFO", "logger": "__main__", "message": "Created resistor R1 (10k) at (100, 100)", "module": "logging_framework_guide", "function": "create_resistor", "line": 245}
```

**Key Features:**
- ISO 8601 timestamp for precise timing
- Flat JSON structure (no nesting) for easy parsing
- All fields present for filtering/analysis
- No DEBUG messages (they're suppressed in production)
- Efficient for log aggregation systems (ELK, Splunk, etc.)

---

### Example: Operation with Context

```json
{"timestamp": "2024-11-06T10:15:34.123456", "level": "INFO", "logger": "__main__", "message": "COMPLETE: add_component (12.5ms)", "module": "logging_framework_guide", "function": "design_voltage_divider", "line": 350, "context": {"operation": "add_component", "component": "R1", "status": "success", "elapsed_ms": 12.5, "details": {"value": "10k"}}}
```

**Context information available for filtering:**
- Operation type
- Component reference
- Success/failure status
- Duration in milliseconds
- Additional details

---

### Example: Error with Full Stack Trace

```json
{
  "timestamp": "2024-11-06T10:15:35.789012",
  "level": "ERROR",
  "logger": "__main__",
  "message": "get_component: Exception: ValueError: Component R999 not found [reference=R999, available_components=['R1', 'R2', 'C1']]",
  "module": "logging_framework_guide",
  "function": "get_component",
  "line": 165,
  "exception": {
    "type": "ValueError",
    "message": "Component R999 not found",
    "traceback": [
      "Traceback (most recent call last):\n",
      "  File \"/Users/example/kicad_sch_api/examples/logging_framework_guide.py\", line 162, in get_component\n",
      "    raise ValueError(f\"Component {reference} not found\")\n",
      "ValueError: Component R999 not found\n"
    ]
  }
}
```

**Complete exception information for debugging**

---

## 3. LOG FILE LOCATIONS & ROTATION

### Main Log File

**Path:** `logs/mcp_server.log`

Contains:
- All DEBUG, INFO, WARNING, ERROR entries
- Rotating: 10MB per file, keep 5 backups
- Backup files: `mcp_server.log.1`, `mcp_server.log.2`, etc.

### Error Log File

**Path:** `logs/mcp_server.error.log`

Contains:
- ERROR and CRITICAL entries only
- Quick access to failures without sifting through DEBUG logs
- Same rotation policy: 10MB per file, keep 5 backups

### Storage Requirements

```
Initial setup (empty):      ~0 KB
Light usage (1 hour):       ~2-5 MB
Normal usage (24 hours):    ~20-50 MB
Heavy usage (1 week):       ~100-200 MB

With rotation (5 backups):  Max ~100 MB (10MB × 10 files)
```

---

## 4. LOG ANALYSIS EXAMPLES

### Getting Statistics

```python
from pathlib import Path
from kicad_sch_api.utils.logging import get_log_statistics

stats = get_log_statistics(Path("logs/mcp_server.log"))

print(f"Debug entries: {stats['debug_count']}")
print(f"Info entries: {stats['info_count']}")
print(f"Errors: {stats['error_count']}")

# Output:
# Debug entries: 127
# Info entries: 34
# Errors: 2
```

### Searching for Errors

```python
from pathlib import Path
from kicad_sch_api.utils.logging import search_logs

# Find all errors
errors = search_logs(Path("logs/mcp_server.log"), level="ERROR")

# Find errors for component R1
r1_errors = search_logs(
    Path("logs/mcp_server.log"),
    level="ERROR",
    component="R1"
)

# Find pin-related issues
pin_issues = search_logs(
    Path("logs/mcp_server.log"),
    pattern=".*pin.*",
    level="ERROR"
)
```

### Using Fluent Query Interface

```python
from pathlib import Path
from kicad_sch_api.utils.logging import LogQuery

# Find all add_component operations that failed
failed_adds = (
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
# {
#   'count': 2,
#   'levels': {'ERROR': 2},
#   'latest': '2024-11-06T10:15:35.789012',
#   'oldest': '2024-11-06T10:15:20.123456'
# }
```

---

## 5. TYPICAL OPERATION FLOW

Here's what a complete operation looks like in logs:

### Creating and Connecting Components

**Development Log (Text):**
```
2024-11-06 10:20:00 [DEBUG   ] mcp_server: START: design_circuit
2024-11-06 10:20:00 [DEBUG   ] mcp_server: Creating schematic: MyCircuit
2024-11-06 10:20:00 [DEBUG   ] mcp_server: START: add_component
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Validating ref=R1
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Checking library for Device:R
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Adding to position (100, 100)
2024-11-06 10:20:00 [INFO    ] mcp_server: COMPLETE: add_component (8.3ms)
2024-11-06 10:20:00 [DEBUG   ] mcp_server: START: add_component
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Validating ref=R2
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Checking library for Device:R
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Adding to position (100, 150)
2024-11-06 10:20:00 [INFO    ] mcp_server: COMPLETE: add_component (7.9ms)
2024-11-06 10:20:00 [DEBUG   ] mcp_server: START: connect_pins
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Getting pin position: R1.2
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Getting pin position: R2.1
2024-11-06 10:20:00 [DEBUG   ] mcp_server:   Calculating orthogonal path
2024-11-06 10:20:00 [DEBUG   ] mcp_server:     Path: 3 points
2024-11-06 10:20:00 [DEBUG   ] mcp_server:     Distance: 47.62mm
2024-11-06 10:20:00 [DEBUG   ] mcp_server:     Creating wire 0: (100.0, 103.81) -> (125.0, 103.81)
2024-11-06 10:20:00 [DEBUG   ] mcp_server:     Creating wire 1: (125.0, 103.81) -> (125.0, 150.0)
2024-11-06 10:20:00 [DEBUG   ] mcp_server:     Creating wire 2: (125.0, 150.0) -> (100.0, 150.0)
2024-11-06 10:20:00 [INFO    ] mcp_server: COMPLETE: connect_pins (15.2ms)
2024-11-06 10:20:00 [INFO    ] mcp_server: COMPLETE: design_circuit (35.8ms)
```

**Production Log (JSON) - Formatted for Readability:**
```json
{
  "timestamp": "2024-11-06T10:20:00.000000",
  "level": "INFO",
  "message": "COMPLETE: design_circuit (35.8ms)",
  "context": {
    "operation": "design_circuit",
    "status": "success",
    "elapsed_ms": 35.8,
    "details": {}
  }
}

{
  "timestamp": "2024-11-06T10:20:00.008300",
  "level": "INFO",
  "message": "COMPLETE: add_component (8.3ms)",
  "context": {
    "operation": "add_component",
    "component": "R1",
    "status": "success",
    "elapsed_ms": 8.3,
    "details": {"value": "10k"}
  }
}

{
  "timestamp": "2024-11-06T10:20:00.016200",
  "level": "INFO",
  "message": "COMPLETE: add_component (7.9ms)",
  "context": {
    "operation": "add_component",
    "component": "R2",
    "status": "success",
    "elapsed_ms": 7.9,
    "details": {"value": "5k"}
  }
}

{
  "timestamp": "2024-11-06T10:20:00.031400",
  "level": "INFO",
  "message": "COMPLETE: connect_pins (15.2ms)",
  "context": {
    "operation": "connect_pins",
    "status": "success",
    "elapsed_ms": 15.2,
    "details": {
      "start": "R1.2",
      "end": "R2.1",
      "wires": 3,
      "distance_mm": 47.62
    }
  }
}
```

---

## 6. DEBUGGING WITH LOGS

When a user reports an issue, use logs to trace it:

### Scenario: "Wire didn't connect properly"

```bash
# Find all connection attempts
grep -i "connect_pins" logs/mcp_server.log

# For JSON logs, use LogQuery:
from kicad_sch_api.utils.logging import LogQuery, Path

query = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_operation("connect_pins")
)
results = query.execute()

# Shows:
# - Which components were connected
# - Path taken
# - Wires created
# - Any errors
```

### Scenario: "Component not found error"

```bash
# Find component lookup failures
grep -i "ERROR" logs/mcp_server.log | grep -i "component\|reference"

# Or use LogQuery:
errors = (
    LogQuery(Path("logs/mcp_server.log"))
    .by_level("ERROR")
    .by_pattern(".*component.*")
    .execute()
)

# Shows:
# - Which component lookup failed
# - Available components
# - Full stack trace
```

### Scenario: "Slow performance on large design"

```bash
# Find operations by duration
from kicad_sch_api.utils.logging import search_logs, Path

ops = search_logs(Path("logs/mcp_server.log"), level="INFO")

# Filter by elapsed_ms in context
slow = [o for o in ops if o.get('context', {}).get('elapsed_ms', 0) > 100]

# Identify bottlenecks
for op in slow:
    print(f"{op['context']['operation']}: {op['context']['elapsed_ms']:.1f}ms")
```

---

## 7. MIGRATION FROM CURRENT LOGGING

If the project has existing logging, migration is straightforward:

### Before:
```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Created resistor {reference}")
logger.debug(f"Position: {position}")
```

### After:
```python
import logging
from kicad_sch_api.utils.logging import (
    operation_context,
    timer_decorator,
    setup_component_logging,
)

logger = logging.getLogger(__name__)

# Option 1: Simple logging (unchanged)
logger.info(f"Created resistor {reference}")
logger.debug(f"Position: {position}")

# Option 2: With context tracking
with operation_context("create_resistor", component=reference):
    logger.debug(f"Position: {position}")
    # Auto-logs completion with duration

# Option 3: With component-specific logging
logger = setup_component_logging(reference)
logger.debug(f"Position: {position}")
# All logs automatically tagged with component

# Option 4: With performance monitoring
@timer_decorator()
def calculate_position():
    return position
```

**Key Point:** Existing code works as-is. New features are opt-in.

---

## Summary

The logging framework provides:

✅ **Development**: Human-readable format, DEBUG level, console output
✅ **Production**: Structured JSON, INFO level, file-only
✅ **Analysis**: Statistics, searching, querying with fluent interface
✅ **Performance**: Timer decorators, operation context tracking
✅ **Debugging**: Full stack traces, component-specific logs
✅ **Rotation**: 10MB files, keep 5 backups, never fill disk
✅ **Integration**: Zero breaking changes to existing code

---

## Next Steps

1. **Review** the sample outputs above to understand format
2. **Run** `examples/logging_framework_guide.py` to generate real logs
3. **Inspect** `logs/mcp_server.log` and `logs/mcp_server.error.log`
4. **Integrate** into MCP server code using patterns from guide
5. **Deploy** with appropriate configuration (dev vs. production)
