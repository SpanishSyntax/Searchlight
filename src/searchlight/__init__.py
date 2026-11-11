"""Searchlight - Interactive full-text PDF search, fuzzy discovery, and document preview engine."""

from __future__ import annotations

from searchlight.engine import SearchMatch, SearchResult, search_pdfs
from searchlight.viewer import detect_viewer, open_pdf

__version__ = "0.1.0"
__author__ = "SpanishSyntax"

__all__ = [
    "__version__",
    "search_pdfs",
    "SearchMatch",
    "SearchResult",
    "detect_viewer",
    "open_pdf",
]
