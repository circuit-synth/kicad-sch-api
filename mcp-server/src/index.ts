#!/usr/bin/env node

/**
 * KiCAD Schematic API MCP Server
 * 
 * Model Context Protocol server providing AI agents with comprehensive
 * KiCAD schematic manipulation capabilities via kicad-sch-api.
 * 
 * Features:
 * - Complete schematic file manipulation
 * - Component management with validation
 * - Library integration and symbol lookup
 * - Wire and connection management
 * - Professional error handling and validation
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  ToolSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { SchematicTools } from './schematic-tools.js';
import { PythonBridge } from './python-bridge.js';
import { MCPLogger } from './logger.js';

class KiCADSchematicMCPServer {
  private server: Server;
  private schematicTools: SchematicTools;
  private pythonBridge: PythonBridge;
  private logger: MCPLogger;

  constructor() {
    this.logger = new MCPLogger('KiCADSchematicMCP');
    this.server = new Server(
      {
        name: 'kicad-sch-api',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize Python bridge
    this.pythonBridge = new PythonBridge();
    
    // Initialize schematic tools
    this.schematicTools = new SchematicTools(this.pythonBridge, this.logger);

    this.setupHandlers();
    this.logger.info('KiCAD Schematic MCP Server initialized');
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = this.schematicTools.getToolDefinitions();
      this.logger.debug(`Listing ${tools.length} available tools`);
      return { tools };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      this.logger.info(`Tool called: ${name}`);
      this.logger.debug(`Tool arguments:`, args);

      try {
        // Validate tool exists
        if (!this.schematicTools.hasUnknownTool(name)) {
          throw new Error(`Unknown tool: ${name}`);
        }

        // Execute tool
        const result = await this.schematicTools.executeTool(name, args || {});
        
        this.logger.debug(`Tool ${name} completed successfully`);
        return {
          content: [
            {
              type: 'text',
              text: typeof result === 'string' ? result : JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        this.logger.error(`Tool ${name} failed: ${errorMessage}`);
        
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${name}: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async start(): Promise<void> {
    // Initialize Python bridge
    await this.pythonBridge.initialize();
    
    // Create transport
    const transport = new StdioServerTransport();
    
    this.logger.info('Starting KiCAD Schematic MCP Server...');
    
    // Connect and start server
    await this.server.connect(transport);
    
    this.logger.info('KiCAD Schematic MCP Server started successfully');
    this.logger.info('Ready to receive tool calls from AI agents');
  }

  async stop(): Promise<void> {
    this.logger.info('Stopping KiCAD Schematic MCP Server...');
    
    // Cleanup Python bridge
    await this.pythonBridge.cleanup();
    
    // Close server
    await this.server.close();
    
    this.logger.info('KiCAD Schematic MCP Server stopped');
  }
}

// Handle process signals for graceful shutdown
const server = new KiCADSchematicMCPServer();

process.on('SIGINT', async () => {
  console.log('\nReceived SIGINT, shutting down gracefully...');
  await server.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\nReceived SIGTERM, shutting down gracefully...');
  await server.stop();
  process.exit(0);
});

// Start the server
server.start().catch((error) => {
  console.error('Failed to start KiCAD Schematic MCP Server:', error);
  process.exit(1);
});

export { KiCADSchematicMCPServer };