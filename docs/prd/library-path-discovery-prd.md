# PRD: Versatile KiCAD Symbol Library Path Discovery

## Overview

Implement robust, flexible KiCAD symbol library path discovery that works across:
- Multiple KiCAD versions (7, 8, 9, version-specific builds like KiCad806)
- Multiple platforms (Windows, macOS, Linux)
- Multiple configuration methods (environment variables, programmatic API, auto-detection)

## Problem Statement

Current library path discovery fails when:
- KiCAD is installed with version-specific names (e.g., `/Applications/KiCad806/` instead of `/Applications/KiCad/`)
- Users set environment variables like `KICAD8_SYMBOL_DIR` which are not checked
- Non-standard installation paths are used
- Multiple KiCAD versions are installed simultaneously

**User Impact**: Users cannot use the library without manually adding library paths via code, making the library harder to use.

## Success Criteria

- [ ] Auto-detects KiCAD installations across all versions (7, 8, 9) and version-specific builds
- [ ] Supports environment variables: `KICAD_SYMBOL_DIR`, `KICAD7_SYMBOL_DIR`, `KICAD8_SYMBOL_DIR`, `KICAD9_SYMBOL_DIR`
- [ ] Maintains backward compatibility with existing code
- [ ] Provides clear error messages with suggested solutions when no libraries found
- [ ] All tests pass
- [ ] Documentation updated with path configuration examples

## Functional Requirements

### REQ-1: Version-Flexible Path Discovery

Auto-detect KiCAD installations regardless of version-specific naming:

**macOS**:
- `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad7/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad8/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad806/KiCad.app/Contents/SharedSupport/symbols/`
- `/Applications/KiCad*/KiCad.app/Contents/SharedSupport/symbols/` (glob pattern)

**Windows**:
- `C:/Program Files/KiCad/*/share/kicad/symbols/` (glob for version subdirs)
- `C:/Program Files (x86)/KiCad/*/share/kicad/symbols/`
- Support for 7.0, 8.0, 9.0, etc.

**Linux**:
- `/usr/share/kicad/symbols/`
- `/usr/local/share/kicad/symbols/`
- `~/.local/share/kicad/symbols/`
- Version-specific paths if they exist

### REQ-2: Environment Variable Support

Check environment variables in order:

1. **Generic**: `KICAD_SYMBOL_DIR` - single path or colon-separated list
2. **Version-specific**: `KICAD9_SYMBOL_DIR`, `KICAD8_SYMBOL_DIR`, `KICAD7_SYMBOL_DIR`
3. **Custom**: Support for custom paths via existing programmatic API

**Behavior**:
- All discovered paths are merged (no priority order, all paths checked)
- Invalid paths logged as warnings but don't cause failures
- Empty/unset env vars are silently skipped

### REQ-3: Path Validation

When discovering paths:
- Verify path exists before adding
- Verify path contains `.kicad_sym` files
- Log informational messages about discovered libraries
- Log warnings for invalid/empty paths

### REQ-4: Error Handling and User Guidance

When no libraries found:
```
LibraryError: No KiCAD symbol libraries found.

Tried the following:
  - Environment variables: KICAD_SYMBOL_DIR, KICAD8_SYMBOL_DIR, KICAD7_SYMBOL_DIR
  - System paths: /Applications/KiCad*/..., /usr/share/kicad/symbols, ...

Solutions:
  1. Set environment variable:
     export KICAD_SYMBOL_DIR=/path/to/kicad/symbols

  2. Add library path programmatically:
     cache = get_symbol_cache()
     cache.add_library_path("/path/to/library.kicad_sym")

  3. Discover libraries manually:
     cache.discover_libraries(["/custom/path"])

For more information, see: https://docs.example.com/library-setup
```

### REQ-5: Backward Compatibility

- Existing code must work without changes
- `discover_libraries()` behavior unchanged
- `add_library_path()` behavior unchanged
- Existing programmatic path addition still works

## Technical Constraints

- Must work on Python 3.8+
- Must not introduce new dependencies
- Must maintain existing API signatures
- Must log at appropriate levels (DEBUG for discovery, INFO for found libraries, WARNING for issues)
- Must handle permission errors gracefully

## KiCAD Format Specifications

Library paths contain `.kicad_sym` files following KiCAD's S-expression format.

**Version compatibility**:
- KiCAD 7: `.kicad_sym` format
- KiCAD 8: `.kicad_sym` format (same as v7)
- KiCAD 9: `.kicad_sym` format (same as v7/8)

No format changes required - this is purely path discovery.

## Edge Cases

### EDGE-1: Multiple KiCAD Versions Installed
- Discover all versions
- Load symbols from all found libraries
- Handle duplicate symbol names (first found wins)

### EDGE-2: Custom Installation Paths
- Windows: `D:/Tools/KiCad/`
- macOS: `~/Applications/KiCad806.app/`
- Linux: `/opt/kicad/`
- Solution: Environment variables

### EDGE-3: No KiCAD Installation
- Provide clear error message with solutions
- Don't crash - allow programmatic path addition
- Useful for CI/CD environments with custom paths

### EDGE-4: Permission Errors
- Some paths may not be readable
- Log warning and continue checking other paths
- Don't fail entire discovery process

### EDGE-5: Empty Library Directories
- Directory exists but contains no `.kicad_sym` files
- Log informational message
- Continue checking other paths

## Impact Analysis

**Files Changed**:
- `kicad_sch_api/library/cache.py` - Update `_get_default_library_paths()`
- `kicad_sch_api/library/cache.py` - Add `_check_environment_variables()`
- `kicad_sch_api/library/cache.py` - Update `discover_libraries()` logging

**New Functions**:
- `_check_environment_variables()` - Extract paths from env vars
- `_glob_version_paths()` - Glob for version-specific paths
- `_validate_library_path()` - Validate path contains libraries

**Tests Required**:
- Unit tests for environment variable parsing
- Unit tests for glob pattern matching
- Unit tests for path validation
- Integration tests with mock file systems
- Integration tests with environment variables set

**Documentation Updates**:
- `README.md` - Add library path configuration section
- `docs/API_REFERENCE.md` - Document environment variables
- `docs/GETTING_STARTED.md` - Add troubleshooting section

## Out of Scope

- Footprint library path discovery (schematic API doesn't use footprints for generation)
- Configuration file support (`.kicad_sch_api.yaml`) - may be added later
- Automatic library updates/downloads
- Network-based library paths
- KiCAD project file parsing for library paths

## Acceptance Criteria

- [x] Auto-detects KiCAD 7, 8, 9 installations on all platforms
- [x] Auto-detects version-specific builds (KiCad806, etc.)
- [x] Reads `KICAD_SYMBOL_DIR` environment variable
- [x] Reads version-specific env vars (`KICAD7_SYMBOL_DIR`, `KICAD8_SYMBOL_DIR`, `KICAD9_SYMBOL_DIR`)
- [x] Merges all discovered paths (env vars + system paths)
- [x] Validates paths before adding
- [x] Provides helpful error message when no libraries found
- [x] All existing tests pass (backward compatibility)
- [x] New tests added for environment variables
- [x] New tests added for version-specific path discovery
- [x] Documentation updated

## Implementation Notes

**Platform Detection**:
- Use `platform.system()` for OS detection
- Use `glob.glob()` for version-flexible path patterns
- Use `os.environ.get()` for environment variables

**Path Priority**:
- All paths merged equally (user requested)
- No specific priority order
- First library with matching symbol wins (existing behavior)

**Logging Strategy**:
- DEBUG: Each path checked
- INFO: Libraries discovered and added
- WARNING: Invalid paths, permission errors
- ERROR: No libraries found (with helpful message)
