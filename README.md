<p align="center">
  <img src="assets/banner.png" alt="High-powered marine searchlight illuminating arctic waters from a ship deck" width="100%" />
</p>

# Searchlight 🔦

Interactive full-text PDF search, fuzzy discovery, and direct page-jumping document viewer integration.

Searchlight is a fast, keyboard-driven document exploration engine designed for research papers, lecture notes, and technical documentation archives. Built on `pdfgrep`, `poppler-utils`, and `prism`, Searchlight scans PDF collections, presents interactive fuzzy pickers, and launches target documents directly to matching page numbers in modern viewers.

---

> [!TIP]
> **Documentation Site**: Detailed usage guides, complete option references, and MCP tool specifications are available on the **[Documentation Site](https://spanishsyntax.github.io/Searchlight)**.

---

## Why "Searchlight"? (The Lore)

> **searchlight** (`/ˈsɜːtʃ.laɪt/`) — *noun:* A powerful, high-intensity projector that casts a narrow, penetrating beam across polar blizzards and fog banks to locate distant landmarks and lost waypoints.

When navigators are caught in an arctic blizzard, ordinary vision fails. Dense blowing snow and zero-visibility whiteouts obscure every reference point. Only a focused, high-candela beam can pierce the storm to illuminate the harbor beacon or cabin marker miles ahead.

Research collections present an equivalent blizzard: hundreds of multi-page technical PDFs, proofs, and references where critical formulas and definitions are buried.

**Searchlight cuts through dense document archives:**

- **Blizzard Penetration**: Employs fast regex and full-text discovery to scan technical papers and textbook collections without pre-indexing delays.
- **Direct Navigation**: Launches document viewers directly positioned at the exact page number matching your query, eliminating manual table-of-contents scrolling.

---

## Features

- **Dual-Engine Search Pipeline**: High-performance regex and pattern querying using `pdfgrep` with graceful fallback to `poppler-utils` (`pdftotext`).
- **Interactive Fuzzy Navigation**: Integrated `fzf` picker with highlighted match lines, page numbers, and reverse layout; native `prism` terminal UI fallback in minimal shells.
- **Precision Page Jumping**: Automatically launches supported PDF viewers (`zathura`, `sioyek`, `okular`, `evince`, `xdg-open`) directly positioned at matching page numbers.
- **Model Context Protocol (MCP)**: Native stdio MCP server exposing PDF search, metadata extraction, text extraction, and viewer launching to AI tools.
- **Structured Output Formats**: Supports `--json`, `--toon`, and `--dry-run` modes for headless pipelines and automated scripts.
- **Declarative Nix Integration**: Nix flake exporting packages, apps, overlays, NixOS modules, and Home Manager modules with complete bundled runtime dependencies (`pdfgrep`, `fzf`, `xdg-utils`, `poppler-utils`).

---

## Quick Start

Run Searchlight directly with Nix without installing:

```bash
# Search for Hamiltonian across current folder and subdirectories
nix run github:SpanishSyntax/Searchlight -- "Hamiltonian"

# Launch MCP server directly
nix run github:SpanishSyntax/Searchlight#mcp
```

### Common CLI Invocations

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

## CLI Options & Flags

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
| | `--toon` | Output results in Token-Oriented Object Notation (TOON) | `false` |
| `-A` | `--agent` | Compact machine-friendly output mode | `false` |
| | `--color MODE` | Terminal color mode (`auto`, `always`, `never`) | `auto` |
| `-h` | `--help` | Display usage instructions | |
| `-V` | `--version` | Display version information | |

---

## Configuration

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

## Home Manager Configuration

Add Searchlight to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    searchlight = {
      url = "github:SpanishSyntax/Searchlight";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, searchlight, ... }: {
    homeConfigurations.user = home-manager.lib.homeManagerConfiguration {
      modules = [
        searchlight.homeManagerModules.default
        {
          programs.searchlight.enable = true;
          programs.searchlight.settings = {
            general = {
              viewer = "zathura";
              recursive = true;
              ignore_case = true;
            };
          };
        }
      ];
    };
  };
}
```

---

## License

MIT © SpanishSyntax
