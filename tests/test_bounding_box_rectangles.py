#!/usr/bin/env python3
"""
Unit tests for bounding box rectangle generation functionality.

Tests the new draw_bounding_box() and draw_component_bounding_boxes() methods
with proper KiCAD rectangle graphics generation and all stroke types.
"""

import os
import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.component_bounds import BoundingBox, get_component_bounding_box
from kicad_sch_api.core.types import Point


class TestBoundingBoxRectangles:
    """Test bounding box rectangle generation functionality."""

    def test_basic_bounding_box_rectangle(self):
        """Test basic rectangle generation from bounding box."""
        sch = ksa.create_schematic("Basic Bounding Box Test")

        # Add a resistor
        resistor = sch.components.add("Device:R", "R1", "10k", Point(100, 100))

        # Get bounding box
        bbox = get_component_bounding_box(resistor, include_properties=False)

        # Draw rectangle
        rect_uuid = sch.draw_bounding_box(bbox)

        # Verify rectangle was added
        assert rect_uuid is not None
        assert len(rect_uuid) > 0

        # Verify schematic can be saved
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            # Verify file exists and has content
            assert os.path.exists(tmp.name)
            assert os.path.getsize(tmp.name) > 0

            # Read content to verify rectangle was saved
            with open(tmp.name, "r") as f:
                content = f.read()
                assert "(rectangle" in content
                assert rect_uuid in content

            # Cleanup
            os.unlink(tmp.name)

    def test_colored_bounding_box_rectangle(self):
        """Test colored rectangle generation."""
        sch = ksa.create_schematic("Colored Bounding Box Test")

        # Add a capacitor
        capacitor = sch.components.add("Device:C", "C1", "100nF", Point(100, 100))
        bbox = get_component_bounding_box(capacitor, include_properties=False)

        # Draw colored rectangle
        rect_uuid = sch.draw_bounding_box(
            bbox, stroke_width=1.0, stroke_color="red", stroke_type="dash"
        )

        assert rect_uuid is not None

        # Verify in saved content
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            with open(tmp.name, "r") as f:
                content = f.read()
                assert "(rectangle" in content
                assert "(width 1)" in content  # 1mm width
                assert "(type dash)" in content
                assert "(color 255 0 0 1)" in content  # Red color

            os.unlink(tmp.name)

    def test_all_stroke_types(self):
        """Test all valid KiCAD stroke types."""
        sch = ksa.create_schematic("All Stroke Types Test")

        stroke_types = ["default", "solid", "dash", "dot", "dash_dot", "dash_dot_dot"]
        colors = ["black", "red", "blue", "green", "magenta", "cyan"]

        rect_uuids = []

        for i, (stroke_type, color) in enumerate(zip(stroke_types, colors)):
            # Add component
            comp = sch.components.add("Device:R", f"R{i+1}", f"{i+1}k", Point(50 + i * 30, 100))
            bbox = get_component_bounding_box(comp, include_properties=False)

            # Draw rectangle with specific stroke type
            rect_uuid = sch.draw_bounding_box(
                bbox, stroke_width=0.5, stroke_color=color, stroke_type=stroke_type
            )

            rect_uuids.append(rect_uuid)
            assert rect_uuid is not None

        # Verify all stroke types in saved content
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            with open(tmp.name, "r") as f:
                content = f.read()

                # Verify all stroke types are present
                for stroke_type in stroke_types:
                    if stroke_type == "default":
                        assert "(type default)" in content
                    else:
                        assert f"(type {stroke_type})" in content

                # Verify all UUIDs are present
                for rect_uuid in rect_uuids:
                    assert rect_uuid in content

            os.unlink(tmp.name)

    def test_body_vs_properties_bounding_boxes(self):
        """Test difference between body-only and with-properties bounding boxes."""
        sch = ksa.create_schematic("Body vs Properties Test")

        # Add op-amp (has significant property expansion)
        opamp = sch.components.add("Amplifier_Operational:LM358", "U1", "LM358", Point(100, 100))

        # Get both bounding box types
        bbox_body = get_component_bounding_box(opamp, include_properties=False)
        bbox_props = get_component_bounding_box(opamp, include_properties=True)

        # Draw both rectangles
        rect_body_uuid = sch.draw_bounding_box(
            bbox_body, stroke_width=0.5, stroke_color="blue", stroke_type="solid"
        )

        rect_props_uuid = sch.draw_bounding_box(
            bbox_props, stroke_width=0.3, stroke_color="red", stroke_type="dash"
        )

        # Verify properties bounding box is larger
        assert bbox_props.width >= bbox_body.width
        assert bbox_props.height >= bbox_body.height

        # For op-amps, properties should significantly expand height
        height_expansion = bbox_props.height - bbox_body.height
        assert height_expansion > 5.0  # Should be > 5mm expansion

        # Verify both rectangles in saved content
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            with open(tmp.name, "r") as f:
                content = f.read()
                assert rect_body_uuid in content
                assert rect_props_uuid in content
                assert "(color 0 0 255 1)" in content  # Blue
                assert "(color 255 0 0 1)" in content  # Red

            os.unlink(tmp.name)

    def test_multiple_component_bounding_boxes(self):
        """Test drawing bounding boxes for multiple components at once."""
        sch = ksa.create_schematic("Multiple Components Test")

        # Add multiple components
        components = []
        components.append(sch.components.add("Device:R", "R1", "1k", Point(50, 100)))
        components.append(sch.components.add("Device:C", "C1", "100nF", Point(100, 100)))
        components.append(sch.components.add("Device:L", "L1", "10uH", Point(150, 100)))

        # Draw bounding boxes for all components
        rect_uuids = sch.draw_component_bounding_boxes(
            include_properties=False, stroke_width=0.4, stroke_color="green", stroke_type="solid"
        )

        # Should have one rectangle per component
        assert len(rect_uuids) == len(components)

        # Verify all rectangles in saved content
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            with open(tmp.name, "r") as f:
                content = f.read()

                # Verify all UUIDs are present
                for rect_uuid in rect_uuids:
                    assert rect_uuid in content

                # Should have at least 3 rectangles (some symbols might have internal rectangles)
                assert content.count("(rectangle") >= len(components)

            os.unlink(tmp.name)

    def test_invalid_stroke_type_validation(self):
        """Test that invalid stroke types are handled gracefully."""
        sch = ksa.create_schematic("Invalid Stroke Test")
        resistor = sch.components.add("Device:R", "R1", "10k", Point(100, 100))
        bbox = get_component_bounding_box(resistor, include_properties=False)

        # Invalid stroke type should either raise ValueError or fallback to default
        try:
            rect_uuid = sch.draw_bounding_box(bbox, stroke_type="invalid_type")

            # If it succeeds, verify it used a fallback
            with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
                sch.save(tmp.name)

                with open(tmp.name, "r") as f:
                    content = f.read()
                    # Should contain a valid stroke type (fallback to default)
                    assert "(type default)" in content or "(type solid)" in content

                os.unlink(tmp.name)

        except ValueError:
            # This is also acceptable behavior
            pass

    def test_bounding_box_coordinates(self):
        """Test that bounding box coordinates are correctly translated to rectangles."""
        sch = ksa.create_schematic("Coordinates Test")

        # Create a custom bounding box with known coordinates
        test_bbox = BoundingBox(10.0, 20.0, 30.0, 40.0)

        rect_uuid = sch.draw_bounding_box(test_bbox)

        # Verify coordinates in saved content
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            with open(tmp.name, "r") as f:
                content = f.read()

                # Should contain start and end coordinates
                assert "(start 10 20)" in content
                assert "(end 30 40)" in content

            os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
