#!/usr/bin/env python3
"""Tests for image support in kicad-sch-api."""

import base64
from pathlib import Path

import pytest

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point


def create_test_image_data() -> str:
    """Create a minimal test PNG image as base64."""
    # 1x1 red pixel PNG
    png_bytes = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    return base64.b64encode(png_bytes).decode("utf-8")


def test_add_image():
    """Test adding an image to a schematic."""
    sch = Schematic.create(name="Image Test")
    image_data = create_test_image_data()

    image_uuid = sch.add_image(position=(100.0, 100.0), data=image_data, scale=1.0)

    assert image_uuid is not None
    assert len(image_uuid) > 0


def test_add_image_with_tuple_position():
    """Test adding an image with tuple position."""
    sch = Schematic.create(name="Image Test")
    image_data = create_test_image_data()

    image_uuid = sch.add_image(position=(150.0, 200.0), data=image_data, scale=2.0)

    assert image_uuid is not None


def test_add_image_with_point_position():
    """Test adding an image with Point position."""
    sch = Schematic.create(name="Image Test")
    image_data = create_test_image_data()

    image_uuid = sch.add_image(position=Point(150.0, 200.0), data=image_data, scale=0.5)

    assert image_uuid is not None


def test_image_roundtrip(tmp_path):
    """Test that images survive save/load roundtrip."""
    sch = Schematic.create(name="Image Roundtrip Test")
    image_data = create_test_image_data()

    # Add image
    image_uuid = sch.add_image(position=(100.0, 100.0), data=image_data, scale=1.5)

    # Save to file
    output_file = tmp_path / "test_image.kicad_sch"
    sch.save(output_file)

    # Load back
    sch_loaded = Schematic.load(output_file)
    images = sch_loaded._data.get("images", [])

    # Verify image was preserved
    assert len(images) == 1
    loaded_image = images[0]
    assert loaded_image.get("uuid") == image_uuid
    assert loaded_image.get("data") == image_data
    assert loaded_image.get("scale") == 1.5

    # Verify position
    pos = loaded_image.get("position", {})
    assert pos.get("x") == 100.0
    assert pos.get("y") == 100.0


def test_multiple_images(tmp_path):
    """Test adding multiple images to a schematic."""
    sch = Schematic.create(name="Multiple Images Test")
    image_data = create_test_image_data()

    # Add multiple images
    uuid1 = sch.add_image(position=(50.0, 50.0), data=image_data, scale=1.0)
    uuid2 = sch.add_image(position=(100.0, 50.0), data=image_data, scale=2.0)
    uuid3 = sch.add_image(position=(150.0, 50.0), data=image_data, scale=0.5)

    # Save and load
    output_file = tmp_path / "test_multiple_images.kicad_sch"
    sch.save(output_file)
    sch_loaded = Schematic.load(output_file)

    # Verify all images preserved
    images = sch_loaded._data.get("images", [])
    assert len(images) == 3

    uuids = [img.get("uuid") for img in images]
    assert uuid1 in uuids
    assert uuid2 in uuids
    assert uuid3 in uuids
