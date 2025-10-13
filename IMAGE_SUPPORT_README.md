# Image Support in kicad-sch-api

## Overview

Images are now fully supported in kicad-sch-api! You can add PNG, JPG, or any image format to your KiCad schematics. The images are **embedded directly in the .kicad_sch file** as base64-encoded data.

## Features

✅ **Add images to schematics** via Python API
✅ **Parse existing images** from KiCad files
✅ **Exact format preservation** - output matches KiCad's native format
✅ **Embedded storage** - no external image files needed after adding
✅ **Scalable images** - control size with scale parameter

## Quick Start

### Adding an Image

```python
import base64
from pathlib import Path
import kicad_sch_api as ksa

# Load or create a schematic
sch = ksa.Schematic.load('my_schematic.kicad_sch')

# Read and encode your image
image_path = Path('circuit_diagram.png')
with open(image_path, 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Add the image to the schematic
image_uuid = sch.add_image(
    position=(100.0, 100.0),  # Position in mm on the schematic
    data=image_data,           # Base64-encoded image data
    scale=1.0                  # Optional: scale factor (1.0 = original size)
)

# Save the schematic
sch.save()
```

### Reading Images from a Schematic

```python
# Load a schematic
sch = ksa.Schematic.load('schematic_with_images.kicad_sch')

# Access images
images = sch._data.get("images", [])

for img in images:
    print(f"UUID: {img['uuid']}")
    print(f"Position: ({img['position']['x']}, {img['position']['y']})")
    print(f"Scale: {img['scale']}")
    print(f"Data length: {len(img['data'])} chars")
```

## Testing

Run the included test script with your circuit image:

```bash
# Using your circuit image
uv run python test_image_support.py /path/to/your/circuit_image.png

# Using the test image
uv run python test_image_support.py test_circuit.png
```

### Test Output

The test will:
1. Load your image and encode it
2. Create a new schematic
3. Add the image at position (100, 100)
4. Add a resistor for reference
5. Save the schematic
6. Load it back and verify the image
7. Create `test_image_output.kicad_sch`

You can open `test_image_output.kicad_sch` in KiCad to see the embedded image!

## How It Works

### Storage Format

Images are embedded in the `.kicad_sch` file in this format:

```lisp
(image
    (at 129.54 87.63)
    (uuid "7ea5043a-a1e5-43aa-a301-327791d1ef19")
    (data "iVBORw0KGgoAAAANSUhEUgAABFYAAALaCAYAAAAbYtf/..."
          "VwdYU8kWnltSSQgQiICU0JsgIiWAlBBaAOlFEJWQBAglxoSgYkcXV3DtIoJlRVdBFDsgYsOuLIrd"
          ...more lines...
    )
)
```

The base64 data is split into 76-character lines for readability (standard base64 line length).

### Benefits of Embedded Storage

- **Self-contained**: No external files to manage
- **Version control friendly**: Image changes tracked with schematic
- **No broken links**: Can't lose the image file
- **KiCad native**: Uses KiCad's built-in image format

## API Reference

### `Schematic.add_image()`

```python
def add_image(
    self,
    position: Union[Point, Tuple[float, float]],
    data: str,
    scale: float = 1.0,
    uuid: Optional[str] = None,
) -> str:
    """
    Add an image element to the schematic.

    Args:
        position: Image position in mm (x, y) or Point object
        data: Base64-encoded image data
        scale: Image scale factor (default 1.0)
        uuid: Optional UUID (auto-generated if None)

    Returns:
        UUID of the created image element
    """
```

### Position Units

- Positions are in **millimeters (mm)** on the schematic canvas
- Origin (0, 0) is typically the top-left corner
- Standard component spacing is 2.54mm (0.1 inch grid)

## Examples

### Add a Logo to Your Schematic

```python
import base64
import kicad_sch_api as ksa

sch = ksa.Schematic.load('project.kicad_sch')

# Add company logo in top-right corner
with open('company_logo.png', 'rb') as f:
    logo_data = base64.b64encode(f.read()).decode('utf-8')

sch.add_image(
    position=(200, 20),  # Top right
    data=logo_data,
    scale=0.5  # Half size
)

sch.save()
```

### Add Multiple Images

```python
images = [
    ('diagram1.png', (50, 50)),
    ('diagram2.png', (150, 50)),
    ('notes.png', (50, 150)),
]

for img_path, pos in images:
    with open(img_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    sch.add_image(position=pos, data=data)

sch.save()
```

## Notes

- **Supported formats**: Any format your image viewer can encode (PNG, JPG, GIF, etc.)
- **File size**: Large images will increase schematic file size significantly
- **KiCad compatibility**: Works with KiCad 6.0+
- **Transparency**: PNG transparency is preserved

## Files

- `test_image_support.py` - Comprehensive test script
- `create_minimal_test_image.py` - Creates a minimal test PNG
- `test_image_output.kicad_sch` - Example output (created by test)

## Implementation Details

### Code Files Modified

1. **types.py**: Added `Image` dataclass
2. **parser.py**: Added `_parse_image()` and `_image_to_sexp()`
3. **schematic.py**: Added `add_image()` method

The implementation preserves KiCad's exact format, including:
- Base64 line splitting (76 chars per line)
- Element ordering in the S-expression
- UUID generation and tracking
