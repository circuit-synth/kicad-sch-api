"""
Symbol resolver interfaces for symbol library operations.

These interfaces define the contract for resolving symbols from libraries,
handling inheritance chains, and managing symbol caching.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol


class ISymbolResolver(Protocol):
    """Interface for symbol resolution and inheritance operations."""

    def resolve_symbol(self, lib_id: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a symbol with full inheritance chain applied.

        Args:
            lib_id: Library identifier (e.g., "Device:R")

        Returns:
            Fully resolved symbol data with inheritance applied,
            or None if symbol not found

        Raises:
            SymbolError: If symbol resolution fails
        """
        ...

    def get_symbol_raw(self, lib_id: str) -> Optional[Dict[str, Any]]:
        """
        Get raw symbol data without inheritance resolution.

        Args:
            lib_id: Library identifier

        Returns:
            Raw symbol data as stored in library,
            or None if symbol not found
        """
        ...

    def resolve_inheritance_chain(self, lib_id: str) -> List[str]:
        """
        Get the complete inheritance chain for a symbol.

        Args:
            lib_id: Library identifier

        Returns:
            List of lib_ids in inheritance order (base to derived)

        Raises:
            SymbolError: If circular inheritance detected
        """
        ...

    def is_symbol_available(self, lib_id: str) -> bool:
        """
        Check if a symbol is available in the libraries.

        Args:
            lib_id: Library identifier

        Returns:
            True if symbol exists and can be resolved
        """
        ...

    def clear_cache(self) -> None:
        """Clear any cached symbol data."""
        ...


class ISymbolCache(Protocol):
    """Interface for symbol library caching operations."""

    def get_symbol(self, lib_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a symbol from cache or load from library.

        Args:
            lib_id: Library identifier

        Returns:
            Symbol data or None if not found
        """
        ...

    def cache_symbol(self, lib_id: str, symbol_data: Dict[str, Any]) -> None:
        """
        Cache symbol data.

        Args:
            lib_id: Library identifier
            symbol_data: Symbol data to cache
        """
        ...

    def invalidate(self, lib_id: Optional[str] = None) -> None:
        """
        Invalidate cache entries.

        Args:
            lib_id: Specific symbol to invalidate, or None for all
        """
        ...

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)
        """
        ...
