"""Logging configuration and helpers for MCP server.

This module provides MCP server-specific logging setup with:
- Integration with kicad_sch_api logging
- MCP protocol logging
- Tool invocation tracking
- Performance metrics
"""

import logging
from pathlib import Path
from typing import Optional
import sys

# Import base logging utilities from kicad_sch_api
try:
    from kicad_sch_api.utils.logging import (
        configure_logging,
        operation_context,
        timer_decorator,
        log_exception,
        setup_component_logging,
        search_logs,
        LogQuery,
    )
    from kicad_sch_api.utils.logging_decorators import (
        log_operation,
        log_timing,
        log_errors,
        ComponentLogger,
        OperationTimer,
    )

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


def configure_mcp_logging(
    log_dir: Path = Path("logs"),
    debug_level: bool = False,
    json_format: bool = True,
) -> None:
    """Configure logging for MCP server.

    Extends the base kicad_sch_api logging with MCP-specific setup.

    Args:
        log_dir: Directory for log files (default: logs/)
        debug_level: Enable DEBUG level logging (default: False)
        json_format: Use JSON format (default: True, production)

    Example:
        # Development setup
        configure_mcp_logging(debug_level=True, json_format=False)

        # Production setup
        configure_mcp_logging(debug_level=False, json_format=True)
    """
    if not LOGGING_AVAILABLE:
        # Fallback to basic logging if kicad_sch_api logging unavailable
        logging.basicConfig(
            level=logging.DEBUG if debug_level else logging.INFO,
            format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        )
        return

    # Configure base logging
    configure_logging(
        log_dir=log_dir,
        debug_level=debug_level,
        json_format=json_format,
        max_bytes=10 * 1024 * 1024,  # 10MB
        backup_count=5,
    )

    # Get MCP server logger
    logger = logging.getLogger("mcp_server")
    logger.info(
        f"MCP server logging configured: "
        f"debug={debug_level}, json={json_format}"
    )


def get_mcp_logger(component: Optional[str] = None) -> logging.Logger:
    """Get a logger for MCP server operations.

    Args:
        component: Optional component name for context

    Returns:
        Configured logger instance

    Example:
        logger = get_mcp_logger("tools")
        logger.info("Tool invoked")

        # Component-specific logger
        logger = get_mcp_logger("resistor_R1")
        logger.debug("Setting value")
    """
    if component:
        return logging.getLogger(f"mcp_server.{component}")
    return logging.getLogger("mcp_server")


# Re-export commonly used utilities for convenience
__all__ = [
    # Configuration
    "configure_mcp_logging",
    "get_mcp_logger",
    # Context managers
    "operation_context",
    # Decorators
    "log_operation",
    "log_timing",
    "log_errors",
    "timer_decorator",
    # Helpers
    "ComponentLogger",
    "OperationTimer",
    "log_exception",
    "setup_component_logging",
    # Querying
    "search_logs",
    "LogQuery",
]
