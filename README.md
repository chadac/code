# code

Dotfiles for your Git repositories.

When managing Git-based projects, there may be some internal stuff
you'd like to keep version-controlled on your machine but don't
necessarily belong to the given project (such as Nix flakes). Code
manages this by tracking your files in a separate Git repository.

It also enables seamlessly breaking up your config into multiple
repositories. This is important for scenarios where you need some of
your project configuration to be private, or potentially distributed
across version control platforms (when you need special configurations
for your company work, for example).

Internally, `code` is fairly simple. It's mainly an alias for the
`git` command, with some modifications mainly motivated by [@durdn's
excellent article on how to manage
dotfiles](https://www.atlassian.com/git/tutorials/dotfiles) with some
additional support for multiple repositories.

## Install

`code` can be installed via [pipx](https://pypa.github.io/pipx/) using:

    pipx install git+ssh://github.com/chadac/code

## Usage



    code init --repo ssh://github.com/.../my-code.git

### The `.code.yaml` file

`code` pulls its configuration information from a local `.code.yml`
file. It manages the default Git repo that is used to track local
files, and manages the configuration of Git directories.

    profile: my-code
    git:
      # The default branch used with `code init`
      default-branch:
        name: main
        tracking: publish/main
      remotes:
        - name: publish
          url: ssh://git@github.com/owner/repo.git
        - name: origin
          url: ssh://git@github.com/chadac/repo.git

This file will be implicitly ignored in your Git repository, so no
need to manually track it.
