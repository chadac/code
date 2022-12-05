{
  pkgs,
  lib,
  poetry2nix,
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
  app = pkgs.callPackage ./app.nix {
    inherit pyVer;
  };
in pkgs.stdenv.mkDerivation rec {
  name = "code-cli-${pyVer.name}";
  src = lib.cleanSource ./bin;
  buildInputs = [ pkgs.git app ];
  prePatch = ''
    substituteInPlace code \
      --replace 'CODE_CLI=code-cli' 'CODE_CLI=${app}/bin/code-cli' \
      --replace 'GIT=git' 'GIT=${pkgs.git}/bin/git'
  '';

  buildPhase = ''
    mkdir -p $out/bin
    cp code $out/bin/
    ln -s $out/bin/code $out/bin/${name}
  '';

  doCheck = doCheckInput;
  checkPhase = ''
      export PATH=$out/bin:$PATH"
      code --help"
  '';

  installPhase = ":";
}
