from __future__ import annotations

from attrs import frozen
import cattrs
from dataclasses import dataclass
from functools import cached_property
import json
import hashlib
from pathlib import Path

from code_cli import git
from code_cli.constants import CONFIG_PATH


@frozen
class DevFilesRepoConfig:
    url: str
    branch: str | None


@frozen
class RemoteConfig:
    name: str
    url: str
    branch: str | None = None


@frozen
class RepoConfig:
    remotes: list[RemoteConfig]


@frozen
class Config:
    enable: bool
    package: str
    root: str
    interval: str
    devFiles: dict[str, DevFilesRepoConfig]
    repositories: dict[str, RepoConfig]

    @property
    def root_path(self) -> Path:
        return Path(self.root)

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        path_ = path or CONFIG_PATH
        with open(path_, "r") as f:
            config_raw = json.load(f)
        return cls.parse(config_raw)

    @classmethod
    def parse(cls, config_raw: dict) -> Config:
        return cattrs.structure(config_raw, cls)


# @dataclass(frozen=True)
# class RepositoryRemote:
#     name: str
#     url: str
#     branch: str | None

#     def ensure(self) -> None:
#         """
#         Update the remote so that it uses proper configs.
#         """
#         git.run(["remote", "set-url", self.name, self.url])

#     def sync_git(self, repo: Repository) -> None:
#         """
#         Ensure the remote is set up and fetch latest remote branch.
#         """
#         self.ensure()
#         if self.branch is not None:
#             git.run(
#                 ["fetch", self.name, f"{self.branch}:{self.branch}"],
#                 cwd=repo.path,
#             )


# @dataclass(frozen=True)
# class Repository:
#     path: Path
#     local_repo: LocalRepository | None
#     remotes: list[RepositoryRemote]

#     def sync_git(self) -> None:
#         """
#         Update all remotes.
#         """
#         for remote in self.remotes:
#             remote.sync_git(self)


# @dataclass(frozen=True)
# class Config:
#     enable: bool
#     root: Path
#     default_local_repo: LocalRepository | None
#     repositories: list[Repository]

#     @cached_property
#     def root_dir(self) -> Path:
#         return Path(self.root)

#     @cached_property
#     def local_repos(self) -> list[LocalRepository]:
#         local_repos = (
#             [self.default_local_repo] if self.default_local_repo is not None
#              else []
#         ) + [repo.local_repo for repo in self.repositories
#              if repo.local_repo is not None]
#         return list(set(local_repos))


#     def get_repo(self, cwd: Path | None = None) -> Repository:
#         cwd_ = cwd or Path.cwd()
#         for repo in self.repositories:
#             if cwd_.is_relative_to(repo.path):
#                 return repo
#         raise RuntimeError(
#             f"No configured Git repository discovered in the directory: {cwd_}")

#     def get_local_repo(self, cwd: Path | None = None) -> LocalRepository:
#         cwd_ = cwd or Path.cwd()
#         local_repo = (
#             self.get_repo(cwd=cwd_).local_repo or self.default_local_repo
#         )
#         if local_repo is None:
#             raise RuntimeError(
#                 f"No local repository configured for the given project: {local_repo}")
#         return local_repo


# def _load_local_repo(content: dict | None, root: Path) -> LocalRepository | None:
#     if content is None:
#         return None
#     else:
#         return LocalRepository(
#             url=content["url"],
#             branch=content["branch"],
#             root=root,
#         )


# def _load_repo_remote(content: dict) -> RepositoryRemote:
#     return RepositoryRemote(
#         name=content["name"],
#         url=content["url"],
#         branch=content["branch"],
#     )


# def _load_repo(path: str, content: dict, root: Path) -> Repository:
#     return Repository(
#         path=root / path,
#         local_repo=_load_local_repo(content["localRepository"], root),
#         remotes=[_load_repo_remote(raw_remote) for raw_remote in content["remotes"]],
#     )


# def load(path: Path | None = None) -> Config:
#     path_ = path or CONFIG_PATH
#     with open(path_, "r") as f:
#         raw = json.load(f)
#     root = Path(raw["root"])
#     return Config(
#         enable=raw["enable"],
#         root=root,
#         default_local_repo=_load_local_repo(raw["defaultLocalRepository"], root),
#         repositories=[_load_repo(path, raw_repo, root) for path, raw_repo in raw["repositories"].items()],
#     )
