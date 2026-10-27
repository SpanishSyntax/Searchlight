"""Tests for Searchlight CLI parsing and execution."""

from __future__ import annotations

import json
from searchlight.cli import main


def test_cli_help(capsys):
    ret = main(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Interactive PDF Search" in captured.out


def test_cli_version(capsys):
    ret = main(["--version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "v0.1.0" in captured.out


def test_cli_no_query_empty():
    ret = main([])
    assert ret == 1


def test_cli_empty_dir_json(tmp_path, capsys):
    ret = main(["quantum", str(tmp_path), "--json"])
    assert ret == 1  # 1 because 0 matches
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["query"] == "quantum"
    assert data["total_matches"] == 0
