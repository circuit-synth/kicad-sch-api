# Library Module

Symbol library management and caching system.

## Overview

This module provides symbol library integration with multi-layer caching for performance. It manages access to KiCAD symbol libraries and caches symbol information.

## Main Components

### Symbol Library Cache (`cache.py`)
- **Lines**: 450+
- **Purpose**: Multi-layer symbol caching and lookup
- **Key Class**: `SymbolLibraryCache`

#### Caching Layers
The cache uses a three-tier caching strategy:

1. **RAM Cache (L1)** - Fast in-memory dictionary
   - Holds recently accessed symbols
   - Cleared on cache reset
   - Fastest access time

2. **Disk Cache (L2)** - SQLite database
   - Persistent between sessions
   - Default location: `~/.kicad_sch_api/cache/`
   - Survives process restarts
   - Moderate access time

3. **KiCAD Library (L3)** - Original source
   - KiCAD symbol library files
   - Slowest but authoritative source
   - Fallback when cache misses

#### Key Methods
- `get_symbol(lib_id)` - Get symbol by ID (triggers cache lookup)
- `load_from_library(lib_id)` - Load from KiCAD library
- `clear_cache()` - Clear all cache layers
- `invalidate_symbol(lib_id)` - Invalidate specific symbol
- `find_symbols(pattern)` - Search symbols by pattern

#### Symbol Information Cached
- Pin definitions and positions
- Symbol properties and parameters
- Footprint information
- Inheritance relationships

### Singleton Access

```python
# Get the global symbol cache instance
cache = get_symbol_cache()

# Or use directly
from kicad_sch_api.library import SymbolLibraryCache
cache = SymbolLibraryCache()
```

## Library Configuration

Symbol libraries are discovered and configured through:

1. **KiCAD System Paths** - Standard KiCAD installation
   - `/usr/share/kicad/symbols/` (Linux)
   - `~/AppData/Roaming/kicad/` (Windows)
   - `/Applications/KiCAD/Contents/SharedSupport/symbols/` (macOS)

2. **User Libraries** - Custom symbol paths
   - Configured in KiCAD project file
   - Can be added programmatically

3. **Environment Variables**
   - `KICAD_SYMBOL_DIR` - Override symbol path
   - `KICAD_LIBRARY_PATH` - Additional library paths

## Symbol Library Format

KiCAD libraries use `.kicad_sym` format:
- S-expression based
- Contains symbol definitions
- Hierarchical symbol inheritance
- Property definitions

## Symbol Inheritance

KiCAD supports symbol inheritance:
- Base symbols define common properties
- Derived symbols inherit and extend
- Cache resolves inheritance chain
- Important for multi-unit symbols

## Performance Characteristics

- **First lookup**: ~100-500ms (loads from KiCAD)
- **Cached lookup**: ~1ms (from RAM cache)
- **Disk cache lookup**: ~10-50ms (from SQLite)

## Cache Management

### Automatic Expiration
- Cache entries don't automatically expire
- Useful for long-running processes
- May need manual invalidation for library updates

### Manual Cache Control
```python
cache = get_symbol_cache()

# Clear all caches
cache.clear_cache()

# Invalidate specific symbol
cache.invalidate_symbol('Device:R')

# Reload from library
cache.load_from_library('Device:R')
```

## Library Search

Find symbols by pattern:
```python
cache = get_symbol_cache()

# Find resistors
resistors = cache.find_symbols('*:R')

# Find specific library
device_lib = cache.find_symbols('Device:*')
```

## Disk Cache Details

**Location**: `~/.kicad_sch_api/cache/symbol_cache.db`

**Contents**: SQLite database with tables:
- `symbols` - Symbol definitions and metadata
- `pins` - Pin information
- `properties` - Symbol properties
- `inheritance` - Symbol inheritance relationships

**Size**: Typically 1-10MB depending on library usage

**Cleanup**: Delete database file to clear (will be regenerated)

## Known Issues

1. **Cache Invalidation** - No automatic invalidation when libraries change
2. **Disk Cache Path** - Hardcoded location, not configurable
3. **Search Performance** - Pattern matching could be optimized
4. **Symbol Inheritance** - Edge cases in multi-level inheritance

## Integration Points

### Used By
- `ComponentManager` - Get symbol info when adding components
- `WireManager` - Get pin positions for routing
- `ValidationManager` - Validate component references
- `FormatterManager` - Format symbol properties

### External Dependencies
- `sexpdata` - Parse KiCAD library files
- `sqlite3` - Disk caching
- Python `pathlib` - Path handling

## Future Improvements

- [ ] Configurable cache location
- [ ] Automatic cache invalidation on file change
- [ ] Library update detection
- [ ] Parallel cache loading
- [ ] Symbol preview/thumbnail support
- [ ] Advanced search features (by properties, functionality)

## Testing

Tests located in `../../tests/`:
- `test_symbol_cache.py` - Cache functionality
- `test_library_integration.py` - Library loading
- Integration tests with real KiCAD libraries

## References

- KiCAD Symbol Format: https://github.com/KiCad/kicad-symbols
- Cache strategy: See `CODEBASE_ANALYSIS.md`
- Configuration: See `core/config.py`
