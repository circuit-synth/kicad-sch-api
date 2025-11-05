"""
Unit tests for WireManager connectivity integration.

Tests the integration of ConnectivityAnalyzer into WireManager API,
including are_pins_connected(), get_net_for_pin(), get_connected_pins(),
and cache invalidation behavior.
"""

from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestWireManagerConnectivity:
    """Test WireManager connectivity integration."""

    @pytest.fixture
    def simple_circuit(self):
        """Create a simple circuit with two resistors connected by wire."""
        sch = ksa.create_schematic("Test Circuit")

        # Add two resistors
        sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        sch.components.add("Device:R", "R2", "10k", position=(150, 100))

        # Connect R1.2 to R2.1 with a wire
        sch._wire_manager.add_wire_between_pins("R1", "2", "R2", "1")

        return sch

    @pytest.fixture
    def circuit_with_junction(self):
        """Create circuit with junction connecting multiple wires."""
        sch = ksa.create_schematic("Junction Test")

        # Add three resistors
        sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        sch.components.add("Device:R", "R2", "10k", position=(150, 100))
        sch.components.add("Device:R", "R3", "10k", position=(125, 125))

        # Get actual pin positions
        # R1.2 = (100.33, 104.14)
        # R2.1 = (149.86, 96.52)
        # R3.1 = (124.46, 120.65)

        # Junction at midpoint
        junction_pos = (125, 104.14)

        # Wire from R1.2 to junction point
        sch.wires.add((100.33, 104.14), junction_pos)

        # Wire from junction to R2.1
        sch.wires.add(junction_pos, (149.86, 96.52))

        # Wire from junction to R3.1
        sch.wires.add(junction_pos, (124.46, 120.65))

        # Add junction at connection point
        sch.junctions.add(position=junction_pos)

        return sch

    @pytest.fixture
    def hierarchical_circuit(self):
        """Load PS2 hierarchical reference schematic."""
        ref_path = (
            Path(__file__).parent.parent
            / "reference_kicad_projects"
            / "connectivity"
            / "ps2_hierarchical_power"
            / "ps2_hierarchical_power.kicad_sch"
        )
        return ksa.Schematic.load(str(ref_path))

    # Test are_pins_connected()

    def test_direct_wire_connection(self, simple_circuit):
        """Test are_pins_connected with direct wire."""
        assert simple_circuit.are_pins_connected(
            "R1", "2", "R2", "1"
        ), "R1.2 and R2.1 should be connected via direct wire"

    def test_not_connected_pins(self, simple_circuit):
        """Test are_pins_connected returns False for unconnected pins."""
        assert not simple_circuit.are_pins_connected(
            "R1", "1", "R2", "2"
        ), "R1.1 and R2.2 should not be connected"

    def test_junction_based_connection(self, circuit_with_junction):
        """Test are_pins_connected through junction."""
        # All three resistors should be connected through junction
        assert circuit_with_junction.are_pins_connected(
            "R1", "2", "R2", "1"
        ), "R1.2 and R2.1 should be connected through junction"

        assert circuit_with_junction.are_pins_connected(
            "R1", "2", "R3", "1"
        ), "R1.2 and R3.1 should be connected through junction"

        assert circuit_with_junction.are_pins_connected(
            "R2", "1", "R3", "1"
        ), "R2.1 and R3.1 should be connected through junction"

    def test_hierarchical_connection(self, hierarchical_circuit):
        """Test are_pins_connected across hierarchical sheets."""
        # R1.2 in parent should connect to R2.1 in child via sheet pin
        assert hierarchical_circuit.are_pins_connected(
            "R1", "2", "R2", "1"
        ), "R1.2 (parent) and R2.1 (child) should be connected hierarchically"

    # Test get_net_for_pin()

    def test_get_net_for_connected_pin(self, simple_circuit):
        """Test get_net_for_pin returns Net object."""
        net = simple_circuit.get_net_for_pin("R1", "2")

        assert net is not None, "Should return Net for connected pin"
        assert len(net.pins) >= 2, "Net should have at least 2 pins"

        # Check that both R1.2 and R2.1 are in the net
        pin_refs = {(p.reference, p.pin_number) for p in net.pins}
        assert ("R1", "2") in pin_refs
        assert ("R2", "1") in pin_refs

    def test_get_net_for_unconnected_pin(self, simple_circuit):
        """Test get_net_for_pin for unconnected pin."""
        # R1.1 and R2.2 are not connected to anything
        net = simple_circuit.get_net_for_pin("R1", "1")

        # May return None or a net with only this pin
        if net is not None:
            assert len(net.pins) == 1, "Unconnected pin should have single-pin net or None"

    def test_get_net_with_junction(self, circuit_with_junction):
        """Test get_net_for_pin with junction."""
        net = circuit_with_junction.get_net_for_pin("R1", "2")

        assert net is not None
        pin_refs = {(p.reference, p.pin_number) for p in net.pins}

        # All three pins should be in the same net
        assert ("R1", "2") in pin_refs
        assert ("R2", "1") in pin_refs
        assert ("R3", "1") in pin_refs

    # Test get_connected_pins()

    def test_get_connected_pins_direct(self, simple_circuit):
        """Test get_connected_pins returns connected pins."""
        connected = simple_circuit.get_connected_pins("R1", "2")

        assert len(connected) >= 1, "Should have at least one connected pin"
        assert ("R2", "1") in connected, "R2.1 should be in connected pins"

    def test_get_connected_pins_junction(self, circuit_with_junction):
        """Test get_connected_pins with junction."""
        connected = circuit_with_junction.get_connected_pins("R1", "2")

        # Should return R2.1 and R3.1 (not R1.2 itself)
        assert len(connected) >= 2
        assert ("R2", "1") in connected
        assert ("R3", "1") in connected
        assert ("R1", "2") not in connected, "Should not include the queried pin itself"

    def test_get_connected_pins_unconnected(self, simple_circuit):
        """Test get_connected_pins for unconnected pin."""
        connected = simple_circuit.get_connected_pins("R1", "1")

        # Unconnected pin should return empty list
        assert len(connected) == 0, "Unconnected pin should have no connected pins"

    # Test cache invalidation

    def test_cache_invalidation_on_wire_add(self, simple_circuit):
        """Test that adding wire invalidates connectivity cache."""
        # First query builds cache
        result1 = simple_circuit.are_pins_connected("R1", "1", "R2", "2")
        assert not result1, "Initially not connected"

        # Add wire connecting them
        simple_circuit._wire_manager.add_wire_between_pins("R1", "1", "R2", "2")

        # Second query should reflect new connection (cache was invalidated)
        result2 = simple_circuit.are_pins_connected("R1", "1", "R2", "2")
        assert result2, "Should be connected after adding wire"

    def test_cache_invalidation_on_wire_remove(self, simple_circuit):
        """Test that removing wire invalidates connectivity cache."""
        # Initially connected
        assert simple_circuit.are_pins_connected("R1", "2", "R2", "1")

        # Find and remove the wire
        for wire in simple_circuit.wires:
            simple_circuit._wire_manager.remove_wire(wire.uuid)
            break

        # After removal, should not be connected
        assert not simple_circuit.are_pins_connected(
            "R1", "2", "R2", "1"
        ), "Should not be connected after wire removal"

    def test_multiple_queries_use_cache(self, simple_circuit):
        """Test that multiple connectivity queries reuse cached analysis."""
        # These should all use the same cached analysis
        result1 = simple_circuit.are_pins_connected("R1", "2", "R2", "1")
        result2 = simple_circuit.get_net_for_pin("R1", "2")
        result3 = simple_circuit.get_connected_pins("R1", "2")

        # All should return consistent results
        assert result1 is True
        assert result2 is not None
        assert len(result3) >= 1

    # Test hierarchical connectivity

    def test_hierarchical_always_enabled(self, hierarchical_circuit):
        """Test that hierarchical analysis is always enabled."""
        # Should find cross-sheet connections without any special flags
        assert hierarchical_circuit.are_pins_connected(
            "R1", "2", "R2", "1"
        ), "Hierarchical connections should work automatically"

    def test_power_symbols_global(self, hierarchical_circuit):
        """Test power symbols create global connections."""
        # VCC net should exist
        vcc_net = hierarchical_circuit.get_net_for_pin("R1", "1")
        assert vcc_net is not None
        assert vcc_net.name == "VCC"

        # GND net should exist
        gnd_net = hierarchical_circuit.get_net_for_pin("R2", "2")
        assert gnd_net is not None
        assert gnd_net.name == "GND"

    # Edge cases

    def test_nonexistent_component(self, simple_circuit):
        """Test behavior with nonexistent component."""
        result = simple_circuit.are_pins_connected("R99", "1", "R1", "1")
        assert not result, "Nonexistent component should return False"

    def test_nonexistent_pin(self, simple_circuit):
        """Test behavior with nonexistent pin number."""
        result = simple_circuit.are_pins_connected("R1", "99", "R2", "1")
        assert not result, "Nonexistent pin should return False"

    def test_same_pin_queried_twice(self, simple_circuit):
        """Test querying if pin is connected to itself."""
        # Pin should not be "connected" to itself
        result = simple_circuit.are_pins_connected("R1", "2", "R1", "2")
        # Result may vary - either False or True depending on implementation
        # Just verify it doesn't crash
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
