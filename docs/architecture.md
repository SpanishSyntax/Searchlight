# Architecture & Design Philosophy

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Design Philosophy

Searchlight is designed around three architectural tenets:

1. **Zero-Indexing Overhead**: Documents are queried on-demand using native C/C++ regex engines. No heavy background indexing daemon, database, or disk cache is required.
2. **Context-Aware Navigation**: A search tool should not stop at returning a filename; it must launch the reader directly to the target page and formula.
3. **Pluggable & Graceful Degradation**: If advanced tools like `pdfgrep` or `fzf` are unavailable, Searchlight seamlessly drops back to `poppler-utils` and native `prism` widgets without crashing.

---

## The Lore

> **searchlight** (`/ˈsɜːtʃ.laɪt/`) — *noun:* A powerful, high-intensity projector that casts a narrow, penetrating beam across polar blizzards and fog banks to locate distant landmarks and lost waypoints.

When navigators are caught in an arctic blizzard, ordinary vision fails. Dense blowing snow and zero-visibility whiteouts obscure every reference point. Only a focused, high-candela beam can pierce the storm to illuminate the harbor beacon or cabin marker miles ahead.

Research collections present an equivalent blizzard: hundreds of multi-page technical PDFs, proofs, and references where critical formulas and definitions are buried. Searchlight cuts through dense document archives through instant regex scanning and direct page jumping.

---

## Dual Search Engine Pipeline

Searchlight implements a prioritized execution pipeline:

```
[User Query]
     │
     ├── Primary: `pdfgrep` (High-Performance C++ Poppler Binding)
     │       ├── Options: -H -n -i -m <limit> -C <context> --page-range
     │       └── Stdout parsed into SearchMatch dataclasses
     │
     └── Fallback: `pdftotext` (poppler-utils)
             ├── Extracted page-by-page via form-feed delimiters (\x0c)
             └── Regex pattern matching executed in Python
```

### Primary Backend: `pdfgrep`

`pdfgrep` is invoked as a subprocess with:
- `-H`: Print filename for each match.
- `-n`: Prefix each matching line with page number within the document.
- `--page-range`: Confines regex matching to requested pages when `-p` is provided.

### Fallback Backend: `pdftotext`

If `pdfgrep` is absent or encounters a fatal binary error, Searchlight falls back to `pdftotext - <file>`. Output is partitioned by form-feed characters (`\x0c`), allowing precise page-number reconstruction in pure Python.

---

## Interactive Fuzzy Picker

Matches are passed to an interactive selection UI:

1. **`fzf` Engine (Preferred)**: If `fzf` is installed and standard input is a terminal, Searchlight opens a high-speed fuzzy picker with custom formatting (`<path>:<page>: <match>`), reverse layout, and real-time query filtering.
2. **Prism Searchbox (Fallback)**: If `fzf` is unavailable or disabled via `--no-fzf`, Searchlight uses Prism's lightweight curses-based terminal selector.

---

## Viewer Detection and Page Jumping

When a match is selected, Searchlight inspects installed system viewers and translates the target page into viewer-specific CLI flags:

| Viewer Executable | Page-Jumping Flag Syntax | Process Model |
| :--- | :--- | :--- |
| **`zathura`** | `zathura -P <page> <file>` | Spawned in new session (`start_new_session=True`) |
| **`sioyek`** | `sioyek --page <page> <file>` | Spawned in new session |
| **`okular`** | `okular -p <page> <file>` | Spawned in new session |
| **`evince`** | `evince -p <page> <file>` | Spawned in new session |
| **`mupdf`** | `mupdf <file> <page>` | Spawned in new session |
| **`xdg-open`** | `xdg-open <file>` | Default system association (page jumping unsupported) |

Viewers are spawned completely detached from the controlling terminal via `subprocess.Popen(..., start_new_session=True)`, allowing the terminal prompt to return immediately.

---

## Model Context Protocol Server

Searchlight provides a native Model Context Protocol (MCP) server running over standard input and output:

- Provides AI coding agents with full-text search across local research papers and documents.
- Extracts raw page text without launching graphical viewers.
- Inspects PDF metadata (page count, title, author, PDF version) via poppler's `pdfinfo`.
