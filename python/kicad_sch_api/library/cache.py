"""
High-performance symbol library cache for KiCAD schematic API.

This module provides intelligent caching and lookup functionality for KiCAD symbol libraries,
significantly improving performance for applications that work with many components.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..core.types import Point, SchematicPin, PinType, PinShape
from ..utils.validation import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class SymbolDefinition:
    """Complete definition of a symbol from KiCAD library."""
    
    lib_id: str  # e.g., "Device:R"
    name: str    # Symbol name within library
    library: str # Library name
    reference_prefix: str  # e.g., "R" for resistors
    description: str = ""
    keywords: str = ""
    datasheet: str = ""
    pins: List[SchematicPin] = field(default_factory=list)
    units: int = 1
    unit_names: Dict[int, str] = field(default_factory=dict)
    power_symbol: bool = False
    graphic_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    load_time: float = 0.0
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Post-initialization processing."""
        self.last_accessed = time.time()
        
        # Validate lib_id format
        if ':' not in self.lib_id:
            raise ValidationError(f"Invalid lib_id format: {self.lib_id} (should be Library:Symbol)")
        
        # Extract library from lib_id if not provided
        if not self.library:
            self.library = self.lib_id.split(':')[0]
    
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
                coordinates.extend([
                    (cx - radius, cy - radius),
                    (cx + radius, cy + radius)
                ])
        
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
        
        if not library_path.suffix == '.kicad_sym':
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
            last_modified=stat.st_mtime
        )
        
        logger.info(f"Added library: {library_name} ({library_path})")
        return True

    def discover_libraries(self, search_paths: List[Union[str, Path]] = None) -> int:
        """
        Automatically discover KiCAD symbol libraries.
        
        Args:
            search_paths: Directories to search for .kicad_sym files
            
        Returns:
            Number of libraries discovered and added
        """
        if search_paths is None:
            search_paths = self._get_default_library_paths()
        
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
        # Check cache first
        if lib_id in self._symbols:
            self._cache_hits += 1
            symbol = self._symbols[lib_id]
            symbol.access_count += 1
            symbol.last_accessed = time.time()
            return symbol
        
        # Cache miss - try to load symbol
        self._cache_misses += 1
        return self._load_symbol(lib_id)

    def search_symbols(self, 
                      query: str, 
                      library: Optional[str] = None,
                      limit: int = 50) -> List[SymbolDefinition]:
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
        if len(results) < 5 and ':' in query:
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
        return [symbol for symbol in self._symbols.values() 
                if symbol.library == library_name]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': round(hit_rate, 2),
            'total_symbols_cached': len(self._symbols),
            'total_libraries': len(self._library_paths),
            'total_load_time_ms': round(self._total_load_time * 1000, 2),
            'avg_load_time_per_symbol_ms': round(
                (self._total_load_time / len(self._symbols) * 1000) 
                if self._symbols else 0, 2
            )
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
        if ':' not in lib_id:
            logger.warning(f"Invalid lib_id format: {lib_id}")
            return None
        
        library_name, symbol_name = lib_id.split(':', 1)
        
        if library_name not in self._library_index:
            logger.warning(f"Library not found: {library_name}")
            return None
        
        library_path = self._library_index[library_name]
        return self._load_symbol_from_library(library_path, lib_id)

    def _load_symbol_from_library(self, library_path: Path, lib_id: str) -> Optional[SymbolDefinition]:
        """Load a specific symbol from a library file."""
        start_time = time.time()
        
        try:
            # This is a simplified version - in reality, you'd parse the .kicad_sym file
            # For now, create a basic symbol definition
            library_name, symbol_name = lib_id.split(':', 1)
            
            # Create basic symbol definition
            # In a real implementation, this would parse the actual .kicad_sym file
            symbol = SymbolDefinition(
                lib_id=lib_id,
                name=symbol_name,
                library=library_name,
                reference_prefix=self._guess_reference_prefix(symbol_name),
                description=f"{symbol_name} component",
                pins=[],  # Would be loaded from actual file
                load_time=time.time() - start_time
            )
            
            self._symbols[lib_id] = symbol
            self._symbol_index[symbol_name] = lib_id
            self._total_load_time += symbol.load_time
            
            logger.debug(f"Loaded symbol {lib_id} in {symbol.load_time:.3f}s")
            return symbol
            
        except Exception as e:
            logger.error(f"Error loading symbol {lib_id} from {library_path}: {e}")
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
                    library_path=library_path,
                    file_size=stat.st_size,
                    last_modified=stat.st_mtime
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
            'R': 'R',           # Resistor
            'C': 'C',           # Capacitor  
            'L': 'L',           # Inductor
            'D': 'D',           # Diode
            'LED': 'D',         # LED
            'Q': 'Q',           # Transistor
            'U': 'U',           # IC
            'J': 'J',           # Connector
            'SW': 'SW',         # Switch
            'TP': 'TP',         # Test point
            'FB': 'FB',         # Ferrite bead
        }
        
        symbol_upper = symbol_name.upper()
        for key, prefix in prefix_mapping.items():
            if symbol_upper.startswith(key):
                return prefix
        
        # Default to 'U' for unknown symbols
        return 'U'

    def _get_default_library_paths(self) -> List[Path]:
        """Get default KiCAD library search paths."""
        search_paths = []
        
        # Common KiCAD installation paths
        if os.name == 'nt':  # Windows
            search_paths.extend([
                Path("C:/Program Files/KiCad/9.0/share/kicad/symbols"),
                Path("C:/Program Files (x86)/KiCad/9.0/share/kicad/symbols"),
            ])
        elif os.name == 'posix':  # Linux/Mac
            search_paths.extend([
                Path("/usr/share/kicad/symbols"),
                Path("/usr/local/share/kicad/symbols"),
                Path.home() / ".local/share/kicad/symbols",
            ])
        
        # User documents
        search_paths.extend([
            Path.home() / "Documents/KiCad/symbols",
            Path.home() / "kicad/symbols",
        ])
        
        return [path for path in search_paths if path.exists()]

    def _load_persistent_index(self):
        """Load persistent symbol index from disk."""
        if not self._enable_persistence or not self._index_file or not self._index_file.exists():
            return
        
        try:
            with open(self._index_file, 'r') as f:
                index_data = json.load(f)
                
            # Restore basic index data
            self._symbol_index = index_data.get('symbol_index', {})
            
            # Restore library paths
            for lib_path_str in index_data.get('library_paths', []):
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
                'symbol_index': self._symbol_index,
                'library_paths': [str(path) for path in self._library_paths],
                'cache_stats': self.get_performance_stats()
            }
            
            with open(self._index_file, 'w') as f:
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