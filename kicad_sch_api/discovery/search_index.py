"""
SQLite-based search index for fast component discovery.

This module creates and maintains a lightweight SQLite database for fast
multi-field component searches, built from the existing SymbolDefinition cache.
"""

import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..library.cache import SymbolDefinition, get_symbol_cache

logger = logging.getLogger(__name__)


class ComponentSearchIndex:
    """Fast SQLite-based search index for KiCAD components."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the search index."""
        self.cache_dir = cache_dir or Path.home() / ".cache" / "kicad-sch-api"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.cache_dir / "search_index.db"
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS components (
                    lib_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    library TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    keywords TEXT DEFAULT '',
                    reference_prefix TEXT DEFAULT 'U',
                    pin_count INTEGER DEFAULT 0,
                    category TEXT DEFAULT '',
                    last_updated REAL DEFAULT 0
                )
            """
            )

            # Create search indexes for fast queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_name 
                ON components(name COLLATE NOCASE)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_description 
                ON components(description COLLATE NOCASE)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_library 
                ON components(library)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_category 
                ON components(category)
            """
            )

            # Full-text search virtual table for advanced queries
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS components_fts 
                USING fts5(lib_id, name, description, keywords, content=components)
            """
            )

            conn.commit()
            logger.debug("Initialized search index database")

    def rebuild_index(self, progress_callback: Optional[callable] = None) -> int:
        """Rebuild the search index from the symbol cache."""
        start_time = time.time()
        symbol_cache = get_symbol_cache()

        # Get all cached symbols
        symbols = []
        for lib_name in symbol_cache._library_index.keys():
            try:
                lib_symbols = symbol_cache.get_library_symbols(lib_name)
                symbols.extend(lib_symbols)

                if progress_callback:
                    progress_callback(f"Indexing {lib_name}: {len(lib_symbols)} symbols")

            except Exception as e:
                logger.warning(f"Failed to load library {lib_name}: {e}")

        # Clear and rebuild index
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("DELETE FROM components")
            conn.execute("DELETE FROM components_fts")

            # Insert symbols in batches for better performance
            batch_size = 100
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i : i + batch_size]

                # Prepare batch data
                batch_data = []
                for symbol in batch:
                    batch_data.append(
                        (
                            symbol.lib_id,
                            symbol.name,
                            symbol.library,
                            symbol.description,
                            symbol.keywords,
                            symbol.reference_prefix,
                            len(symbol.pins),
                            self._categorize_component(symbol),
                            time.time(),
                        )
                    )

                # Insert batch
                conn.executemany(
                    """
                    INSERT OR REPLACE INTO components
                    (lib_id, name, library, description, keywords, reference_prefix, 
                     pin_count, category, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    batch_data,
                )

                # Update FTS table
                conn.executemany(
                    """
                    INSERT OR REPLACE INTO components_fts
                    (lib_id, name, description, keywords)
                    VALUES (?, ?, ?, ?)
                """,
                    [(data[0], data[1], data[3], data[4]) for data in batch_data],
                )

                if progress_callback:
                    progress_callback(
                        f"Indexed {min(i + batch_size, len(symbols))}/{len(symbols)} components"
                    )

            conn.commit()

        elapsed = time.time() - start_time
        logger.info(f"Rebuilt search index with {len(symbols)} components in {elapsed:.2f}s")
        return len(symbols)

    def search(
        self,
        query: str,
        library: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search components using multiple strategies."""
        results = []

        # Try different search strategies
        strategies = [
            self._search_exact_match,
            self._search_prefix_match,
            self._search_contains,
            self._search_fts,
        ]

        for strategy in strategies:
            try:
                strategy_results = strategy(query, library, category, limit - len(results))

                # Avoid duplicates
                existing_ids = {r["lib_id"] for r in results}
                new_results = [r for r in strategy_results if r["lib_id"] not in existing_ids]

                results.extend(new_results)

                if len(results) >= limit:
                    break

            except Exception as e:
                logger.debug(f"Search strategy failed: {e}")

        return results[:limit]

    def _search_exact_match(
        self, query: str, library: Optional[str], category: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Search for exact name matches."""
        conditions = ["name = ? COLLATE NOCASE"]
        params = [query]

        if library:
            conditions.append("library = ?")
            params.append(library)

        if category:
            conditions.append("category = ?")
            params.append(category)

        sql = f"""
            SELECT lib_id, name, library, description, keywords, reference_prefix, 
                   pin_count, category, 1.0 as match_score
            FROM components
            WHERE {' AND '.join(conditions)}
            ORDER BY name
            LIMIT ?
        """
        params.append(limit)

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]

    def _search_prefix_match(
        self, query: str, library: Optional[str], category: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Search for components starting with query."""
        conditions = ["name LIKE ? COLLATE NOCASE"]
        params = [f"{query}%"]

        if library:
            conditions.append("library = ?")
            params.append(library)

        if category:
            conditions.append("category = ?")
            params.append(category)

        sql = f"""
            SELECT lib_id, name, library, description, keywords, reference_prefix, 
                   pin_count, category, 0.8 as match_score
            FROM components
            WHERE {' AND '.join(conditions)}
            ORDER BY name
            LIMIT ?
        """
        params.append(limit)

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]

    def _search_contains(
        self, query: str, library: Optional[str], category: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Search for components containing query in name or description."""
        conditions = ["(name LIKE ? COLLATE NOCASE OR description LIKE ? COLLATE NOCASE)"]
        params = [f"%{query}%", f"%{query}%"]

        if library:
            conditions.append("library = ?")
            params.append(library)

        if category:
            conditions.append("category = ?")
            params.append(category)

        sql = f"""
            SELECT lib_id, name, library, description, keywords, reference_prefix, 
                   pin_count, category, 0.6 as match_score
            FROM components
            WHERE {' AND '.join(conditions)}
            ORDER BY 
                CASE WHEN name LIKE ? COLLATE NOCASE THEN 1 ELSE 2 END,
                name
            LIMIT ?
        """
        params.extend([f"%{query}%", limit])

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]

    def _search_fts(
        self, query: str, library: Optional[str], category: Optional[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Full-text search using FTS5."""
        # Build FTS query
        fts_query = " ".join(f'"{term}"*' for term in query.split())

        sql = """
            SELECT c.lib_id, c.name, c.library, c.description, c.keywords, 
                   c.reference_prefix, c.pin_count, c.category, 
                   fts.rank as match_score
            FROM components_fts fts
            JOIN components c ON c.lib_id = fts.lib_id
            WHERE fts MATCH ?
        """
        params = [fts_query]

        if library:
            sql += " AND c.library = ?"
            params.append(library)

        if category:
            sql += " AND c.category = ?"
            params.append(category)

        sql += " ORDER BY fts.rank LIMIT ?"
        params.append(limit)

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute(sql, params)]
        except sqlite3.OperationalError:
            # FTS query failed, return empty results
            return []

    def get_libraries(self) -> List[Dict[str, Any]]:
        """Get all available libraries with component counts."""
        sql = """
            SELECT library, COUNT(*) as component_count
            FROM components
            GROUP BY library
            ORDER BY library
        """

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql)]

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all component categories with counts."""
        sql = """
            SELECT category, COUNT(*) as component_count
            FROM components
            WHERE category != ''
            GROUP BY category
            ORDER BY component_count DESC
        """

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql)]

    def validate_component(self, lib_id: str) -> Optional[Dict[str, Any]]:
        """Check if a component exists in the index."""
        sql = """
            SELECT lib_id, name, library, description, keywords, reference_prefix, 
                   pin_count, category
            FROM components
            WHERE lib_id = ?
        """

        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(sql, [lib_id]).fetchone()
            return dict(result) if result else None

    def get_stats(self) -> Dict[str, Any]:
        """Get search index statistics."""
        with sqlite3.connect(str(self.db_path)) as conn:
            total_components = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
            total_libraries = conn.execute(
                "SELECT COUNT(DISTINCT library) FROM components"
            ).fetchone()[0]

            # Get library breakdown
            library_stats = conn.execute(
                """
                SELECT library, COUNT(*) as count
                FROM components
                GROUP BY library
                ORDER BY count DESC
                LIMIT 10
            """
            ).fetchall()

        return {
            "total_components": total_components,
            "total_libraries": total_libraries,
            "top_libraries": [{"library": lib, "count": count} for lib, count in library_stats],
            "database_path": str(self.db_path),
            "database_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2),
        }

    def _categorize_component(self, symbol: SymbolDefinition) -> str:
        """Categorize a component based on its properties."""
        prefix = symbol.reference_prefix.upper()
        name_lower = symbol.name.lower()
        desc_lower = symbol.description.lower()

        # Category mapping based on reference prefix and description
        if prefix == "R":
            return "resistor"
        elif prefix == "C":
            return "capacitor"
        elif prefix == "L":
            return "inductor"
        elif prefix in ["D", "LED"]:
            return "diode"
        elif prefix == "Q":
            return "transistor"
        elif prefix == "U":
            if any(term in desc_lower for term in ["microcontroller", "mcu", "processor"]):
                return "microcontroller"
            elif any(term in desc_lower for term in ["amplifier", "op-amp", "opamp"]):
                return "amplifier"
            elif any(term in desc_lower for term in ["regulator", "ldo", "buck", "boost"]):
                return "regulator"
            else:
                return "integrated_circuit"
        elif prefix == "J":
            return "connector"
        elif prefix in ["SW", "S"]:
            return "switch"
        elif prefix == "Y":
            return "crystal"
        elif prefix == "TP":
            return "test_point"
        else:
            return "other"


# Global search index instance
_global_search_index: Optional[ComponentSearchIndex] = None


def get_search_index() -> ComponentSearchIndex:
    """Get the global search index instance."""
    global _global_search_index
    if _global_search_index is None:
        _global_search_index = ComponentSearchIndex()
    return _global_search_index


def ensure_index_built(rebuild: bool = False) -> int:
    """Ensure the search index is built and up-to-date."""
    index = get_search_index()

    if rebuild or not index.db_path.exists():
        logger.info("Building component search index...")
        return index.rebuild_index()
    else:
        # Check if index needs updating based on symbol cache
        stats = index.get_stats()
        logger.info(f"Search index ready: {stats['total_components']} components")
        return stats["total_components"]
