"""
Integration tests for KiCad CLI wrappers.

These tests require either:
1. Local kicad-cli installation (KiCad 8.0+)
2. Docker installed

Tests will be skipped if neither is available.
"""

from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.cli import get_executor_info
from kicad_sch_api.cli.bom import export_bom
from kicad_sch_api.cli.erc import run_erc
from kicad_sch_api.cli.netlist import export_netlist

# Check if KiCad CLI is available (local or Docker)
executor_info = get_executor_info()
kicad_available = executor_info.local_available or executor_info.docker_available

skip_if_no_kicad = pytest.mark.skipif(
    not kicad_available, reason="KiCad CLI not available (neither local nor Docker)"
)


@skip_if_no_kicad
class TestCLIIntegration:
    """Integration tests for CLI wrappers."""

    @pytest.fixture
    def simple_schematic(self, tmp_path):
        """Create a simple test schematic."""
        sch = ksa.create_schematic("Test Circuit")

        # Add components
        sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        sch.components.add("Device:R", reference="R2", value="10k", position=(150, 100))
        sch.components.add("Device:C", reference="C1", value="100nF", position=(125, 150))

        # Add wire
        sch.add_wire(start=(100, 110), end=(150, 110))

        # Save
        sch_path = tmp_path / "test.kicad_sch"
        sch.save(sch_path)

        return sch_path

    def test_netlist_export_kicadsexpr(self, simple_schematic, tmp_path):
        """Test exporting KiCad S-expression netlist."""
        output = tmp_path / "test.net"

        result = export_netlist(simple_schematic, output_path=output, format="kicadsexpr")

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

        # Check netlist contains component references
        content = output.read_text()
        assert "R1" in content or "R2" in content

    def test_bom_export_default(self, simple_schematic, tmp_path):
        """Test exporting BOM with default options."""
        output = tmp_path / "test.csv"

        result = export_bom(
            simple_schematic,
            output_path=output,
        )

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0

        # Check BOM contains components
        content = output.read_text()
        assert "R1" in content or "R2" in content or "C1" in content

    def test_bom_export_with_grouping(self, simple_schematic, tmp_path):
        """Test exporting BOM with grouping."""
        output = tmp_path / "test_grouped.csv"

        result = export_bom(
            simple_schematic,
            output_path=output,
            fields=["Reference", "Value", "Footprint"],
            group_by=["Value"],
        )

        assert result == output
        assert output.exists()

        # Check BOM format
        content = output.read_text()
        lines = content.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one row

    def test_erc_validation(self, simple_schematic, tmp_path):
        """Test ERC validation."""
        report = run_erc(
            simple_schematic,
            format="json",
        )

        # Report should be generated
        assert report is not None
        assert report.schematic_path == simple_schematic

        # May have violations (unconnected pins, etc.)
        # Just check the report structure works
        assert isinstance(report.error_count, int)
        assert isinstance(report.warning_count, int)
        assert report.error_count >= 0
        assert report.warning_count >= 0

    def test_schematic_class_export_netlist(self, tmp_path):
        """Test Schematic class export_netlist method."""
        # Create schematic
        sch = ksa.create_schematic("Integration Test")
        sch.components.add("Device:R", reference="R1", value="1k", position=(100, 100))

        sch_path = tmp_path / "test_sch.kicad_sch"
        sch.save(sch_path)

        # Export netlist using Schematic method
        netlist_path = sch.export_netlist(format="kicadsexpr")

        assert netlist_path.exists()
        assert netlist_path.suffix == ".net"

    def test_schematic_class_export_bom(self, tmp_path):
        """Test Schematic class export_bom method."""
        # Create schematic
        sch = ksa.create_schematic("Integration Test")
        sch.components.add("Device:R", reference="R1", value="1k", position=(100, 100))
        sch.components.add("Device:C", reference="C1", value="10uF", position=(150, 100))

        sch_path = tmp_path / "test_sch.kicad_sch"
        sch.save(sch_path)

        # Export BOM using Schematic method
        bom_path = sch.export_bom()

        assert bom_path.exists()
        assert bom_path.suffix == ".csv"

        # Check content
        content = bom_path.read_text()
        assert "R1" in content or "C1" in content

    def test_schematic_class_run_erc(self, tmp_path):
        """Test Schematic class run_erc method."""
        # Create schematic
        sch = ksa.create_schematic("Integration Test")
        sch.components.add("Device:R", reference="R1", value="1k", position=(100, 100))

        sch_path = tmp_path / "test_sch.kicad_sch"
        sch.save(sch_path)

        # Run ERC using Schematic method
        report = sch.run_erc()

        assert report is not None
        assert isinstance(report.error_count, int)
        assert isinstance(report.warning_count, int)

    def test_multiple_netlist_formats(self, simple_schematic, tmp_path):
        """Test exporting netlists in different formats."""
        formats_to_test = ["kicadsexpr", "kicadxml"]

        for fmt in formats_to_test:
            output = tmp_path / f"test_{fmt}.net"

            result = export_netlist(simple_schematic, output_path=output, format=fmt)

            assert result == output
            assert output.exists(), f"Failed to export {fmt} format"
            assert output.stat().st_size > 0, f"{fmt} file is empty"


@skip_if_no_kicad
class TestExecutorModes:
    """Test different executor modes."""

    def test_executor_info(self):
        """Test getting executor information."""
        info = get_executor_info()

        assert hasattr(info, "local_available")
        assert hasattr(info, "docker_available")
        assert hasattr(info, "active_mode")

        # At least one should be available if tests are running
        assert info.local_available or info.docker_available

    def test_local_mode_if_available(self, tmp_path):
        """Test forcing local mode if available."""
        if not executor_info.local_available:
            pytest.skip("Local kicad-cli not available")

        # Create simple schematic
        sch = ksa.create_schematic("Local Mode Test")
        sch.components.add("Device:R", reference="R1", value="1k", position=(100, 100))

        sch_path = tmp_path / "test.kicad_sch"
        sch.save(sch_path)

        # Force local mode
        from kicad_sch_api.cli.base import KiCadExecutor

        executor = KiCadExecutor(mode="local", verbose=True)
        result = export_netlist(sch_path, executor=executor)

        assert result.exists()

    def test_docker_mode_if_available(self, tmp_path):
        """Test forcing Docker mode if available."""
        if not executor_info.docker_available:
            pytest.skip("Docker not available")

        # Create simple schematic
        sch = ksa.create_schematic("Docker Mode Test")
        sch.components.add("Device:R", reference="R1", value="1k", position=(100, 100))

        sch_path = tmp_path / "test.kicad_sch"
        sch.save(sch_path)

        # Force Docker mode
        from kicad_sch_api.cli.base import KiCadExecutor

        executor = KiCadExecutor(mode="docker", verbose=True)
        result = export_netlist(sch_path, executor=executor)

        assert result.exists()
