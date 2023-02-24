{ config, lib, pkgs }:
let
  inherit (lib) mkIf mkOption types mapAttrsToList;
  inherit (builtins) concatStringsSep;
  code = pkgs.callPackage ./code-cli {};
  cfg = config.services.code;
  homeDirectory = config.home.homeDirectory;

  devFilesRepoType = types.submodule {
    options = {
      url = mkOption {
        type = types.str;
        description = "Remote URL.";
      };
      branch = mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "Branch to use. If null, uses default.";
      };
    };
  };

  remoteType = types.submodule {
    options = {
      name = mkOption {
        type = types.str;
        default = "origin";
        description = "Name for the remote repository.";
      };
      url = mkOption {
        type = types.str;
        description = "URL of the remote.";
      };
      branch = mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "If set, this branch will track and regularly update to follow the given upstream.";
      };
    };
  };

  repositoryType = types.submodule {
    options = {
      remotes = types.listOf remoteType;
    };
  };
in
{
  options = {
    services.code = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = ''
          Whether to enable the code configuration and Git cloning service.
        '';
      };

      package = mkOption {
        type = types.package;
        default = pkgs.code-cli;
        defaultText = "pkgs.code-cli";
        description = ''
          Package to use for code-cli.
        '';
      };

      root = mkOption {
        type = types.str;
        default = "${homeDirectory}";
        description = ''
          Root directory hosting Git repositories.
        '';
      };

      interval = mkOption {
        type = types.str;
        default = "hourly";
        example = "hourly";
        description = ''
          Update the main branch on each repository at this interval.
        '';
      };

      devFiles = mkOption {
        type = types.nullOr (types.attrsOf devFilesRepoType);
        default = null;
        description = ''
          Remotes of Git repositories that will track dev files.
        '';
      };

      repositories = types.attrsOf repositoryType;
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    home.files = {
      "${homeDirectory}/.config/code-cli/config.json" =
        builtins.toJSON (builtins.removeAttrs cfg [ "package" ]);
    };

    systemd.user.services.update-code = {
      description = "Update local Git repositories.";
      script = "${pkgs.code-cli}/bin/code sync";
    };

    systemd.user.timers.update-code = {
      description = "Update timer to run code syncs.";
      partOf = [ "update-code.service" ];
      wantedBy = [ "timers.target" ];
      timerConfig.OnCalendar = cfg.interval;
    };
  };
}
