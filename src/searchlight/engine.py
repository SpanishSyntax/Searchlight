"""Core PDF search engine supporting pdfgrep and poppler-utils backends."""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class SearchMatch:
    """Represents a single text match found within a PDF document."""

    file: str
    page: int | None = None
    line_number: int | None = None
    text: str = ""
    context_before: list[str] = field(default_factory=list)
    context_after: list[str] = field(default_factory=list)

    @property
    def display_path(self) -> str:
        """Returns relative or shortened path for display."""
        try:
            return str(Path(self.file).relative_to(Path.cwd()))
        except ValueError:
            return self.file

    def to_dict(self) -> dict[str, Any]:
        """Converts match to serializable dictionary."""
        return {
            "file": self.file,
            "display_path": self.display_path,
            "page": self.page,
            "line_number": self.line_number,
            "text": self.text,
            "context_before": self.context_before,
            "context_after": self.context_after,
        }


@dataclass
class SearchResult:
    """Container holding full results of a PDF search query."""

    query: str
    target: str
    matches: list[SearchMatch] = field(default_factory=list)
    files_scanned: int = 0
    elapsed_sec: float = 0.0

    @property
    def total_matches(self) -> int:
        return len(self.matches)

    @property
    def matching_files(self) -> list[str]:
        seen = set()
        out = []
        for m in self.matches:
            if m.file not in seen:
                seen.add(m.file)
                out.append(m.file)
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "target": self.target,
            "total_matches": self.total_matches,
            "matching_files": self.matching_files,
            "files_scanned": self.files_scanned,
            "elapsed_sec": round(self.elapsed_sec, 4),
            "matches": [m.to_dict() for m in self.matches],
        }


def parse_pdfgrep_output(stdout: str) -> list[SearchMatch]:
    """Parses raw stdout from pdfgrep -H -n into structured SearchMatch objects."""
    matches: list[SearchMatch] = []
    current_match: SearchMatch | None = None

    for raw_line in stdout.splitlines():
        line = raw_line.rstrip()
        if not line or line == "--":
            if current_match:
                matches.append(current_match)
                current_match = None
            continue

        # Look for match pattern: filepath:page:text or filepath:page-context_text
        match_pat = re.match(r"^(.+?\.pdf):(\d+):(.*)$", line, re.IGNORECASE)
        ctx_pat = re.match(r"^(.+?\.pdf):(\d+)-(.*)$", line, re.IGNORECASE)

        if match_pat:
            if current_match:
                matches.append(current_match)
            fpath, page_str, text = match_pat.groups()
            current_match = SearchMatch(
                file=fpath,
                page=int(page_str),
                text=text.strip(),
            )
        elif ctx_pat and current_match:
            _, _, ctx_text = ctx_pat.groups()
            current_match.context_after.append(ctx_text.strip())
        else:
            # Fallback for generic colon splitting
            parts = line.split(":", 2)
            if len(parts) >= 2:
                if current_match:
                    matches.append(current_match)
                fpath = parts[0]
                page_num = int(parts[1]) if parts[1].isdigit() else None
                text = parts[2].strip() if len(parts) > 2 else ""
                current_match = SearchMatch(
                    file=fpath,
                    page=page_num,
                    text=text,
                )

    if current_match:
        matches.append(current_match)

    return matches


def _search_with_pdftotext(
    pattern: str,
    pdf_files: Sequence[Path],
    ignore_case: bool = True,
    max_count: int = 50,
) -> list[SearchMatch]:
    """Fallback search backend utilizing pdftotext from poppler-utils."""
    matches: list[SearchMatch] = []
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error:
        regex = re.compile(re.escape(pattern), flags)

    for pdf_path in pdf_files:
        cmd = ["pdftotext", str(pdf_path), "-"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                continue

            # In pdftotext output, pages are separated by form feed \x0c
            pages = proc.stdout.split("\x0c")
            file_match_count = 0

            for page_idx, page_text in enumerate(pages, 1):
                if file_match_count >= max_count:
                    break
                for line_idx, line in enumerate(page_text.splitlines(), 1):
                    if regex.search(line):
                        matches.append(
                            SearchMatch(
                                file=str(pdf_path),
                                page=page_idx,
                                line_number=line_idx,
                                text=line.strip(),
                            )
                        )
                        file_match_count += 1
                        if file_match_count >= max_count:
                            break
        except Exception:
            continue

    return matches


def search_pdfs(
    query: str,
    target: str | Path = ".",
    ignore_case: bool = True,
    recursive: bool = True,
    max_count: int = 50,
    context: int = 0,
    page: int | None = None,
) -> SearchResult:
    """Executes a full-text search across PDF documents in the specified target."""
    start_time = time.perf_counter()
    target_path = Path(target).expanduser().resolve()

    if not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")

    # Discover candidate PDF files
    if target_path.is_file():
        if target_path.suffix.lower() != ".pdf":
            raise ValueError(f"Target file is not a PDF: {target_path}")
        pdf_files = [target_path]
    elif recursive:
        pdf_files = sorted(target_path.rglob("*.pdf"))
    else:
        pdf_files = sorted(target_path.glob("*.pdf"))

    if not pdf_files:
        return SearchResult(
            query=query,
            target=str(target_path),
            matches=[],
            files_scanned=0,
            elapsed_sec=time.perf_counter() - start_time,
        )

    # Primary backend: pdfgrep
    has_pdfgrep = shutil.which("pdfgrep") is not None
    matches: list[SearchMatch] = []

    if has_pdfgrep:
        cmd = ["pdfgrep", "-H", "-n", "--color=never"]
        if ignore_case:
            cmd.append("-i")
        if recursive and target_path.is_dir():
            cmd.append("-r")
        if max_count > 0:
            cmd.extend(["-m", str(max_count)])
        if context > 0:
            cmd.extend(["-C", str(context)])
        if page is not None and page > 0:
            cmd.extend(["--page-range", str(page)])

        cmd.append(query)
        cmd.append(str(target_path))

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60.0,
            )
            # pdfgrep returns 0 on match, 1 on no match, 2 on error
            if proc.returncode in (0, 1):
                matches = parse_pdfgrep_output(proc.stdout)
            elif proc.returncode == 2 and not proc.stdout:
                # If pdfgrep errored out, fallback to poppler
                matches = _search_with_pdftotext(query, pdf_files, ignore_case, max_count)
        except Exception:
            matches = _search_with_pdftotext(query, pdf_files, ignore_case, max_count)
    else:
        # Fallback backend: pdftotext
        matches = _search_with_pdftotext(query, pdf_files, ignore_case, max_count)

    # Filter by specific page if requested and not handled by backend
    if page is not None:
        matches = [m for m in matches if m.page == page]

    elapsed = time.perf_counter() - start_time
    return SearchResult(
        query=query,
        target=str(target_path),
        matches=matches,
        files_scanned=len(pdf_files),
        elapsed_sec=elapsed,
    )
