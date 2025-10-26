"""
Repository interfaces for schematic data persistence.

These interfaces define the contract for loading and saving schematic data,
abstracting away the specific file format and storage mechanisms.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Protocol, Union


class ISchematicRepository(Protocol):
    """Interface for schematic data persistence operations."""

    def load(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Load schematic data from a file.

        Args:
            filepath: Path to the schematic file

        Returns:
            Complete schematic data structure

        Raises:
            FileNotFoundError: If file doesn't exist
            RepositoryError: If file cannot be loaded
        """
        ...

    def save(self, data: Dict[str, Any], filepath: Union[str, Path]) -> None:
        """
        Save schematic data to a file.

        Args:
            data: Complete schematic data structure
            filepath: Path where to save the file

        Raises:
            RepositoryError: If file cannot be saved
        """
        ...

    def exists(self, filepath: Union[str, Path]) -> bool:
        """
        Check if a schematic file exists.

        Args:
            filepath: Path to check

        Returns:
            True if file exists and is accessible
        """
        ...

    def validate_format(self, filepath: Union[str, Path]) -> bool:
        """
        Validate that a file is in the correct format.

        Args:
            filepath: Path to the file to validate

        Returns:
            True if file format is valid

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        ...
