# from __future__ import annotations

# from typing import TYPE_CHECKING

# import pytest

# import json
# import os

# from code_cli import cli, git, config_file


# if TYPE_CHECKING:
#     from pathlib import Path
#     from pytest_mock import MockerFixture


# def touch(f: Path) -> None:
#     if not f.parent.exists():
#         f.parent.mkdir(parents=True, exist_ok=True)
#     open(f, "w").write("")


# def mkrepo(path: Path, branch: str | None = None) -> Path:
#     path.parent.mkdir(parents=True, exist_ok=True)
#     git.run(["init", str(path)])
#     touch(path / "README.md")
#     git.run(["add", "-A"], cwd=path)
#     git.run(["commit", "-m", "'Initial commit.'"], cwd=path)
#     if branch is not None:
#         git.run(["checkout", "-b", branch], cwd=path)
#     return path


# def code_root(tmp_path: Path) -> Path:
#     return tmp_path


# @pytest.fixture
# def git_repo1(tmp_path: Path) -> Path:
#     return mkrepo(tmp_path / "repo1")


# @pytest.fixture
# def git_repo2(tmp_path: Path) -> Path:
#     return mkrepo(tmp_path / "repo2")


# @pytest.fixture
# def local_repo(tmp_path: Path) -> Path:
#     return mkrepo(tmp_path / "local_repo")


# @pytest.fixture
# def local_repo2(tmp_path: Path) -> Path:
#     return mkrepo(tmp_path / "local_repo2", branch="first")


# @pytest.fixture
# def git_config_home(mocker: MockerFixture, tmp_path: Path) -> Path:
#     git_config = tmp_path / "git" / "config"
#     git_config.parent.mkdir(parents=True, exist_ok=True)
#     mocker.patch.dict(os.environ, {
#         "GIT_CONFIG_COUNT": "3",
#         "GIT_CONFIG_KEY_0": "user.name",
#         "GIT_CONFIG_VALUE_0": "testuser",
#         "GIT_CONFIG_KEY_1": "user.email",
#         "GIT_CONFIG_VALUE_1": "testuser@example.org",
#         "GIT_CONFIG_KEY_2": "init.defaultBranch",
#         "GIT_CONFIG_VALUE_2": "main",
#     })
#     # git.run(["config", "user.name", "nix-test"])
#     # git.run(["config", "user.email", "nix-test@example.org"])
#     # git.run(["config", "init.defaultBranch", "main"])
#     return git_config


# @pytest.fixture
# def share_path(mocker: MockerFixture, tmp_path: Path) -> Path:
#     share_path = tmp_path / ".local" / "share" / "code-cli" / "repos"
#     mocker.patch("code_cli.config_file.SHARE_PATH", share_path)
#     return share_path


# @pytest.fixture
# def config_path(
#     mocker: MockerFixture,
#     tmp_path: Path,
#     git_repo1: Path,
#     git_repo2: Path,
#     local_repo: Path,
#     local_repo2: Path,
# ) -> Path:
#     config_path = tmp_path / ".config" / "code-cli" / "config.json"
#     config_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(config_path, "w") as f:
#         json.dump({
#             "enable": True,
#             "root": str(tmp_path / "ws-root"),
#             "interval": 0,
#             "defaultLocalRepository": {"url": str(local_repo), "branch": None},
#             "repositories": {
#                 "repo1": {
#                     "localRepository": None,
#                     "remotes": [
#                         {"name": "origin", "url": str(git_repo1), "branch": None},
#                     ],
#                 },
#                 "nested/repo2": {
#                     "localRepository": {"url": str(local_repo2), "branch": "first"},
#                     "remotes": [
#                         {"name": "publish", "url": str(git_repo2), "branch": None},
#                     ],
#                 },
#             },
#         }, f)
#     mocker.patch("code_cli.config_file.CONFIG_PATH", config_path)
#     mocker.patch("code_cli.cli.config", config_file.load())
#     return config_path


# @pytest.fixture
# def code_init(
#     git_config_home: Path,
#     share_path: Path,
#     config_path: Path,
# ) -> None:
#     pass


# def test_help(code_init: None):
#     cli.print_help()


# def test_sync_git(code_init: None):
#     cli.do_sync_git([])


# def test_sync_local(code_init: None):
#     cli.do_sync_local([])
