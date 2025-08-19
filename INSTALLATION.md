# KiCAD Schematic API - Installation Guide

## 🚀 New! Daemon-Style Setup (Recommended)

**For best performance - persistent background MCP server:**

```bash
# Install and setup with daemon-style MCP server
pip install 'kicad-sch-api[mcp]' && kicad-sch-api --setup-daemon
```

**✨ What's new with daemon mode:**
- 🚀 **Persistent**: MCP server runs in background, no restart needed
- ⚡ **Fast**: Better performance, no startup delays
- 🔒 **Reliable**: No PATH issues or virtual environment problems
- 🛠️ **Manageable**: Easy start/stop/restart controls

**Daemon Management:**
```bash
kicad-sch-api --daemon-status     # Check if daemon is running
kicad-sch-api --start-daemon      # Start daemon
kicad-sch-api --stop-daemon       # Stop daemon  
kicad-sch-api --restart-daemon    # Restart daemon
```

After setup, just restart Claude Code and try:
```
"Create a voltage divider with two 10kΩ resistors"
```

---

## 📦 Legacy Setup (Still Works)

**Traditional setup method:**

```bash
# Install and setup everything automatically
pip install 'kicad-sch-api[mcp]' && kicad-sch-api --setup
```

**What this does:**
- ✅ Install the Python library
- ✅ Install MCP server for AI agents  
- ✅ Configure Claude Code automatically
- ✅ Initialize component cache
- ✅ Create a demo schematic
- ✅ Test everything works

---

## 📋 Manual Installation (Advanced Users)

### Python Library Only
```bash
# Just the Python library
pip install kicad-sch-api

# Test basic functionality
python -c "import kicad_sch_api as ksa; print('✅ Library working!')"
```

### With AI Agent Support
```bash
# Library + MCP server for AI agents
pip install kicad-sch-api[mcp]

# One-command setup
kicad-sch-api --setup

# Or manual setup
kicad-sch-api --setup-claude-code
kicad-sch-mcp --test
```

### Development Installation
```bash
# Clone and install from source
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
uv pip install -e .[mcp]
kicad-sch-api --setup
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