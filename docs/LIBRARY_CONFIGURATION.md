# KiCAD Symbol Library Configuration

Guide to configuring KiCAD symbol library paths for use with kicad-sch-api.

## Automatic Library Discovery

The library automatically discovers KiCAD symbol libraries from:

1. **Environment variables** (highest priority)
2. **Standard KiCAD installation paths**
3. **User document directories**

### Version-Flexible Discovery

The library automatically detects KiCAD installations regardless of version:

**macOS**:
- `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad7/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad8/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols/`
- Any installation matching `/Applications/KiCad*/`

**Windows**:
- `C:/Program Files/KiCad/7.0/share/kicad/symbols/`
- `C:/Program Files/KiCad/8.0/share/kicad/symbols/`
- `C:/Program Files/KiCad/9.0/share/kicad/symbols/`
- Any version subdirectory under `Program Files/KiCad/`

**Linux**:
- `/usr/share/kicad/symbols/`
- `/usr/local/share/kicad/symbols/`
- `~/.local/share/kicad/symbols/`

## Environment Variables

### Generic Path

Set a generic path that works across all KiCAD versions:

```bash
# Single path
export KICAD_SYMBOL_DIR=/path/to/kicad/symbols

# Multiple paths (Unix - colon-separated)
export KICAD_SYMBOL_DIR=/path/to/kicad/symbols:/path/to/custom/symbols

# Multiple paths (Windows - semicolon-separated)
set KICAD_SYMBOL_DIR=C:\KiCad\symbols;D:\Custom\symbols
```

### Version-Specific Paths

Set paths for specific KiCAD versions:

```bash
# KiCAD 7
export KICAD7_SYMBOL_DIR=/Applications/KiCad7/KiCad.app/Contents/SharedSupport/symbols

# KiCAD 8
export KICAD8_SYMBOL_DIR=/Applications/KiCad8/KiCad.app/Contents/SharedSupport/symbols

# KiCAD 9
export KICAD9_SYMBOL_DIR=/Applications/KiCad9/KiCad.app/Contents/SharedSupport/symbols
```

**All discovered paths are merged** - you can set multiple environment variables simultaneously.

## Programmatic Configuration

Add library paths directly in your Python code:

```python
import kicad_sch_api as ksa

# Get the global cache
cache = ksa.library.get_symbol_cache()

# Add a single library file
cache.add_library_path("/path/to/Device.kicad_sym")

# Discover all libraries in a directory
cache.discover_libraries(["/path/to/custom/symbols"])
```

## Troubleshooting

### No Libraries Found

If you see this warning:

```
WARNING: No KiCAD symbol libraries found.

Tried the following:
  - Environment variables: KICAD_SYMBOL_DIR, KICAD8_SYMBOL_DIR, KICAD7_SYMBOL_DIR
  - System paths: Default KiCAD installation locations

Solutions:
  1. Set environment variable:
     export KICAD_SYMBOL_DIR=/path/to/kicad/symbols

  2. Add library path programmatically:
     cache = get_symbol_cache()
     cache.add_library_path("/path/to/library.kicad_sym")

  3. Discover libraries manually:
     cache.discover_libraries(["/custom/path"])
```

**Solutions:**

1. **Find your KiCAD installation**:
   - macOS: Open KiCAD, go to Preferences → Configure Paths, look for `KICAD_SYMBOL_DIR`
   - Windows: Usually `C:\Program Files\KiCad\[version]\share\kicad\symbols\`
   - Linux: Usually `/usr/share/kicad/symbols/` or `/usr/local/share/kicad/symbols/`

2. **Set environment variable**:
   ```bash
   # macOS/Linux (add to ~/.bashrc or ~/.zshrc)
   export KICAD_SYMBOL_DIR=/path/to/kicad/symbols

   # Windows (System Environment Variables)
   setx KICAD_SYMBOL_DIR "C:\Path\To\KiCad\symbols"
   ```

3. **Verify the path contains `.kicad_sym` files**:
   ```bash
   ls /path/to/kicad/symbols/*.kicad_sym
   ```

### Custom Library Path Not Found

If your custom library path isn't being discovered:

1. **Check path exists**:
   ```bash
   ls -la /path/to/custom/symbols
   ```

2. **Verify `.kicad_sym` files present**:
   ```bash
   ls /path/to/custom/symbols/*.kicad_sym
   ```

3. **Check permissions**:
   ```bash
   # Ensure read access
   chmod +r /path/to/custom/symbols/*.kicad_sym
   ```

4. **Add path explicitly**:
   ```python
   import kicad_sch_api as ksa

   cache = ksa.library.get_symbol_cache()
   cache.add_library_path("/path/to/custom/library.kicad_sym")
   ```

### Multiple KiCAD Versions Installed

If you have multiple KiCAD versions:

- The library discovers **all versions** automatically
- Set version-specific environment variables if needed
- All libraries are merged (first match wins for duplicate symbols)

Example with multiple versions:

```bash
# Prefer KiCAD 8, fallback to KiCAD 7
export KICAD8_SYMBOL_DIR=/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols
export KICAD7_SYMBOL_DIR=/Applications/KiCad7/KiCad.app/Contents/SharedSupport/symbols
```

### Symbol Not Found

If a specific symbol isn't found:

```python
from kicad_sch_api.core.exceptions import LibraryError

try:
    sch.components.add('Device:R', 'R1', '10k')
except LibraryError as e:
    print(f"Symbol not found: {e}")
    # Check which libraries are loaded
    cache = ksa.library.get_symbol_cache()
    print(f"Loaded libraries: {len(cache._library_paths)}")
```

**Solutions:**

1. **Verify library name**: Check the exact library name in KiCAD
2. **Check symbol name**: Symbol names are case-sensitive
3. **Load library manually**:
   ```python
   cache.add_library_path("/path/to/Device.kicad_sym")
   ```

## Checking Configuration

Verify your library configuration:

```python
import kicad_sch_api as ksa

# Get cache and check discovered libraries
cache = ksa.library.get_symbol_cache()

print(f"Total libraries: {len(cache._library_paths)}")
print(f"Sample libraries: {list(cache._library_paths)[:5]}")

# Check if a specific symbol exists
try:
    symbol_info = cache.get_symbol_info("Device:R")
    print(f"Found symbol: {symbol_info.name}")
    print(f"Pin count: {len(symbol_info.pins)}")
except Exception as e:
    print(f"Symbol not found: {e}")
```

## Advanced Configuration

### Custom Cache Directory

By default, the cache is stored in `~/.cache/kicad-sch-api/symbols`. To use a custom location:

```python
from pathlib import Path
from kicad_sch_api.library.cache import SymbolLibraryCache

cache = SymbolLibraryCache(
    cache_dir=Path("/custom/cache/dir"),
    enable_persistence=True
)
```

### Disable Persistence

For testing or temporary use:

```python
cache = SymbolLibraryCache(enable_persistence=False)
```

### Clear Cache

To force reload of libraries:

```python
cache = ksa.library.get_symbol_cache()
cache.clear_cache()
```

## Platform-Specific Notes

### macOS

- KiCAD app bundles contain libraries inside: `KiCad.app/Contents/SharedSupport/symbols/`
- Version-specific installations are automatically detected (KiCad, KiCad7, KiCad8, KiCad806, etc.)
- Environment variables can be set in `~/.zshrc` or `~/.bashrc`

### Windows

- Libraries typically in: `C:\Program Files\KiCad\[version]\share\kicad\symbols\`
- Use semicolons (`;`) to separate multiple paths in environment variables
- Set environment variables through System Properties → Environment Variables

### Linux

- System-wide libraries in `/usr/share/kicad/symbols/`
- User-specific libraries in `~/.local/share/kicad/symbols/`
- Environment variables can be set in `~/.bashrc` or `~/.profile`

## Examples

### Example 1: Standard KiCAD Installation

No configuration needed - automatic discovery works:

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("MyCircuit")
# Libraries discovered automatically
sch.components.add('Device:R', 'R1', '10k')
```

### Example 2: Custom Library Path

```bash
# Set environment variable
export KICAD_SYMBOL_DIR=/Users/me/CustomLibs/symbols
```

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("MyCircuit")
# Uses custom library path
sch.components.add('MyCustom:SpecialResistor', 'R1', '10k')
```

### Example 3: Multiple Paths

```bash
# Multiple paths (Unix)
export KICAD_SYMBOL_DIR=/opt/kicad/symbols:/home/user/libs/symbols
```

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("MyCircuit")
# Searches both paths
sch.components.add('Device:R', 'R1', '10k')
```

### Example 4: Programmatic Configuration

```python
import kicad_sch_api as ksa

# Get cache
cache = ksa.library.get_symbol_cache()

# Add custom libraries
cache.add_library_path("/path/to/custom/MyLibrary.kicad_sym")

# Discover all libraries in a directory
cache.discover_libraries(["/path/to/my/symbols"])

# Now use them
sch = ksa.create_schematic("MyCircuit")
sch.components.add('MyLibrary:CustomPart', 'U1', 'Value')
```

## See Also

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Getting Started](GETTING_STARTED.md) - Quick start guide
- [README](../README.md) - Main documentation
