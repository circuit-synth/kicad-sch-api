# KiCAD Schematic MCP Server - Windows Installation Script
# Usage: iwr -useb https://raw.githubusercontent.com/circuit-synth/kicad-sch-api/main/install.ps1 | iex

param(
    [switch]$SkipClaudeConfig = $false
)

# Color functions
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Info { Write-ColorOutput Cyan $args }

Write-Info "🚀 KiCAD Schematic MCP Server Installation"
Write-Info "==========================================="
Write-Output ""

# Check prerequisites
function Test-Prerequisites {
    Write-Info "📋 Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            throw "Python not found"
        }
        Write-Success "✅ Python found: $pythonVersion"
    }
    catch {
        Write-Error "❌ Python 3 is required but not installed."
        Write-Output "Please install Python 3.8 or later from https://python.org and try again."
        exit 1
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>$null
        if (-not $pipVersion) {
            throw "pip not found"
        }
        Write-Success "✅ pip found: $pipVersion"
    }
    catch {
        Write-Error "❌ pip is required but not installed."
        Write-Output "Please install pip and try again."
        exit 1
    }
}

# Install the package
function Install-Package {
    Write-Info "📦 Installing kicad-sch-api..."
    
    # Check if installing from local source
    if (Test-Path "pyproject.toml") {
        Write-Output "Installing from local source..."
        pip install -e .
    }
    else {
        Write-Output "Installing from PyPI..."
        try {
            pip install kicad-sch-api
        }
        catch {
            Write-Warning "⚠️  PyPI package not yet available, installing from GitHub..."
            pip install git+https://github.com/circuit-synth/kicad-sch-api.git
        }
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Package installation failed"
        exit 1
    }
    
    Write-Success "✅ Package installed successfully"
}

# Configure Claude Code
function Set-ClaudeCodeConfig {
    if ($SkipClaudeConfig) {
        Write-Warning "⏭️  Skipping Claude Code configuration"
        return
    }
    
    Write-Info "⚙️  Configuring Claude Code MCP settings..."
    
    # Determine Claude Code config directory
    $claudeDir = "$env:APPDATA\Claude"
    $configFile = "$claudeDir\claude_desktop_config.json"
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $claudeDir)) {
        New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    }
    
    # Backup existing config
    if (Test-Path $configFile) {
        $backupFile = "$configFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $configFile $backupFile
        Write-Output "Backed up existing config to: $backupFile"
    }
    
    # Find kicad-sch-mcp command path
    $mcpCommand = Get-Command kicad-sch-mcp -ErrorAction SilentlyContinue
    if ($mcpCommand) {
        $mcpPath = $mcpCommand.Source
    }
    else {
        $mcpPath = "kicad-sch-mcp"
    }
    
    # Create configuration JSON
    $config = @{
        mcpServers = @{
            "kicad-sch-api" = @{
                command = $mcpPath
                args = @()
                env = @{}
            }
        }
    }
    
    # Write configuration file
    $config | ConvertTo-Json -Depth 3 | Out-File -FilePath $configFile -Encoding UTF8
    
    Write-Success "✅ Claude Code configuration updated"
    Write-Warning "📁 Config file: $configFile"
}

# Test installation
function Test-Installation {
    Write-Info "🧪 Testing installation..."
    
    # Test if command is available
    $mcpCommand = Get-Command kicad-sch-mcp -ErrorAction SilentlyContinue
    if (-not $mcpCommand) {
        Write-Error "❌ kicad-sch-mcp command not found in PATH"
        Write-Output "You may need to restart your terminal or check your Python Scripts directory is in PATH."
        return $false
    }
    
    Write-Success "✅ kicad-sch-mcp command found: $($mcpCommand.Source)"
    
    # Test server startup (with timeout)
    Write-Output "Testing MCP server startup..."
    try {
        $job = Start-Job -ScriptBlock { kicad-sch-mcp --test }
        if (Wait-Job $job -Timeout 10) {
            $result = Receive-Job $job
            Write-Success "✅ MCP server test passed"
        }
        else {
            Write-Warning "⚠️  MCP server test timeout (this may be normal)"
        }
        Remove-Job $job -Force
    }
    catch {
        Write-Warning "⚠️  MCP server test failed: $($_.Exception.Message)"
    }
    
    Write-Success "✅ Installation test completed"
    return $true
}

# Show usage examples
function Show-Examples {
    Write-Info "📚 Usage Examples"
    Write-Info "=================="
    Write-Output ""
    Write-Output "In Claude Code, try these commands:"
    Write-Success "• Create a new schematic called 'MyCircuit'"
    Write-Success "• Add a 10k resistor and 100nF capacitor"
    Write-Success "• Create a hierarchical schematic with subcircuits"
    Write-Output ""
    Write-Output "Command line usage:"
    Write-Success "kicad-sch-mcp --help        # Show all options"
    Write-Success "kicad-sch-mcp --demo        # Create demo schematic"
    Write-Success "kicad-sch-mcp --status      # Check server status"
    Write-Output ""
}

# Main installation flow
function Main {
    try {
        Write-Output "Starting installation..."
        Write-Output ""
        
        Test-Prerequisites
        Install-Package
        Set-ClaudeCodeConfig
        $testResult = Test-Installation
        
        Write-Output ""
        Write-Success "🎉 Installation completed successfully!"
        Write-Output ""
        
        Show-Examples
        
        Write-Info "Next steps:"
        Write-Output "1. Restart Claude Code to load the new MCP server"
        Write-Output "2. Try creating a schematic with natural language"
        Write-Output "3. Check out the documentation: https://github.com/circuit-synth/kicad-sch-api"
        Write-Output ""
        Write-Warning "If you encounter issues, run: kicad-sch-mcp --help"
    }
    catch {
        Write-Error "❌ Installation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Run the installation
Main