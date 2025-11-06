# MCP Server Logging Integration Guide

This document provides step-by-step integration of the production-ready logging framework
into the kicad-sch-api MCP server.

## Quick Start

### 1. Initialize Logging in Server Startup

**File:** `mcp_server/__init__.py` or `mcp_server/main.py`

```python
import logging
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging

# At application startup:
def initialize_mcp_server(debug: bool = False):
    """Initialize MCP server with logging."""

    # Configure logging based on environment
    configure_logging(
        log_dir=Path("logs"),
        debug_level=debug,  # True for dev, False for production
        json_format=not debug,  # JSON for production, text for dev
        max_bytes=10 * 1024 * 1024,  # 10MB per file
        backup_count=5,  # Keep 5 backups
    )

    logger = logging.getLogger(__name__)
    logger.info(f"MCP Server initialized (debug={debug})")
```

### 2. Use in Tool Implementations

**File:** `mcp_server/tools/create_schematic.py`

```python
import logging
from kicad_sch_api.utils.logging import operation_context, timer_decorator
import kicad_sch_api as ksa

logger = logging.getLogger(__name__)

@timer_decorator(logger_obj=logger)
async def create_schematic(name: str, filename: str = None):
    """MCP tool: Create a new schematic."""

    with operation_context("create_schematic", details={"name": name, "filename": filename}):
        logger.debug(f"Creating schematic: {name}")

        try:
            sch = ksa.create_schematic(name)
            logger.debug(f"Schematic object created")

            if filename:
                sch.save(filename)
                logger.debug(f"Saved to: {filename}")
            else:
                logger.debug(f"No filename provided, schematic in memory")

            logger.info(f"Schematic '{name}' created successfully")
            return {
                "success": True,
                "message": f"Created schematic: {name}",
                "uuid": sch.uuid,
            }

        except Exception as e:
            logger.error(f"Failed to create schematic: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }
```

### 3. Component-Specific Operations

**File:** `mcp_server/tools/add_component.py`

```python
import logging
from kicad_sch_api.utils.logging import operation_context, setup_component_logging
import kicad_sch_api as ksa

logger = logging.getLogger(__name__)

async def add_component(
    schematic_uuid: str,
    lib_id: str,
    reference: str,
    value: str,
    position: tuple,
    **kwargs
):
    """MCP tool: Add component to schematic."""

    # Use component-specific logger
    comp_logger = setup_component_logging(reference)
    comp_logger.debug(f"Adding to schematic")

    with operation_context(
        "add_component",
        component=reference,
        details={
            "lib_id": lib_id,
            "value": value,
            "position": position,
        }
    ):

        comp_logger.debug(f"Library ID: {lib_id}")
        comp_logger.debug(f"Value: {value}")
        comp_logger.debug(f"Position: {position}")

        try:
            sch = ksa.load_schematic_by_uuid(schematic_uuid)
            comp_logger.debug(f"Loaded schematic")

            component = sch.components.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=position,
                **kwargs
            )

            comp_logger.debug(f"Component added to collection")
            comp_logger.info(f"Component added successfully")

            return {
                "success": True,
                "message": f"Added {reference}",
                "uuid": component.uuid,
                "position": component.position,
            }

        except Exception as e:
            comp_logger.error(f"Failed to add component: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }
```

### 4. Wire/Connection Operations

**File:** `mcp_server/tools/connect_pins.py`

```python
import logging
from kicad_sch_api.utils.logging import operation_context, log_exception
import kicad_sch_api as ksa

logger = logging.getLogger(__name__)

async def connect_pins(
    schematic_uuid: str,
    ref1: str,
    pin1: str,
    ref2: str,
    pin2: str,
    routing: str = "orthogonal",
):
    """MCP tool: Connect two component pins."""

    with operation_context(
        "connect_pins",
        details={
            "start": f"{ref1}.{pin1}",
            "end": f"{ref2}.{pin2}",
            "routing": routing,
        }
    ):

        logger.debug(f"Connecting: {ref1}.{pin1} → {ref2}.{pin2}")
        logger.debug(f"Routing strategy: {routing}")

        try:
            sch = ksa.load_schematic_by_uuid(schematic_uuid)

            # Validate components exist
            logger.debug(f"Validating components...")
            comp1 = sch.components.get(ref1)
            comp2 = sch.components.get(ref2)

            if not comp1:
                error_msg = f"Component {ref1} not found"
                logger.debug(error_msg)
                return {"success": False, "error": error_msg}

            if not comp2:
                error_msg = f"Component {ref2} not found"
                logger.debug(error_msg)
                return {"success": False, "error": error_msg}

            logger.debug(f"Components found: ✓")

            # Get pin positions
            logger.debug(f"Getting pin positions...")
            pos1 = sch.get_component_pin_position(ref1, pin1)
            pos2 = sch.get_component_pin_position(ref2, pin2)

            if not pos1 or not pos2:
                error_msg = f"One or both pins not found"
                logger.debug(error_msg)
                return {"success": False, "error": error_msg}

            logger.debug(f"Pin positions: {ref1}.{pin1}=({pos1.x}, {pos1.y}), {ref2}.{pin2}=({pos2.x}, {pos2.y})")

            # Create connection
            logger.debug(f"Creating connection...")
            result = sch.connect_pins(ref1, pin1, ref2, pin2, routing=routing)

            if result.success:
                logger.info(f"Connected {ref1}.{pin1} to {ref2}.{pin2}")
                return {
                    "success": True,
                    "message": f"Connected pins",
                    "wires": len(result.wire_uuids),
                    "junctions": len(result.junction_uuids),
                    "distance_mm": result.total_length,
                }
            else:
                logger.debug(f"Connection failed")
                return {
                    "success": False,
                    "error": "Connection failed",
                }

        except Exception as e:
            log_exception(
                logger, e,
                context="connect_pins",
                ref1=ref1, pin1=pin1,
                ref2=ref2, pin2=pin2
            )
            return {
                "success": False,
                "error": str(e),
            }
```

---

## Advanced Usage Patterns

### Pattern 1: Bulk Operations with Progress Logging

```python
import logging
from kicad_sch_api.utils.logging import operation_context

logger = logging.getLogger(__name__)

async def bulk_add_components(schematic_uuid: str, components: list):
    """Add multiple components with progress tracking."""

    with operation_context(
        "bulk_add_components",
        details={"count": len(components)}
    ):

        logger.debug(f"Starting bulk add: {len(components)} components")

        results = []
        for i, comp_spec in enumerate(components, 1):
            with operation_context(
                "add_component",
                component=comp_spec.get("reference"),
                details={
                    "progress": f"{i}/{len(components)}",
                    "lib_id": comp_spec.get("lib_id"),
                }
            ):

                logger.debug(f"Adding {comp_spec['reference']} ({i}/{len(components)})")

                try:
                    # Add component...
                    results.append({
                        "reference": comp_spec["reference"],
                        "success": True,
                    })

                except Exception as e:
                    logger.error(
                        f"Failed to add {comp_spec['reference']}: {e}",
                        exc_info=True
                    )
                    results.append({
                        "reference": comp_spec["reference"],
                        "success": False,
                        "error": str(e),
                    })

        logger.info(f"Bulk add complete: {sum(1 for r in results if r['success'])}/{len(results)} successful")
        return results
```

### Pattern 2: Validation with Detailed Logging

```python
import logging
from kicad_sch_api.utils.logging import operation_context, log_exception

logger = logging.getLogger(__name__)

async def validate_schematic(schematic_uuid: str):
    """Validate schematic with detailed issue logging."""

    with operation_context("validate_schematic"):

        logger.debug(f"Loading schematic...")
        sch = ksa.load_schematic_by_uuid(schematic_uuid)

        logger.debug(f"Validating connectivity...")
        connectivity = sch.validate_connectivity()

        logger.debug(f"Found {len(connectivity.issues)} issues")

        for issue in connectivity.issues:
            if issue.severity == "error":
                logger.error(
                    f"[{issue.component}] {issue.message}",
                    extra={"issue_type": issue.severity}
                )
            elif issue.severity == "warning":
                logger.warning(
                    f"[{issue.component}] {issue.message}",
                    extra={"issue_type": issue.severity}
                )
            else:
                logger.debug(
                    f"[{issue.component}] {issue.message}"
                )

        logger.info(
            f"Validation {'PASSED' if connectivity.passed else 'FAILED'} "
            f"({connectivity.error_count} errors, {connectivity.warning_count} warnings)"
        )

        return {
            "passed": connectivity.passed,
            "errors": connectivity.error_count,
            "warnings": connectivity.warning_count,
            "issues": [
                {
                    "component": i.component,
                    "severity": i.severity,
                    "message": i.message,
                }
                for i in connectivity.issues
            ]
        }
```

### Pattern 3: Hierarchical Operations

```python
import logging
from kicad_sch_api.utils.logging import operation_context

logger = logging.getLogger(__name__)

async def create_hierarchical_project(project_name: str):
    """Create hierarchical schematic project."""

    with operation_context(
        "create_hierarchical_project",
        details={"project": project_name}
    ):

        logger.debug(f"Creating parent schematic...")

        with operation_context("create_parent_schematic"):
            main = ksa.create_schematic(project_name)
            logger.debug(f"Parent schematic UUID: {main.uuid}")

        logger.debug(f"Creating child schematics...")

        children = []
        for sheet_name in ["Power", "Signal Processing", "Output"]:

            with operation_context(
                "create_sheet",
                details={"name": sheet_name}
            ):

                logger.debug(f"Creating sheet: {sheet_name}")

                sheet_uuid = main.sheets.add_sheet(
                    name=sheet_name,
                    filename=f"{sheet_name.lower()}.kicad_sch",
                    position=(50, 50),
                    size=(100, 100),
                    project_name=project_name,
                )

                child = ksa.create_schematic(project_name)
                child.set_hierarchy_context(main.uuid, sheet_uuid)

                logger.debug(f"Sheet {sheet_name} UUID: {sheet_uuid}")
                children.append((sheet_name, child))

        logger.info(f"Created hierarchical project: {project_name} (1 parent + {len(children)} children)")
        return {
            "success": True,
            "parent_uuid": main.uuid,
            "children": [{"name": n, "uuid": c.uuid} for n, c in children],
        }
```

---

## Debugging Tools

### Query Recent Errors

```python
from pathlib import Path
from kicad_sch_api.utils.logging import LogQuery

# Find all errors in last session
errors = LogQuery(Path("logs/mcp_server.log")).by_level("ERROR").execute()

for error in errors:
    print(f"{error['timestamp']}: {error['message']}")
```

### Analyze Performance

```python
from pathlib import Path
from kicad_sch_api.utils.logging import search_logs

# Find slow operations
ops = search_logs(Path("logs/mcp_server.log"), level="INFO")
slow = [o for o in ops if o.get('context', {}).get('elapsed_ms', 0) > 100]

for op in sorted(slow, key=lambda x: x['context']['elapsed_ms'], reverse=True):
    print(f"{op['context']['operation']}: {op['context']['elapsed_ms']:.1f}ms")
```

### Track Specific Component

```python
from pathlib import Path
from kicad_sch_api.utils.logging import LogQuery

# All operations involving R1
r1_logs = LogQuery(Path("logs/mcp_server.log")).by_component("R1").execute()

for log in r1_logs:
    print(f"{log['timestamp']}: {log['message']}")
```

---

## Configuration by Environment

### Development Configuration

```python
# .env.local or config.dev.py
LOGGING_DEBUG = True
LOGGING_JSON_FORMAT = False
LOGGING_LOG_DIR = "logs"
LOGGING_ROTATE_SIZE = 10 * 1024 * 1024  # 10MB
LOGGING_BACKUP_COUNT = 5
```

**Initialization:**
```python
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging

configure_logging(
    log_dir=Path(os.getenv("LOGGING_LOG_DIR", "logs")),
    debug_level=os.getenv("LOGGING_DEBUG", "true").lower() == "true",
    json_format=os.getenv("LOGGING_JSON_FORMAT", "false").lower() == "true",
    max_bytes=int(os.getenv("LOGGING_ROTATE_SIZE", 10 * 1024 * 1024)),
    backup_count=int(os.getenv("LOGGING_BACKUP_COUNT", 5)),
)
```

### Production Configuration

```python
# .env.prod or config.prod.py
LOGGING_DEBUG = False
LOGGING_JSON_FORMAT = True
LOGGING_LOG_DIR = "/var/log/mcp-server"
LOGGING_ROTATE_SIZE = 50 * 1024 * 1024  # 50MB
LOGGING_BACKUP_COUNT = 10
```

---

## Testing with Logs

### Unit Test Example

```python
import logging
import pytest
from pathlib import Path
from kicad_sch_api.utils.logging import configure_logging, LogQuery

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    configure_logging(
        log_dir=Path("logs/test"),
        debug_level=True,
        json_format=False,
    )
    yield
    # Cleanup or analysis after test


def test_add_component_logging(caplog):
    """Test that component addition is logged correctly."""

    with caplog.at_level(logging.DEBUG):
        # Your test code here
        pass

    # Assert logs
    assert "add_component" in caplog.text
    assert "R1" in caplog.text
```

---

## Best Practices

### 1. Always Use Operation Context for User-Facing Operations

```python
# Good
with operation_context("create_schematic", details={"name": name}):
    sch = ksa.create_schematic(name)

# Avoid
sch = ksa.create_schematic(name)  # No context
```

### 2. Use Component-Specific Logger for Component Operations

```python
# Good
logger = setup_component_logging(reference)
logger.debug("Adding value property")

# Acceptable
logger.debug(f"[{reference}] Adding value property")
```

### 3. Log at Appropriate Levels

```python
# DEBUG: Detailed progress, values, calculations
logger.debug(f"Pin position: ({x}, {y})")

# INFO: Significant operations, results
logger.info(f"Added resistor {ref}")

# WARNING: Unexpected but handled
logger.warning(f"Component not found, using default")

# ERROR: Operation failed
logger.error(f"Invalid pin position: {e}", exc_info=True)
```

### 4. Include Context in Exception Logging

```python
# Good
log_exception(
    logger, e,
    context="get_pin_position",
    component=ref,
    pin=pin_num
)

# Less helpful
logger.error(f"Error: {e}")
```

### 5. Use Timer Decorator for Performance-Critical Functions

```python
@timer_decorator(logger_obj=logger)
def calculate_routing_path(start: Point, end: Point):
    # Execution time automatically logged
    return path
```

---

## Troubleshooting

### Issue: Logs are empty

**Cause:** Logging not configured at startup

**Solution:**
```python
# Must call before any logging
from kicad_sch_api.utils.logging import configure_logging
from pathlib import Path

configure_logging(log_dir=Path("logs"))
```

### Issue: Wrong log format

**Cause:** json_format parameter incorrect

**Solution:**
```python
# For development (text):
configure_logging(json_format=False)

# For production (JSON):
configure_logging(json_format=True)
```

### Issue: Logs filling disk

**Cause:** Rotation not working

**Solution:**
```python
# Ensure max_bytes is set correctly
configure_logging(
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5,  # Keep 5 backups = 50MB max
)
```

### Issue: DEBUG logs not appearing

**Cause:** debug_level=False in production

**Solution:**
```python
# For development, enable DEBUG:
configure_logging(debug_level=True)

# For production with DEBUG:
configure_logging(debug_level=True, json_format=True)
```

---

## Migration Checklist

- [ ] Add `configure_logging()` to server initialization
- [ ] Wrap major operations with `operation_context()`
- [ ] Use `@timer_decorator()` on slow functions
- [ ] Use `setup_component_logging()` for component work
- [ ] Replace manual exception logging with `log_exception()`
- [ ] Set up log rotation (10MB, 5 backups)
- [ ] Test in development with text format
- [ ] Test in production with JSON format
- [ ] Configure log retention policy
- [ ] Set up log monitoring/alerting

---

## References

- **Logging Framework**: `kicad_sch_api/utils/logging.py`
- **Examples**: `examples/logging_framework_guide.py`
- **Sample Output**: `examples/example_logging_sample_output.md`
- **Guidelines**: `TESTING_AND_LOGGING_GUIDELINES.md`

---

**Last Updated:** November 6, 2024
**Version:** 1.0
**Status:** Production Ready
