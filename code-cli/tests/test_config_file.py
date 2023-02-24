from __future__ import annotations

from typing import TYPE_CHECKING

from code_cli.config import Config, DevFilesRepoConfig, RepoConfig, RemoteConfig


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_it_parses(mocker: MockerFixture):
    config_raw = {
        "enable": True,
        "package": "IGNORE",
        "root": "/test/path",
        "interval": "IGNORE",
        "devFiles": {
            ".": {
                "url": "git@github.com:test/devfiles.git",
                "branch": "main",
            },
            "private": {
                "url": "git@github.com:test/devfiles-private.git",
                "branch": "main2",
            },
        },
        "repositories": {
            "github.com/NixOS/nixpkgs": {
                "remotes": [
                    {
                        "name": "publish",
                        "url": "git@github.com:NixOS/nixpkgs.git",
                        "branch": "master",
                    }
                ],
            },
        },
    }
    config = Config.parse(config_raw)
    assert config == Config(
        enable=True,
        package="IGNORE",
        root="/test/path",
        interval="IGNORE",
        devFiles={
            ".": DevFilesRepoConfig(
                url="git@github.com:test/devfiles.git",
                branch="main",
            ),
            "private": DevFilesRepoConfig(
                url="git@github.com:test/devfiles-private.git",
                branch="main2",
            ),
        },
        repositories={
            "github.com/NixOS/nixpkgs": RepoConfig(
                remotes=[
                    RemoteConfig(
                        name="publish",
                        url="git@github.com:NixOS/nixpkgs.git",
                        branch="master",
                    ),
                ]
            ),
        },
    )


# @pytest.fixture
# def local_repo() -> LocalRepository:
#     return LocalRepository(
#         url="git@github.com:example/repo.git",
#         branch="main",
#         root=Path("/a/b/c"),
#     )


# @pytest.fixture
# def local_repo_b() -> LocalRepository:
#     return LocalRepository(
#         url="git@github.com:example/repo.git",
#         branch=None,
#         root=Path("/a/b/c")
#     )


# @pytest.fixture
# def git_args(tmp_path: Path, mocker: MockerFixture) -> list[str]:
#     mocker.patch("code_cli.config_file.SHARE_PATH", tmp_path)
#     return [
#         f"--git-dir='{str(tmp_path)}/b84ac2ac219be14b7f50d88132b02acb66ae167673d333e82a6e6e4a1f42ebb6'",  # noqa: E501
#         "--work-tree='/a/b/c'",
#     ]


# def test_local_repo_id(
#     local_repo: LocalRepository,
#     local_repo_b: LocalRepository
# ) -> None:
# Ensure I don't change anything historical
#     assert local_repo.id == \
#         'b84ac2ac219be14b7f50d88132b02acb66ae167673d333e82a6e6e4a1f42ebb6'

#     assert local_repo_b.id == \
#         '9f47a2c7cdad10d5c96c97673f9bc37ed05ed2f77df6fb1c19cf0dc2aeff0041'


# def test_local_repo__git_args(
#     local_repo: LocalRepository,
#     git_args: list[str]
# ) -> None:
#     assert local_repo._git_args == git_args


# def test_local_repo_run_git(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
#     git_args: list[str]
# ) -> None:
#     m = mocker.patch("code_cli.git.run")
#     local_repo.run_git(["x", "y", "z"], x=1)
#     m.assert_called_with(git_args + ["x", "y", "z"], x=1)
#     local_repo.run_git("x y z", x=1)
#     m.assert_called_with(" ".join(git_args + ["x", "y", "z"]), x=1)


# def test_local_repo_check_git(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
#     git_args: list[str],
# ) -> None:
#     m = mocker.patch("code_cli.git.check", return_value="retval")
#     assert local_repo.check_git(["x", "y", "z"], x=1) == "retval"
#     m.assert_called_with(git_args + ["x", "y", "z"], x=1)
#     assert local_repo.check_git("x y z", x=1) == "retval"
#     m.assert_called_with(" ".join(git_args + ["x", "y", "z"]), x=1)


# def test_local_repo_get_files(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
#     git_args: list[str],
# ) -> None:
#     m = mocker.patch("code_cli.git.check", return_value="/a/b/c\n/a/b")
#     assert local_repo.get_files() == [Path("/a/b/c"), Path("/a/b")]
#     m.assert_called_with(
#         git_args + ["ls-tree", "--full-tree", "--name-only", "-r", "HEAD"])


# def test_local_repo_exists(local_repo: LocalRepository) -> None:
#     assert not local_repo.exists()


# def test_local_repo__clone(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
#     local_repo_b: LocalRepository,
# ) -> None:
#     m = mocker.patch("code_cli.git.run")
#     local_repo._clone()
#     m.assert_called_with([
#         "clone", "-b", local_repo.branch, local_repo.url, str(local_repo.path)
#     ])
#     local_repo_b._clone()
#     m.assert_called_with([
#         "clone", local_repo_b.url, str(local_repo_b.path)
#     ])


# def test_local_repo__init(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
#     local_repo_b: LocalRepository,
# ) -> None:
#     m = mocker.patch("code_cli.git.run")
#     local_repo._init()
#     m.assert_has_calls([
#         mocker.call(["init", "--bare", str(local_repo.path)]),
#         mocker.call(local_repo._git_args
#                     + ["remote", "set-url", "origin", local_repo.url]),
#         mocker.call(local_repo._git_args
#                     + ["checkout", "-b", local_repo.branch])
#     ], any_order=False)

#     local_repo_b._init()
#     m.assert_has_calls([
#         mocker.call(["init", "--bare", str(local_repo_b.path)]),
#         mocker.call(local_repo_b._git_args
#                     + ["remote", "set-url", "origin", local_repo_b.url]),
#     ], any_order=False)


# def test_local_repo__config(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
# ) -> None:
#     m = mocker.patch("code_cli.git.run")
#     local_repo._config()
#     m.assert_called_with(
#         local_repo._git_args +
#         ["config", "--local", "status.showUntrackedFiles", "no"],
#         cwd=local_repo.path
#     )


# def test_local_repo_create(
#     mocker: MockerFixture,
#     local_repo: LocalRepository,
# ) -> None:
#     m1 = mocker.patch("pathlib.Path.mkdir")
#     m2 = mocker.patch("code_cli.config_file.LocalRepository.exists",
#                       return_value=False)
#     m3 = mocker.patch("code_cli.config_file.LocalRepository._clone")
#     m4 = mocker.patch("code_cli.config_file.LocalRepository._init")
#     m5 = mocker.patch("code_cli.config_file.LocalRepository._config")
#     local_repo.create()
#     assert m1.called
#     assert m2.called
#     assert m3.called
#     assert not m4.called
#     assert m5.called
#     m1.assert_called_with(parents=True, exist_ok=True)
