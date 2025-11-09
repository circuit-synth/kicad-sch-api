"""Production-ready structured logging framework for kicad-sch-api MCP server.

This module provides:
- Structured JSON logging for production
- Separate debug/error file handling
- File rotation with size limits
- Context tracking for operations
- No stdout contamination (stderr only)
- Performance monitoring decorators
- Exception logging helpers
"""

import functools
import json
import logging
import logging.handlers
import time
import traceback
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Type definitions
T = TypeVar("T")


@dataclass
class OperationContext:
    """Context information for tracking operations."""

    operation_name: str
    start_time: float = field(default_factory=time.time)
    component: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "in_progress"
    end_time: Optional[float] = None

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation": self.operation_name,
            "component": self.component,
            "status": self.status,
            "elapsed_ms": self.elapsed_ms(),
            "details": self.details,
        }


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured JSON for production logs."""

    def __init__(self, json_mode: bool = True):
        """Initialize formatter.

        Args:
            json_mode: If True, output JSON. If False, output human-readable text.
        """
        self.json_mode = json_mode
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.json_mode:
            return self._format_json(record)
        else:
            return self._format_text(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON for structured logging."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add custom attributes if present
        if hasattr(record, "operation_context"):
            log_data["context"] = record.operation_context.to_dict()

        return json.dumps(log_data)

    def _format_text(self, record: logging.LogRecord) -> str:
        """Format as human-readable text for development."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        logger = record.name
        msg = record.getMessage()

        if record.exc_info and record.exc_info[0] is not None:
            msg += f"\n{traceback.format_exc()}"

        return f"{timestamp} [{level:8}] {logger}: {msg}"


def configure_logging(
    log_dir: Path = Path("logs"),
    debug_level: bool = False,
    json_format: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """Configure production-ready logging.

    This function sets up:
    - Main log file (all levels)
    - Error log file (ERROR and CRITICAL only)
    - DEBUG level for all loggers (if debug_level=True)
    - No stdout contamination (stderr only)
    - File rotation based on size

    Args:
        log_dir: Directory to store log files
        debug_level: If True, set DEBUG level for all loggers
        json_format: If True, use JSON format for structured logging
        max_bytes: Maximum log file size before rotation (default 10MB)
        backup_count: Number of backup log files to keep (default 5)

    Example:
        # Development with debug output
        configure_logging(debug_level=True, json_format=False)

        # Production with JSON
        configure_logging(debug_level=False, json_format=True)
    """
    # Create logs directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug_level else logging.INFO)

    # Clear existing handlers
    root.handlers.clear()

    # Create formatter
    formatter = StructuredFormatter(json_mode=json_format)

    # Main log file handler (all levels)
    main_log_path = log_dir / "mcp_server.log"
    main_handler = logging.handlers.RotatingFileHandler(
        main_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    main_handler.setLevel(logging.DEBUG if debug_level else logging.INFO)
    main_handler.setFormatter(formatter)
    root.addHandler(main_handler)

    # Error log file handler (errors only)
    error_log_path = log_dir / "mcp_server.error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)

    # Console handler to stderr (INFO and above in production, DEBUG in dev)
    if debug_level:
        # Development: verbose debug output to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(StructuredFormatter(json_mode=False))
        root.addHandler(console)

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: log_dir={log_dir}, " f"debug={debug_level}, json={json_format}"
    )


@contextmanager
def operation_context(operation_name: str, component: Optional[str] = None, **details: Any):
    """Context manager for tracking operation execution.

    Logs operation start, completion, duration, and any exceptions.

    Example:
        with operation_context("create_schematic", details={"name": "My Circuit"}):
            sch = ksa.create_schematic("My Circuit")
            # Operation logged automatically on exit
    """
    context = OperationContext(
        operation_name=operation_name,
        component=component,
        details=details,
    )

    logger = logging.getLogger(__name__)

    # Log operation start
    logger.debug(f"START: {operation_name}", extra={"operation_context": context})

    try:
        yield context
        # Mark success
        context.status = "success"
        context.end_time = time.time()
        logger.info(
            f"COMPLETE: {operation_name} ({context.elapsed_ms():.1f}ms)",
            extra={"operation_context": context},
        )

    except Exception as e:
        # Mark failure
        context.status = "failed"
        context.end_time = time.time()
        logger.error(
            f"FAILED: {operation_name} - {e.__class__.__name__}: {e}",
            exc_info=True,
            extra={"operation_context": context},
        )
        raise


def timer_decorator(logger_obj: Optional[logging.Logger] = None) -> Callable:
    """Decorator for measuring function execution time.

    Logs execution time at INFO level on success, ERROR on exception.

    Example:
        @timer_decorator()
        def calculate_pin_position(component, pin_num):
            # Time automatically logged
            return position
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger = logger_obj or logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000
                logger.debug(f"{func.__name__} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_exception(
    logger_obj: logging.Logger,
    exception: Exception,
    context: Optional[str] = None,
    **extra_info: Any,
) -> None:
    """Log an exception with full context and additional information.

    Args:
        logger_obj: Logger instance to use
        exception: The exception to log
        context: Optional context string describing what was happening
        **extra_info: Additional information to include in log

    Example:
        try:
            pin_pos = get_pin_position(comp, pin)
        except ValueError as e:
            log_exception(logger, e, context="get_pin_position",
                        component="R1", pin="2")
    """
    msg = f"Exception: {exception.__class__.__name__}: {exception}"
    if context:
        msg = f"{context}: {msg}"

    if extra_info:
        msg += f" [{', '.join(f'{k}={v}' for k, v in extra_info.items())}]"

    logger_obj.error(msg, exc_info=True)


def setup_component_logging(
    component_ref: str,
) -> logging.LoggerAdapter:
    """Create a logger adapter for a specific component.

    All logs from this adapter automatically include the component reference.

    Example:
        logger = setup_component_logging("R1")
        logger.debug("Setting value to 10k")  # Logs with component=R1
    """
    logger = logging.getLogger(__name__)

    class ComponentAdapter(logging.LoggerAdapter):
        def process(self, msg: str, kwargs: Any) -> tuple:
            return f"[{component_ref}] {msg}", kwargs

    return ComponentAdapter(logger, {})


def get_log_statistics(log_path: Path) -> Dict[str, Any]:
    """Parse log file and get statistics.

    Returns counts of log levels, unique operations, errors, etc.

    Example:
        stats = get_log_statistics(Path("logs/mcp_server.log"))
        print(f"Errors: {stats['error_count']}")
    """
    if not log_path.exists():
        return {"error": "Log file not found"}

    stats = {
        "debug_count": 0,
        "info_count": 0,
        "warning_count": 0,
        "error_count": 0,
        "critical_count": 0,
        "operations": {},
        "components": set(),
        "errors": [],
    }

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    if line.strip().startswith("{"):
                        record = json.loads(line)
                        level = record.get("level", "").lower()

                        # Count by level
                        if level == "debug":
                            stats["debug_count"] += 1
                        elif level == "info":
                            stats["info_count"] += 1
                        elif level == "warning":
                            stats["warning_count"] += 1
                        elif level == "error":
                            stats["error_count"] += 1
                            stats["errors"].append(
                                {
                                    "message": record.get("message"),
                                    "timestamp": record.get("timestamp"),
                                }
                            )
                        elif level == "critical":
                            stats["critical_count"] += 1

                        # Track operations
                        if "context" in record:
                            op = record["context"].get("operation")
                            if op:
                                stats["operations"][op] = stats["operations"].get(op, 0) + 1

                            comp = record["context"].get("component")
                            if comp:
                                stats["components"].add(comp)

                except json.JSONDecodeError:
                    pass

    except Exception as e:
        stats["parse_error"] = str(e)

    # Convert set to list for JSON serialization
    stats["components"] = sorted(list(stats["components"]))

    return stats


def search_logs(
    log_path: Path,
    pattern: Optional[str] = None,
    level: Optional[str] = None,
    operation: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Search log file for entries matching criteria.

    Example:
        # Find all errors related to R1
        errors = search_logs(
            Path("logs/mcp_server.log"),
            level="ERROR",
            component="R1"
        )

        # Find all component creation operations
        operations = search_logs(
            Path("logs/mcp_server.log"),
            operation="add_component"
        )

        # Search by message pattern
        results = search_logs(
            Path("logs/mcp_server.log"),
            pattern="pin.*position"
        )
    """
    import re

    if not log_path.exists():
        return []

    results = []
    pattern_re = re.compile(pattern) if pattern else None

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    if not line.strip().startswith("{"):
                        continue

                    record = json.loads(line)

                    # Filter by level
                    if level and record.get("level", "").upper() != level.upper():
                        continue

                    # Filter by message pattern
                    if pattern_re:
                        msg = record.get("message", "")
                        if not pattern_re.search(msg):
                            continue

                    # Filter by operation
                    if operation:
                        ctx_op = record.get("context", {}).get("operation")
                        if ctx_op != operation:
                            continue

                    # Filter by component
                    if component:
                        ctx_comp = record.get("context", {}).get("component")
                        if ctx_comp != component:
                            continue

                    results.append(record)

                    if len(results) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

    except Exception:
        pass

    return results


class LogQuery:
    """Fluent interface for querying logs."""

    def __init__(self, log_path: Path):
        """Initialize with log file path."""
        self.log_path = log_path
        self.filters = {
            "pattern": None,
            "level": None,
            "operation": None,
            "component": None,
            "limit": 100,
        }

    def by_pattern(self, pattern: str) -> "LogQuery":
        """Filter by message pattern (regex)."""
        self.filters["pattern"] = pattern
        return self

    def by_level(self, level: str) -> "LogQuery":
        """Filter by log level."""
        self.filters["level"] = level
        return self

    def by_operation(self, operation: str) -> "LogQuery":
        """Filter by operation name."""
        self.filters["operation"] = operation
        return self

    def by_component(self, component: str) -> "LogQuery":
        """Filter by component reference."""
        self.filters["component"] = component
        return self

    def limit(self, limit: int) -> "LogQuery":
        """Limit number of results."""
        self.filters["limit"] = limit
        return self

    def execute(self) -> List[Dict[str, Any]]:
        """Execute query and return results."""
        return search_logs(self.log_path, **self.filters)

    def summary(self) -> Dict[str, Any]:
        """Get summary of results."""
        results = self.execute()
        return {
            "count": len(results),
            "levels": self._count_by_key(results, "level"),
            "latest": results[-1]["timestamp"] if results else None,
            "oldest": results[0]["timestamp"] if results else None,
        }

    @staticmethod
    def _count_by_key(items: List[Dict], key: str) -> Dict[str, int]:
        """Count items by key value."""
        counts = {}
        for item in items:
            val = item.get(key, "unknown")
            counts[val] = counts.get(val, 0) + 1
        return counts


# Module-level logger
logger = logging.getLogger(__name__)
