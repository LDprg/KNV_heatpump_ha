{ system ? builtins.currentSystem, pkgs ? import <nixpkgs> { inherit system; }
}:
pkgs.mkShell {
  nativeBuildInputs = with pkgs;
    [
      (let
        python = let
          packageOverrides = self: super: {
            wheel = super.wheel.overridePythonAttrs (old: rec {
              pname = "wheel";
              version = "0.40.0";
              src = fetchPypi {
                inherit pname version;
                hash = "sha256-zRGW8/ruKzGWjWJuFzHJT5nL22fPWkbk9WVsvudziHM=";
              };
            });
          };
        in pkgs.python3.override {
          inherit packageOverrides;
          self = python;
        };
      in python.withPackages (ps:
        with ps; [
          pip
          voluptuous
          async-timeout
          setuptools-scm
          (buildPythonPackage rec {
            pname = "scapy";
            version = "2.5.0";
            doCheck = false;

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-WyYMK3VP2NQJuoPueu4pTs27LCNfn3j+kLwRy25d68I=";
            };
          })
          (buildPythonPackage rec {
            pname = "knvheatpumplib";
            version = "0.0.21";
            pyproject = true;
            doCheck = false;

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-lu/Kiq27rMLvUnPqCJOqNqr3WUlGiwwHM5H3//XY0XM=";
            };

            nativeBuildInputs = [
              setuptools
              setuptools-scm
            ];
          })
          (buildPythonPackage rec {
            pname = "homeassistant";
            version = "2023.10.1";
            pyproject = true;
            doCheck = false;

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-3VkV5DirOzLO9Qbo4s5of5Aie7JvSAN7hgHBTA8koAE=";
            };

            nativeBuildInputs = [
              (buildPythonPackage rec {
                pname = "setuptools";
                version = "68.0.0";
                pyproject = true;
                doCheck = false;

                src = fetchPypi {
                  inherit pname version;
                  sha256 =
                    "sha256-uvH9tBxtpM0urnIuE1UA2pEzMqs/L1x9M6+bSSrLUjU=";
                };
              })
            ];
          })
        ]))
    ];
}
