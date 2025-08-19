# KiCAD Schematic MCP Server

**Professional KiCAD Schematic Manipulation with Claude Code Integration**

Transform natural language into professional KiCAD schematics using AI. This MCP (Model Context Protocol) server provides Claude Code with powerful tools for creating, editing, and managing KiCAD schematic files with exact format preservation.

## 🚀 Quick Start - One Command Installation

**For macOS/Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.sh | bash
```

**For Windows (PowerShell):**
```powershell
iwr -useb https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.ps1 | iex
```

**⏱️ Installation time: 2 minutes | Setup time: 30 seconds | Ready to design! 🚀**

## 📋 Prerequisites

- **KiCAD 8.0+** installed (for component symbol libraries)
- **Claude Code** installed ([download here](https://claude.ai/code))
- **Python 3.8+** (automatically handled by installation script)

## ✨ What You Get

After installation, use natural language in Claude Code to:

```
"Create a voltage divider with two 10kΩ resistors"
"Add an ESP32 microcontroller with USB connector" 
"Generate a hierarchical schematic with power supply subcircuit"
"Export component list with manufacturer part numbers"
```

## 🎯 Key Features

- **🤖 AI-Native**: Built specifically for Claude Code integration
- **📋 Exact Format Preservation**: Output matches KiCAD's native formatting exactly
- **⚡ High Performance**: Optimized for large schematics with intelligent caching
- **🏗️ Hierarchical Design**: Full support for complex multi-sheet schematics
- **📚 Component Discovery**: Intelligent search across 13,000+ KiCAD symbols
- **🔍 Advanced Analysis**: Component filtering, area selection, and validation
- **✅ Professional Quality**: Comprehensive error handling and reporting

## 🆚 vs. Existing Solutions

| Feature | kicad-sch-api | Other Solutions | KiCAD Native |
|---------|---------------|-----------------|--------------|
| **AI Integration** | ✅ Claude Code | ❌ None | ❌ None |
| **Format Preservation** | ✅ Exact | ⚠️ Basic | ✅ Native |
| **Component Discovery** | ✅ 13,000+ | ⚠️ Limited | ⚠️ Manual |
| **Hierarchical Support** | ✅ Complete | ⚠️ Varies | ✅ Native |
| **Performance** | ✅ Optimized | ⚠️ Basic | ⚠️ GUI Only |
| **Automation** | ✅ Full API | ❌ None | ⚠️ Limited |

## 📦 Installation Options

Choose the method that works best for you:

### 🚀 Option 1: One-Click Setup (Recommended)

The installation script automatically:
- ✅ Installs the MCP server via pip
- ✅ Configures Claude Code MCP settings
- ✅ Tests the connection
- ✅ Displays usage examples

### 🐳 Option 2: Docker Container

```bash
# Pull and run the container
docker run -d --name kicad-mcp -p 3000:3000 circuitsynth/kicad-sch-api:latest
```

### 🛠️ Option 3: From Source (Developers)

```bash
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
pip install -e .
kicad-sch-api --setup-claude-code
```

### 📦 Option 4: PyPI Package

```bash
pip install kicad-sch-api
kicad-sch-api --setup-claude-code
```

## 🎯 Quick Start Examples

### Basic Circuit Creation

Ask Claude Code:
```
Create a simple LED circuit with a 220Ω current limiting resistor
```

Claude Code will:
1. Create a new schematic file
2. Add LED component from Device library  
3. Add 220Ω resistor with proper footprint
4. Connect components with hierarchical labels (no messy wires!)
5. Add power supply connections
6. Save with exact KiCAD formatting

**Note**: Our enhanced AI guidance uses hierarchical labels instead of wires for cleaner, professional schematics.

### Advanced Hierarchical Design

```
Design a microcontroller board with separate power supply and USB interface subcircuits
```

Claude Code will:
1. Create main schematic with hierarchical sheets
2. Generate power supply subcircuit with regulators
3. Create USB interface subcircuit with connectors
4. Add inter-sheet connections and labels
5. Export complete project with proper hierarchy

### Component Discovery and Analysis

```
Find all operational amplifiers in the project and update their footprints to SOIC-8
```

Claude Code will:
1. Search through all schematic sheets
2. Identify op-amp components by symbol library
3. Update footprint properties systematically
4. Generate change report with before/after comparison

## 🔧 Available MCP Tools

The MCP server provides Claude Code with 15+ tools for complete schematic manipulation:

| Tool Category | Available Tools |
|---------------|-----------------|
| **Creation** | `create_schematic`, `add_component`, `add_hierarchical_label` |
| **Hierarchical** | `add_hierarchical_sheet`, `add_sheet_pin`, `load_schematic` |
| **Discovery** | `search_components`, `list_available_symbols`, `validate_component` |
| **Analysis** | `list_components`, `get_schematic_info`, `browse_library` |
| **Export** | `save_schematic`, `export_netlist`, `generate_bom` |

**Enhanced AI Guidance**: Each tool includes comprehensive design rules and professional guidance to ensure clean, industry-standard schematics.

## ⚙️ Configuration

### Automatic Configuration (Recommended)
```bash
kicad-sch-api --setup-claude-code
```

### Manual Configuration
Add to your Claude Code MCP settings:

**File Location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%/Claude/claude_desktop_config.json`  
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

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

## ✅ Verification

### Test Installation
```bash
kicad-sch-api --test
kicad-sch-api --demo
```

### In Claude Code
Ask Claude Code:
```
Test the KiCAD MCP server by creating a simple resistor circuit
```

If successful, you'll see Claude Code using the kicad-sch-api tools to create schematics.

## 🤖 How the MCP Server Works

### **What is MCP?**
The Model Context Protocol (MCP) allows AI agents like Claude Code to use external tools. Our MCP server gives Claude Code direct access to KiCAD schematic manipulation capabilities.

### **Enhanced AI Guidance**
Unlike basic tools, our MCP server includes comprehensive AI guidance:

- **🚫 Wire-free Design**: AI defaults to hierarchical labels for clean schematics
- **📏 Proper Sizing**: Hierarchical sheets sized correctly (60x40 to 100x60)  
- **🔍 Component Validation**: Automatic "?" reference fixing and component validation
- **📋 Professional Standards**: Industry-standard footprints and component values
- **⚡ Smart Defaults**: Grid-aligned positioning and proper spacing

### **User Experience**
1. **Natural Language**: You speak normally to Claude Code
2. **AI Translation**: Claude Code uses our MCP tools to manipulate KiCAD files  
3. **Professional Output**: You get clean, industry-standard schematics
4. **Exact Format**: Output matches KiCAD native formatting perfectly

**Example Workflow:**
```
You: "Create a voltage divider"
AI: Uses create_schematic() → add_component() → add_hierarchical_label() → save_schematic()
Result: Professional KiCAD file with proper references, clean layout, no wire mess
```

## 🐍 Python API Usage

For developers who want to use the core library directly:

```python
import kicad_sch_api as ksa

# Create new schematic
sch = ksa.create_schematic("My Circuit")

# Add components with all properties
sch.components.add(
    lib_id="Device:R",
    reference="R1", 
    value="10k",
    position=(100.0, 100.0),
    footprint="Resistor_SMD:R_0603_1608Metric",
    datasheet="~",
    description="Resistor"
)

# Add second component  
sch.components.add(
    lib_id="Device:C",
    reference="C1", 
    value="100nF",
    position=(150.0, 100.0),
    footprint="Capacitor_SMD:C_0603_1608Metric"
)

# Save schematic
sch.save("my_circuit.kicad_sch")
```

**Key Points:**
- Use `sch.components.add()` with named parameters
- Positions are tuples of floats: `(100.0, 100.0)`
- All properties specified in single call (no separate assignment)
- Footprint included as parameter, not property assignment

## 🏗️ Architecture

### Core Python Library
- **Enhanced Object Model**: Intuitive API with fast component collections
- **Exact Format Preservation**: S-expression writer that matches KiCAD output
- **Symbol Caching**: High-performance library symbol management
- **Comprehensive Validation**: Error collection and professional reporting

### MCP Server Integration
- **Claude Code Tools**: 15+ tools for complete schematic manipulation
- **Professional Error Handling**: Detailed error context for AI agents
- **Component Discovery**: SQLite-indexed search across KiCAD libraries
- **Hierarchical Support**: Full multi-sheet schematic capabilities

## 🧪 Testing & Quality

```bash
# Test the MCP server
kicad-sch-mcp --test

# Run comprehensive tests
uv run pytest tests/ -v

# Format preservation tests (critical)
uv run pytest tests/reference_tests/ -v

# Run specific reference tests
uv run pytest tests/reference_tests/test_single_resistor.py -v
uv run pytest tests/reference_tests/test_resistor_divider.py -v

# Code quality checks
uv run black kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
uv run flake8 kicad_sch_api/ tests/
```

## 🔧 Troubleshooting

### Common Issues

**"Command not found: kicad-sch-mcp"**
```bash
# Check installation status
kicad-sch-api --status

# Add to PATH permanently
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"
```

**"Component libraries not found"**
```bash
# Initialize component cache
kicad-sch-api --init-cache

# Check KiCAD installation
kicad-sch-api --check-kicad
```

**"MCP server not responding"**
```bash
# View server logs
kicad-sch-api --logs

# Test server startup
kicad-sch-mcp --debug
```

## 🤝 Contributing

We welcome contributions! See [INSTALLATION.md](INSTALLATION.md) for setup details and [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas for contribution:
- Additional KiCAD symbol library support
- Enhanced component discovery algorithms
- Performance optimizations for large schematics
- New MCP tools and capabilities

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)**: Comprehensive circuit design automation
- **[Claude Code](https://claude.ai/code)**: AI-powered development environment
- **[MCP](https://modelcontextprotocol.io/)**: Model Context Protocol for AI tool integration

---

**Transform ideas into schematics with AI ⚡ Built with ❤️ by the Circuit-Synth team**