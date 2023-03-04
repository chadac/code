from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from code_cli import git
from code_cli.config import CodeRepoConfig


@dataclass(frozen=True)
class CodeRepoRemote:
    name: str
    url: str
    branch: str | None
    path: Path

    @property
    def clone_args(self) -> list[str]:
        """Arguments passed to git when cloning from this remote."""
        args = ["--single-branch", "-o", self.name]
        if self.branch is not None:
            args += ["-b", self.branch]
        args += [self.url]
        return args

    def _ensure(self) -> None:
        """Update the remote with proper configurations."""
        git.run(["remote", "set-url", self.name, self.url], cwd=self.path)

    def sync(self) -> None:
        self._ensure()
        if self.branch is not None:
            git.run(
                ["fetch", self.name, f"{self.branch}:{self.branch}"],
                cwd=self.path
            )


@dataclass(frozen=True)
class CodeRepo:
    path: Path
    remotes: list[CodeRepoRemote]

    @classmethod
    def init(cls, path: Path, config: CodeRepoConfig) -> CodeRepo:
        return cls(
            path=path,
            remotes=[CodeRepoRemote(r.name, r.url, r.branch, path)
                     for r in config.remotes]
        )

    def _create(self) -> None:
        cmd = ["clone"] + self.remotes[0].clone_args + [str(self.path)]
        git.run(cmd)

    def sync(self) -> None:
        if not (self.path / ".git").exists():
            self._create()

        for remote in self.remotes:
            remote.sync()
