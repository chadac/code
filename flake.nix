{
  description = "An example NixOS configuration";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: {
    overlay = import ./overlay.nix;
    homeModule = import ./home-module.nix;
  } // flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { inherit system; };
      inherit (builtins) map listToAttrs;
      inherit (pkgs) lib;
      pyVers = map (v: "python${v}") [ "38" "39" "310" "311" ];
      pyPreferred = lib.last pyVers;
      codePkgs = listToAttrs (map (pyVer: {
        name = "code-cli-${pyVer}";
        value = pkgs.callPackage ./code-cli {
          python3 = pkgs.${pyPreferred};
        };
      }) pyVers);
      code-cli = codePkgs."code-cli-${pyPreferred}";
    in {
      packages = codePkgs // {
        default = codePkgs."code-cli-${pyPreferred}";
      };
      devShells.default = pkgs.callPackage ./code-cli/shell.nix {
        inherit code-cli;
      };
    }
  );
}
