"""Core kicad-sch-api functionality."""

from ..collections import Component, ComponentCollection

# Exception hierarchy
from .exceptions import (
    CLIError,
    CollectionError,
    CollectionOperationError,
    DuplicateElementError,
    ElementNotFoundError,
    FileOperationError,
    FormatError,
    GeometryError,
    KiCadSchError,
    LibraryError,
    NetError,
    ParseError,
    ReferenceError,
    SchematicStateError,
    ValidationError,
)
from .formatter import ExactFormatter
from .parser import SExpressionParser
from .schematic import Schematic, create_schematic, load_schematic
from .types import BusEntry, Junction, Label, Net, PinInfo, Point, SchematicSymbol, Wire

__all__ = [
    "Schematic",
    "Component",
    "ComponentCollection",
    "Point",
    "SchematicSymbol",
    "Wire",
    "BusEntry",
    "Junction",
    "Label",
    "Net",
    "PinInfo",
    "SExpressionParser",
    "ExactFormatter",
    "load_schematic",
    "create_schematic",
    # Exceptions
    "KiCadSchError",
    "ValidationError",
    "ReferenceError",
    "LibraryError",
    "GeometryError",
    "NetError",
    "ParseError",
    "FormatError",
    "CollectionError",
    "ElementNotFoundError",
    "DuplicateElementError",
    "CollectionOperationError",
    "FileOperationError",
    "CLIError",
    "SchematicStateError",
]
