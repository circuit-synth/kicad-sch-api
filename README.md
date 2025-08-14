# kicad-sch-api

**Professional KiCAD Schematic Manipulation Library with AI Agent Integration**


## 🚀 Key Features

- **📋 Exact Format Preservation**: Output matches KiCAD's native formatting exactly
- **⚡ High Performance**: Optimized for large schematics with symbol caching
- **🔧 Enhanced API**: Intuitive object-oriented interface with bulk operations
- **📚 Advanced Library Management**: Multi-source symbol lookup and caching
- **✅ Professional Validation**: Comprehensive error collection and reporting
- **🎯 KiCAD 9 Optimized**: Built specifically for latest KiCAD format

## 🆚 vs. Existing Solutions

| Feature | kicad-sch-api | kicad-skip | KiCAD Official API |
|---------|---------------|------------|-------------------|
| **Schematic Support** | ✅ Full | ✅ Full | ❌ PCB Only |
| **Format Preservation** | ✅ Exact | ❌ Basic | N/A |
| **Performance** | ✅ Optimized | ⚠️ Basic | N/A |
| **Library Management** | ✅ Advanced | ⚠️ Basic | N/A |
| **Runtime Dependencies** | ❌ None | ❌ None | ✅ KiCAD Required |

## 📦 Installation

```bash
# Install from PyPI (coming soon)
pip install kicad-sch-api

# Or install from source
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api/python
pip install -e .

npm install
npm run build
```

## 🎯 Quick Start

### Basic Schematic Manipulation

```python
import kicad_sch_api as ksa

# Create new schematic
sch = ksa.create_schematic('My Circuit')

# Add components
resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
capacitor = sch.components.add('Device:C', reference='C1', value='0.1uF', position=(150, 100))

# Update properties
resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
resistor.set_property('MPN', 'RC0603FR-0710KL')

# Save with exact format preservation
sch.save('my_circuit.kicad_sch')
```

### Advanced Operations

```python
# Bulk operations for large schematics
resistors = sch.components.filter(lib_id='Device:R')
for r in resistors:
    r.set_property('Tolerance', '1%')

# Search and analysis
power_components = sch.components.in_area(0, 0, 50, 50)
high_value_resistors = sch.components.filter(
    lib_id='Device:R', 
    value_pattern='*k'  # Components with 'k' in value
)

# Validation and error checking
issues = sch.validate()
if issues:
    print(f"Found {len(issues)} validation issues:")
    for issue in issues:
        print(f"  {issue}")

# Performance statistics
stats = sch.get_performance_stats()
print(f"Cache hit rate: {stats['symbol_cache']['hit_rate_percent']}%")
```



```json
{
  "kicad-sch": {
    "command": "node",
    "env": {
      "PYTHON_PATH": "python3",
      "KICAD_SCH_API_PATH": "/path/to/kicad-sch-api/python"
    }
  }
}
```

Then use natural language with your AI agent:

```
User: "Create a voltage divider circuit with two 10k resistors"

Claude: I'll create a voltage divider circuit for you.

1. Create new schematic
2. Add R1 (10k resistor) at (100, 100)
3. Add R2 (10k resistor) at (100, 150) 
4. Connect components with wires
5. Add voltage input and output labels
6. Save schematic with exact formatting

Your voltage divider circuit is ready! The circuit provides 50% voltage division
with two 10kΩ resistors in series configuration.
```

## 🏗️ Architecture

The library consists of two main components:

### Python Library (Core)
- **Enhanced Object Model**: Intuitive API with fast component collections
- **Exact Format Preservation**: S-expression writer that matches KiCAD output
- **Symbol Caching**: High-performance library symbol management
- **Comprehensive Validation**: Error collection and professional reporting

- **Python Bridge**: Reliable subprocess communication
- **Comprehensive Tools**: 15+ tools for complete schematic manipulation
- **Professional Error Handling**: Detailed error context for AI agents

## 🧪 Testing & Quality

```bash
# Python tests
cd python
python -m pytest tests/ -v --cov=kicad_sch_api

npm test

# Format preservation tests
python -m pytest tests/test_format_preservation.py -v
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)**: Comprehensive circuit design automation
- **[kicad-skip](https://github.com/psychogenic/kicad-skip)**: Foundation S-expression parser

---

**Built with ❤️ by the Circuit-Synth team**
