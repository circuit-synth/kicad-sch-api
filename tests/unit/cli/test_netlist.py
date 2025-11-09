"""Unit tests for netlist export functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kicad_sch_api.cli.netlist import _get_extension_for_format, export_netlist


class TestNetlistExport:
    """Test netlist export functions."""

    def test_export_netlist_default_format(self, tmp_path):
        """Test netlist export with default format."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch("kicad_sch_api.cli.netlist.KiCadExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            result = export_netlist(sch_file)

            # Check output path
            assert result == sch_file.with_suffix(".net")

            # Check executor was called correctly
            mock_executor.run.assert_called_once()
            args = mock_executor.run.call_args[0][0]
            assert args == [
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadsexpr",
                "--output",
                str(sch_file.with_suffix(".net")),
                str(sch_file),
            ]

    def test_export_netlist_spice_format(self, tmp_path):
        """Test netlist export with SPICE format."""
        sch_file = tmp_path / "circuit.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch("kicad_sch_api.cli.netlist.KiCadExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            result = export_netlist(sch_file, format="spice")

            # Check output path has correct extension
            assert result == sch_file.with_suffix(".cir")

            # Check format argument
            args = mock_executor.run.call_args[0][0]
            assert "--format" in args
            assert "spice" in args

    def test_export_netlist_custom_output_path(self, tmp_path):
        """Test netlist export with custom output path."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")
        output_file = tmp_path / "custom_netlist.net"

        with patch("kicad_sch_api.cli.netlist.KiCadExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            result = export_netlist(sch_file, output_path=output_file)

            assert result == output_file

            args = mock_executor.run.call_args[0][0]
            assert str(output_file) in args

    def test_export_netlist_file_not_found(self, tmp_path):
        """Test netlist export with non-existent schematic file."""
        sch_file = tmp_path / "nonexistent.kicad_sch"

        with pytest.raises(FileNotFoundError):
            export_netlist(sch_file)

    def test_export_netlist_custom_executor(self, tmp_path):
        """Test netlist export with custom executor."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        custom_executor = Mock()

        export_netlist(sch_file, executor=custom_executor)

        # Custom executor should be used
        custom_executor.run.assert_called_once()

    def test_get_extension_for_format(self):
        """Test extension mapping for different formats."""
        assert _get_extension_for_format("kicadsexpr") == ".net"
        assert _get_extension_for_format("kicadxml") == ".xml"
        assert _get_extension_for_format("spice") == ".cir"
        assert _get_extension_for_format("spicemodel") == ".cir"
        assert _get_extension_for_format("cadstar") == ".frp"
        assert _get_extension_for_format("orcadpcb2") == ".net"
        assert _get_extension_for_format("pads") == ".asc"
        assert _get_extension_for_format("allegro") == ".alg"

    @pytest.mark.parametrize(
        "format",
        [
            "kicadsexpr",
            "kicadxml",
            "cadstar",
            "orcadpcb2",
            "spice",
            "spicemodel",
            "pads",
            "allegro",
        ],
    )
    def test_all_netlist_formats(self, format, tmp_path):
        """Test all supported netlist formats."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch("kicad_sch_api.cli.netlist.KiCadExecutor") as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_netlist(sch_file, format=format)

            args = mock_executor.run.call_args[0][0]
            assert "--format" in args
            assert format in args
