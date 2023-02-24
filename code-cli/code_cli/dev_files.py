from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from functools import cached_property
import hashlib

from code_cli import git
from code_cli import constants


@dataclass(frozen=True)
class DevFilesRepo:
    url: str
    branch: str | None
    root: Path

    @cached_property
    def id(self) -> str:
        h = hashlib.sha256()
        h.update(self.url.encode())
        h.update(str(self.root).encode())
        if self.branch is not None:
            h.update(self.branch.encode())
        return h.hexdigest()

    @cached_property
    def path(self) -> Path:
        return constants.SHARE_PATH / self.id

    @cached_property
    def _git_args(self) -> list[str]:
        return [
            f"--git-dir='{self.path}'",
            f"--work-tree='{self.root}'",
        ]

    def run_git(self, args: str | list[str], **kwargs) -> None:
        new_args: str | list[str]
        if isinstance(args, str):
            new_args = " ".join(self._git_args + [args])
        else:
            new_args = self._git_args + args
        git.run(
            new_args,
            **kwargs,
        )

    def check_git(self, args: str | list[str], **kwargs) -> str:
        new_args: str | list[str]
        if isinstance(args, str):
            new_args = " ".join(self._git_args + [args])
        else:
            new_args = self._git_args + args
        return git.check(
            new_args,
            **kwargs,
        )

    def get_files(self) -> list[Path]:
        files = self.check_git(["ls-tree", "--full-tree", "--name-only", "-r", "HEAD"])
        return [Path(f) for f in files.split("\n")]

    def exists(self) -> bool:
        return self.path.exists()

    def _clone(self) -> None:
        git.run(["clone", "--bare", self.url, str(self.path)])
        if self.branch is not None:
            self.run_git(["checkout", self.branch])
        else:
            self.run_git(["checkout"])

    def _bare_init(self) -> None:
        git.run(["init", "--bare", str(self.path)])
        self.run_git(["remote", "set-url", "origin", self.url])
        if self.branch is not None:
            self.run_git(["checkout", "-b", self.branch])

    def _config(self) -> None:
        git.run(["config", "--local", "status.showUntrackedFiles", "no"], cwd=self.path)

    def create(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.exists():
            try:
                self._clone()
            except git.GitError:
                self._bare_init()
            self._config()
