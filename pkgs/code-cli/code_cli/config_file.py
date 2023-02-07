from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
import json
import hashlib
from pathlib import Path

from code_cli import git


CONFIG_PATH = Path.home() / ".config" / "code-cli" / "config.json"
SHARE_PATH = Path.home() / ".local" / "share" / "code-cli" / "repos"


@dataclass(frozen=True)
class LocalRepository:
    url: str
    branch: str | None
    root: Path

    @cached_property
    def path(self) -> Path:
        return SHARE_PATH / self.id

    @cached_property
    def id(self) -> str:
        h = hashlib.sha256()
        h.update(self.url.encode())
        h.update(str(self.root).encode())
        if self.branch:
            h.update(self.branch.encode())
        return h.hexdigest()

    @cached_property
    def _git_args(self) -> list[str]:
        return [
            f"--git-dir={str(self.path)}",
            f"--work-tree={str(self.root)}",
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
        files = self.check_git(
            ["ls-tree", "--full-tree", "--name-only", "-r", "HEAD"]
        )
        return [Path(f) for f in files.split("\n")]

    def exists(self) -> bool:
        return self.path.exists()

    def _clone(self) -> None:
        git.run(["clone", "--bare", self.url, str(self.path)])
        if self.branch is not None:
            self.run_git(["checkout", self.branch])
        else:
            self.run_git(["checkout"])

    def _init(self) -> None:
        git.run(["init", "--bare", str(self.path)])
        self.run_git(["remote", "set-url", "origin", self.url])
        if self.branch is not None:
            self.run_git(["checkout", "-b", self.branch])

    def _config(self) -> None:
        git.run(["config", "--local", "status.showUntrackedFiles", "no"],
                cwd=self.path)

    def create(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.exists():
            try:
                self._clone()
            except git.GitError:
                self._init()
            self._config()

    def pull(self) -> None:
        self.run_git(["pull"])


@dataclass(frozen=True)
class RepositoryRemote:
    name: str
    url: str
    branch: str | None

    def ensure(self) -> None:
        """
        Update the remote so that it uses proper configs.
        """
        git.run(["remote", "set-url", self.name, self.url])

    def sync_git(self, repo: Repository) -> None:
        """
        Ensure the remote is set up and fetch latest remote branch.
        """
        self.ensure()
        if self.branch is not None:
            git.run(
                ["fetch", self.name, f"{self.branch}:{self.branch}"],
                cwd=repo.path,
            )


@dataclass(frozen=True)
class Repository:
    path: Path
    local_repo: LocalRepository | None
    remotes: list[RepositoryRemote]

    def sync_git(self) -> None:
        """
        Update all remotes.
        """
        for remote in self.remotes:
            remote.sync_git(self)


@dataclass(frozen=True)
class Config:
    enable: bool
    root: Path
    default_local_repo: LocalRepository | None
    repositories: list[Repository]

    @cached_property
    def root_dir(self) -> Path:
        return Path(self.root)

    @cached_property
    def local_repos(self) -> list[LocalRepository]:
        local_repos = (
            [self.default_local_repo] if self.default_local_repo is not None
             else []
        ) + [repo.local_repo for repo in self.repositories
             if repo.local_repo is not None]
        return list(set(local_repos))


    def get_repo(self, cwd: Path | None = None) -> Repository:
        cwd_ = cwd or Path.cwd()
        for repo in self.repositories:
            if cwd_.is_relative_to(repo.path):
                return repo
        raise RuntimeError(
            f"No configured Git repository discovered in the directory: {cwd_}")

    def get_local_repo(self, cwd: Path | None = None) -> LocalRepository:
        cwd_ = cwd or Path.cwd()
        local_repo = (
            self.get_repo(cwd=cwd_).local_repo or self.default_local_repo
        )
        if local_repo is None:
            raise RuntimeError(
                f"No local repository configured for the given project: {local_repo}")
        return local_repo


def _load_local_repo(content: dict | None, root: Path) -> LocalRepository | None:
    if content is None:
        return None
    else:
        return LocalRepository(
            url=content["url"],
            branch=content["branch"],
            root=root,
        )


def _load_repo_remote(content: dict) -> RepositoryRemote:
    return RepositoryRemote(
        name=content["name"],
        url=content["url"],
        branch=content["branch"],
    )


def _load_repo(path: str, content: dict, root: Path) -> Repository:
    return Repository(
        path=root / path,
        local_repo=_load_local_repo(content["localRepository"], root),
        remotes=[_load_repo_remote(raw_remote) for raw_remote in content["remotes"]],
    )


def load(path: Path | None = None) -> Config:
    path_ = path or CONFIG_PATH
    with open(path_, "r") as f:
        raw = json.load(f)
    root = Path(raw["root"])
    return Config(
        enable=raw["enable"],
        root=root,
        default_local_repo=_load_local_repo(raw["defaultLocalRepository"], root),
        repositories=[_load_repo(path, raw_repo, root) for path, raw_repo in raw["repositories"].items()],
    )
