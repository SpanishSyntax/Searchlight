<p align="center">
  <img src="assets/banner.png" alt="High-powered marine searchlight illuminating arctic waters from a ship deck" width="100%" />
</p>

# Searchlight 🔦

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

> Interactive full-text PDF search, fuzzy discovery, and direct page-jumping document viewer integration.

Searchlight is a keyboard-driven document exploration engine designed for technical papers, lecture notes, and research archives. Built upon `pdfgrep`, `poppler-utils`, and `prism`, Searchlight performs full-text regex querying, provides an interactive fuzzy picker, and launches external document viewers directly at the matching page.

---

## Why "Searchlight"? (The Lore)

> **searchlight** (`/ˈsɜːtʃ.laɪt/`) — *noun:* A powerful, high-intensity projector that casts a narrow, penetrating beam across polar blizzards and fog banks to locate distant landmarks and lost waypoints.

When navigators are caught in an arctic blizzard, ordinary vision fails. Dense blowing snow and zero-visibility whiteouts obscure every reference point. Only a focused, high-candela beam can pierce the storm to illuminate the harbor beacon or cabin marker miles ahead.

Research and documentation collections present an equivalent blizzard: hundreds of multi-page technical PDFs, proofs, and references where critical formulas and definitions are buried.

**Searchlight cuts through dense document archives:**

- **Blizzard Penetration**: Employs fast regex and full-text discovery to scan technical papers and textbook collections without pre-indexing delays.
- **Direct Navigation**: Launches document viewers directly positioned at the exact page number matching your query, eliminating manual table-of-contents scrolling.

---

## Architecture at a Glance

Searchlight is structured into modular layers:

1. **Search Engine Core (`searchlight.engine`)**: Dual-engine search pipeline leveraging `pdfgrep` with automatic fallback to `poppler-utils` (`pdftotext`).
2. **Interactive Navigation (`searchlight.interactive`)**: Fast terminal fuzzy picker utilizing `fzf` with an embedded fallback to native `prism` components.
3. **Viewer Dispatcher (`searchlight.viewer`)**: Auto-detection and argument translation for modern PDF viewers (`zathura`, `sioyek`, `okular`, `evince`, `xdg-open`).
4. **Model Context Protocol (`searchlight.mcp`)**: Native stdio MCP server exposing PDF search, metadata extraction, text extraction, and viewer launching to AI assistants.
5. **CLI Router (`searchlight.cli`)**: Command parsing, configuration loading, dry-run previews, and structured JSON output.

---

## Documentation Navigation

- [Installation & Quick Start](getting-started.md): How to install Searchlight via Nix, Home Manager, or pip, and common examples.
- [Architecture & Design Philosophy](architecture.md): Search backends, regex parsing, viewer detection logic, and MCP architecture.
- [CLI Reference & Command Guide](usage.md): Full flag specifications, structured output modes, MCP tool schemas, and practical recipes.
- [Configuration & Advanced Options](configuration.md): Declarative configuration via `searchlight.toml`, Home Manager setup, and AI tool configurations.
