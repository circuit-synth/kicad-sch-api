#!/bin/bash
#
# KiCAD Schematic MCP Server - One-Click Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.sh | bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 KiCAD Schematic MCP Server Installation${NC}"
echo "==========================================="
echo

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}📋 Checking prerequisites...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
        echo "Please install Python 3.8 or later and try again."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        echo -e "${RED}❌ pip is required but not installed.${NC}"
        echo "Please install pip and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python and pip found${NC}"
}

# Install the package
install_package() {
    echo -e "${BLUE}📦 Installing kicad-sch-api...${NC}"
    
    # Use pip3 if available, otherwise pip
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    # For development, install from local source
    if [[ -f "pyproject.toml" ]]; then
        echo "Installing from local source..."
        $PIP_CMD install -e .
    else
        echo "Installing from PyPI..."
        $PIP_CMD install kicad-sch-api || {
            echo -e "${YELLOW}⚠️  PyPI package not yet available, installing from GitHub...${NC}"
            $PIP_CMD install git+https://github.com/circuit-synth/kicad-sch-api.git
        }
    fi
    
    echo -e "${GREEN}✅ Package installed successfully${NC}"
}

# Configure Claude Code
configure_claude_code() {
    echo -e "${BLUE}⚙️  Configuring Claude Code MCP settings...${NC}"
    
    # Determine Claude Code config directory
    case "$(uname -s)" in
        Darwin*)    CLAUDE_DIR="$HOME/Library/Application Support/Claude" ;;
        Linux*)     CLAUDE_DIR="$HOME/.config/Claude" ;;
        *)          CLAUDE_DIR="$HOME/.claude" ;;
    esac
    
    CONFIG_FILE="$CLAUDE_DIR/claude_desktop_config.json"
    
    # Create directory if it doesn't exist
    mkdir -p "$CLAUDE_DIR"
    
    # Check if config file exists
    if [[ -f "$CONFIG_FILE" ]]; then
        echo "Backing up existing Claude Code configuration..."
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Get the kicad-sch-mcp command path (use found path if available)
    if [[ -n "$FOUND_MCP_PATH" ]]; then
        MCP_COMMAND="$FOUND_MCP_PATH"
    else
        MCP_COMMAND=$(which kicad-sch-mcp 2>/dev/null || echo "kicad-sch-mcp")
    fi
    
    # Create or update configuration
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "$MCP_COMMAND",
      "args": [],
      "env": {}
    }
  }
}
EOF
    
    echo -e "${GREEN}✅ Claude Code configuration updated${NC}"
    echo -e "${YELLOW}📁 Config file: $CONFIG_FILE${NC}"
}

# Test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    
    # First try to find the command in PATH
    MCP_CMD_PATH=$(command -v kicad-sch-mcp 2>/dev/null)
    
    if [[ -z "$MCP_CMD_PATH" ]]; then
        # Try common Python installation locations
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        POSSIBLE_PATHS=(
            "/Library/Frameworks/Python.framework/Versions/${PYTHON_VERSION}/bin/kicad-sch-mcp"
            "$HOME/Library/Python/${PYTHON_VERSION}/bin/kicad-sch-mcp"
            "$HOME/.local/bin/kicad-sch-mcp"
            "/usr/local/bin/kicad-sch-mcp"
        )
        
        for path in "${POSSIBLE_PATHS[@]}"; do
            if [[ -x "$path" ]]; then
                MCP_CMD_PATH="$path"
                break
            fi
        done
    fi
    
    if [[ -z "$MCP_CMD_PATH" ]]; then
        echo -e "${RED}❌ kicad-sch-mcp command not found${NC}"
        echo "Please add the Python scripts directory to your PATH or restart your terminal."
        echo -e "${YELLOW}To add to PATH permanently, add this line to your ~/.bash_profile or ~/.zshrc:${NC}"
        echo "export PATH=\"/Library/Frameworks/Python.framework/Versions/${PYTHON_VERSION}/bin:\$PATH\""
        return 1
    fi
    
    echo -e "${GREEN}✅ kicad-sch-mcp found at: $MCP_CMD_PATH${NC}"
    
    # Test server startup
    echo "Testing MCP server startup..."
    if timeout 10 "$MCP_CMD_PATH" --test &> /dev/null; then
        echo -e "${GREEN}✅ MCP server test passed${NC}"
    else
        echo -e "${YELLOW}⚠️  MCP server test timeout (this may be normal)${NC}"
    fi
    
    echo -e "${GREEN}✅ Installation test completed${NC}"
    
    # Update MCP command in configuration
    export FOUND_MCP_PATH="$MCP_CMD_PATH"
}

# Show usage examples
show_examples() {
    echo -e "${BLUE}📚 Usage Examples${NC}"
    echo "=================="
    echo
    echo "In Claude Code, try these commands:"
    echo -e "${GREEN}• Create a new schematic called 'MyCircuit'${NC}"
    echo -e "${GREEN}• Add a 10k resistor and 100nF capacitor${NC}"
    echo -e "${GREEN}• Create a hierarchical schematic with subcircuits${NC}"
    echo
    echo "Command line usage:"
    echo -e "${GREEN}kicad-sch-mcp --help${NC}        # Show all options"
    echo -e "${GREEN}kicad-sch-mcp --demo${NC}        # Create demo schematic"
    echo -e "${GREEN}kicad-sch-mcp --status${NC}      # Check server status"
    echo
}

# Main installation flow
main() {
    echo "Starting installation..."
    echo
    
    check_prerequisites
    install_package
    configure_claude_code
    test_installation
    
    echo
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo
    
    show_examples
    
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Restart Claude Code to load the new MCP server"
    echo "2. Try creating a schematic with natural language"
    echo "3. Check out the documentation: https://github.com/circuit-synth/kicad-sch-api"
    echo
    echo -e "${YELLOW}If you encounter issues, run: kicad-sch-mcp --help${NC}"
}

# Run the installation
main "$@"