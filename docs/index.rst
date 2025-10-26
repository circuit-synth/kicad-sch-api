kicad-sch-api Documentation
============================

Professional KiCAD Schematic Manipulation Library

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
   ARCHITECTURE

.. toctree::
   :maxdepth: 2
   :caption: Feature Documentation

   ERC_PRD
   ERC_ERD

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

✅ **Professional API** - Modern Python with full type hints
   Clean, intuitive interface with comprehensive validation

✅ **Performance Optimized** - O(1) lookups, bulk operations, symbol caching
   Handles large schematics with hundreds of components efficiently

✅ **AI Agent Ready** - Purpose-built for MCP integration
   Natural language circuit generation through Claude and other AI agents

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

Installation
------------

.. code-block:: bash

   pip install kicad-sch-api

Requirements:
   - Python 3.9 or higher
   - KiCAD 7 or 8 installation (for component libraries)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
