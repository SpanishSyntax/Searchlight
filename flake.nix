{
  description = "Searchlight - Interactive Full-Text PDF Search, Fuzzy Discovery & Preview Engine";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    prism = {
      url = "github:SpanishSyntax/Prism";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    prism,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [prism.overlays.default];
      };
      lib = pkgs.lib;

      searchlightPackage = pkgs.python3Packages.buildPythonApplication {
        pname = "searchlight";
        version = "0.1.0";
        src = lib.cleanSource ./.;
        pyproject = true;

        build-system = [
          pkgs.python3Packages.setuptools
        ];

        nativeBuildInputs = [
          pkgs.makeWrapper
        ];

        propagatedBuildInputs = [
          pkgs.python3Packages.prism
        ];

        postFixup = ''
          for prog in $out/bin/*; do
            wrapProgram "$prog" \
              --prefix PATH : ${lib.makeBinPath [
              pkgs.pdfgrep
              pkgs.fzf
              pkgs.xdg-utils
              pkgs.poppler-utils
            ]}
          done
        '';

        nativeCheckInputs = [
          pkgs.python3Packages.pytest
          pkgs.pdfgrep
          pkgs.fzf
          pkgs.xdg-utils
          pkgs.poppler-utils
        ];

        checkPhase = ''
          runHook preCheck
          pytest
          runHook postCheck
        '';

        doCheck = true;

        meta = with lib; {
          description = "Interactive full-text PDF search, fuzzy discovery, and document preview engine";
          homepage = "https://github.com/SpanishSyntax/Searchlight";
          license = licenses.mit;
          mainProgram = "searchlight";
        };
      };
    in {
      packages = {
        default = searchlightPackage;
        searchlight = searchlightPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${searchlightPackage}/bin/searchlight";
        };
        searchlight = {
          type = "app";
          program = "${searchlightPackage}/bin/searchlight";
        };
        mcp = {
          type = "app";
          program = "${searchlightPackage}/bin/searchlight-mcp";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          (python3.withPackages (ps: [
            ps.setuptools
            ps.pytest
            ps.prism
          ]))
          pdfgrep
          fzf
          xdg-utils
          poppler-utils
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          searchlight = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        searchlight = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.searchlight;
        searchlight = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.searchlight;
          system = pkgs.stdenv.hostPlatform.system;
        in {
          options.programs.searchlight = {
            enable = lib.mkEnableOption "Searchlight - Interactive full-text PDF search engine";
            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${system}.default;
              description = "The Searchlight package to install system-wide.";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.searchlight;
        searchlight = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.searchlight;
          tomlFormat = pkgs.formats.toml {};
          system = pkgs.stdenv.hostPlatform.system;
          defaultSearchlight = self.packages.${system}.default;
        in {
          options.programs.searchlight = {
            enable = lib.mkEnableOption "Searchlight - Interactive full-text PDF search engine";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultSearchlight;
              description = "The Searchlight package to use.";
            };

            settings = lib.mkOption {
              type = tomlFormat.type;
              default = {};
              description = "Configuration written to ~/.config/searchlight/searchlight.toml.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];

            xdg.configFile."searchlight/searchlight.toml" = lib.mkIf (cfg.settings != {}) {
              source = tomlFormat.generate "searchlight.toml" cfg.settings;
            };
          };
        };
      };
    };
}
