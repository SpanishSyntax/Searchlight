# 🔦 Searchlight

**Interactive Full-Text PDF Search, Fuzzy Discovery & Preview Engine**

Searchlight is a crystalline, keyboard-driven document exploration engine designed for the Frost and SpanishSyntax ecosystem. Built upon `pdfgrep` and `prism`, Searchlight scans research papers, lecture notes, and documentation archives, rendering instant fuzzy pickers and launching target PDFs directly to matching page numbers in modern document viewers.

---

## ✨ Features

- **Blazing Fast PDF Grep Engine**: Full-text regex and pattern querying across single files or deep directory trees using `pdfgrep` with graceful `poppler-utils` fallback.
- **Interactive Fuzzy Navigation**: Integrated `fzf` picker with highlighted match lines, page indices, and reverse layout; native `prism` terminal UI fallback when running in minimal shells.
- **Precision Page Jumping**: Automatically launches supported PDF viewers (`zathura`, `sioyek`, `okular`, `evince`, `xdg-open`) directly positioned at the matching page number.
- **Deep Nix Ecosystem Integration**: Native Nix flake exporting packages, apps, overlays, NixOS modules, and Home Manager modules with complete bundled runtime dependencies (`pdfgrep`, `fzf`, `xdg-utils`, `poppler-utils`).
- **Structured JSON & Scripting Modes**: `--json` and `--dry-run` flags for headless workflows, pipeline integrations, and MCP tool bridges.

---

## 🚀 Quick Start

### Run Directly with Nix

```bash
nix run github:SpanishSyntax/Searchlight -- "Hamiltonian"
```

### CLI Usage

```bash
# Interactive fuzzy search across current directory and subdirectories
searchlight "Schrodinger"

# Search within a specific folder
searchlight "Laplace" ~/Documents/Papers/

# Search only a specific page number
searchlight "Theorem 4.2" -p 12

# Case-sensitive search with surrounding context lines
searchlight "Euler-Lagrange" -s -C 2

# List all matches without opening the interactive picker (dry run)
searchlight "gradient descent" -n

# Machine-readable output for scripts and AI tooling
searchlight "convergence" --json

# Launch Model Context Protocol (MCP) Server over stdio
searchlight mcp
```

---

## 🔌 Model Context Protocol (MCP) Server

Searchlight provides a native MCP server exposing atomic PDF utilities over standard I/O (stdio). It integrates seamlessly with Antigravity, Claude Desktop, and OpenCode.

### Tools Exposed

1. **`searchlight_search`**: Full-text regex and pattern querying across PDF files with line numbers, page indexes, and context lines.
2. **`searchlight_info`**: Detailed PDF metadata extraction (title, author, total pages, paper size, encryption status, PDF version).
3. **`searchlight_extract_text`**: Plain text extraction across an entire document or specific page ranges (`first_page` to `last_page`).
4. **`searchlight_open_viewer`**: Launch local document viewer directly positioned at a specific page.

### Antigravity Configuration (`~/.gemini/config/mcp_config.json`)

```json
{
  "mcpServers": {
    "searchlight": {
      "command": "searchlight",
      "args": ["mcp"]
    }
  }
}
```

---

## ⚙️ Options & Flags

| Flag | Long Option | Description | Default |
| :--- | :--- | :--- | :--- |
| `-d` | `--dir DIR` | Target directory or PDF file to scan | Current directory |
| `-r` | `--recursive` | Recursively scan subdirectories for PDFs | `true` |
| | `--no-recursive` | Scan only the immediate target directory | `false` |
| `-i` | `--ignore-case` | Case-insensitive pattern matching | `true` |
| `-s` | `--case-sensitive` | Strict case-sensitive matching | `false` |
| `-C` | `--context NUM` | Number of context lines before/after match | `0` |
| `-m` | `--max-count NUM` | Maximum matches per PDF document | `50` |
| `-p` | `--page NUM` | Filter matches by specific page number | `None` |
| | `--viewer CMD` | Custom viewer executable (`zathura`, `sioyek`, `okular`, etc.) | Auto-detect |
| | `--fzf` / `--no-fzf` | Toggle interactive `fzf` fuzzy finder | `true` |
| `-o` | `--open` / `--no-open` | Open viewer immediately on match selection | `true` |
| `-n` | `--dry-run` | Print matches and exit without launching picker | `false` |
| | `--json` | Output structured search results in JSON | `false` |
| | `--color MODE` | Terminal color mode (`auto`, `always`, `never`) | `auto` |
| `-h` | `--help` | Display usage instructions | |
| `-V` | `--version` | Display version information | |

---

## 🛠️ Configuration

Searchlight optionally reads user preferences from `~/.config/searchlight/searchlight.toml`:

```toml
[general]
recursive = true
ignore_case = true
viewer = "zathura"
use_fzf = true
max_count = 50
context = 0
color = "auto"
```

---

## ❄️ Frost & Home Manager Integration

In your Frost or NixOS Home Manager configuration:

```nix
# flake.nix
{
  inputs = {
    searchlight.url = "github:SpanishSyntax/Searchlight";
    searchlight.inputs.nixpkgs.follows = "nixpkgs";
    searchlight.inputs.prism.follows = "prism";
  };
}

# home-manager module
{ inputs, ... }: {
  imports = [ inputs.searchlight.homeManagerModules.default ];

  programs.searchlight = {
    enable = true;
    settings = {
      viewer = "zathura";
      recursive = true;
      ignore_case = true;
    };
  };
}
```

---

## 📄 License

MIT © [SpanishSyntax](https://github.com/SpanishSyntax)
