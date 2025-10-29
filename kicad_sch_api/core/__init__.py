"""Core kicad-sch-api functionality."""

from .components import Component, ComponentCollection
from .formatter import ExactFormatter
from .parser import SExpressionParser
from .schematic import Schematic, create_schematic, load_schematic
from .types import Junction, Label, Net, Point, SchematicSymbol, Wire
# Exception hierarchy
from .exceptions import (
    KiCadSchError,
    ValidationError,
    ReferenceError,
    LibraryError,
    GeometryError,
    NetError,
    ParseError,
    FormatError,
    CollectionError,
    ElementNotFoundError,
    DuplicateElementError,
    CollectionOperationError,
    FileOperationError,
    CLIError,
    SchematicStateError,
)

__all__ = [
    "Schematic",
    "Component",
    "ComponentCollection",
    "Point",
    "SchematicSymbol",
    "Wire",
    "Junction",
    "Label",
    "Net",
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
