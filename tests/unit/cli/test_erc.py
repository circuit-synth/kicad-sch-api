"""Unit tests for ERC functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kicad_sch_api.cli.erc import ErcReport, ErcViolation, run_erc


class TestERCExecution:
    """Test ERC execution functions."""

    def test_run_erc_default_options(self, tmp_path):
        """Test ERC with default options."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.erc.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            # Mock the output file
            erc_output = tmp_path / "test_erc.json"
            erc_output.write_text(json.dumps({"violations": []}))

            with patch('pathlib.Path.read_text', return_value='{"violations": []}'):
                report = run_erc(sch_file)

            assert isinstance(report, ErcReport)
            assert report.error_count == 0
            assert report.warning_count == 0

    def test_run_erc_json_format(self, tmp_path):
        """Test ERC with JSON format."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.erc.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            json_content = json.dumps({
                "violations": [
                    {
                        "severity": "error",
                        "type": "pin_not_connected",
                        "description": "Pin not connected",
                        "sheet": "/"
                    }
                ]
            })

            with patch('pathlib.Path.read_text', return_value=json_content):
                report = run_erc(sch_file, format="json")

            assert report.error_count == 1
            assert len(report.violations) == 1
            assert report.violations[0].severity == "error"

    def test_run_erc_severity_options(self, tmp_path):
        """Test ERC with different severity options."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.erc.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            with patch('pathlib.Path.read_text', return_value='{"violations": []}'):
                run_erc(sch_file, severity="error")

            args = mock_executor.run.call_args[0][0]
            assert "--severity-error" in args

    def test_run_erc_units(self, tmp_path):
        """Test ERC with different units."""
        sch_file = tmp_path / "test.kicad_sch"
        sch_file.write_text("(kicad_sch (version 20230121))")

        with patch('kicad_sch_api.cli.erc.KiCadExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor_class.return_value = mock_executor

            with patch('pathlib.Path.read_text', return_value='{"violations": []}'):
                run_erc(sch_file, units="in")

            args = mock_executor.run.call_args[0][0]
            assert "--units" in args
            assert "in" in args

    def test_run_erc_file_not_found(self, tmp_path):
        """Test ERC with non-existent schematic file."""
        sch_file = tmp_path / "nonexistent.kicad_sch"

        with pytest.raises(FileNotFoundError):
            run_erc(sch_file)


class TestErcReport:
    """Test ErcReport class."""

    def test_erc_report_has_errors(self):
        """Test has_errors method."""
        report = ErcReport(
            violations=[],
            error_count=2,
            warning_count=1,
            exclusion_count=0,
            schematic_path=Path("test.kicad_sch"),
            raw_output="",
        )
        assert report.has_errors() is True

    def test_erc_report_no_errors(self):
        """Test has_errors when no errors."""
        report = ErcReport(
            violations=[],
            error_count=0,
            warning_count=1,
            exclusion_count=0,
            schematic_path=Path("test.kicad_sch"),
            raw_output="",
        )
        assert report.has_errors() is False

    def test_erc_report_get_errors(self):
        """Test get_errors method."""
        violations = [
            ErcViolation("error", "type1", "Error 1", "/"),
            ErcViolation("warning", "type2", "Warning 1", "/"),
            ErcViolation("error", "type3", "Error 2", "/"),
        ]

        report = ErcReport(
            violations=violations,
            error_count=2,
            warning_count=1,
            exclusion_count=0,
            schematic_path=Path("test.kicad_sch"),
            raw_output="",
        )

        errors = report.get_errors()
        assert len(errors) == 2
        assert all(e.severity == "error" for e in errors)

    def test_erc_report_get_warnings(self):
        """Test get_warnings method."""
        violations = [
            ErcViolation("error", "type1", "Error 1", "/"),
            ErcViolation("warning", "type2", "Warning 1", "/"),
            ErcViolation("warning", "type3", "Warning 2", "/"),
        ]

        report = ErcReport(
            violations=violations,
            error_count=1,
            warning_count=2,
            exclusion_count=0,
            schematic_path=Path("test.kicad_sch"),
            raw_output="",
        )

        warnings = report.get_warnings()
        assert len(warnings) == 2
        assert all(w.severity == "warning" for w in warnings)
