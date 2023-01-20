from pathlib import Path
import os
import subprocess


GIT_COMMAND = "git"


def _mk_cmd(args: str | list[str]) -> str | list[str]:
    if isinstance(args, str):
        return f"{GIT_COMMAND} {args}"
    else:
        return [GIT_COMMAND] + args


def run(args: str | list[str], **kwargs) -> None:
    cmd = _mk_cmd(args)
    r = subprocess.run(cmd, **kwargs)
    if r.returncode != 0:
        error_msg = None
        if r.stderr is not None:
            error_msg = r.stderr.decode()
        raise GitError(
            cmd,
            cwd=kwargs.get("cwd"),
            error=error_msg
        )


def check(args: str | list[str], **kwargs) -> str:
    cmd = _mk_cmd(args)
    try:
        r = subprocess.check_output(cmd, **kwargs)
    except subprocess.CalledProcessError as e:
        error_msg = None
        if r.stderr is not None:
            error_msg = r.stderr.decode()
        raise GitError(
            cmd,
            cwd=kwargs.get("cwd"),
            error=error_msg
        )
    return r


class GitError(Exception):
    def __init__(self, cmd: str | list[str], cwd: Path | None, error: str | None):
        if isinstance(cmd, list):
            cmd_msg = " ".join(cmd)
        else:
            cmd_msg = cmd

        if cwd is not None:
            cwd_msg = str(cwd)
        else:
            cwd_msg = None

        msg = f"{cwd_msg or ''}> {cmd_msg}\n{error or ''}"
        super().__init__(msg)
