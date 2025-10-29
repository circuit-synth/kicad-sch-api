"""
Metadata Manager for KiCAD schematic configuration.

Handles schematic-level settings, properties, and configuration including
paper size, title block, version information, and instance sections.
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseManager

logger = logging.getLogger(__name__)


class MetadataManager(BaseManager):
    """
    Manages schematic metadata and configuration settings.

    Responsible for:
    - Title block management
    - Paper size and page setup
    - Version and generator information
    - Library and instance sections
    - Schema-level properties
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize MetadataManager with schematic data.

        Args:
            schematic_data: Reference to schematic data dictionary
        """
        super().__init__(schematic_data)

    def set_paper_size(self, paper: str) -> None:
        """
        Set paper size for the schematic.

        Args:
            paper: Paper size (e.g., "A4", "A3", "Letter", "Legal")
        """
        from ..config import config

        if paper not in config.paper.valid_sizes:
            logger.warning(f"Unusual paper size: {paper}. Valid sizes: {config.paper.valid_sizes}")

        self._data["paper"] = paper
        logger.debug(f"Set paper size: {paper}")

    def set_version_info(
        self, version: Optional[int] = None, generator: Optional[str] = None
    ) -> None:
        """
        Set KiCAD version and generator information.

        Args:
            version: KiCAD schema version number
            generator: Generator application string
        """
        if version is not None:
            self._data["version"] = version
            logger.debug(f"Set version: {version}")

        if generator is not None:
            self._data["generator"] = generator
            logger.debug(f"Set generator: {generator}")

    def set_title_block(
        self,
        title: str = "",
        date: str = "",
        rev: str = "",
        company: str = "",
        comments: Optional[Dict[int, str]] = None,
    ) -> None:
        """
        Set title block information.

        Args:
            title: Schematic title
            date: Creation/revision date
            rev: Revision number
            company: Company name
            comments: Numbered comments (1, 2, 3, etc.)
        """
        if comments is None:
            comments = {}

        self._data["title_block"] = {
            "title": title,
            "date": date,
            "rev": rev,
            "company": company,
            "comments": comments,
        }

        logger.debug(f"Set title block: {title} rev {rev}")

    def copy_metadata_from(self, source_data: Dict[str, Any]) -> None:
        """
        Copy metadata from another schematic.

        Args:
            source_data: Source schematic data to copy from
        """
        # Copy basic metadata
        for key in ["paper", "version", "generator"]:
            if key in source_data:
                self._data[key] = source_data[key]

        # Copy title block if present
        if "title_block" in source_data:
            self._data["title_block"] = source_data["title_block"].copy()

        # Copy lib_symbols if present
        if "lib_symbols" in source_data:
            self._data["lib_symbols"] = source_data["lib_symbols"].copy()

        logger.info("Copied metadata from source schematic")

    def add_lib_symbols_section(self, lib_symbols: Dict[str, Any]) -> None:
        """
        Add or update lib_symbols section.

        Args:
            lib_symbols: Library symbols data
        """
        self._data["lib_symbols"] = lib_symbols
        logger.debug(f"Updated lib_symbols section with {len(lib_symbols)} symbols")

    def add_instances_section(self, instances: Dict[str, Any]) -> None:
        """
        Add or update symbol instances section.

        Args:
            instances: Symbol instances data
        """
        self._data["symbol_instances"] = instances
        logger.debug("Updated symbol_instances section")

    def add_sheet_instances_section(self, sheet_instances: List[Dict]) -> None:
        """
        Add or update sheet instances section.

        Args:
            sheet_instances: List of sheet instance data
        """
        self._data["sheet_instances"] = sheet_instances
        logger.debug(f"Updated sheet_instances section with {len(sheet_instances)} instances")

    def set_uuid(self, uuid_str: str) -> None:
        """
        Set schematic UUID.

        Args:
            uuid_str: UUID string for the schematic
        """
        self._data["uuid"] = uuid_str
        logger.debug(f"Set schematic UUID: {uuid_str}")

    def get_version(self) -> Optional[int]:
        """Get KiCAD schema version."""
        return self._data.get("version")

    def get_generator(self) -> Optional[str]:
        """Get generator application string."""
        return self._data.get("generator")

    def get_uuid(self) -> Optional[str]:
        """Get schematic UUID."""
        return self._data.get("uuid")

    def get_paper_size(self) -> Optional[str]:
        """Get paper size."""
        return self._data.get("paper")

    def get_title_block(self) -> Dict[str, Any]:
        """
        Get title block information.

        Returns:
            Title block data dictionary
        """
        return self._data.get("title_block", {})

    def get_lib_symbols(self) -> Dict[str, Any]:
        """
        Get lib_symbols section.

        Returns:
            Library symbols data
        """
        return self._data.get("lib_symbols", {})

    def get_symbol_instances(self) -> Dict[str, Any]:
        """
        Get symbol instances section.

        Returns:
            Symbol instances data
        """
        return self._data.get("symbol_instances", {})

    def get_sheet_instances(self) -> List[Dict]:
        """
        Get sheet instances section.

        Returns:
            List of sheet instances
        """
        return self._data.get("sheet_instances", [])

    def get_metadata_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive metadata summary.

        Returns:
            Dictionary with all metadata information
        """
        title_block = self.get_title_block()

        return {
            "version": self.get_version(),
            "generator": self.get_generator(),
            "uuid": self.get_uuid(),
            "paper": self.get_paper_size(),
            "title": title_block.get("title", ""),
            "revision": title_block.get("rev", ""),
            "company": title_block.get("company", ""),
            "date": title_block.get("date", ""),
            "comments": title_block.get("comments", {}),
            "lib_symbols_count": len(self.get_lib_symbols()),
            "symbol_instances_count": (
                len(self.get_symbol_instances())
                if isinstance(self.get_symbol_instances(), list)
                else 1 if self.get_symbol_instances() else 0
            ),
            "sheet_instances_count": len(self.get_sheet_instances()),
        }

    def validate_metadata(self) -> List[str]:
        """
        Validate metadata consistency and completeness.

        Returns:
            List of validation warnings/issues
        """
        issues = []

        # Check required fields
        if not self.get_version():
            issues.append("Missing KiCAD version")

        if not self.get_generator():
            issues.append("Missing generator information")

        # Check title block
        title_block = self.get_title_block()
        if not title_block.get("title"):
            issues.append("Title block missing title")

        # Check paper size
        from ..config import config

        paper = self.get_paper_size()
        if paper and paper not in config.paper.valid_sizes:
            issues.append(f"Non-standard paper size: {paper}")

        return issues
