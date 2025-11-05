"""
Unit tests for connectivity analysis - PS2: Hierarchical power symbols.

Tests multi-sheet hierarchical connectivity with power symbols and sheet pins.
"""

import pytest
from pathlib import Path

import kicad_sch_api as ksa
from kicad_sch_api.core.connectivity import ConnectivityAnalyzer


class TestConnectivityPS2Hierarchical:
    """Test hierarchical connectivity across parent and child sheets."""

    @pytest.fixture
    def reference_schematic(self):
        """Load PS2 reference schematic with hierarchical child sheet."""
        ref_path = Path(__file__).parent.parent / "reference_kicad_projects" / "connectivity" / "ps2_hierarchical_power" / "ps2_hierarchical_power.kicad_sch"
        return ksa.Schematic.load(str(ref_path))

    @pytest.fixture
    def analyzer(self, reference_schematic):
        """Create and run connectivity analyzer with hierarchical support."""
        analyzer = ConnectivityAnalyzer(tolerance=0.1)
        analyzer.analyze(reference_schematic, hierarchical=True)
        return analyzer

    def test_three_nets_found(self, analyzer):
        """Should have 3 nets (VCC, DATA, GND)."""
        assert len(analyzer.nets) == 3, "Expected exactly 3 nets"

    def test_vcc_net_global_power_symbol(self, analyzer):
        """VCC power symbol creates global net in parent sheet."""
        vcc_net = analyzer.get_net_for_pin('R1', '1')
        assert vcc_net is not None, "VCC net should exist"
        assert vcc_net.name == 'VCC', "VCC net should be named 'VCC'"

        pins = {(p.reference, p.pin_number) for p in vcc_net.pins}
        assert ('R1', '1') in pins, "VCC should connect R1.1"
        assert any(ref.startswith('#PWR') for ref, _ in pins), "VCC should have power symbol"

    def test_gnd_net_global_power_symbol(self, analyzer):
        """GND power symbol creates global net in child sheet."""
        gnd_net = analyzer.get_net_for_pin('R2', '2')
        assert gnd_net is not None, "GND net should exist"
        assert gnd_net.name == 'GND', "GND net should be named 'GND'"

        pins = {(p.reference, p.pin_number) for p in gnd_net.pins}
        assert ('R2', '2') in pins, "GND should connect R2.2"
        assert any(ref.startswith('#PWR') for ref, _ in pins), "GND should have power symbol"

    def test_data_net_hierarchical_connection(self, analyzer):
        """DATA net connects parent and child via sheet pin and hierarchical label."""
        data_net = analyzer.get_net_for_pin('R1', '2')
        assert data_net is not None, "DATA net should exist"
        assert data_net.name == 'DATA', "DATA net should be named 'DATA'"

        pins = {(p.reference, p.pin_number) for p in data_net.pins}
        assert ('R1', '2') in pins, "DATA should connect R1.2 (parent)"
        assert ('R2', '1') in pins, "DATA should connect R2.1 (child)"

    def test_hierarchical_connection_merges_nets(self, analyzer):
        """Sheet pin in parent connects to hierarchical label in child."""
        # R1.2 in parent should be connected to R2.1 in child via DATA sheet pin
        assert analyzer.are_connected('R1', '2', 'R2', '1'), \
            "R1.2 (parent) and R2.1 (child) should be connected via hierarchical DATA"

    def test_cross_sheet_power_symbols_not_redundant(self, analyzer):
        """Power symbols create single global net across all sheets."""
        # All GND power symbols should be on one net
        # All VCC power symbols should be on one net
        # Even though they're on different sheets

        vcc_nets = [analyzer.get_net_for_pin(ref, '1')
                   for ref in ['R1'] if analyzer.get_net_for_pin(ref, '1')]
        vcc_net_names = {net.name for net in vcc_nets if net}
        assert len(vcc_net_names) == 1, "All VCC power symbols should be on ONE global net"

        gnd_nets = [analyzer.get_net_for_pin('R2', '2')]
        gnd_net_names = {net.name for net in gnd_nets if net}
        assert len(gnd_net_names) == 1, "All GND power symbols should be on ONE global net"

    def test_separate_nets_not_connected(self, analyzer):
        """Different nets should not be connected."""
        # VCC and DATA should be separate
        assert not analyzer.are_connected('R1', '1', 'R1', '2'), \
            "R1.1 (VCC) and R1.2 (DATA) should NOT be connected"

        # DATA and GND should be separate
        assert not analyzer.are_connected('R2', '1', 'R2', '2'), \
            "R2.1 (DATA) and R2.2 (GND) should NOT be connected"

        # VCC and GND should be separate (even though both are power symbols)
        assert not analyzer.are_connected('R1', '1', 'R2', '2'), \
            "R1.1 (VCC) and R2.2 (GND) should NOT be connected"

    def test_get_connected_pins_cross_sheet(self, analyzer):
        """get_connected_pins should work across hierarchical sheets."""
        # R1.2 connects to R2.1 via hierarchical connection
        connected = analyzer.get_connected_pins('R1', '2')
        assert ('R2', '1') in connected, "R1.2 should be connected to R2.1"

        # Reverse direction
        connected = analyzer.get_connected_pins('R2', '1')
        assert ('R1', '2') in connected, "R2.1 should be connected to R1.2"

    def test_hierarchical_labels_counted(self, reference_schematic):
        """Child schematic should have hierarchical labels."""
        # Load child manually to verify structure
        parent_path = Path(reference_schematic.file_path)
        child_path = parent_path.parent / "child_circuit.kicad_sch"

        child_sch = ksa.Schematic.load(str(child_path))
        hier_labels = list(child_sch.hierarchical_labels)

        assert len(hier_labels) > 0, "Child should have hierarchical labels"
        assert any(label.text == 'DATA' for label in hier_labels), \
            "Child should have DATA hierarchical label"

    def test_sheet_pins_in_parent(self, reference_schematic):
        """Parent schematic should have hierarchical sheet with pins."""
        sheets = reference_schematic._data.get('sheets', [])
        assert len(sheets) > 0, "Parent should have hierarchical sheets"

        sheet = sheets[0]
        pins = sheet.get('pins', [])
        assert len(pins) > 0, "Hierarchical sheet should have pins"

        pin_names = [pin.get('name') for pin in pins]
        assert 'DATA' in pin_names, "Sheet should have DATA pin"


class TestConnectivityPS2WithoutHierarchical:
    """Test that hierarchical analysis can be disabled."""

    def test_analyze_parent_only(self):
        """Analyze parent sheet without loading children."""
        ref_path = Path(__file__).parent.parent / "reference_kicad_projects" / "connectivity" / "ps2_hierarchical_power" / "ps2_hierarchical_power.kicad_sch"
        parent = ksa.Schematic.load(str(ref_path))

        analyzer = ConnectivityAnalyzer(tolerance=0.1)
        nets = analyzer.analyze(parent, hierarchical=False)

        # Should only have nets from parent sheet
        # Parent has R1 with VCC, so should have 2 nets (VCC, DATA)
        # (no GND because that's only in child)
        assert len(nets) == 2, "Parent-only analysis should have 2 nets"

        # R2 from child should not be in connectivity
        r2_net = analyzer.get_net_for_pin('R2', '1')
        assert r2_net is None, "R2 (from child) should not be analyzed when hierarchical=False"
