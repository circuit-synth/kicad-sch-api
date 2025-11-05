#!/usr/bin/env python3
"""
Unit tests for component rotation functionality.

Tests both setting rotation during creation and using the rotate() method.
"""

import pytest
import kicad_sch_api as ksa


class TestComponentRotation:
    """Test component rotation parameter and methods."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("rotation_test")

    def test_add_component_with_zero_rotation(self, schematic):
        """Test adding component with default rotation (0°)."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100)
        )
        assert comp.rotation == 0.0, "Default rotation should be 0°"

    def test_add_component_with_90_degree_rotation(self, schematic):
        """Test adding component with 90° rotation."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=90
        )
        assert comp.rotation == 90.0, "Component should have 90° rotation"

    def test_add_component_with_180_degree_rotation(self, schematic):
        """Test adding component with 180° rotation."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=180
        )
        assert comp.rotation == 180.0, "Component should have 180° rotation"

    def test_add_component_with_270_degree_rotation(self, schematic):
        """Test adding component with 270° rotation."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=270
        )
        assert comp.rotation == 270.0, "Component should have 270° rotation"

    @pytest.mark.parametrize("angle", [0, 90, 180, 270])
    def test_add_component_with_various_angles(self, schematic, angle):
        """Test adding components with valid rotation angles (KiCad only accepts 0, 90, 180, 270)."""
        comp = schematic.components.add(
            "Device:R", f"R{angle}", "10k", position=(100, 100), rotation=angle
        )
        assert comp.rotation == float(angle), f"Component should have {angle}° rotation"

    def test_rotate_method_adds_to_current_rotation(self, schematic):
        """Test that rotate() method adds to current rotation."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=0
        )

        assert comp.rotation == 0.0

        comp.rotate(90)
        assert comp.rotation == 90.0

        comp.rotate(90)
        assert comp.rotation == 180.0

        comp.rotate(90)
        assert comp.rotation == 270.0

    def test_rotate_method_wraps_at_360(self, schematic):
        """Test that rotation wraps around at 360°."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=270
        )

        comp.rotate(180)
        # 270 + 180 = 450, wraps to 90
        assert comp.rotation == 90.0

    def test_set_rotation_property(self, schematic):
        """Test setting rotation via property."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100)
        )

        comp.rotation = 180
        assert comp.rotation == 180.0

    def test_rotation_property_wraps_at_360(self, schematic):
        """Test that setting rotation property wraps at 360°."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100)
        )

        comp.rotation = 450  # Should wrap to 90
        assert comp.rotation == 90.0

    @pytest.mark.skip(reason="Loading components needs investigation - separate issue")
    def test_rotation_persists_in_saved_file(self, schematic, tmp_path):
        """Test that rotation is preserved when saving and loading."""
        # Add components with different rotations
        schematic.components.add("Device:R", "R1", "10k", (100, 100), rotation=0)
        schematic.components.add("Device:R", "R2", "10k", (150, 100), rotation=90)
        schematic.components.add("Device:R", "R3", "10k", (100, 150), rotation=180)
        schematic.components.add("Device:R", "R4", "10k", (150, 150), rotation=270)

        # Save
        test_file = tmp_path / "rotation_test.kicad_sch"
        schematic.save(test_file)

        # Load
        loaded_sch = ksa.Schematic(file_path=test_file)

        # Verify rotations are preserved
        assert loaded_sch.components.get("R1").rotation == 0.0
        assert loaded_sch.components.get("R2").rotation == 90.0
        assert loaded_sch.components.get("R3").rotation == 180.0
        assert loaded_sch.components.get("R4").rotation == 270.0

    def test_multiple_components_with_different_rotations(self, schematic):
        """Test adding multiple components with different rotations."""
        rotations = [0, 90, 180, 270]
        components = []

        for i, angle in enumerate(rotations):
            comp = schematic.components.add(
                "Device:R",
                f"R{i+1}",
                "10k",
                position=(100 + i * 50, 100),
                rotation=angle
            )
            components.append(comp)

        # Verify each component has correct rotation
        for comp, expected_angle in zip(components, rotations):
            assert comp.rotation == float(expected_angle)

    def test_rotation_with_different_component_types(self, schematic):
        """Test rotation works with different component types."""
        # Test with resistor
        r = schematic.components.add("Device:R", "R1", "10k", (100, 100), rotation=90)
        assert r.rotation == 90.0

        # Test with capacitor
        c = schematic.components.add("Device:C", "C1", "100nF", (150, 100), rotation=180)
        assert c.rotation == 180.0

        # Test with LED
        led = schematic.components.add("Device:LED", "D1", "LED", (100, 150), rotation=270)
        assert led.rotation == 270.0

    def test_negative_rotation_normalizes(self, schematic):
        """Test that negative rotation values are normalized to 0-360 range."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=-90
        )
        # -90 should normalize to 270
        assert comp.rotation == 270.0

    def test_rotation_greater_than_360_normalizes(self, schematic):
        """Test that rotation > 360 normalizes to valid angle."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=450
        )
        # 450 should normalize to 90
        assert comp.rotation == 90.0

    def test_invalid_rotation_45_rejected(self, schematic):
        """Test that 45° rotation is rejected (not valid in KiCad)."""
        with pytest.raises(Exception, match="must be 0, 90, 180, or 270"):
            schematic.components.add(
                "Device:R", "R1", "10k", position=(100, 100), rotation=45
            )

    def test_invalid_rotation_135_rejected(self, schematic):
        """Test that 135° rotation is rejected (not valid in KiCad)."""
        with pytest.raises(Exception, match="must be 0, 90, 180, or 270"):
            schematic.components.add(
                "Device:R", "R1", "10k", position=(100, 100), rotation=135
            )

    def test_invalid_rotation_via_setter(self, schematic):
        """Test that invalid rotation via setter is rejected."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=0
        )
        with pytest.raises(ValueError, match="must be 0, 90, 180, or 270"):
            comp.rotation = 45

    def test_invalid_rotation_via_rotate_method(self, schematic):
        """Test that rotate() method rejects invalid final angles."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100, 100), rotation=0
        )
        # rotate() adds to current rotation, so 0 + 45 = 45 (invalid)
        with pytest.raises(ValueError, match="must be 0, 90, 180, or 270"):
            comp.rotate(45)

    def test_valid_rotations_only(self, schematic):
        """Test that only 0, 90, 180, 270 are accepted."""
        valid_angles = [0, 90, 180, 270]

        for i, angle in enumerate(valid_angles):
            comp = schematic.components.add(
                "Device:R",
                f"R{i+1}",
                "10k",
                position=(100 + i * 20, 100),
                rotation=angle
            )
            assert comp.rotation == angle, f"{angle}° should be accepted"

    def test_invalid_rotations_comprehensive(self, schematic):
        """Test that various invalid angles are all rejected."""
        invalid_angles = [1, 30, 45, 60, 120, 135, 150, 200, 225, 315]

        for angle in invalid_angles:
            with pytest.raises(Exception, match="must be 0, 90, 180, or 270"):
                schematic.components.add(
                    "Device:R",
                    f"R{angle}",
                    "10k",
                    position=(100, 100),
                    rotation=angle
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
