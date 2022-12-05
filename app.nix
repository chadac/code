{
  pkgs,
  poetry2nix,
  lib,
  pyVer,
  editable ? false,
  dev ? false,
  test ? false,
  lintCheck ? false,
  typeCheck ? false,
  doCheck ? true,
}:
let
  doCheckInput = doCheck;
  poetryCommand = if !editable then "mkPoetryApplication" else "mkPoetryEnv";
in poetry2nix.${poetryCommand} (
  {
    projectDir = lib.cleanSource ./.;
    python = pyVer;
    groups =
      (if dev then ["dev"] else [])
      ++ (if test then ["test"] else [])
      ++ (if lintCheck then ["linting"] else [])
      ++ (if typeCheck then ["typing"] else [])
    ;
  } // (if editable then {
    editablePackageSources = {
      code-cli = ./src;
    };
  } else {
    doCheck = doCheckInput;
    checkPhase = builtins.concatStringsSep "\n" (
      (if test then [
        "python -m pytest ./tests"
      ] else [])
      ++ (if lintCheck then [
        "python -m flake8"
        "python -m black . --check"
        "python -m isort . -c"
      ] else [])
      ++ (if typeCheck then [
        "python -m mypy"
      ] else [])
    );
  })
)
