"""
Font metrics and text rendering constants for KiCad schematic text.

These constants are used for accurate text bounding box calculations
and symbol spacing in schematic layouts.
"""

# KiCad default text size in mm
# Increased to better match actual KiCad rendering
DEFAULT_TEXT_HEIGHT = 2.54  # 100 mils (doubled from 50 mils)

# Default pin dimensions
DEFAULT_PIN_LENGTH = 2.54  # 100 mils
DEFAULT_PIN_NAME_OFFSET = 0.508  # 20 mils - offset from pin endpoint to label text
DEFAULT_PIN_NUMBER_SIZE = 1.27  # 50 mils

# Text width ratio for proportional font rendering
# KiCad uses proportional fonts where average character width is ~0.65x height
# This prevents label text from extending beyond calculated bounding boxes
DEFAULT_PIN_TEXT_WIDTH_RATIO = (
    0.65  # Width to height ratio for pin text (proportional font average)
)
