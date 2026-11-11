# CLI Reference & Command Guide

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Command Overview

```text
Usage: searchlight <query> [path] [options]
       searchlight mcp
       searchlight [options]
```

| Invocation | Description |
| :--- | :--- |
| `searchlight <query>` | Interactive search across current directory and subdirectories. |
| `searchlight <query> <path>` | Interactive search targeting a specific directory or individual PDF file. |
| `searchlight mcp` | Launch standard I/O Model Context Protocol (MCP) server. |

---

## Search Query Syntax

Searchlight accepts plain text queries or full regular expressions supported by standard regex syntax:

- Plain phrase: `searchlight "gradient descent"`
- Exact match: `searchlight "Theorem 4\.2"`
- Alternation: `searchlight "Lyapunov|Hamiltonian"`
- Boundary match: `searchlight "\bLQR\b"`

By default, queries are case-insensitive. Pass `-s` or `--case-sensitive` for exact casing matches.

---

## Options and Flags

| Flag | Long Option | Description | Default |
| :--- | :--- | :--- | :--- |
| `-d` | `--dir DIR` | Target directory or PDF file to scan. | Current directory (`.`) |
| `-r` | `--recursive` | Recursively scan subdirectories for PDF files. | `true` |
| | `--no-recursive` | Scan only the immediate target directory. | `false` |
| `-i` | `--ignore-case` | Case-insensitive pattern matching. | `true` |
| `-s` | `--case-sensitive` | Case-sensitive pattern matching. | `false` |
| `-C` | `--context NUM` | Number of context lines before and after match. | `0` |
| `-m` | `--max-count NUM` | Maximum matches per PDF document. | `50` |
| `-p` | `--page NUM` | Search only a specific page number. | `None` |
| | `--viewer CMD` | Custom PDF viewer executable (`zathura`, `sioyek`, `okular`). | Auto-detected |
| | `--fzf` | Use `fzf` for interactive match picking. | `true` |
| | `--no-fzf` | Use native Prism searchbox instead of `fzf`. | `false` |
| `-o` | `--open` | Open document viewer on match selection. | `true` |
| | `--no-open` | Do not launch viewer after selection. | `false` |
| `-n` | `--dry-run` | Print matches to stdout and exit without launching picker. | `false` |
| | `--json` | Output search results in structured JSON format. | `false` |
| | `--toon` | Output results in Token-Oriented Object Notation (TOON). | `false` |
| `-A` | `--agent` | Compact machine-friendly output mode. | `false` |
| | `--color MODE` | Terminal color mode: `auto`, `always`, or `never`. | `auto` |
| | `--no-color` | Disable colored output. | `false` |
| `-h` | `--help` | Show help message and exit. | - |
| `-V` | `--version` | Show version information and exit. | - |

---

## Structured Output Modes

### JSON Output (`--json`)

```bash
searchlight "convergence" --json
```

Output schema:

```json
{
  "query": "convergence",
  "target": "/home/user/papers",
  "total_matches": 3,
  "matching_files": [
    "/home/user/papers/optimization.pdf"
  ],
  "files_scanned": 12,
  "elapsed_sec": 0.042,
  "matches": [
    {
      "file": "/home/user/papers/optimization.pdf",
      "display_path": "optimization.pdf",
      "page": 14,
      "line_number": 28,
      "text": "guarantees asymptotic convergence of the sequence",
      "context_before": [],
      "context_after": []
    }
  ]
}
```

### Dry-Run Output (`-n`)

```bash
searchlight "Schrodinger" -n
```

Prints clean, human-readable terminal lines with file paths, page indices, and matching text snippets without launching any viewer or interactive picker.

---

## MCP Tools Reference

When running in MCP mode (`searchlight mcp`), the following tools are exposed over stdio:

### 1. `searchlight_search`
- **Arguments**: `query` (str), `path` (str, optional), `recursive` (bool, optional), `case_sensitive` (bool, optional), `page` (int, optional), `max_count` (int, optional).
- **Returns**: Formatted list of matches with file paths, page numbers, and matching text.

### 2. `searchlight_info`
- **Arguments**: `file_path` (str).
- **Returns**: PDF metadata (page count, title, author, creation date, PDF version).

### 3. `searchlight_extract_text`
- **Arguments**: `file_path` (str), `first_page` (int, optional), `last_page` (int, optional).
- **Returns**: Plain text extracted from the requested page range.

### 4. `searchlight_open_viewer`
- **Arguments**: `file_path` (str), `page` (int, optional), `viewer` (str, optional).
- **Returns**: Success status and launch confirmation.

---

## Practical Recipes

### Recipe 1: Find a Proof in a Long Book

```bash
searchlight "Proof of Theorem 5.1" textbook.pdf
```

### Recipe 2: Search with Surrounding Context

```bash
searchlight "saddle point" -C 3 ./lecture_notes/
```

### Recipe 3: Pipe Search Results to Ripgrep or Fzf

```bash
searchlight "eigenvalue" -n | grep -i "multiplicity"
```
