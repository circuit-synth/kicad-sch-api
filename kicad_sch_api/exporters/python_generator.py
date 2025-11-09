"""
Python Code Generator for KiCad Schematics.

This module converts loaded KiCad schematic objects into executable Python code
that uses the kicad-sch-api library to recreate the schematic.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, PackageLoader, select_autoescape

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class CodeGenerationError(Exception):
    """Error during Python code generation."""

    pass


class TemplateNotFoundError(CodeGenerationError):
    """Template file not found."""

    pass


class PythonCodeGenerator:
    """
    Generate executable Python code from KiCad schematics.

    This class converts loaded Schematic objects into executable Python
    code that uses the kicad-sch-api to recreate the schematic.

    Attributes:
        template: Template style ('minimal', 'default', 'verbose', 'documented')
        format_code: Whether to format code with Black
        add_comments: Whether to add explanatory comments
    """

    def __init__(
        self, template: str = "default", format_code: bool = True, add_comments: bool = True
    ):
        """
        Initialize code generator.

        Args:
            template: Template style to use ('minimal', 'default', 'verbose', 'documented')
            format_code: Format output with Black (if available)
            add_comments: Add explanatory comments
        """
        self.template = template
        self.format_code = format_code
        self.add_comments = add_comments

        # Initialize Jinja2 environment if available
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment(
                loader=PackageLoader("kicad_sch_api", "exporters/templates"),
                trim_blocks=True,
                lstrip_blocks=True,
                autoescape=select_autoescape(["html", "xml"]),
            )
            # Register custom filters
            self.jinja_env.filters["sanitize"] = self._sanitize_variable_name
        else:
            self.jinja_env = None

    def generate(
        self,
        schematic,  # Type: Schematic (avoid circular import)
        include_hierarchy: bool = True,
        output_path: Optional[Path] = None,
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

        # Generate code using template or fallback
        if self.jinja_env and self.template != "minimal":
            code = self._generate_with_template(data)
        else:
            # Use simple string-based generation for minimal or if Jinja2 unavailable
            code = self._generate_minimal(data)

        # Format code
        if self.format_code:
            code = self._format_with_black(code)

        # Validate syntax
        self._validate_syntax(code)

        # Write to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(code, encoding="utf-8")
            # Make executable on Unix-like systems
            try:
                output_path.chmod(0o755)
            except Exception:
                pass  # Windows doesn't support chmod

        return code

    def _extract_schematic_data(self, schematic, include_hierarchy: bool) -> Dict[str, Any]:
        """
        Extract all data from schematic for code generation.

        Args:
            schematic: Schematic to extract from
            include_hierarchy: Include hierarchical sheets

        Returns:
            Dictionary with all template data
        """
        return {
            "metadata": self._extract_metadata(schematic),
            "components": self._extract_components(schematic),
            "wires": self._extract_wires(schematic),
            "labels": self._extract_labels(schematic),
            "sheets": self._extract_sheets(schematic) if include_hierarchy else [],
            "options": {"add_comments": self.add_comments, "include_hierarchy": include_hierarchy},
        }

    def _extract_metadata(self, schematic) -> Dict[str, Any]:
        """Extract schematic metadata."""
        import kicad_sch_api

        # Get project name from schematic
        name = getattr(schematic, "name", None) or "untitled"

        # Get title from title block if available
        title = ""
        if hasattr(schematic, "title_block") and schematic.title_block:
            title = getattr(schematic.title_block, "title", "")

        if not title:
            title = name

        return {
            "name": name,
            "title": title,
            "version": kicad_sch_api.__version__,
            "date": datetime.now().isoformat(),
            "source_file": (
                str(schematic.filepath)
                if hasattr(schematic, "filepath") and schematic.filepath
                else "unknown"
            ),
        }

    def _extract_components(self, schematic) -> List[Dict[str, Any]]:
        """
        Extract component data.

        Returns:
            List of component dictionaries
        """
        components = []

        # Access components collection
        comp_collection = schematic.components if hasattr(schematic, "components") else []

        for comp in comp_collection:
            # Extract component properties
            ref = getattr(comp, "reference", "") or getattr(comp, "ref", "")
            lib_id = getattr(comp, "lib_id", "") or getattr(comp, "symbol", "")
            value = getattr(comp, "value", "")
            footprint = getattr(comp, "footprint", "")

            # Get position
            pos = getattr(comp, "position", None)
            if pos:
                x = getattr(pos, "x", 0.0)
                y = getattr(pos, "y", 0.0)
            else:
                x, y = 0.0, 0.0

            # Get rotation
            rotation = getattr(comp, "rotation", 0)

            comp_data = {
                "ref": ref,
                "variable": self._sanitize_variable_name(ref),
                "lib_id": lib_id,
                "value": value,
                "footprint": footprint,
                "x": x,
                "y": y,
                "rotation": rotation,
                "properties": self._extract_custom_properties(comp),
            }
            components.append(comp_data)

        return components

    def _extract_wires(self, schematic) -> List[Dict[str, Any]]:
        """
        Extract wire data.

        Returns:
            List of wire dictionaries
        """
        wires = []

        # Access wires collection
        wire_collection = schematic.wires if hasattr(schematic, "wires") else []

        for wire in wire_collection:
            # Get start and end points
            start = getattr(wire, "start", None)
            end = getattr(wire, "end", None)

            if start and end:
                wire_data = {
                    "start_x": getattr(start, "x", 0.0),
                    "start_y": getattr(start, "y", 0.0),
                    "end_x": getattr(end, "x", 0.0),
                    "end_y": getattr(end, "y", 0.0),
                    "style": getattr(wire, "style", "solid"),
                }
                wires.append(wire_data)

        return wires

    def _extract_labels(self, schematic) -> List[Dict[str, Any]]:
        """
        Extract label data.

        Returns:
            List of label dictionaries
        """
        labels = []

        # Access labels collection
        label_collection = schematic.labels if hasattr(schematic, "labels") else []

        for label in label_collection:
            # Get label properties
            text = getattr(label, "text", "")
            pos = getattr(label, "position", None)

            if pos:
                x = getattr(pos, "x", 0.0)
                y = getattr(pos, "y", 0.0)
            else:
                x, y = 0.0, 0.0

            label_type = getattr(label, "label_type", "local")
            rotation = getattr(label, "rotation", 0)

            label_data = {"text": text, "x": x, "y": y, "type": label_type, "rotation": rotation}
            labels.append(label_data)

        return labels

    def _extract_sheets(self, schematic) -> List[Dict[str, Any]]:
        """
        Extract hierarchical sheet data.

        Returns:
            List of sheet dictionaries
        """
        sheets = []

        # Access sheets collection if available
        if not hasattr(schematic, "sheets"):
            return sheets

        # SheetManager doesn't support direct iteration
        # For now, return empty list - hierarchical support is Phase 3
        # TODO: Implement when SheetManager has proper iteration support
        return sheets

        # The code below is for future when SheetManager is iterable:
        for sheet in getattr(schematic.sheets, "data", []):
            # Get sheet properties
            name = getattr(sheet, "name", "")
            filename = getattr(sheet, "filename", "")

            pos = getattr(sheet, "position", None)
            size = getattr(sheet, "size", None)

            if pos:
                x = getattr(pos, "x", 0.0)
                y = getattr(pos, "y", 0.0)
            else:
                x, y = 0.0, 0.0

            if size:
                width = getattr(size, "width", 100.0)
                height = getattr(size, "height", 100.0)
            else:
                width, height = 100.0, 100.0

            # Extract pins
            pins = []
            if hasattr(sheet, "pins"):
                for pin in sheet.pins:
                    pin_pos = getattr(pin, "position", None)
                    pins.append(
                        {
                            "name": getattr(pin, "name", ""),
                            "type": getattr(pin, "pin_type", "input"),
                            "x": getattr(pin_pos, "x", 0.0) if pin_pos else 0.0,
                            "y": getattr(pin_pos, "y", 0.0) if pin_pos else 0.0,
                        }
                    )

            sheet_data = {
                "name": name,
                "filename": filename,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "pins": pins,
            }
            sheets.append(sheet_data)

        return sheets

    def _extract_custom_properties(self, component) -> List[Dict[str, str]]:
        """
        Extract custom component properties.

        Returns:
            List of property dictionaries
        """
        # Standard properties to exclude
        standard_props = {
            "Reference",
            "Value",
            "Footprint",
            "Datasheet",
            "ki_keywords",
            "ki_description",
            "ki_fp_filters",
            "Description",  # Also exclude Description as it's often auto-generated
        }

        properties = []

        # Get properties if available
        if hasattr(component, "properties"):
            comp_props = component.properties
            if isinstance(comp_props, dict):
                for prop_name, prop_value in comp_props.items():
                    # Skip internal properties (start with __)
                    if prop_name.startswith("__"):
                        continue
                    # Skip standard properties
                    if prop_name in standard_props:
                        continue
                    # Skip if value contains non-serializable content
                    str_value = str(prop_value)
                    if "Symbol(" in str_value or "[Symbol(" in str_value:
                        continue

                    properties.append({"name": prop_name, "value": str_value})

        return properties

    @staticmethod
    def _sanitize_variable_name(name: str) -> str:
        """
        Convert reference/name to valid Python variable name.

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
        import keyword

        # Handle special power net cases
        power_nets = {
            "3V3": "_3v3",
            "3.3V": "_3v3",
            "+3V3": "_3v3",
            "+3.3V": "_3v3",
            "5V": "_5v",
            "+5V": "_5v",
            "12V": "_12v",
            "+12V": "_12v",
            "VCC": "vcc",
            "VDD": "vdd",
            "GND": "gnd",
            "VSS": "vss",
        }

        if name in power_nets:
            return power_nets[name]

        # Convert to lowercase
        var_name = name.lower()

        # Replace invalid characters
        var_name = var_name.replace("$", "_")
        var_name = var_name.replace("+", "p")
        var_name = var_name.replace("-", "n")
        var_name = var_name.replace(".", "_")
        var_name = re.sub(r"[^a-z0-9_]", "_", var_name)

        # Remove consecutive underscores
        var_name = re.sub(r"_+", "_", var_name)

        # Strip leading/trailing underscores
        var_name = var_name.strip("_")

        # Prefix if starts with digit or is empty
        if not var_name or var_name[0].isdigit():
            var_name = "_" + var_name

        # Ensure not a Python keyword
        if keyword.iskeyword(var_name):
            var_name = var_name + "_"

        return var_name

    def _generate_with_template(self, data: Dict[str, Any]) -> str:
        """
        Generate code using Jinja2 template.

        Args:
            data: Template data

        Returns:
            Generated code

        Raises:
            TemplateNotFoundError: If template not found
        """
        try:
            template = self.jinja_env.get_template(f"{self.template}.py.jinja2")
            code = template.render(**data)
            return code
        except Exception as e:
            raise TemplateNotFoundError(
                f"Template '{self.template}' not found or invalid: {e}"
            ) from e

    def _generate_minimal(self, data: Dict[str, Any]) -> str:
        """
        Generate minimal Python code without templates.

        This is a fallback when Jinja2 is not available or for minimal template.

        Args:
            data: Extracted schematic data

        Returns:
            Generated Python code
        """
        lines = []

        # Header
        lines.append("#!/usr/bin/env python3")
        lines.append('"""')
        lines.append(f"{data['metadata']['title']}")
        lines.append("")
        lines.append(f"Generated from: {data['metadata']['source_file']}")
        lines.append(f"Generated by: kicad-sch-api v{data['metadata']['version']}")
        lines.append('"""')
        lines.append("")
        lines.append("import kicad_sch_api as ksa")
        lines.append("")

        # Function definition
        func_name = self._sanitize_variable_name(data["metadata"]["name"])
        lines.append(f"def create_{func_name}():")
        lines.append(f'    """Create {data["metadata"]["title"]} schematic."""')
        lines.append("")

        # Create schematic
        lines.append("    # Create schematic")
        lines.append(f"    sch = ksa.create_schematic('{data['metadata']['name']}')")
        lines.append("")

        # Add components
        if data["components"]:
            lines.append("    # Add components")
            for comp in data["components"]:
                lines.append(f"    {comp['variable']} = sch.components.add(")
                lines.append(f"        '{comp['lib_id']}',")
                lines.append(f"        reference='{comp['ref']}',")
                lines.append(f"        value='{comp['value']}',")
                lines.append(f"        position=({comp['x']}, {comp['y']})")
                if comp["rotation"] != 0:
                    lines.append(f"        rotation={comp['rotation']}")
                lines.append("    )")
                if comp["footprint"]:
                    lines.append(f"    {comp['variable']}.footprint = '{comp['footprint']}'")
                for prop in comp["properties"]:
                    lines.append(
                        f"    {comp['variable']}.set_property('{prop['name']}', '{prop['value']}')"
                    )
                lines.append("")

        # Add wires
        if data["wires"]:
            lines.append("    # Add wires")
            for wire in data["wires"]:
                lines.append(f"    sch.add_wire(")
                lines.append(f"        start=({wire['start_x']}, {wire['start_y']}),")
                lines.append(f"        end=({wire['end_x']}, {wire['end_y']})")
                lines.append("    )")
            lines.append("")

        # Add labels
        if data["labels"]:
            lines.append("    # Add labels")
            for label in data["labels"]:
                lines.append(f"    sch.add_label(")
                lines.append(f"        '{label['text']}',")
                lines.append(f"        position=({label['x']}, {label['y']})")
                lines.append("    )")
            lines.append("")

        # Return
        lines.append("    return sch")
        lines.append("")
        lines.append("")

        # Main block
        lines.append("if __name__ == '__main__':")
        lines.append(f"    schematic = create_{func_name}()")
        lines.append(f"    schematic.save('{data['metadata']['name']}.kicad_sch')")
        lines.append(f"    print('✅ Schematic generated: {data['metadata']['name']}.kicad_sch')")
        lines.append("")

        return "\n".join(lines)

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
                string_normalization=True,
            )

            formatted = black.format_str(code, mode=mode)
            return formatted

        except ImportError:
            # Black not available, return unformatted
            return code

        except Exception:
            # Black failed, return unformatted
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
            compile(code, "<generated>", "exec")
        except SyntaxError as e:
            raise CodeGenerationError(
                f"Generated code has syntax error at line {e.lineno}: {e.msg}"
            ) from e
