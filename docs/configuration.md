# Configuration & Advanced Options

[Overview](README.md) • [Getting Started](getting-started.md) • [Architecture](architecture.md) • [CLI Reference](usage.md) • [Configuration](configuration.md)

---

## Configuration File

Searchlight optionally reads user configuration settings from `~/.config/searchlight/searchlight.toml` (or `$XDG_CONFIG_HOME/searchlight/searchlight.toml`).

### Specification (`searchlight.toml`)

```toml
[general]
# Whether to search subdirectories recursively by default
recursive = true

# Whether matching is case-insensitive by default
ignore_case = true

# Preferred document viewer executable
# Options: zathura, sioyek, okular, evince, xdg-open
viewer = "zathura"

# Use fzf for interactive match selection
use_fzf = true

# Maximum matches returned per PDF document
max_count = 50

# Number of surrounding context lines to extract
context = 0

# Terminal color mode: auto, always, or never
color = "auto"
```

Command-line flags always take precedence over values defined in `searchlight.toml`.

---

## NixOS and Home Manager

### NixOS System Module

```nix
# flake.nix or configuration.nix
{
  programs.searchlight = {
    enable = true;
    package = inputs.searchlight.packages.${pkgs.system}.default;
  };
}
```

### Home Manager Module

```nix
{
  programs.searchlight = {
    enable = true;
    settings = {
      general = {
        viewer = "sioyek";
        recursive = true;
        ignore_case = true;
        use_fzf = true;
        max_count = 100;
      };
    };
  };
}
```

---

## MCP Client Configuration

To integrate Searchlight's Model Context Protocol server with AI environments:

### Antigravity (`~/.gemini/config/mcp_config.json`)

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

### Claude Desktop (`~/.config/Claude/claude_desktop_config.json`)

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
