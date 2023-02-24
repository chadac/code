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
* Share local dev files (such as `.envrc`, `flake.nix`,
  `shell.nix`) across machines without needing to explicitly track them
  within your projects.

## Usage

### Home-Manager service

The HM service manages generating a config file and regularly updating
your repositories to track the latest version of each remote.

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
  imports = [ code.homeModule ];

  services.code = {
    # If true, runs the code refreshing service
    enable = true;

    # Root directory for hosting all code repositories. Default is $HOME.
    root = "${config.home.homeDirectory}/code";

    # Interval to update repositories with their upstream.
    interval = "hourly";

    # Your list of repositories
    repositories = {
      "github.com/chadac/dotfiles" = {
        # You can specify all remotes you will track here.
        remotes = [{
          # The name of the remote. Default is 'origin'.
          name = "origin";
          # The remote URL
          url = "git@github.com:chadac/dotfiles";
          # If specified, will auto-fetch changes for this branch regularly
          branch = "nix-config";
        }];
      };

      "github.com/NixOS/nixpkgs" = {
        remotes = [
          { name = "publish"; url = "git@github.com:NixOS/nixpkgs.git";
            branch = "master"; }
          { name = "origin"; url = "git@github.com:chadac/nixpkgs.git"; }
        ];
      };
    };

    # Any "dev" files that don't belong in these repositories but you would
    # like to share between your machines can be tracked via a separate repo.
    devFiles = {
      # Required: "." signifies the default repository to track local files.
      "." = {
        url = "git@github.com:chadac/devfiles";
        branch = "main";
      };

      # Optional: You can track subdirectories with different repositories.
      # Any dev files in $HOME/code/private are stored in an alternative repo.
      "private" = {
        url = "git@github.com:chadac/devfiles-private";
        branch = "main";
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

## Code CLI

Once installed via home-manager, you can use the `code` CLI utility to
manage your repositories and local files:

To update all of your repositories:

    code sync

Besides the `sync` command, the `code` utility is an alias for the
`git` command for dev files. So, suppose you create a project:

    cd code/github.com/NixOS/nixpkgs
    vi .envrc
    # ... make changes ...

You can track the local copy of `.envrc` with:

    code add .envrc

The rest works just like a regular Git alias:

    code commit -m "Add NixOS/nixpkgs/envrc"
    code push

Most of what `code` does is based on the [bare Git repository method
for silently storing
files](https://www.atlassian.com/git/tutorials/dotfiles) by durdn@.
