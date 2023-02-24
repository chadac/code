"""code-cli: Manage consistent copies of your local code repositories.

This is a lightweight tool that helps sync Git repositories between
many machines. It's effectively a wrapper to run some Git commands.
"""
from __future__ import annotations

from dataclasses import dataclass
import textwrap
from pathlib import Path
import sys

from code_cli import git
from code_cli.code import Code
from code_cli.config_file import Config


def print_help() -> None:
    print(
        textwrap.dedent(
            """\
    usage: code <command> [<args>]

    If <command> is a general Git command, it runs Git for your dev files.

    Sync commands:
      sync     Pulls changes from all Git repositories tracked by code.

    Utility commands:
      path         Print the path to the local file repository.
    """.strip(
                "\n"
            )
        )
    )


def do_sync(code: Code, args: list[str]) -> None:
    """
    Update remotes for all Git repositories.

    Does the following:
    1. Create any Git repositories that have not existed yet.
    2. Fetch all changes from upstream remotes.
    3. Update any branches that are tracked to be updated.
    """
    failed = False
    for repository in code.repositories:
        try:
            repository.sync_git()
        except Exception as e:
            # TODO: Make this nicer!
            print(f"{repository}: sync failed: {e}", file=sys.stderr)
            failed = True
    for dev_repo in code.dev_repos:
        try:
            dev_repo.create()
        except Exception as e:
            print(f"{dev_repo}: create failed: {e}", file=sys.stderr)
            failed = True
    if failed:
        exit(1)


def do_path(code: Code, args: list[str]) -> None:
    """
    Print the path of the directory storing the local Git repository.
    """
    remote = config.get_local_repo()
    remote.create()
    print(str(remote.path))


def do_git(code: Code, args: list[str]) -> None:
    """
    Runs Git command with args to use the local file repository instead.
    """
    remote = code.get_devfiles_repo()
    remote.ensure()
    remote.run_git(args, shell=True)


def main() -> None:
    global config

    args = sys.argv[1:]
    if len(args) == 0 or args[0] == "--help":
        print_help()
        exit(0)

    code = Code.init()

    if args[0] == "sync":
        do_sync(args[1:])
    elif args[0] == "path":
        do_path(args[1:])
    else:
        do_git(args)
