"""
Tests for sym-lib-table parsing and variable resolution.
"""

import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from kicad_sch_api.library.sym_lib_table import (
    SymLibTable,
    SymLibTableEntry,
    SymLibTableParser,
    SymLibTableVariableResolver,
)


class TestSymLibTableEntry:
    """Tests for SymLibTableEntry dataclass."""

    def test_entry_creation(self):
        """Test creating a basic entry."""
        entry = SymLibTableEntry(
            name="Device",
            uri="${KICAD9_SYMBOL_DIR}/Device.kicad_sym",
            type="KiCad",
            options="",
            description="Standard device symbols",
        )
        assert entry.name == "Device"
        assert entry.uri == "${KICAD9_SYMBOL_DIR}/Device.kicad_sym"
        assert entry.type == "KiCad"
        assert entry.description == "Standard device symbols"

    def test_entry_defaults(self):
        """Test entry default values."""
        entry = SymLibTableEntry(name="Test", uri="/path/to/lib.kicad_sym")
        assert entry.type == "KiCad"
        assert entry.options == ""
        assert entry.description == ""


class TestSymLibTableVariableResolver:
    """Tests for variable resolution."""

    def test_resolve_kiprjmod(self):
        """Test resolving ${KIPRJMOD} variable."""
        project_dir = Path("/home/user/projects/myproject")
        resolver = SymLibTableVariableResolver(project_dir)

        uri = "${KIPRJMOD}/libraries/symbols/EDA-MCP.kicad_sym"
        resolved = resolver.resolve(uri)

        assert resolved == Path("/home/user/projects/myproject/libraries/symbols/EDA-MCP.kicad_sym")

    def test_resolve_env_variable(self):
        """Test resolving environment variable."""
        with patch.dict(os.environ, {"KICAD9_SYMBOL_DIR": "/opt/kicad/symbols"}):
            resolver = SymLibTableVariableResolver()
            uri = "${KICAD9_SYMBOL_DIR}/Device.kicad_sym"
            resolved = resolver.resolve(uri)
            assert resolved == Path("/opt/kicad/symbols/Device.kicad_sym")

    def test_resolve_unset_variable_returns_none(self):
        """Test that unset variables result in None return."""
        # Ensure the variable is not set
        with patch.dict(os.environ, {}, clear=True):
            resolver = SymLibTableVariableResolver()
            resolver._variables = {}  # Clear all variables
            uri = "${UNKNOWN_VAR}/some/path.kicad_sym"
            resolved = resolver.resolve(uri)
            assert resolved is None

    def test_resolve_multiple_variables(self):
        """Test resolving multiple variables in one URI."""
        project_dir = Path("/home/user/project")
        with patch.dict(os.environ, {"CUSTOM_VAR": "custom"}):
            resolver = SymLibTableVariableResolver(project_dir)
            resolver.add_variable("CUSTOM_VAR", "custom")
            uri = "${KIPRJMOD}/${CUSTOM_VAR}/lib.kicad_sym"
            resolved = resolver.resolve(uri)
            assert resolved == Path("/home/user/project/custom/lib.kicad_sym")

    def test_add_variable(self):
        """Test adding custom variables."""
        resolver = SymLibTableVariableResolver()
        resolver.add_variable("MY_LIBS", "/path/to/libs")

        uri = "${MY_LIBS}/symbols.kicad_sym"
        resolved = resolver.resolve(uri)
        assert resolved == Path("/path/to/libs/symbols.kicad_sym")

    def test_resolve_absolute_path(self):
        """Test resolving path without variables."""
        resolver = SymLibTableVariableResolver()
        uri = "/absolute/path/to/lib.kicad_sym"
        resolved = resolver.resolve(uri)
        assert resolved == Path("/absolute/path/to/lib.kicad_sym")


class TestSymLibTableParser:
    """Tests for sym-lib-table file parsing."""

    def test_parse_valid_table(self, tmp_path):
        """Test parsing a valid sym-lib-table file."""
        content = """(sym_lib_table
  (version 7)
  (lib (name "Device")(type "KiCad")(uri "${KICAD9_SYMBOL_DIR}/Device.kicad_sym")(options "")(descr "Standard devices"))
  (lib (name "EDA-MCP")(type "KiCad")(uri "${KIPRJMOD}/libraries/symbols/EDA-MCP.kicad_sym")(options "")(descr "Project components"))
)"""
        table_file = tmp_path / "sym-lib-table"
        table_file.write_text(content)

        table = SymLibTableParser.parse(table_file)

        assert table is not None
        assert table.version == 7
        assert len(table.entries) == 2

        assert table.entries[0].name == "Device"
        assert table.entries[0].uri == "${KICAD9_SYMBOL_DIR}/Device.kicad_sym"
        assert table.entries[0].description == "Standard devices"

        assert table.entries[1].name == "EDA-MCP"
        assert table.entries[1].uri == "${KIPRJMOD}/libraries/symbols/EDA-MCP.kicad_sym"

    def test_parse_nonexistent_file(self, tmp_path):
        """Test parsing nonexistent file returns None."""
        table = SymLibTableParser.parse(tmp_path / "nonexistent")
        assert table is None

    def test_parse_empty_table(self, tmp_path):
        """Test parsing empty sym-lib-table."""
        content = "(sym_lib_table\n  (version 7)\n)"
        table_file = tmp_path / "sym-lib-table"
        table_file.write_text(content)

        table = SymLibTableParser.parse(table_file)
        assert table is not None
        assert table.version == 7
        assert len(table.entries) == 0

    def test_parse_invalid_format(self, tmp_path):
        """Test parsing invalid format returns None."""
        content = "(fp_lib_table\n  (version 7)\n)"  # Wrong table type
        table_file = tmp_path / "sym-lib-table"
        table_file.write_text(content)

        table = SymLibTableParser.parse(table_file)
        assert table is None

    @pytest.mark.skipif(platform.system() != "Darwin", reason="macOS-specific test")
    def test_get_global_path_macos(self):
        """Test getting global sym-lib-table path on macOS."""
        expected_path = Path.home() / "Library" / "Preferences" / "kicad" / "9.0" / "sym-lib-table"

        # Only test if the file exists
        if expected_path.exists():
            path = SymLibTableParser.get_global_sym_lib_table_path()
            assert path is not None
            assert path.exists()

    def test_get_project_table_path(self, tmp_path):
        """Test getting project sym-lib-table path."""
        # Create project sym-lib-table
        table_file = tmp_path / "sym-lib-table"
        table_file.write_text("(sym_lib_table (version 7))")

        path = SymLibTableParser.get_project_sym_lib_table_path(tmp_path)
        assert path is not None
        assert path == table_file

    def test_get_project_table_path_missing(self, tmp_path):
        """Test getting project sym-lib-table path when missing."""
        path = SymLibTableParser.get_project_sym_lib_table_path(tmp_path)
        assert path is None


class TestSymLibTableIntegration:
    """Integration tests for sym-lib-table functionality."""

    def test_full_resolution_workflow(self, tmp_path):
        """Test complete workflow of parsing and resolving."""
        # Create a project structure
        project_dir = tmp_path / "myproject"
        project_dir.mkdir()

        libs_dir = project_dir / "libraries" / "symbols"
        libs_dir.mkdir(parents=True)

        # Create a dummy library file
        lib_file = libs_dir / "Custom.kicad_sym"
        lib_file.write_text("(kicad_symbol_lib)")

        # Create sym-lib-table
        table_content = f"""(sym_lib_table
  (version 7)
  (lib (name "Custom")(type "KiCad")(uri "${{KIPRJMOD}}/libraries/symbols/Custom.kicad_sym")(options "")(descr ""))
)"""
        table_file = project_dir / "sym-lib-table"
        table_file.write_text(table_content)

        # Parse and resolve
        table = SymLibTableParser.parse(table_file)
        resolver = SymLibTableVariableResolver(project_dir)

        assert table is not None
        assert len(table.entries) == 1

        resolved_path = resolver.resolve(table.entries[0].uri)
        assert resolved_path is not None
        assert resolved_path.exists()
        assert resolved_path == lib_file
