"""Unit tests for BOM export functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kicad_sch_api.cli.bom import export_bom


class TestBOMExport:
    """Test BOM export functions."""

    def test_export_bom_default_options(self, tmp_path):
        """Test BOM export with default options."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            result = export_bom(sch_file)

            # Check output path
            assert result == sch_file.with_suffix(".csv")

            # Check executor was called
            mock_executor.run.assert_called_once()
            args = mock_executor.run.call_args[0][0]
            assert "sch" in args
            assert "export" in args
            assert "bom" in args

    def test_export_bom_custom_fields(self, tmp_path):
        """Test BOM export with custom fields."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_bom(
                sch_file,
                fields=['Reference', 'Value', 'Footprint', 'MPN'],
                labels=['Refs', 'Value', 'Footprint', 'Part Number'],
            )

            args = mock_executor.run.call_args[0][0]
            assert "--fields" in args
            assert "Reference,Value,Footprint,MPN" in args
            assert "--labels" in args
            assert "Refs,Value,Footprint,Part Number" in args

    def test_export_bom_grouping(self, tmp_path):
        """Test BOM export with grouping."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_bom(
                sch_file,
                group_by=['Value', 'Footprint'],
            )

            args = mock_executor.run.call_args[0][0]
            assert "--group-by" in args
            assert "Value,Footprint" in args

    def test_export_bom_exclude_dnp(self, tmp_path):
        """Test BOM export with DNP exclusion."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_bom(sch_file, exclude_dnp=True)

            args = mock_executor.run.call_args[0][0]
            assert "--exclude-dnp" in args

    def test_export_bom_sort_options(self, tmp_path):
        """Test BOM export with sorting options."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_bom(
                sch_file,
                sort_field='Value',
                sort_asc=True,
            )

            args = mock_executor.run.call_args[0][0]
            assert "--sort-field" in args
            assert "Value" in args
            assert "--sort-asc" in args

    def test_export_bom_delimiters(self, tmp_path):
        """Test BOM export with custom delimiters."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            export_bom(
                sch_file,
                field_delimiter=';',
                string_delimiter="'",
                ref_delimiter=',',
                ref_range_delimiter='-',
            )

            args = mock_executor.run.call_args[0][0]
            assert "--field-delimiter" in args
            assert ";" in args
            assert "--string-delimiter" in args
            assert "--ref-delimiter" in args
            assert "--ref-range-delimiter" in args

    def test_export_bom_file_not_found(self, tmp_path):
        """Test BOM export with non-existent schematic file."""
        sch_file = tmp_path / "nonexistent.kicad_sch"

        with pytest.raises(FileNotFoundError):
            export_bom(sch_file)

    def test_export_bom_custom_output_path(self, tmp_path):
        """Test BOM export with custom output path."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")
        output_file = tmp_path / "custom_bom.csv"

        with patch('kicad_sch_api.cli.bom.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            result = export_bom(sch_file, output_path=output_file)

            assert result == output_file
            args = mock_executor.run.call_args[0][0]
            assert str(output_file) in args
