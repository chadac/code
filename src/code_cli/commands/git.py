from __future__ import annotations

from cleo.commands.base_command import BaseCommand
from cleo.io.io import IO


class GitCommand(BaseCommand):
    name: str = "git"
    aliases: list[str] = [
        "add",
        "mv",
        "restore",
        "rm",
        "bisect",
        "diff",
        "grep",
        "log",
        "show",
        "status",
        "branch",
        "commit",
        "merge",
        "rebase",
        "reset",
        "switch",
        "tag",
        "fetch",
        "pull",
        "push",
    ]
    description: str = "Alias for the Git command."

    def run(self, io: IO) -> int:
        raise RuntimeError("If you're seeing this, you've set up code-cli incorrectly.")
