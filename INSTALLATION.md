# KiCAD Schematic API - Installation Guide

## 🚀 Quick Start (Recommended)

### Python Package Installation

```bash
# Install the package
pip install kicad-sch-api

# Test installation
python -c "import kicad_sch_api as ksa; print('Installation successful!')"
```

### Development Installation

```bash
# Clone and install
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api/python
uv pip install -e .
```

---

## 🤖 AI Agent Integration (MCP Server)

### MCP Server Setup  
The library includes an optional MCP server for AI agent integration:

```bash
# Install with MCP support
pip install kicad-sch-api[mcp]

# Test MCP server
kicad-sch-mcp --test
```

### Claude Code Configuration
Add this to your Claude Code MCP settings file:

**Location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`  
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "kicad-sch-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

---

## ✅ Verification

### Test Python Library
```python
import kicad_sch_api as ksa

# Create a simple schematic
sch = ksa.create_schematic("Test Circuit")
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k", 
    position=(100, 100)
)
sch.save("test.kicad_sch")
print("Library working correctly!")
```

### Test MCP Server (if installed)
Ask your AI agent:
```
Create a simple schematic with a resistor and capacitor
```

If successful, you'll see the AI agent using the kicad-sch-api MCP tools.

---

## 🔧 Troubleshooting

### Common Issues

**"Module not found: kicad_sch_api"**
```bash
# Verify installation
pip list | grep kicad-sch-api

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

**"MCP server not responding"**
```bash
# Test server directly
python run_mcp_server.py

# Check for port conflicts or permission issues
```

**"Component libraries not found"**
- Ensure KiCAD is installed and libraries are accessible
- Check KiCAD library paths in system preferences

### Get Help

- 📚 Documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/circuit-synth/kicad-sch-api/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/circuit-synth/kicad-sch-api/discussions)

---

## 🎯 Next Steps

Once installed:

1. **Learn the basics:** Check out the [README.md](README.md) quick start guide
2. **Explore examples:** Try the [examples/](examples/) directory
3. **Build hierarchical designs:** Use hierarchical sheets for complex projects
4. **AI Integration:** Set up the MCP server for AI agent integration
5. **Join the community:** Share your projects and get help on GitHub

---

**Python library: Ready to use! | MCP server: Optional for AI agents 🚀**