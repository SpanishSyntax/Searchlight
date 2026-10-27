"""Command-line interface and argument router for Searchlight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from searchlight import __version__
from searchlight.config import load_user_config
from searchlight.engine import search_pdfs
from searchlight.interactive import select_match
from searchlight.ui import add_color_args, handle_color_args, ui
from searchlight.viewer import detect_viewer, open_pdf


def print_help() -> None:
    """Prints colored usage instructions matching Frost iceberg standards."""
    print(f"""{ui.badge()} {ui.bold("Interactive PDF Search, Fuzzy Discovery & Preview Engine")}

{ui.blue("Usage:")}
  searchlight <search-term> [path] [options]    Search PDFs and open interactive picker
  searchlight [options]                         Interactive search wizard

{ui.blue("Options:")}
  -d, --dir DIR          Target directory or PDF file to search (default: current directory)
  -r, --recursive        Recursively scan all subdirectories for PDF files (default: true)
  --no-recursive         Search only the immediate directory
  -i, --ignore-case      Case-insensitive pattern matching (default: true)
  -s, --case-sensitive   Enable case-sensitive matching
  -C, --context NUM      Number of context lines before and after match (default: 0)
  -m, --max-count NUM    Maximum matches per document (default: 50)
  -p, --page NUM         Search only a specific page number
  --viewer CMD           Custom PDF viewer executable (e.g. zathura, sioyek, okular, xdg-open)
  --fzf                  Use fzf for interactive selection if available (default: true)
  --no-fzf               Use native terminal menu instead of fzf
  -o, --open             Open selected PDF in viewer (default in interactive mode)
  --no-open              Do not open viewer after selection
  -n, --dry-run          Print all matches without opening an interactive picker
  --json                 Output search results as JSON to stdout
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored output
  -h, --help             Show this help message and exit
  -V, -v, --version      Show version information and exit

{ui.blue("Configuration:")}
  User defaults can be defined in ~/.config/searchlight/searchlight.toml:
    [general]
    recursive = true
    ignore_case = true
    viewer = "zathura"
    use_fzf = true

{ui.blue("Examples:")}
  searchlight "Hamiltonian"                     # Fuzzy search current dir and subdirs
  searchlight "proof of lemma" ./papers/        # Search specific papers directory
  searchlight "Theorem 4.2" -p 12               # Search only page 12 of PDFs
  searchlight "Laplace" -n                      # List all matching occurrences
  searchlight "Schrodinger" --json              # Output machine-readable JSON
""")


def _build_parser(user_cfg: dict[str, Any]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="searchlight", add_help=False)
    parser.add_argument("query", nargs="?", default="", help="Text or regex pattern to search for.")
    parser.add_argument("path", nargs="?", default="", help="Optional target directory or file.")
    parser.add_argument("-d", "--dir", default="", help="Target directory (default: current directory).")

    # Recursive
    rec_default = bool(user_cfg.get("recursive", True))
    parser.add_argument("-r", "--recursive", dest="recursive", action="store_true", default=rec_default)
    parser.add_argument("--no-recursive", dest="recursive", action="store_false")

    # Case sensitivity
    ic_default = bool(user_cfg.get("ignore_case", True))
    parser.add_argument("-i", "--ignore-case", dest="ignore_case", action="store_true", default=ic_default)
    parser.add_argument("-s", "--case-sensitive", dest="ignore_case", action="store_false")

    # Search tuning
    parser.add_argument("-C", "--context", type=int, default=int(user_cfg.get("context", 0)))
    parser.add_argument("-m", "--max-count", type=int, default=int(user_cfg.get("max_count", 50)))
    parser.add_argument("-p", "--page", type=int, default=None)

    # Viewer & fzf
    parser.add_argument("--viewer", default=str(user_cfg.get("viewer", "")))
    fzf_default = bool(user_cfg.get("use_fzf", True))
    parser.add_argument("--fzf", dest="use_fzf", action="store_true", default=fzf_default)
    parser.add_argument("--no-fzf", dest="use_fzf", action="store_false")

    # Actions
    parser.add_argument("-o", "--open", dest="open_viewer", action="store_true", default=True)
    parser.add_argument("--no-open", dest="open_viewer", action="store_false")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Print matches and exit without picker.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")

    add_color_args(parser)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-V", "-v", "--version", action="store_true")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    user_cfg = load_user_config()
    if "color" in user_cfg:
        ui.set_color_mode(str(user_cfg["color"]))
    handle_color_args(raw_args)

    if any(a in ("-h", "--help", "help") for a in raw_args):
        print_help()
        return 0

    if any(a in ("-V", "-v", "--version", "version") for a in raw_args):
        print(f"{ui.badge()} {ui.bold(f'v{__version__}')}")
        return 0

    parser = _build_parser(user_cfg)
    args = parser.parse_args(raw_args)

    # Determine target path
    target = args.path or args.dir or "."
    target_path = Path(target).expanduser().resolve()
    if not target_path.exists():
        ui.error(f"Target path does not exist: {target_path}")
        return 1

    # Determine query
    query = args.query.strip()
    if not query:
        if sys.stdin.isatty() and not args.json:
            query = ui.prompt("Search term or pattern")
            if not query:
                ui.warn("Search query cannot be empty.")
                return 1
        else:
            ui.error("Search query is required. See `searchlight --help`.")
            return 1

    viewer_cmd = args.viewer or None

    try:
        result = search_pdfs(
            query=query,
            target=target_path,
            ignore_case=args.ignore_case,
            recursive=args.recursive,
            max_count=args.max_count,
            context=args.context,
            page=args.page,
        )
    except Exception as exc:
        ui.error(f"Search failed: {exc}")
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.matches else 1

    if not result.matches:
        ui.warn(
            f"No matches found for {ui.bold(repr(query))} across {result.files_scanned} PDF document(s)."
        )
        return 1

    # In dry-run mode or non-interactive terminal, print matches cleanly
    if args.dry_run or not sys.stdin.isatty():
        for m in result.matches:
            page_str = f":p.{m.page}" if m.page is not None else ""
            print(f"{ui.cyan(m.display_path)}{ui.bold_green(page_str)}: {m.text}")
        ui.info(
            f"Found {ui.bold(str(result.total_matches))} match(es) across {len(result.matching_files)} document(s) in {result.elapsed_sec:.2f}s."
        )
        return 0

    # Interactive picker mode
    detected_v = detect_viewer(viewer_cmd)
    panel_lines = [
        f"{ui.bold('Query:')}        {ui.bold_yellow(repr(query))}",
        f"{ui.bold('Target:')}       {ui.cyan(str(target_path))} ({result.files_scanned} PDFs scanned)",
        f"{ui.bold('Matches:')}      {ui.bold_green(str(result.total_matches))} in {len(result.matching_files)} document(s)",
        f"{ui.bold('Viewer:')}       {ui.bold_cyan(detected_v)}",
    ]
    ui.panel("SEARCHLIGHT PDF DISCOVERY", panel_lines)

    selected = select_match(
        result.matches,
        prefer_fzf=args.use_fzf,
        prompt="PDF Match ❯ ",
    )

    if not selected:
        ui.info("No selection made. Exiting.")
        return 0

    page_hint = f" at page {selected.page}" if selected.page else ""
    ui.success(f"Selected {ui.bold(selected.display_path)}{page_hint}")

    if args.open_viewer:
        ui.info(f"Opening with {ui.bold(detected_v)}...")
        opened = open_pdf(selected.file, page=selected.page, viewer=viewer_cmd)
        if not opened:
            ui.error(f"Failed to launch viewer '{detected_v}'.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
