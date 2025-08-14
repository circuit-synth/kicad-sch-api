/**
 * Python Bridge for KiCAD Schematic API
 * 
 * Manages communication between the TypeScript MCP server and the Python
 * kicad-sch-api library via subprocess communication.
 */

import { spawn, ChildProcess } from 'child_process';
import { v4 as uuidv4 } from 'uuid';
import { MCPLogger } from './logger.js';

interface PythonCommand {
  id: string;
  command: string;
  params: Record<string, unknown>;
}

interface PythonResponse {
  id: string;
  result?: any;
  error?: string;
}

interface PendingCommand {
  resolve: (value: any) => void;
  reject: (error: Error) => void;
  timestamp: number;
}

export class PythonBridge {
  private pythonProcess: ChildProcess | null = null;
  private pendingCommands: Map<string, PendingCommand> = new Map();
  private logger: MCPLogger;
  private initialized = false;
  private readonly COMMAND_TIMEOUT = 30000; // 30 seconds

  constructor() {
    this.logger = new MCPLogger('PythonBridge');
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    this.logger.info('Initializing Python bridge...');

    try {
      // Start Python subprocess
      const pythonPath = process.env.PYTHON_PATH || 'python3';
      const scriptPath = process.env.KICAD_SCH_API_SCRIPT || 
                         '../python/kicad_sch_api/mcp/server.py';

      this.pythonProcess = spawn(pythonPath, [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PYTHONPATH: process.env.PYTHONPATH || '../python',
          PYTHONUNBUFFERED: '1',
        },
      });

      // Set up event handlers
      this.setupProcessHandlers();

      // Wait for Python process to be ready
      await this.waitForReady();

      this.initialized = true;
      this.logger.info('Python bridge initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Python bridge:', error);
      throw new Error(`Python bridge initialization failed: ${error}`);
    }
  }

  private setupProcessHandlers(): void {
    if (!this.pythonProcess) return;

    // Handle stdout (responses from Python)
    this.pythonProcess.stdout?.on('data', (data: Buffer) => {
      const lines = data.toString().trim().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          this.handlePythonResponse(line);
        }
      }
    });

    // Handle stderr (Python errors and logs)
    this.pythonProcess.stderr?.on('data', (data: Buffer) => {
      const message = data.toString().trim();
      this.logger.debug('Python stderr:', message);
    });

    // Handle process exit
    this.pythonProcess.on('exit', (code, signal) => {
      this.logger.error(`Python process exited with code ${code}, signal ${signal}`);
      this.initialized = false;
      
      // Reject all pending commands
      for (const [id, pending] of this.pendingCommands) {
        pending.reject(new Error('Python process exited unexpectedly'));
      }
      this.pendingCommands.clear();
    });

    // Handle process errors
    this.pythonProcess.on('error', (error) => {
      this.logger.error('Python process error:', error);
      this.initialized = false;
    });
  }

  private handlePythonResponse(line: string): void {
    try {
      const response: PythonResponse = JSON.parse(line);
      
      const pending = this.pendingCommands.get(response.id);
      if (!pending) {
        this.logger.warning(`Received response for unknown command: ${response.id}`);
        return;
      }

      this.pendingCommands.delete(response.id);

      if (response.error) {
        pending.reject(new Error(response.error));
      } else {
        pending.resolve(response.result);
      }
    } catch (error) {
      this.logger.error('Error parsing Python response:', error);
      this.logger.debug('Raw response:', line);
    }
  }

  private async waitForReady(timeout: number = 10000): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Python process startup timeout'));
      }, timeout);

      // Send a ping command to verify Python is ready
      this.executeCommand('ping', {})
        .then(() => {
          clearTimeout(timeoutId);
          resolve();
        })
        .catch((error) => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  async executeCommand(command: string, params: Record<string, unknown>): Promise<any> {
    if (!this.initialized || !this.pythonProcess) {
      throw new Error('Python bridge not initialized');
    }

    const commandId = uuidv4();
    const pythonCommand: PythonCommand = {
      id: commandId,
      command,
      params,
    };

    this.logger.debug(`Executing Python command: ${command}`, params);

    return new Promise((resolve, reject) => {
      // Set up timeout
      const timeoutId = setTimeout(() => {
        this.pendingCommands.delete(commandId);
        reject(new Error(`Command timeout: ${command}`));
      }, this.COMMAND_TIMEOUT);

      // Store pending command
      this.pendingCommands.set(commandId, {
        resolve: (value) => {
          clearTimeout(timeoutId);
          resolve(value);
        },
        reject: (error) => {
          clearTimeout(timeoutId);
          reject(error);
        },
        timestamp: Date.now(),
      });

      // Send command to Python
      const commandJson = JSON.stringify(pythonCommand) + '\n';
      this.pythonProcess?.stdin?.write(commandJson);
    });
  }

  async cleanup(): Promise<void> {
    if (!this.pythonProcess) {
      return;
    }

    this.logger.info('Cleaning up Python bridge...');

    // Reject all pending commands
    for (const [id, pending] of this.pendingCommands) {
      pending.reject(new Error('Python bridge shutting down'));
    }
    this.pendingCommands.clear();

    // Terminate Python process
    this.pythonProcess.kill('SIGTERM');
    
    // Wait for process to exit gracefully
    await new Promise<void>((resolve) => {
      const timeout = setTimeout(() => {
        this.pythonProcess?.kill('SIGKILL');
        resolve();
      }, 5000);

      this.pythonProcess?.on('exit', () => {
        clearTimeout(timeout);
        resolve();
      });
    });

    this.pythonProcess = null;
    this.initialized = false;
    this.logger.info('Python bridge cleaned up');
  }

  isInitialized(): boolean {
    return this.initialized;
  }

  getStats(): Record<string, any> {
    return {
      initialized: this.initialized,
      pending_commands: this.pendingCommands.size,
      process_pid: this.pythonProcess?.pid,
    };
  }
}