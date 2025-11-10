---
name: troubleshoot-library
description: Troubleshoot KiCAD symbol library path discovery issues
---

# Troubleshoot KiCAD Symbol Library Issues

## Common Symptom

User reports errors like:
- "Library not found"
- "Symbol X:Y not found"
- "Cannot load component from library"
- Components fail to create with library errors

## Root Cause

The kicad-sch-api library cannot find KiCAD symbol libraries (`.kicad_sym` files).

## Solution: Configure Library Paths

### Step 1: Find Your KiCAD Installation

**✨ NEW: Automatic Library Finder**

The easiest way to find your KiCAD libraries:

```bash
ksa-find-libraries
```

This command automatically searches your system and provides setup instructions.

**Manual Search (if needed):**

**macOS:**
```bash
ls /Applications/KiCad*.app/Contents/SharedSupport/symbols/
```

**Linux:**
```bash
ls /usr/share/kicad/symbols/
ls ~/.local/share/kicad/*/symbols/
```

**Windows:**
```powershell
dir "C:\Program Files\KiCad\*\share\kicad\symbols"
```

### Step 2: Set Environment Variable

**macOS/Linux:**
```bash
# Generic (works for any version)
export KICAD_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols

# Version-specific (if you have KiCAD 8)
export KICAD8_SYMBOL_DIR=/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols/

# Add to ~/.bashrc or ~/.zshrc to make permanent
echo 'export KICAD8_SYMBOL_DIR=/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols/' >> ~/.zshrc
```

**Windows PowerShell:**
```powershell
$env:KICAD8_SYMBOL_DIR="C:\Program Files\KiCad\8.0\share\kicad\symbols"

# Make permanent:
[System.Environment]::SetEnvironmentVariable('KICAD8_SYMBOL_DIR', 'C:\Program Files\KiCad\8.0\share\kicad\symbols', 'User')
```

### Step 3: Verify Configuration

Create a test script:

```python
#!/usr/bin/env python3
import kicad_sch_api as ksa

# Test library discovery
cache = ksa.SymbolLibraryCache(enable_persistence=False)
lib_count = cache.discover_libraries()

print(f"Discovered {lib_count} libraries")

# Test loading a symbol
symbol = cache.get_symbol("Device:R")
if symbol:
    print("✓ Successfully loaded Device:R")
else:
    print("✗ Failed to load symbol")
```

Run with:
```bash
python test_library.py
```

## Supported Environment Variables

The library checks these environment variables in order:

1. `KICAD_SYMBOL_DIR` - Generic, works for any KiCAD version
2. `KICAD9_SYMBOL_DIR` - KiCAD 9 specific
3. `KICAD8_SYMBOL_DIR` - KiCAD 8 specific
4. `KICAD7_SYMBOL_DIR` - KiCAD 7 specific

You can specify multiple paths separated by:
- `:` on macOS/Linux
- `;` on Windows

Example:
```bash
export KICAD_SYMBOL_DIR=/path/1:/path/2:/custom/symbols
```

## Alternative: Programmatic Configuration

If environment variables aren't an option:

```python
import kicad_sch_api as ksa

# Add custom library path
cache = ksa.SymbolLibraryCache()
cache.add_library_path("/path/to/kicad/symbols")
cache.discover_libraries()

# Now create schematic
sch = ksa.create_schematic("MyCircuit")
```

## Verification

Check library discovery worked:

```python
import kicad_sch_api as ksa

cache = ksa.SymbolLibraryCache(enable_persistence=False)
count = cache.discover_libraries()

if count > 0:
    print(f"✓ Found {count} libraries")

    # Test common symbols
    for lib_id in ["Device:R", "Device:C", "power:GND"]:
        symbol = cache.get_symbol(lib_id)
        if symbol:
            print(f"  ✓ {lib_id}")
        else:
            print(f"  ✗ {lib_id} not found")
else:
    print("✗ No libraries found - check environment variables")
```

## Documentation

For complete details, see:
- `docs/LIBRARY_CONFIGURATION.md`
- README section on "Library Path Configuration"

## When to Use This Command

Use this troubleshooting guide when:
- User reports "library not found" errors
- Component creation fails with symbol errors
- User is on non-standard KiCAD installation
- User needs custom library paths
- Library discovery returns 0 libraries
