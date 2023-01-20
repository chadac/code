# code

## NOTE: STILL A WIP! Not really usable yet. Gotta get tests to pass...

A Home Manager module for managing your Git repositories. I name it
after my `code` folder because that definitely won't lead to
confusion. It's sort of like the dev machine-friendly version of
[git-sync](https://github.com/kubernetes/git-sync).

The tool takes care of a couple of things for you:

* Set up consistent Git clones and remote names between your machines.
* Regularly update key branches on your core repositories so that you
  don't need to regularly `git fetch` the main branches for rebasing.
* Share untracked local files (such as `.envrc`, `flake.nix`,
  `shell.nix`) into projects so that you don't have to manually clone
  them.

I also built this specifically thinking of use cases where you may
want to have only subsets of packages imported on a per-machine
basis. It's not explicitly available, but with some Nix hacking, this
is easily doable.

## Usage

Import this code to your `flake.nix`:

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  flake-utils.url = "github:numtide/flake-utils";
  code = {
    url = 'github:chadac/code';
    inputs.nixpkgs.follows = "nixpkgs";
    inputs.flake-utils.follows = "flake-utils";
  };
};
```

Then, update your `home.nix` (or what have you) with the appropriate
imports:

```nix
{ config, code, ... }:
{
  ...
  imports = [ code.homeModules.code ];

  services.code = {
    # If true, runs the code refreshing service
    enable = true;

    # Root directory for hosting all code repositories. Default is $HOME.
    root = "${config.home.homeDirectory}/code";

    # Can be any type of cron schedule. Default is hourly.
    interval = "hourly";

    # Your list of repositories
    repositories = {
      "github.com/chadac/dotfiles" = [
        # You can specify all remotes you will track here.
        remotes = [{
          # The name of the remote. Default is 'origin'.
          remote = "origin";
          # The remote URL
          url = "git@github.com:chadac/dotfiles";
          # If specified, will auto-fetch changes for this branch regularly
          branch = "nix-config";
        }];
      ];

      "github.com/NixOS/nixpkgs" = {
        remotes = [
          { remote = "publish"; url = "git@github.com:NixOS/nixpkgs.git";
            branch = "master"; }
          { remote = "origin"; url = "git@github.com:chadac/nixpkgs.git"; }
        ];
      };
    };
  };
}
```

This will create the following directory structure:

    $HOME/
      code/
        github.com/
          chadac/
            dotfiles/
              .git
              ..
          NixOS/
            nixpkgs/
              .git
              ..
