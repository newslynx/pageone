#!/bin/sh
cd docs/
make html
cd _build/html
python -m SimpleHTTPServer