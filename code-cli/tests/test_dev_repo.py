from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

from pathlib import Path

from code_cli.dev_repo import DevRepo

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def dev_repo_a() -> DevRepo:
    return DevRepo(
        url="git@github.com:example/repo_a.git", branch="main", root=Path("/a/b/c"), prefix="."
    )


@pytest.fixture
def dev_repo_b() -> DevRepo:
    return DevRepo(
        url="git@github.com:example/repo_b.git", branch=None, root=Path("/a/b/c"), prefix="./private"
    )


@pytest.fixture
def share_path(tmp_path: Path, mocker: MockerFixture) -> Path:
    mocker.patch("code_cli.constants.SHARE_PATH", tmp_path)
    return tmp_path


@pytest.fixture
def git_args_a(share_path: Path) -> list[str]:
    return [
        f"--git-dir='{str(share_path)}/e5bde798d7dffd88f4d2d315bc721351ad51d41bf82ad9853ee9f5e825d89098'",  # noqa: E501
        "--work-tree='/a/b/c'",
    ]


def test_repo_id_consistent(dev_repo_a: DevRepo, dev_repo_b: DevRepo) -> None:
    """
    Code changes should never change repo ID's to be anything different.

    This affects the location of folders on the filesystem, so we
    definitely want to avoid this.
    """
    assert (
        dev_repo_a.id
        == "e5bde798d7dffd88f4d2d315bc721351ad51d41bf82ad9853ee9f5e825d89098"
    )

    assert (
        dev_repo_b.id
        == "2ca3b38211d5d428897e700ee965ef561940d593e5af03f6cd0cc6a5e6c136f4"
    )


def test_git_args(dev_repo_a: DevRepo, git_args_a: list[str]) -> None:
    assert dev_repo_a._git_args == git_args_a


def test_run_git(
    dev_repo_a: DevRepo,
    git_args_a: list[str],
    mocker: MockerFixture,
) -> None:
    m = mocker.patch("code_cli.git.run")
    dev_repo_a.run_git(["x", "y", "z"], x=1)
    m.assert_called_with(git_args_a + ["x", "y", "z"], x=1)
    dev_repo_a.run_git("x y z", x=1)
    m.assert_called_with(" ".join(git_args_a + ["x", "y", "z"]), x=1)


def test_clone(
    dev_repo_a: DevRepo,
    dev_repo_b: DevRepo,
    mocker: MockerFixture,
) -> None:
    m = mocker.patch("code_cli.git.run")
    args = [
        (dev_repo_a, [
            mocker.call(["clone", "--bare", dev_repo_a.url, str(dev_repo_a.path)]),
            mocker.call(dev_repo_a._git_args + ["checkout", dev_repo_a.branch])
        ]),
        (dev_repo_b, [
            mocker.call(["clone", "--bare", dev_repo_b.url, str(dev_repo_b.path)]),
            mocker.call(dev_repo_b._git_args + ["checkout"])
        ])
    ]
    for dev_repo, calls in args:
        m = mocker.patch("code_cli.git.run")
        dev_repo._clone()
        m.assert_has_calls(calls)


def test_bare_init(
    dev_repo_a: DevRepo,
    dev_repo_b: DevRepo,
    mocker: MockerFixture,
) -> None:
    m = mocker.patch("code_cli.git.run")
    dev_repo_a._bare_init()
    m.assert_has_calls([
        mocker.call(["init", "--bare", str(dev_repo_a.path)]),
        mocker.call(dev_repo_a._git_args
                    + ["remote", "set-url", "origin", dev_repo_a.url]),
        mocker.call(dev_repo_a._git_args
                    + ["checkout", "-b", dev_repo_a.branch])
    ], any_order=False)

    dev_repo_b._bare_init()
    m.assert_has_calls([
        mocker.call(["init", "--bare", str(dev_repo_b.path)]),
        mocker.call(dev_repo_b._git_args
                    + ["remote", "set-url", "origin", dev_repo_b.url]),
    ], any_order=False)


def test_config(
    dev_repo_a: DevRepo,
    mocker: MockerFixture
) -> None:
    m = mocker.patch("code_cli.git.run")
    dev_repo_a._config()
    m.assert_called_with([
        "config",
        "--local",
        "status.showUntrackedFiles",
        "no"
    ], cwd=dev_repo_a.path)
