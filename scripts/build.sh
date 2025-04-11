#! /bin/bash

git submodule update --init
uv sync 
python3 -m build
