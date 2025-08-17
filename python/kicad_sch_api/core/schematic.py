"""
Main Schematic class for KiCAD schematic manipulation.

This module provides the primary interface for loading, modifying, and saving
KiCAD schematic files with exact format preservation and professional features.
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..library.cache import get_symbol_cache
from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .components import ComponentCollection
from .formatter import ExactFormatter
from .parser import SExpressionParser
from .types import Junction, Label, Net, Point, SchematicSymbol, TitleBlock, Wire, LabelType, HierarchicalLabelShape, WireType
from .wires import WireCollection
from .junctions import JunctionCollection

logger = logging.getLogger(__name__)


class Schematic:
    """
    Professional KiCAD schematic manipulation class.

    Features:
    - Exact format preservation
    - Enhanced component management with fast lookup
    - Advanced library integration
    - Comprehensive validation
    - Performance optimization for large schematics
    - AI agent integration via MCP

    This class provides a modern, intuitive API while maintaining exact compatibility
    with KiCAD's native file format.
    """

    def __init__(self, schematic_data: Dict[str, Any] = None, file_path: Optional[str] = None):
        """
        Initialize schematic object.

        Args:
            schematic_data: Parsed schematic data
            file_path: Original file path (for format preservation)
        """
        # Core data
        self._data = schematic_data or self._create_empty_schematic_data()
        self._file_path = Path(file_path) if file_path else None
        self._original_content = self._data.get("_original_content", "")

        # Initialize parser and formatter
        self._parser = SExpressionParser(preserve_format=True)
        self._formatter = ExactFormatter()
        self._validator = SchematicValidator()

        # Initialize component collection
        component_symbols = [
            SchematicSymbol(**comp) if isinstance(comp, dict) else comp
            for comp in self._data.get("components", [])
        ]
        self._components = ComponentCollection(component_symbols)

        # Initialize wire collection
        wire_data = self._data.get("wires", [])
        wires = []
        for wire_dict in wire_data:
            if isinstance(wire_dict, dict):
                # Convert dict to Wire object
                points = []
                for point_data in wire_dict.get("points", []):
                    if isinstance(point_data, dict):
                        points.append(Point(point_data["x"], point_data["y"]))
                    elif isinstance(point_data, (list, tuple)):
                        points.append(Point(point_data[0], point_data[1]))
                    else:
                        points.append(point_data)
                
                wire = Wire(
                    uuid=wire_dict.get("uuid", str(uuid.uuid4())),
                    points=points,
                    wire_type=WireType(wire_dict.get("wire_type", "wire")),
                    stroke_width=wire_dict.get("stroke_width", 0.0),
                    stroke_type=wire_dict.get("stroke_type", "default")
                )
                wires.append(wire)
        self._wires = WireCollection(wires)

        # Initialize junction collection
        junction_data = self._data.get("junctions", [])
        junctions = []
        for junction_dict in junction_data:
            if isinstance(junction_dict, dict):
                # Convert dict to Junction object
                position = junction_dict.get("position", {"x": 0, "y": 0})
                if isinstance(position, dict):
                    pos = Point(position["x"], position["y"])
                elif isinstance(position, (list, tuple)):
                    pos = Point(position[0], position[1])
                else:
                    pos = position
                
                junction = Junction(
                    uuid=junction_dict.get("uuid", str(uuid.uuid4())),
                    position=pos,
                    diameter=junction_dict.get("diameter", 0),
                    color=junction_dict.get("color", (0, 0, 0, 0))
                )
                junctions.append(junction)
        self._junctions = JunctionCollection(junctions)

        # Track modifications for save optimization
        self._modified = False
        self._last_save_time = None

        # Performance tracking
        self._operation_count = 0
        self._total_operation_time = 0.0

        logger.debug(f"Schematic initialized with {len(self._components)} components, {len(self._wires)} wires, and {len(self._junctions)} junctions")

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "Schematic":
        """
        Load a KiCAD schematic file.

        Args:
            file_path: Path to .kicad_sch file

        Returns:
            Loaded Schematic object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If file is invalid or corrupted
        """
        start_time = time.time()
        file_path = Path(file_path)

        logger.info(f"Loading schematic: {file_path}")

        parser = SExpressionParser(preserve_format=True)
        schematic_data = parser.parse_file(file_path)

        load_time = time.time() - start_time
        logger.info(f"Loaded schematic in {load_time:.3f}s")

        return cls(schematic_data, str(file_path))

    @classmethod
    def create(cls, name: str = "Untitled", version: str = "20250114", 
               generator: str = "eeschema", generator_version: str = "9.0",
               paper: str = "A4", uuid: str = None) -> "Schematic":
        """
        Create a new empty schematic with configurable parameters.

        Args:
            name: Schematic name
            version: KiCAD version (default: "20250114")
            generator: Generator name (default: "eeschema") 
            generator_version: Generator version (default: "9.0")
            paper: Paper size (default: "A4")
            uuid: Specific UUID (auto-generated if None)

        Returns:
            New empty Schematic object
        """
        schematic_data = cls._create_empty_schematic_data()
        schematic_data["version"] = version
        schematic_data["generator"] = generator
        schematic_data["generator_version"] = generator_version
        schematic_data["paper"] = paper
        if uuid:
            schematic_data["uuid"] = uuid
        schematic_data["title_block"] = {"title": name}

        logger.info(f"Created new schematic: {name}")
        return cls(schematic_data)

    # Core properties
    @property
    def components(self) -> ComponentCollection:
        """Collection of all components in the schematic."""
        return self._components

    @property
    def wires(self) -> WireCollection:
        """Collection of all wires in the schematic."""
        return self._wires

    @property
    def junctions(self) -> JunctionCollection:
        """Collection of all junctions in the schematic."""
        return self._junctions

    @property
    def version(self) -> Optional[str]:
        """KiCAD version string."""
        return self._data.get("version")

    @property
    def generator(self) -> Optional[str]:
        """Generator string (e.g., 'eeschema')."""
        return self._data.get("generator")

    @property
    def uuid(self) -> Optional[str]:
        """Schematic UUID."""
        return self._data.get("uuid")

    @property
    def title_block(self) -> Dict[str, Any]:
        """Title block information."""
        return self._data.get("title_block", {})

    @property
    def file_path(self) -> Optional[Path]:
        """Current file path."""
        return self._file_path

    @property
    def modified(self) -> bool:
        """Whether schematic has been modified since last save."""
        return self._modified or self._components._modified

    # File operations
    def save(self, file_path: Optional[Union[str, Path]] = None, preserve_format: bool = True):
        """
        Save schematic to file.

        Args:
            file_path: Output file path (uses current path if None)
            preserve_format: Whether to preserve exact formatting

        Raises:
            ValidationError: If schematic data is invalid
        """
        start_time = time.time()

        # Use current file path if not specified
        if file_path is None:
            if self._file_path is None:
                raise ValidationError("No file path specified and no current file")
            file_path = self._file_path
        else:
            file_path = Path(file_path)
            self._file_path = file_path

        # Validate before saving
        issues = self.validate()
        errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
        if errors:
            raise ValidationError("Cannot save schematic with validation errors", errors)

        # Update data structure with current component, wire, and junction state
        self._sync_components_to_data()
        self._sync_wires_to_data()
        self._sync_junctions_to_data()

        # Write file
        if preserve_format and self._original_content:
            # Use format-preserving writer
            sexp_data = self._parser._schematic_data_to_sexp(self._data)
            content = self._formatter.format_preserving_write(sexp_data, self._original_content)
        else:
            # Standard formatting
            sexp_data = self._parser._schematic_data_to_sexp(self._data)
            content = self._formatter.format(sexp_data)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Update state
        self._modified = False
        self._components._modified = False
        self._last_save_time = time.time()

        save_time = time.time() - start_time
        logger.info(f"Saved schematic to {file_path} in {save_time:.3f}s")

    def save_as(self, file_path: Union[str, Path], preserve_format: bool = True):
        """Save schematic to a new file path."""
        self.save(file_path, preserve_format)

    def backup(self, suffix: str = ".backup") -> Path:
        """
        Create a backup of the current schematic file.

        Args:
            suffix: Suffix to add to backup filename

        Returns:
            Path to backup file
        """
        if not self._file_path:
            raise ValidationError("Cannot backup - no file path set")

        backup_path = self._file_path.with_suffix(self._file_path.suffix + suffix)

        if self._file_path.exists():
            import shutil

            shutil.copy2(self._file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

        return backup_path

    # Validation and analysis
    def validate(self) -> List[ValidationIssue]:
        """
        Validate the schematic for errors and issues.

        Returns:
            List of validation issues found
        """
        # Sync current state to data for validation
        self._sync_components_to_data()

        # Use validator to check schematic
        issues = self._validator.validate_schematic_data(self._data)

        # Add component-level validation
        component_issues = self._components.validate_all()
        issues.extend(component_issues)

        return issues
    
    # Focused helper functions for specific KiCAD sections
    def add_lib_symbols_section(self, lib_symbols: Dict[str, Any]):
        """Add or update lib_symbols section with specific symbol definitions."""
        self._data["lib_symbols"] = lib_symbols
        self._modified = True
    
    def add_instances_section(self, instances: Dict[str, Any]):
        """Add instances section for component placement tracking."""
        self._data["instances"] = instances
        self._modified = True
    
    def add_sheet_instances_section(self, sheet_instances: List[Dict]):
        """Add sheet_instances section for hierarchical design."""
        self._data["sheet_instances"] = sheet_instances  
        self._modified = True
    
    def set_paper_size(self, paper: str):
        """Set paper size (A4, A3, etc.)."""
        self._data["paper"] = paper
        self._modified = True
    
    def set_version_info(self, version: str, generator: str = "eeschema", generator_version: str = "9.0"):
        """Set version and generator information."""
        self._data["version"] = version
        self._data["generator"] = generator  
        self._data["generator_version"] = generator_version
        self._modified = True
    
    def copy_metadata_from(self, source_schematic: "Schematic"):
        """Copy all metadata from another schematic (version, generator, paper, etc.)."""
        metadata_fields = ["version", "generator", "generator_version", "paper", "uuid", "title_block"]
        for field in metadata_fields:
            if field in source_schematic._data:
                self._data[field] = source_schematic._data[field]
        self._modified = True

    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about the schematic."""
        component_stats = self._components.get_statistics()

        return {
            "file_path": str(self._file_path) if self._file_path else None,
            "version": self.version,
            "uuid": self.uuid,
            "title": self.title_block.get("title", ""),
            "component_count": len(self._components),
            "modified": self.modified,
            "last_save": self._last_save_time,
            "component_stats": component_stats,
            "performance": {
                "operation_count": self._operation_count,
                "avg_operation_time_ms": round(
                    (
                        (self._total_operation_time / self._operation_count * 1000)
                        if self._operation_count > 0
                        else 0
                    ),
                    2,
                ),
            },
        }

    # Wire and connection management (basic implementation)
    def add_wire(
        self, start: Union[Point, Tuple[float, float]], end: Union[Point, Tuple[float, float]]
    ) -> str:
        """
        Add a wire connection.

        Args:
            start: Start point
            end: End point

        Returns:
            UUID of created wire
        """
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        wire = Wire(uuid=str(uuid.uuid4()), start=start, end=end)

        if "wires" not in self._data:
            self._data["wires"] = []

        self._data["wires"].append(wire.__dict__)
        self._modified = True

        logger.debug(f"Added wire: {start} -> {end}")
        return wire.uuid

    def remove_wire(self, wire_uuid: str) -> bool:
        """Remove wire by UUID."""
        wires = self._data.get("wires", [])
        for i, wire in enumerate(wires):
            if wire.get("uuid") == wire_uuid:
                del wires[i]
                self._modified = True
                logger.debug(f"Removed wire: {wire_uuid}")
                return True
        return False

    # Label management
    def add_hierarchical_label(
        self, 
        text: str, 
        position: Union[Point, Tuple[float, float]], 
        shape: HierarchicalLabelShape = HierarchicalLabelShape.INPUT,
        rotation: float = 0.0,
        size: float = 1.27
    ) -> str:
        """
        Add a hierarchical label.

        Args:
            text: Label text
            position: Label position
            shape: Label shape/direction
            rotation: Text rotation in degrees
            size: Font size

        Returns:
            UUID of created hierarchical label
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        label = Label(
            uuid=str(uuid.uuid4()),
            position=position,
            text=text,
            label_type=LabelType.HIERARCHICAL,
            rotation=rotation,
            size=size,
            shape=shape
        )

        if "hierarchical_labels" not in self._data:
            self._data["hierarchical_labels"] = []

        self._data["hierarchical_labels"].append({
            "uuid": label.uuid,
            "position": {"x": label.position.x, "y": label.position.y},
            "text": label.text,
            "shape": label.shape.value,
            "rotation": label.rotation,
            "size": label.size
        })
        self._modified = True

        logger.debug(f"Added hierarchical label: {text} at {position}")
        return label.uuid

    def remove_hierarchical_label(self, label_uuid: str) -> bool:
        """Remove hierarchical label by UUID."""
        labels = self._data.get("hierarchical_labels", [])
        for i, label in enumerate(labels):
            if label.get("uuid") == label_uuid:
                del labels[i]
                self._modified = True
                logger.debug(f"Removed hierarchical label: {label_uuid}")
                return True
        return False

    # Library management
    @property
    def libraries(self) -> "LibraryManager":
        """Access to library management."""
        if not hasattr(self, "_library_manager"):
            from ..library.manager import LibraryManager

            self._library_manager = LibraryManager(self)
        return self._library_manager

    # Utility methods
    def clear(self):
        """Clear all components, wires, and other elements."""
        self._data["components"] = []
        self._data["wires"] = []
        self._data["junctions"] = []
        self._data["labels"] = []
        self._components = ComponentCollection()
        self._modified = True
        logger.info("Cleared schematic")

    def clone(self, new_name: Optional[str] = None) -> "Schematic":
        """Create a copy of this schematic."""
        import copy

        cloned_data = copy.deepcopy(self._data)

        if new_name:
            cloned_data["title_block"]["title"] = new_name
            cloned_data["uuid"] = str(uuid.uuid4())  # New UUID for clone

        return Schematic(cloned_data)

    # Performance optimization
    def rebuild_indexes(self):
        """Rebuild internal indexes for performance."""
        # This would rebuild component indexes, etc.
        logger.info("Rebuilt schematic indexes")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_stats = get_symbol_cache().get_performance_stats()

        return {
            "schematic": {
                "operation_count": self._operation_count,
                "total_operation_time_s": round(self._total_operation_time, 3),
                "avg_operation_time_ms": round(
                    (
                        (self._total_operation_time / self._operation_count * 1000)
                        if self._operation_count > 0
                        else 0
                    ),
                    2,
                ),
            },
            "components": self._components.get_statistics(),
            "symbol_cache": cache_stats,
        }

    # Internal methods
    def _sync_components_to_data(self):
        """Sync component collection state back to data structure."""
        self._data["components"] = [comp._data.__dict__ for comp in self._components]
        
        # Populate lib_symbols with actual symbol definitions used by components
        lib_symbols = {}
        cache = get_symbol_cache()
        
        for comp in self._components:
            if comp.lib_id and comp.lib_id not in lib_symbols:
                # Get the actual symbol definition
                symbol_def = cache.get_symbol(comp.lib_id)
                if symbol_def:
                    lib_symbols[comp.lib_id] = self._convert_symbol_to_kicad_format(symbol_def, comp.lib_id)
                else:
                    # Fallback for unknown symbols
                    lib_symbols[comp.lib_id] = {"definition": "basic"}
        
        self._data["lib_symbols"] = lib_symbols

    def _sync_wires_to_data(self):
        """Sync wire collection state back to data structure."""
        wire_data = []
        for wire in self._wires:
            wire_dict = {
                "uuid": wire.uuid,
                "points": [{"x": p.x, "y": p.y} for p in wire.points],
                "wire_type": wire.wire_type.value,
                "stroke_width": wire.stroke_width,
                "stroke_type": wire.stroke_type
            }
            wire_data.append(wire_dict)
        
        self._data["wires"] = wire_data

    def _sync_junctions_to_data(self):
        """Sync junction collection state back to data structure."""
        junction_data = []
        for junction in self._junctions:
            junction_dict = {
                "uuid": junction.uuid,
                "position": {"x": junction.position.x, "y": junction.position.y},
                "diameter": junction.diameter,
                "color": junction.color
            }
            junction_data.append(junction_dict)
        
        self._data["junctions"] = junction_data

    def _convert_symbol_to_kicad_format(self, symbol: "SymbolDefinition", lib_id: str) -> Dict[str, Any]:
        """Convert SymbolDefinition to KiCAD lib_symbols format using raw parsed data."""
        # If we have raw KiCAD data from the library file, use it directly
        if hasattr(symbol, 'raw_kicad_data') and symbol.raw_kicad_data:
            return self._convert_raw_symbol_data(symbol.raw_kicad_data, lib_id)
        
        # Fallback: create basic symbol structure  
        return {
            "pin_numbers": {"hide": "yes"},
            "pin_names": {"offset": 0},
            "exclude_from_sim": "no",
            "in_bom": "yes", 
            "on_board": "yes",
            "properties": {
                "Reference": {
                    "value": symbol.reference_prefix,
                    "at": [2.032, 0, 90],
                    "effects": {"font": {"size": [1.27, 1.27]}}
                },
                "Value": {
                    "value": symbol.reference_prefix,
                    "at": [0, 0, 90],
                    "effects": {"font": {"size": [1.27, 1.27]}}
                },
                "Footprint": {
                    "value": "",
                    "at": [-1.778, 0, 90],
                    "effects": {
                        "font": {"size": [1.27, 1.27]},
                        "hide": "yes"
                    }
                },
                "Datasheet": {
                    "value": getattr(symbol, 'Datasheet', None) or getattr(symbol, 'datasheet', None) or "~",
                    "at": [0, 0, 0],
                    "effects": {
                        "font": {"size": [1.27, 1.27]},
                        "hide": "yes"
                    }
                },
                "Description": {
                    "value": getattr(symbol, 'Description', None) or getattr(symbol, 'description', None) or "Resistor",
                    "at": [0, 0, 0],
                    "effects": {
                        "font": {"size": [1.27, 1.27]},
                        "hide": "yes"
                    }
                }
            },
            "embedded_fonts": "no"
        }

    def _convert_raw_symbol_data(self, raw_data: List, lib_id: str) -> Dict[str, Any]:
        """Convert raw parsed KiCAD symbol data to dictionary format for S-expression generation."""
        import copy
        import sexpdata
        
        # Make a copy and fix symbol name and string/symbol issues
        modified_data = copy.deepcopy(raw_data)
        
        # Replace the symbol name with the full lib_id
        if len(modified_data) >= 2:
            modified_data[1] = lib_id  # Change 'R' to 'Device:R'
        
        # Fix string/symbol conversion issues in pin definitions
        print(f"🔧 DEBUG: Before fix - checking for pin definitions...")
        self._fix_symbol_strings_recursively(modified_data)
        print(f"🔧 DEBUG: After fix - symbol strings fixed")
        
        return modified_data

    def _fix_symbol_strings_recursively(self, data):
        """Recursively fix string/symbol issues in parsed S-expression data."""
        import sexpdata
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, list):
                    # Check for pin definitions that need fixing
                    if (len(item) >= 3 and 
                        item[0] == sexpdata.Symbol('pin')):
                        print(f"🔧 DEBUG: Found pin definition: {item[:3]} - types: {[type(x) for x in item[:3]]}")
                        # Fix pin type and shape - ensure they are symbols not strings
                        if isinstance(item[1], str):
                            print(f"🔧 DEBUG: Converting pin type '{item[1]}' to symbol")
                            item[1] = sexpdata.Symbol(item[1])  # pin type: "passive" -> passive
                        if len(item) >= 3 and isinstance(item[2], str):
                            print(f"🔧 DEBUG: Converting pin shape '{item[2]}' to symbol")
                            item[2] = sexpdata.Symbol(item[2])  # pin shape: "line" -> line
                    
                    # Recursively process nested lists
                    self._fix_symbol_strings_recursively(item)
                elif isinstance(item, str):
                    # Fix common KiCAD keywords that should be symbols
                    if item in ['yes', 'no', 'default', 'none', 'left', 'right', 'center']:
                        data[i] = sexpdata.Symbol(item)
        
        return data

    @staticmethod
    def _create_empty_schematic_data() -> Dict[str, Any]:
        """Create empty schematic data structure."""
        return {
            "version": "20250114",
            "generator": "eeschema",
            "generator_version": "9.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "title_block": {
                "title": "Untitled",
                "date": "",
                "revision": "1.0",
                "company": "",
                "size": "A4",
            },
            "components": [],
            "wires": [],
            "junctions": [],
            "labels": [],
            "nets": [],
            "lib_symbols": {},
            "sheet_instances": [
                {
                    "path": "/",
                    "page": "1"
                }
            ],
            "symbol_instances": [],
            "embedded_fonts": "no",
        }

    # Context manager support for atomic operations
    def __enter__(self):
        """Enter atomic operation context."""
        # Create backup for potential rollback
        if self._file_path and self._file_path.exists():
            self._backup_path = self.backup(".atomic_backup")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit atomic operation context."""
        if exc_type is not None:
            # Exception occurred - rollback if possible
            if hasattr(self, "_backup_path") and self._backup_path.exists():
                logger.warning("Exception in atomic operation - rolling back")
                # Restore from backup
                restored_data = self._parser.parse_file(self._backup_path)
                self._data = restored_data
                self._modified = True
        else:
            # Success - clean up backup
            if hasattr(self, "_backup_path") and self._backup_path.exists():
                self._backup_path.unlink()

    def __str__(self) -> str:
        """String representation."""
        title = self.title_block.get("title", "Untitled")
        component_count = len(self._components)
        return f"<Schematic '{title}': {component_count} components>"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Schematic(file='{self._file_path}', "
            f"components={len(self._components)}, "
            f"modified={self.modified})"
        )


# Convenience functions for common operations
def load_schematic(file_path: Union[str, Path]) -> Schematic:
    """
    Load a KiCAD schematic file.

    Args:
        file_path: Path to .kicad_sch file

    Returns:
        Loaded Schematic object
    """
    return Schematic.load(file_path)


def create_schematic(name: str = "New Circuit") -> Schematic:
    """
    Create a new empty schematic.

    Args:
        name: Schematic name for title block

    Returns:
        New Schematic object
    """
    return Schematic.create(name)
