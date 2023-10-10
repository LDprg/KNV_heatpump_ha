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
          setuptools-scm
          (buildPythonPackage rec {
            pname = "getmac";
            version = "0.9.4";
            doCheck = false;

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-hHd1W2n/k6O1FLVOH7uOu1fY9OXDfnwYvO86Dx8UkjI=";
            };
          })
          (buildPythonPackage rec {
            pname = "knvheatpumplib";
            version = "0.0.7";
            pyproject = true;
            doCheck = false;

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-+abauMfGTqjEKsMdgdBTjAxaALg5HjaQHqA8d724pUc=";
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
