# ReadTheDocs Setup Guide

This document explains how to set up and deploy the kicad-sch-api documentation on ReadTheDocs.

## What's Configured

The repository is fully configured for ReadTheDocs deployment:

### Configuration Files

- **`.readthedocs.yaml`** - ReadTheDocs build configuration
  - Python 3.11 build environment
  - Installs `uv` package manager
  - Uses `docs/conf.py` for Sphinx configuration
  - Generates PDF and EPUB formats

- **`docs/conf.py`** - Sphinx configuration
  - Sphinx RTD theme for professional styling
  - MyST parser for markdown support
  - Auto-generated API docs from docstrings
  - Napoleon extension for Google/NumPy style docstrings

- **`docs/index.rst`** - Main documentation index
  - Navigation structure
  - Quick example and installation guide
  - Links to all documentation sections

- **`docs/api/modules.rst`** - API reference structure
  - Auto-generated from Python docstrings
  - Organized by module (collections, parsers, etc.)

### Documentation Structure

```
docs/
├── conf.py                    # Sphinx configuration
├── index.rst                  # Main index (entry point)
├── api/
│   └── modules.rst           # API reference
├── _static/                   # Static assets (images, CSS)
├── _templates/                # Custom templates (if needed)
├── README.md                  # Documentation index
├── GETTING_STARTED.md         # Beginner's guide
├── WHY_USE_THIS_LIBRARY.md   # Value proposition
├── API_REFERENCE.md           # Complete API docs
├── RECIPES.md                 # Practical examples
└── ARCHITECTURE.md            # Internal design
```

## Local Testing

### Build Documentation Locally

```bash
# Install docs dependencies
uv pip install -e ".[docs]"

# Build HTML documentation
cd docs
uv run sphinx-build -b html . _build/html

# View in browser
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
start _build/html/index.html  # Windows
```

### Build Other Formats

```bash
# PDF (requires LaTeX)
uv run sphinx-build -b latex . _build/latex
cd _build/latex && make

# EPUB
uv run sphinx-build -b epub . _build/epub
```

## ReadTheDocs Deployment

### Initial Setup

1. **Import Project on ReadTheDocs**
   - Go to https://readthedocs.org/
   - Sign in with GitHub account
   - Click "Import a Project"
   - Select `circuit-synth/kicad-sch-api`

2. **Configure Project**
   - Project will auto-detect `.readthedocs.yaml`
   - Default branch: `main`
   - Documentation URL: `https://kicad-sch-api.readthedocs.io/`

3. **Build Settings** (auto-configured via `.readthedocs.yaml`)
   - ✅ Build documentation on every commit
   - ✅ Build documentation on pull requests
   - ✅ Generate PDF and EPUB downloads

### Webhook Integration

ReadTheDocs automatically sets up GitHub webhooks to trigger builds on:
- Pushes to `main` branch
- New tags/releases
- Pull requests (for preview builds)

### Custom Domain (Optional)

If you want to use a custom domain:

1. In ReadTheDocs Admin → Domains
2. Add custom domain (e.g., `docs.circuit-synth.com`)
3. Add CNAME record in DNS pointing to `readthedocs.io`

## Adding New Documentation

### Adding Markdown Pages

1. Create new `.md` file in `docs/` directory
2. Add to `docs/index.rst` table of contents:

```rst
.. toctree::
   :maxdepth: 2
   :caption: Your Section

   YOUR_NEW_FILE
```

3. Commit and push - ReadTheDocs will rebuild automatically

### Adding New API Modules

New Python modules are auto-discovered if they have docstrings. To explicitly add:

1. Edit `docs/api/modules.rst`
2. Add module reference:

```rst
New Module
~~~~~~~~~~

.. automodule:: kicad_sch_api.your.new.module
   :members:
   :undoc-members:
   :show-inheritance:
```

## Troubleshooting

### Build Failures

Check ReadTheDocs build logs:
1. Go to https://readthedocs.org/projects/kicad-sch-api/
2. Click "Builds" tab
3. View latest build log

Common issues:
- Missing dependencies: Add to `pyproject.toml` under `[project.optional-dependencies.docs]`
- Import errors: Ensure module can be imported in build environment
- MyST errors: Check markdown syntax in `.md` files

### Local Build Warnings

Current build has ~28 warnings (mostly cross-reference anchors). These are cosmetic and don't affect functionality.

To reduce warnings:
- Fix internal cross-references in markdown files
- Add explicit anchor targets with `(anchor-name)=` syntax

### Documentation Not Updating

If changes aren't appearing:
1. Check ReadTheDocs build status
2. Clear browser cache
3. Trigger manual rebuild in ReadTheDocs dashboard

## Version Management

ReadTheDocs automatically builds:
- **Latest**: Development version from `main` branch
- **Stable**: Latest tagged release
- **Version-specific**: Each tag creates a versioned build

Example URLs:
- Latest: `https://kicad-sch-api.readthedocs.io/en/latest/`
- Stable: `https://kicad-sch-api.readthedocs.io/en/stable/`
- v0.4.0: `https://kicad-sch-api.readthedocs.io/en/v0.4.0/`

## Maintenance

### Updating Sphinx Configuration

Edit `docs/conf.py` to change:
- Theme settings
- Extension configuration
- Project metadata

### Updating ReadTheDocs Configuration

Edit `.readthedocs.yaml` to change:
- Python version
- Build commands
- Output formats

### Monitoring Build Status

Add ReadTheDocs badge to README.md:

```markdown
[![Documentation Status](https://readthedocs.org/projects/kicad-sch-api/badge/?version=latest)](https://kicad-sch-api.readthedocs.io/en/latest/?badge=latest)
```

## Resources

- [ReadTheDocs Documentation](https://docs.readthedocs.io/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Sphinx RTD Theme](https://sphinx-rtd-theme.readthedocs.io/)

---

**Status**: ✅ Fully configured and ready for ReadTheDocs deployment
**Next Step**: Import project on ReadTheDocs.org
