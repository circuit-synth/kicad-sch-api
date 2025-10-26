"""
Utility functions for S-expression parsing.

Common helper functions used across multiple element parsers,
extracted from monolithic parser.py for reusability.
"""

from typing import List


def color_to_rgba(color_name: str) -> List[float]:
    """
    Convert color name to RGBA values (0.0-1.0) for KiCAD compatibility.

    Args:
        color_name: Color name (e.g., "red", "blue", "green")

    Returns:
        List of 4 floats [R, G, B, A] in range 0.0-1.0

    Example:
        >>> color_to_rgba("red")
        [1.0, 0.0, 0.0, 1.0]
        >>> color_to_rgba("unknown")
        [0.0, 0.0, 0.0, 1.0]  # defaults to black
    """
    # Basic color mapping for common colors (0.0-1.0 range)
    color_map = {
        "red": [1.0, 0.0, 0.0, 1.0],
        "blue": [0.0, 0.0, 1.0, 1.0],
        "green": [0.0, 1.0, 0.0, 1.0],
        "yellow": [1.0, 1.0, 0.0, 1.0],
        "magenta": [1.0, 0.0, 1.0, 1.0],
        "cyan": [0.0, 1.0, 1.0, 1.0],
        "black": [0.0, 0.0, 0.0, 1.0],
        "white": [1.0, 1.0, 1.0, 1.0],
        "gray": [0.5, 0.5, 0.5, 1.0],
        "grey": [0.5, 0.5, 0.5, 1.0],
        "orange": [1.0, 0.5, 0.0, 1.0],
        "purple": [0.5, 0.0, 0.5, 1.0],
    }

    # Return RGBA values, default to black if color not found
    return color_map.get(color_name.lower(), [0.0, 0.0, 0.0, 1.0])


def color_to_rgb255(color_name: str) -> List[int]:
    """
    Convert color name to RGB values (0-255) for KiCAD rectangle graphics.

    Args:
        color_name: Color name (e.g., "red", "blue", "green")

    Returns:
        List of 3 integers [R, G, B] in range 0-255

    Example:
        >>> color_to_rgb255("red")
        [255, 0, 0]
        >>> color_to_rgb255("unknown")
        [0, 0, 0]  # defaults to black
    """
    # Basic color mapping for common colors (0-255 range)
    color_map = {
        "red": [255, 0, 0],
        "blue": [0, 0, 255],
        "green": [0, 255, 0],
        "yellow": [255, 255, 0],
        "magenta": [255, 0, 255],
        "cyan": [0, 255, 255],
        "black": [0, 0, 0],
        "white": [255, 255, 255],
        "gray": [128, 128, 128],
        "grey": [128, 128, 128],
        "orange": [255, 128, 0],
        "purple": [128, 0, 128],
    }

    # Return RGB values, default to black if color not found
    return color_map.get(color_name.lower(), [0, 0, 0])
