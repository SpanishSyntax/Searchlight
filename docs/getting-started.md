# Getting Started with Searchlight

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Installation

### Running Directly via Nix (Recommended)

Run Searchlight without permanent host installation:

```bash
# Search for Hamiltonian across current folder and subdirectories
nix run github:SpanishSyntax/Searchlight -- "Hamiltonian"

# Launch MCP server directly
nix run github:SpanishSyntax/Searchlight#mcp
```

### Home Manager

Add Searchlight to your `flake.nix` inputs:

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

### NixOS System Configuration

```nix
{
  programs.searchlight.enable = true;
  programs.searchlight.package = inputs.searchlight.packages.${pkgs.system}.default;
}
```

### Installing via Pip / Uv

When installing via pip or uv, ensure system dependencies (`pdfgrep`, `fzf`, and `poppler-utils`) are available in your `$PATH`:

```bash
# Using uv
uv tool install git+https://github.com/SpanishSyntax/Searchlight.git

# Using pip
pip install git+https://github.com/SpanishSyntax/Searchlight.git
```

---

## Quick Start

### 1. Interactive Search in Current Directory

Search across all PDF documents in the current directory and subdirectories:

```bash
searchlight "Schrodinger"
```

Searchlight will scan matching documents, display an interactive fuzzy picker with highlighted matches, and launch your preferred document viewer (`zathura`, `sioyek`, etc.) opened directly to the selected page upon pressing `Enter`.

### 2. Search a Specific Directory

Target a specific papers or course archive:

```bash
searchlight "Lyapunov" ~/Documents/Papers/
```

### 3. Restrict Search to a Specific Page

Search only page 12 of all scanned PDFs:

```bash
searchlight "Theorem 4.2" -p 12
```

### 4. Non-Interactive / Dry-Run Mode

List all matching occurrences directly in your terminal without opening a picker or viewer:

```bash
searchlight "gradient descent" -n
```

### 5. Structured JSON Output

Produce machine-readable JSON for automated scripts and workflows:

```bash
searchlight "convergence" --json
```
