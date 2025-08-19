#!/usr/bin/env python3
"""
KiCAD Schematic API - MCP Server Daemon

Provides daemon-style MCP server with proper process management.
Users can start/stop/restart the server as a background process.
"""

import os
import sys
import signal
import subprocess
import time
import json
import logging
from pathlib import Path
from typing import Optional
import tempfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPDaemon:
    """Manages the MCP server as a daemon process."""
    
    def __init__(self):
        self.name = "kicad-sch-mcp"
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".kicad-sch-api"
        self.config_dir.mkdir(exist_ok=True)
        
        # Daemon files
        self.pid_file = self.config_dir / "mcp-daemon.pid"
        self.log_file = self.config_dir / "mcp-daemon.log"
        self.socket_file = self.config_dir / "mcp-daemon.sock"
        
        # Claude configuration
        self.claude_config = self._get_claude_config_path()
    
    def _get_claude_config_path(self) -> Path:
        """Get the Claude Code configuration file path for current platform."""
        if sys.platform == "darwin":
            return self.home_dir / "Library/Application Support/Claude/claude_desktop_config.json"
        elif sys.platform == "win32":
            return Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json"
        else:  # Linux and others
            return self.home_dir / ".config/Claude/claude_desktop_config.json"
    
    def is_running(self) -> bool:
        """Check if daemon is currently running."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            
            # Check if process is still alive
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, OSError):
            # PID file exists but process is dead, clean up
            self.pid_file.unlink(missing_ok=True)
            return False
    
    def get_status(self) -> dict:
        """Get detailed daemon status."""
        status = {
            "running": self.is_running(),
            "pid": None,
            "log_file": str(self.log_file),
            "socket_file": str(self.socket_file),
            "claude_configured": self._check_claude_config()
        }
        
        if status["running"] and self.pid_file.exists():
            try:
                with open(self.pid_file) as f:
                    status["pid"] = int(f.read().strip())
            except (ValueError, OSError):
                pass
        
        return status
    
    def _check_claude_config(self) -> bool:
        """Check if Claude Code is configured with our MCP server."""
        if not self.claude_config.exists():
            return False
        
        try:
            with open(self.claude_config) as f:
                config = json.load(f)
            
            servers = config.get("mcpServers", {})
            return "kicad-sch-api" in servers
        except (json.JSONDecodeError, OSError):
            return False
    
    def start(self) -> bool:
        """Start the daemon process."""
        if self.is_running():
            logger.info("Daemon is already running")
            return True
        
        logger.info("Starting MCP daemon...")
        
        try:
            # Create the daemon process using the MCP server entry point
            cmd = [
                sys.executable, "-m", "kicad_sch_api.mcp.server",
                "--daemon",
                "--log-file", str(self.log_file),
                "--pid-file", str(self.pid_file)
            ]
            
            # Start daemon process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it started successfully
            if self.is_running():
                logger.info(f"Daemon started successfully (PID: {process.pid})")
                self._update_claude_config()
                return True
            else:
                logger.error("Failed to start daemon")
                return False
                
        except Exception as e:
            logger.error(f"Error starting daemon: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the daemon process."""
        if not self.is_running():
            logger.info("Daemon is not running")
            return True
        
        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            
            logger.info(f"Stopping daemon (PID: {pid})...")
            
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for _ in range(10):
                if not self.is_running():
                    break
                time.sleep(0.5)
            
            # Force kill if still running
            if self.is_running():
                logger.warning("Forcing daemon shutdown...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            
            # Clean up files
            self.pid_file.unlink(missing_ok=True)
            self.socket_file.unlink(missing_ok=True)
            
            if self.is_running():
                logger.error("Failed to stop daemon")
                return False
            else:
                logger.info("Daemon stopped successfully")
                return True
                
        except (ValueError, ProcessLookupError, OSError) as e:
            logger.error(f"Error stopping daemon: {e}")
            # Clean up stale files
            self.pid_file.unlink(missing_ok=True)
            self.socket_file.unlink(missing_ok=True)
            return True
    
    def restart(self) -> bool:
        """Restart the daemon process."""
        logger.info("Restarting daemon...")
        self.stop()
        time.sleep(1)
        return self.start()
    
    def _update_claude_config(self) -> bool:
        """Update Claude Code configuration with daemon socket."""
        try:
            # Create directory if it doesn't exist
            self.claude_config.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing config or create new one
            if self.claude_config.exists():
                with open(self.claude_config) as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Ensure mcpServers section exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            # Update our server configuration
            config["mcpServers"]["kicad-sch-api"] = {
                "command": sys.executable,
                "args": ["-m", "kicad_sch_api.mcp.server"],
                "env": {}
            }
            
            # Write configuration back
            with open(self.claude_config, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated Claude configuration: {self.claude_config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Claude configuration: {e}")
            return False
    
    def show_logs(self, lines: int = 20) -> None:
        """Show recent daemon log entries."""
        if not self.log_file.exists():
            print("No log file found")
            return
        
        try:
            # Use tail-like functionality
            with open(self.log_file) as f:
                log_lines = f.readlines()
            
            # Show last N lines
            for line in log_lines[-lines:]:
                print(line.rstrip())
                
        except OSError as e:
            logger.error(f"Error reading log file: {e}")

# CLI functions for entry points
def start_daemon():
    """Entry point for starting daemon."""
    daemon = MCPDaemon()
    success = daemon.start()
    sys.exit(0 if success else 1)

def stop_daemon():
    """Entry point for stopping daemon."""
    daemon = MCPDaemon()
    success = daemon.stop()
    sys.exit(0 if success else 1)

def restart_daemon():
    """Entry point for restarting daemon."""
    daemon = MCPDaemon()
    success = daemon.restart()
    sys.exit(0 if success else 1)

def status_daemon():
    """Entry point for daemon status."""
    daemon = MCPDaemon()
    status = daemon.get_status()
    
    print(f"🚀 KiCAD Schematic MCP Server Status")
    print("=" * 40)
    print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
    
    if status["pid"]:
        print(f"PID: {status['pid']}")
    
    print(f"Log file: {status['log_file']}")
    print(f"Claude configured: {'✅ Yes' if status['claude_configured'] else '❌ No'}")
    
    if not status["claude_configured"]:
        print("\n⚠️  Claude Code not configured. Run with --configure-claude to fix.")
    
    if status["running"]:
        print("\n📜 Recent logs:")
        daemon.show_logs(10)

def main():
    """Main daemon management interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="KiCAD Schematic MCP Daemon Manager")
    parser.add_argument("--start", action="store_true", help="Start the daemon")
    parser.add_argument("--stop", action="store_true", help="Stop the daemon")
    parser.add_argument("--restart", action="store_true", help="Restart the daemon")
    parser.add_argument("--status", action="store_true", help="Show daemon status")
    parser.add_argument("--logs", type=int, default=20, help="Show recent log lines")
    
    args = parser.parse_args()
    
    daemon = MCPDaemon()
    
    if args.start:
        success = daemon.start()
        sys.exit(0 if success else 1)
    elif args.stop:
        success = daemon.stop()
        sys.exit(0 if success else 1)
    elif args.restart:
        success = daemon.restart()
        sys.exit(0 if success else 1)
    elif args.status:
        status_daemon()
    else:
        # No arguments, show status
        status_daemon()

if __name__ == "__main__":
    main()