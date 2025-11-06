"""
Utility functions for the MCP server.

Provides logging configuration and helper functions for MCP tools.
"""

import logging
import sys
from typing import Optional


def configure_mcp_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the MCP server.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def get_mcp_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for MCP server components.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
