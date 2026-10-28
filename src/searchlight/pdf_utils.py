"""PDF document utility functions for metadata extraction and text reading."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def get_pdf_info(pdf_path: str | Path) -> dict[str, Any]:
    """Extracts structured metadata from a PDF file using `pdfinfo`.

    Args:
        pdf_path: Path to the target PDF file.

    Returns:
        Dictionary containing metadata attributes like title, author, pages, etc.
    """
    path = Path(pdf_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Target is not a PDF file: {path}")

    res: dict[str, Any] = {
        "file": str(path),
        "name": path.name,
        "size_bytes": path.stat().st_size,
    }

    pdfinfo_bin = shutil.which("pdfinfo")
    if not pdfinfo_bin:
        res["note"] = "`pdfinfo` utility not found in PATH; basic file info returned."
        return res

    proc = subprocess.run(
        [pdfinfo_bin, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        res["error"] = proc.stderr.strip() or f"pdfinfo failed with code {proc.returncode}"
        return res

    key_map = {
        "Title": "title",
        "Subject": "subject",
        "Keywords": "keywords",
        "Author": "author",
        "Creator": "creator",
        "Producer": "producer",
        "CreationDate": "creation_date",
        "ModDate": "modification_date",
        "Tagged": "tagged",
        "UserProperties": "user_properties",
        "Suspects": "suspects",
        "Form": "form",
        "JavaScript": "javascript",
        "Pages": "pages",
        "Encrypted": "encrypted",
        "Page size": "page_size",
        "Page rot": "page_rot",
        "File size": "file_size_str",
        "Optimized": "optimized",
        "PDF version": "pdf_version",
    }

    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(":", 1)
        if len(parts) == 2:
            raw_key, val = parts[0].strip(), parts[1].strip()
            dict_key = key_map.get(raw_key, raw_key.lower().replace(" ", "_"))
            if dict_key == "pages":
                try:
                    res[dict_key] = int(val)
                except ValueError:
                    res[dict_key] = val
            elif dict_key == "encrypted":
                res[dict_key] = val.lower().startswith("yes")
            else:
                res[dict_key] = val

    return res


def extract_pdf_text(
    pdf_path: str | Path,
    first_page: int | None = None,
    last_page: int | None = None,
    layout: bool = False,
) -> dict[str, Any]:
    """Extracts text content from a PDF document using `pdftotext`.

    Args:
        pdf_path: Path to the target PDF file.
        first_page: Optional starting page (1-based index).
        last_page: Optional ending page (1-based index).
        layout: Whether to maintain physical layout.

    Returns:
        Dictionary with extracted text, page range, and character count.
    """
    path = Path(pdf_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Target is not a PDF file: {path}")

    pdftotext_bin = shutil.which("pdftotext")
    if not pdftotext_bin:
        raise RuntimeError("`pdftotext` from poppler-utils was not found in PATH.")

    cmd = [pdftotext_bin]
    if first_page is not None and first_page > 0:
        cmd.extend(["-f", str(first_page)])
    if last_page is not None and last_page > 0:
        cmd.extend(["-l", str(last_page)])
    if layout:
        cmd.append("-layout")

    cmd.extend([str(path), "-"])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {
            "status": "error",
            "file": str(path),
            "error": proc.stderr.strip() or f"pdftotext failed with exit code {proc.returncode}",
        }

    text = proc.stdout
    return {
        "status": "ok",
        "file": str(path),
        "first_page": first_page,
        "last_page": last_page,
        "char_count": len(text),
        "text": text,
    }
