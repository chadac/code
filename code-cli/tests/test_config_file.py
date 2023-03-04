from __future__ import annotations

from typing import TYPE_CHECKING

from code_cli.config import Config, DevRepoConfig, CodeRepoConfig, CodeRepoRemoteConfig


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_it_parses(mocker: MockerFixture):
    config_raw = {
        "enable": True,
        "package": "IGNORE",
        "root": "/test/path",
        "interval": "IGNORE",
        "devRepos": {
            ".": {
                "url": "git@github.com:test/devfiles.git",
                "branch": "main",
            },
            "private": {
                "url": "git@github.com:test/devfiles-private.git",
                "branch": "main2",
            },
        },
        "codeRepos": {
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
        devRepos={
            ".": DevRepoConfig(
                url="git@github.com:test/devfiles.git",
                branch="main",
            ),
            "private": DevRepoConfig(
                url="git@github.com:test/devfiles-private.git",
                branch="main2",
            ),
        },
        codeRepos={
            "github.com/NixOS/nixpkgs": CodeRepoConfig(
                remotes=[
                    CodeRepoRemoteConfig(
                        name="publish",
                        url="git@github.com:NixOS/nixpkgs.git",
                        branch="master",
                    ),
                ]
            ),
        },
    )
