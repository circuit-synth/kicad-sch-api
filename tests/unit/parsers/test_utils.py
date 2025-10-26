"""
Unit tests for parser utility functions.
"""

import pytest

from kicad_sch_api.parsers.utils import color_to_rgb255, color_to_rgba


class TestColorConversion:
    """Test color conversion utilities."""

    def test_color_to_rgba_basic_colors(self):
        """Test RGBA conversion for basic colors."""
        assert color_to_rgba("red") == [1.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("blue") == [0.0, 0.0, 1.0, 1.0]
        assert color_to_rgba("green") == [0.0, 1.0, 0.0, 1.0]
        assert color_to_rgba("yellow") == [1.0, 1.0, 0.0, 1.0]
        assert color_to_rgba("magenta") == [1.0, 0.0, 1.0, 1.0]
        assert color_to_rgba("cyan") == [0.0, 1.0, 1.0, 1.0]

    def test_color_to_rgba_grayscale(self):
        """Test RGBA conversion for grayscale colors."""
        assert color_to_rgba("black") == [0.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("white") == [1.0, 1.0, 1.0, 1.0]
        assert color_to_rgba("gray") == [0.5, 0.5, 0.5, 1.0]
        assert color_to_rgba("grey") == [0.5, 0.5, 0.5, 1.0]  # British spelling

    def test_color_to_rgba_case_insensitive(self):
        """Test that color names are case-insensitive."""
        assert color_to_rgba("RED") == [1.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("Red") == [1.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("rEd") == [1.0, 0.0, 0.0, 1.0]

    def test_color_to_rgba_unknown_color(self):
        """Test that unknown colors default to black."""
        assert color_to_rgba("unknown") == [0.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("notacolor") == [0.0, 0.0, 0.0, 1.0]
        assert color_to_rgba("") == [0.0, 0.0, 0.0, 1.0]

    def test_color_to_rgb255_basic_colors(self):
        """Test RGB255 conversion for basic colors."""
        assert color_to_rgb255("red") == [255, 0, 0]
        assert color_to_rgb255("blue") == [0, 0, 255]
        assert color_to_rgb255("green") == [0, 255, 0]
        assert color_to_rgb255("yellow") == [255, 255, 0]
        assert color_to_rgb255("magenta") == [255, 0, 255]
        assert color_to_rgb255("cyan") == [0, 255, 255]

    def test_color_to_rgb255_grayscale(self):
        """Test RGB255 conversion for grayscale colors."""
        assert color_to_rgb255("black") == [0, 0, 0]
        assert color_to_rgb255("white") == [255, 255, 255]
        assert color_to_rgb255("gray") == [128, 128, 128]
        assert color_to_rgb255("grey") == [128, 128, 128]  # British spelling

    def test_color_to_rgb255_case_insensitive(self):
        """Test that color names are case-insensitive."""
        assert color_to_rgb255("RED") == [255, 0, 0]
        assert color_to_rgb255("Red") == [255, 0, 0]
        assert color_to_rgb255("rEd") == [255, 0, 0]

    def test_color_to_rgb255_unknown_color(self):
        """Test that unknown colors default to black."""
        assert color_to_rgb255("unknown") == [0, 0, 0]
        assert color_to_rgb255("notacolor") == [0, 0, 0]
        assert color_to_rgb255("") == [0, 0, 0]

    def test_color_formats_are_consistent(self):
        """Test that rgba and rgb255 return consistent colors (scaled)."""
        # Red should be [1.0, 0.0, 0.0, 1.0] in RGBA and [255, 0, 0] in RGB255
        rgba = color_to_rgba("red")
        rgb255 = color_to_rgb255("red")

        # Check that RGB components scale correctly (ignore alpha)
        assert int(rgba[0] * 255) == rgb255[0]
        assert int(rgba[1] * 255) == rgb255[1]
        assert int(rgba[2] * 255) == rgb255[2]
