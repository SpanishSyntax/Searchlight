"""Document viewer detection and launcher with page-jumping capabilities."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


VIEWER_CANDIDATES = [
    "zathura",
    "sioyek",
    "okular",
    "evince",
    "xdg-open",
]


def detect_viewer(preferred: str | None = None) -> str:
    """Detects the best available PDF viewer executable on the system."""
    if preferred and shutil.which(preferred):
        return preferred

    env_viewer = os.environ.get("PDFVIEWER") or os.environ.get("READER")
    if env_viewer and shutil.which(env_viewer):
        return env_viewer

    for candidate in VIEWER_CANDIDATES:
        if shutil.which(candidate):
            return candidate

    return "xdg-open"


def build_viewer_command(viewer: str, file_path: Path | str, page: int | None = None) -> list[str]:
    """Constructs the command-line arguments to launch the viewer, jumping to page if supported."""
    file_str = str(Path(file_path).resolve())
    base_name = Path(viewer).name.lower()

    if page is not None and page > 0:
        if base_name == "zathura":
            return [viewer, "-P", str(page), file_str]
        elif base_name == "sioyek":
            return [viewer, "--page", str(page), file_str]
        elif base_name in ("okular", "evince"):
            return [viewer, "-p", str(page), file_str]
        elif base_name == "mupdf":
            return [viewer, file_str, str(page)]

    return [viewer, file_str]


def open_pdf(file_path: Path | str, page: int | None = None, viewer: str | None = None) -> bool:
    """Launches the PDF document asynchronously in the background viewer."""
    target_path = Path(file_path).resolve()
    if not target_path.exists():
        return False

    chosen_viewer = detect_viewer(viewer)
    cmd = build_viewer_command(chosen_viewer, target_path, page)

    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True
    except Exception:
        # Fallback to xdg-open if custom viewer command failed
        if chosen_viewer != "xdg-open" and shutil.which("xdg-open"):
            try:
                subprocess.Popen(
                    ["xdg-open", str(target_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return True
            except Exception:
                return False
        return False
