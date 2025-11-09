"""
Unit tests for edge-based sheet pin positioning.

Tests verify that sheet pins are correctly positioned, rotated, and justified
based on the edge parameter (right, bottom, left, top).
"""

import pytest

import kicad_sch_api as ksa


class TestSheetPinEdges:
    """Test suite for edge-based sheet pin placement."""

    @pytest.fixture
    def schematic_with_sheet(self):
        """Create a schematic with a hierarchical sheet."""
        sch = ksa.create_schematic("Sheet Pin Test")
        sheet_uuid = sch.add_sheet(
            name="TestSheet",
            filename="test.kicad_sch",
            position=(100, 100),
            size=(50, 40),  # Width=50, Height=40
        )
        return sch, sheet_uuid

    def test_right_edge_pin(self, schematic_with_sheet):
        """Test pin on right edge."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_RIGHT",
            pin_type="input",
            edge="right",
            position_along_edge=18.11,
        )

        # Verify pin was created
        assert pin_uuid is not None

        # Get pin data
        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 1

        pin = pins[0]
        assert pin["name"] == "PIN_RIGHT"
        assert pin["pin_type"] == "input"

        # Verify position (right edge: x = 100 + 50 = 150)
        assert pin["position"].x == 150
        assert pin["position"].y == 100 + 18.11

        # Verify rotation and justification
        assert pin["data"]["rotation"] == 0
        assert pin["data"]["justify"] == "right"

    def test_bottom_edge_pin(self, schematic_with_sheet):
        """Test pin on bottom edge."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_BOTTOM",
            pin_type="output",
            edge="bottom",
            position_along_edge=27,
        )

        # Verify pin was created
        assert pin_uuid is not None

        # Get pin data
        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 1

        pin = pins[0]
        assert pin["name"] == "PIN_BOTTOM"
        assert pin["pin_type"] == "output"

        # Verify position (bottom edge: y = 100 + 40 = 140)
        assert pin["position"].x == 100 + 27
        assert pin["position"].y == 140

        # Verify rotation and justification
        assert pin["data"]["rotation"] == 270
        assert pin["data"]["justify"] == "left"

    def test_left_edge_pin(self, schematic_with_sheet):
        """Test pin on left edge."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_LEFT",
            pin_type="input",
            edge="left",
            position_along_edge=21.89,
        )

        # Verify pin was created
        assert pin_uuid is not None

        # Get pin data
        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 1

        pin = pins[0]
        assert pin["name"] == "PIN_LEFT"
        assert pin["pin_type"] == "input"

        # Verify position (left edge: x = 100, y from bottom)
        assert pin["position"].x == 100
        assert pin["position"].y == 140 - 21.89

        # Verify rotation and justification
        assert pin["data"]["rotation"] == 180
        assert pin["data"]["justify"] == "left"

    def test_top_edge_pin(self, schematic_with_sheet):
        """Test pin on top edge."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_TOP",
            pin_type="output",
            edge="top",
            position_along_edge=27,
        )

        # Verify pin was created
        assert pin_uuid is not None

        # Get pin data
        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 1

        pin = pins[0]
        assert pin["name"] == "PIN_TOP"
        assert pin["pin_type"] == "output"

        # Verify position (top edge: y = 100)
        assert pin["position"].x == 100 + 27
        assert pin["position"].y == 100

        # Verify rotation and justification
        assert pin["data"]["rotation"] == 90
        assert pin["data"]["justify"] == "right"

    def test_all_four_edges(self, schematic_with_sheet):
        """Test adding pins to all four edges."""
        sch, sheet_uuid = schematic_with_sheet

        # Add pins to all edges
        pin_right = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_RIGHT",
            pin_type="input",
            edge="right",
            position_along_edge=18.11,
        )

        pin_bottom = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_BOTTOM",
            pin_type="output",
            edge="bottom",
            position_along_edge=27,
        )

        pin_left = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_LEFT",
            pin_type="input",
            edge="left",
            position_along_edge=21.89,
        )

        pin_top = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_TOP",
            pin_type="output",
            edge="top",
            position_along_edge=27,
        )

        # Verify all pins were created
        assert all([pin_right, pin_bottom, pin_left, pin_top])

        # Get all pins
        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 4

        # Verify names
        pin_names = [p["name"] for p in pins]
        assert "PIN_RIGHT" in pin_names
        assert "PIN_BOTTOM" in pin_names
        assert "PIN_LEFT" in pin_names
        assert "PIN_TOP" in pin_names

    def test_invalid_edge(self, schematic_with_sheet):
        """Test that invalid edge parameter is handled."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_INVALID",
            pin_type="input",
            edge="diagonal",  # Invalid edge
            position_along_edge=20,
        )

        # Should return None for invalid edge
        assert pin_uuid is None

    def test_invalid_pin_type(self, schematic_with_sheet):
        """Test that invalid pin type defaults to 'input'."""
        sch, sheet_uuid = schematic_with_sheet

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_INVALID_TYPE",
            pin_type="invalid_type",  # Invalid type
            edge="right",
            position_along_edge=20,
        )

        # Should still create pin with default type
        assert pin_uuid is not None

        pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
        assert len(pins) == 1
        # Type should be changed to 'input'
        assert pins[0]["pin_type"] == "input"

    def test_clockwise_rotation_pattern(self, schematic_with_sheet):
        """Verify clockwise rotation pattern: right(0°) → bottom(270°) → left(180°) → top(90°)."""
        sch, sheet_uuid = schematic_with_sheet

        edges_and_rotations = [
            ("right", 0),
            ("bottom", 270),
            ("left", 180),
            ("top", 90),
        ]

        for edge, expected_rotation in edges_and_rotations:
            pin_uuid = sch.add_sheet_pin(
                sheet_uuid=sheet_uuid,
                name=f"PIN_{edge.upper()}",
                pin_type="input",
                edge=edge,
                position_along_edge=20,
            )

            pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
            pin = [p for p in pins if p["name"] == f"PIN_{edge.upper()}"][0]

            assert (
                pin["data"]["rotation"] == expected_rotation
            ), f"Edge {edge} should have rotation {expected_rotation}"

    def test_justification_pattern(self, schematic_with_sheet):
        """Verify justification pattern: right→right, bottom→left, left→left, top→right."""
        sch, sheet_uuid = schematic_with_sheet

        edges_and_justifications = [
            ("right", "right"),
            ("bottom", "left"),
            ("left", "left"),
            ("top", "right"),
        ]

        for edge, expected_justify in edges_and_justifications:
            pin_uuid = sch.add_sheet_pin(
                sheet_uuid=sheet_uuid,
                name=f"PIN_{edge.upper()}",
                pin_type="input",
                edge=edge,
                position_along_edge=20,
            )

            pins = sch._sheet_manager.list_sheet_pins(sheet_uuid)
            pin = [p for p in pins if p["name"] == f"PIN_{edge.upper()}"][0]

            assert (
                pin["data"]["justify"] == expected_justify
            ), f"Edge {edge} should have justify {expected_justify}"

    def test_sheet_not_found(self):
        """Test adding pin to non-existent sheet."""
        sch = ksa.create_schematic("Test")

        pin_uuid = sch.add_sheet_pin(
            sheet_uuid="nonexistent-uuid",
            name="PIN_TEST",
            pin_type="input",
            edge="right",
            position_along_edge=20,
        )

        # Should return None when sheet not found
        assert pin_uuid is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
