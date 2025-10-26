"""
Symbol cache interface and implementation for KiCAD symbol libraries.

Provides high-performance caching with clear separation between cache
management and symbol resolution concerns.
"""

import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import sexpdata

from ..library.cache import LibraryStats, SymbolDefinition
from ..utils.validation import ValidationError

logger = logging.getLogger(__name__)


class ISymbolCache(ABC):
    """
    Interface for symbol caching implementations.

    Defines the contract for symbol caching without coupling to specific
    inheritance resolution or validation logic.
    """

    @abstractmethod
    def get_symbol(self, lib_id: str) -> Optional[SymbolDefinition]:
        """
        Get a symbol by library ID.

        Args:
            lib_id: Library identifier (e.g., "Device:R")

        Returns:
            Symbol definition if found, None otherwise
        """
        pass

    @abstractmethod
    def has_symbol(self, lib_id: str) -> bool:
        """
        Check if symbol exists in cache.

        Args:
            lib_id: Library identifier to check

        Returns:
            True if symbol exists in cache
        """
        pass

    @abstractmethod
    def add_library_path(self, library_path: Union[str, Path]) -> bool:
        """
        Add a library path to the cache.

        Args:
            library_path: Path to .kicad_sym file

        Returns:
            True if library was added successfully
        """
        pass

    @abstractmethod
    def get_library_symbols(self, library_name: str) -> List[str]:
        """
        Get all symbol IDs from a specific library.

        Args:
            library_name: Name of library

        Returns:
            List of symbol lib_ids from the library
        """
        pass

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear all cached symbols."""
        pass

    @abstractmethod
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        pass


class SymbolCache(ISymbolCache):
    """
    High-performance symbol cache implementation.

    Focuses purely on caching functionality without inheritance resolution,
    which is handled by the SymbolResolver.
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

    def get_symbol(self, lib_id: str) -> Optional[SymbolDefinition]:
        """
        Get a symbol by library ID.

        Note: This returns the raw symbol without inheritance resolution.
        Use SymbolResolver for fully resolved symbols.
        """
        if lib_id in self._symbols:
            self._cache_hits += 1
            symbol = self._symbols[lib_id]
            symbol.access_count += 1
            symbol.last_accessed = time.time()
            return symbol

        self._cache_misses += 1

        # Try to load from library
        symbol = self._load_symbol_from_library(lib_id)
        if symbol:
            self._symbols[lib_id] = symbol

        return symbol

    def has_symbol(self, lib_id: str) -> bool:
        """Check if symbol exists in cache."""
        if lib_id in self._symbols:
            return True

        # Check if we can load it
        return self._can_load_symbol(lib_id)

    def add_library_path(self, library_path: Union[str, Path]) -> bool:
        """Add a library path to the cache."""
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
            library_path=library_path,
            file_size=stat.st_size,
            last_modified=stat.st_mtime,
            symbol_count=0,  # Will be updated when library is loaded
        )

        logger.info(f"Added library: {library_name} ({library_path})")
        return True

    def get_library_symbols(self, library_name: str) -> List[str]:
        """Get all symbol IDs from a specific library."""
        if library_name not in self._library_index:
            return []

        # Load library if not already loaded
        library_path = self._library_index[library_name]
        symbols = []

        try:
            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()

            parsed = sexpdata.loads(content, true=None, false=None, nil=None)

            # Extract symbol names from parsed data
            for item in parsed[1:]:  # Skip first item which is 'kicad_symbol_lib'
                if isinstance(item, list) and len(item) > 1:
                    if item[0] == sexpdata.Symbol("symbol"):
                        symbol_name = str(item[1]).strip('"')
                        lib_id = f"{library_name}:{symbol_name}"
                        symbols.append(lib_id)

        except Exception as e:
            logger.error(f"Error loading symbols from {library_name}: {e}")

        return symbols

    def clear_cache(self) -> None:
        """Clear all cached symbols."""
        self._symbols.clear()
        self._symbol_index.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Symbol cache cleared")

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "symbols_cached": len(self._symbols),
            "libraries_loaded": len(self._library_paths),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": hit_rate,
            "total_load_time": self._total_load_time,
            "library_stats": {
                name: {
                    "file_size": stats.file_size,
                    "symbols_count": stats.symbols_count,
                    "last_loaded": stats.last_loaded,
                }
                for name, stats in self._lib_stats.items()
            },
        }

    # Private methods for implementation details
    def _load_symbol_from_library(self, lib_id: str) -> Optional[SymbolDefinition]:
        """Load symbol from library file."""
        if ":" not in lib_id:
            logger.warning(f"Invalid lib_id format: {lib_id}")
            return None

        library_name, symbol_name = lib_id.split(":", 1)

        if library_name not in self._library_index:
            logger.debug(f"Library {library_name} not in cache")
            return None

        library_path = self._library_index[library_name]

        try:
            start_time = time.time()

            with open(library_path, "r", encoding="utf-8") as f:
                content = f.read()

            parsed = sexpdata.loads(content, true=None, false=None, nil=None)
            symbol_data = self._find_symbol_in_parsed_data(parsed, symbol_name)

            if not symbol_data:
                logger.debug(f"Symbol {symbol_name} not found in {library_name}")
                return None

            # Create symbol definition without inheritance resolution
            symbol = self._create_symbol_definition(symbol_data, lib_id, library_name)

            load_time = time.time() - start_time
            self._total_load_time += load_time
            symbol.load_time = load_time

            logger.debug(f"Loaded symbol {lib_id} in {load_time:.3f}s")
            return symbol

        except Exception as e:
            logger.error(f"Error loading symbol {lib_id}: {e}")
            return None

    def _find_symbol_in_parsed_data(self, parsed_data: List, symbol_name: str) -> Optional[List]:
        """Find symbol data in parsed library content."""
        for item in parsed_data[1:]:  # Skip first item which is 'kicad_symbol_lib'
            if isinstance(item, list) and len(item) > 1:
                if item[0] == sexpdata.Symbol("symbol"):
                    name = str(item[1]).strip('"')
                    if name == symbol_name:
                        return item
        return None

    def _create_symbol_definition(
        self, symbol_data: List, lib_id: str, library_name: str
    ) -> SymbolDefinition:
        """Create SymbolDefinition from parsed symbol data."""
        symbol_name = str(symbol_data[1]).strip('"')

        # Extract basic symbol properties
        properties = self._extract_symbol_properties(symbol_data)
        pins = self._extract_symbol_pins(symbol_data)
        graphic_elements = self._extract_graphic_elements(symbol_data)

        # Check for extends directive
        extends = self._check_extends_directive(symbol_data)

        return SymbolDefinition(
            lib_id=lib_id,
            name=symbol_name,
            library=library_name,
            reference_prefix=properties.get("reference_prefix", "U"),
            description=properties.get("description", ""),
            keywords=properties.get("keywords", ""),
            datasheet=properties.get("datasheet", ""),
            pins=pins,
            units=properties.get("units", 1),
            power_symbol=properties.get("power_symbol", False),
            graphic_elements=graphic_elements,
            raw_kicad_data=symbol_data,
            extends=extends,  # Store extends information for resolver
        )

    def _extract_symbol_properties(self, symbol_data: List) -> Dict[str, Any]:
        """Extract symbol properties from symbol data."""
        properties = {
            "reference_prefix": "U",
            "description": "",
            "keywords": "",
            "datasheet": "",
            "units": 1,
            "power_symbol": False,
        }

        for item in symbol_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                key = str(item[0])
                if key == "property":
                    prop_name = str(item[1]).strip('"')
                    prop_value = str(item[2]).strip('"') if len(item) > 2 else ""

                    if prop_name == "Reference":
                        # Extract prefix from reference like "R" from "R?"
                        ref = prop_value.rstrip("?")
                        if ref:
                            properties["reference_prefix"] = ref
                    elif prop_name == "ki_description":
                        properties["description"] = prop_value
                    elif prop_name == "ki_keywords":
                        properties["keywords"] = prop_value
                    elif prop_name == "ki_fp_filters":
                        properties["datasheet"] = prop_value

        return properties

    def _extract_symbol_pins(self, symbol_data: List) -> List:
        """Extract pins from symbol data."""
        # For now, return empty list - pin extraction would be implemented here
        # This would parse pin definitions from the symbol units
        return []

    def _extract_graphic_elements(self, symbol_data: List) -> List[Dict[str, Any]]:
        """Extract graphic elements from symbol data."""
        # For now, return empty list - graphic element extraction would be implemented here
        # This would parse rectangles, circles, arcs, etc. from symbol units
        return []

    def _check_extends_directive(self, symbol_data: List) -> Optional[str]:
        """Check if symbol has extends directive and return parent symbol name."""
        if not isinstance(symbol_data, list):
            return None

        for item in symbol_data[1:]:
            if isinstance(item, list) and len(item) >= 2:
                if str(item[0]) == "extends":
                    parent_name = str(item[1]).strip('"')
                    logger.debug(f"Found extends directive: {parent_name}")
                    return parent_name
        return None

    def _can_load_symbol(self, lib_id: str) -> bool:
        """Check if symbol can be loaded without actually loading it."""
        if ":" not in lib_id:
            return False

        library_name, _ = lib_id.split(":", 1)
        return library_name in self._library_index

    def _load_persistent_index(self) -> None:
        """Load persistent index from disk."""
        if not self._index_file or not self._index_file.exists():
            return

        try:
            with open(self._index_file, "r") as f:
                index_data = json.load(f)

            # Restore symbol index
            self._symbol_index = index_data.get("symbol_index", {})

            # Restore library paths that still exist
            for lib_path_str in index_data.get("library_paths", []):
                lib_path = Path(lib_path_str)
                if lib_path.exists():
                    self._library_paths.add(lib_path)
                    self._library_index[lib_path.stem] = lib_path

            logger.debug(f"Loaded persistent index with {len(self._symbol_index)} symbols")

        except Exception as e:
            logger.warning(f"Failed to load persistent index: {e}")

    def save_persistent_index(self) -> None:
        """Save current index to disk."""
        if not self._enable_persistence or not self._index_file:
            return

        try:
            index_data = {
                "symbol_index": self._symbol_index,
                "library_paths": [str(path) for path in self._library_paths],
                "created": time.time(),
            }

            with open(self._index_file, "w") as f:
                json.dump(index_data, f, indent=2)

            logger.debug("Saved persistent index")

        except Exception as e:
            logger.warning(f"Failed to save persistent index: {e}")

    def _find_symbol_in_parsed_data(self, parsed_data: List, symbol_name: str) -> Optional[List]:
        """Find symbol data in parsed library data."""
        if not isinstance(parsed_data, list):
            return None

        for item in parsed_data:
            if isinstance(item, list) and len(item) >= 2:
                if str(item[0]) == "symbol" and str(item[1]) == symbol_name:
                    return item

        return None
