from __future__ import annotations

from cleo.commands.command import Command
from cleo.io.io import IO


class GitArgsCommand(Command):
    name: str = "git-args"
    description: str = "Links git to the appropriate repository."

    def run(self, io: IO) -> int:
        print("Hello!")
        return 0
