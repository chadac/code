final: prev: {
  code-cli = prev.callPackage ./pkgs/code-cli { python = final.python3; };
}
