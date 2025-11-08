kicad-sch-api Documentation
============================

KiCAD Schematic Manipulation Library

**kicad-sch-api** is a Python library for programmatic creation and manipulation of KiCAD schematic files with exact format preservation.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   README
   GETTING_STARTED
   WHY_USE_THIS_LIBRARY

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   API_REFERENCE
   RECIPES
   HIERARCHY_FEATURES
   ORTHOGONAL_ROUTING
   ARCHITECTURE
   ERC_USER_GUIDE

.. toctree::
   :maxdepth: 2
   :caption: MCP Server (AI Agents)

   MCP_EXAMPLES
   MCP_SERVER_LOGGING_INTEGRATION

.. toctree::
   :maxdepth: 1
   :caption: Developer Documentation

   ERC_PRD
   ERC_ERD
   READTHEDOCS_SETUP

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/modules

.. toctree::
   :maxdepth: 1
   :caption: Project Info

   GitHub Repository <https://github.com/circuit-synth/kicad-sch-api>
   PyPI Package <https://pypi.org/project/kicad-sch-api/>

Key Features
------------

✅ **Exact Format Preservation** - Byte-perfect KiCAD output
   Generated schematics are indistinguishable from hand-drawn ones

✅ **Real KiCAD Library Integration** - Works with your KiCAD installation
   Automatic component validation and pin position calculation

✅ **Object-Oriented API** - Modern Python with full type hints
   Clean, intuitive interface with comprehensive validation

✅ **Automatic Wire Routing** - Manhattan-style orthogonal routing
   L-shaped wire paths generated automatically between components

✅ **Performance Optimized** - O(1) lookups, bulk operations, symbol caching
   Handles large schematics with hundreds of components efficiently

✅ **MCP Server** - 15 tools for programmatic schematic manipulation
   Enables circuit generation through natural language with AI agents
   Build circuits from text prompts using Claude or other MCP clients

Quick Example
-------------

.. code-block:: python

   import kicad_sch_api as ksa

   # Create new schematic
   sch = ksa.create_schematic('My Circuit')

   # Add components
   led = sch.components.add('Device:LED', 'D1', 'RED', (100, 100))
   resistor = sch.components.add('Device:R', 'R1', '330', (100, 80))

   # Wire them together
   sch.add_wire_between_pins('R1', '2', 'D1', '1')

   # Save with exact KiCAD format
   sch.save('led_circuit.kicad_sch')

MCP Server (AI Agents)
----------------------

Build circuits from natural language using the integrated MCP server:

.. code-block:: bash

   # Start the MCP server
   uv run kicad-sch-mcp

   # Or configure in Claude Desktop
   # See MCP_EXAMPLES for complete setup guide

AI agents can now create complete circuits:

.. code-block:: text

   "Create a voltage divider with R1=10k and R2=20k, fully wired with VCC and GND"

The AI agent will automatically:
- Create schematic and add components
- Calculate pin positions and route wires
- Add net labels and junctions
- Save the complete, functional circuit

**15 MCP Tools Available:**
- Component management (add, list, update, remove, filter)
- Connectivity (wires, labels, junctions)
- Pin discovery (by name, type, complete info)
- Schematic management (create, load, save, query)

See :doc:`MCP_EXAMPLES` for complete documentation.

Installation
------------

.. code-block:: bash

   pip install kicad-sch-api

Requirements:
   - Python 3.10 or higher
   - KiCAD 7 or 8 installation (for component libraries)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
