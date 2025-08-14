# KiCAD-SCH-API MCP Server Integration Plan

## Executive Summary

Adding a Model Context Protocol (MCP) server to kicad-sch-api will create a powerful interface for AI agents to manipulate KiCAD schematics. This combines the best of both worlds: kicad-sch-api's professional schematic manipulation with the proven MCP interface that agents already understand.

## MCP Server Architecture

### High-Level Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ AI Agent        │────│ MCP Server       │────│ kicad-sch-api   │
│ (Claude/GPT)    │    │ (TypeScript)     │    │ (Python)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────────┐     ┌─────────────────┐    ┌─────────────────┐
    │ Natural     │     │ JSON-RPC        │    │ KiCAD .kicad_sch│
    │ Language    │     │ Protocol        │    │ Files           │
    └─────────────┘     └─────────────────┘    └─────────────────┘
```

### Project Structure

```
kicad-sch-api/
├── python/                      # Core kicad-sch-api library
│   ├── kicad_sch_api/
│   └── setup.py
├── mcp-server/                  # MCP server implementation
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts            # Main MCP server
│   │   ├── schematic-tools.ts  # Schematic manipulation tools
│   │   ├── python-bridge.ts    # Python subprocess management
│   │   └── types.ts            # TypeScript type definitions
│   └── dist/                   # Compiled JavaScript
└── examples/                   # Integration examples
    ├── claude-desktop-config.json
    └── agent-workflows/
```

## MCP Tools Specification

### Core Schematic Tools

#### **1. Schematic Management**

```typescript
// Load and save schematics
{
  name: "load_schematic",
  description: "Load a KiCAD schematic file for manipulation",
  inputSchema: {
    type: "object",
    properties: {
      file_path: { type: "string", description: "Path to .kicad_sch file" }
    }
  }
}

{
  name: "save_schematic", 
  description: "Save schematic with exact format preservation",
  inputSchema: {
    type: "object",
    properties: {
      file_path: { type: "string", description: "Output file path" },
      preserve_format: { type: "boolean", default: true }
    }
  }
}
```

#### **2. Component Operations**

```typescript
{
  name: "add_component",
  description: "Add a component to the schematic",
  inputSchema: {
    type: "object",
    properties: {
      lib_id: { type: "string", description: "Library ID (e.g., 'Device:R')" },
      reference: { type: "string", description: "Component reference (e.g., 'R1')" },
      value: { type: "string", description: "Component value (e.g., '10k')" },
      position: {
        type: "object",
        properties: {
          x: { type: "number" },
          y: { type: "number" }
        }
      },
      properties: { 
        type: "object", 
        description: "Additional properties (footprint, MPN, etc.)"
      }
    }
  }
}

{
  name: "update_component",
  description: "Update component properties or position", 
  inputSchema: {
    type: "object",
    properties: {
      reference: { type: "string" },
      updates: {
        type: "object",
        properties: {
          value: { type: "string" },
          position: { type: "object" },
          properties: { type: "object" }
        }
      }
    }
  }
}

{
  name: "remove_component",
  description: "Remove component from schematic",
  inputSchema: {
    type: "object", 
    properties: {
      reference: { type: "string", description: "Component reference to remove" }
    }
  }
}
```

#### **3. Connection Management**

```typescript
{
  name: "add_wire",
  description: "Add wire connection between two points",
  inputSchema: {
    type: "object",
    properties: {
      start: {
        type: "object",
        properties: {
          x: { type: "number" },
          y: { type: "number" }
        }
      },
      end: {
        type: "object", 
        properties: {
          x: { type: "number" },
          y: { type: "number" }
        }
      }
    }
  }
}

{
  name: "connect_components",
  description: "Connect two component pins with wire",
  inputSchema: {
    type: "object",
    properties: {
      from_component: { type: "string", description: "Source component reference" },
      from_pin: { type: "string", description: "Source pin name/number" },
      to_component: { type: "string", description: "Target component reference" },
      to_pin: { type: "string", description: "Target pin name/number" }
    }
  }
}
```

#### **4. Analysis and Search**

```typescript
{
  name: "find_components",
  description: "Search for components by various criteria",
  inputSchema: {
    type: "object",
    properties: {
      reference_pattern: { type: "string" },
      value_pattern: { type: "string" },
      lib_id_pattern: { type: "string" },
      within_area: {
        type: "object",
        properties: {
          x1: { type: "number" },
          y1: { type: "number" },
          x2: { type: "number" },
          y2: { type: "number" }
        }
      }
    }
  }
}

{
  name: "analyze_connections",
  description: "Analyze electrical connections and nets",
  inputSchema: {
    type: "object",
    properties: {
      component_reference: { type: "string", description: "Component to analyze connections for" }
    }
  }
}

{
  name: "validate_schematic",
  description: "Validate schematic for errors and issues",
  inputSchema: {
    type: "object",
    properties: {
      check_types: {
        type: "array",
        items: { 
          type: "string",
          enum: ["electrical", "syntax", "references", "connections"]
        }
      }
    }
  }
}
```

### Advanced Tools

#### **5. Library Integration**

```typescript
{
  name: "search_component_library",
  description: "Search for components across multiple sources",
  inputSchema: {
    type: "object",
    properties: {
      query: { type: "string", description: "Component search query" },
      sources: {
        type: "array",
        items: { type: "string", enum: ["local", "digikey", "snapeda"] }
      },
      filters: {
        type: "object",
        properties: {
          package: { type: "string" },
          value_range: { type: "object" },
          in_stock: { type: "boolean" }
        }
      }
    }
  }
}
```

#### **6. Batch Operations**

```typescript
{
  name: "batch_update_components",
  description: "Update multiple components with same changes",
  inputSchema: {
    type: "object",
    properties: {
      selection_criteria: {
        type: "object",
        properties: {
          reference_pattern: { type: "string" },
          value_pattern: { type: "string" }
        }
      },
      updates: {
        type: "object",
        description: "Properties to update on all matching components"
      }
    }
  }
}
```

## Python Bridge Implementation

### Subprocess Management

```typescript
// python-bridge.ts
class PythonBridge {
  private pythonProcess: ChildProcess | null = null;
  private commandQueue: Map<string, Promise<any>> = new Map();
  
  async executeCommand(command: string, params: any): Promise<any> {
    const requestId = uuidv4();
    
    const request = {
      id: requestId,
      command: command,
      params: params
    };
    
    // Send to Python process via stdin
    this.pythonProcess?.stdin?.write(JSON.stringify(request) + '\n');
    
    // Return promise that resolves when response received
    return new Promise((resolve, reject) => {
      this.commandQueue.set(requestId, { resolve, reject });
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.commandQueue.has(requestId)) {
          this.commandQueue.delete(requestId);
          reject(new Error('Command timeout'));
        }
      }, 30000);
    });
  }
}
```

### Python Command Handler

```python
# python/kicad_sch_api/mcp_interface.py
import json
import sys
import logging
from typing import Dict, Any
from .core import SchematicDocument

class MCPInterface:
    def __init__(self):
        self.current_schematic: Optional[SchematicDocument] = None
        self.command_handlers = {
            'load_schematic': self.load_schematic,
            'save_schematic': self.save_schematic,
            'add_component': self.add_component,
            'update_component': self.update_component,
            'remove_component': self.remove_component,
            'add_wire': self.add_wire,
            'find_components': self.find_components,
            # ... more handlers
        }
    
    def load_schematic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            file_path = params['file_path']
            self.current_schematic = SchematicDocument.load(file_path)
            return {
                'success': True,
                'message': f'Loaded schematic: {file_path}',
                'component_count': len(self.current_schematic.components),
                'wire_count': len(self.current_schematic.wires)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_commands(self):
        """Main command processing loop"""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                command = request.get('command')
                params = request.get('params', {})
                request_id = request.get('id')
                
                if command in self.command_handlers:
                    result = self.command_handlers[command](params)
                    response = {
                        'id': request_id,
                        'result': result
                    }
                else:
                    response = {
                        'id': request_id,
                        'error': f'Unknown command: {command}'
                    }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except Exception as e:
                logging.error(f'Error processing command: {e}')
                error_response = {
                    'id': request.get('id') if 'request' in locals() else None,
                    'error': str(e)
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == '__main__':
    interface = MCPInterface()
    interface.process_commands()
```

## Agent Workflow Examples

### Example 1: LED Circuit Creation

```typescript
// Agent workflow: "Create a simple LED circuit with current limiting resistor"

// 1. Load or create new schematic
await mcp.callTool("load_schematic", {
  file_path: "/tmp/led_circuit.kicad_sch"
});

// 2. Add LED component
await mcp.callTool("add_component", {
  lib_id: "Device:LED",
  reference: "D1", 
  value: "Red",
  position: { x: 100, y: 100 },
  properties: {
    footprint: "LED_SMD:LED_0603_1608Metric"
  }
});

// 3. Add current limiting resistor  
await mcp.callTool("add_component", {
  lib_id: "Device:R",
  reference: "R1",
  value: "330",
  position: { x: 50, y: 100 },
  properties: {
    footprint: "Resistor_SMD:R_0603_1608Metric"
  }
});

// 4. Connect resistor to LED
await mcp.callTool("connect_components", {
  from_component: "R1",
  from_pin: "2", 
  to_component: "D1",
  to_pin: "A"
});

// 5. Save with format preservation
await mcp.callTool("save_schematic", {
  file_path: "/tmp/led_circuit.kicad_sch",
  preserve_format: true
});
```

### Example 2: Component Analysis and Updates

```typescript
// Agent workflow: "Find all 0603 resistors and update their footprints"

// 1. Find components matching criteria
const resistors = await mcp.callTool("find_components", {
  lib_id_pattern: "Device:R",
  properties: {
    footprint: "*0603*"
  }
});

// 2. Batch update footprints to more specific variant
await mcp.callTool("batch_update_components", {
  selection_criteria: {
    reference_pattern: "R[0-9]+"
  },
  updates: {
    properties: {
      footprint: "Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder"
    }
  }
});

// 3. Validate changes
const validation = await mcp.callTool("validate_schematic", {
  check_types: ["references", "footprints"]
});
```

## Integration with Claude Desktop

### Configuration Example

```json
// claude-desktop-config.json
{
  "kicad-sch": {
    "command": "node",
    "args": ["/path/to/kicad-sch-api/mcp-server/dist/index.js"],
    "env": {
      "PYTHON_PATH": "/path/to/kicad-sch-api/python",
      "DEBUG": "mcp:*"
    }
  }
}
```

### Usage in Claude

```
User: "Create a voltage divider circuit with two 10k resistors"

Claude: I'll create a voltage divider circuit for you using the kicad-sch-api.

[Uses MCP tools to:]
1. Load/create schematic
2. Add two 10k resistors (R1, R2) 
3. Position them vertically
4. Add connection wires
5. Add voltage input and output labels
6. Save the schematic

The voltage divider circuit has been created with:
- R1: 10kΩ resistor (input side)
- R2: 10kΩ resistor (ground side)  
- Proper connections for 50% voltage division
- Standard SMD footprints assigned
```

## Benefits of MCP Integration

### For AI Agents
- **Standardized Interface**: Uses proven MCP protocol agents already understand
- **Rich Tool Set**: Comprehensive schematic manipulation capabilities
- **Professional Output**: Format-preserving operations for production use
- **Error Handling**: Robust error reporting and validation

### For Developers  
- **Language Agnostic**: Agents can use any language that supports MCP
- **Tool Ecosystem**: Integrates with existing MCP tool chains
- **Extensible**: Easy to add new tools and capabilities
- **Documented**: Self-documenting tools with JSON schemas

### For Circuit Design
- **AI-Assisted Design**: Natural language to schematic generation
- **Batch Operations**: Efficient bulk component updates
- **Design Validation**: Automated error checking and analysis  
- **Library Integration**: Smart component selection and sourcing

## Development Timeline

### Phase 1: Core MCP Server (Weeks 1-3)
- [ ] Basic MCP server setup with TypeScript
- [ ] Python bridge implementation  
- [ ] Essential tools (load, save, add/remove components)
- [ ] Error handling and validation

### Phase 2: Advanced Tools (Weeks 4-6)
- [ ] Connection management tools
- [ ] Search and analysis capabilities
- [ ] Batch operation tools
- [ ] Library integration tools

### Phase 3: Professional Features (Weeks 7-8)
- [ ] Comprehensive validation and error reporting
- [ ] Performance optimization
- [ ] Documentation and examples
- [ ] Integration testing with Claude

This MCP server integration will make kicad-sch-api incredibly powerful for AI-assisted circuit design, combining professional-grade schematic manipulation with the natural language interface that makes AI agents so effective.