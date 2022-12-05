{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, flake-utils, nixpkgs, poetry2nix, gitignore }:
    let
      inherit (nixpkgs) lib;
      inherit (gitignore.lib) gitignoreSource;
      # Replace cleanSource with gitignoreSource
      gitignoreOverlay = self: super: {
        lib = super.lib // {
          cleanSource = gitignoreSource;
        };
      };
      # Supported Python versions
      pyVersions = map (v: "python${v}") ["38" "39" "310" "311"];
      # Preferred Python version
      pyPreferred = "python311";
    in
      flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ poetry2nix.overlay gitignoreOverlay ];
          };
          codePackages = lib.listToAttrs (map (pyVer:
            lib.nameValuePair "code-${pyVer}" (pkgs.callPackage ./default.nix {
              pyVer = pkgs.${pyVer};
              test = true;
              lintCheck = true;
              typeCheck = true;
            })
          ) pyVersions);
          codeApps = lib.listToAttrs (map (pyVer:
            lib.nameValuePair "code-${pyVer}" (flake-utils.lib.mkApp {
              drv = codePackages."code-${pyVer}";
            })
          ) pyVersions);
        in
        rec {
          packages = codePackages // {
            default = codePackages."code-${pyPreferred}";
          };
          apps = codeApps // {
            code = apps."code-${pyPreferred}";
            default = apps.code;
          };
          devShells.default = pkgs.mkShell {
            buildInputs = [
              (pkgs.callPackage ./app.nix {
                pyVer = pkgs.${pyPreferred};
                test = true;
                editable = true;
                lintCheck = true;
                typeCheck = true;
              })
            ];
          };
        }
      );
}
