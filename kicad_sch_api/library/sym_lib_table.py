"""
KiCAD sym-lib-table parsing and variable resolution.

This module provides functionality to parse KiCAD's sym-lib-table files
and resolve path variables like ${KICAD9_SYMBOL_DIR} and ${KIPRJMOD}.
"""

import logging
import os
import platform
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import sexpdata

logger = logging.getLogger(__name__)


@dataclass
class SymLibTableEntry:
    """A single library entry from sym-lib-table."""

    name: str  # Library nickname (e.g., "EDA-MCP")
    uri: str  # Raw URI with variables (e.g., "${KIPRJMOD}/libraries/symbols/EDA-MCP.kicad_sym")
    type: str = "KiCad"  # Library type (usually "KiCad")
    options: str = ""  # Library options (usually empty)
    description: str = ""  # Library description


@dataclass
class SymLibTable:
    """Parsed sym-lib-table containing library entries."""

    version: int = 7
    entries: List[SymLibTableEntry] = field(default_factory=list)


class SymLibTableVariableResolver:
    """
    Resolves KiCAD path variables to actual filesystem paths.

    Supported variables:
    - ${KICAD9_SYMBOL_DIR}, ${KICAD8_SYMBOL_DIR}, etc. - From environment
    - ${KICAD_SYMBOL_DIR} - Generic version
    - ${KIPRJMOD} - Project directory (requires project_dir to be set)
    - ${KICAD9_3RD_PARTY} - Third party libraries location
    """

    # Pattern to match ${VARIABLE_NAME}
    VARIABLE_PATTERN = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, project_dir: Optional[Path] = None):
        """
        Initialize the resolver.

        Args:
            project_dir: Project directory for ${KIPRJMOD} resolution
        """
        self.project_dir = project_dir
        self._variables = self._build_variable_map()

    def _build_variable_map(self) -> Dict[str, str]:
        """Build map of variable names to resolved paths."""
        variables = {}

        # Environment variable based paths
        env_vars = [
            "KICAD_SYMBOL_DIR",
            "KICAD9_SYMBOL_DIR",
            "KICAD8_SYMBOL_DIR",
            "KICAD7_SYMBOL_DIR",
            "KICAD_TEMPLATE_DIR",
            "KICAD9_TEMPLATE_DIR",
            "KICAD_FOOTPRINT_DIR",
            "KICAD9_FOOTPRINT_DIR",
            "KICAD9_3DMODEL_DIR",
        ]

        for env_var in env_vars:
            value = os.environ.get(env_var)
            if value:
                variables[env_var] = value
                logger.debug(f"Loaded env variable {env_var}={value}")

        # KIPRJMOD - project directory
        if self.project_dir:
            variables["KIPRJMOD"] = str(self.project_dir)
            logger.debug(f"Set KIPRJMOD={self.project_dir}")

        # Platform-specific default paths
        system = platform.system()

        if system == "Darwin":  # macOS
            # KiCAD 9 default paths on macOS
            kicad_share = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport")
            if kicad_share.exists():
                if "KICAD9_SYMBOL_DIR" not in variables:
                    symbol_dir = kicad_share / "symbols"
                    if symbol_dir.exists():
                        variables["KICAD9_SYMBOL_DIR"] = str(symbol_dir)
                if "KICAD9_FOOTPRINT_DIR" not in variables:
                    fp_dir = kicad_share / "footprints"
                    if fp_dir.exists():
                        variables["KICAD9_FOOTPRINT_DIR"] = str(fp_dir)
                if "KICAD9_3DMODEL_DIR" not in variables:
                    model_dir = kicad_share / "3dmodels"
                    if model_dir.exists():
                        variables["KICAD9_3DMODEL_DIR"] = str(model_dir)

            # Third party libraries location
            third_party = Path.home() / "Documents" / "KiCad" / "9.0"
            if third_party.exists():
                variables["KICAD9_3RD_PARTY"] = str(third_party)

        elif system == "Linux":
            # Standard Linux paths
            kicad_share = Path("/usr/share/kicad")
            if kicad_share.exists():
                if "KICAD9_SYMBOL_DIR" not in variables:
                    symbol_dir = kicad_share / "symbols"
                    if symbol_dir.exists():
                        variables["KICAD9_SYMBOL_DIR"] = str(symbol_dir)

            # User third party
            third_party = Path.home() / ".local" / "share" / "kicad" / "9.0"
            if third_party.exists():
                variables["KICAD9_3RD_PARTY"] = str(third_party)

        elif system == "Windows":
            # Windows default paths
            program_files = Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
            kicad_base = program_files / "KiCad" / "9.0"
            if kicad_base.exists():
                symbol_dir = kicad_base / "share" / "kicad" / "symbols"
                if symbol_dir.exists() and "KICAD9_SYMBOL_DIR" not in variables:
                    variables["KICAD9_SYMBOL_DIR"] = str(symbol_dir)

            # User third party
            appdata = Path(os.environ.get("APPDATA", ""))
            if appdata:
                third_party = appdata / "kicad" / "9.0"
                if third_party.exists():
                    variables["KICAD9_3RD_PARTY"] = str(third_party)

        return variables

    def resolve(self, uri: str) -> Optional[Path]:
        """
        Resolve a URI with variables to an actual filesystem path.

        Args:
            uri: URI string potentially containing ${VARIABLE} patterns

        Returns:
            Resolved Path if all variables resolved and path exists, None otherwise
        """
        resolved = uri

        # Find and replace all variables
        def replace_var(match):
            var_name = match.group(1)
            if var_name in self._variables:
                return self._variables[var_name]
            logger.warning(f"Unknown variable: ${{{var_name}}}")
            return match.group(0)  # Keep original if unknown

        resolved = self.VARIABLE_PATTERN.sub(replace_var, resolved)

        # Check if any variables remain unresolved
        if self.VARIABLE_PATTERN.search(resolved):
            logger.debug(f"URI contains unresolved variables: {resolved}")
            return None

        path = Path(resolved)

        # Handle relative paths (relative to project dir if set)
        if not path.is_absolute() and self.project_dir:
            path = self.project_dir / path

        return path

    def add_variable(self, name: str, value: str):
        """Add or update a variable mapping."""
        self._variables[name] = value
        logger.debug(f"Added variable {name}={value}")


class SymLibTableParser:
    """
    Parser for KiCAD sym-lib-table files.

    sym-lib-table files use S-expression format:
    (sym_lib_table
      (version 7)
      (lib (name "Device")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Device.kicad_sym")(options "")(descr ""))
      ...
    )
    """

    @staticmethod
    def parse(file_path: Path) -> Optional[SymLibTable]:
        """
        Parse a sym-lib-table file.

        Args:
            file_path: Path to sym-lib-table file

        Returns:
            Parsed SymLibTable or None on error
        """
        if not file_path.exists():
            logger.warning(f"sym-lib-table not found: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            parsed = sexpdata.loads(content, true=None, false=None, nil=None)

            if not isinstance(parsed, list) or len(parsed) < 1:
                logger.warning(f"Invalid sym-lib-table format: {file_path}")
                return None

            # Verify it's a sym_lib_table
            if parsed[0] != sexpdata.Symbol("sym_lib_table"):
                logger.warning(f"Not a sym_lib_table file: {file_path}")
                return None

            table = SymLibTable()

            # Parse entries
            for item in parsed[1:]:
                if isinstance(item, list) and len(item) > 0:
                    if item[0] == sexpdata.Symbol("version"):
                        if len(item) > 1:
                            table.version = int(item[1])
                    elif item[0] == sexpdata.Symbol("lib"):
                        entry = SymLibTableParser._parse_lib_entry(item)
                        if entry:
                            table.entries.append(entry)

            logger.info(f"Parsed sym-lib-table with {len(table.entries)} entries from {file_path}")
            return table

        except Exception as e:
            logger.error(f"Error parsing sym-lib-table {file_path}: {e}")
            return None

    @staticmethod
    def _parse_lib_entry(lib_data: List) -> Optional[SymLibTableEntry]:
        """Parse a single (lib ...) entry."""
        try:
            entry = SymLibTableEntry(name="", uri="")

            for item in lib_data[1:]:
                if isinstance(item, list) and len(item) >= 2:
                    key = item[0]
                    value = item[1]

                    # Handle string values (may be sexpdata.Symbol or str)
                    if hasattr(value, "value"):
                        value = value.value()
                    value = str(value).strip('"')

                    if key == sexpdata.Symbol("name"):
                        entry.name = value
                    elif key == sexpdata.Symbol("type"):
                        entry.type = value
                    elif key == sexpdata.Symbol("uri"):
                        entry.uri = value
                    elif key == sexpdata.Symbol("options"):
                        entry.options = value
                    elif key == sexpdata.Symbol("descr"):
                        entry.description = value

            if entry.name and entry.uri:
                return entry
            else:
                logger.warning(f"Incomplete lib entry: name={entry.name}, uri={entry.uri}")
                return None

        except Exception as e:
            logger.error(f"Error parsing lib entry: {e}")
            return None

    @staticmethod
    def get_global_sym_lib_table_path() -> Optional[Path]:
        """
        Get platform-specific path to global sym-lib-table.

        Returns:
            Path to global sym-lib-table or None if not found
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            # Try KiCAD 9 first, then fall back to older versions
            paths = [
                Path.home() / "Library" / "Preferences" / "kicad" / "9.0" / "sym-lib-table",
                Path.home() / "Library" / "Preferences" / "kicad" / "8.0" / "sym-lib-table",
                Path.home() / "Library" / "Preferences" / "kicad" / "7.0" / "sym-lib-table",
            ]
        elif system == "Linux":
            paths = [
                Path.home() / ".config" / "kicad" / "9.0" / "sym-lib-table",
                Path.home() / ".config" / "kicad" / "8.0" / "sym-lib-table",
                Path.home() / ".config" / "kicad" / "7.0" / "sym-lib-table",
            ]
        elif system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            if appdata:
                paths = [
                    appdata / "kicad" / "9.0" / "sym-lib-table",
                    appdata / "kicad" / "8.0" / "sym-lib-table",
                    appdata / "kicad" / "7.0" / "sym-lib-table",
                ]
            else:
                paths = []
        else:
            paths = []

        for path in paths:
            if path.exists():
                logger.debug(f"Found global sym-lib-table: {path}")
                return path

        logger.warning("No global sym-lib-table found")
        return None

    @staticmethod
    def get_project_sym_lib_table_path(project_dir: Path) -> Optional[Path]:
        """
        Get path to project-local sym-lib-table.

        Args:
            project_dir: Project directory

        Returns:
            Path to project sym-lib-table or None if not found
        """
        path = project_dir / "sym-lib-table"
        if path.exists():
            logger.debug(f"Found project sym-lib-table: {path}")
            return path
        return None
