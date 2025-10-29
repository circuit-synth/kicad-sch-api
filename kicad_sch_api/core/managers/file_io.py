"""
File I/O Manager for KiCAD schematic operations.

Handles all file system interactions including loading, saving, and backup operations
while maintaining exact format preservation.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ...utils.validation import ValidationError
from ..config import config
from ..formatter import ExactFormatter
from ..parser import SExpressionParser
from .base import BaseManager

logger = logging.getLogger(__name__)


class FileIOManager(BaseManager):
    """
    Manages file I/O operations for KiCAD schematics.

    Responsible for:
    - Loading schematic files with validation
    - Saving with format preservation
    - Creating backup files
    - Managing file paths and metadata
    """

    def __init__(self):
        """Initialize the FileIOManager."""
        super().__init__()
        self._parser = SExpressionParser(preserve_format=True)
        self._formatter = ExactFormatter()

    def load_schematic(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load a KiCAD schematic file.

        Args:
            file_path: Path to .kicad_sch file

        Returns:
            Parsed schematic data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If file is invalid or corrupted
        """
        start_time = time.time()
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Schematic file not found: {file_path}")

        if not file_path.suffix == ".kicad_sch":
            raise ValidationError(f"Not a KiCAD schematic file: {file_path}")

        logger.info(f"Loading schematic: {file_path}")

        try:
            schematic_data = self._parser.parse_file(file_path)
            load_time = time.time() - start_time
            logger.info(f"Loaded schematic in {load_time:.3f}s")

            return schematic_data

        except Exception as e:
            logger.error(f"Failed to load schematic {file_path}: {e}")
            raise ValidationError(f"Invalid schematic file: {e}") from e

    def save_schematic(
        self,
        schematic_data: Dict[str, Any],
        file_path: Union[str, Path],
        preserve_format: bool = True,
    ) -> None:
        """
        Save schematic data to file.

        Args:
            schematic_data: Schematic data to save
            file_path: Target file path
            preserve_format: Whether to preserve exact formatting

        Raises:
            PermissionError: If file cannot be written
            ValidationError: If data is invalid
        """
        start_time = time.time()
        file_path = Path(file_path)

        logger.info(f"Saving schematic: {file_path}")

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to S-expression format and save
            sexp_data = self._parser._schematic_data_to_sexp(schematic_data)
            formatted_content = self._formatter.format(sexp_data)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(formatted_content)

            save_time = time.time() - start_time
            logger.info(f"Saved schematic in {save_time:.3f}s")

        except PermissionError as e:
            logger.error(f"Permission denied saving to {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to save schematic to {file_path}: {e}")
            raise ValidationError(f"Save failed: {e}") from e

    def create_backup(self, file_path: Union[str, Path], suffix: str = ".backup") -> Path:
        """
        Create a backup copy of the schematic file.

        Args:
            file_path: Source file to backup
            suffix: Backup file suffix

        Returns:
            Path to backup file

        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If backup cannot be created
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")

        # Create backup with timestamp if suffix doesn't include one
        if suffix == ".backup":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.with_suffix(f".{timestamp}.backup")
        else:
            backup_path = file_path.with_suffix(f"{file_path.suffix}{suffix}")

        try:
            # Copy file content
            backup_path.write_bytes(file_path.read_bytes())
            logger.info(f"Created backup: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup {backup_path}: {e}")
            raise PermissionError(f"Backup failed: {e}") from e

    def validate_file_path(self, file_path: Union[str, Path]) -> Path:
        """
        Validate and normalize a file path for schematic operations.

        Args:
            file_path: Path to validate

        Returns:
            Normalized Path object

        Raises:
            ValidationError: If path is invalid
        """
        file_path = Path(file_path)

        # Ensure .kicad_sch extension
        if not file_path.suffix:
            file_path = file_path.with_suffix(".kicad_sch")
        elif file_path.suffix != ".kicad_sch":
            raise ValidationError(f"Invalid schematic file extension: {file_path.suffix}")

        # Validate path characters
        try:
            file_path.resolve()
        except (OSError, ValueError) as e:
            raise ValidationError(f"Invalid file path: {e}") from e

        return file_path

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get file system information about a schematic file.

        Args:
            file_path: Path to analyze

        Returns:
            Dictionary with file information

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()

        return {
            "path": str(file_path.resolve()),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": getattr(stat, "st_birthtime", stat.st_ctime),
            "readable": file_path.is_file() and file_path.exists(),
            "writable": file_path.parent.exists() and file_path.parent.is_dir(),
            "extension": file_path.suffix,
        }

    def create_empty_schematic_data(self) -> Dict[str, Any]:
        """
        Create empty schematic data structure.

        Returns:
            Empty schematic data dictionary
        """
        return {
            "kicad_sch": {
                "version": 20230819,
                "generator": config.file_format.generator_default,
                "uuid": None,  # Will be set by calling code
                "paper": config.paper.default,
                "lib_symbols": {},
                "symbol": [],
                "wire": [],
                "junction": [],
                "label": [],
                "hierarchical_label": [],
                "global_label": [],
                "text": [],
                "text_box": [],
                "polyline": [],
                "rectangle": [],
                "circle": [],
                "arc": [],
                "image": [],
                "sheet": [],
                "sheet_instances": [],
                "symbol_instances": [],
            }
        }
