{
  pkgs ? import <nixpkgs> { },
  code-cli ? pkgs.callPackage ./. { },
}:
pkgs.mkShell {
  name = "code-devShell";

  # Import all dependencies from code-cli
  inputsFrom = [ code-cli ];

  nativeBuildInputs = with code-cli.python3.pkgs; [ pytest-watch ];

  # Add our package to the PYTHONPATH so that we can properly run tests.
  shellHook = ''
    export PYTHONPATH=$PWD/code-cli:$PYTHONPATH
  '';
}
