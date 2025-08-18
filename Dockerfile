# KiCAD Schematic MCP Server - Docker Container
FROM python:3.11-slim

LABEL maintainer="shane@circuit-synth.com"
LABEL description="KiCAD Schematic MCP Server with component discovery"
LABEL version="0.1.1"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
RUN chown -R mcp:mcp /app
USER mcp

# Expose port for potential future web interface
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD kicad-sch-mcp --test || exit 1

# Default command
CMD ["kicad-sch-mcp"]

# Usage examples:
#
# Build:
#   docker build -t kicad-sch-mcp .
#
# Run standalone:
#   docker run -d --name kicad-mcp kicad-sch-mcp
#
# Run with Claude Code:
#   Add to claude_desktop_config.json:
#   {
#     "mcpServers": {
#       "kicad-sch-api": {
#         "command": "docker",
#         "args": ["exec", "kicad-mcp", "kicad-sch-mcp"],
#         "env": {}
#       }
#     }
#   }
#
# Test:
#   docker run --rm kicad-sch-mcp kicad-sch-mcp --test