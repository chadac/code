{ pkgs, lib, python, git }:
with python.pkgs;
buildPythonApplication {
  pname = "code";
  version = "0.1";
  src = lib.cleanSource ./.;
  format = "pyproject";

  doCheck = true;
  checkInputs = [ pytest pytest-mock mypy flake8 ];
  checkPhase = ''
    mypy src/* tests/*
    pytest tests/*
    flake8 src/* tests/*
  '';

  postPatch = ''
    substituteInPlace ./code_cli/git.py \
      --replace 'GIT_COMMAND = "git"' 'GIT_COMMAND = "${pkgs.git}/bin/git"'
  '';

  propagatedBuildInputs = [ setuptools git ];
}
