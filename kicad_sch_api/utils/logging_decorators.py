"""Advanced decorators for operation logging and performance monitoring.

This module provides decorators for:
- Operation entry/exit logging with context
- Function timing and performance tracking
- Exception logging with context
- Context managers for multi-step operations
- Retry logic with logging
"""

import functools
import logging
import time
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Type definitions
T = TypeVar("T")


def log_operation(
    operation_name: Optional[str] = None,
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
) -> Callable:
    """Decorator for logging function entry and exit.

    Logs when a function starts and completes, with optional argument/result logging.

    Args:
        operation_name: Name for logs (default: function name)
        level: Log level (default: INFO)
        include_args: Include function arguments in logs (default: False)
        include_result: Include return value in logs (default: False)

    Example:
        @log_operation(operation_name="create_component")
        def add_resistor(schematic, value):
            # Logs: "START: create_component"
            # ... code ...
            # Logs: "COMPLETE: create_component"
            return resistor

        @log_operation(include_args=True, include_result=True)
        def calculate_position(x, y):
            # Logs: "START: calculate_position args=x, y=10"
            # ... code ...
            # Logs: "COMPLETE: calculate_position result=(100, 200)"
            return (100, 200)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        op_name = operation_name or func.__name__
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Log entry
            entry_msg = f"START: {op_name}"
            if include_args and (args or kwargs):
                arg_strs = [repr(arg) for arg in args[:3]]  # Limit to 3 args
                kwarg_strs = [f"{k}={v!r}" for k, v in list(kwargs.items())[:3]]
                all_args = ", ".join(arg_strs + kwarg_strs)
                entry_msg += f" ({all_args})"

            logger.log(level, entry_msg)

            # Execute function
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000

                # Log exit
                exit_msg = f"COMPLETE: {op_name} ({elapsed:.2f}ms)"
                if include_result:
                    exit_msg += f" result={result!r}"

                logger.log(level, exit_msg)
                return result

            except Exception as e:
                elapsed = (time.time() - start) * 1000
                logger.error(
                    f"FAILED: {op_name} ({elapsed:.2f}ms): {e.__class__.__name__}: {e}",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_timing(
    level: int = logging.DEBUG,
    threshold_ms: Optional[float] = None,
) -> Callable:
    """Decorator for performance tracking with optional slow operation alerts.

    Logs execution time. If threshold is set, logs WARNING for slow operations.

    Args:
        level: Log level for normal operations (default: DEBUG)
        threshold_ms: Alert if slower than this many milliseconds (optional)

    Example:
        @log_timing()
        def get_pin_position(component, pin):
            # Logs: "get_pin_position: 5.23ms"
            return position

        @log_timing(threshold_ms=50)
        def expensive_operation():
            # Logs: "expensive_operation: 150.45ms" at WARNING level
            return result
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000

                # Determine log level based on threshold
                log_level = level
                message = f"{func.__name__}: {elapsed:.2f}ms"

                if threshold_ms and elapsed > threshold_ms:
                    log_level = logging.WARNING
                    message += f" (SLOW, threshold: {threshold_ms}ms)"

                logger.log(log_level, message)
                return result

            except Exception as e:
                elapsed = (time.time() - start) * 1000
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms",
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_errors(
    operation_name: Optional[str] = None,
    reraise: bool = True,
) -> Callable:
    """Decorator for comprehensive exception logging and optional suppression.

    Logs exceptions with full context. Can optionally suppress exceptions.

    Args:
        operation_name: Name for error logs (default: function name)
        reraise: Re-raise exception after logging (default: True)

    Example:
        @log_errors(operation_name="validate_circuit")
        def validate(circuit):
            # Logs exception with full context
            # Raises exception
            raise ValueError("Invalid circuit")

        @log_errors(reraise=False)
        def safe_operation():
            # Logs exception but doesn't raise
            # Returns None
            raise RuntimeError("Something went wrong")
            return result  # Not reached
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        op_name = operation_name or func.__name__
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                # Build comprehensive error message
                error_msg = f"Error in {op_name}: {e.__class__.__name__}: {e}"

                # Try to extract component context if available
                component_info = ""
                for arg in args:
                    if hasattr(arg, "reference"):
                        component_info = f" [component: {arg.reference}]"
                        break

                if component_info:
                    error_msg += component_info

                # Log with full context
                logger.error(error_msg, exc_info=True)

                # Either re-raise or suppress
                if reraise:
                    raise
                else:
                    return None

        return wrapper

    return decorator


def log_retry(
    max_attempts: int = 3,
    delay_ms: float = 100,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator for logging retry logic.

    Automatically retries failed operations with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        delay_ms: Delay between retries in milliseconds (default: 100)
        backoff: Multiply delay by this after each retry (default: 2.0)
        exceptions: Exceptions to catch for retry (default: all)

    Example:
        @log_retry(max_attempts=3, delay_ms=100)
        def load_symbol(symbol_name):
            # Retries up to 3 times with exponential backoff
            return load_from_cache(symbol_name)

        @log_retry(exceptions=(IOError, TimeoutError))
        def fetch_data(url):
            # Only retries on IOError or TimeoutError
            return requests.get(url)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            current_delay = delay_ms

            for attempt in range(1, max_attempts + 1):
                try:
                    if attempt > 1:
                        logger.info(f"Retry {attempt}/{max_attempts} for {func.__name__}")

                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed in "
                        f"{func.__name__}: {e.__class__.__name__}: {e}"
                    )

                    if attempt < max_attempts:
                        time.sleep(current_delay / 1000)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")

            # All attempts exhausted
            raise last_exception

        return wrapper

    return decorator


@contextmanager
def log_context(
    context_name: str,
    component: Optional[str] = None,
    log_level: int = logging.DEBUG,
    **context_info: Any,
):
    """Context manager for logging a block of code.

    Logs entry and exit with timing. Logs exceptions.

    Args:
        context_name: Name of the context block
        component: Optional component reference
        log_level: Log level (default: DEBUG)
        **context_info: Additional context information

    Example:
        with log_context("load_symbols", log_level=logging.INFO):
            # Logs: "ENTER: load_symbols"
            # ... code ...
            # Logs: "EXIT: load_symbols (42.3ms)"

        with log_context("configure_resistor", component="R1", value="10k"):
            # Logs: "ENTER: configure_resistor [R1] value=10k"
            # ... code ...
    """
    logger = logging.getLogger(__name__)
    start = time.time()

    # Build entry message
    entry_msg = f"ENTER: {context_name}"
    if component:
        entry_msg += f" [{component}]"
    if context_info:
        info_parts = [f"{k}={v}" for k, v in context_info.items()]
        entry_msg += f" ({', '.join(info_parts)})"

    logger.log(log_level, entry_msg)

    try:
        yield
        # Log successful exit
        elapsed = (time.time() - start) * 1000
        logger.log(log_level, f"EXIT: {context_name} ({elapsed:.2f}ms)")

    except Exception as e:
        elapsed = (time.time() - start) * 1000
        logger.error(
            f"EXCEPTION in {context_name} ({elapsed:.2f}ms): " f"{e.__class__.__name__}: {e}",
            exc_info=True,
        )
        raise


@contextmanager
def log_step(step_name: str, total_steps: Optional[int] = None):
    """Context manager for logging multi-step processes.

    Useful for tracking progress through complex operations.

    Args:
        step_name: Name of this step
        total_steps: Total steps in process (optional)

    Example:
        total = 3
        with log_step("loading symbols", total_steps=total):
            # Logs: "[Step 1/?] loading symbols"
            pass
        with log_step("creating components", total_steps=total):
            # Logs: "[Step 2/?] creating components"
            pass
        with log_step("connecting wires", total_steps=total):
            # Logs: "[Step 3/?] connecting wires"
            pass
    """
    logger = logging.getLogger(__name__)

    # Track step number (would need to be in a wrapper)
    msg = f"Step: {step_name}"
    if total_steps:
        msg += f" (of {total_steps})"

    logger.info(msg)

    try:
        yield
    except Exception as e:
        logger.error(f"Failed at step: {step_name}", exc_info=True)
        raise


class ComponentLogger:
    """Logger for tracking component operations across multiple steps.

    Groups related component operations with automatic tagging.

    Example:
        with ComponentLogger("R1") as logger:
            logger.debug("Setting value")
            logger.info("Configured successfully")
            # All logs automatically tagged with [R1]
    """

    def __init__(self, component_ref: str):
        """Initialize component logger.

        Args:
            component_ref: Component reference (e.g., "R1", "C2")
        """
        self.component_ref = component_ref
        self.logger = logging.getLogger(__name__)
        self.operations: List[Dict[str, Any]] = []

    def debug(self, message: str) -> None:
        """Log debug message."""
        msg = f"[{self.component_ref}] {message}"
        self.logger.debug(msg)
        self._record_operation("DEBUG", message)

    def info(self, message: str) -> None:
        """Log info message."""
        msg = f"[{self.component_ref}] {message}"
        self.logger.info(msg)
        self._record_operation("INFO", message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        msg = f"[{self.component_ref}] {message}"
        self.logger.warning(msg)
        self._record_operation("WARNING", message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message."""
        msg = f"[{self.component_ref}] {message}"
        self.logger.error(msg, exc_info=exc_info)
        self._record_operation("ERROR", message)

    def _record_operation(self, level: str, message: str) -> None:
        """Record operation in internal history."""
        self.operations.append(
            {
                "timestamp": time.time(),
                "level": level,
                "message": message,
            }
        )

    def get_history(self) -> List[Dict[str, Any]]:
        """Get operation history."""
        return self.operations.copy()

    def summary(self) -> str:
        """Get summary of operations."""
        if not self.operations:
            return f"{self.component_ref}: No operations logged"

        levels = {}
        for op in self.operations:
            level = op["level"]
            levels[level] = levels.get(level, 0) + 1

        summary_parts = [f"{self.component_ref}:"]
        for level, count in sorted(levels.items()):
            summary_parts.append(f"{level}={count}")

        return " ".join(summary_parts)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.error(f"Exception: {exc_type.__name__}: {exc_val}")
        return False


class OperationTimer:
    """Context manager for measuring operation time with logging.

    Automatically logs operation timing with optional alerts for slow operations.

    Example:
        with OperationTimer("calculate_positions", threshold_ms=100):
            # Logs: "TIMER: calculate_positions started"
            # ... calculation ...
            # Logs: "TIMER: calculate_positions completed in 50.23ms"

        with OperationTimer("load_library", threshold_ms=500):
            # If slower than 500ms, logs at WARNING level
            pass
    """

    def __init__(
        self,
        operation_name: str,
        threshold_ms: Optional[float] = None,
        log_level: int = logging.INFO,
    ):
        """Initialize timer.

        Args:
            operation_name: Name of operation
            threshold_ms: Alert if slower than this (optional)
            log_level: Log level for normal operations (default: INFO)
        """
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.log_level = log_level
        self.logger = logging.getLogger(__name__)
        self.start_time = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        self.logger.log(self.log_level, f"TIMER: {self.operation_name} started")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and log result."""
        elapsed = (time.time() - self.start_time) * 1000

        if exc_type:
            self.logger.error(
                f"TIMER: {self.operation_name} failed after {elapsed:.2f}ms: "
                f"{exc_type.__name__}: {exc_val}",
                exc_info=True,
            )
            return False

        # Determine log level based on threshold
        level = self.log_level
        message = f"TIMER: {self.operation_name} completed in {elapsed:.2f}ms"

        if self.threshold_ms and elapsed > self.threshold_ms:
            level = logging.WARNING
            message += f" (SLOW, threshold: {self.threshold_ms}ms)"

        self.logger.log(level, message)
        return False

    def elapsed(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time is None:
            return 0
        return (time.time() - self.start_time) * 1000


def trace_calls(
    log_level: int = logging.DEBUG,
) -> Callable:
    """Decorator for detailed call tracing.

    Logs all calls to the function with full arguments and return values.

    Args:
        log_level: Log level for traces (default: DEBUG)

    Example:
        @trace_calls()
        def calculate(x, y, operation="add"):
            # Logs: "TRACE: calculate called with x=5, y=3, operation='add'"
            # ... calculation ...
            # Logs: "TRACE: calculate returned 8"
            return result
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Log call
            arg_strs = [repr(arg) for arg in args]
            kwarg_strs = [f"{k}={v!r}" for k, v in kwargs.items()]
            all_args = ", ".join(arg_strs + kwarg_strs)

            logger.log(log_level, f"TRACE: {func.__name__} called with {all_args}")

            # Execute and log return
            result = func(*args, **kwargs)
            logger.log(log_level, f"TRACE: {func.__name__} returned {result!r}")

            return result

        return wrapper

    return decorator


# Module-level logger
logger = logging.getLogger(__name__)
