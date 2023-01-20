"""code-cli: Manage consistent copies of your local code repositories.

This is a lightweight tool that helps sync Git repositories between
many machines. It's effectively a wrapper to run some Git commands.
"""
from __future__ import annotations

from dataclasses import dataclass
import textwrap
from pathlib import Path
import sys

from code_cli import git, config_file
from code_cli.config_file import Config


config: Config = None  # type: ignore


def print_help() -> None:
    print(textwrap.dedent("""\
    usage: code <command> [<args>]
    
    If <command> is a general Git command, it runs Git for your local files.
    
    Sync commands:
      sync-git     Pulls changes from all Git repositories tracked by code.
      sync-files   Pulls updates to local files.
    
    Utility commands:
      path         Print the path to the local file repository.
    """.strip("\n")))


def do_sync_git(args: list[str]) -> None:
    """
    Update remotes for all Git repositories.

    Does the following:
    1. Create any Git repositories that have not existed yet.
    2. Fetch all changes from upstream remotes.
    3. Update any branches that are tracked to be updated.
    """
    failed = False
    for repository in config.repositories:
        try:
            repository.sync_git()
        except Exception as e:
            print(f"{repository}: sync failed: {e}", file=sys.stderr)
            failed = True
    if failed:
        exit(1)


def do_sync_local(args: list[str]) -> None:
    """
    Pulls down any new files or changes to existing local files.
    """
    for remote in config.local_repos:
        remote.create()
        try:
            remote.pull()
        except git.GitError as e:
            print(f"{remote}: git pull failed: {e}", file=sys.stderr)
            raise e


def do_path(args: list[str]) -> None:
    """
    Print the path of the directory storing the local Git repository.
    """
    remote = config.get_local_repo()
    remote.create()
    print(str(remote.path))


def do_git(args: list[str]) -> None:
    """
    Runs Git command with args to use the local file repository instead.
    """
    remote = config.get_local_repo()
    remote.create()
    remote.run_git(args, shell=True)


def main() -> None:
    global config

    args = sys.argv[1:]
    if len(args) == 0 or args[0] == "--help":
        print_help()
        exit(0)

    config = config_file.load()

    if args[0] == "sync-git":
        do_sync_git(args[1:])
    elif args[0] == "sync-files":
        do_sync_local(args[1:])
    elif args[0] == "path":
        do_path(args[1:])
    else:
        do_git(args)
