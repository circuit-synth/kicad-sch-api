/**
 * KiCAD Schematic MCP Tools
 * 
 * This module defines all the MCP tools available for AI agents to manipulate
 * KiCAD schematic files through the kicad-sch-api library.
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { PythonBridge } from './python-bridge.js';
import { MCPLogger } from './logger.js';

// Zod schemas for tool input validation
const PositionSchema = z.object({
  x: z.number(),
  y: z.number(),
});

const ComponentSchema = z.object({
  lib_id: z.string().describe('Library identifier (e.g., "Device:R")'),
  reference: z.string().optional().describe('Component reference (e.g., "R1")'),
  value: z.string().optional().describe('Component value (e.g., "10k")'),
  position: PositionSchema.optional().describe('Component position in mm'),
  footprint: z.string().optional().describe('Component footprint'),
  properties: z.record(z.string()).optional().describe('Additional properties'),
});

const SearchCriteriaSchema = z.object({
  lib_id: z.string().optional(),
  reference_pattern: z.string().optional(),
  value_pattern: z.string().optional(),
  footprint: z.string().optional(),
  in_area: z.tuple([z.number(), z.number(), z.number(), z.number()]).optional(),
  has_property: z.string().optional(),
});

export class SchematicTools {
  private pythonBridge: PythonBridge;
  private logger: MCPLogger;
  private tools: Map<string, Tool>;

  constructor(pythonBridge: PythonBridge, logger: MCPLogger) {
    this.pythonBridge = pythonBridge;
    this.logger = logger;
    this.tools = new Map();
    this.initializeTools();
  }

  private initializeTools(): void {
    // File operations
    this.registerTool({
      name: 'load_schematic',
      description: 'Load a KiCAD schematic file for manipulation',
      inputSchema: {
        type: 'object',
        properties: {
          file_path: {
            type: 'string',
            description: 'Path to .kicad_sch file to load',
          },
        },
        required: ['file_path'],
      },
    });

    this.registerTool({
      name: 'save_schematic',
      description: 'Save the current schematic to file with exact format preservation',
      inputSchema: {
        type: 'object',
        properties: {
          file_path: {
            type: 'string',
            description: 'Output file path (optional, uses current path if not specified)',
          },
          preserve_format: {
            type: 'boolean',
            description: 'Whether to preserve exact formatting (default: true)',
            default: true,
          },
        },
      },
    });

    this.registerTool({
      name: 'create_schematic',
      description: 'Create a new empty schematic',
      inputSchema: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'Schematic name for title block',
            default: 'New Circuit',
          },
        },
      },
    });

    // Component operations
    this.registerTool({
      name: 'add_component',
      description: 'Add a component to the schematic',
      inputSchema: {
        type: 'object',
        properties: {
          lib_id: {
            type: 'string',
            description: 'Library identifier (e.g., "Device:R" for resistor)',
          },
          reference: {
            type: 'string',
            description: 'Component reference (e.g., "R1"). Auto-generated if not provided.',
          },
          value: {
            type: 'string',
            description: 'Component value (e.g., "10k" for 10k ohm resistor)',
          },
          position: {
            type: 'object',
            properties: {
              x: { type: 'number', description: 'X coordinate in mm' },
              y: { type: 'number', description: 'Y coordinate in mm' },
            },
            description: 'Component position. Auto-placed if not provided.',
          },
          footprint: {
            type: 'string',
            description: 'Component footprint (e.g., "Resistor_SMD:R_0603_1608Metric")',
          },
          properties: {
            type: 'object',
            description: 'Additional component properties (MPN, Datasheet, etc.)',
          },
        },
        required: ['lib_id'],
      },
    });

    this.registerTool({
      name: 'update_component',
      description: 'Update properties of an existing component',
      inputSchema: {
        type: 'object',
        properties: {
          reference: {
            type: 'string',
            description: 'Component reference to update',
          },
          value: {
            type: 'string',
            description: 'New component value',
          },
          position: {
            type: 'object',
            properties: {
              x: { type: 'number' },
              y: { type: 'number' },
            },
            description: 'New position',
          },
          footprint: {
            type: 'string',
            description: 'New footprint',
          },
          properties: {
            type: 'object',
            description: 'Properties to update',
          },
        },
        required: ['reference'],
      },
    });

    this.registerTool({
      name: 'remove_component', 
      description: 'Remove a component from the schematic',
      inputSchema: {
        type: 'object',
        properties: {
          reference: {
            type: 'string',
            description: 'Component reference to remove',
          },
        },
        required: ['reference'],
      },
    });

    this.registerTool({
      name: 'get_component',
      description: 'Get detailed information about a component',
      inputSchema: {
        type: 'object',
        properties: {
          reference: {
            type: 'string',
            description: 'Component reference to get information for',
          },
        },
        required: ['reference'],
      },
    });

    this.registerTool({
      name: 'find_components',
      description: 'Search for components by various criteria',
      inputSchema: {
        type: 'object',
        properties: {
          lib_id: {
            type: 'string',
            description: 'Filter by library ID (e.g., "Device:R")',
          },
          reference_pattern: {
            type: 'string',
            description: 'Filter by reference pattern (regex)',
          },
          value_pattern: {
            type: 'string',
            description: 'Filter by value pattern (contains)',
          },
          footprint: {
            type: 'string',
            description: 'Filter by footprint',
          },
          in_area: {
            type: 'array',
            items: { type: 'number' },
            minItems: 4,
            maxItems: 4,
            description: 'Filter by area [x1, y1, x2, y2] in mm',
          },
          has_property: {
            type: 'string',
            description: 'Filter by presence of property',
          },
        },
      },
    });

    // Connection operations
    this.registerTool({
      name: 'add_wire',
      description: 'Add a wire connection between two points',
      inputSchema: {
        type: 'object',
        properties: {
          start: {
            type: 'object',
            properties: {
              x: { type: 'number' },
              y: { type: 'number' },
            },
            required: ['x', 'y'],
            description: 'Start point in mm',
          },
          end: {
            type: 'object', 
            properties: {
              x: { type: 'number' },
              y: { type: 'number' },
            },
            required: ['x', 'y'],
            description: 'End point in mm',
          },
        },
        required: ['start', 'end'],
      },
    });

    this.registerTool({
      name: 'connect_components',
      description: 'Connect two component pins with a wire',
      inputSchema: {
        type: 'object',
        properties: {
          from_component: {
            type: 'string',
            description: 'Source component reference',
          },
          from_pin: {
            type: 'string',
            description: 'Source pin number',
          },
          to_component: {
            type: 'string',
            description: 'Target component reference',
          },
          to_pin: {
            type: 'string',
            description: 'Target pin number',
          },
        },
        required: ['from_component', 'from_pin', 'to_component', 'to_pin'],
      },
    });

    // Bulk operations  
    this.registerTool({
      name: 'bulk_update_components',
      description: 'Update multiple components matching criteria',
      inputSchema: {
        type: 'object',
        properties: {
          criteria: {
            type: 'object',
            description: 'Component selection criteria',
            properties: {
              lib_id: { type: 'string' },
              reference_pattern: { type: 'string' },
              value_pattern: { type: 'string' },
              footprint: { type: 'string' },
            },
          },
          updates: {
            type: 'object',
            description: 'Updates to apply to matching components',
            properties: {
              value: { type: 'string' },
              footprint: { type: 'string' },
              properties: { type: 'object' },
            },
          },
        },
        required: ['criteria', 'updates'],
      },
    });

    // Analysis and validation
    this.registerTool({
      name: 'validate_schematic',
      description: 'Validate schematic for errors and issues',
      inputSchema: {
        type: 'object',
        properties: {
          check_types: {
            type: 'array',
            items: {
              type: 'string',
              enum: ['syntax', 'references', 'connections', 'libraries'],
            },
            description: 'Types of validation to perform',
            default: ['syntax', 'references'],
          },
        },
      },
    });

    this.registerTool({
      name: 'get_schematic_summary',
      description: 'Get summary information about the loaded schematic',
      inputSchema: {
        type: 'object',
        properties: {},
      },
    });

    // Library operations
    this.registerTool({
      name: 'search_library_symbols',
      description: 'Search for symbols in component libraries',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query (component name, description, keywords)',
          },
          library: {
            type: 'string',
            description: 'Specific library to search (optional)',
          },
          limit: {
            type: 'number',
            description: 'Maximum number of results',
            default: 20,
          },
        },
        required: ['query'],
      },
    });

    this.registerTool({
      name: 'add_library_path',
      description: 'Add a custom symbol library path',
      inputSchema: {
        type: 'object',
        properties: {
          library_path: {
            type: 'string',
            description: 'Path to .kicad_sym library file',
          },
        },
        required: ['library_path'],
      },
    });

    this.logger.info(`Registered ${this.tools.size} MCP tools`);
  }

  private registerTool(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }

  getToolDefinitions(): Tool[] {
    return Array.from(this.tools.values());
  }

  hasUnknownTool(name: string): boolean {
    return this.tools.has(name);
  }

  async executeTool(name: string, args: Record<string, unknown>): Promise<any> {
    // Delegate to SchematicTools
    return await this.schematicTools.executeTool(name, args);
  }
}

export { KiCADSchematicMCPServer };