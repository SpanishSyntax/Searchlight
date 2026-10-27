"""Tests for viewer detection and command generation."""

from __future__ import annotations

from pathlib import Path
from searchlight.viewer import build_viewer_command, detect_viewer, open_pdf


def test_detect_viewer_preferred(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/" + cmd if cmd == "zathura" else None)
    assert detect_viewer("zathura") == "zathura"


def test_detect_viewer_fallback(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda cmd: None)
    assert detect_viewer() == "xdg-open"


def test_build_viewer_command_zathura():
    cmd = build_viewer_command("zathura", "/tmp/doc.pdf", page=15)
    assert cmd == ["zathura", "-P", "15", "/tmp/doc.pdf"]


def test_build_viewer_command_sioyek():
    cmd = build_viewer_command("sioyek", "/tmp/doc.pdf", page=7)
    assert cmd == ["sioyek", "--page", "7", "/tmp/doc.pdf"]


def test_build_viewer_command_okular():
    cmd = build_viewer_command("okular", "/tmp/doc.pdf", page=3)
    assert cmd == ["okular", "-p", "3", "/tmp/doc.pdf"]


def test_build_viewer_command_xdg():
    cmd = build_viewer_command("xdg-open", "/tmp/doc.pdf", page=3)
    assert cmd == ["xdg-open", "/tmp/doc.pdf"]


def test_open_pdf_nonexistent():
    assert open_pdf("/nonexistent/file.pdf") is False
