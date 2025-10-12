"""
Component discovery tools for KiCAD schematic API.

This module provides fast search and discovery capabilities for KiCAD components
using a SQLite search index built from the existing symbol cache.
"""

from .search_index import ComponentSearchIndex, get_search_index

__all__ = ["ComponentSearchIndex", "get_search_index"]
