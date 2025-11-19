"""BOM (Bill of Materials) property management module.

This module provides tools for auditing, updating, and transforming component
properties in KiCad schematics - useful for BOM cleanup and standardization.
"""

from .auditor import BOMPropertyAuditor, ComponentIssue
from .matcher import PropertyMatcher

__all__ = [
    'BOMPropertyAuditor',
    'ComponentIssue',
    'PropertyMatcher',
]
