{ pkgs, lib, python3, git }:
with python3.pkgs;
buildPythonApplication {
  pname = "code";
  version = "1.0";
  src = lib.cleanSource ./.;
  format = "pyproject";

  buildInputs = [ cattrs git ];

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

  passthru = {
    inherit python3;
  };
}
