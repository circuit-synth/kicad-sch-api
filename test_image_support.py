#!/usr/bin/env python3
"""
Test script for image support in kicad-sch-api.

This script demonstrates adding an image to a KiCad schematic,
saving it, and verifying it can be read back.
"""

import base64
import sys
from pathlib import Path

# Add the package to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point


def encode_image_to_base64(image_path: Path) -> str:
    """Read an image file and encode it to base64."""
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode('utf-8')


def test_add_image():
    """Test adding an image to a schematic."""

    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:
        print("Usage: python test_image_support.py <image_path>")
        print("Example: python test_image_support.py test_circuit.png")
        sys.exit(1)

    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)

    print(f"📸 Testing image support with: {image_path}")
    print(f"   Image size: {image_path.stat().st_size} bytes")

    # Create a new schematic
    print("\n1️⃣  Creating new schematic...")
    sch = Schematic.create(name="Image Test Schematic")

    # Encode the image to base64
    print("2️⃣  Encoding image to base64...")
    image_data = encode_image_to_base64(image_path)
    print(f"   Encoded data length: {len(image_data)} characters")

    # Add the image to the schematic
    print("3️⃣  Adding image to schematic...")
    image_uuid = sch.add_image(
        position=(100.0, 100.0),  # Position in mm
        data=image_data,
        scale=1.0
    )
    print(f"   ✓ Image added with UUID: {image_uuid}")

    # Add a component for reference
    print("4️⃣  Adding a resistor for reference...")
    sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=Point(50.0, 50.0)
    )
    print("   ✓ Resistor R1 added")

    # Save the schematic
    output_path = Path("test_image_output.kicad_sch")
    print(f"\n5️⃣  Saving schematic to: {output_path}")
    sch.save(output_path)
    print(f"   ✓ Saved ({output_path.stat().st_size} bytes)")

    # Verify by loading it back
    print("\n6️⃣  Verifying: Loading schematic back...")
    sch_loaded = Schematic.load(output_path)

    # Check that images are present
    images = sch_loaded._data.get("images", [])
    print(f"   Found {len(images)} image(s) in loaded schematic")

    if len(images) > 0:
        loaded_image = images[0]
        print(f"   ✓ Image UUID: {loaded_image.get('uuid')}")
        print(f"   ✓ Image position: ({loaded_image.get('position', {}).get('x')}, {loaded_image.get('position', {}).get('y')})")
        print(f"   ✓ Image scale: {loaded_image.get('scale')}")
        print(f"   ✓ Image data length: {len(loaded_image.get('data', ''))} characters")

        # Verify data integrity
        if loaded_image.get('data') == image_data:
            print("   ✅ Image data matches original!")
        else:
            print("   ❌ Image data does not match original")
            return False
    else:
        print("   ❌ No images found in loaded schematic")
        return False

    # Check component is still there
    components = sch_loaded.components
    print(f"\n   Found {len(components)} component(s)")
    if len(components) > 0:
        print(f"   ✓ Component R1 preserved")

    print("\n✅ All tests passed!")
    print(f"\n📁 Output file: {output_path.absolute()}")
    print("   You can now open this file in KiCad to see the embedded image")

    return True


def test_parse_existing_image():
    """Test parsing an existing schematic with an image."""
    test_file = Path("test_image_output.kicad_sch")

    if not test_file.exists():
        print(f"No existing test file found at {test_file}")
        return

    print("\n" + "="*60)
    print("Testing parsing of existing schematic with image")
    print("="*60)

    sch = Schematic.load(test_file)
    images = sch._data.get("images", [])

    print(f"\nFound {len(images)} image(s)")
    for i, img in enumerate(images, 1):
        print(f"\nImage {i}:")
        print(f"  UUID: {img.get('uuid')}")
        print(f"  Position: ({img.get('position', {}).get('x')}, {img.get('position', {}).get('y')})")
        print(f"  Scale: {img.get('scale', 1.0)}")
        print(f"  Data length: {len(img.get('data', ''))} characters")
        print(f"  Data preview: {img.get('data', '')[:80]}...")


if __name__ == "__main__":
    try:
        success = test_add_image()

        # Also test parsing if the file exists
        if success:
            test_parse_existing_image()

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
