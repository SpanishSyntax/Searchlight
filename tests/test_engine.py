"""Tests for search engine parsing and execution."""

from __future__ import annotations

import pytest
from pathlib import Path
from searchlight.engine import SearchMatch, parse_pdfgrep_output, search_pdfs


def test_parse_pdfgrep_output_standard():
    raw = """/home/user/docs/calculus.pdf:12:The derivative of sin(x) is cos(x).
/home/user/docs/calculus.pdf:45:Integration by parts formula.
/home/user/docs/linear_algebra.pdf:3:Eigenvalues and eigenvectors of A.
"""
    matches = parse_pdfgrep_output(raw)
    assert len(matches) == 3
    assert matches[0].file == "/home/user/docs/calculus.pdf"
    assert matches[0].page == 12
    assert "derivative" in matches[0].text
    assert matches[1].page == 45
    assert matches[2].file == "/home/user/docs/linear_algebra.pdf"
    assert matches[2].page == 3


def test_parse_pdfgrep_output_with_context():
    raw = """/docs/paper.pdf:10:Main Theorem 1.1
/docs/paper.pdf:10-Assume X is a Banach space.
--
/docs/paper.pdf:20:Corollary 2.3
"""
    matches = parse_pdfgrep_output(raw)
    assert len(matches) == 2
    assert matches[0].page == 10
    assert matches[0].text == "Main Theorem 1.1"
    assert len(matches[0].context_after) == 1
    assert "Banach" in matches[0].context_after[0]


def test_search_pdfs_empty_dir(tmp_path):
    res = search_pdfs("matrix", target=tmp_path)
    assert res.total_matches == 0
    assert res.files_scanned == 0


def test_search_pdfs_nonexistent(tmp_path):
    with pytest.raises(FileNotFoundError):
        search_pdfs("test", target=tmp_path / "nonexistent")
