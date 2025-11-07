# Engineering Requirements Document: KiCad-to-Python Export

**Feature**: KiCad Schematic to Python Code Converter
**Issue**: #129
**Version**: 1.0
**Date**: 2025-11-07
**Author**: Claude Code (AI Assistant)
**Status**: Draft

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Specifications](#component-specifications)
3. [API Specifications](#api-specifications)
4. [Data Flow](#data-flow)
5. [File Formats](#file-formats)
6. [Testing Requirements](#testing-requirements)
7. [Performance Requirements](#performance-requirements)
8. [Security Considerations](#security-considerations)
9. [Deployment](#deployment)

---

## System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ CLI Command │  │ Python API   │  │ Utility Function     │  │
│  │             │  │              │  │                      │  │
│  │ kicad-to-   │  │ sch.export_  │  │ ksa.schematic_to_   │  │
│  │ python      │  │ to_python()  │  │ python()             │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                │                      │               │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          └────────────────┴──────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    Core Export Engine                           │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │             PythonCodeGenerator                           │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │  • Template Management                                    │ │
│  │  • Code Generation Logic                                 │ │
│  │  • Variable Sanitization                                 │ │
│  │  • Code Formatting (Black)                               │ │
│  │  • Syntax Validation                                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                   Schematic Analysis Layer                      │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │ Component   │  │ Wire        │  │ Label Extractor      │   │
│  │ Extractor   │  │ Extractor   │  │                      │   │
│  └─────────────┘  └─────────────┘  └──────────────────────┘   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│  │ Sheet       │  │ Metadata    │  │ Property Extractor   │   │
│  │ Extractor   │  │ Extractor   │  │                      │   │
│  └─────────────┘  └─────────────┘  └──────────────────────┘   │
│                                                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  Existing kicad-sch-api Core                    │
├────────────────────────────────────────────────────────────────┤
│  • Schematic.load()                                             │
│  • S-expression Parsing                                        │
│  • Object Model (Component, Wire, Label, etc.)                │
│  • Format Preservation                                         │
└────────────────────────────────────────────────────────────────┘
```

---

### Module Dependencies

```
kicad_sch_api/
│
├── exporters/               ← NEW MODULE
│   ├── python_generator.py
│   ├── templates/
│   └── utils.py
│       │
│       └─── Depends on ──→ core/schematic.py
│                          └ core/types.py
│                          └ utils/validation.py
│
├── cli/
│   └── kicad_to_python.py  ← NEW CLI
│       │
│       └─── Depends on ──→ exporters/python_generator.py
│                          └ core/schematic.py
│
└── core/
    └── schematic.py        ← ADD METHOD
        │
        └─── New method ──→ export_to_python()
```

---

## Component Specifications

### 1. PythonCodeGenerator

**File**: `kicad_sch_api/exporters/python_generator.py`

#### Class Definition

```python
from pathlib import Path
from typing import Optional, Dict, Any, List
from jinja2 import Environment, PackageLoader
from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Component, Wire, Label, HierarchicalSheet

class PythonCodeGenerator:
    """
    Generate executable Python code from KiCad schematics.

    This class converts loaded Schematic objects into executable Python
    code that uses the kicad-sch-api to recreate the schematic.

    Attributes:
        template: Template style ('minimal', 'default', 'verbose', 'documented')
        jinja_env: Jinja2 environment for template rendering
        format_code: Whether to format code with Black
        add_comments: Whether to add explanatory comments
    """

    def __init__(
        self,
        template: str = 'default',
        format_code: bool = True,
        add_comments: bool = True
    ):
        """
        Initialize code generator.

        Args:
            template: Template style to use
            format_code: Format output with Black
            add_comments: Add explanatory comments
        """
        self.template = template
        self.format_code = format_code
        self.add_comments = add_comments

        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=PackageLoader('kicad_sch_api', 'exporters/templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Register custom filters
        self.jinja_env.filters['sanitize'] = self._sanitize_variable_name

    def generate(
        self,
        schematic: Schematic,
        include_hierarchy: bool = True,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate Python code from schematic.

        Args:
            schematic: Loaded Schematic object
            include_hierarchy: Include hierarchical sheets
            output_path: Optional output file path

        Returns:
            Generated Python code as string

        Raises:
            CodeGenerationError: If code generation fails
            TemplateNotFoundError: If template doesn't exist
        """
        # Extract all schematic data
        data = self._extract_schematic_data(schematic, include_hierarchy)

        # Load and render template
        template = self.jinja_env.get_template(f'{self.template}.py.jinja2')
        code = template.render(**data)

        # Format code
        if self.format_code:
            code = self._format_with_black(code)

        # Validate syntax
        self._validate_syntax(code)

        # Write to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(code, encoding='utf-8')
            output_path.chmod(0o755)  # Make executable

        return code

    def _extract_schematic_data(
        self,
        schematic: Schematic,
        include_hierarchy: bool
    ) -> Dict[str, Any]:
        """
        Extract all data from schematic for template rendering.

        Args:
            schematic: Schematic to extract from
            include_hierarchy: Include hierarchical sheets

        Returns:
            Dictionary with all template data
        """
        return {
            'metadata': self._extract_metadata(schematic),
            'components': self._extract_components(schematic),
            'wires': self._extract_wires(schematic),
            'labels': self._extract_labels(schematic),
            'sheets': self._extract_sheets(schematic) if include_hierarchy else [],
            'options': {
                'add_comments': self.add_comments,
                'include_hierarchy': include_hierarchy
            }
        }

    def _extract_metadata(self, schematic: Schematic) -> Dict[str, Any]:
        """Extract schematic metadata."""
        from datetime import datetime
        import kicad_sch_api

        return {
            'name': schematic.name or 'untitled',
            'title': schematic.title_block.title if schematic.title_block else '',
            'version': kicad_sch_api.__version__,
            'date': datetime.now().isoformat(),
            'source_file': str(schematic.filepath) if schematic.filepath else 'unknown'
        }

    def _extract_components(self, schematic: Schematic) -> List[Dict[str, Any]]:
        """
        Extract component data.

        Returns:
            List of component dictionaries with keys:
            - ref: Reference (R1, C1, etc.)
            - variable: Sanitized Python variable name (r1, c1, etc.)
            - lib_id: Library identifier (Device:R, etc.)
            - value: Component value (10k, 100nF, etc.)
            - footprint: Footprint name
            - x, y: Position coordinates
            - rotation: Rotation angle
            - properties: List of custom properties
        """
        components = []
        for comp in schematic.components:
            comp_data = {
                'ref': comp.reference,
                'variable': self._sanitize_variable_name(comp.reference),
                'lib_id': comp.lib_id,
                'value': comp.value,
                'footprint': comp.footprint or '',
                'x': comp.position.x,
                'y': comp.position.y,
                'rotation': comp.rotation,
                'properties': self._extract_custom_properties(comp)
            }
            components.append(comp_data)
        return components

    def _extract_wires(self, schematic: Schematic) -> List[Dict[str, Any]]:
        """
        Extract wire data.

        Returns:
            List of wire dictionaries with keys:
            - start_x, start_y: Start point
            - end_x, end_y: End point
            - style: Wire style (solid, dashed, etc.)
        """
        wires = []
        for wire in schematic.wires:
            wire_data = {
                'start_x': wire.start.x,
                'start_y': wire.start.y,
                'end_x': wire.end.x,
                'end_y': wire.end.y,
                'style': getattr(wire, 'style', 'solid')
            }
            wires.append(wire_data)
        return wires

    def _extract_labels(self, schematic: Schematic) -> List[Dict[str, Any]]:
        """
        Extract label data.

        Returns:
            List of label dictionaries with keys:
            - text: Label text
            - x, y: Position
            - type: Label type (local, global, hierarchical)
            - rotation: Rotation angle
        """
        labels = []
        for label in schematic.labels:
            label_data = {
                'text': label.text,
                'x': label.position.x,
                'y': label.position.y,
                'type': label.label_type,
                'rotation': getattr(label, 'rotation', 0)
            }
            labels.append(label_data)
        return labels

    def _extract_sheets(self, schematic: Schematic) -> List[Dict[str, Any]]:
        """
        Extract hierarchical sheet data.

        Returns:
            List of sheet dictionaries with keys:
            - name: Sheet name
            - filename: Sheet filename
            - x, y: Position
            - width, height: Size
            - pins: List of sheet pins
        """
        sheets = []
        for sheet in schematic.sheets:
            sheet_data = {
                'name': sheet.name,
                'filename': sheet.filename,
                'x': sheet.position.x,
                'y': sheet.position.y,
                'width': sheet.size.width,
                'height': sheet.size.height,
                'pins': [
                    {
                        'name': pin.name,
                        'type': pin.pin_type,
                        'x': pin.position.x,
                        'y': pin.position.y
                    }
                    for pin in sheet.pins
                ]
            }
            sheets.append(sheet_data)
        return sheets

    def _extract_custom_properties(self, component: Component) -> List[Dict[str, str]]:
        """
        Extract custom component properties.

        Returns:
            List of property dictionaries with keys:
            - name: Property name
            - value: Property value
        """
        # Standard properties to exclude
        standard_props = {
            'Reference', 'Value', 'Footprint', 'Datasheet',
            'ki_keywords', 'ki_description', 'ki_fp_filters'
        }

        properties = []
        for prop_name, prop_value in component.properties.items():
            if prop_name not in standard_props:
                properties.append({
                    'name': prop_name,
                    'value': prop_value
                })
        return properties

    @staticmethod
    def _sanitize_variable_name(name: str) -> str:
        """
        Convert reference/name to valid Python variable name.

        Rules:
        - Convert to lowercase
        - Replace invalid characters with underscore
        - Prefix with underscore if starts with digit
        - Handle special power net cases

        Args:
            name: Original name (R1, 3V3, etc.)

        Returns:
            Sanitized variable name (r1, _3v3, etc.)

        Examples:
            >>> PythonCodeGenerator._sanitize_variable_name('R1')
            'r1'
            >>> PythonCodeGenerator._sanitize_variable_name('3V3')
            '_3v3'
            >>> PythonCodeGenerator._sanitize_variable_name('U$1')
            'u_1'
        """
        import re

        # Handle special power net cases
        power_nets = {
            '3V3': '_3v3',
            '3.3V': '_3v3',
            '+3V3': '_3v3',
            '+3.3V': '_3v3',
            '5V': '_5v',
            '+5V': '_5v',
            '12V': '_12v',
            '+12V': '_12v',
            'VCC': 'vcc',
            'VDD': 'vdd',
            'GND': 'gnd',
            'VSS': 'vss'
        }

        if name in power_nets:
            return power_nets[name]

        # Convert to lowercase
        var_name = name.lower()

        # Replace invalid characters
        var_name = var_name.replace('$', '_')
        var_name = var_name.replace('+', 'p')
        var_name = var_name.replace('-', 'n')
        var_name = var_name.replace('.', '_')
        var_name = re.sub(r'[^a-z0-9_]', '_', var_name)

        # Remove consecutive underscores
        var_name = re.sub(r'_+', '_', var_name)

        # Strip leading/trailing underscores
        var_name = var_name.strip('_')

        # Prefix if starts with digit or is empty
        if not var_name or var_name[0].isdigit():
            var_name = '_' + var_name

        # Ensure not a Python keyword
        import keyword
        if keyword.iskeyword(var_name):
            var_name = var_name + '_'

        return var_name

    def _format_with_black(self, code: str) -> str:
        """
        Format code using Black formatter.

        Args:
            code: Unformatted Python code

        Returns:
            Formatted code (or original if Black unavailable)
        """
        try:
            import black

            mode = black.Mode(
                target_versions={black.TargetVersion.PY38},
                line_length=88,
                string_normalization=True
            )

            formatted = black.format_str(code, mode=mode)
            return formatted

        except ImportError:
            # Black not available, return unformatted
            return code

        except Exception as e:
            # Black failed, log warning and return unformatted
            import logging
            logging.warning(f"Black formatting failed: {e}")
            return code

    def _validate_syntax(self, code: str) -> None:
        """
        Validate generated code syntax.

        Args:
            code: Generated Python code

        Raises:
            CodeGenerationError: If code has syntax errors
        """
        try:
            compile(code, '<generated>', 'exec')
        except SyntaxError as e:
            from kicad_sch_api.utils.exceptions import CodeGenerationError
            raise CodeGenerationError(
                f"Generated code has syntax error at line {e.lineno}: {e.msg}"
            ) from e
```

---

### 2. CLI Command

**File**: `kicad_sch_api/cli/kicad_to_python.py`

#### Implementation

```python
#!/usr/bin/env python3
"""
KiCad-to-Python CLI Command

Convert KiCad schematic files to executable Python code.

Usage:
    kicad-to-python input.kicad_sch output.py
    kicad-to-python input.kicad_sch output.py --template verbose
    kicad-to-python project.kicad_pro output_dir/ --include-hierarchy
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import kicad_sch_api as ksa
from kicad_sch_api.exporters.python_generator import PythonCodeGenerator
from kicad_sch_api.utils.exceptions import CodeGenerationError


def main(argv: Optional[list] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (None = sys.argv)

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        prog='kicad-to-python',
        description='Convert KiCad schematics to Python code',
        epilog='For more information: https://github.com/circuit-synth/kicad-sch-api'
    )

    # Positional arguments
    parser.add_argument(
        'input',
        type=Path,
        help='Input KiCad schematic (.kicad_sch) or project (.kicad_pro)'
    )

    parser.add_argument(
        'output',
        type=Path,
        help='Output Python file (.py) or directory (for hierarchical)'
    )

    # Options
    parser.add_argument(
        '--template',
        choices=['minimal', 'default', 'verbose', 'documented'],
        default='default',
        help='Code template style (default: default)'
    )

    parser.add_argument(
        '--include-hierarchy',
        action='store_true',
        help='Include hierarchical sheets'
    )

    parser.add_argument(
        '--no-format',
        action='store_true',
        help='Skip Black code formatting'
    )

    parser.add_argument(
        '--no-comments',
        action='store_true',
        help='Skip explanatory comments'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args(argv)

    try:
        # Validate input file
        if not args.input.exists():
            print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
            return 1

        if args.input.suffix not in ['.kicad_sch', '.kicad_pro']:
            print(
                f"❌ Error: Input must be .kicad_sch or .kicad_pro file",
                file=sys.stderr
            )
            return 1

        # Load schematic
        if args.verbose:
            print(f"📖 Loading schematic: {args.input}")

        schematic = ksa.Schematic.load(args.input)

        if args.verbose:
            print(f"   Found {len(schematic.components)} components")
            print(f"   Found {len(schematic.wires)} wires")
            print(f"   Found {len(schematic.labels)} labels")

        # Generate Python code
        if args.verbose:
            print(f"🔨 Generating Python code...")

        generator = PythonCodeGenerator(
            template=args.template,
            format_code=not args.no_format,
            add_comments=not args.no_comments
        )

        code = generator.generate(
            schematic=schematic,
            include_hierarchy=args.include_hierarchy,
            output_path=args.output
        )

        # Report success
        lines = len(code.split('\n'))
        print(f"✅ Generated {args.output} ({lines} lines)")

        if args.verbose:
            print(f"   Template: {args.template}")
            print(f"   Formatted: {not args.no_format}")
            print(f"   Comments: {not args.no_comments}")

        return 0

    except CodeGenerationError as e:
        print(f"❌ Code generation error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def entry_point():
    """Entry point for setuptools console_scripts."""
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())
```

---

### 3. Schematic Export Method

**File**: `kicad_sch_api/core/schematic.py` (addition)

#### Method Addition

```python
class Schematic:
    # ... existing methods ...

    def export_to_python(
        self,
        output_path: Union[str, Path],
        template: str = 'default',
        include_hierarchy: bool = True,
        format_code: bool = True,
        add_comments: bool = True
    ) -> Path:
        """
        Export schematic to executable Python code.

        Generates Python code that uses kicad-sch-api to recreate this
        schematic programmatically.

        Args:
            output_path: Output .py file path
            template: Code template style ('minimal', 'default', 'verbose', 'documented')
            include_hierarchy: Include hierarchical sheets
            format_code: Format code with Black
            add_comments: Add explanatory comments

        Returns:
            Path to generated Python file

        Raises:
            CodeGenerationError: If code generation fails

        Example:
            >>> sch = Schematic.load('circuit.kicad_sch')
            >>> sch.export_to_python('circuit.py')
            Path('circuit.py')

            >>> sch.export_to_python('circuit.py',
            ...                      template='verbose',
            ...                      add_comments=True)
            Path('circuit.py')
        """
        from kicad_sch_api.exporters.python_generator import PythonCodeGenerator

        generator = PythonCodeGenerator(
            template=template,
            format_code=format_code,
            add_comments=add_comments
        )

        generator.generate(
            schematic=self,
            include_hierarchy=include_hierarchy,
            output_path=Path(output_path)
        )

        return Path(output_path)
```

---

### 4. Utility Function

**File**: `kicad_sch_api/__init__.py` (addition)

#### Function Definition

```python
def schematic_to_python(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    template: str = 'default',
    include_hierarchy: bool = True,
    format_code: bool = True,
    add_comments: bool = True
) -> Path:
    """
    Convert KiCad schematic to Python code (one-line convenience function).

    Loads a KiCad schematic and generates executable Python code that
    recreates it using the kicad-sch-api library.

    Args:
        input_path: Input .kicad_sch file
        output_path: Output .py file
        template: Code template style ('minimal', 'default', 'verbose', 'documented')
        include_hierarchy: Include hierarchical sheets
        format_code: Format code with Black
        add_comments: Add explanatory comments

    Returns:
        Path to generated Python file

    Raises:
        FileNotFoundError: If input file doesn't exist
        CodeGenerationError: If code generation fails

    Example:
        >>> import kicad_sch_api as ksa
        >>> ksa.schematic_to_python('input.kicad_sch', 'output.py')
        Path('output.py')

        >>> ksa.schematic_to_python('input.kicad_sch', 'output.py',
        ...                         template='minimal',
        ...                         add_comments=False)
        Path('output.py')
    """
    # Load schematic
    schematic = Schematic.load(input_path)

    # Export to Python
    return schematic.export_to_python(
        output_path=output_path,
        template=template,
        include_hierarchy=include_hierarchy,
        format_code=format_code,
        add_comments=add_comments
    )
```

---

## API Specifications

### Public APIs

#### 1. CLI Command
```bash
kicad-to-python INPUT OUTPUT [OPTIONS]

Arguments:
  INPUT                    Input .kicad_sch or .kicad_pro file
  OUTPUT                   Output .py file or directory

Options:
  --template STYLE         Code template: minimal, default, verbose, documented
  --include-hierarchy      Include hierarchical sheets
  --no-format              Skip Black code formatting
  --no-comments            Skip explanatory comments
  --verbose, -v            Verbose output
  --help, -h               Show help message
```

#### 2. Python API Method
```python
Schematic.export_to_python(
    output_path: Union[str, Path],
    template: str = 'default',
    include_hierarchy: bool = True,
    format_code: bool = True,
    add_comments: bool = True
) -> Path
```

#### 3. Utility Function
```python
ksa.schematic_to_python(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    template: str = 'default',
    include_hierarchy: bool = True,
    format_code: bool = True,
    add_comments: bool = True
) -> Path
```

---

## Data Flow

### Export Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      START: User Request                         │
│                                                                  │
│  CLI: kicad-to-python input.kicad_sch output.py                 │
│  API: sch.export_to_python('output.py')                         │
│  Util: ksa.schematic_to_python('input.kicad_sch', 'output.py') │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STEP 1: Load Schematic                         │
│                                                                  │
│  • Use Schematic.load('input.kicad_sch')                        │
│  • Parse S-expressions                                          │
│  • Build object model                                           │
│  • Validate schematic integrity                                 │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│             STEP 2: Extract Schematic Data                       │
│                                                                  │
│  ┌────────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ _extract_      │  │ _extract_   │  │ _extract_labels()    │ │
│  │ metadata()     │  │ components()│  │                      │ │
│  │                │  │             │  │                      │ │
│  │ • Name         │  │ • Ref       │  │ • Text               │ │
│  │ • Title        │  │ • Value     │  │ • Position           │ │
│  │ • Date         │  │ • Footprint │  │ • Type               │ │
│  │ • Version      │  │ • Position  │  │                      │ │
│  └────────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                                  │
│  ┌────────────────┐  ┌─────────────┐                            │
│  │ _extract_      │  │ _extract_   │                            │
│  │ wires()        │  │ sheets()    │                            │
│  │                │  │ (optional)  │                            │
│  │ • Start point  │  │ • Name      │                            │
│  │ • End point    │  │ • Filename  │                            │
│  │                │  │ • Pins      │                            │
│  └────────────────┘  └─────────────┘                            │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 3: Load Template                              │
│                                                                  │
│  • Select template based on 'template' parameter                │
│  • Load Jinja2 template from templates/ directory               │
│  • Register custom filters (sanitize, etc.)                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: Render Template                             │
│                                                                  │
│  • Pass extracted data to template                              │
│  • Generate imports and header                                  │
│  • Generate component creation code                             │
│  • Generate wire/label creation code                            │
│  • Generate main() and if __name__ block                        │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                STEP 5: Format Code                               │
│                                                                  │
│  • If format_code=True:                                         │
│    - Try to import Black                                        │
│    - Format code with Black                                     │
│    - Fall back to unformatted if Black unavailable              │
│  • Else: Skip formatting                                        │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 6: Validate Syntax                            │
│                                                                  │
│  • Compile generated code with compile()                        │
│  • Check for SyntaxError                                        │
│  • Raise CodeGenerationError if invalid                         │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 7: Write Output File                          │
│                                                                  │
│  • Write code to output_path                                    │
│  • Set encoding to UTF-8                                        │
│  • Make file executable (chmod +x)                              │
│  • Return Path object                                           │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      END: Success                                │
│                                                                  │
│  • Return: Path('output.py')                                    │
│  • User can execute: python output.py                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Formats

### Template Format (Jinja2)

**File**: `kicad_sch_api/exporters/templates/default.py.jinja2`

```python
#!/usr/bin/env python3
"""
{{ metadata.title }}

Generated from: {{ metadata.source_file }}
Generated by: kicad-sch-api v{{ metadata.version }}
Date: {{ metadata.date }}
"""

import kicad_sch_api as ksa

def create_{{ metadata.name|sanitize }}():
    """Create {{ metadata.title }} schematic."""

    # Create schematic
    sch = ksa.create_schematic('{{ metadata.name }}')

    {% if components %}
    # Add components
    {% for comp in components %}
    {{ comp.variable }} = sch.components.add(
        '{{ comp.lib_id }}',
        reference='{{ comp.ref }}',
        value='{{ comp.value }}',
        position=({{ comp.x }}, {{ comp.y }})
        {%- if comp.rotation != 0 %},
        rotation={{ comp.rotation }}
        {%- endif %}
    )
    {%- if comp.footprint %}
    {{ comp.variable }}.footprint = '{{ comp.footprint }}'
    {%- endif %}
    {%- for prop in comp.properties %}
    {{ comp.variable }}.set_property('{{ prop.name }}', '{{ prop.value }}')
    {%- endfor %}

    {% endfor %}
    {% endif %}

    {% if wires %}
    # Add wires
    {% for wire in wires %}
    sch.add_wire(start=({{ wire.start_x }}, {{ wire.start_y }}),
                 end=({{ wire.end_x }}, {{ wire.end_y }}))
    {% endfor %}

    {% endif %}

    {% if labels %}
    # Add labels
    {% for label in labels %}
    sch.add_label('{{ label.text }}',
                  position=({{ label.x }}, {{ label.y }}),
                  label_type='{{ label.type }}')
    {% endfor %}

    {% endif %}

    return sch


if __name__ == '__main__':
    schematic = create_{{ metadata.name|sanitize }}()
    schematic.save('{{ metadata.name }}.kicad_sch')
    print('✅ Schematic generated: {{ metadata.name }}.kicad_sch')
```

---

## Testing Requirements

### Test Coverage Goals
- **Overall**: >90% code coverage
- **Core Functions**: 100% coverage
- **Edge Cases**: Comprehensive edge case testing
- **Reference Tests**: All reference schematics tested

### Test Categories

#### 1. Unit Tests
**Location**: `tests/unit/test_python_generator.py`

```python
class TestPythonCodeGenerator:
    """Test PythonCodeGenerator class."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        gen = PythonCodeGenerator()
        assert gen.template == 'default'
        assert gen.format_code is True
        assert gen.add_comments is True

    def test_sanitize_variable_name(self):
        """Test variable name sanitization."""
        assert PythonCodeGenerator._sanitize_variable_name('R1') == 'r1'
        assert PythonCodeGenerator._sanitize_variable_name('3V3') == '_3v3'
        assert PythonCodeGenerator._sanitize_variable_name('U$1') == 'u_1'
        assert PythonCodeGenerator._sanitize_variable_name('GND') == 'gnd'

    def test_extract_components(self):
        """Test component extraction."""
        # TODO: Implement

    def test_extract_wires(self):
        """Test wire extraction."""
        # TODO: Implement

    def test_extract_labels(self):
        """Test label extraction."""
        # TODO: Implement
```

#### 2. Integration Tests
**Location**: `tests/integration/test_kicad_to_python_export.py`

```python
class TestKicadToPythonExport:
    """Test end-to-end export functionality."""

    def test_export_simple_schematic(self):
        """Test exporting simple single-resistor schematic."""
        sch = ksa.Schematic.load('tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch')
        output = ksa.schematic_to_python(sch, 'temp.py')

        assert output.exists()
        assert output.read_text().startswith('#!/usr/bin/env python3')

    def test_generated_code_is_executable(self):
        """Test that generated code can be executed."""
        # TODO: Implement

    def test_cli_command(self):
        """Test CLI command."""
        # TODO: Implement
```

#### 3. Round-Trip Tests
**Location**: `tests/integration/test_round_trip.py`

```python
class TestRoundTrip:
    """Test round-trip conversion: schematic → python → schematic."""

    def test_round_trip_single_resistor(self):
        """Test round-trip for single resistor."""
        # 1. Load original
        original = ksa.Schematic.load('tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch')

        # 2. Export to Python
        python_code = ksa.schematic_to_python(original, 'temp.py')

        # 3. Execute Python code
        exec_globals = {}
        exec(compile(python_code.read_text(), 'temp.py', 'exec'), exec_globals)

        # 4. Load regenerated schematic
        regenerated = ksa.Schematic.load('temp_output.kicad_sch')

        # 5. Compare
        assert original.components.count() == regenerated.components.count()
        assert original.wires.count() == regenerated.wires.count()

    def test_round_trip_resistor_divider(self):
        """Test round-trip for resistor divider."""
        # TODO: Implement

    def test_round_trip_hierarchical(self):
        """Test round-trip for hierarchical schematic."""
        # TODO: Implement
```

#### 4. Template Tests
**Location**: `tests/unit/test_templates.py`

```python
class TestTemplates:
    """Test template rendering."""

    def test_minimal_template(self):
        """Test minimal template produces compact code."""
        # TODO: Implement

    def test_default_template(self):
        """Test default template."""
        # TODO: Implement

    def test_verbose_template(self):
        """Test verbose template includes all details."""
        # TODO: Implement

    def test_documented_template(self):
        """Test documented template includes docstrings."""
        # TODO: Implement
```

---

## Performance Requirements

### Performance Targets

| Schematic Size | Components | Target Time | Max Memory |
|----------------|------------|-------------|------------|
| Small          | <10        | <100ms      | <10MB      |
| Medium         | 10-100     | <1s         | <50MB      |
| Large          | 100-1000   | <5s         | <200MB     |
| Very Large     | >1000      | <30s        | <500MB     |

### Performance Optimizations

1. **Lazy Loading**: Don't load templates until needed
2. **Caching**: Cache template compilation
3. **Streaming**: Write large output files incrementally
4. **Parallel Processing**: Process hierarchical sheets in parallel (future)

---

## Security Considerations

### Input Validation
- Validate input file exists and is readable
- Check file extension (.kicad_sch, .kicad_pro)
- Sanitize all user-provided paths
- Prevent path traversal attacks

### Code Generation Safety
- Escape all user-controlled strings in templates
- Validate variable names against Python keywords
- Limit output file size to prevent disk exhaustion
- Use safe template rendering (Jinja2 autoescape)

### Execution Safety
- Never execute generated code automatically
- Warn users before overwriting existing files
- Validate generated code syntax before writing
- Use safe file permissions (644 for code, 755 for executables)

---

## Deployment

### Package Dependencies

**Required**:
- `kicad-sch-api` (existing)
- `jinja2` >= 3.0

**Optional**:
- `black` >= 22.0 (for code formatting)

### Installation

```bash
# Install with default dependencies
pip install kicad-sch-api[export]

# Or if already installed
pip install jinja2
```

### CLI Registration

**pyproject.toml**:
```toml
[project.scripts]
kicad-to-python = "kicad_sch_api.cli.kicad_to_python:entry_point"
```

---

## Error Handling

### Exception Hierarchy

```python
kicad_sch_api/utils/exceptions.py

class KicadSchApiException(Exception):
    """Base exception for kicad-sch-api."""

class CodeGenerationError(KicadSchApiException):
    """Error during Python code generation."""

class TemplateNotFoundError(CodeGenerationError):
    """Template file not found."""

class InvalidTemplateError(CodeGenerationError):
    """Template is malformed or invalid."""
```

### Error Messages

**Good Error Messages**:
```
❌ Error: Input file not found: circuit.kicad_sch

❌ Code generation error: Generated code has syntax error at line 42:
   invalid syntax in component 'R$1' variable name

❌ Template error: Template 'custom' not found.
   Available templates: minimal, default, verbose, documented
```

---

**End of ERD**
