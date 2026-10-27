"""Interactive match selection using fzf or native Prism menus."""

from __future__ import annotations

import shutil
import subprocess
from typing import Sequence

from searchlight.engine import SearchMatch
from searchlight.ui import select_menu, strip_ansi, ui


def select_match_fzf(matches: Sequence[SearchMatch], prompt: str = "Searchlight ❯ ") -> SearchMatch | None:
    """Uses fzf for fuzzy interactive filtering and selection."""
    if not matches:
        return None

    # Construct formatted input for fzf with indexed keys to guarantee exact mapping
    lines = []
    for idx, m in enumerate(matches):
        page_tag = f"Page {m.page:>3}" if m.page is not None else "Page   -"
        clean_text = m.text.replace("\n", " ").strip()
        display_line = f"[{idx:03d}]  {ui.bold_cyan(page_tag)}  {ui.dim(m.display_path)}  │ {clean_text}"
        lines.append(display_line)

    input_data = "\n".join(lines)
    cmd = [
        "fzf",
        "--ansi",
        f"--prompt={prompt}",
        "--height=50%",
        "--layout=reverse",
        "--border",
        "--header=ENTER: Open in Viewer | ESC: Cancel",
    ]

    try:
        proc = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return None

        selected = proc.stdout.strip()
        if not selected:
            return None

        # Parse index from selection prefix "[001]"
        plain = strip_ansi(selected)
        if plain.startswith("[") and "]" in plain:
            idx_str = plain[1 : plain.index("]")]
            if idx_str.isdigit():
                idx = int(idx_str)
                if 0 <= idx < len(matches):
                    return matches[idx]
    except Exception:
        return None

    return None


def select_match_menu(matches: Sequence[SearchMatch], title: str = "Select a match to open:") -> SearchMatch | None:
    """Uses native Prism interactive menu when fzf is unavailable."""
    if not matches:
        return None

    # Create menu options
    options = []
    for idx, m in enumerate(matches):
        page_tag = f"P.{m.page}" if m.page is not None else "P.?"
        preview = m.text[:60] + "..." if len(m.text) > 60 else m.text
        label = f"{ui.bold_cyan(f'[{page_tag}]')} {m.display_path} — {ui.dim(preview)}"
        options.append((str(idx), label))

    options.append(("cancel", ui.dim("Cancel and exit")))

    selected_key = select_menu(title=title, options=options)
    if not selected_key or selected_key == "cancel":
        return None

    if selected_key.isdigit():
        idx = int(selected_key)
        if 0 <= idx < len(matches):
            return matches[idx]

    return None


def select_match(
    matches: Sequence[SearchMatch],
    prefer_fzf: bool = True,
    prompt: str = "Searchlight ❯ ",
) -> SearchMatch | None:
    """Selects a match interactively via fzf (if available and preferred) or native menu."""
    if not matches:
        return None

    if prefer_fzf and shutil.which("fzf"):
        selected = select_match_fzf(matches, prompt=prompt)
        if selected is not None:
            return selected

    return select_match_menu(matches)
