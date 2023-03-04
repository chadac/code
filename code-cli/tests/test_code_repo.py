from __future__ import annotations
from typing import TYPE_CHECKING
import pytest

from pathlib import Path

from code_cli.code_repo import CodeRepo, CodeRepoRemote

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def code_repo(tmp_path: Path) -> CodeRepo:
    return CodeRepo(
        path=tmp_path,
        remotes=[
            CodeRepoRemote(
                name="publish",
                url="git@github.com:chadac/code-repo-test.git",
                branch="default",
                path=tmp_path
            ),
            CodeRepoRemote(
                name="origin",
                url="git@github.com:chadac/code-repo-test-b.git",
                branch="new",
                path=tmp_path
            )
        ],
    )


@pytest.fixture
def expected_clone_cmd(code_repo: CodeRepo) -> list[str]:
    return [
        "clone", "--single-branch", "-o", "publish", "-b", "default",
        "git@github.com:chadac/code-repo-test.git", str(code_repo.path)
    ]


def test_create(mocker: MockerFixture, code_repo: CodeRepo, expected_clone_cmd: list[str]) -> None:
    m = mocker.patch("code_cli.git.run")
    code_repo._create()
    m.assert_called_with(expected_clone_cmd)


def test_sync(mocker: MockerFixture, code_repo: CodeRepo, expected_clone_cmd: list[str]) -> None:
    m = mocker.patch("code_cli.git.run")
    code_repo.sync()
    cwd = code_repo.path
    m.assert_has_calls([
        mocker.call(expected_clone_cmd),
        mocker.call(["remote", "set-url", "publish", "git@github.com:chadac/code-repo-test.git"], cwd=cwd),
        mocker.call(["fetch", "publish", "default:default"], cwd=cwd),
        mocker.call(["remote", "set-url", "origin", "git@github.com:chadac/code-repo-test-b.git"], cwd=cwd),
        mocker.call(["fetch", "origin", "new:new"], cwd=cwd),
    ])
