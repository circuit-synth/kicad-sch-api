"""
Main Schematic class for KiCAD schematic manipulation.

This module provides the primary interface for loading, modifying, and saving
KiCAD schematic files with exact format preservation and professional features.
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..library.cache import get_symbol_cache
from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .components import ComponentCollection
from .formatter import ExactFormatter
from .parser import SExpressionParser
from .types import Junction, Label, Net, Point, SchematicSymbol, TitleBlock, Wire

logger = logging.getLogger(__name__)


class Schematic:
    """
    Professional KiCAD schematic manipulation class.

    Features:
    - Exact format preservation
    - Enhanced component management with fast lookup
    - Advanced library integration
    - Comprehensive validation
    - Performance optimization for large schematics
    - AI agent integration via MCP

    This class provides a modern, intuitive API while maintaining exact compatibility
    with KiCAD's native file format.
    """

    def __init__(self, schematic_data: Dict[str, Any] = None, file_path: Optional[str] = None):
        """
        Initialize schematic object.

        Args:
            schematic_data: Parsed schematic data
            file_path: Original file path (for format preservation)
        """
        # Core data
        self._data = schematic_data or self._create_empty_schematic_data()
        self._file_path = Path(file_path) if file_path else None
        self._original_content = self._data.get("_original_content", "")

        # Initialize parser and formatter
        self._parser = SExpressionParser(preserve_format=True)
        self._formatter = ExactFormatter()
        self._validator = SchematicValidator()

        # Initialize component collection
        component_symbols = [
            SchematicSymbol(**comp) if isinstance(comp, dict) else comp
            for comp in self._data.get("components", [])
        ]
        self._components = ComponentCollection(component_symbols)

        # Track modifications for save optimization
        self._modified = False
        self._last_save_time = None

        # Performance tracking
        self._operation_count = 0
        self._total_operation_time = 0.0

        logger.debug(f"Schematic initialized with {len(self._components)} components")

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "Schematic":
        """
        Load a KiCAD schematic file.

        Args:
            file_path: Path to .kicad_sch file

        Returns:
            Loaded Schematic object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If file is invalid or corrupted
        """
        start_time = time.time()
        file_path = Path(file_path)

        logger.info(f"Loading schematic: {file_path}")

        parser = SExpressionParser(preserve_format=True)
        schematic_data = parser.parse_file(file_path)

        load_time = time.time() - start_time
        logger.info(f"Loaded schematic in {load_time:.3f}s")

        return cls(schematic_data, str(file_path))

    @classmethod
    def create(cls, name: str = "Untitled", version: str = "20230121") -> "Schematic":
        """
        Create a new empty schematic.

        Args:
            name: Schematic name
            version: KiCAD version string

        Returns:
            New empty Schematic object
        """
        schematic_data = cls._create_empty_schematic_data()
        schematic_data["version"] = version
        schematic_data["title_block"] = {"title": name}

        logger.info(f"Created new schematic: {name}")
        return cls(schematic_data)

    # Core properties
    @property
    def components(self) -> ComponentCollection:
        """Collection of all components in the schematic."""
        return self._components

    @property
    def version(self) -> Optional[str]:
        """KiCAD version string."""
        return self._data.get("version")

    @property
    def generator(self) -> Optional[str]:
        """Generator string (e.g., 'eeschema')."""
        return self._data.get("generator")

    @property
    def uuid(self) -> Optional[str]:
        """Schematic UUID."""
        return self._data.get("uuid")

    @property
    def title_block(self) -> Dict[str, Any]:
        """Title block information."""
        return self._data.get("title_block", {})

    @property
    def file_path(self) -> Optional[Path]:
        """Current file path."""
        return self._file_path

    @property
    def modified(self) -> bool:
        """Whether schematic has been modified since last save."""
        return self._modified or self._components._modified

    # File operations
    def save(self, file_path: Optional[Union[str, Path]] = None, preserve_format: bool = True):
        """
        Save schematic to file.

        Args:
            file_path: Output file path (uses current path if None)
            preserve_format: Whether to preserve exact formatting

        Raises:
            ValidationError: If schematic data is invalid
        """
        start_time = time.time()

        # Use current file path if not specified
        if file_path is None:
            if self._file_path is None:
                raise ValidationError("No file path specified and no current file")
            file_path = self._file_path
        else:
            file_path = Path(file_path)
            self._file_path = file_path

        # Validate before saving
        issues = self.validate()
        errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
        if errors:
            raise ValidationError("Cannot save schematic with validation errors", errors)

        # Update data structure with current component state
        self._sync_components_to_data()

        # Write file
        if preserve_format and self._original_content:
            # Use format-preserving writer
            sexp_data = self._parser._schematic_data_to_sexp(self._data)
            content = self._formatter.format_preserving_write(sexp_data, self._original_content)
        else:
            # Standard formatting
            sexp_data = self._parser._schematic_data_to_sexp(self._data)
            content = self._formatter.format(sexp_data)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Update state
        self._modified = False
        self._components._modified = False
        self._last_save_time = time.time()

        save_time = time.time() - start_time
        logger.info(f"Saved schematic to {file_path} in {save_time:.3f}s")

    def save_as(self, file_path: Union[str, Path], preserve_format: bool = True):
        """Save schematic to a new file path."""
        self.save(file_path, preserve_format)

    def backup(self, suffix: str = ".backup") -> Path:
        """
        Create a backup of the current schematic file.

        Args:
            suffix: Suffix to add to backup filename

        Returns:
            Path to backup file
        """
        if not self._file_path:
            raise ValidationError("Cannot backup - no file path set")

        backup_path = self._file_path.with_suffix(self._file_path.suffix + suffix)

        if self._file_path.exists():
            import shutil

            shutil.copy2(self._file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

        return backup_path

    # Validation and analysis
    def validate(self) -> List[ValidationIssue]:
        """
        Validate the schematic for errors and issues.

        Returns:
            List of validation issues found
        """
        # Sync current state to data for validation
        self._sync_components_to_data()

        # Use validator to check schematic
        issues = self._validator.validate_schematic_data(self._data)

        # Add component-level validation
        component_issues = self._components.validate_all()
        issues.extend(component_issues)

        return issues

    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about the schematic."""
        component_stats = self._components.get_statistics()

        return {
            "file_path": str(self._file_path) if self._file_path else None,
            "version": self.version,
            "uuid": self.uuid,
            "title": self.title_block.get("title", ""),
            "component_count": len(self._components),
            "modified": self.modified,
            "last_save": self._last_save_time,
            "component_stats": component_stats,
            "performance": {
                "operation_count": self._operation_count,
                "avg_operation_time_ms": round(
                    (
                        (self._total_operation_time / self._operation_count * 1000)
                        if self._operation_count > 0
                        else 0
                    ),
                    2,
                ),
            },
        }

    # Wire and connection management (basic implementation)
    def add_wire(
        self, start: Union[Point, Tuple[float, float]], end: Union[Point, Tuple[float, float]]
    ) -> str:
        """
        Add a wire connection.

        Args:
            start: Start point
            end: End point

        Returns:
            UUID of created wire
        """
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        wire = Wire(uuid=str(uuid.uuid4()), start=start, end=end)

        if "wires" not in self._data:
            self._data["wires"] = []

        self._data["wires"].append(wire.__dict__)
        self._modified = True

        logger.debug(f"Added wire: {start} -> {end}")
        return wire.uuid

    def remove_wire(self, wire_uuid: str) -> bool:
        """Remove wire by UUID."""
        wires = self._data.get("wires", [])
        for i, wire in enumerate(wires):
            if wire.get("uuid") == wire_uuid:
                del wires[i]
                self._modified = True
                logger.debug(f"Removed wire: {wire_uuid}")
                return True
        return False

    # Library management
    @property
    def libraries(self) -> "LibraryManager":
        """Access to library management."""
        if not hasattr(self, "_library_manager"):
            from ..library.manager import LibraryManager

            self._library_manager = LibraryManager(self)
        return self._library_manager

    # Utility methods
    def clear(self):
        """Clear all components, wires, and other elements."""
        self._data["components"] = []
        self._data["wires"] = []
        self._data["junctions"] = []
        self._data["labels"] = []
        self._components = ComponentCollection()
        self._modified = True
        logger.info("Cleared schematic")

    def clone(self, new_name: Optional[str] = None) -> "Schematic":
        """Create a copy of this schematic."""
        import copy

        cloned_data = copy.deepcopy(self._data)

        if new_name:
            cloned_data["title_block"]["title"] = new_name
            cloned_data["uuid"] = str(uuid.uuid4())  # New UUID for clone

        return Schematic(cloned_data)

    # Performance optimization
    def rebuild_indexes(self):
        """Rebuild internal indexes for performance."""
        # This would rebuild component indexes, etc.
        logger.info("Rebuilt schematic indexes")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_stats = get_symbol_cache().get_performance_stats()

        return {
            "schematic": {
                "operation_count": self._operation_count,
                "total_operation_time_s": round(self._total_operation_time, 3),
                "avg_operation_time_ms": round(
                    (
                        (self._total_operation_time / self._operation_count * 1000)
                        if self._operation_count > 0
                        else 0
                    ),
                    2,
                ),
            },
            "components": self._components.get_statistics(),
            "symbol_cache": cache_stats,
        }

    # Internal methods
    def _sync_components_to_data(self):
        """Sync component collection state back to data structure."""
        self._data["components"] = [comp._data.__dict__ for comp in self._components]

    @staticmethod
    def _create_empty_schematic_data() -> Dict[str, Any]:
        """Create empty schematic data structure."""
        return {
            "version": "20230121",
            "generator": "kicad-sch-api",
            "uuid": str(uuid.uuid4()),
            "title_block": {
                "title": "Untitled",
                "date": "",
                "revision": "1.0",
                "company": "",
                "size": "A4",
            },
            "components": [],
            "wires": [],
            "junctions": [],
            "labels": [],
            "nets": [],
            "lib_symbols": {},
        }

    # Context manager support for atomic operations
    def __enter__(self):
        """Enter atomic operation context."""
        # Create backup for potential rollback
        if self._file_path and self._file_path.exists():
            self._backup_path = self.backup(".atomic_backup")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit atomic operation context."""
        if exc_type is not None:
            # Exception occurred - rollback if possible
            if hasattr(self, "_backup_path") and self._backup_path.exists():
                logger.warning("Exception in atomic operation - rolling back")
                # Restore from backup
                restored_data = self._parser.parse_file(self._backup_path)
                self._data = restored_data
                self._modified = True
        else:
            # Success - clean up backup
            if hasattr(self, "_backup_path") and self._backup_path.exists():
                self._backup_path.unlink()

    def __str__(self) -> str:
        """String representation."""
        title = self.title_block.get("title", "Untitled")
        component_count = len(self._components)
        return f"<Schematic '{title}': {component_count} components>"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Schematic(file='{self._file_path}', "
            f"components={len(self._components)}, "
            f"modified={self.modified})"
        )


# Convenience functions for common operations
def load_schematic(file_path: Union[str, Path]) -> Schematic:
    """
    Load a KiCAD schematic file.

    Args:
        file_path: Path to .kicad_sch file

    Returns:
        Loaded Schematic object
    """
    return Schematic.load(file_path)


def create_schematic(name: str = "New Circuit") -> Schematic:
    """
    Create a new empty schematic.

    Args:
        name: Schematic name for title block

    Returns:
        New Schematic object
    """
    return Schematic.create(name)
