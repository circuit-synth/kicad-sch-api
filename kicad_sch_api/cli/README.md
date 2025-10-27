

# KiCad CLI Wrappers with Docker Fallback

Pythonic wrappers around `kicad-cli` commands with automatic Docker fallback for users without KiCad installed.

## Features

✅ **Dual Execution Mode**: Works with local `kicad-cli` OR Docker
✅ **Automatic Fallback**: Tries local first, falls back to Docker seamlessly
✅ **Zero Install Option**: Pull Docker image on demand
✅ **Trustworthy**: Uses KiCad's official tools (guaranteed correctness)
✅ **Complete**: All 8 netlist formats, full BOM customization, ERC validation
✅ **CI/CD Friendly**: Consistent environment across all platforms

## Quick Start

```python
import kicad_sch_api as ksa

# Load schematic
sch = ksa.Schematic.load('circuit.kicad_sch')

# Run ERC validation
report = sch.run_erc()
if report.has_errors():
    print(f"Found {report.error_count} errors")

# Export netlist for SPICE simulation
sch.export_netlist(format='spice')

# Export BOM for manufacturing
sch.export_bom(
    fields=['Reference', 'Value', 'Footprint', 'MPN'],
    group_by=['Value', 'Footprint'],
    exclude_dnp=True,
)

# Export PDF documentation
sch.export_pdf(theme='KiCad Classic')
```

## Supported Operations

### 1. ERC (Electrical Rule Check)

Validate schematic for electrical errors.

```python
report = sch.run_erc(
    format='json',        # 'json' or 'report'
    severity='all',       # 'all', 'error', 'warning', 'exclusions'
    units='mm',           # 'mm', 'in', 'mils'
)

if report.has_errors():
    for error in report.get_errors():
        print(f"Error: {error.description}")
```

### 2. Netlist Export (8 Formats)

Export netlists for PCB layout and simulation.

```python
# KiCad S-expression (default)
sch.export_netlist(format='kicadsexpr')

# SPICE for simulation
sch.export_netlist(format='spice')

# Other formats
formats = ['kicadxml', 'cadstar', 'orcadpcb2', 'spicemodel', 'pads', 'allegro']
```

### 3. BOM (Bill of Materials) Export

Generate CSV files for manufacturing and procurement.

```python
sch.export_bom(
    fields=['Reference', 'Value', 'Footprint', 'MPN', 'Manufacturer'],
    labels=['Refs', 'Value', 'Footprint', 'MPN', 'Mfr'],
    group_by=['Value', 'Footprint'],
    sort_field='Reference',
    exclude_dnp=True,                    # Exclude Do-Not-Populate
    include_excluded_from_bom=False,     # Exclude components marked 'Exclude from BOM'
    field_delimiter=',',
    ref_range_delimiter='-',             # Use ranges like "R1-R5"
)
```

### 4. PDF Export

Export professional documentation.

```python
sch.export_pdf(
    theme='KiCad Classic',
    black_and_white=False,
    exclude_pdf_property_popups=False,
    exclude_pdf_hierarchical_links=False,
    pages=[1, 2, 3],  # Specific pages, or None for all
)
```

### 5. SVG Export

Export web-ready graphics.

```python
svgs = sch.export_svg(
    theme='KiCad Classic',
    black_and_white=False,
    no_background_color=True,
)

for svg in svgs:
    print(f"Generated: {svg}")
```

### 6. DXF Export

Export for CAD integration.

```python
dxfs = sch.export_dxf()
```

## Execution Modes

### Auto Mode (Default)

Tries local `kicad-cli` first, falls back to Docker if unavailable.

```python
# Uses auto mode by default
sch.export_netlist(format='spice')
```

### Force Local Mode

```bash
export KICAD_CLI_MODE=local
```

```python
from kicad_sch_api.cli import set_execution_mode
set_execution_mode('local')
```

### Force Docker Mode

```bash
export KICAD_CLI_MODE=docker
export KICAD_DOCKER_IMAGE=kicad/kicad:9.0  # Optional: specify version
```

```python
from kicad_sch_api.cli import set_execution_mode
set_execution_mode('docker')
```

## Installation

### Option 1: Local KiCad (Recommended)

Install KiCad 8.0+ from https://www.kicad.org/download/

Verify installation:
```bash
kicad-cli version
```

### Option 2: Docker

Install Docker from https://docs.docker.com/get-docker/

The Docker image will be automatically pulled on first use (~2GB).

### Option 3: Both

Install both for maximum flexibility. The library will use local when available, Docker when needed.

## Checking Availability

```python
from kicad_sch_api.cli import get_executor_info

info = get_executor_info()
print(f"Local KiCad: {info.local_available} ({info.local_version})")
print(f"Docker: {info.docker_available}")
print(f"Active mode: {info.active_mode}")
```

## Low-Level API

For advanced use cases, you can use the CLI modules directly:

```python
from pathlib import Path
from kicad_sch_api.cli.netlist import export_netlist
from kicad_sch_api.cli.bom import export_bom
from kicad_sch_api.cli.erc import run_erc

# Direct function calls
netlist = export_netlist(
    Path('circuit.kicad_sch'),
    format='spice',
)

bom = export_bom(
    Path('circuit.kicad_sch'),
    exclude_dnp=True,
)

report = run_erc(
    Path('circuit.kicad_sch'),
    format='json',
)
```

## Custom Executor

For fine-grained control:

```python
from kicad_sch_api.cli.base import KiCadExecutor

executor = KiCadExecutor(
    mode='docker',
    docker_image='kicad/kicad:9.0',
    verbose=True,  # Print commands
)

# Use with export functions
from kicad_sch_api.cli.netlist import export_netlist

netlist = export_netlist(
    Path('circuit.kicad_sch'),
    format='spice',
    executor=executor,
)
```

## Docker Details

### Images

Official KiCad Docker images: `kicad/kicad`

Available tags:
- `latest` - Latest stable version
- `9.0` - KiCad 9.0
- `8.0` - KiCad 8.0

### How It Works

```bash
# What happens behind the scenes:
docker run --rm \
  -v /path/to/project:/workspace \
  -w /workspace \
  --user $(id -u):$(id -g) \
  kicad/kicad:latest \
  kicad-cli sch export netlist --format spice circuit.kicad_sch
```

The library:
1. Mounts your project directory
2. Sets working directory
3. Maps user ID to avoid permission issues
4. Executes `kicad-cli` inside container
5. Returns results to you

### Performance

- **First run**: Downloads image (~2GB, one-time)
- **Subsequent runs**: Container startup overhead (~1-2 seconds)
- **Local mode**: No overhead, instant execution

## Troubleshooting

### "kicad-cli not found"

```
❌ KiCad CLI not available in any mode.

Install options:
1. Install KiCad: https://www.kicad.org/download/
2. Install Docker: https://docs.docker.com/get-docker/
```

**Solution**: Install KiCad or Docker

### "Docker not running"

```
❌ Docker not found
```

**Solution**: Start Docker Desktop or Docker daemon

### Permission Issues (Linux)

If Docker outputs files owned by root:

```python
# The library automatically handles this with --user flag
# But if issues persist, check Docker daemon configuration
```

### Version Mismatch

Force specific KiCad version:

```bash
export KICAD_DOCKER_IMAGE=kicad/kicad:9.0
```

## Examples

See `examples/kicad_cli_exports.py` for a comprehensive demonstration.

## Benefits Over Manual Implementation

| Approach | Complexity | Trust | Maintenance | Formats |
|----------|------------|-------|-------------|---------|
| **Reimplementing netlist generation** | Very High | Low | High | Limited |
| **Using kicad-cli wrappers** | Low | ✅ High | ✅ Low | ✅ All 8 |

**Why use KiCad's tools:**
- ✅ Guaranteed correctness (KiCad's own implementation)
- ✅ All formats supported (8 netlist formats, etc.)
- ✅ Future-proof (works with new KiCad versions)
- ✅ Less code to maintain (thin wrappers vs full implementation)
- ✅ Users can trust the output

## Architecture

```
kicad_sch_api/cli/
├── __init__.py          # Public API
├── base.py              # KiCadExecutor with Docker fallback
├── types.py             # Type definitions
├── erc.py               # ERC validation
├── netlist.py           # Netlist export
├── bom.py               # BOM export
└── export_docs.py       # PDF/SVG/DXF export
```

## Related Issues

- GitHub Issue #33: Netlist generation ✅ Solved
- GitHub Issue #34: BOM generation ✅ Solved
- New capability: ERC validation ✅
- New capability: PDF/SVG documentation ✅

## License

MIT License - Same as kicad-sch-api

---

**This module provides trustworthy, comprehensive KiCad export functionality with zero-install Docker fallback!**
