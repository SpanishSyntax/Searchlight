"""Tests for Searchlight configuration loader."""

from __future__ import annotations

from pathlib import Path
from searchlight.config import load_user_config


def test_load_user_config_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    cfg = load_user_config()
    assert cfg == {}


def test_load_user_config_valid(monkeypatch, tmp_path):
    cfg_dir = tmp_path / "searchlight"
    cfg_dir.mkdir(parents=True)
    cfg_file = cfg_dir / "searchlight.toml"
    cfg_file.write_text("""
[general]
recursive = false
ignore_case = true
viewer = "zathura"
use_fzf = false
max_count = 100
""")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    cfg = load_user_config()
    assert cfg.get("recursive") is False
    assert cfg.get("viewer") == "zathura"
    assert cfg.get("max_count") == 100
