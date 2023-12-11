{ pkgs ? (import <nixpkgs> {}).pkgs }: with pkgs;
  let
    venvDir = "./.venv";
  in mkShell {
    buildInputs = [
      python311Packages.virtualenv # run virtualenv .
      python311Packages.pip

      # Those are dependencies that we would like to use from nixpkgs, which will
      # add them to PYTHONPATH and thus make them accessible from within the venv.
      python311Packages.psutil
      python311Packages.dbus-python
      python311Packages.pygobject3

      # In this particular example, in order to compile any binary extensions they may
      # require, the Python modules listed in the hypothetical requirements.txt need
      # the following packages to be installed locally:
      taglib
      openssl
      git
      libxml2
      libxslt
      libzip
      zlib
    ];

    # This is very close to how venvShellHook is implemented, but
    # adapted to use 'virtualenv'
    shellHook = ''
      # Fixes libstdc++ issues and libgl.so issues
      LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/libstdc++.so.6

      SOURCE_DATE_EPOCH=$(date +%s)

      if [ -d "${venvDir}" ]; then
        echo "Skipping venv creation, '${venvDir}' already exists"
      else
        echo "Creating new venv environment in path: '${venvDir}'"
        # Note that the module venv was only introduced in python 3, so for 2.7
        # this needs to be replaced with a call to virtualenv
        ${python311Packages.python.interpreter} -m venv "${venvDir}"
      fi

      # Under some circumstances it might be necessary to add your virtual
      # environment to PYTHONPATH, which you can do here too;
      # PYTHONPATH=$PWD/${venvDir}/${python311Packages.python.sitePackages}/:$PYTHONPATH

      source "${venvDir}/bin/activate"

      # As in the previous example, this is optional.
      # pip install -r requirements.txt
      pip install openrgb-python requests
    '';
  }
