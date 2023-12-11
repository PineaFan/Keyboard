#!/usr/bin/env bash
cd ~/Code/Keyboard
nix-shell shell.nix --run "python main.py"
