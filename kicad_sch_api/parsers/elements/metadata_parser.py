"""
Title block and symbol instances parser for KiCAD schematics.

Handles parsing and serialization of Title block and symbol instances.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class MetadataParser(BaseElementParser):
    """Parser for Title block and symbol instances."""

    def __init__(self):
        """Initialize metadata parser."""
        super().__init__("metadata")

    def _parse_title_block(self, item: List[Any]) -> Dict[str, Any]:
        """Parse title block information."""
        title_block = {}
        for sub_item in item[1:]:
            if isinstance(sub_item, list) and len(sub_item) >= 2:
                key = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None
                if key:
                    title_block[key] = sub_item[1] if len(sub_item) > 1 else None
        return title_block

    def _parse_symbol_instances(self, item: List[Any]) -> List[Any]:
        """Parse symbol_instances section."""
        # For now, just return the raw structure minus the header
        return item[1:] if len(item) > 1 else []

    def _title_block_to_sexp(self, title_block: Dict[str, Any]) -> List[Any]:
        """Convert title block to S-expression."""
        sexp = [sexpdata.Symbol("title_block")]

        # Add standard fields
        for key in ["title", "date", "rev", "company"]:
            if key in title_block and title_block[key]:
                sexp.append([sexpdata.Symbol(key), title_block[key]])

        # Add comments with special formatting
        comments = title_block.get("comments", {})
        if isinstance(comments, dict):
            for comment_num, comment_text in comments.items():
                sexp.append([sexpdata.Symbol("comment"), comment_num, comment_text])

        return sexp
