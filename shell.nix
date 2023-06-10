{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = [ 
      pkgs.python311 
      pkgs.python311Packages.pip
      pkgs.python311Packages.pyqt5
      pkgs.python311Packages.bleak
      pkgs.python311Packages.black
      pkgs.python311Packages.fastapi
      pkgs.python311Packages.uvicorn
      pkgs.python311Packages.requests
    ];
}
