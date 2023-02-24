from __future__ import annotations

from attrs import frozen
from pathlib import Path

from code_cli.config import Config
from code_cli.dev_files import DevFilesRepo


@frozen
class Code:
    config: Config

    @classmethod
    def init(cls, path: Path = None) -> Code:
        return Code(config=Config.load(path))
