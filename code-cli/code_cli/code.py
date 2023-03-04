from __future__ import annotations

from attrs import frozen
from pathlib import Path

from code_cli.config import Config
from code_cli.code_repo import CodeRepo
from code_cli.dev_repo import DevRepo


@frozen
class Code:
    config: Config
    root: Path
    dev_repos: list[DevRepo] = []
    code_repos: list[CodeRepo] = []

    @classmethod
    def init(cls, path: Path | None = None) -> Code:
        config = Config.load(path)
        root = Path(config.root)
        return Code(
            config=config,
            root=root,
            dev_repos=[DevRepo.init(root, prefix, dev_repo) for prefix, dev_repo in config.devRepos.items()],
            code_repos=[CodeRepo.init(Path(path), code_repo) for path, code_repo in config.codeRepos.items()],
        )

    def sync(self) -> None:
        # TODO: Continue if a single repo fails to sync.
        for repo in self.code_repos:
            repo.sync()

    @property
    def active_dev_repo(self, cwd: Path | None = None) -> DevRepo:
        path = cwd or Path.cwd()
        if not path.relative_to(self.root):
            raise RuntimeError(f"Currently not located in code root {self.root}")

        code_path = "." + str(path).removeprefix(str(self.root))

        # Search repos in sorted order from length of prefix to ensure we
        # always choose highest specificity
        repos = sorted(self.dev_repos, key=lambda r: -len(r.prefix))

        for repo in repos:
            if code_path.startswith(repo.prefix):
                return repo

        raise ValueError("No default devRepo configured. Ensure you have a devRepo with the key '.'")
