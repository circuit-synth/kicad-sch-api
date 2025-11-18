"""
High-performance symbol library cache for KiCAD schematic API.

This module provides intelligent caching and lookup functionality for KiCAD symbol libraries,
significantly improving performance for applications that work with many components.
"""

import glob
import hashlib
import json
import logging
import os
import platform
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import sexpdata

from ..core.types import PinShape, PinType, Point, SchematicPin
from ..utils.validation import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class SymbolDefinition:
    """Complete definition of a symbol from KiCAD library."""

    lib_id: str  # e.g., "Device:R"
    name: str  # Symbol name within library
    library: str  # Library name
    reference_prefix: str  # e.g., "R" for resistors
    description: str = ""
    keywords: str = ""
    datasheet: str = ""
    pins: List[SchematicPin] = field(default_factory=list)
    units: int = 1
    unit_names: Dict[int, str] = field(default_factory=dict)
    power_symbol: bool = False
    graphic_elements: List[Dict[str, Any]] = field(default_factory=list)

    # Property positions from symbol library (for auto-placement)
    # Maps property name to (x, y, rotation) tuple
    property_positions: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)

    # Raw KiCAD data for exact format preservation
    raw_kicad_data: Any = None

    # Symbol inheritance
    extends: Optional[str] = None  # Parent symbol name if this symbol extends another

    # Performance metrics
    load_time: float = 0.0
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def __post_init__(self):
        """Post-initialization processing."""
        self.last_accessed = time.time()

        # Validate lib_id format
        if ":" not in self.lib_id:
            raise ValidationError(
                f"Invalid lib_id format: {self.lib_id} (should be Library:Symbol)"
            )

        # Extract library from lib_id if not provided
        if not self.library:
            self.library = self.lib_id.split(":")[0]

    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        Calculate symbol bounding box from graphic elements and pins.

        Returns:
            (min_x, min_y, max_x, max_y) in mm
        """
        if not self.graphic_elements and not self.pins:
            # Default bounding box for empty symbol
            return (-2.54, -2.54, 2.54, 2.54)

        coordinates = []

        # Collect pin positions
        for pin in self.pins:
            coordinates.extend([(pin.position.x, pin.position.y)])

        # Collect graphic element coordinates
        for elem in self.graphic_elements:
            if "points" in elem:
                coordinates.extend(elem["points"])
            elif "center" in elem and "radius" in elem:
                # Circle - approximate with bounding box
                cx, cy = elem["center"]
                radius = elem["radius"]
                coordinates.extend([(cx - radius, cy - radius), (cx + radius, cy + radius)])

        if not coordinates:
            return (-2.54, -2.54, 2.54, 2.54)

        min_x = min(coord[0] for coord in coordinates)
        max_x = max(coord[0] for coord in coordinates)
        min_y = min(coord[1] for coord in coordinates)
        max_y = max(coord[1] for coord in coordinates)

        return (min_x, min_y, max_x, max_y)

    @property
    def size(self) -> Tuple[float, float]:
        """Get symbol size (width, height) in mm."""
        min_x, min_y, max_x, max_y = self.bounding_box
        return (max_x - min_x, max_y - min_y)

    def get_pin(self, pin_number: str) -> Optional[SchematicPin]:
        """Get pin by number."""
        for pin in self.pins:
            if pin.number == pin_number:
                pin.name  # Access pin to update symbol statistics
                self.access_count += 1
                self.last_accessed = time.time()
                return pin
        return None

    def get_pins_by_type(self, pin_type: PinType) -> List[SchematicPin]:
        """Get all pins of specified type."""
        self.access_count += 1
        self.last_accessed = time.time()
        return [pin for pin in self.pins if pin.pin_type == pin_type]


@dataclass
class LibraryStats:
    """Statistics for symbol library performance tracking."""

    library_path: Path
    symbol_count: int = 0
    load_time: float = 0.0
    file_size: int = 0
    last_modified: float = 0.0
    cache_hit_rate: float = 0.0
    access_count: int = 0


class SymbolLibraryCache:
    """
    High-performance cache for KiCAD symbol libraries.

    Features:
    - Intelligent caching with performance metrics
    - Fast symbol lookup and indexing
    - Library discovery and management
    - Memory-efficient storage
    - Cache invalidation based on file modification time
    """

    def __init__(self, cache_dir: Optional[Path] = None, enable_persistence: bool = True):
        """
        Initialize the symbol cache.

        Args:
            cache_dir: Directory to store cached symbol data
            enable_persistence: Whether to persist cache to disk
        """
        self._symbols: Dict[str, SymbolDefinition] = {}
        self._library_paths: Set[Path] = set()

        # Cache configuration
        self._cache_dir = cache_dir or Path.home() / ".cache" / "kicad-sch-api" / "symbols"
        self._enable_persistence = enable_persistence

        if enable_persistence:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Indexes for fast lookup
        self._symbol_index: Dict[str, str] = {}  # symbol_name -> lib_id
        self._library_index: Dict[str, Path] = {}  # library_name -> path
        self._lib_stats: Dict[str, LibraryStats] = {}

        # Performance tracking
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_load_time = 0.0

        # Load persistent cache if available
        self._index_file = self._cache_dir / "symbol_index.json" if enable_persistence else None
        if enable_persistence:
            self._load_persistent_index()

        logger.info(f"Symbol cache initialized (persistence: {enable_persistence})")

    def add_library_path(self, library_path: Union[str, Path]) -> bool:
        """
        Add a library path to the cache.

        Args:
            library_path: Path to .kicad_sym file

        Returns:
            True if library was added successfully
        """
        library_path = Path(library_path)

        if not library_path.exists():
            logger.warning(f"Library file not found: {library_path}")
            return False

        if not library_path.suffix == ".kicad_sym":
            logger.warning(f"Not a KiCAD symbol library: {library_path}")
            return False

        if library_path in self._library_paths:
            logger.debug(f"Library already in cache: {library_path}")
            return True

        self._library_paths.add(library_path)
        library_name = library_path.stem
        self._library_index[library_name] = library_path

        # Initialize library statistics
        stat = library_path.stat()
        self._lib_stats[library_name] = LibraryStats(
            library_path=library_path, file_size=stat.st_size, last_modified=stat.st_mtime
        )

        logger.info(f"Added library: {library_name} ({library_path})")
        return True

    def discover_libraries(self, search_paths: List[Union[str, Path]] = None) -> int:
        """
        Automatically discover KiCAD symbol libraries.

        Searches environment variables and system paths for KiCAD symbol libraries.
        Supports version-flexible discovery across KiCAD 7, 8, 9, and custom installations.

        Environment variables checked:
        - KICAD_SYMBOL_DIR (generic, supports : or ; separated paths)
        - KICAD9_SYMBOL_DIR (KiCAD 9 specific)
        - KICAD8_SYMBOL_DIR (KiCAD 8 specific)
        - KICAD7_SYMBOL_DIR (KiCAD 7 specific)

        Args:
            search_paths: Optional custom directories to search for .kicad_sym files.
                         If None, uses environment variables + default system paths.

        Returns:
            Number of libraries discovered and added
        """
        if search_paths is None:
            # Merge environment variable paths with system paths
            env_paths = self._check_environment_variables()
            system_paths = self._get_default_library_paths()

            # Combine and deduplicate
            all_paths = list(dict.fromkeys(env_paths + system_paths))
            search_paths = all_paths

            logger.debug(
                f"Library discovery: {len(env_paths)} from env vars, "
                f"{len(system_paths)} from system, "
                f"{len(search_paths)} total (after dedup)"
            )

        discovered_count = 0

        for search_path in search_paths:
            search_path = Path(search_path)
            if not search_path.exists():
                continue

            logger.info(f"Discovering libraries in: {search_path}")

            # Find all .kicad_sym files
            for lib_file in search_path.rglob("*.kicad_sym"):
                if self.add_library_path(lib_file):
                    discovered_count += 1

        if discovered_count == 0:
            logger.warning(
                "No KiCAD symbol libraries found.\n\n"
                "Tried the following:\n"
                "  - Environment variables: KICAD_SYMBOL_DIR, KICAD8_SYMBOL_DIR, KICAD7_SYMBOL_DIR\n"
                "  - System paths: Default KiCAD installation locations\n\n"
                "Solutions:\n"
                "  1. Set environment variable:\n"
                "     export KICAD_SYMBOL_DIR=/path/to/kicad/symbols\n\n"
                "  2. Add library path programmatically:\n"
                "     cache = get_symbol_cache()\n"
                "     cache.add_library_path('/path/to/library.kicad_sym')\n\n"
                "  3. Discover libraries manually:\n"
                "     cache.discover_libraries(['/custom/path'])\n"
            )
        else:
            logger.info(f"Discovered {discovered_count} libraries")

        return discovered_count

    def get_symbol(self, lib_id: str) -> Optional[SymbolDefinition]:
        """
        Get symbol definition by lib_id.

        Args:
            lib_id: Symbol identifier (e.g., "Device:R")

        Returns:
            Symbol definition if found, None otherwise
        """
        logger.debug(f"🔧 CACHE: Requesting symbol: {lib_id}")

        # Check cache first
        if lib_id in self._symbols:
            self._cache_hits += 1
            symbol = self._symbols[lib_id]
            symbol.access_count += 1
            symbol.last_accessed = time.time()
            logger.debug(f"🔧 CACHE: Cache hit for {lib_id}")
            return symbol

        # Cache miss - try to load symbol
        logger.debug(f"🔧 CACHE: Cache miss for {lib_id}, loading...")
        self._cache_misses += 1
        return self._load_symbol(lib_id)

    def get_symbol_info(self, lib_id: str):
        """
        Get symbol metadata for library introspection.

        Returns SymbolInfo with unit count, names, and other metadata.
        Used by LLMs to query multi-unit component information before adding.

        Args:
            lib_id: Library identifier (e.g., "Amplifier_Operational:TL072")

        Returns:
            SymbolInfo object with symbol metadata

        Raises:
            LibraryError: If symbol not found

        Example:
            info = cache.get_symbol_info("Amplifier_Operational:TL072")
            print(f"Units: {info.unit_count}")  # 3
            print(f"Unit names: {info.unit_names}")  # {1: "A", 2: "B", 3: "C"}
        """
        from ..core.exceptions import LibraryError
        from ..core.types import SymbolInfo

        symbol_def = self.get_symbol(lib_id)

        if not symbol_def:
            library_name = lib_id.split(":")[0] if ":" in lib_id else "unknown"
            raise LibraryError(
                f"Symbol '{lib_id}' not found in KiCAD libraries. "
                f"Please verify the library name '{library_name}' and symbol name are correct.",
                field="lib_id",
                value=lib_id,
            )

        return SymbolInfo(
            lib_id=symbol_def.lib_id,
            name=symbol_def.name,
            library=symbol_def.library,
            reference_prefix=symbol_def.reference_prefix,
            description=symbol_def.description,
            keywords=symbol_def.keywords,
            datasheet=symbol_def.datasheet,
            unit_count=symbol_def.units if symbol_def.units > 0 else 1,
            unit_names=symbol_def.unit_names.copy(),
            pins=symbol_def.pins.copy(),
            power_symbol=symbol_def.power_symbol,
        )

    def search_symbols(
        self, query: str, library: Optional[str] = None, limit: int = 50
    ) -> List[SymbolDefinition]:
        """
        Search for symbols by name, description, or keywords.

        Args:
            query: Search query string
            library: Optional library name to search within
            limit: Maximum number of results

        Returns:
            List of matching symbol definitions
        """
        results = []
        query_lower = query.lower()

        # Search in cached symbols first
        for symbol in self._symbols.values():
            if library and symbol.library != library:
                continue

            # Check if query matches name, description, or keywords
            searchable_text = f"{symbol.name} {symbol.description} {symbol.keywords}".lower()
            if query_lower in searchable_text:
                results.append(symbol)
                if len(results) >= limit:
                    break

        # If not enough results and query looks like a specific symbol, try loading
        if len(results) < 5 and ":" in query:
            symbol = self.get_symbol(query)
            if symbol and symbol not in results:
                results.insert(0, symbol)  # Put exact match first

        return results

    def get_library_symbols(self, library_name: str) -> List[SymbolDefinition]:
        """Get all symbols from a specific library."""
        if library_name not in self._library_index:
            logger.warning(f"Library not found: {library_name}")
            return []

        # Load library if not already cached
        library_path = self._library_index[library_name]
        self._load_library(library_path)

        # Return all symbols from this library
        return [symbol for symbol in self._symbols.values() if symbol.library == library_name]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_symbols_cached": len(self._symbols),
            "total_libraries": len(self._library_paths),
            "total_load_time_ms": round(self._total_load_time * 1000, 2),
            "avg_load_time_per_symbol_ms": round(
                (self._total_load_time / len(self._symbols) * 1000) if self._symbols else 0, 2
            ),
        }

    def clear_cache(self):
        """Clear all cached symbol data."""
        self._symbols.clear()
        self._symbol_index.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_load_time = 0.0
        logger.info("Symbol cache cleared")

    def _load_symbol(self, lib_id: str) -> Optional[SymbolDefinition]:
        """Load a single symbol from its library."""
        logger.debug(f"🔧 LOAD: Loading symbol {lib_id}")

        if ":" not in lib_id:
            logger.warning(f"🔧 LOAD: Invalid lib_id format: {lib_id}")
            return None

        library_name, symbol_name = lib_id.split(":", 1)
        logger.debug(f"🔧 LOAD: Library: {library_name}, Symbol: {symbol_name}")

        if library_name not in self._library_index:
            logger.warning(f"🔧 LOAD: Library not found: {library_name}")
            logger.debug(f"🔧 LOAD: Available libraries: {list(self._library_index.keys())}")
            return None

        library_path = self._library_index[library_name]
        logger.debug(f"🔧 LOAD: Library path: {library_path}")
        return self._load_symbol_from_library(library_path, lib_id)

    def _load_symbol_from_library(
        self, library_path: Path, lib_id: str
    ) -> Optional[SymbolDefinition]:
        """Load a specific symbol from a library file."""
        start_time = time.time()

        try:
            library_name, symbol_name = lib_id.split(":", 1)

            # Parse the .kicad_sym file to find the symbol
            symbol_data = self._parse_kicad_symbol_file(library_path, lib_id)
            if not symbol_data:
                logger.warning(f"Symbol {symbol_name} not found in {library_path}")
                return None

            # Create SymbolDefinition from parsed data
            symbol = SymbolDefinition(
                lib_id=lib_id,
                name=symbol_name,
                library=library_name,
                reference_prefix=symbol_data.get("reference_prefix", "U"),
                description=symbol_data.get("Description", symbol_data.get("description", "")),
                keywords=symbol_data.get("keywords", ""),
                datasheet=symbol_data.get("Datasheet", symbol_data.get("datasheet", "~")),
                pins=symbol_data.get("pins", []),
                units=symbol_data.get("units", 1),  # Use extracted unit count
                extends=symbol_data.get("extends"),  # Store extends information
                property_positions=symbol_data.get(
                    "property_positions", {}
                ),  # Property positions for auto-placement
                load_time=time.time() - start_time,
            )

            # Store the raw symbol data for later use in schematic generation
            symbol.raw_kicad_data = symbol_data.get("raw_data", {})
            logger.debug(f"🔧 CREATED: SymbolDefinition for {lib_id}, extends: {symbol.extends}")

            self._symbols[lib_id] = symbol
            self._symbol_index[symbol_name] = lib_id
            self._total_load_time += symbol.load_time

            logger.debug(f"Loaded symbol {lib_id} in {symbol.load_time:.3f}s")
            return symbol

        except Exception as e:
            logger.error(f"Error loading symbol {lib_id} from {library_path}: {e}")
            return None

    def _parse_kicad_symbol_file(self, library_path: Path, lib_id: str) -> Optional[Dict[str, Any]]:
        """Parse a KiCAD .kicad_sym file to extract a specific symbol."""
        try:
            # Extract symbol name from lib_id
            library_name, symbol_name = lib_id.split(":", 1)

            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the S-expression with symbol preservation
            parsed = sexpdata.loads(content, true=None, false=None, nil=None)
            logger.debug(f"🔧 PARSE: Parsed library file with {len(parsed)} top-level items")

            # Find the symbol we're looking for
            symbol_data = self._find_symbol_in_parsed_data(parsed, symbol_name)
            if not symbol_data:
                logger.debug(f"🔧 PARSE: Symbol {symbol_name} not found in {library_path}")
                return None

            logger.debug(f"🔧 PARSE: Found symbol {symbol_name} in library")

            # Extract the library name and symbol name for resolution
            library_name, symbol_name = lib_id.split(":", 1)

            # Check if this symbol extends another symbol
            extends_symbol = self._check_extends_directive(symbol_data)
            logger.debug(f"🔧 CACHE: Symbol {lib_id} extends: {extends_symbol}")

            # If this symbol extends another, we need to resolve it
            if extends_symbol:
                resolved_symbol_data = self._resolve_extends_relationship(
                    symbol_data, extends_symbol, library_path, library_name
                )
                if resolved_symbol_data:
                    symbol_data = resolved_symbol_data
                    extends_symbol = None  # Clear extends after resolution
                    logger.debug(f"🔧 CACHE: Resolved extends for {lib_id}")

            # Extract symbol information
            result = {
                "raw_data": symbol_data,  # Store the raw parsed data
                "reference_prefix": "U",  # Default
                "description": "",
                "keywords": "",
                "datasheet": "~",
                "pins": [],
                "extends": extends_symbol,  # Should be None after resolution
                "property_positions": {},  # Property positions for auto-placement
            }

            # Extract properties from the symbol
            for item in symbol_data[1:]:
                if isinstance(item, list) and len(item) > 0:
                    if item[0] == sexpdata.Symbol("property"):
                        prop_name = item[1]
                        prop_value = item[2]

                        logger.debug(f"🔧 Processing property: {prop_name} = {prop_value}")

                        # Extract property position (at x y rotation)
                        prop_position = self._extract_property_position(item)
                        if prop_position:
                            prop_name_str = str(prop_name).strip('"')
                            result["property_positions"][prop_name_str] = prop_position
                            logger.debug(
                                f"🔧 Extracted position for {prop_name_str}: {prop_position}"
                            )

                        if prop_name == sexpdata.Symbol("Reference"):
                            result["reference_prefix"] = str(prop_value)
                            logger.debug(f"🔧 Set reference_prefix: {str(prop_value)}")
                        elif prop_name == sexpdata.Symbol("Description"):
                            result["Description"] = str(prop_value)  # Keep original case
                            logger.debug(f"🔧 Set Description: {str(prop_value)}")
                        elif prop_name == sexpdata.Symbol("ki_keywords"):
                            result["keywords"] = str(prop_value)
                        elif prop_name == sexpdata.Symbol("Datasheet"):
                            result["Datasheet"] = str(prop_value)  # Keep original case
                            logger.debug(f"🔧 Set Datasheet: {str(prop_value)}")

            # Extract pins (this is simplified - pins are in symbol sub-definitions)
            # For now, we'll extract pins from the actual symbol structure
            result["pins"] = self._extract_pins_from_symbol(symbol_data)

            # Extract unit count from symbol structure
            result["units"] = self._count_symbol_units(symbol_data)
            logger.debug(f"🔧 PARSE: Symbol has {result['units']} units")

            return result

        except Exception as e:
            logger.error(f"Error parsing {library_path}: {e}")
            return None

    def _find_symbol_in_parsed_data(self, parsed_data: List, symbol_name: str) -> Optional[List]:
        """Find a specific symbol in parsed KiCAD library data."""
        logger.debug(f"🔧 FIND: Looking for symbol '{symbol_name}' in parsed data")

        if not isinstance(parsed_data, list):
            logger.debug(f"🔧 FIND: Parsed data is not a list: {type(parsed_data)}")
            return None

        # First, log all available symbols for debugging
        available_symbols = []
        for item in parsed_data:
            if isinstance(item, list) and len(item) >= 2:
                if item[0] == sexpdata.Symbol("symbol"):
                    available_symbols.append(str(item[1]).strip('"'))

        logger.debug(
            f"🔧 FIND: Available symbols in library: {available_symbols[:10]}..."
        )  # Show first 10

        # Search through the parsed data for the symbol
        for item in parsed_data:
            if isinstance(item, list) and len(item) >= 2:
                if (
                    item[0] == sexpdata.Symbol("symbol")
                    and len(item) > 1
                    and str(item[1]).strip('"') == symbol_name
                ):
                    logger.debug(f"🔧 FIND: Found symbol '{symbol_name}'")
                    return item

        logger.debug(f"🔧 FIND: Symbol '{symbol_name}' not found in library")
        return None

    def _check_extends_directive(self, symbol_data: List) -> Optional[str]:
        """Check if symbol has extends directive and return parent symbol name."""
        if not isinstance(symbol_data, list):
            return None

        for item in symbol_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                if item[0] == sexpdata.Symbol("extends"):
                    parent_name = str(item[1]).strip('"')
                    logger.debug(f"Found extends directive: {parent_name}")
                    return parent_name
        return None

    def _resolve_extends_relationship(
        self, child_symbol_data: List, parent_name: str, library_path: Path, library_name: str
    ) -> Optional[List]:
        """Resolve extends relationship by merging parent symbol into child."""
        logger.debug(f"🔧 RESOLVE: Resolving extends {parent_name} for child symbol")

        try:
            # Load the parent symbol from the same library
            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()

            parsed = sexpdata.loads(content, true=None, false=None, nil=None)
            parent_symbol_data = self._find_symbol_in_parsed_data(parsed, parent_name)

            if not parent_symbol_data:
                logger.warning(f"🔧 RESOLVE: Parent symbol {parent_name} not found in library")
                return None

            logger.debug(f"🔧 RESOLVE: Found parent symbol {parent_name}")

            # Merge parent into child (adapt from circuit-synth logic)
            merged_symbol = self._merge_parent_into_child(child_symbol_data, parent_symbol_data)
            logger.debug(f"🔧 RESOLVE: Merged parent into child symbol")

            return merged_symbol

        except Exception as e:
            logger.error(f"🔧 RESOLVE: Error resolving extends: {e}")
            return None

    def _merge_parent_into_child(self, child_data: List, parent_data: List) -> List:
        """Merge parent symbol graphics and pins into child symbol."""
        import copy

        # Get child and parent symbol names for unit renaming
        child_name = str(child_data[1]).strip('"') if len(child_data) > 1 else "Child"
        parent_name = str(parent_data[1]).strip('"') if len(parent_data) > 1 else "Parent"

        logger.debug(f"🔧 MERGE: Merging {parent_name} into {child_name}")

        # Start with child symbol structure
        merged = copy.deepcopy(child_data)

        # Remove the extends directive from child
        merged = [
            item
            for item in merged
            if not (
                isinstance(item, list) and len(item) >= 2 and item[0] == sexpdata.Symbol("extends")
            )
        ]

        # Copy all graphics and unit definitions from parent
        for item in parent_data[1:]:
            if isinstance(item, list) and len(item) > 0:
                # Copy symbol unit definitions (contain graphics and pins)
                if item[0] == sexpdata.Symbol("symbol"):
                    # Rename unit from parent name to child name
                    unit_item = copy.deepcopy(item)
                    if len(unit_item) > 1:
                        old_unit_name = str(unit_item[1]).strip('"')
                        # Replace parent name with child name in unit name
                        new_unit_name = old_unit_name.replace(parent_name, child_name)
                        unit_item[1] = new_unit_name
                        logger.debug(f"🔧 MERGE: Renamed unit {old_unit_name} -> {new_unit_name}")
                    merged.append(unit_item)
                # Copy other non-property elements (child properties override parent)
                elif item[0] not in [sexpdata.Symbol("property")]:
                    merged.append(copy.deepcopy(item))

        logger.debug(f"🔧 MERGE: Merged symbol has {len(merged)} elements")
        return merged

    def _extract_property_position(
        self, property_item: List
    ) -> Optional[Tuple[float, float, float]]:
        """
        Extract position (at x y rotation) from a property S-expression.

        Args:
            property_item: Property S-expression like (property "Reference" "U" (at x y rotation) ...)

        Returns:
            Tuple of (x, y, rotation) or None if no position found
        """
        try:
            # Look for (at x y rotation) in property item
            for sub_item in property_item:
                if isinstance(sub_item, list) and len(sub_item) >= 3:
                    if sub_item[0] == sexpdata.Symbol("at"):
                        x = float(sub_item[1])
                        y = float(sub_item[2])
                        rotation = float(sub_item[3]) if len(sub_item) > 3 else 0.0
                        return (x, y, rotation)
            return None
        except (ValueError, IndexError, TypeError) as e:
            logger.debug(f"Failed to extract property position: {e}")
            return None

    def _extract_pins_from_symbol(self, symbol_data: List) -> List[SchematicPin]:
        """Extract pins from symbol data."""
        pins = []

        # Look for symbol sub-definitions like "R_1_1" that contain pins
        for item in symbol_data[1:]:
            if isinstance(item, list) and len(item) > 0:
                if item[0] == sexpdata.Symbol("symbol"):
                    # This is a symbol unit definition, look for pins
                    pins.extend(self._extract_pins_from_unit(item))

        return pins

    def _count_symbol_units(self, symbol_data: List) -> int:
        """
        Count the number of units in a symbol.

        Multi-unit symbols have sub-symbol definitions with names like "Symbol_1_1", "Symbol_1_2", etc.
        The unit number is the last component before the final "_1" (which is the drawing style).

        Args:
            symbol_data: Parsed symbol S-expression data

        Returns:
            Number of units (minimum 1)
        """
        unit_numbers = set()

        # Look for symbol sub-definitions
        for item in symbol_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                if item[0] == sexpdata.Symbol("symbol"):
                    # Symbol name format: "LibraryName:SymbolName_unit_style"
                    # Example: "TL072_1_1", "TL072_2_1", "TL072_3_1"
                    symbol_name = str(item[1]).strip('"')

                    # Extract unit number from symbol name
                    # Format: Name_UnitNum_StyleNum
                    parts = symbol_name.split("_")
                    if len(parts) >= 2:
                        try:
                            # The second-to-last part is the unit number
                            unit_num = int(parts[-2])
                            unit_numbers.add(unit_num)
                            logger.debug(f"🔧 COUNT_UNITS: Found unit {unit_num} in {symbol_name}")
                        except ValueError:
                            # Not a number, skip
                            pass

        unit_count = len(unit_numbers) if unit_numbers else 1
        logger.debug(f"🔧 COUNT_UNITS: Total units found: {unit_count}")
        return unit_count

    def _extract_pins_from_unit(self, unit_data: List) -> List[SchematicPin]:
        """Extract pins from a symbol unit definition."""
        pins = []

        for item in unit_data[1:]:
            if isinstance(item, list) and len(item) > 0:
                if item[0] == sexpdata.Symbol("pin"):
                    pin = self._parse_pin_definition(item)
                    if pin:
                        pins.append(pin)

        return pins

    def _parse_pin_definition(self, pin_data: List) -> Optional[SchematicPin]:
        """Parse a pin definition from KiCAD format."""
        try:
            # pin_data format: (pin passive line (at 0 3.81 270) (length 1.27) ...)
            pin_type_str = str(pin_data[1]) if len(pin_data) > 1 else "passive"
            pin_shape_str = str(pin_data[2]) if len(pin_data) > 2 else "line"

            position = Point(0, 0)
            length = 2.54
            rotation = 0
            name = "~"
            number = "1"

            # Parse pin attributes
            for item in pin_data[3:]:
                if isinstance(item, list) and len(item) > 0:
                    if item[0] == sexpdata.Symbol("at"):
                        # (at x y rotation)
                        if len(item) >= 3:
                            position = Point(float(item[1]), float(item[2]))
                            if len(item) >= 4:
                                rotation = float(item[3])
                    elif item[0] == sexpdata.Symbol("length"):
                        length = float(item[1])
                    elif item[0] == sexpdata.Symbol("name"):
                        name = str(item[1]).strip('"')
                    elif item[0] == sexpdata.Symbol("number"):
                        number = str(item[1]).strip('"')

            # Map pin type
            pin_type = PinType.PASSIVE
            if pin_type_str == "input":
                pin_type = PinType.INPUT
            elif pin_type_str == "output":
                pin_type = PinType.OUTPUT
            elif pin_type_str == "bidirectional":
                pin_type = PinType.BIDIRECTIONAL
            elif pin_type_str == "power_in":
                pin_type = PinType.POWER_IN
            elif pin_type_str == "power_out":
                pin_type = PinType.POWER_OUT

            # Map pin shape
            pin_shape = PinShape.LINE
            if pin_shape_str == "inverted":
                pin_shape = PinShape.INVERTED
            elif pin_shape_str == "clock":
                pin_shape = PinShape.CLOCK

            return SchematicPin(
                number=number,
                name=name,
                position=position,
                pin_type=pin_type,
                pin_shape=pin_shape,
                length=length,
                rotation=rotation,
            )

        except Exception as e:
            logger.error(f"Error parsing pin definition: {e}")
            return None

    def _load_library(self, library_path: Path) -> bool:
        """Load all symbols from a library file."""
        library_name = library_path.stem

        # Check if library needs reloading based on modification time
        if library_name in self._lib_stats:
            stat = library_path.stat()
            if stat.st_mtime <= self._lib_stats[library_name].last_modified:
                logger.debug(f"Library {library_name} already up-to-date")
                return True

        start_time = time.time()
        logger.info(f"Loading library: {library_name}")

        try:
            # In a real implementation, this would parse the .kicad_sym file
            # and extract all symbol definitions

            # For now, just update statistics
            load_time = time.time() - start_time

            if library_name not in self._lib_stats:
                stat = library_path.stat()
                self._lib_stats[library_name] = LibraryStats(
                    library_path=library_path, file_size=stat.st_size, last_modified=stat.st_mtime
                )

            self._lib_stats[library_name].load_time = load_time
            self._total_load_time += load_time

            logger.info(f"Loaded library {library_name} in {load_time:.3f}s")
            return True

        except Exception as e:
            logger.error(f"Error loading library {library_path}: {e}")
            return False

    def _guess_reference_prefix(self, symbol_name: str) -> str:
        """Guess the reference prefix from symbol name."""
        # Common mappings
        prefix_mapping = {
            "R": "R",  # Resistor
            "C": "C",  # Capacitor
            "L": "L",  # Inductor
            "D": "D",  # Diode
            "LED": "D",  # LED
            "Q": "Q",  # Transistor
            "U": "U",  # IC
            "J": "J",  # Connector
            "SW": "SW",  # Switch
            "TP": "TP",  # Test point
            "FB": "FB",  # Ferrite bead
        }

        symbol_upper = symbol_name.upper()
        for key, prefix in prefix_mapping.items():
            if symbol_upper.startswith(key):
                return prefix

        # Default to 'U' for unknown symbols
        return "U"

    def _check_environment_variables(self) -> List[Path]:
        """
        Check environment variables for library paths.

        Supports:
        - KICAD_SYMBOL_DIR (generic, colon/semicolon-separated)
        - KICAD9_SYMBOL_DIR (KiCAD 9 specific)
        - KICAD8_SYMBOL_DIR (KiCAD 8 specific)
        - KICAD7_SYMBOL_DIR (KiCAD 7 specific)

        Returns:
            List of valid library paths from environment variables
        """
        env_paths = []
        env_vars = [
            "KICAD_SYMBOL_DIR",
            "KICAD9_SYMBOL_DIR",
            "KICAD8_SYMBOL_DIR",
            "KICAD7_SYMBOL_DIR",
        ]

        for env_var in env_vars:
            env_value = os.environ.get(env_var)
            if not env_value or env_value.strip() == "":
                continue

            logger.debug(f"Found environment variable {env_var}={env_value}")

            # Handle path separators (: for Unix, ; for Windows)
            separator = ";" if os.name == "nt" else ":"
            paths = env_value.split(separator)

            for path_str in paths:
                path_str = path_str.strip()
                if not path_str:
                    continue

                path = Path(path_str).expanduser()
                if self._validate_library_path(path):
                    env_paths.append(path)
                    logger.info(f"Added library path from {env_var}: {path}")
                else:
                    logger.warning(
                        f"Invalid library path from {env_var}: {path} (does not exist or contains no .kicad_sym files)"
                    )

        return env_paths

    def _glob_version_paths(self, pattern: str) -> List[Path]:
        """
        Use glob to find version-specific library paths.

        Args:
            pattern: Glob pattern (e.g., "/Applications/KiCad*/symbols")

        Returns:
            List of matching paths that exist
        """
        paths = []
        try:
            matches = glob.glob(pattern)
            for match in matches:
                path = Path(match)
                if path.exists() and path.is_dir():
                    paths.append(path)
                    logger.debug(f"Glob found: {path}")
        except Exception as e:
            logger.debug(f"Error globbing pattern {pattern}: {e}")

        return paths

    def _validate_library_path(self, path: Path) -> bool:
        """
        Validate that a path contains KiCAD symbol libraries.

        Args:
            path: Path to validate

        Returns:
            True if path exists and contains .kicad_sym files
        """
        try:
            if not path.exists():
                return False

            # If it's a file, check if it's a .kicad_sym file
            if path.is_file():
                return path.suffix == ".kicad_sym"

            # If it's a directory, check if it contains any .kicad_sym files
            if path.is_dir():
                return any(path.glob("*.kicad_sym"))

            return False

        except (PermissionError, OSError) as e:
            logger.warning(f"Permission error accessing {path}: {e}")
            return False

    def _get_default_library_paths(self) -> List[Path]:
        """
        Get default KiCAD library search paths with version-flexible discovery.

        Uses glob patterns to find KiCAD installations regardless of version number.
        """
        search_paths = []

        # Windows paths - use glob for version flexibility
        if os.name == "nt":
            # Search for all KiCAD versions in Program Files
            for base_path in ["C:/Program Files/KiCad", "C:/Program Files (x86)/KiCad"]:
                # Glob for version subdirectories (7.0, 8.0, 9.0, etc.)
                version_paths = self._glob_version_paths(f"{base_path}/*/share/kicad/symbols")
                search_paths.extend(version_paths)

                # Also check base path without version
                try:
                    base_symbols = Path(base_path) / "share" / "kicad" / "symbols"
                    if base_symbols.exists():
                        search_paths.append(base_symbols)
                except (PermissionError, OSError) as e:
                    logger.debug(f"Permission error accessing {base_symbols}: {e}")

        # Linux/macOS paths
        elif os.name == "posix":
            # Standard Linux paths
            standard_linux_paths = [
                Path("/usr/share/kicad/symbols"),
                Path("/usr/local/share/kicad/symbols"),
                Path.home() / ".local/share/kicad/symbols",
            ]
            # Safely check paths with permission error handling
            for p in standard_linux_paths:
                try:
                    if p.exists():
                        search_paths.append(p)
                except (PermissionError, OSError) as e:
                    logger.debug(f"Permission error accessing {p}: {e}")

            # macOS KiCAD.app bundle paths - glob for version flexibility
            if platform.system() == "Darwin":
                # Search for KiCad, KiCad7, KiCad8, KiCad806, etc.
                macos_pattern = "/Applications/KiCad*/KiCad.app/Contents/SharedSupport/symbols"
                macos_paths = self._glob_version_paths(macos_pattern)
                search_paths.extend(macos_paths)

        # User document directories (all platforms)
        user_paths = [
            Path.home() / "Documents/KiCad/symbols",
            Path.home() / "Documents/kicad/symbols",
            Path.home() / "kicad/symbols",
        ]
        # Safely check paths with permission error handling
        for p in user_paths:
            try:
                if p.exists():
                    search_paths.append(p)
            except (PermissionError, OSError) as e:
                logger.debug(f"Permission error accessing {p}: {e}")

        logger.debug(f"Discovered {len(search_paths)} default library search paths")
        return search_paths

    def _load_persistent_index(self):
        """Load persistent symbol index from disk."""
        if not self._enable_persistence or not self._index_file or not self._index_file.exists():
            return

        try:
            with open(self._index_file, "r") as f:
                index_data = json.load(f)

            # Restore basic index data
            self._symbol_index = index_data.get("symbol_index", {})

            # Restore library paths
            for lib_path_str in index_data.get("library_paths", []):
                lib_path = Path(lib_path_str)
                if lib_path.exists():
                    self.add_library_path(lib_path)

            logger.info(f"Loaded persistent index with {len(self._symbol_index)} symbols")

        except Exception as e:
            logger.warning(f"Failed to load persistent index: {e}")

    def _save_persistent_index(self):
        """Save symbol index to disk for persistence."""
        if not self._enable_persistence or not self._index_file:
            return

        try:
            index_data = {
                "symbol_index": self._symbol_index,
                "library_paths": [str(path) for path in self._library_paths],
                "cache_stats": self.get_performance_stats(),
            }

            with open(self._index_file, "w") as f:
                json.dump(index_data, f, indent=2)

            logger.debug("Saved persistent symbol index")

        except Exception as e:
            logger.warning(f"Failed to save persistent index: {e}")


# Global cache instance
_global_cache: Optional[SymbolLibraryCache] = None


def get_symbol_cache() -> SymbolLibraryCache:
    """Get the global symbol cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = SymbolLibraryCache()
        # Auto-discover libraries on first use
        _global_cache.discover_libraries()
    return _global_cache


def set_symbol_cache(cache: SymbolLibraryCache):
    """Set the global symbol cache instance."""
    global _global_cache
    _global_cache = cache
