# KiCAD Schematic MCP Server - Installation Guide

Choose the installation method that works best for you:

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Setup Script

**For macOS/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.sh | bash
```

**For Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.ps1 | iex
```

This script will:
- ✅ Install the MCP server via pip
- ✅ Auto-configure Claude Code MCP settings
- ✅ Test the connection
- ✅ Display usage examples

---

## 📦 Manual Installation Options

### Option 2: PyPI Package (Coming Soon)

```bash
# Install the package
pip install kicad-sch-api

# Auto-configure Claude Code
kicad-sch-mcp --setup-claude-code

# Test installation
kicad-sch-mcp --test
```

### Option 3: Docker Container

```bash
# Pull and run the container
docker run -d --name kicad-mcp -p 3000:3000 circuitsynth/kicad-sch-api:latest

# Add to Claude Code settings:
{
  "kicad-sch-api": {
    "command": "docker",
    "args": ["exec", "kicad-mcp", "kicad-sch-mcp"],
    "env": {}
  }
}
```

### Option 4: From Source (Developers)

```bash
# Clone and install
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
pip install -e .

# Configure Claude Code
kicad-sch-mcp --setup-claude-code
```

---

## ⚙️ Claude Code Configuration

### Automatic Configuration (Recommended)
```bash
kicad-sch-mcp --setup-claude-code
```

### Manual Configuration
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

### Test the Installation
```bash
# Quick test
kicad-sch-mcp --test

# Create a test schematic
kicad-sch-mcp --demo
```

### In Claude Code
Ask Claude Code:
```
Create a simple schematic with a resistor and capacitor
```

If successful, you'll see Claude Code using the kicad-sch-api MCP tools.

---

## 🔧 Troubleshooting

### Common Issues

**"Command not found: kicad-sch-mcp"**
```bash
# Ensure pip bin directory is in PATH
pip show -f kicad-sch-api | grep Location
```

**"MCP server not responding"**
```bash
# Check server status
kicad-sch-mcp --status

# View logs
kicad-sch-mcp --logs
```

**"Component libraries not found"**
```bash
# Initialize component cache
kicad-sch-mcp --init-cache

# Check KiCAD installation
kicad-sch-mcp --check-kicad
```

### Get Help

- 📚 Documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/circuit-synth/kicad-sch-api/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/circuit-synth/kicad-sch-api/discussions)

---

## 🎯 Next Steps

Once installed:

1. **Learn the basics:** Check out the [Quick Start Guide](README.md#quick-start)
2. **Explore examples:** Try the [Common Circuit Patterns](README.md#examples)
3. **Build hierarchical designs:** Use the [Hierarchical Schematic Guide](HIERARCHICAL_GUIDE.md)
4. **Join the community:** Share your projects and get help

---

**Installation time: 2 minutes | Setup time: 30 seconds | Ready to design! 🚀**