#!/usr/bin/env python3
"""
KiCAD Schematic API - Command Line Interface

Provides helpful commands for setup, testing, and usage of the MCP server.
"""

import sys
import json
import os
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any

def get_claude_config_path() -> Path:
    """Get the Claude Code configuration file path for current platform."""
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "Claude/claude_desktop_config.json"
    else:  # Linux and others
        return Path.home() / ".config/Claude/claude_desktop_config.json"

def setup_claude_code() -> bool:
    """Automatically configure Claude Code MCP settings."""
    print("🔧 Setting up Claude Code MCP configuration...")
    
    config_path = get_claude_config_path()
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing config
    if config_path.exists():
        backup_path = config_path.with_suffix(f".backup.{config_path.stat().st_mtime:.0f}.json")
        backup_path.write_text(config_path.read_text())
        print(f"📁 Backed up existing config to: {backup_path}")
    
    # Determine MCP command path
    mcp_command = os.environ.get('FOUND_MCP_PATH', 'kicad-sch-mcp')
    
    # If still using default, try to find the actual path
    if mcp_command == 'kicad-sch-mcp':
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        possible_paths = [
            f"/Library/Frameworks/Python.framework/Versions/{python_version}/bin/kicad-sch-mcp",
            os.path.expanduser(f"~/Library/Python/{python_version}/bin/kicad-sch-mcp"),
            os.path.expanduser("~/.local/bin/kicad-sch-mcp"),
            "/usr/local/bin/kicad-sch-mcp"
        ]
        
        for path_to_try in possible_paths:
            if os.path.exists(path_to_try) and os.access(path_to_try, os.X_OK):
                mcp_command = path_to_try
                print(f"📍 Using MCP command at: {mcp_command}")
                break
    
    # Create new configuration
    config = {
        "mcpServers": {
            "kicad-sch-api": {
                "command": mcp_command,
                "args": [],
                "env": {}
            }
        }
    }
    
    # Write configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration written to: {config_path}")
    print("🔄 Please restart Claude Code to apply changes")
    return True

def test_installation() -> bool:
    """Test that the MCP server is working correctly."""
    print("🧪 Testing KiCAD Schematic MCP Server...")
    
    try:
        # Test import
        from kicad_sch_api.mcp.server import main as mcp_main
        print("✅ MCP server module imports successfully")
        
        # Test component discovery
        from kicad_sch_api.discovery.search_index import get_search_index
        print("✅ Component discovery system available")
        
        # Test KiCAD library access
        from kicad_sch_api.library.cache import get_symbol_cache
        cache = get_symbol_cache()
        stats = cache.get_performance_stats()
        print(f"✅ Symbol cache initialized: {stats['total_symbols_cached']} symbols")
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_status() -> bool:
    """Show current installation and configuration status."""
    print("📊 KiCAD Schematic MCP Server Status")
    print("=" * 40)
    
    # Check installation
    try:
        import kicad_sch_api
        version = getattr(kicad_sch_api, '__version__', 'unknown')
        print(f"✅ Package installed: v{version}")
    except ImportError:
        print("❌ Package not installed")
        return False
    
    # Check MCP command
    mcp_cmd_path = None
    try:
        result = subprocess.run(['kicad-sch-mcp', '--help'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ MCP command available")
            mcp_cmd_path = "kicad-sch-mcp"
        else:
            print("⚠️  MCP command found but returns error")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Try to find the command in common locations
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        possible_paths = [
            f"/Library/Frameworks/Python.framework/Versions/{python_version}/bin/kicad-sch-mcp",
            os.path.expanduser(f"~/Library/Python/{python_version}/bin/kicad-sch-mcp"),
            os.path.expanduser("~/.local/bin/kicad-sch-mcp"),
            "/usr/local/bin/kicad-sch-mcp"
        ]
        
        for path_to_try in possible_paths:
            if os.path.exists(path_to_try) and os.access(path_to_try, os.X_OK):
                print(f"✅ MCP command found at: {path_to_try}")
                print("⚠️  Note: Command not in PATH, but found at above location")
                mcp_cmd_path = path_to_try
                break
        
        if not mcp_cmd_path:
            print("❌ MCP command not found in PATH")
            print("   You may need to add Python scripts directory to your PATH")
            print(f"   Try: export PATH=\"/Library/Frameworks/Python.framework/Versions/{python_version}/bin:$PATH\"")
    
    # Store found path for potential use in configuration
    if mcp_cmd_path:
        os.environ['FOUND_MCP_PATH'] = mcp_cmd_path
    
    # Check Claude Code configuration
    config_path = get_claude_config_path()
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            if "kicad-sch-api" in config.get("mcpServers", {}):
                print("✅ Claude Code MCP configuration found")
            else:
                print("⚠️  Claude Code config exists but kicad-sch-api not configured")
        except json.JSONDecodeError:
            print("❌ Claude Code config file is invalid JSON")
    else:
        print("❌ Claude Code configuration not found")
    
    # Check KiCAD libraries
    try:
        from kicad_sch_api.library.cache import get_symbol_cache
        cache = get_symbol_cache()
        stats = cache.get_performance_stats()
        print(f"✅ KiCAD libraries: {len(cache._lib_stats)} libraries, {stats['total_symbols_cached']} symbols")
    except Exception as e:
        print(f"⚠️  KiCAD library access: {e}")
    
    return True

def create_demo() -> bool:
    """Create a demo schematic to test functionality."""
    print("🎨 Creating demo schematic...")
    
    try:
        import kicad_sch_api as ksa
        
        # Create demo schematic
        sch = ksa.create_schematic("Demo_Circuit")
        
        # Add components
        resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
        capacitor = sch.components.add('Device:C', reference='C1', value='100nF', position=(150, 100))
        led = sch.components.add('Device:LED', reference='D1', value='LED', position=(200, 100))
        
        # Add a hierarchical sheet
        sheet_uuid = sch.add_sheet(
            name="Subcircuit",
            filename="subcircuit_demo.kicad_sch",
            position=(100, 150),
            size=(60, 40)
        )
        
        # Add sheet pins
        sch.add_sheet_pin(sheet_uuid, "VCC", "input", (0, 10))
        sch.add_sheet_pin(sheet_uuid, "GND", "input", (0, 30))
        
        # Save schematic
        sch.save("demo_circuit.kicad_sch")
        
        print("✅ Demo schematic created: demo_circuit.kicad_sch")
        print("📁 Contains: resistor, capacitor, LED, and hierarchical sheet")
        print("🔗 Try opening in KiCAD: kicad demo_circuit.kicad_sch")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo creation failed: {e}")
        return False

def init_cache() -> bool:
    """Initialize the component discovery cache."""
    print("🔄 Initializing component discovery cache...")
    
    try:
        from kicad_sch_api.discovery.search_index import ensure_index_built
        component_count = ensure_index_built()
        print(f"✅ Component cache initialized: {component_count} components indexed")
        return True
    except Exception as e:
        print(f"❌ Cache initialization failed: {e}")
        return False

def check_kicad() -> bool:
    """Check KiCAD installation and library access."""
    print("🔍 Checking KiCAD installation...")
    
    try:
        # Check if KiCAD command is available
        result = subprocess.run(['kicad', '--version'], 
                              capture_output=True, timeout=10)
        if result.returncode == 0:
            version_output = result.stdout.decode().strip()
            print(f"✅ KiCAD found: {version_output}")
        else:
            print("⚠️  KiCAD command found but version check failed")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ KiCAD command not found in PATH")
        print("   Please ensure KiCAD is installed and accessible")
    
    # Check library directories
    try:
        from kicad_sch_api.library.cache import get_symbol_cache
        cache = get_symbol_cache()
        
        print("📚 KiCAD Library Status:")
        for lib_name, lib_stats in cache._lib_stats.items():
            print(f"   • {lib_name}: {lib_stats.symbol_count} symbols")
        
        return True
    except Exception as e:
        print(f"❌ Library access failed: {e}")
        return False

def show_logs():
    """Show recent MCP server logs."""
    print("📜 Recent MCP Server Logs")
    print("=" * 25)
    
    # For now, just run the server with debug output
    print("To view live logs, run:")
    print("  kicad-sch-mcp --debug")
    print()
    print("Or check Claude Code logs in:")
    if sys.platform == "darwin":
        print("  ~/Library/Logs/Claude/mcp-server-kicad-sch-api.log")
    elif sys.platform == "win32":
        print("  %USERPROFILE%\\AppData\\Local\\Claude\\Logs\\mcp-server-kicad-sch-api.log")
    else:
        print("  ~/.local/share/Claude/logs/mcp-server-kicad-sch-api.log")

def setup_everything() -> bool:
    """One-command setup that does everything automatically."""
    print("🚀 KiCAD Schematic API - Complete Setup")
    print("=" * 45)
    print()
    
    success = True
    
    # 1. Test installation
    print("Step 1/4: Testing installation...")
    if not test_installation():
        print("❌ Installation test failed. Please reinstall the package.")
        return False
    print()
    
    # 2. Initialize cache
    print("Step 2/4: Initializing component cache...")
    if not init_cache():
        print("⚠️  Cache initialization failed, but continuing...")
    print()
    
    # 3. Setup Claude Code
    print("Step 3/4: Configuring Claude Code...")
    if not setup_claude_code():
        print("⚠️  Claude Code setup failed, but continuing...")
    print()
    
    # 4. Create demo
    print("Step 4/4: Creating demo schematic...")
    if not create_demo():
        print("⚠️  Demo creation failed, but setup is complete")
    print()
    
    # Final status
    print("🎉 Setup Complete!")
    print()
    print("Next steps:")
    print("1. Restart Claude Code")
    print("2. Try: 'Create a voltage divider with two 10kΩ resistors'")
    print("3. Open demo_circuit.kicad_sch in KiCAD to see the example")
    print()
    
    return True

def setup_daemon() -> bool:
    """Setup with daemon-style MCP server (RECOMMENDED)."""
    print("🚀 KiCAD Schematic API - Daemon Setup")
    print("=" * 50)
    print("This will set up a persistent MCP daemon that runs in the background.")
    print()
    
    success = True
    
    # 1. Test installation
    print("Step 1/5: Testing installation...")
    if not test_installation():
        print("❌ Installation test failed. Please reinstall the package.")
        return False
    print()
    
    # 2. Initialize cache
    print("Step 2/5: Initializing component cache...")
    if not init_cache():
        print("⚠️  Cache initialization failed, but continuing...")
    print()
    
    # 3. Start daemon
    print("Step 3/5: Starting MCP daemon...")
    from .daemon import MCPDaemon
    daemon = MCPDaemon()
    
    if daemon.is_running():
        print("✅ Daemon is already running")
    else:
        if not daemon.start():
            print("❌ Failed to start daemon")
            return False
    print()
    
    # 4. Configure Claude Code
    print("Step 4/5: Configuring Claude Code...")
    if not daemon._update_claude_config():
        print("⚠️  Claude Code configuration failed, but daemon is running...")
    else:
        print("✅ Claude Code configured successfully")
    print()
    
    # 5. Create demo
    print("Step 5/5: Creating demo schematic...")
    if not create_demo():
        print("⚠️  Demo creation failed, but setup is complete")
    print()
    
    # Final status
    status = daemon.get_status()
    print("🎉 Daemon Setup Complete!")
    print()
    print("✨ What's new with daemon mode:")
    print("  • MCP server runs persistently in background")
    print("  • No PATH issues or virtual environment problems")
    print("  • Automatic startup after system reboot (if desired)")
    print("  • Better performance and reliability")
    print()
    print("📊 Status:")
    print(f"  Daemon running: {'✅ Yes' if status['running'] else '❌ No'}")
    print(f"  Claude configured: {'✅ Yes' if status['claude_configured'] else '❌ No'}")
    print(f"  Log file: {status['log_file']}")
    print()
    
    if status['running'] and status['claude_configured']:
        print("🚀 Next steps:")
        print("1. Restart Claude Code")
        print("2. Try: 'Create a voltage divider with two 10kΩ resistors'")
        print("3. Open demo_circuit.kicad_sch in KiCAD to see the example")
        print()
        print("🔧 Daemon management:")
        print("  kicad-sch-api --daemon-status    # Check status")
        print("  kicad-sch-api --stop-daemon      # Stop daemon")
        print("  kicad-sch-api --start-daemon     # Start daemon")
        print("  kicad-sch-api --restart-daemon   # Restart daemon")
    else:
        print("⚠️  Setup incomplete. Check the status and try again.")
        return False
    
    print()
    return True

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KiCAD Schematic API - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kicad-sch-api --setup                # Complete one-command setup (RECOMMENDED)
  kicad-sch-api --setup-daemon          # Setup with daemon-style MCP server
  kicad-sch-api --start-daemon          # Start MCP daemon in background
  kicad-sch-api --stop-daemon           # Stop MCP daemon
  kicad-sch-api --daemon-status         # Show daemon status
  kicad-sch-api --test                  # Test installation
  kicad-sch-api --demo                  # Create demo schematic
        """
    )
    
    # Main setup options
    parser.add_argument('--setup', action='store_true',
                       help='Complete one-command setup (RECOMMENDED for new users)')
    parser.add_argument('--setup-daemon', action='store_true',
                       help='Setup with daemon-style MCP server (RECOMMENDED)')
    
    # Daemon management
    parser.add_argument('--start-daemon', action='store_true',
                       help='Start MCP daemon in background')
    parser.add_argument('--stop-daemon', action='store_true',
                       help='Stop MCP daemon')
    parser.add_argument('--restart-daemon', action='store_true',
                       help='Restart MCP daemon')
    parser.add_argument('--daemon-status', action='store_true',
                       help='Show daemon status and logs')
    
    # Legacy/manual setup options
    parser.add_argument('--setup-claude-code', action='store_true',
                       help='Configure Claude Code MCP settings only')
    parser.add_argument('--test', action='store_true',
                       help='Test that the installation is working')
    parser.add_argument('--status', action='store_true',
                       help='Show detailed installation and configuration status')
    parser.add_argument('--demo', action='store_true',
                       help='Create a demo schematic')
    parser.add_argument('--init-cache', action='store_true',
                       help='Initialize component discovery cache')
    parser.add_argument('--check-kicad', action='store_true',
                       help='Check KiCAD installation and libraries')
    parser.add_argument('--logs', action='store_true',
                       help='Show recent MCP server logs')
    
    args = parser.parse_args()
    
    # If no arguments provided, suggest the daemon setup
    if not any(vars(args).values()):
        print("🚀 KiCAD Schematic API - Command Line Interface")
        print()
        print("🌟 RECOMMENDED: Setup with daemon-style MCP server:")
        print("  kicad-sch-api --setup-daemon")
        print()
        print("📖 For legacy setup:")
        print("  kicad-sch-api --setup")
        print()
        print("🆘 For help with all options:")
        print("  kicad-sch-api --help")
        return
    
    # Import daemon management after args check
    from .daemon import MCPDaemon
    
    # Handle daemon commands
    daemon = MCPDaemon()
    
    if args.start_daemon:
        success = daemon.start()
        sys.exit(0 if success else 1)
    
    if args.stop_daemon:
        success = daemon.stop()
        sys.exit(0 if success else 1)
    
    if args.restart_daemon:
        success = daemon.restart()
        sys.exit(0 if success else 1)
    
    if args.daemon_status:
        status = daemon.get_status()
        print(f"🚀 KiCAD Schematic MCP Server Status")
        print("=" * 40)
        print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
        
        if status["pid"]:
            print(f"PID: {status['pid']}")
        
        print(f"Log file: {status['log_file']}")
        print(f"Claude configured: {'✅ Yes' if status['claude_configured'] else '❌ No'}")
        
        if not status["claude_configured"]:
            print("\n⚠️  Claude Code not configured. Run with --setup-daemon to fix.")
        
        if status["running"]:
            print("\n📜 Recent logs:")
            daemon.show_logs(10)
        
        return
    
    # Execute requested actions
    success = True
    
    if args.setup_daemon:
        success &= setup_daemon()
    elif args.setup:
        success &= setup_everything()
    
    if args.setup_claude_code:
        success &= setup_claude_code()
    
    if args.test:
        success &= test_installation()
    
    if args.status:
        success &= show_status()
    
    if args.demo:
        success &= create_demo()
    
    if args.init_cache:
        success &= init_cache()
    
    if args.check_kicad:
        success &= check_kicad()
    
    if args.logs:
        show_logs()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()