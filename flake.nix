{
  description = "aidecl-validate development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python314;
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            (python.withPackages (ps: [
              ps.jsonschema
              ps.pyyaml
              ps.pytest
              ps.pytest-cov
              ps.referencing
            ]))
          ];

          shellHook = ''
            echo "aidecl-validate dev environment ready"
          '';
        };
      });
}
