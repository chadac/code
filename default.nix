{ config, lib, pkgs }:

let
  inherit (lib) mkOption types mapAttrsToList;
  inherit (builtins) concatStringsSep;
  code = pkgs.callPackage ./code-cli {};
  cfg = config.services.gitRepositories;
in {
  options = {
    services.gitRepositories = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = ''
          Whether to enable the code configuration and Git cloning service.
        '';
      };
      root = mkOption {
        type = types.str;
        default = "${config.home.homeDirectory}/code";
        description = ''
          Root directory hosting Git repositories.
        '';
      };
      interval = mkOption {
        type = types.str;
        default = "hourly";
        description = ''
          Update the main branch on each repository at this interval.
        '';
      };
      repositories = types.attrsOf (types.submodule {
        options = {
          remote = mkOption {
            type = types.str;
            default = "origin";
            description = "Name for the remote repository.";
          };
          url = mkOption {
            type = types.str;
            description = "URL of the remote.";
          };
          branch = mkOption {
            type = types.str;
            description = "Tracking branch to update.";
          };
        };
      });
    };
  };

  config = {
    systemd.user.services.update-git-repositories = {
      description = "Update local Git repositories.";
      path = [ code ];
      script = builtins.concatStringsSep "\n" (mapAttrsToList (path: repo: ''
        ${code}/bin/code \
          --path '${cfg.root}/${path}' \
          --name '${repo.remote}' \
          --url '${repo.name}' \
          --branch '${repo.branch}'
      '') cfg.repositories);
    };
  };
}
